"""
Retry Utility
Sustainable Economic Development Analytics Hub
Ministry of Economy and Planning

Provides retry logic with exponential backoff for external service calls.
"""

import functools
import logging
import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import TypeVar

from analytics_hub_platform.infrastructure.exceptions import ExternalServiceError

logger = logging.getLogger(__name__)

T = TypeVar("T")


@dataclass
class RetryConfig:
    """Configuration for retry behavior."""

    max_attempts: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    jitter: bool = True
    retryable_exceptions: tuple[type[Exception], ...] = (Exception,)


def calculate_delay(
    attempt: int,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
) -> float:
    """
    Calculate delay for exponential backoff.

    Args:
        attempt: Current attempt number (0-indexed)
        base_delay: Base delay in seconds
        max_delay: Maximum delay cap
        exponential_base: Base for exponential calculation
        jitter: Whether to add random jitter

    Returns:
        Delay in seconds
    """
    import random

    delay = base_delay * (exponential_base**attempt)
    delay = min(delay, max_delay)

    if jitter:
        # Add jitter of ±25%
        jitter_range = delay * 0.25
        delay = delay + random.uniform(-jitter_range, jitter_range)

    return max(0.0, delay)


def retry_with_backoff(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    retryable_exceptions: tuple[type[Exception], ...] = (Exception,),
    on_retry: Callable[[int, Exception], None] | None = None,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Decorator for retrying functions with exponential backoff.

    Args:
        max_attempts: Maximum number of attempts
        base_delay: Initial delay in seconds
        max_delay: Maximum delay cap in seconds
        exponential_base: Base for exponential backoff
        jitter: Add randomness to delay
        retryable_exceptions: Tuple of exceptions to retry on
        on_retry: Optional callback called on each retry

    Returns:
        Decorated function

    Example:
        @retry_with_backoff(max_attempts=3, retryable_exceptions=(ConnectionError, TimeoutError))
        def call_external_api():
            return requests.get("https://api.example.com/data")
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            last_exception: Exception | None = None

            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except retryable_exceptions as e:
                    last_exception = e

                    if attempt < max_attempts - 1:
                        delay = calculate_delay(
                            attempt,
                            base_delay,
                            max_delay,
                            exponential_base,
                            jitter,
                        )

                        logger.warning(
                            f"Attempt {attempt + 1}/{max_attempts} failed for {func.__name__}: {e}. "
                            f"Retrying in {delay:.2f}s..."
                        )

                        if on_retry:
                            on_retry(attempt + 1, e)

                        time.sleep(delay)
                    else:
                        logger.error(f"All {max_attempts} attempts failed for {func.__name__}: {e}")

            # All attempts failed
            raise ExternalServiceError(
                f"Operation failed after {max_attempts} attempts: {last_exception}"
            ) from last_exception

        return wrapper

    return decorator


async def retry_with_backoff_async(
    func: Callable[..., T],
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    retryable_exceptions: tuple[type[Exception], ...] = (Exception,),
    on_retry: Callable[[int, Exception], None] | None = None,
    *args,
    **kwargs,
) -> T:
    """
    Async version of retry with backoff.

    Args:
        func: Async function to retry
        max_attempts: Maximum number of attempts
        base_delay: Initial delay in seconds
        max_delay: Maximum delay cap
        exponential_base: Base for exponential backoff
        jitter: Add randomness to delay
        retryable_exceptions: Tuple of exceptions to retry on
        on_retry: Optional callback on each retry
        *args: Arguments for func
        **kwargs: Keyword arguments for func

    Returns:
        Result of successful function call
    """
    import asyncio

    last_exception: Exception | None = None

    for attempt in range(max_attempts):
        try:
            return await func(*args, **kwargs)
        except retryable_exceptions as e:
            last_exception = e

            if attempt < max_attempts - 1:
                delay = calculate_delay(
                    attempt,
                    base_delay,
                    max_delay,
                    exponential_base,
                    jitter,
                )

                logger.warning(
                    f"Async attempt {attempt + 1}/{max_attempts} failed: {e}. "
                    f"Retrying in {delay:.2f}s..."
                )

                if on_retry:
                    on_retry(attempt + 1, e)

                await asyncio.sleep(delay)
            else:
                logger.error(f"All {max_attempts} async attempts failed: {e}")

    raise ExternalServiceError(
        f"Async operation failed after {max_attempts} attempts: {last_exception}"
    ) from last_exception


class RetryContext:
    """
    Context manager for retry logic.

    Example:
        with RetryContext(max_attempts=3) as retry:
            while retry.should_retry():
                try:
                    result = call_api()
                    break
                except APIError as e:
                    retry.record_failure(e)
    """

    def __init__(
        self,
        max_attempts: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True,
    ):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter

        self._attempt = 0
        self._last_exception: Exception | None = None
        self._succeeded = False

    def __enter__(self) -> "RetryContext":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def should_retry(self) -> bool:
        """Check if another retry attempt should be made."""
        return self._attempt < self.max_attempts and not self._succeeded

    def record_failure(self, exception: Exception) -> None:
        """Record a failed attempt and sleep before retry."""
        self._last_exception = exception
        self._attempt += 1

        if self._attempt < self.max_attempts:
            delay = calculate_delay(
                self._attempt - 1,
                self.base_delay,
                self.max_delay,
                self.exponential_base,
                self.jitter,
            )
            logger.warning(
                f"Attempt {self._attempt}/{self.max_attempts} failed: {exception}. "
                f"Retrying in {delay:.2f}s..."
            )
            time.sleep(delay)

    def record_success(self) -> None:
        """Record a successful attempt."""
        self._succeeded = True

    @property
    def attempt(self) -> int:
        """Current attempt number (1-indexed)."""
        return self._attempt + 1

    @property
    def last_exception(self) -> Exception | None:
        """Last recorded exception."""
        return self._last_exception
