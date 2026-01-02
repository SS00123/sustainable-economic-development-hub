"""
Rate Limiting Module
Sustainable Economic Development Analytics Hub
Ministry of Economy and Planning

Production-ready rate limiting with:
- Sliding window algorithm (more accurate than fixed window)
- Token bucket for burst handling
- Per-user and per-IP limiting
- FastAPI middleware integration
- Thread-safe implementation
"""

import logging
import threading
import time
from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass, field
from functools import wraps
from typing import Any, Optional

from analytics_hub_platform.infrastructure.exceptions import RateLimitError
from analytics_hub_platform.infrastructure.settings import get_settings

logger = logging.getLogger(__name__)


@dataclass
class RateLimitConfig:
    """Configuration for a rate limit rule."""

    max_requests: int
    window_seconds: int
    burst_size: int | None = None  # Token bucket burst size
    key_prefix: str = ""

    def __post_init__(self):
        if self.burst_size is None:
            self.burst_size = self.max_requests


@dataclass
class RateLimitState:
    """Internal state for rate limiting."""

    timestamps: list = field(default_factory=list)
    tokens: float = -1.0  # -1 indicates uninitialized
    last_update: float = field(default_factory=time.time)


class SlidingWindowRateLimiter:
    """
    Sliding window rate limiter with token bucket for burst handling.

    Combines two algorithms:
    1. Sliding window log - tracks exact request timestamps
    2. Token bucket - allows controlled bursts

    Thread-safe implementation suitable for multi-threaded servers.

    For production at scale, replace with Redis-based implementation.
    """

    def __init__(self, config: RateLimitConfig):
        """
        Initialize rate limiter.

        Args:
            config: Rate limit configuration
        """
        self.config = config
        self._states: dict[str, RateLimitState] = defaultdict(RateLimitState)
        self._lock = threading.RLock()

        # Token refill rate (tokens per second)
        self._refill_rate = config.max_requests / config.window_seconds

    def _get_key(self, identifier: str) -> str:
        """Generate full key with prefix."""
        if self.config.key_prefix:
            return f"{self.config.key_prefix}:{identifier}"
        return identifier

    def _cleanup_timestamps(self, state: RateLimitState, now: float) -> None:
        """Remove timestamps outside the window."""
        cutoff = now - self.config.window_seconds
        state.timestamps = [ts for ts in state.timestamps if ts > cutoff]

    def _initialize_tokens(self, state: RateLimitState) -> None:
        """Initialize tokens to burst size if uninitialized."""
        if state.tokens < 0:
            state.tokens = float(self.config.burst_size)

    def _refill_tokens(self, state: RateLimitState, now: float) -> None:
        """Refill tokens based on elapsed time."""
        self._initialize_tokens(state)
        elapsed = now - state.last_update
        state.tokens = min(self.config.burst_size, state.tokens + elapsed * self._refill_rate)
        state.last_update = now

    def check(self, identifier: str) -> tuple[bool, int, int]:
        """
        Check if request would be allowed (non-consuming).

        Args:
            identifier: Unique identifier (user_id, IP, etc.)

        Returns:
            Tuple of (allowed, remaining, retry_after_seconds)
        """
        key = self._get_key(identifier)
        now = time.time()

        with self._lock:
            state = self._states[key]
            self._cleanup_timestamps(state, now)
            self._refill_tokens(state, now)

            current_count = len(state.timestamps)
            remaining = max(0, self.config.max_requests - current_count)

            if current_count >= self.config.max_requests:
                # Calculate retry after
                if state.timestamps:
                    oldest = min(state.timestamps)
                    retry_after = int(oldest + self.config.window_seconds - now) + 1
                else:
                    retry_after = self.config.window_seconds
                return False, 0, max(1, retry_after)

            return True, remaining, 0

    def acquire(self, identifier: str) -> tuple[bool, int, int]:
        """
        Try to acquire a request slot.

        Args:
            identifier: Unique identifier

        Returns:
            Tuple of (acquired, remaining, retry_after_seconds)
        """
        key = self._get_key(identifier)
        now = time.time()

        with self._lock:
            state = self._states[key]
            self._cleanup_timestamps(state, now)
            self._refill_tokens(state, now)

            current_count = len(state.timestamps)

            if current_count >= self.config.max_requests:
                if state.timestamps:
                    oldest = min(state.timestamps)
                    retry_after = int(oldest + self.config.window_seconds - now) + 1
                else:
                    retry_after = self.config.window_seconds
                return False, 0, max(1, retry_after)

            # Check token bucket for burst protection
            if state.tokens < 1.0:
                retry_after = int((1.0 - state.tokens) / self._refill_rate) + 1
                return False, 0, max(1, retry_after)

            # Acquire slot
            state.timestamps.append(now)
            state.tokens -= 1.0
            remaining = max(0, self.config.max_requests - len(state.timestamps))

            return True, remaining, 0

    def acquire_or_raise(self, identifier: str) -> int:
        """
        Acquire a request slot or raise RateLimitError.

        Args:
            identifier: Unique identifier

        Returns:
            Remaining requests

        Raises:
            RateLimitError: If rate limit exceeded
        """
        acquired, remaining, retry_after = self.acquire(identifier)

        if not acquired:
            logger.warning(
                f"Rate limit exceeded for {identifier}: "
                f"{self.config.max_requests}/{self.config.window_seconds}s"
            )
            raise RateLimitError(
                message=f"Rate limit exceeded. Try again in {retry_after} seconds.",
                limit=self.config.max_requests,
                window_seconds=self.config.window_seconds,
                retry_after=retry_after,
            )

        return remaining

    def reset(self, identifier: str) -> None:
        """Reset rate limit state for an identifier."""
        key = self._get_key(identifier)
        with self._lock:
            if key in self._states:
                del self._states[key]

    def get_stats(self, identifier: str) -> dict[str, Any]:
        """Get rate limit statistics for debugging."""
        key = self._get_key(identifier)
        now = time.time()

        with self._lock:
            state = self._states.get(key)
            if not state:
                return {
                    "current_count": 0,
                    "remaining": self.config.max_requests,
                    "tokens": float(self.config.burst_size),
                    "window_seconds": self.config.window_seconds,
                }

            self._cleanup_timestamps(state, now)
            current_count = len(state.timestamps)

            return {
                "current_count": current_count,
                "remaining": max(0, self.config.max_requests - current_count),
                "tokens": state.tokens,
                "window_seconds": self.config.window_seconds,
            }


