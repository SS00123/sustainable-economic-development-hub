"""
Domain Model Tests
Sustainable Economic Development Analytics Hub

Tests for domain models and Pydantic schemas.
"""

import pytest
from datetime import datetime, date

from analytics_hub_platform.domain.models import (
    FilterParams,
    KPIValue,
    KPIStatus,
    DashboardSummary,
    TimeSeriesPoint,
    RegionalComparison,
    IndicatorRecord,
)


class TestFilterParams:
    """Tests for FilterParams model."""
    
    def test_filter_params_defaults(self):
        """Test FilterParams with default values."""
        params = FilterParams(tenant_id="test")
        
        assert params.tenant_id == "test"
        assert params.year is None
        assert params.quarter is None
        assert params.region is None
        assert params.limit is None
        assert params.offset is None
    
    def test_filter_params_with_values(self):
        """Test FilterParams with all values."""
        params = FilterParams(
            tenant_id="tenant_001",
            year=2024,
            quarter=4,
            region="Riyadh",
            limit=100,
            offset=0,
        )
        
        assert params.tenant_id == "tenant_001"
        assert params.year == 2024
        assert params.quarter == 4
        assert params.region == "Riyadh"
        assert params.limit == 100
        assert params.offset == 0


class TestKPIValue:
    """Tests for KPIValue model."""
    
    def test_kpi_value_creation(self):
        """Test KPIValue creation."""
        kpi = KPIValue(
            id="sustainability_index",
            name="Sustainability Index",
            value=72.5,
            unit="",
            status=KPIStatus.GREEN,
            trend=5.2,
            higher_is_better=True,
        )
        
        assert kpi.id == "sustainability_index"
        assert kpi.value == 72.5
        assert kpi.status == KPIStatus.GREEN
        assert kpi.trend == 5.2
    
    def test_kpi_status_enum(self):
        """Test KPIStatus enum values."""
        assert KPIStatus.GREEN.value == "green"
        assert KPIStatus.AMBER.value == "amber"
        assert KPIStatus.RED.value == "red"
        assert KPIStatus.NEUTRAL.value == "neutral"


class TestDashboardSummary:
    """Tests for DashboardSummary model."""
    
    def test_dashboard_summary_creation(self):
        """Test DashboardSummary creation."""
        kpis = [
            KPIValue(
                id="test_kpi",
                name="Test KPI",
                value=50.0,
                unit="%",
                status=KPIStatus.AMBER,
            ),
        ]
        
        summary = DashboardSummary(
            tenant_id="test",
            period="Q4 2024",
            sustainability_index=72.5,
            kpis=kpis,
            trend=3.5,
        )
        
        assert summary.tenant_id == "test"
        assert summary.sustainability_index == 72.5
        assert len(summary.kpis) == 1
        assert summary.trend == 3.5


class TestTimeSeriesPoint:
    """Tests for TimeSeriesPoint model."""
    
    def test_timeseries_point_creation(self):
        """Test TimeSeriesPoint creation."""
        point = TimeSeriesPoint(
            period="Q4 2024",
            value=65.5,
            year=2024,
            quarter=4,
        )
        
        assert point.period == "Q4 2024"
        assert point.value == 65.5
        assert point.year == 2024
        assert point.quarter == 4


class TestRegionalComparison:
    """Tests for RegionalComparison model."""
    
    def test_regional_comparison_creation(self):
        """Test RegionalComparison creation."""
        comparison = RegionalComparison(
            region="Riyadh",
            value=75.5,
            rank=1,
            national_average=68.2,
            variance=7.3,
        )
        
        assert comparison.region == "Riyadh"
        assert comparison.rank == 1
        assert comparison.variance == 7.3


class TestIndicatorRecord:
    """Tests for IndicatorRecord model."""
    
    def test_indicator_record_creation(self):
        """Test IndicatorRecord creation."""
        record = IndicatorRecord(
            tenant_id="test",
            year=2024,
            quarter=4,
            region="Riyadh",
            sustainability_index=72.5,
            co2_per_gdp=0.42,
            renewable_energy_pct=12.5,
            data_quality_score=85.0,
        )
        
        assert record.tenant_id == "test"
        assert record.year == 2024
        assert record.sustainability_index == 72.5
        assert record.co2_per_gdp == 0.42
    
    def test_indicator_record_optional_fields(self):
        """Test IndicatorRecord with optional fields."""
        record = IndicatorRecord(
            tenant_id="test",
            year=2024,
            quarter=4,
            region="Riyadh",
        )
        
        assert record.sustainability_index is None
        assert record.co2_per_gdp is None
        assert record.renewable_energy_pct is None
