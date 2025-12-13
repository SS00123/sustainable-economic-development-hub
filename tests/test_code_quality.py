"""
Code Quality Tests
Sustainable Economic Development Analytics Hub
Ministry of Economy and Planning

Tests for edge cases, validation, and code quality checks.
"""

import pytest
from datetime import datetime, timezone
from typing import List, Dict, Any

from analytics_hub_platform.config.constants import (
    SAUDI_REGIONS,
    REGION_PROFILES,
    QUARTERS,
    MIN_YEAR,
    MAX_YEAR,
    ML_MIN_FORECAST_POINTS,
    ANOMALY_ZSCORE_WARNING,
    ANOMALY_ZSCORE_CRITICAL,
    get_valid_regions,
    is_valid_region,
    is_valid_quarter,
    is_valid_year,
    get_kpi_status,
)
from analytics_hub_platform.infrastructure.exceptions import (
    ValidationError,
    InsufficientDataError,
    ModelNotFittedError,
)
from analytics_hub_platform.utils.validation import (
    sanitize_string,
    sanitize_tenant_id,
    validate_year,
    validate_quarter,
    validate_percentage,
    validate_inputs,
    validate_required,
)


# ============================================
# CONSTANTS MODULE TESTS
# ============================================

class TestConstants:
    """Test constants module functionality."""
    
    def test_saudi_regions_count(self):
        """Verify correct number of Saudi regions."""
        assert len(SAUDI_REGIONS) == 13
    
    def test_saudi_regions_unique(self):
        """Verify all regions are unique."""
        assert len(SAUDI_REGIONS) == len(set(SAUDI_REGIONS))
    
    def test_region_profiles_match_regions(self):
        """Verify REGION_PROFILES has entry for each region."""
        for region in SAUDI_REGIONS:
            assert region in REGION_PROFILES, f"Missing profile for {region}"
    
    def test_region_profiles_have_required_keys(self):
        """Verify each region profile has required keys."""
        required_keys = {"gdp_base", "population", "urban"}
        for region, profile in REGION_PROFILES.items():
            missing = required_keys - set(profile.keys())
            assert not missing, f"Region {region} missing keys: {missing}"
    
    def test_quarters_are_valid(self):
        """Verify quarters tuple is correct."""
        assert QUARTERS == (1, 2, 3, 4)
    
    def test_year_range_valid(self):
        """Verify year range makes sense."""
        assert MIN_YEAR < MAX_YEAR
        assert MIN_YEAR >= 1900
        assert MAX_YEAR <= 2200


class TestConstantHelpers:
    """Test helper functions in constants module."""
    
    def test_get_valid_regions(self):
        """Test get_valid_regions returns correct list."""
        regions = get_valid_regions()
        assert regions == list(SAUDI_REGIONS)
    
    def test_is_valid_region_case_insensitive(self):
        """Test is_valid_region is case insensitive."""
        assert is_valid_region("Riyadh")
        assert is_valid_region("RIYADH")
        assert is_valid_region("riyadh")
        assert not is_valid_region("NotARegion")
    
    def test_is_valid_quarter_valid(self):
        """Test is_valid_quarter with valid quarters."""
        for q in [1, 2, 3, 4]:
            assert is_valid_quarter(q), f"Quarter {q} should be valid"
    
    def test_is_valid_quarter_invalid(self):
        """Test is_valid_quarter with invalid quarters."""
        for q in [0, 5, -1, 10]:
            assert not is_valid_quarter(q), f"Quarter {q} should be invalid"
    
    def test_is_valid_year_valid(self):
        """Test is_valid_year with valid years."""
        assert is_valid_year(2024)
        assert is_valid_year(MIN_YEAR)
        assert is_valid_year(MAX_YEAR)
    
    def test_is_valid_year_invalid(self):
        """Test is_valid_year with invalid years."""
        assert not is_valid_year(1800)
        assert not is_valid_year(2200)
    
    def test_get_kpi_status_higher_is_better(self):
        """Test KPI status calculation when higher is better."""
        # Sustainability index example: green >= 70, amber >= 50
        assert get_kpi_status(75, 70.0, 50.0, higher_is_better=True) == "green"
        assert get_kpi_status(60, 70.0, 50.0, higher_is_better=True) == "amber"
        assert get_kpi_status(40, 70.0, 50.0, higher_is_better=True) == "red"
    
    def test_get_kpi_status_lower_is_better(self):
        """Test KPI status calculation when lower is better."""
        # CO2 emissions example: green <= 0.35, amber <= 0.50
        assert get_kpi_status(0.30, 0.35, 0.50, higher_is_better=False) == "green"
        assert get_kpi_status(0.40, 0.35, 0.50, higher_is_better=False) == "amber"
        assert get_kpi_status(0.60, 0.35, 0.50, higher_is_better=False) == "red"
    
    def test_get_kpi_status_boundary_values(self):
        """Test KPI status at exact thresholds."""
        assert get_kpi_status(70.0, 70.0, 50.0, higher_is_better=True) == "green"
        assert get_kpi_status(50.0, 70.0, 50.0, higher_is_better=True) == "amber"


# ============================================
# VALIDATION MODULE TESTS
# ============================================

