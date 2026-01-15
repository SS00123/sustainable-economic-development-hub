"""
Telemetry Module
Sustainable Economic Development Analytics Hub

Provides event capture for:
- Page views
- Export actions
- Preset usage
- Filter changes
- Performance metrics
"""

import json
import logging
import os
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any

import streamlit as st


# =============================================================================
# TELEMETRY CONFIGURATION
# =============================================================================


class TelemetryBackend(Enum):
    """Available telemetry backends."""

    NONE = "none"
    FILE = "file"
    LOG = "log"
    # Future: POSTHOG = "posthog", MIXPANEL = "mixpanel", etc.


# Configuration from environment
TELEMETRY_ENABLED = os.getenv("TELEMETRY_ENABLED", "true").lower() == "true"
TELEMETRY_BACKEND = TelemetryBackend(os.getenv("TELEMETRY_BACKEND", "log"))
TELEMETRY_FILE_PATH = os.getenv("TELEMETRY_FILE", "logs/telemetry.jsonl")


# =============================================================================
# EVENT MODELS
# =============================================================================


class EventType(Enum):
    """Types of telemetry events."""

    PAGE_VIEW = "page_view"
    EXPORT_CSV = "export_csv"
    EXPORT_PNG = "export_png"
    EXPORT_PDF = "export_pdf"
    PRESET_LOAD = "preset_load"
    PRESET_SAVE = "preset_save"
    FILTER_CHANGE = "filter_change"
    SHARE_LINK = "share_link"
    DQ_REPORT = "dq_report"
    DATA_UPLOAD = "data_upload"
    ERROR = "error"
    PERFORMANCE = "performance"


@dataclass
class TelemetryEvent:
    """A telemetry event record."""

    event_type: str
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    session_id: str = ""
    user_id: str = ""
    page: str = ""
    properties: dict[str, Any] = field(default_factory=dict)
    duration_ms: float | None = None
    correlation_id: str = ""

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "event_type": self.event_type,
            "timestamp": self.timestamp,
            "session_id": self.session_id,
            "user_id": self.user_id,
            "page": self.page,
            "properties": self.properties,
            "duration_ms": self.duration_ms,
            "correlation_id": self.correlation_id,
        }

    def to_json(self) -> str:
        """Serialize to JSON string."""
        return json.dumps(self.to_dict(), default=str)


# =============================================================================
# TELEMETRY COLLECTOR
# =============================================================================


