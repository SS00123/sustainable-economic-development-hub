"""
FastAPI Application Entry Point
Sustainable Economic Development Analytics Hub
Ministry of Economy and Planning

Main FastAPI application for REST API access.
Run with: uvicorn main_api:app --reload
"""

from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse

from analytics_hub_platform.api.routers import create_api_router
from analytics_hub_platform.infrastructure.settings import get_settings
from analytics_hub_platform.infrastructure.db_init import initialize_database, check_database_health
from analytics_hub_platform.infrastructure.middleware import add_observability_middleware
from analytics_hub_platform.infrastructure.observability import (
    get_health_checker,
    get_metrics,
    get_context_logger,
    HealthCheckResult,
    setup_structured_logging,
)
from analytics_hub_platform.infrastructure.caching import get_cache
from analytics_hub_platform.config.branding import BRANDING
from analytics_hub_platform.api.docs import API_TAGS, get_openapi_config


# Initialize structured logging
settings = get_settings()
if not settings.debug:
    setup_structured_logging(json_format=True)

logger = get_context_logger(__name__)


# =============================================================================
# HEALTH CHECK FUNCTIONS
# =============================================================================

def check_database() -> HealthCheckResult:
    """Health check for database connectivity."""
    try:
        health = check_database_health()
        return HealthCheckResult(
            name="database",
            healthy=health.get("connected", False),
            message="Connected" if health.get("connected") else "Disconnected",
            details=health,
        )
    except Exception as e:
        return HealthCheckResult(
            name="database",
            healthy=False,
            message=str(e),
        )


def check_cache() -> HealthCheckResult:
    """Health check for cache system."""
    try:
        cache = get_cache()
        stats = cache.get_stats()
        
        # Test cache operation
        cache.set("_health_check", "ok", ttl=10)
        test_value = cache.get("_health_check")
        
        return HealthCheckResult(
            name="cache",
            healthy=test_value == "ok",
            message="Operational" if test_value == "ok" else "Cache test failed",
            details=stats,
        )
    except Exception as e:
        return HealthCheckResult(
            name="cache",
            healthy=False,
            message=str(e),
        )


def register_health_checks():
    """Register all health check functions."""
    checker = get_health_checker()
    checker.register("database", check_database)
    checker.register("cache", check_cache)


# =============================================================================
# APPLICATION LIFESPAN
# =============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler.
    
    Runs on startup and shutdown.
    """
    # Startup
    settings = get_settings()
    initialize_database()
    register_health_checks()
    
    logger.info(
        "Application started",
        environment=settings.environment,
        debug=settings.debug,
    )
    
    yield
    
    # Shutdown
    logger.info("Application shutting down")


# Create FastAPI app with enhanced documentation
openapi_config = get_openapi_config()
app = FastAPI(
    title=openapi_config["title"],
    description=openapi_config["description"],
    version=openapi_config["version"],
    openapi_tags=API_TAGS,
    contact=openapi_config["contact"],
    license_info=openapi_config["license_info"],
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Add observability middleware
add_observability_middleware(app)

# CORS middleware
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.debug else ["https://ministry.gov.sa"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Handle uncaught exceptions."""
    from analytics_hub_platform.infrastructure.observability import increment_counter
    
    increment_counter(
        "http_unhandled_exceptions_total",
        labels={"exception_type": type(exc).__name__},
    )
    
    logger.exception(
        "Unhandled exception",
        exception_type=type(exc).__name__,
        path=str(request.url.path),
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "type": type(exc).__name__,
        },
    )


# =============================================================================
# OBSERVABILITY ENDPOINTS
# =============================================================================

@app.get("/health", tags=["Observability"])
async def health_check():
    """
    Comprehensive health check endpoint.
    
    Returns status of all service dependencies.
    """
    checker = get_health_checker()
    summary = checker.get_summary()
    
    status_code = 200 if summary["status"] == "healthy" else 503
    return JSONResponse(content=summary, status_code=status_code)


@app.get("/health/live", tags=["Observability"])
async def liveness_check():
    """
    Kubernetes liveness probe.
    
    Returns 200 if the application is running.
    """
    return {"status": "alive", "timestamp": datetime.now(timezone.utc).isoformat()}


@app.get("/health/ready", tags=["Observability"])
async def readiness_check():
    """
    Kubernetes readiness probe.
    
    Returns 200 if the application is ready to serve traffic.
    """
    checker = get_health_checker()
    is_ready = checker.is_healthy()
    
    if is_ready:
        return {"status": "ready", "timestamp": datetime.now(timezone.utc).isoformat()}
    else:
        return JSONResponse(
            status_code=503,
            content={"status": "not_ready", "timestamp": datetime.now(timezone.utc).isoformat()},
        )


@app.get("/metrics", tags=["Observability"])
async def metrics_endpoint():
    """
    Prometheus-compatible metrics endpoint.
    
    Returns metrics in Prometheus text format.
    """
    metrics = get_metrics()
    return PlainTextResponse(
        content=metrics.export_prometheus(),
        media_type="text/plain",
    )


# Include API router
api_router = create_api_router()
app.include_router(api_router, prefix="/api/v1")


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Sustainable Economic Development Analytics Hub API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health",
        "metrics": "/metrics",
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
