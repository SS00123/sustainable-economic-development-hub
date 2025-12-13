"""
Observability Tests
Sustainable Economic Development Analytics Hub
Ministry of Economy and Planning

Tests for:
- Structured logging and correlation IDs
- Metrics collection
- Health checks
- Alerting thresholds
"""

import json
import logging
import threading
import time
from datetime import datetime, timezone
from io import StringIO
from unittest.mock import patch, MagicMock

import pytest


class TestCorrelationID:
    """Tests for correlation ID management."""
    
    def test_get_correlation_id_generates_uuid(self):
        """Test that get_correlation_id generates a new UUID."""
        from analytics_hub_platform.infrastructure.observability import (
            get_correlation_id,
            clear_correlation_id,
        )
        
        clear_correlation_id()
        cid = get_correlation_id()
        
        assert cid is not None
        assert len(cid) == 36  # UUID format
        assert cid.count("-") == 4
    
    def test_set_and_get_correlation_id(self):
        """Test setting and retrieving correlation ID."""
        from analytics_hub_platform.infrastructure.observability import (
            set_correlation_id,
            get_correlation_id,
            clear_correlation_id,
        )
        
        test_id = "test-correlation-123"
        set_correlation_id(test_id)
        
        assert get_correlation_id() == test_id
        
        clear_correlation_id()
    
    def test_correlation_context_manager(self):
        """Test correlation_context context manager."""
        from analytics_hub_platform.infrastructure.observability import (
            correlation_context,
            get_correlation_id,
            clear_correlation_id,
        )
        
        clear_correlation_id()
        
        with correlation_context("ctx-123") as cid:
            assert cid == "ctx-123"
            assert get_correlation_id() == "ctx-123"
        
        # Should be cleared after context
        # (or restored to previous if there was one)
    
    def test_correlation_id_thread_isolation(self):
        """Test that correlation IDs are isolated per thread."""
        from analytics_hub_platform.infrastructure.observability import (
            set_correlation_id,
            get_correlation_id,
            clear_correlation_id,
        )
        
        results = {}
        
        def thread_func(thread_id):
            set_correlation_id(f"thread-{thread_id}")
            time.sleep(0.01)  # Let other threads run
            results[thread_id] = get_correlation_id()
            clear_correlation_id()
        
        threads = [threading.Thread(target=thread_func, args=(i,)) for i in range(5)]
        
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # Each thread should have its own ID
        for i in range(5):
            assert results[i] == f"thread-{i}"


class TestStructuredLogging:
    """Tests for structured JSON logging."""
    
    def test_structured_log_formatter_json_output(self):
        """Test that StructuredLogFormatter outputs valid JSON."""
        from analytics_hub_platform.infrastructure.observability import (
            StructuredLogFormatter,
            set_correlation_id,
            clear_correlation_id,
        )
        
        set_correlation_id("log-test-123")
        
        formatter = StructuredLogFormatter()
        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        
        output = formatter.format(record)
        
        # Should be valid JSON
        data = json.loads(output)
        
        assert data["level"] == "INFO"
        assert data["logger"] == "test.logger"
        assert data["message"] == "Test message"
        assert data["correlation_id"] == "log-test-123"
        assert "timestamp" in data
        
        clear_correlation_id()
    
    def test_context_logger_includes_correlation_id(self):
        """Test that ContextLogger includes correlation ID in logs."""
        from analytics_hub_platform.infrastructure.observability import (
            ContextLogger,
            set_correlation_id,
            clear_correlation_id,
        )
        
        set_correlation_id("ctx-log-456")
        
        logger = ContextLogger("test.context")
        
        with patch.object(logger._logger, 'log') as mock_log:
            logger.info("Test message", user_id="123")
            
            mock_log.assert_called_once()
            call_args = mock_log.call_args
            extra = call_args[1]["extra"]
            
            assert extra["correlation_id"] == "ctx-log-456"
            assert extra["user_id"] == "123"
        
        clear_correlation_id()
    
    def test_get_context_logger(self):
        """Test get_context_logger factory function."""
        from analytics_hub_platform.infrastructure.observability import get_context_logger
        
        logger = get_context_logger("test.module")
        
        assert isinstance(logger, object)
        assert hasattr(logger, "info")
        assert hasattr(logger, "error")
        assert hasattr(logger, "warning")


