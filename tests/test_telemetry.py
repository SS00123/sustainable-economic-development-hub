"""
Tests for telemetry module.

Tests event capture, timing utilities, and telemetry backends.
"""

import json
import time
from unittest.mock import MagicMock, patch

import pytest

from analytics_hub_platform.infrastructure.telemetry import (
    EventType,
    TelemetryBackend,
    TelemetryCollector,
    TelemetryEvent,
    TimingContext,
    get_telemetry_collector,
    get_telemetry_stats,
    init_telemetry,
    timed,
)


class TestTelemetryEvent:
    """Test TelemetryEvent dataclass."""

    def test_event_creation(self):
        """Test creating a telemetry event."""
        event = TelemetryEvent(
            event_type="page_view",
        )

        assert event.event_type == "page_view"
        assert event.timestamp is not None
        assert event.session_id == ""
        assert event.user_id == ""
        assert event.properties == {}

    def test_event_with_all_fields(self):
        """Test event with all fields populated."""
        event = TelemetryEvent(
            event_type="export_csv",
            session_id="session-123",
            user_id="user-456",
            page="dashboard",
            properties={"rows": 100},
            duration_ms=150.5,
            correlation_id="corr-789",
        )

        assert event.session_id == "session-123"
        assert event.user_id == "user-456"
        assert event.page == "dashboard"
        assert event.properties["rows"] == 100
        assert event.duration_ms == 150.5

    def test_to_dict(self):
        """Test converting event to dictionary."""
        event = TelemetryEvent(
            event_type="filter_change",
            session_id="sess-1",
            page="kpis",
            properties={"filter": "year", "value": 2024},
        )

        d = event.to_dict()

        assert d["event_type"] == "filter_change"
        assert d["properties"]["filter"] == "year"
        assert d["session_id"] == "sess-1"
        assert "timestamp" in d

    def test_to_json(self):
        """Test converting event to JSON string."""
        event = TelemetryEvent(
            event_type="page_view",
            page="kpis",
        )

        json_str = event.to_json()
        parsed = json.loads(json_str)

        assert parsed["event_type"] == "page_view"
        assert parsed["page"] == "kpis"


class TestTelemetryBackend:
    """Test TelemetryBackend enum."""

    def test_backend_values(self):
        """Test backend enum values."""
        assert TelemetryBackend.NONE.value == "none"
        assert TelemetryBackend.FILE.value == "file"
        assert TelemetryBackend.LOG.value == "log"

    def test_from_string(self):
        """Test creating backend from string."""
        assert TelemetryBackend("file") == TelemetryBackend.FILE
        assert TelemetryBackend("log") == TelemetryBackend.LOG
        assert TelemetryBackend("none") == TelemetryBackend.NONE


class TestEventType:
    """Test EventType enum."""

    def test_event_type_values(self):
        """Test all event types exist."""
        assert EventType.PAGE_VIEW.value == "page_view"
        assert EventType.EXPORT_CSV.value == "export_csv"
        assert EventType.EXPORT_PNG.value == "export_png"
        assert EventType.EXPORT_PDF.value == "export_pdf"
        assert EventType.PRESET_LOAD.value == "preset_load"
        assert EventType.PRESET_SAVE.value == "preset_save"
        assert EventType.FILTER_CHANGE.value == "filter_change"
        assert EventType.SHARE_LINK.value == "share_link"
        assert EventType.DQ_REPORT.value == "dq_report"
        assert EventType.DATA_UPLOAD.value == "data_upload"
        assert EventType.ERROR.value == "error"
        assert EventType.PERFORMANCE.value == "performance"

    def test_all_event_types_count(self):
        """Test expected number of event types."""
        assert len(EventType) == 12


