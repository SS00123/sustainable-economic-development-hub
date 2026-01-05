"""
Observability Module
Sustainable Economic Development Analytics Hub
Ministry of Economy and Planning

Provides observability infrastructure:
- Structured JSON logging with correlation IDs
- Request/response timing middleware
- Metrics collection
- Health check utilities
"""

import json
import logging
import threading
import time
import uuid
from collections import defaultdict
from collections.abc import Callable
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timezone
from functools import wraps
from typing import Any

from analytics_hub_platform.infrastructure.settings import get_settings

# =============================================================================
# CORRELATION ID MANAGEMENT
# =============================================================================

# Thread-local storage for correlation IDs
_context = threading.local()


def get_correlation_id() -> str:
    """Get the current correlation ID, or generate a new one."""
    correlation_id = getattr(_context, "correlation_id", None)
    if correlation_id is None:
        correlation_id = str(uuid.uuid4())
        set_correlation_id(correlation_id)
    return correlation_id


def set_correlation_id(correlation_id: str) -> None:
    """Set the correlation ID for the current context."""
    _context.correlation_id = correlation_id


def clear_correlation_id() -> None:
    """Clear the correlation ID from the current context."""
    _context.correlation_id = None


@contextmanager
def correlation_context(correlation_id: str | None = None):
    """
    Context manager for correlation ID scope.

    Args:
        correlation_id: Optional ID to use, otherwise generates new one

    Example:
        with correlation_context() as cid:
            logger.info("Processing request", extra={"correlation_id": cid})
    """
    old_id = getattr(_context, "correlation_id", None)
    new_id = correlation_id or str(uuid.uuid4())
    set_correlation_id(new_id)
    try:
        yield new_id
    finally:
        if old_id:
            set_correlation_id(old_id)
        else:
            clear_correlation_id()


# =============================================================================
# STRUCTURED JSON LOGGING
# =============================================================================


class StructuredLogFormatter(logging.Formatter):
    """
    JSON formatter for structured logging.

    Outputs logs in JSON format with consistent fields:
    - timestamp: ISO 8601 format
    - level: Log level
    - logger: Logger name
    - message: Log message
    - correlation_id: Request correlation ID
    - extra: Additional context
    """

    RESERVED_ATTRS = {
        "name",
        "msg",
        "args",
        "created",
        "filename",
        "funcName",
        "levelname",
        "levelno",
        "lineno",
        "module",
        "msecs",
        "pathname",
        "process",
        "processName",
        "relativeCreated",
        "stack_info",
        "exc_info",
        "exc_text",
        "thread",
        "threadName",
        "message",
        "asctime",
    }

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        # Base log structure
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "correlation_id": get_correlation_id(),
        }

        # Add location info in debug mode
        settings = get_settings()
        if settings.debug:
            log_data["location"] = {
                "file": record.filename,
                "line": record.lineno,
                "function": record.funcName,
            }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add extra fields
        extra = {}
        for key, value in record.__dict__.items():
            if key not in self.RESERVED_ATTRS:
                try:
                    # Ensure value is JSON serializable
                    json.dumps(value)
                    extra[key] = value
                except (TypeError, ValueError):
                    extra[key] = str(value)

        if extra:
            log_data["extra"] = extra

        return json.dumps(log_data, default=str)


class ContextLogger:
    """
    Logger wrapper that automatically includes correlation ID and context.

    Example:
        logger = ContextLogger(__name__)
        logger.info("Processing request", user_id="123", action="view")
    """

    def __init__(self, name: str):
        self._logger = logging.getLogger(name)

    def _log(self, level: int, message: str, **kwargs):
        """Log with extra context."""
        extra = {"correlation_id": get_correlation_id()}
        extra.update(kwargs)
        self._logger.log(level, message, extra=extra)

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

    def exception(self, message: str, **kwargs):
        """Log exception with traceback."""
        extra = {"correlation_id": get_correlation_id()}
        extra.update(kwargs)
        self._logger.exception(message, extra=extra)


def get_context_logger(name: str) -> ContextLogger:
    """Get a context-aware logger."""
    return ContextLogger(name)