class TelemetryCollector:
    """
    Collects and dispatches telemetry events.

    Thread-safe, singleton pattern for Streamlit apps.
    """

    _instance: "TelemetryCollector | None" = None
    _logger = logging.getLogger("analytics_hub.telemetry")

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._enabled = TELEMETRY_ENABLED
        self._backend = TELEMETRY_BACKEND
        self._file_path = Path(TELEMETRY_FILE_PATH)
        self._buffer: list[TelemetryEvent] = []
        self._buffer_size = 10
        self._initialized = True

        # Ensure log directory exists
        if self._backend == TelemetryBackend.FILE:
            self._file_path.parent.mkdir(parents=True, exist_ok=True)

    @property
    def session_id(self) -> str:
        """Get or create session ID."""
        if "telemetry_session_id" not in st.session_state:
            st.session_state.telemetry_session_id = str(uuid.uuid4())[:8]
        return st.session_state.telemetry_session_id

    @property
    def user_id(self) -> str:
        """Get user ID if available."""
        return st.session_state.get("user_id", "anonymous")

    @property
    def correlation_id(self) -> str:
        """Get correlation ID for request tracing."""
        return st.session_state.get("correlation_id", "")

    def track(
        self,
        event_type: EventType | str,
        page: str = "",
        properties: dict[str, Any] | None = None,
        duration_ms: float | None = None,
    ):
        """
        Track a telemetry event.

        Args:
            event_type: Type of event
            page: Page name where event occurred
            properties: Additional event properties
            duration_ms: Duration in milliseconds (for performance events)
        """
        if not self._enabled:
            return

        event = TelemetryEvent(
            event_type=event_type.value if isinstance(event_type, EventType) else event_type,
            session_id=self.session_id,
            user_id=self.user_id,
            page=page or self._get_current_page(),
            properties=properties or {},
            duration_ms=duration_ms,
            correlation_id=self.correlation_id,
        )

        self._dispatch(event)

    def track_page_view(self, page: str, referrer: str = ""):
        """Track a page view event."""
        self.track(
            EventType.PAGE_VIEW,
            page=page,
            properties={"referrer": referrer},
        )

    def track_export(self, export_type: str, format: str, row_count: int = 0):
        """Track an export event."""
        event_type = {
            "csv": EventType.EXPORT_CSV,
            "png": EventType.EXPORT_PNG,
            "pdf": EventType.EXPORT_PDF,
        }.get(format.lower(), EventType.EXPORT_CSV)

        self.track(
            event_type,
            properties={
                "export_type": export_type,
                "format": format,
                "row_count": row_count,
            },
        )

    def track_preset_usage(self, preset_id: str, action: str = "load"):
        """Track preset load or save."""
        event_type = EventType.PRESET_LOAD if action == "load" else EventType.PRESET_SAVE
        self.track(
            event_type,
            properties={"preset_id": preset_id, "action": action},
        )

    def track_filter_change(self, filter_name: str, old_value: Any, new_value: Any):
        """Track filter value changes."""
        self.track(
            EventType.FILTER_CHANGE,
            properties={
                "filter": filter_name,
                "old_value": str(old_value),
                "new_value": str(new_value),
            },
        )

    def track_performance(self, operation: str, duration_ms: float, metadata: dict | None = None):
        """Track performance metrics."""
        self.track(
            EventType.PERFORMANCE,
            properties={"operation": operation, **(metadata or {})},
            duration_ms=duration_ms,
        )

    def track_error(self, error: str, context: dict | None = None):
        """Track error events."""
        self.track(
            EventType.ERROR,
            properties={"error": error, "context": context or {}},
        )

    def _get_current_page(self) -> str:
        """Get current page name from Streamlit."""
        try:
            # Try to get from session state
            return st.session_state.get("current_page", "unknown")
        except Exception:
            return "unknown"

    def _dispatch(self, event: TelemetryEvent):
        """Dispatch event to configured backend."""
        if self._backend == TelemetryBackend.LOG:
            self._dispatch_to_log(event)
        elif self._backend == TelemetryBackend.FILE:
            self._dispatch_to_file(event)
        # TelemetryBackend.NONE does nothing

    def _dispatch_to_log(self, event: TelemetryEvent):
        """Write event to application log."""
        self._logger.info(
            f"TELEMETRY: {event.event_type}",
            extra={
                "telemetry_event": event.to_dict(),
            },
        )

    def _dispatch_to_file(self, event: TelemetryEvent):
        """Write event to JSONL file."""
        try:
            with open(self._file_path, "a", encoding="utf-8") as f:
                f.write(event.to_json() + "\n")
        except Exception as e:
            self._logger.error(f"Failed to write telemetry event: {e}")

    def flush(self):
        """Flush any buffered events."""
        # Currently events are written immediately
        # Future: batch writes for performance
        pass


# =============================================================================
# TIMING CONTEXT MANAGER
# =============================================================================


class TimingContext:
    """Context manager for timing operations."""

    def __init__(self, operation: str, collector: TelemetryCollector | None = None):
        self.operation = operation
        self.collector = collector or get_telemetry_collector()
        self.start_time: float = 0
        self.duration_ms: float = 0

    def __enter__(self):
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.duration_ms = (time.perf_counter() - self.start_time) * 1000
        self.collector.track_performance(
            self.operation,
            self.duration_ms,
            {"error": str(exc_val) if exc_val else None},
        )
        return False


def timed(operation: str):
    """Decorator for timing function execution."""

    def decorator(func):
        def wrapper(*args, **kwargs):
            with TimingContext(operation):
                return func(*args, **kwargs)

        return wrapper

    return decorator


# =============================================================================
# GLOBAL ACCESS
# =============================================================================


def get_telemetry_collector() -> TelemetryCollector:
    """Get the global telemetry collector instance."""
    return TelemetryCollector()


def track_event(event_type: EventType | str, **kwargs):
    """Convenience function to track an event."""
    get_telemetry_collector().track(event_type, **kwargs)


def track_page_view(page: str):
    """Convenience function to track page view."""
    get_telemetry_collector().track_page_view(page)


# =============================================================================
# STREAMLIT INTEGRATION
# =============================================================================


def init_telemetry():
    """
    Initialize telemetry for a Streamlit page.
    Call this at the start of each page.
    """
    collector = get_telemetry_collector()

    # Track page view on first load
    if "page_view_tracked" not in st.session_state:
        st.session_state.page_view_tracked = set()

    current_page = st.session_state.get("current_page", "unknown")
    if current_page not in st.session_state.page_view_tracked:
        collector.track_page_view(current_page)
        st.session_state.page_view_tracked.add(current_page)


def get_telemetry_stats() -> dict:
    """
    Get telemetry statistics for the current session.
    Useful for diagnostics.
    """
    return {
        "enabled": TELEMETRY_ENABLED,
        "backend": TELEMETRY_BACKEND.value,
        "session_id": st.session_state.get("telemetry_session_id", "N/A"),
        "pages_viewed": list(st.session_state.get("page_view_tracked", [])),
    }