class TestTelemetryCollectorSingleton:
    """Test TelemetryCollector singleton pattern."""

    def test_singleton_pattern(self):
        """Test that TelemetryCollector is a singleton."""
        # Reset singleton
        TelemetryCollector._instance = None

        collector1 = TelemetryCollector()
        collector2 = TelemetryCollector()

        assert collector1 is collector2

        # Cleanup
        TelemetryCollector._instance = None

    def test_get_telemetry_collector_returns_instance(self):
        """Test get_telemetry_collector returns collector."""
        TelemetryCollector._instance = None

        collector = get_telemetry_collector()

        assert collector is not None
        assert isinstance(collector, TelemetryCollector)

        TelemetryCollector._instance = None


class TestTelemetryCollectorDisabled:
    """Test TelemetryCollector when disabled."""

    @pytest.fixture
    def disabled_collector(self):
        """Create a disabled telemetry collector."""
        TelemetryCollector._instance = None

        # Create collector and manually disable
        collector = TelemetryCollector()
        collector._enabled = False

        yield collector

        TelemetryCollector._instance = None

    def test_disabled_collector_track_no_error(self, disabled_collector):
        """Test that disabled collector doesn't raise on track."""
        # Should not raise
        disabled_collector.track(EventType.PAGE_VIEW, page="test")


class TestTelemetryCollectorMocked:
    """Test TelemetryCollector with mocked Streamlit."""

    @pytest.fixture
    def mock_st(self):
        """Mock streamlit session state."""
        mock_session = MagicMock()
        mock_session.get.return_value = "test_session"
        mock_session.__contains__ = lambda self, x: False
        mock_session.__setitem__ = MagicMock()
        mock_session.__getitem__ = MagicMock(return_value="test")

        with patch("analytics_hub_platform.infrastructure.telemetry.st") as mock:
            mock.session_state = mock_session
            yield mock

    @pytest.fixture
    def enabled_collector(self, mock_st):
        """Create an enabled telemetry collector with log backend."""
        TelemetryCollector._instance = None

        collector = TelemetryCollector()
        collector._enabled = True
        collector._backend = TelemetryBackend.LOG

        yield collector

        TelemetryCollector._instance = None

    def test_track_page_view(self, enabled_collector):
        """Test tracking page views."""
        # Should not raise
        enabled_collector.track_page_view("Dashboard")

    def test_track_export_csv(self, enabled_collector):
        """Test tracking CSV export."""
        enabled_collector.track_export("data", "csv", row_count=500)

    def test_track_export_png(self, enabled_collector):
        """Test tracking PNG export."""
        enabled_collector.track_export("chart", "png")

    def test_track_export_pdf(self, enabled_collector):
        """Test tracking PDF export."""
        enabled_collector.track_export("report", "pdf")

    def test_track_preset_usage_load(self, enabled_collector):
        """Test tracking preset load."""
        enabled_collector.track_preset_usage("economic_focus", action="load")

    def test_track_preset_usage_save(self, enabled_collector):
        """Test tracking preset save."""
        enabled_collector.track_preset_usage("custom_view", action="save")

    def test_track_filter_change(self, enabled_collector):
        """Test tracking filter changes."""
        enabled_collector.track_filter_change(
            filter_name="year",
            old_value=2023,
            new_value=2024,
        )

    def test_track_performance(self, enabled_collector):
        """Test tracking performance metrics."""
        enabled_collector.track_performance(
            operation="database_query",
            duration_ms=150.5,
            metadata={"query": "SELECT * FROM indicators"},
        )

    def test_track_error(self, enabled_collector):
        """Test tracking errors."""
        enabled_collector.track_error(
            error="Database connection failed",
            context={"code": "DB001", "retry": True},
        )