def setup_structured_logging(
    level: str | None = None,
    json_format: bool = True,
) -> None:
    """
    Configure structured JSON logging.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR)
        json_format: Use JSON format (True) or plain text (False)
    """
    import sys

    settings = get_settings()
    level = level or settings.log_level
    numeric_level = getattr(logging, level.upper(), logging.INFO)

    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    root_logger.handlers = []

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(numeric_level)

    if json_format:
        handler.setFormatter(StructuredLogFormatter())
    else:
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s [%(levelname)s] %(name)s (%(correlation_id)s): %(message)s"
            )
        )

    root_logger.addHandler(handler)

    # Quiet noisy libraries
    for lib in ["urllib3", "httpx", "sqlalchemy", "uvicorn.access"]:
        logging.getLogger(lib).setLevel(logging.WARNING)


# =============================================================================
# METRICS COLLECTION
# =============================================================================


@dataclass
class MetricPoint:
    """Single metric data point."""

    name: str
    value: float
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    labels: dict[str, str] = field(default_factory=dict)


class MetricsCollector:
    """
    Thread-safe metrics collector.

    Collects:
    - Counters (monotonically increasing values)
    - Gauges (point-in-time values)
    - Histograms (distribution of values)
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._counters: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
        self._gauges: dict[str, dict[str, float]] = defaultdict(dict)
        self._histograms: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
        self._data_lock = threading.Lock()
        self._initialized = True

    def _label_key(self, labels: dict[str, str]) -> str:
        """Create a consistent key from labels."""
        if not labels:
            return ""
        return ",".join(f"{k}={v}" for k, v in sorted(labels.items()))

    def increment_counter(
        self,
        name: str,
        value: float = 1.0,
        labels: dict[str, str] | None = None,
    ) -> None:
        """Increment a counter metric."""
        with self._data_lock:
            key = self._label_key(labels or {})
            self._counters[name][key] += value

    def set_gauge(
        self,
        name: str,
        value: float,
        labels: dict[str, str] | None = None,
    ) -> None:
        """Set a gauge metric."""
        with self._data_lock:
            key = self._label_key(labels or {})
            self._gauges[name][key] = value

    def observe_histogram(
        self,
        name: str,
        value: float,
        labels: dict[str, str] | None = None,
    ) -> None:
        """Add observation to histogram."""
        with self._data_lock:
            key = self._label_key(labels or {})
            self._histograms[name][key].append(value)
            # Keep only last 1000 observations per bucket
            if len(self._histograms[name][key]) > 1000:
                self._histograms[name][key] = self._histograms[name][key][-1000:]

    def get_counter(self, name: str, labels: dict[str, str] | None = None) -> float:
        """Get counter value."""
        with self._data_lock:
            key = self._label_key(labels or {})
            return self._counters[name].get(key, 0.0)

    def get_gauge(self, name: str, labels: dict[str, str] | None = None) -> float | None:
        """Get gauge value."""
        with self._data_lock:
            key = self._label_key(labels or {})
            return self._gauges[name].get(key)

    def get_histogram_stats(
        self,
        name: str,
        labels: dict[str, str] | None = None,
    ) -> dict[str, float]:
        """Get histogram statistics."""
        with self._data_lock:
            key = self._label_key(labels or {})
            values = self._histograms[name].get(key, [])

            if not values:
                return {"count": 0}

            sorted_values = sorted(values)
            count = len(values)

            return {
                "count": count,
                "sum": sum(values),
                "min": sorted_values[0],
                "max": sorted_values[-1],
                "avg": sum(values) / count,
                "p50": sorted_values[int(count * 0.5)],
                "p90": sorted_values[int(count * 0.9)],
                "p99": sorted_values[min(int(count * 0.99), count - 1)],
            }

    def get_all_metrics(self) -> dict[str, Any]:
        """Get all metrics in a structured format."""
        with self._data_lock:
            return {
                "counters": dict(self._counters),
                "gauges": dict(self._gauges),
                "histograms": {
                    name: {
                        key: self.get_histogram_stats(
                            name, dict(item.split("=") for item in key.split(",")) if key else None
                        )
                        for key in buckets
                    }
                    for name, buckets in self._histograms.items()
                },
            }

    def export_prometheus(self) -> str:
        """Export metrics in Prometheus format."""
        lines = []

        with self._data_lock:
            # Counters
            for name, buckets in self._counters.items():
                for labels_str, value in buckets.items():
                    labels_part = f"{{{labels_str}}}" if labels_str else ""
                    lines.append(f"{name}_total{labels_part} {value}")

            # Gauges
            for name, buckets in self._gauges.items():
                for labels_str, value in buckets.items():
                    labels_part = f"{{{labels_str}}}" if labels_str else ""
                    lines.append(f"{name}{labels_part} {value}")

            # Histograms (simplified)
            for name, buckets in self._histograms.items():
                for labels_str, values in buckets.items():
                    if not values:
                        continue
                    labels_part = f"{{{labels_str}}}" if labels_str else ""
                    lines.append(f"{name}_count{labels_part} {len(values)}")
                    lines.append(f"{name}_sum{labels_part} {sum(values)}")

        return "\n".join(lines)

    def reset(self) -> None:
        """Reset all metrics (mainly for testing)."""
        with self._data_lock:
            self._counters.clear()
            self._gauges.clear()
            self._histograms.clear()


def get_metrics() -> MetricsCollector:
    """Get the global metrics collector instance."""
    return MetricsCollector()


# Convenience functions
def increment_counter(name: str, value: float = 1.0, labels: dict[str, str] | None = None):
    """Increment a counter."""
    get_metrics().increment_counter(name, value, labels)


def set_gauge(name: str, value: float, labels: dict[str, str] | None = None):
    """Set a gauge value."""
    get_metrics().set_gauge(name, value, labels)


def observe_histogram(name: str, value: float, labels: dict[str, str] | None = None):
    """Observe histogram value."""
    get_metrics().observe_histogram(name, value, labels)


# =============================================================================
# TIMING UTILITIES
# =============================================================================


@contextmanager
def timed_operation(name: str, labels: dict[str, str] | None = None):
    """
    Context manager for timing operations.

    Example:
        with timed_operation("db_query", {"table": "indicators"}):
            result = db.query(...)
    """
    start = time.perf_counter()
    try:
        yield
    finally:
        elapsed = time.perf_counter() - start
        observe_histogram(f"{name}_duration_seconds", elapsed, labels)


def timed(name: str | None = None, labels: dict[str, str] | None = None):
    """
    Decorator for timing function execution.

    Example:
        @timed("calculate_index")
        def calculate_sustainability_index(data):
            ...
    """

    def decorator(func: Callable) -> Callable:
        metric_name = name or f"{func.__module__}.{func.__name__}"

        @wraps(func)
        def wrapper(*args, **kwargs):
            with timed_operation(metric_name, labels):
                return func(*args, **kwargs)

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            with timed_operation(metric_name, labels):
                return await func(*args, **kwargs)

        import asyncio

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return wrapper

    return decorator


# =============================================================================
# HEALTH CHECK UTILITIES
# =============================================================================


@dataclass
class HealthCheckResult:
    """Result of a health check."""

    name: str
    healthy: bool
    message: str = ""
    latency_ms: float = 0.0
    details: dict[str, Any] = field(default_factory=dict)


class HealthChecker:
    """
    Health check manager for monitoring service dependencies.

    Example:
        checker = HealthChecker()
        checker.register("database", check_database_health)
        checker.register("cache", check_cache_health)

        results = checker.check_all()
    """

    def __init__(self):
        self._checks: dict[str, Callable[[], HealthCheckResult]] = {}

    def register(self, name: str, check_func: Callable[[], HealthCheckResult]) -> None:
        """Register a health check function."""
        self._checks[name] = check_func

    def check(self, name: str) -> HealthCheckResult:
        """Run a specific health check."""
        if name not in self._checks:
            return HealthCheckResult(
                name=name,
                healthy=False,
                message=f"Unknown health check: {name}",
            )

        start = time.perf_counter()
        try:
            result = self._checks[name]()
            result.latency_ms = (time.perf_counter() - start) * 1000
            return result
        except Exception as e:
            return HealthCheckResult(
                name=name,
                healthy=False,
                message=str(e),
                latency_ms=(time.perf_counter() - start) * 1000,
            )

    def check_all(self) -> dict[str, HealthCheckResult]:
        """Run all registered health checks."""
        return {name: self.check(name) for name in self._checks}

    def is_healthy(self) -> bool:
        """Check if all health checks pass."""
        results = self.check_all()
        return all(r.healthy for r in results.values())

    def get_summary(self) -> dict[str, Any]:
        """Get summary of all health checks."""
        results = self.check_all()
        all_healthy = all(r.healthy for r in results.values())

        return {
            "status": "healthy" if all_healthy else "unhealthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "checks": {
                name: {
                    "healthy": r.healthy,
                    "message": r.message,
                    "latency_ms": round(r.latency_ms, 2),
                    "details": r.details,
                }
                for name, r in results.items()
            },
        }


# Global health checker instance
_health_checker: HealthChecker | None = None


def get_health_checker() -> HealthChecker:
    """Get or create the global health checker."""
    global _health_checker
    if _health_checker is None:
        _health_checker = HealthChecker()
    return _health_checker


# =============================================================================
# ALERTING CONFIGURATION
# =============================================================================


@dataclass
class AlertThreshold:
    """Configuration for an alert threshold."""

    name: str
    metric: str
    operator: str  # "gt", "lt", "gte", "lte", "eq"
    threshold: float
    severity: str  # "info", "warning", "critical"
    message_template: str = ""

    def check(self, value: float) -> bool:
        """Check if value exceeds threshold."""
        ops = {
            "gt": lambda v, t: v > t,
            "lt": lambda v, t: v < t,
            "gte": lambda v, t: v >= t,
            "lte": lambda v, t: v <= t,
            "eq": lambda v, t: v == t,
        }
        return ops.get(self.operator, lambda v, t: False)(value, self.threshold)

    def format_message(self, value: float) -> str:
        """Format alert message."""
        if self.message_template:
            return self.message_template.format(
                name=self.name,
                metric=self.metric,
                value=value,
                threshold=self.threshold,
            )
        return f"{self.name}: {self.metric} is {value} ({self.operator} {self.threshold})"


# Default alert thresholds
DEFAULT_ALERT_THRESHOLDS = [
    AlertThreshold(
        name="High Error Rate",
        metric="http_errors_total",
        operator="gt",
        threshold=100,
        severity="critical",
        message_template="Error rate exceeded: {value} errors (threshold: {threshold})",
    ),
    AlertThreshold(
        name="High Latency",
        metric="http_request_duration_seconds_p99",
        operator="gt",
        threshold=2.0,
        severity="warning",
        message_template="P99 latency is {value}s (threshold: {threshold}s)",
    ),
    AlertThreshold(
        name="Cache Miss Rate",
        metric="cache_miss_rate",
        operator="gt",
        threshold=0.5,
        severity="warning",
        message_template="Cache miss rate is {value:.1%} (threshold: {threshold:.1%})",
    ),
    AlertThreshold(
        name="Database Connection Pool",
        metric="db_pool_exhausted",
        operator="gt",
        threshold=0,
        severity="critical",
        message_template="Database connection pool exhausted {value} times",
    ),
]


class AlertManager:
    """
    Manages alert thresholds and checks.
    """

    def __init__(self, thresholds: list[AlertThreshold] | None = None):
        self._thresholds = thresholds or DEFAULT_ALERT_THRESHOLDS.copy()
        self._logger = get_context_logger(__name__)

    def add_threshold(self, threshold: AlertThreshold) -> None:
        """Add an alert threshold."""
        self._thresholds.append(threshold)

    def check_alerts(self, metrics: MetricsCollector) -> list[dict[str, Any]]:
        """Check all thresholds against current metrics."""
        alerts = []

        for threshold in self._thresholds:
            # Try to get metric value
            value = metrics.get_counter(threshold.metric)
            if value is None:
                value = metrics.get_gauge(threshold.metric)
            if value is None:
                stats = metrics.get_histogram_stats(threshold.metric)
                if "p99" in threshold.metric:
                    value = stats.get("p99")
                elif "avg" in threshold.metric:
                    value = stats.get("avg")

            if value is not None and threshold.check(value):
                alert = {
                    "name": threshold.name,
                    "metric": threshold.metric,
                    "value": value,
                    "threshold": threshold.threshold,
                    "severity": threshold.severity,
                    "message": threshold.format_message(value),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
                alerts.append(alert)

                # Log alert
                log_method = getattr(self._logger, threshold.severity, self._logger.warning)
                log_method(
                    alert["message"],
                    alert_name=threshold.name,
                    metric=threshold.metric,
                    value=value,
                )

        return alerts


def get_alert_manager() -> AlertManager:
    """Get an alert manager with default thresholds."""
    return AlertManager()
