"""
Validator Tests
Sustainable Economic Development Analytics Hub

Tests for data validation functions.
"""

import pytest
import pandas as pd
import numpy as np

from analytics_hub_platform.utils.validators import (
    validate_indicator_data,
    validate_filter_params,
    validate_kpi_value,
    validate_export_request,
    sanitize_string,
    ValidationError,
    ValidationResult,
)
from analytics_hub_platform.domain.models import FilterParams


class TestValidateIndicatorData:
    """Tests for indicator data validation."""
    
    def test_validate_valid_data(self, sample_indicator_data):
        """Test validation of valid data."""
        result = validate_indicator_data(sample_indicator_data)
        
        assert result.is_valid
        assert len(result.errors) == 0
    
    def test_validate_empty_data(self):
        """Test validation of empty DataFrame."""
        result = validate_indicator_data(pd.DataFrame())
        
        assert result.is_valid  # Empty is valid, just warns
        assert "empty" in result.warnings[0].lower()
    
    def test_validate_none_data(self):
        """Test validation of None data."""
        result = validate_indicator_data(None)
        
        assert not result.is_valid
        assert len(result.errors) > 0
    
    def test_validate_missing_columns(self):
        """Test validation with missing required columns."""
        data = pd.DataFrame({
            "year": [2024],
            "region": ["Riyadh"],
        })
        
        result = validate_indicator_data(data)
        
        assert not result.is_valid
        assert any("Missing required columns" in e for e in result.errors)
    
    def test_validate_invalid_quarter(self):
        """Test validation with invalid quarter values."""
        data = pd.DataFrame({
            "year": [2024, 2024],
            "quarter": [1, 5],  # 5 is invalid
            "region": ["Riyadh", "Riyadh"],
            "sustainability_index": [70, 75],
            "tenant_id": ["test", "test"],
        })
        
        result = validate_indicator_data(data)
        
        assert not result.is_valid
        assert any("quarter" in e.lower() for e in result.errors)
    
    def test_validate_out_of_range_percentage(self):
        """Test validation with out-of-range percentage."""
        data = pd.DataFrame({
            "year": [2024],
            "quarter": [4],
            "region": ["Riyadh"],
            "sustainability_index": [70],
            "tenant_id": ["test"],
            "renewable_energy_pct": [150],  # Out of range
        })
        
        result = validate_indicator_data(data)
        
        # Should warn about out-of-range value
        assert len(result.warnings) > 0
    
    def test_validate_strict_mode(self):
        """Test validation in strict mode."""
        with pytest.raises(ValidationError):
            validate_indicator_data(None, strict=True)


class TestValidateFilterParams:
    """Tests for filter parameter validation."""
    
    def test_validate_valid_params(self, sample_filter_params):
        """Test validation of valid filter params."""
        result = validate_filter_params(sample_filter_params)
        
        assert result.is_valid
    
    def test_validate_missing_tenant(self):
        """Test validation with missing tenant."""
        params = FilterParams(tenant_id="")
        
        result = validate_filter_params(params)
        
        assert not result.is_valid
        assert any("tenant_id" in e for e in result.errors)
    
    def test_validate_invalid_quarter(self):
        """Test validation with invalid quarter."""
        params = FilterParams(tenant_id="test", quarter=5)
        
        result = validate_filter_params(params)
        
        assert not result.is_valid
    
    def test_validate_invalid_year(self):
        """Test validation with year out of range."""
        params = FilterParams(tenant_id="test", year=1900)
        
        result = validate_filter_params(params)
        
        assert not result.is_valid
    
    def test_validate_large_limit_warning(self):
        """Test validation warns on large limit."""
        params = FilterParams(tenant_id="test", limit=50000)
        
        result = validate_filter_params(params)
        
        assert result.is_valid
        assert len(result.warnings) > 0


class TestValidateKPIValue:
    """Tests for KPI value validation."""
    
    def test_validate_valid_value(self):
        """Test validation of valid KPI value."""
        result = validate_kpi_value("test_kpi", 75.5)
        
        assert result.is_valid
    
    def test_validate_null_value(self):
        """Test validation of null value."""
        result = validate_kpi_value("test_kpi", None)
        
        assert result.is_valid  # Null is valid, just warns
        assert len(result.warnings) > 0
    
    def test_validate_nan_value(self):
        """Test validation of NaN value."""
        result = validate_kpi_value("test_kpi", float("nan"))
        
        assert not result.is_valid
    
    def test_validate_infinite_value(self):
        """Test validation of infinite value."""
        result = validate_kpi_value("test_kpi", float("inf"))
        
        assert not result.is_valid
    
    def test_validate_with_thresholds(self):
        """Test validation with threshold checks."""
        thresholds = {"min": 0, "max": 100}
        
        result = validate_kpi_value("test_kpi", 150, thresholds)
        
        assert len(result.warnings) > 0
        assert "above maximum" in result.warnings[0]


class TestValidateExportRequest:
    """Tests for export request validation."""
    
    def test_validate_valid_export(self):
        """Test validation of valid export request."""
        result = validate_export_request("xlsx", 1000)
        
        assert result.is_valid
    
    def test_validate_invalid_format(self):
        """Test validation with invalid format."""
        result = validate_export_request("docx", 1000)
        
        assert not result.is_valid
    
    def test_validate_too_many_rows(self):
        """Test validation with too many rows."""
        result = validate_export_request("xlsx", 200000)
        
        assert not result.is_valid
    
    def test_validate_large_export_warning(self):
        """Test validation warns on large export."""
        result = validate_export_request("xlsx", 60000)
        
        assert result.is_valid
        assert len(result.warnings) > 0


class TestSanitizeString:
    """Tests for string sanitization."""
    
    def test_sanitize_normal_string(self):
        """Test sanitizing normal string."""
        result = sanitize_string("Hello World")
        
        assert result == "Hello World"
    
    def test_sanitize_with_html(self):
        """Test sanitizing string with HTML."""
        result = sanitize_string("<script>alert('xss')</script>Hello")
        
        assert "<script>" not in result
        assert "Hello" in result
    
    def test_sanitize_truncation(self):
        """Test string truncation."""
        long_string = "x" * 1000
        result = sanitize_string(long_string, max_length=100)
        
        assert len(result) == 100
    
    def test_sanitize_null_bytes(self):
        """Test removing null bytes."""
        result = sanitize_string("Hello\x00World")
        
        assert "\x00" not in result
    
    def test_sanitize_whitespace(self):
        """Test whitespace trimming."""
        result = sanitize_string("  Hello World  ")
        
        assert result == "Hello World"


class TestValidationResult:
    """Tests for ValidationResult class."""
    
    def test_validation_result_init(self):
        """Test ValidationResult initialization."""
        result = ValidationResult()
        
        assert result.is_valid
        assert len(result.errors) == 0
        assert len(result.warnings) == 0
    
    def test_add_error(self):
        """Test adding error to result."""
        result = ValidationResult()
        result.add_error("Test error")
        
        assert not result.is_valid
        assert "Test error" in result.errors
    
    def test_add_warning(self):
        """Test adding warning to result."""
        result = ValidationResult()
        result.add_warning("Test warning")
        
        assert result.is_valid  # Warnings don't invalidate
        assert "Test warning" in result.warnings
    
    def test_merge_results(self):
        """Test merging validation results."""
        result1 = ValidationResult()
        result1.add_error("Error 1")
        
        result2 = ValidationResult()
        result2.add_warning("Warning 1")
        
        merged = result1.merge(result2)
        
        assert not merged.is_valid
        assert len(merged.errors) == 1
        assert len(merged.warnings) == 1
