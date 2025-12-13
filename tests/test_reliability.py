"""
Reliability Tests
Sustainable Economic Development Analytics Hub
Ministry of Economy and Planning

Tests for retry logic, connection handling, error recovery, and validation.
"""

import pytest
import time
import threading
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone

from analytics_hub_platform.infrastructure.exceptions import (
    ExternalServiceError,
    InsufficientDataError,
    ModelNotFittedError,
    ConstantSeriesError,
    DataError,
    ValidationError,
)


class TestRetryLogic:
    """Tests for retry with exponential backoff."""
    
    def test_retry_succeeds_first_attempt(self):
        """Test function succeeds on first attempt."""
        from analytics_hub_platform.infrastructure.retry import retry_with_backoff
        
        call_count = [0]
        
        @retry_with_backoff(max_attempts=3)
        def successful_func():
            call_count[0] += 1
            return "success"
        
        result = successful_func()
        
        assert result == "success"
        assert call_count[0] == 1
    
    def test_retry_succeeds_after_failures(self):
        """Test function succeeds after initial failures."""
        from analytics_hub_platform.infrastructure.retry import retry_with_backoff
        
        call_count = [0]
        
        @retry_with_backoff(max_attempts=3, base_delay=0.1)
        def eventually_succeeds():
            call_count[0] += 1
            if call_count[0] < 3:
                raise ConnectionError("Temporary failure")
            return "success"
        
        result = eventually_succeeds()
        
        assert result == "success"
        assert call_count[0] == 3
    
    def test_retry_exhausted_raises_error(self):
        """Test raises ExternalServiceError after all retries exhausted."""
        from analytics_hub_platform.infrastructure.retry import retry_with_backoff
        
        @retry_with_backoff(
            max_attempts=3,
            base_delay=0.01,
            retryable_exceptions=(ValueError,),
        )
        def always_fails():
            raise ValueError("Always fails")
        
        with pytest.raises(ExternalServiceError) as exc_info:
            always_fails()
        
        assert "3 attempts" in str(exc_info.value)
    
    def test_retry_non_retryable_exception(self):
        """Test non-retryable exceptions are raised immediately."""
        from analytics_hub_platform.infrastructure.retry import retry_with_backoff
        
        call_count = [0]
        
        @retry_with_backoff(
            max_attempts=3,
            retryable_exceptions=(ConnectionError,),
        )
        def raises_type_error():
            call_count[0] += 1
            raise TypeError("Not retryable")
        
        with pytest.raises(TypeError):
            raises_type_error()
        
        # Should only be called once since TypeError isn't retryable
        assert call_count[0] == 1
    
    def test_calculate_delay_exponential(self):
        """Test exponential backoff delay calculation."""
        from analytics_hub_platform.infrastructure.retry import calculate_delay
        
        # Without jitter for predictable testing
        delay0 = calculate_delay(0, base_delay=1.0, jitter=False)
        delay1 = calculate_delay(1, base_delay=1.0, jitter=False)
        delay2 = calculate_delay(2, base_delay=1.0, jitter=False)
        
        assert delay0 == 1.0
        assert delay1 == 2.0
        assert delay2 == 4.0
    
    def test_calculate_delay_max_cap(self):
        """Test delay is capped at max_delay."""
        from analytics_hub_platform.infrastructure.retry import calculate_delay
        
        delay = calculate_delay(10, base_delay=1.0, max_delay=30.0, jitter=False)
        
        assert delay == 30.0
    
    def test_retry_context_manager(self):
        """Test RetryContext context manager."""
        from analytics_hub_platform.infrastructure.retry import RetryContext
        
        attempts = [0]
        
        with RetryContext(max_attempts=3, base_delay=0.01) as retry:
            while retry.should_retry():
                try:
                    attempts[0] += 1
                    if attempts[0] < 3:
                        raise ValueError("Not yet")
                    retry.record_success()
                    break
                except ValueError as e:
                    retry.record_failure(e)
        
        assert attempts[0] == 3