class TestMetricsCollector:
    """Tests for MetricsCollector."""
    
    @pytest.fixture(autouse=True)
    def reset_metrics(self):
        """Reset metrics before each test."""
        from analytics_hub_platform.infrastructure.observability import get_metrics
        get_metrics().reset()
        yield
        get_metrics().reset()
    
    def test_increment_counter(self):
        """Test counter increment."""
        from analytics_hub_platform.infrastructure.observability import (
            get_metrics,
            increment_counter,
        )
        
        increment_counter("test_requests_total")
        increment_counter("test_requests_total")
        increment_counter("test_requests_total", value=3)
        
        metrics = get_metrics()
        assert metrics.get_counter("test_requests_total") == 5
    
    def test_counter_with_labels(self):
        """Test counter with labels."""
        from analytics_hub_platform.infrastructure.observability import (
            get_metrics,
            increment_counter,
        )
        
        increment_counter("http_requests", labels={"method": "GET", "status": "200"})
        increment_counter("http_requests", labels={"method": "POST", "status": "201"})
        increment_counter("http_requests", labels={"method": "GET", "status": "200"})
        
        metrics = get_metrics()
        assert metrics.get_counter("http_requests", {"method": "GET", "status": "200"}) == 2
        assert metrics.get_counter("http_requests", {"method": "POST", "status": "201"}) == 1
    
    def test_set_gauge(self):
        """Test gauge setting."""
        from analytics_hub_platform.infrastructure.observability import (
            get_metrics,
            set_gauge,
        )
        
        set_gauge("active_connections", 10)
        set_gauge("active_connections", 15)
        
        metrics = get_metrics()
        assert metrics.get_gauge("active_connections") == 15
    
    def test_observe_histogram(self):
        """Test histogram observations."""
        from analytics_hub_platform.infrastructure.observability import (
            get_metrics,
            observe_histogram,
        )
        
        for value in [0.1, 0.2, 0.3, 0.5, 1.0, 2.0]:
            observe_histogram("request_duration", value)
        
        metrics = get_metrics()
        stats = metrics.get_histogram_stats("request_duration")
        
        assert stats["count"] == 6
        assert stats["min"] == 0.1
        assert stats["max"] == 2.0
        assert "avg" in stats
        assert "p50" in stats
        assert "p99" in stats
    
    def test_export_prometheus_format(self):
        """Test Prometheus export format."""
        from analytics_hub_platform.infrastructure.observability import (
            get_metrics,
            increment_counter,
            set_gauge,
        )
        
        increment_counter("http_requests", labels={"method": "GET"})
        set_gauge("memory_usage", 1024)
        
        metrics = get_metrics()
        output = metrics.export_prometheus()
        
        assert "http_requests_total" in output
        assert "memory_usage" in output
        assert "method=GET" in output
    
    def test_metrics_thread_safety(self):
        """Test metrics are thread-safe."""
        from analytics_hub_platform.infrastructure.observability import (
            get_metrics,
            increment_counter,
        )
        
        errors = []
        
        def increment_many():
            try:
                for _ in range(100):
                    increment_counter("concurrent_counter")
            except Exception as e:
                errors.append(e)
        
        threads = [threading.Thread(target=increment_many) for _ in range(10)]
        
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        assert len(errors) == 0
        assert get_metrics().get_counter("concurrent_counter") == 1000


