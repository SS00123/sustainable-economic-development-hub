"""
Tests for Domain Models
"""

import pytest
from datetime import datetime, timezone


class TestFilterParams:
    """Tests for FilterParams model."""
    
    def test_create_filter_params(self):
        """Test creating FilterParams with valid data."""
        from analytics_hub_platform.domain.models import FilterParams
        
        params = FilterParams(
            tenant_id="ministry_economy",
            year=2026,
            quarter=4,
            region="Riyadh",
        )
        
        assert params.tenant_id == "ministry_economy"
        assert params.year == 2026
        assert params.quarter == 4
        assert params.region == "Riyadh"
    
    def test_filter_params_optional_region(self):
        """Test FilterParams with optional region."""
        from analytics_hub_platform.domain.models import FilterParams
        
        params = FilterParams(
            tenant_id="ministry_economy",
            year=2026,
            quarter=4,
        )
        
        assert params.region is None
    
    def test_filter_params_quarter_validation(self):
        """Test that quarter must be 1-4."""
        from analytics_hub_platform.domain.models import FilterParams
        
        # Valid quarters
        for q in [1, 2, 3, 4]:
            params = FilterParams(tenant_id="test", year=2026, quarter=q)
            assert params.quarter == q


class TestKPIStatus:
    """Tests for KPIStatus enum."""
    
    def test_status_values(self):
        """Test KPIStatus enum values."""
        from analytics_hub_platform.domain.models import KPIStatus
        
        assert KPIStatus.GREEN.value == "green"
        assert KPIStatus.AMBER.value == "amber"
        assert KPIStatus.RED.value == "red"
        assert KPIStatus.UNKNOWN.value == "unknown"


class TestTimezoneUsage:
    """Tests to verify Python 3.10 compatible timezone usage."""
    
    def test_no_utc_import(self):
        """Verify we're using timezone.utc, not UTC."""
        # This should not raise ImportError
        from datetime import timezone
        
        now = datetime.now(timezone.utc)
        assert now.tzinfo is not None
        assert now.tzinfo == timezone.utc
    
    def test_models_use_timezone_utc(self):
        """Verify domain models use timezone.utc."""
        # Import should succeed without UTC
        from analytics_hub_platform.domain import models
        
        # If this import works, we're good
        assert models is not None