class RateLimiterManager:
    """
    Manages multiple rate limiters for different purposes.

    Provides centralized access to rate limiters for:
    - API endpoints
    - Export operations
    - Authentication attempts
    - Custom rules
    """

    _instance: Optional["RateLimiterManager"] = None
    _lock = threading.Lock()

    def __new__(cls):
        """Singleton pattern."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialize rate limiter manager."""
        if self._initialized:
            return

        self._limiters: dict[str, SlidingWindowRateLimiter] = {}
        self._settings = get_settings()
        self._setup_default_limiters()
        self._initialized = True

    def _setup_default_limiters(self) -> None:
        """Create default rate limiters from settings."""
        # API rate limiter
        self._limiters["api"] = SlidingWindowRateLimiter(
            RateLimitConfig(
                max_requests=self._settings.rate_limit_api,
                window_seconds=60,
                burst_size=min(20, self._settings.rate_limit_api // 2),
                key_prefix="api",
            )
        )

        # Export rate limiter (stricter)
        self._limiters["export"] = SlidingWindowRateLimiter(
            RateLimitConfig(
                max_requests=self._settings.rate_limit_exports,
                window_seconds=60,
                burst_size=3,
                key_prefix="export",
            )
        )

        # Auth rate limiter (prevent brute force)
        self._limiters["auth"] = SlidingWindowRateLimiter(
            RateLimitConfig(
                max_requests=5,
                window_seconds=300,  # 5 attempts per 5 minutes
                burst_size=3,
                key_prefix="auth",
            )
        )

    def get(self, name: str) -> SlidingWindowRateLimiter:
        """
        Get a rate limiter by name.

        Args:
            name: Limiter name (api, export, auth)

        Returns:
            Rate limiter instance

        Raises:
            KeyError: If limiter not found
        """
        if name not in self._limiters:
            raise KeyError(f"Rate limiter '{name}' not found")
        return self._limiters[name]

    def register(self, name: str, config: RateLimitConfig) -> SlidingWindowRateLimiter:
        """
        Register a custom rate limiter.

        Args:
            name: Limiter name
            config: Rate limit configuration

        Returns:
            Created rate limiter
        """
        limiter = SlidingWindowRateLimiter(config)
        self._limiters[name] = limiter
        return limiter

    def check_api(self, identifier: str) -> tuple[bool, int, int]:
        """Check API rate limit."""
        return self._limiters["api"].check(identifier)

    def acquire_api(self, identifier: str) -> int:
        """Acquire API rate limit slot or raise."""
        return self._limiters["api"].acquire_or_raise(identifier)

    def check_export(self, identifier: str) -> tuple[bool, int, int]:
        """Check export rate limit."""
        return self._limiters["export"].check(identifier)

    def acquire_export(self, identifier: str) -> int:
        """Acquire export rate limit slot or raise."""
        return self._limiters["export"].acquire_or_raise(identifier)

    def check_auth(self, identifier: str) -> tuple[bool, int, int]:
        """Check auth rate limit."""
        return self._limiters["auth"].check(identifier)

    def acquire_auth(self, identifier: str) -> int:
        """Acquire auth rate limit slot or raise."""
        return self._limiters["auth"].acquire_or_raise(identifier)


def get_rate_limiter_manager() -> RateLimiterManager:
    """Get the global rate limiter manager."""
    return RateLimiterManager()


def rate_limited(
    limiter_name: str = "api",
    key_func: Callable[..., str] | None = None,
):
    """
    Decorator for rate-limited functions.

    Args:
        limiter_name: Name of the rate limiter to use
        key_func: Function to extract rate limit key from arguments

    Example:
        @rate_limited("export", key_func=lambda user_id, **kw: user_id)
        def export_pdf(user_id: str, data: dict):
            ...
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            manager = get_rate_limiter_manager()
            limiter = manager.get(limiter_name)

            # Determine rate limit key
            if key_func:
                key = key_func(*args, **kwargs)
            else:
                key = "global"

            limiter.acquire_or_raise(key)
            return func(*args, **kwargs)

        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            manager = get_rate_limiter_manager()
            limiter = manager.get(limiter_name)

            if key_func:
                key = key_func(*args, **kwargs)
            else:
                key = "global"

            limiter.acquire_or_raise(key)
            return await func(*args, **kwargs)

        # Return appropriate wrapper based on function type
        import asyncio

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return wrapper

    return decorator


# FastAPI middleware
async def rate_limit_middleware(request, call_next):
    """
    FastAPI middleware for API rate limiting.

    Adds rate limit headers to responses:
    - X-RateLimit-Limit: Maximum requests allowed
    - X-RateLimit-Remaining: Remaining requests
    - X-RateLimit-Reset: Seconds until window reset
    """
    from fastapi.responses import JSONResponse

    # Skip rate limiting for health checks
    if request.url.path in ("/health", "/health/live", "/health/ready", "/metrics"):
        return await call_next(request)

    # Determine identifier (prefer user ID, fall back to IP)
    identifier = request.headers.get("X-User-ID")
    if not identifier:
        identifier = request.client.host if request.client else "unknown"

    manager = get_rate_limiter_manager()

    try:
        remaining = manager.acquire_api(identifier)
        response = await call_next(request)

        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(manager.get("api").config.max_requests)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(manager.get("api").config.window_seconds)

        return response

    except RateLimitError as e:
        logger.warning(f"Rate limit exceeded for {identifier}")
        return JSONResponse(
            status_code=429,
            content={
                "error": "rate_limit_exceeded",
                "message": e.message,
                "retry_after": e.details.get("retry_after", 60),
            },
            headers={
                "X-RateLimit-Limit": str(e.details.get("limit", 100)),
                "X-RateLimit-Remaining": "0",
                "Retry-After": str(e.details.get("retry_after", 60)),
            },
        )