class TestDatabaseConnectionPooling:
    """Tests for database connection pooling."""
    
    def test_check_database_health_returns_dict(self):
        """Test health check returns proper structure."""
        from analytics_hub_platform.infrastructure.db_init import check_database_health
        
        result = check_database_health()
        
        assert isinstance(result, dict)
        assert "status" in result
        assert "connected" in result
        assert "message" in result
    
    def test_get_engine_returns_same_instance(self):
        """Test get_engine returns same instance (singleton)."""
        from analytics_hub_platform.infrastructure.db_init import get_engine
        
        engine1 = get_engine()
        engine2 = get_engine()
        
        assert engine1 is engine2
    
    def test_engine_thread_safety(self):
        """Test engine creation is thread-safe."""
        from analytics_hub_platform.infrastructure.db_init import get_engine
        
        engines = []
        errors = []
        
        def get_engine_in_thread():
            try:
                engine = get_engine()
                engines.append(engine)
            except Exception as e:
                errors.append(e)
        
        threads = [threading.Thread(target=get_engine_in_thread) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        assert len(errors) == 0
        # All engines should be the same instance
        assert all(e is engines[0] for e in engines)


class TestInputValidation:
    """Tests for input validation utilities."""
    
    def test_validate_year_valid(self):
        """Test valid year passes validation."""
        from analytics_hub_platform.utils.validation import validate_year
        
        assert validate_year(2024) == 2024
        assert validate_year("2024") == 2024
    
    def test_validate_year_invalid(self):
        """Test invalid year raises ValidationError."""
        from analytics_hub_platform.utils.validation import validate_year
        
        with pytest.raises(ValidationError):
            validate_year(1800)
        
        with pytest.raises(ValidationError):
            validate_year(2200)
        
        with pytest.raises(ValidationError):
            validate_year("not a number")
    
    def test_validate_quarter_valid(self):
        """Test valid quarter passes validation."""
        from analytics_hub_platform.utils.validation import validate_quarter
        
        assert validate_quarter(1) == 1
        assert validate_quarter(4) == 4
        assert validate_quarter("2") == 2
    
    def test_validate_quarter_invalid(self):
        """Test invalid quarter raises ValidationError."""
        from analytics_hub_platform.utils.validation import validate_quarter
        
        with pytest.raises(ValidationError):
            validate_quarter(0)
        
        with pytest.raises(ValidationError):
            validate_quarter(5)
    
    def test_sanitize_string_removes_html(self):
        """Test HTML tags are removed."""
        from analytics_hub_platform.utils.validation import sanitize_string
        
        result = sanitize_string("<script>alert('xss')</script>Hello")
        
        assert "<script>" not in result
        assert "Hello" in result
    
    def test_sanitize_string_removes_sql_injection(self):
        """Test SQL injection patterns are removed."""
        from analytics_hub_platform.utils.validation import sanitize_string
        
        result = sanitize_string("'; DROP TABLE users; --")
        
        assert "DROP" not in result.upper()
        assert "--" not in result
    
    def test_sanitize_tenant_id_valid(self):
        """Test valid tenant ID passes."""
        from analytics_hub_platform.utils.validation import sanitize_tenant_id
        
        assert sanitize_tenant_id("ministry-001") == "ministry-001"
        assert sanitize_tenant_id("tenant_123") == "tenant_123"
    
    def test_sanitize_tenant_id_invalid(self):
        """Test invalid tenant ID raises ValidationError."""
        from analytics_hub_platform.utils.validation import sanitize_tenant_id
        
        with pytest.raises(ValidationError):
            sanitize_tenant_id("")
        
        with pytest.raises(ValidationError):
            sanitize_tenant_id("a")  # Too short
    
    def test_validate_inputs_decorator(self):
        """Test validate_inputs decorator."""
        from analytics_hub_platform.utils.validation import validate_inputs
        
        @validate_inputs(
            year=lambda x: 2000 <= x <= 2100,
            quarter=lambda x: 1 <= x <= 4,
        )
        def get_data(year: int, quarter: int):
            return f"Data for Q{quarter} {year}"
        
        # Valid inputs
        result = get_data(2024, 2)
        assert result == "Data for Q2 2024"
        
        # Invalid year
        with pytest.raises(ValidationError):
            get_data(1900, 2)
        
        # Invalid quarter
        with pytest.raises(ValidationError):
            get_data(2024, 5)
    
    def test_validate_required_decorator(self):
        """Test validate_required decorator."""
        from analytics_hub_platform.utils.validation import validate_required
        
        @validate_required('name', 'value')
        def process(name: str, value: int, optional: str = None):
            return f"{name}={value}"
        
        # Valid call
        result = process("test", 42)
        assert result == "test=42"
        
        # Missing required param
        with pytest.raises(ValidationError):
            process(None, 42)


class TestMLErrorHandling:
    """Tests for ML service error handling."""
    
    def test_forecaster_insufficient_data(self):
        """Test forecaster raises InsufficientDataError."""
        import pandas as pd
        from analytics_hub_platform.domain.ml_services import KPIForecaster
        
        forecaster = KPIForecaster()
        
        # Too few data points
        df = pd.DataFrame({
            "year": [2024],
            "quarter": [1],
            "value": [100.0],
        })
        
        with pytest.raises(InsufficientDataError) as exc_info:
            forecaster.fit(df)
        
        assert exc_info.value.details.get("required_points") == 4
        assert exc_info.value.details.get("actual_points") == 1
    
    def test_forecaster_constant_series(self):
        """Test forecaster raises ConstantSeriesError."""
        import pandas as pd
        from analytics_hub_platform.domain.ml_services import KPIForecaster
        
        forecaster = KPIForecaster()
        
        # Constant series (zero variance)
        df = pd.DataFrame({
            "year": [2024, 2024, 2024, 2024],
            "quarter": [1, 2, 3, 4],
            "value": [100.0, 100.0, 100.0, 100.0],  # All same value
        })
        
        with pytest.raises(ConstantSeriesError):
            forecaster.fit(df)
    
    def test_forecaster_predict_without_fit(self):
        """Test predicting without fitting raises ModelNotFittedError."""
        from analytics_hub_platform.domain.ml_services import KPIForecaster
        
        forecaster = KPIForecaster()
        
        with pytest.raises(ModelNotFittedError):
            forecaster.predict()
    
    def test_forecaster_nan_values(self):
        """Test forecaster raises DataError for NaN values."""
        import pandas as pd
        import numpy as np
        from analytics_hub_platform.domain.ml_services import KPIForecaster
        
        forecaster = KPIForecaster()
        
        df = pd.DataFrame({
            "year": [2024, 2024, 2024, 2024],
            "quarter": [1, 2, 3, 4],
            "value": [100.0, np.nan, 120.0, 130.0],
        })
        
        with pytest.raises(DataError):
            forecaster.fit(df)


class TestCacheThreadSafety:
    """Tests for cache thread safety under load."""
    
    def test_concurrent_cache_operations(self):
        """Test cache handles concurrent read/write operations."""
        from analytics_hub_platform.infrastructure.caching import CacheManager
        
        cache = CacheManager(default_ttl=300, max_size=1000)
        errors = []
        operations = [0]
        
        def cache_stress_test(thread_id):
            try:
                for i in range(50):
                    key = f"stress-{thread_id}-{i}"
                    cache.set(key, f"value-{i}")
                    value = cache.get(key)
                    if i % 5 == 0:
                        cache.delete(key)
                    operations[0] += 1
            except Exception as e:
                errors.append(e)
        
        threads = [threading.Thread(target=cache_stress_test, args=(i,)) for i in range(20)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        assert len(errors) == 0
        assert operations[0] == 20 * 50  # All operations completed


class TestExceptionHierarchy:
    """Tests for exception hierarchy."""
    
    def test_ml_exceptions_inherit_correctly(self):
        """Test ML exceptions have correct inheritance."""
        from analytics_hub_platform.infrastructure.exceptions import (
            MLError,
            InsufficientDataError,
            ModelNotFittedError,
            ForecastError,
            ConstantSeriesError,
            AnalyticsHubError,
        )
        
        # All ML errors should inherit from MLError
        assert issubclass(InsufficientDataError, MLError)
        assert issubclass(ModelNotFittedError, MLError)
        assert issubclass(ForecastError, MLError)
        assert issubclass(ConstantSeriesError, MLError)
        
        # MLError should inherit from AnalyticsHubError
        assert issubclass(MLError, AnalyticsHubError)
    
    def test_exception_details_preserved(self):
        """Test exception details are preserved."""
        error = InsufficientDataError(
            message="Not enough data",
            required_points=10,
            actual_points=3,
        )
        
        assert error.details["required_points"] == 10
        assert error.details["actual_points"] == 3
        assert "Not enough data" in str(error)
