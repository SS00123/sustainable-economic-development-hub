"""
API Middleware
Sustainable Economic Development Analytics Hub
Ministry of Economy and Planning

FastAPI middleware for:
- Request/response logging
- Timing and metrics collection
- Correlation ID propagation
- Error tracking
"""

import time
import uuid
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from analytics_hub_platform.infrastructure.observability import (
    get_context_logger,
    get_correlation_id,
    set_correlation_id,
    clear_correlation_id,
    increment_counter,
    observe_histogram,
    set_gauge,
)


logger = get_context_logger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging HTTP requests and responses.
    
    Features:
    - Assigns correlation ID to each request
    - Logs request start and completion
    - Records timing metrics
    - Tracks error rates
    """
    
    # Paths to exclude from detailed logging
    EXCLUDE_PATHS = {"/health", "/metrics", "/favicon.ico"}
    
    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        # Skip excluded paths
        if request.url.path in self.EXCLUDE_PATHS:
            return await call_next(request)
        
        # Get or create correlation ID
        correlation_id = request.headers.get("X-Correlation-ID")
        if not correlation_id:
            correlation_id = str(uuid.uuid4())
        
        set_correlation_id(correlation_id)
        
        # Extract request info
        method = request.method
        path = request.url.path
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("User-Agent", "")[:100]
        
        # Log request start
        logger.info(
            f"Request started: {method} {path}",
            method=method,
            path=path,
            client_ip=client_ip,
            user_agent=user_agent,
        )
        
        # Increment request counter
        increment_counter(
            "http_requests_total",
            labels={"method": method, "path": self._normalize_path(path)},
        )
        
        # Track active requests
        set_gauge("http_requests_active", 1, labels={"method": method})
        
        # Process request
        start_time = time.perf_counter()
        try:
            response = await call_next(request)
            status_code = response.status_code
            
            # Track response metrics
            elapsed = time.perf_counter() - start_time
            
            observe_histogram(
                "http_request_duration_seconds",
                elapsed,
                labels={
                    "method": method,
                    "path": self._normalize_path(path),
                    "status": str(status_code),
                },
            )
            
            # Log request completion
            log_level = "info" if status_code < 400 else "warning" if status_code < 500 else "error"
            getattr(logger, log_level)(
                f"Request completed: {method} {path} - {status_code} ({elapsed*1000:.1f}ms)",
                method=method,
                path=path,
                status_code=status_code,
                duration_ms=round(elapsed * 1000, 2),
            )
            
            # Track errors
            if status_code >= 400:
                increment_counter(
                    "http_errors_total",
                    labels={
                        "method": method,
                        "path": self._normalize_path(path),
                        "status": str(status_code),
                    },
                )
            
            # Add correlation ID to response headers
            response.headers["X-Correlation-ID"] = correlation_id
            
            return response
            
        except Exception as e:
            # Track exception
            elapsed = time.perf_counter() - start_time
            
            logger.exception(
                f"Request failed: {method} {path} - {type(e).__name__}",
                method=method,
                path=path,
                exception_type=type(e).__name__,
                duration_ms=round(elapsed * 1000, 2),
            )
            
            increment_counter(
                "http_errors_total",
                labels={
                    "method": method,
                    "path": self._normalize_path(path),
                    "status": "500",
                    "exception": type(e).__name__,
                },
            )
            
            raise
            
        finally:
            clear_correlation_id()
            set_gauge("http_requests_active", 0, labels={"method": method})
    
    def _normalize_path(self, path: str) -> str:
        """
        Normalize path for metric labels.
        
        Replaces dynamic segments (IDs, etc.) with placeholders
        to avoid high-cardinality labels.
        """
        parts = path.strip("/").split("/")
        normalized = []
        
        for part in parts:
            # Replace numeric IDs
            if part.isdigit():
                normalized.append("{id}")
            # Replace UUIDs
            elif len(part) == 36 and part.count("-") == 4:
                normalized.append("{uuid}")
            else:
                normalized.append(part)
        
        return "/" + "/".join(normalized) if normalized else "/"


class MetricsMiddleware(BaseHTTPMiddleware):
    """
    Lightweight middleware for collecting request metrics.
    
    Use this instead of RequestLoggingMiddleware if you only need metrics
    without detailed logging.
    """
    
    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        method = request.method
        path = request.url.path
        
        start_time = time.perf_counter()
        
        try:
            response = await call_next(request)
            status = str(response.status_code)
        except Exception:
            status = "500"
            raise
        finally:
            elapsed = time.perf_counter() - start_time
            
            # Record metrics
            observe_histogram(
                "http_request_duration_seconds",
                elapsed,
                labels={"method": method, "status": status},
            )
            increment_counter(
                "http_requests_total",
                labels={"method": method, "status": status},
            )
        
        return response


def add_observability_middleware(app) -> None:
    """
    Add observability middleware to a FastAPI application.
    
    Args:
        app: FastAPI application instance
        
    Example:
        from fastapi import FastAPI
        from analytics_hub_platform.infrastructure.middleware import add_observability_middleware
        
        app = FastAPI()
        add_observability_middleware(app)
    """
    app.add_middleware(RequestLoggingMiddleware)
