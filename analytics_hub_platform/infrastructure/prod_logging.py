"""
Production Logging Configuration
Sustainable Economic Development Analytics Hub

Provides structured logging with:
- Rotating file handlers
- JSON formatting for production
- Console output for development
- Per-request context
- Performance timing
"""

import logging
import logging.handlers
import os
import sys
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from functools import wraps
from pathlib import Path
from typing import Any, Callable

import streamlit as st

# =============================================================================
# CONFIGURATION
# =============================================================================

LOG_DIR = Path(os.getenv("LOG_DIR", "logs"))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_FORMAT_JSON = os.getenv("LOG_FORMAT", "text").lower() == "json"
ENABLE_TIMING = os.getenv("ENABLE_TIMING_LOGS", "false").lower() == "true"

# Ensure log directory exists
LOG_DIR.mkdir(parents=True, exist_ok=True)


# =============================================================================
# FORMATTERS
# =============================================================================


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging in production."""

    def format(self, record: logging.LogRecord) -> str:
        import json

        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add extra fields
        for key in ["request_id", "user_id", "tenant_id", "duration_ms"]:
            if hasattr(record, key):
                log_data[key] = getattr(record, key)

        return json.dumps(log_data, ensure_ascii=False)


class ColoredFormatter(logging.Formatter):
    """Colored console formatter for development."""

    COLORS = {
        "DEBUG": "\033[36m",     # Cyan
        "INFO": "\033[32m",      # Green
        "WARNING": "\033[33m",   # Yellow
        "ERROR": "\033[31m",     # Red
        "CRITICAL": "\033[35m",  # Magenta
    }
    RESET = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{color}{record.levelname}{self.RESET}"
        return super().format(record)


# =============================================================================
# LOGGER SETUP
# =============================================================================


def setup_logging(
    log_level: str = LOG_LEVEL,
    log_dir: Path = LOG_DIR,
    json_format: bool = LOG_FORMAT_JSON,
) -> logging.Logger:
    """
    Configure application logging with rotating file handlers.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: Directory for log files
        json_format: Use JSON format for file logs

    Returns:
        Configured root logger
    """
    # Get root logger
    logger = logging.getLogger("analytics_hub")
    logger.setLevel(getattr(logging, log_level))

    # Clear existing handlers
    logger.handlers.clear()

    # Console handler (always text format, colored in dev)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)

    if sys.stdout.isatty():
        console_format = "%(asctime)s │ %(levelname)-8s │ %(name)s │ %(message)s"
        console_handler.setFormatter(ColoredFormatter(console_format, datefmt="%H:%M:%S"))
    else:
        console_format = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
        console_handler.setFormatter(logging.Formatter(console_format))

    logger.addHandler(console_handler)

    # File handler - rotating, 10MB max, 5 backups
    file_handler = logging.handlers.RotatingFileHandler(
        log_dir / "app.log",
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.INFO)

    if json_format:
        file_handler.setFormatter(JSONFormatter())
    else:
        file_format = "%(asctime)s - %(levelname)s - %(name)s - %(module)s:%(lineno)d - %(message)s"
        file_handler.setFormatter(logging.Formatter(file_format))

    logger.addHandler(file_handler)

    # Error file handler - errors only
    error_handler = logging.handlers.RotatingFileHandler(
        log_dir / "error.log",
        maxBytes=10 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8",
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(JSONFormatter() if json_format else logging.Formatter(
        "%(asctime)s - %(levelname)s - %(name)s - %(module)s:%(lineno)d - %(message)s\n%(exc_info)s"
    ))
    logger.addHandler(error_handler)

    return logger


def get_logger(name: str = "analytics_hub") -> logging.Logger:
    """Get a logger instance with the given name."""
    return logging.getLogger(name)


# =============================================================================
# TIMING UTILITIES
# =============================================================================


@contextmanager
def log_timing(operation: str, logger: logging.Logger | None = None):
    """
    Context manager for logging operation timing.

    Usage:
        with log_timing("load_data"):
            data = load_data()
    """
    if not ENABLE_TIMING:
        yield
        return

    log = logger or get_logger()
    start = time.perf_counter()

    try:
        yield
    finally:
        duration_ms = (time.perf_counter() - start) * 1000
        log.info(
            f"[TIMING] {operation}: {duration_ms:.2f}ms",
            extra={"duration_ms": duration_ms, "operation": operation}
        )


def timed(func: Callable) -> Callable:
    """
    Decorator for timing function execution.

    Usage:
        @timed
        def my_function():
            ...
    """
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        if not ENABLE_TIMING:
            return func(*args, **kwargs)

        logger = get_logger()
        start = time.perf_counter()

        try:
            result = func(*args, **kwargs)
            duration_ms = (time.perf_counter() - start) * 1000
            logger.info(
                f"[TIMING] {func.__module__}.{func.__name__}: {duration_ms:.2f}ms",
                extra={"duration_ms": duration_ms}
            )
            return result
        except Exception as e:
            duration_ms = (time.perf_counter() - start) * 1000
            logger.error(
                f"[TIMING] {func.__module__}.{func.__name__} FAILED after {duration_ms:.2f}ms: {e}",
                exc_info=True
            )
            raise

    return wrapper


def log_section_timing(section_name: str):
    """
    Decorator for timing dashboard section rendering.

    Usage:
        @log_section_timing("Hero Section")
        def render_hero_section():
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            if not ENABLE_TIMING:
                return func(*args, **kwargs)

            logger = get_logger("analytics_hub.sections")
            correlation_id = get_correlation_id()
            start = time.perf_counter()

            try:
                result = func(*args, **kwargs)
                duration_ms = (time.perf_counter() - start) * 1000

                # Also store in session state for dashboard display
                if "section_timings" not in st.session_state:
                    st.session_state.section_timings = {}
                st.session_state.section_timings[section_name] = duration_ms

                logger.info(
                    f"[SECTION] {section_name}: {duration_ms:.2f}ms",
                    extra={"correlation_id": correlation_id, "section": section_name, "duration_ms": duration_ms}
                )
                return result
            except Exception as e:
                logger.error(
                    f"[SECTION] {section_name} FAILED: {e}",
                    extra={"correlation_id": correlation_id, "section": section_name},
                    exc_info=True
                )
                raise

        return wrapper
    return decorator