class TestTimingUtilities:
    """Tests for timing utilities."""
    
    @pytest.fixture(autouse=True)
    def reset_metrics(self):
        """Reset metrics before each test."""
        from analytics_hub_platform.infrastructure.observability import get_metrics
        get_metrics().reset()
        yield
        get_metrics().reset()
    
    def test_timed_operation_context_manager(self):
        """Test timed_operation context manager."""
        from analytics_hub_platform.infrastructure.observability import (
            timed_operation,
            get_metrics,
        )
        
        with timed_operation("test_operation"):
            time.sleep(0.01)
        
        stats = get_metrics().get_histogram_stats("test_operation_duration_seconds")
        
        assert stats["count"] == 1
        assert stats["min"] >= 0.01
    
    def test_timed_decorator(self):
        """Test @timed decorator."""
        from analytics_hub_platform.infrastructure.observability import (
            timed,
            get_metrics,
        )
        
        @timed("decorated_function")
        def slow_function():
            time.sleep(0.01)
            return "done"
        
        result = slow_function()
        
        assert result == "done"
        
        stats = get_metrics().get_histogram_stats("decorated_function_duration_seconds")
        assert stats["count"] == 1


class TestHealthChecker:
    """Tests for HealthChecker."""
    
    def test_register_and_check(self):
        """Test registering and running health checks."""
        from analytics_hub_platform.infrastructure.observability import (
            HealthChecker,
            HealthCheckResult,
        )
        
        checker = HealthChecker()
        
        def healthy_check():
            return HealthCheckResult(name="test", healthy=True, message="OK")
        
        checker.register("test", healthy_check)
        result = checker.check("test")
        
        assert result.healthy is True
        assert result.message == "OK"
        assert result.latency_ms > 0
    
    def test_check_unknown(self):
        """Test checking unknown health check."""
        from analytics_hub_platform.infrastructure.observability import HealthChecker
        
        checker = HealthChecker()
        result = checker.check("nonexistent")
        
        assert result.healthy is False
        assert "Unknown" in result.message
    
    def test_check_all(self):
        """Test checking all health checks."""
        from analytics_hub_platform.infrastructure.observability import (
            HealthChecker,
            HealthCheckResult,
        )
        
        checker = HealthChecker()
        
        checker.register("db", lambda: HealthCheckResult(name="db", healthy=True))
        checker.register("cache", lambda: HealthCheckResult(name="cache", healthy=True))
        
        results = checker.check_all()
        
        assert len(results) == 2
        assert results["db"].healthy is True
        assert results["cache"].healthy is True
    
    def test_is_healthy(self):
        """Test overall health status."""
        from analytics_hub_platform.infrastructure.observability import (
            HealthChecker,
            HealthCheckResult,
        )
        
        checker = HealthChecker()
        
        checker.register("ok", lambda: HealthCheckResult(name="ok", healthy=True))
        checker.register("bad", lambda: HealthCheckResult(name="bad", healthy=False))
        
        assert checker.is_healthy() is False
    
    def test_get_summary(self):
        """Test health check summary."""
        from analytics_hub_platform.infrastructure.observability import (
            HealthChecker,
            HealthCheckResult,
        )
        
        checker = HealthChecker()
        checker.register("test", lambda: HealthCheckResult(name="test", healthy=True))
        
        summary = checker.get_summary()
        
        assert summary["status"] == "healthy"
        assert "timestamp" in summary
        assert "checks" in summary
        assert "test" in summary["checks"]
    
    def test_health_check_exception_handling(self):
        """Test that exceptions in health checks are handled."""
        from analytics_hub_platform.infrastructure.observability import HealthChecker
        
        checker = HealthChecker()
        
        def failing_check():
            raise RuntimeError("Connection failed")
        
        checker.register("failing", failing_check)
        result = checker.check("failing")
        
        assert result.healthy is False
        assert "Connection failed" in result.message


class TestAlertThreshold:
    """Tests for AlertThreshold."""
    
    def test_alert_threshold_operators(self):
        """Test alert threshold operators."""
        from analytics_hub_platform.infrastructure.observability import AlertThreshold
        
        # Greater than
        gt = AlertThreshold(name="Test", metric="m", operator="gt", threshold=10, severity="warning")
        assert gt.check(15) is True
        assert gt.check(10) is False
        assert gt.check(5) is False
        
        # Less than
        lt = AlertThreshold(name="Test", metric="m", operator="lt", threshold=10, severity="warning")
        assert lt.check(5) is True
        assert lt.check(10) is False
        assert lt.check(15) is False
        
        # Greater than or equal
        gte = AlertThreshold(name="Test", metric="m", operator="gte", threshold=10, severity="warning")
        assert gte.check(15) is True
        assert gte.check(10) is True
        assert gte.check(5) is False
    
    def test_alert_format_message(self):
        """Test alert message formatting."""
        from analytics_hub_platform.infrastructure.observability import AlertThreshold
        
        alert = AlertThreshold(
            name="High Latency",
            metric="latency",
            operator="gt",
            threshold=1.0,
            severity="warning",
            message_template="Latency {value}s exceeds {threshold}s",
        )
        
        message = alert.format_message(2.5)
        assert "2.5" in message
        assert "1.0" in message