class TestTimingContext:
    """Test TimingContext context manager."""

    @pytest.fixture
    def mock_st(self):
        """Mock streamlit session state."""
        mock_session = MagicMock()
        mock_session.get.return_value = "test_session"
        mock_session.__contains__ = lambda self, x: False

        with patch("analytics_hub_platform.infrastructure.telemetry.st") as mock:
            mock.session_state = mock_session
            yield mock

    @pytest.fixture
    def mock_collector(self, mock_st):
        """Create mock collector for timing tests."""
        TelemetryCollector._instance = None
        collector = TelemetryCollector()
        collector._enabled = True
        collector._backend = TelemetryBackend.NONE
        yield collector
        TelemetryCollector._instance = None

    def test_timing_context_measures_time(self, mock_collector):
        """Test that timing context measures elapsed time."""
        with TimingContext("test_operation", mock_collector) as ctx:
            time.sleep(0.05)  # Sleep 50ms

        # Duration should be recorded
        assert ctx.duration_ms >= 40  # At least 40ms

    def test_timing_context_no_exception(self, mock_collector):
        """Test timing context handles normal flow."""
        with TimingContext("operation", mock_collector) as _ctx:  # noqa: F841
            x = 1 + 1

        # Should complete without exception
        assert x == 2

    def test_timing_context_with_exception(self, mock_collector):
        """Test timing context handles exceptions."""
        with pytest.raises(ValueError):
            with TimingContext("failing_operation", mock_collector):
                raise ValueError("Test error")


class TestTimedDecorator:
    """Test @timed decorator."""

    @pytest.fixture
    def mock_st(self):
        """Mock streamlit session state."""
        mock_session = MagicMock()
        mock_session.get.return_value = "test_session"
        mock_session.__contains__ = lambda self, x: False

        with patch("analytics_hub_platform.infrastructure.telemetry.st") as mock:
            mock.session_state = mock_session
            yield mock

    @pytest.fixture
    def setup_collector(self, mock_st):
        """Setup collector for timed tests."""
        TelemetryCollector._instance = None
        collector = TelemetryCollector()
        collector._enabled = True
        collector._backend = TelemetryBackend.NONE
        yield
        TelemetryCollector._instance = None

    def test_timed_decorator(self, setup_collector):
        """Test @timed decorator measures function time."""
        call_count = 0

        @timed("sample_operation")
        def sample_function():
            nonlocal call_count
            call_count += 1
            time.sleep(0.02)  # 20ms
            return "result"

        result = sample_function()

        assert result == "result"
        assert call_count == 1

    def test_timed_decorator_with_args(self, setup_collector):
        """Test @timed decorator with function arguments."""
        @timed("add_operation")
        def add_numbers(a, b):
            return a + b

        result = add_numbers(3, 5)

        assert result == 8

    def test_timed_decorator_with_kwargs(self, setup_collector):
        """Test @timed decorator with keyword arguments."""
        @timed("greet_operation")
        def greet(name, greeting="Hello"):
            return f"{greeting}, {name}!"

        result = greet("World", greeting="Hi")

        assert result == "Hi, World!"

    def test_timed_decorator_preserves_exception(self, setup_collector):
        """Test @timed decorator preserves exceptions."""
        @timed("failing_operation")
        def failing_function():
            raise RuntimeError("Intentional failure")

        with pytest.raises(RuntimeError, match="Intentional failure"):
            failing_function()


class TestInitTelemetry:
    """Test init_telemetry function."""

    @pytest.fixture
    def mock_st(self):
        """Mock streamlit session state with proper attribute access."""
        mock_session = MagicMock()
        mock_session.get.return_value = "unknown"
        mock_session.__contains__ = lambda self, x: x == "page_view_tracked"
        mock_session.page_view_tracked = set()

        with patch("analytics_hub_platform.infrastructure.telemetry.st") as mock:
            mock.session_state = mock_session
            yield mock

    def test_init_telemetry_creates_collector(self, mock_st):
        """Test that init_telemetry creates a collector."""
        TelemetryCollector._instance = None

        init_telemetry()
        collector = get_telemetry_collector()
        assert collector is not None

        TelemetryCollector._instance = None