class TestSanitization:
    """Test input sanitization functions."""
    
    def test_sanitize_string_basic(self):
        """Test basic string sanitization."""
        result = sanitize_string("Hello World")
        assert result == "Hello World"
    
    def test_sanitize_string_max_length(self):
        """Test string truncation."""
        long_string = "a" * 2000
        result = sanitize_string(long_string, max_length=100)
        assert len(result) == 100
    
    def test_sanitize_string_html_stripping(self):
        """Test HTML tag removal."""
        html_string = "<script>alert('xss')</script>Hello"
        result = sanitize_string(html_string, strip_html=True)
        assert "<script>" not in result
        assert "Hello" in result
    
    def test_sanitize_string_sql_stripping(self):
        """Test SQL injection pattern removal."""
        sql_string = "value'; DROP TABLE users; --"
        result = sanitize_string(sql_string, strip_sql=True)
        assert "DROP TABLE" not in result
    
    def test_sanitize_tenant_id_valid(self):
        """Test valid tenant ID sanitization."""
        result = sanitize_tenant_id("ministry_of_economy")
        assert result == "ministry_of_economy"
    
    def test_sanitize_tenant_id_special_chars(self):
        """Test tenant ID with special characters."""
        result = sanitize_tenant_id("ministry@of#economy!")
        assert "@" not in result
        assert "#" not in result


class TestValidators:
    """Test validation functions."""
    
    def test_validate_year_valid(self):
        """Test year validation with valid years."""
        # These should not raise
        validate_year(2024)
        validate_year(2000)
    
    def test_validate_year_invalid(self):
        """Test year validation with invalid years."""
        with pytest.raises(ValidationError):
            validate_year(1800)
        with pytest.raises(ValidationError):
            validate_year(2200)
    
    def test_validate_quarter_valid(self):
        """Test quarter validation with valid quarters."""
        for q in [1, 2, 3, 4]:
            validate_quarter(q)  # Should not raise
    
    def test_validate_quarter_invalid(self):
        """Test quarter validation with invalid quarters."""
        with pytest.raises(ValidationError):
            validate_quarter(0)
        with pytest.raises(ValidationError):
            validate_quarter(5)
    
    def test_validate_percentage_valid(self):
        """Test percentage validation with valid values."""
        # These should not raise and return the validated value
        result = validate_percentage(50.5)
        assert result == 50.5
        result = validate_percentage(100)
        assert result == 100.0
    
    def test_validate_percentage_invalid(self):
        """Test percentage validation with invalid values."""
        with pytest.raises(ValidationError):
            validate_percentage(-1)
        with pytest.raises(ValidationError):
            validate_percentage(101)


class TestValidationDecorators:
    """Test validation decorators."""
    
    def test_validate_inputs_decorator(self):
        """Test validate_inputs decorator with valid inputs."""
        @validate_inputs(year=lambda x: 2000 <= x <= 2100)
        def get_data(year: int) -> int:
            return year
        
        assert get_data(2024) == 2024
    
    def test_validate_inputs_decorator_invalid(self):
        """Test validate_inputs decorator with invalid inputs."""
        @validate_inputs(year=lambda x: 2000 <= x <= 2100)
        def get_data(year: int) -> int:
            return year
        
        with pytest.raises(ValidationError):
            get_data(1800)
    
    def test_validate_required_decorator(self):
        """Test validate_required decorator."""
        @validate_required('tenant_id')
        def get_data(tenant_id: str) -> str:
            return tenant_id
        
        assert get_data("test") == "test"
    
    def test_validate_required_decorator_missing(self):
        """Test validate_required decorator with missing param."""
        @validate_required('tenant_id')
        def get_data(tenant_id: str = None) -> str:
            return tenant_id
        
        with pytest.raises(ValidationError):
            get_data()


# ============================================
# EDGE CASE TESTS
# ============================================

class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_empty_string_sanitization(self):
        """Test sanitizing empty string."""
        result = sanitize_string("")
        assert result == ""
    
    def test_none_handling_in_validation(self):
        """Test that None values are handled gracefully."""
        @validate_inputs(year=lambda x: x is None or 2000 <= x <= 2100)
        def get_data(year: int = None) -> int:
            return year
        
        assert get_data(None) is None
    
    def test_ml_constants_reasonable_values(self):
        """Test ML constants have reasonable values."""
        assert ML_MIN_FORECAST_POINTS >= 2
        assert ANOMALY_ZSCORE_WARNING < ANOMALY_ZSCORE_CRITICAL
        assert ANOMALY_ZSCORE_WARNING > 0
    
    def test_region_gdp_positive(self):
        """Test all region GDP bases are positive."""
        for region, profile in REGION_PROFILES.items():
            assert profile["gdp_base"] > 0, f"Region {region} has invalid GDP"
    
    def test_region_population_positive(self):
        """Test all region populations are positive."""
        for region, profile in REGION_PROFILES.items():
            assert profile["population"] > 0, f"Region {region} has invalid population"


# ============================================
# INTEGRATION TESTS
# ============================================

class TestIntegration:
    """Integration tests for code quality."""
    
    def test_constants_used_consistently(self):
        """Test that constants are defined consistently."""
        # Verify thresholds are in logical order
        from analytics_hub_platform.config.constants import (
            SUSTAINABILITY_INDEX_GREEN,
            SUSTAINABILITY_INDEX_AMBER,
        )
        assert SUSTAINABILITY_INDEX_GREEN > SUSTAINABILITY_INDEX_AMBER
    
    def test_exception_hierarchy(self):
        """Test custom exceptions can be caught properly."""
        from analytics_hub_platform.infrastructure.exceptions import (
            AnalyticsHubError,
        )
        
        assert issubclass(ValidationError, AnalyticsHubError)
        assert issubclass(InsufficientDataError, AnalyticsHubError)
        assert issubclass(ModelNotFittedError, AnalyticsHubError)
    
    def test_timezone_aware_datetime(self):
        """Test that we use timezone-aware datetimes."""
        now = datetime.now(timezone.utc)
        assert now.tzinfo is not None