class TestAlertManager:
    """Tests for AlertManager."""
    
    @pytest.fixture(autouse=True)
    def reset_metrics(self):
        """Reset metrics before each test."""
        from analytics_hub_platform.infrastructure.observability import get_metrics
        get_metrics().reset()
        yield
        get_metrics().reset()
    
    def test_check_alerts_triggered(self):
        """Test that alerts are triggered when thresholds exceeded."""
        from analytics_hub_platform.infrastructure.observability import (
            AlertManager,
            AlertThreshold,
            get_metrics,
            increment_counter,
        )
        
        # Set up a counter that exceeds threshold
        for _ in range(150):
            increment_counter("test_errors")
        
        manager = AlertManager([
            AlertThreshold(
                name="High Errors",
                metric="test_errors",
                operator="gt",
                threshold=100,
                severity="critical",
            )
        ])
        
        alerts = manager.check_alerts(get_metrics())
        
        assert len(alerts) == 1
        assert alerts[0]["name"] == "High Errors"
        assert alerts[0]["severity"] == "critical"
    
    def test_check_alerts_not_triggered(self):
        """Test that alerts are not triggered when below threshold."""
        from analytics_hub_platform.infrastructure.observability import (
            AlertManager,
            AlertThreshold,
            get_metrics,
            increment_counter,
        )
        
        for _ in range(50):
            increment_counter("test_errors")
        
        manager = AlertManager([
            AlertThreshold(
                name="High Errors",
                metric="test_errors",
                operator="gt",
                threshold=100,
                severity="critical",
            )
        ])
        
        alerts = manager.check_alerts(get_metrics())
        
        assert len(alerts) == 0


class TestAPIObservability:
    """Integration tests for API observability."""
    
    @pytest.fixture
    def client(self):
        """Get test client."""
        from fastapi.testclient import TestClient
        from main_api import app
        return TestClient(app)
    
    def test_health_endpoint(self, client):
        """Test /health endpoint."""
        response = client.get("/health")
        
        assert response.status_code in [200, 503]
        
        data = response.json()
        assert "status" in data
        assert "timestamp" in data
        assert "checks" in data
    
    def test_liveness_endpoint(self, client):
        """Test /health/live endpoint."""
        response = client.get("/health/live")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "alive"
    
    def test_readiness_endpoint(self, client):
        """Test /health/ready endpoint."""
        response = client.get("/health/ready")
        
        # May be 200 or 503 depending on dependencies
        assert response.status_code in [200, 503]
        data = response.json()
        assert data["status"] in ["ready", "not_ready"]
    
    def test_metrics_endpoint(self, client):
        """Test /metrics endpoint."""
        # Make some requests first to generate metrics
        client.get("/")
        client.get("/api/v1/health")
        
        response = client.get("/metrics")
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/plain; charset=utf-8"
    
    def test_correlation_id_in_response(self, client):
        """Test that correlation ID is returned in response headers."""
        response = client.get("/")
        
        # Correlation ID should be in response headers
        assert "x-correlation-id" in response.headers
        
        cid = response.headers["x-correlation-id"]
        assert len(cid) == 36  # UUID format
    
    def test_custom_correlation_id_propagated(self, client):
        """Test that custom correlation ID is propagated."""
        custom_id = "custom-correlation-123"
        
        response = client.get("/", headers={"X-Correlation-ID": custom_id})
        
        assert response.headers.get("x-correlation-id") == custom_id