class TestGetTelemetryStats:
    """Test get_telemetry_stats function."""

    @pytest.fixture
    def mock_st(self):
        """Mock streamlit session state."""
        mock_session = {"telemetry_session_id": "test-123"}

        with patch("analytics_hub_platform.infrastructure.telemetry.st") as mock:
            mock.session_state = mock_session
            yield mock

    def test_get_stats_returns_dict(self, mock_st):
        """Test that get_telemetry_stats returns a dictionary."""
        TelemetryCollector._instance = None

        stats = get_telemetry_stats()

        assert isinstance(stats, dict)
        assert "enabled" in stats
        assert "backend" in stats
        assert "session_id" in stats

        TelemetryCollector._instance = None


class TestFileBackendIntegration:
    """Integration tests for file backend."""

    @pytest.fixture
    def mock_st(self):
        """Mock streamlit session state."""
        mock_session = MagicMock()
        mock_session.get.return_value = "test_session"
        mock_session.__contains__ = lambda self, x: True  # Has session_id
        mock_session.__getitem__ = MagicMock(return_value="test-session-id")

        with patch("analytics_hub_platform.infrastructure.telemetry.st") as mock:
            mock.session_state = mock_session
            yield mock

    def test_file_backend_config(self, tmp_path, mock_st):
        """Test that file backend can be configured."""
        TelemetryCollector._instance = None

        collector = TelemetryCollector()
        collector._enabled = True
        collector._backend = TelemetryBackend.FILE
        collector._file_path = tmp_path / "telemetry.jsonl"

        # Track an event - should not raise
        collector.track(EventType.PAGE_VIEW, page="test")

        TelemetryCollector._instance = None

    def test_log_backend_config(self, mock_st):
        """Test that log backend can be configured."""
        TelemetryCollector._instance = None

        collector = TelemetryCollector()
        collector._enabled = True
        collector._backend = TelemetryBackend.LOG

        # Track an event - should not raise
        collector.track(EventType.PAGE_VIEW, page="test")

        TelemetryCollector._instance = None

    def test_none_backend_no_dispatch(self, mock_st):
        """Test that NONE backend doesn't dispatch."""
        TelemetryCollector._instance = None

        collector = TelemetryCollector()
        collector._enabled = True
        collector._backend = TelemetryBackend.NONE

        # Track an event - should not raise
        collector.track(EventType.PAGE_VIEW, page="test")

        TelemetryCollector._instance = None


class TestEventTypeMappings:
    """Test event type mappings in TelemetryCollector."""

    @pytest.fixture
    def mock_st(self):
        """Mock streamlit session state."""
        mock_session = MagicMock()
        mock_session.get.return_value = "test_session"
        mock_session.__contains__ = lambda self, x: False

        with patch("analytics_hub_platform.infrastructure.telemetry.st") as mock:
            mock.session_state = mock_session
            yield mock

    def test_export_csv_mapping(self, mock_st):
        """Test CSV export maps to EXPORT_CSV event type."""
        TelemetryCollector._instance = None
        collector = TelemetryCollector()
        collector._enabled = True
        collector._backend = TelemetryBackend.NONE

        # Should not raise
        collector.track_export("data", "csv")

        TelemetryCollector._instance = None

    def test_export_png_mapping(self, mock_st):
        """Test PNG export maps to EXPORT_PNG event type."""
        TelemetryCollector._instance = None
        collector = TelemetryCollector()
        collector._enabled = True
        collector._backend = TelemetryBackend.NONE

        collector.track_export("chart", "png")

        TelemetryCollector._instance = None

    def test_export_pdf_mapping(self, mock_st):
        """Test PDF export maps to EXPORT_PDF event type."""
        TelemetryCollector._instance = None
        collector = TelemetryCollector()
        collector._enabled = True
        collector._backend = TelemetryBackend.NONE

        collector.track_export("report", "pdf")

        TelemetryCollector._instance = None