# =============================================================================
# CORRELATION ID MANAGEMENT
# =============================================================================

def get_correlation_id() -> str:
    """
    Get or generate a correlation ID for request tracing.

    Uses Streamlit session state if available, otherwise generates a new one.
    """
    try:
        if "correlation_id" not in st.session_state:
            import uuid
            st.session_state.correlation_id = str(uuid.uuid4())[:8]
        return st.session_state.correlation_id
    except Exception:
        # Not in Streamlit context
        import uuid
        return str(uuid.uuid4())[:8]


def log_with_correlation(
    logger: logging.Logger,
    level: int,
    message: str,
    **extra_fields
) -> None:
    """
    Log a message with automatic correlation ID injection.

    Usage:
        log_with_correlation(logger, logging.INFO, "Processing data", user_id="123")
    """
    correlation_id = get_correlation_id()
    extra = {"correlation_id": correlation_id, **extra_fields}
    logger.log(level, f"[{correlation_id}] {message}", extra=extra)


class CorrelatedLogger:
    """
    Logger wrapper that automatically includes correlation ID.

    Usage:
        logger = CorrelatedLogger("my_module")
        logger.info("Processing started")
    """

    def __init__(self, name: str = "analytics_hub"):
        self._logger = logging.getLogger(name)

    def _log(self, level: int, message: str, **kwargs):
        correlation_id = get_correlation_id()
        extra = kwargs.pop("extra", {})
        extra["correlation_id"] = correlation_id
        self._logger.log(level, f"[{correlation_id}] {message}", extra=extra, **kwargs)

    def debug(self, message: str, **kwargs):
        self._log(logging.DEBUG, message, **kwargs)

    def info(self, message: str, **kwargs):
        self._log(logging.INFO, message, **kwargs)

    def warning(self, message: str, **kwargs):
        self._log(logging.WARNING, message, **kwargs)

    def error(self, message: str, **kwargs):
        self._log(logging.ERROR, message, **kwargs)

    def critical(self, message: str, **kwargs):
        self._log(logging.CRITICAL, message, **kwargs)


def get_correlated_logger(name: str = "analytics_hub") -> CorrelatedLogger:
    """Get a logger that automatically includes correlation IDs."""
    return CorrelatedLogger(name)


# =============================================================================
# INITIALIZATION
# =============================================================================

# Initialize logging on module import
_logger = setup_logging()
