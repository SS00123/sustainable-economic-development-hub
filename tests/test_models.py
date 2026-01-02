"""
Domain Model Tests
Sustainable Economic Development Analytics Hub

Tests for domain models and Pydantic schemas.
"""

from analytics_hub_platform.domain.models import (
    DashboardSummary,
    FilterParams,
    IndicatorRecord,
    KPIDefinition,
    KPIStatus,
    KPIThresholds,
    RegionalComparison,
    Tenant,
    TimeSeriesPoint,
    User,
    UserRole,
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

    def test_filter_params_with_values(self):
        """Test FilterParams with all values."""
        params = FilterParams(
            tenant_id="tenant_001",
            year=2024,
            quarter=4,
            region="Riyadh",
        )

        assert params.tenant_id == "tenant_001"
        assert params.year == 2024
        assert params.quarter == 4
        assert params.region == "Riyadh"

    def test_filter_params_to_query_params(self):
        """Test converting FilterParams to query dict."""
        params = FilterParams(
            tenant_id="test",
            year=2024,
            region="Riyadh",
        )

        query = params.to_query_params()
        assert query["tenant_id"] == "test"
        assert query["year"] == 2024
        assert query["region"] == "Riyadh"


class TestKPIStatus:
    """Tests for KPIStatus enum."""

    def test_kpi_status_enum(self):
        """Test KPIStatus enum values."""
        assert KPIStatus.GREEN.value == "green"
        assert KPIStatus.AMBER.value == "amber"
        assert KPIStatus.RED.value == "red"


class TestDashboardSummary:
    """Tests for DashboardSummary model."""

    def test_dashboard_summary_creation(self):
        """Test DashboardSummary creation."""
        summary = DashboardSummary(
            total_indicators=10,
            on_target_count=7,
            warning_count=2,
            critical_count=1,
            period="Q4 2024",
            sustainability_index=72.5,
        )

        assert summary.total_indicators == 10
        assert summary.sustainability_index == 72.5
        assert summary.period == "Q4 2024"

    def test_dashboard_summary_calculate_percentages(self):
        """Test percentage calculation."""
        summary = DashboardSummary(
            total_indicators=10,
            on_target_count=7,
            warning_count=2,
            critical_count=1,
        )
        summary.calculate_percentages()

        assert summary.on_target_percentage == 70.0
        assert summary.warning_percentage == 20.0
        assert summary.critical_percentage == 10.0


class TestTimeSeriesPoint:
    """Tests for TimeSeriesPoint model."""

    def test_timeseries_point_creation(self):
        """Test TimeSeriesPoint creation."""
        point = TimeSeriesPoint(
            period="Q4 2024",
            value=65.5,
            status=KPIStatus.GREEN,
        )

        assert point.period == "Q4 2024"
        assert point.value == 65.5
        assert point.status == KPIStatus.GREEN


class TestRegionalComparison:
    """Tests for RegionalComparison model."""

    def test_regional_comparison_creation(self):
        """Test RegionalComparison creation."""
        comparison = RegionalComparison(
            kpi_id="sustainability_index",
            kpi_name="Sustainability Index",
            regions=["Riyadh", "Makkah"],
            values=[75.5, 68.2],
            statuses=[KPIStatus.GREEN, KPIStatus.AMBER],
            national_average=70.0,
        )

        assert comparison.kpi_id == "sustainability_index"
        assert len(comparison.regions) == 2
        assert comparison.national_average == 70.0


class TestIndicatorRecord:
    """Tests for IndicatorRecord model."""

    def test_indicator_record_creation(self):
        """Test IndicatorRecord creation."""
        record = IndicatorRecord(
            id=1,
            tenant_id="test",
            year=2024,
            quarter=4,
            region="Riyadh",
            sustainability_index=72.5,
            co2_per_gdp=0.42,
            data_quality_score=85.0,
        )

        assert record.tenant_id == "test"
        assert record.year == 2024
        assert record.sustainability_index == 72.5
        assert record.co2_per_gdp == 0.42

    def test_indicator_record_optional_fields(self):
        """Test IndicatorRecord with optional fields."""
        record = IndicatorRecord(
            id=1,
            tenant_id="test",
            year=2024,
            quarter=4,
            region="Riyadh",
        )

        assert record.sustainability_index is None
        assert record.co2_per_gdp is None


class TestUserRole:
    """Tests for UserRole enum."""

    def test_user_roles(self):
        """Test UserRole enum values."""
        assert UserRole.EXECUTIVE == "executive"
        assert UserRole.DIRECTOR == "director"
        assert UserRole.ANALYST == "analyst"


class TestTenant:
    """Tests for Tenant model."""

    def test_tenant_creation(self):
        """Test Tenant creation."""
        tenant = Tenant(
            id="mep-sa-001",
            name="Ministry of Economy and Planning",
            country="Saudi Arabia",
        )

        assert tenant.id == "mep-sa-001"
        assert tenant.name == "Ministry of Economy and Planning"


class TestUser:
    """Tests for User model."""

    def test_user_creation(self):
        """Test User creation."""
        user = User(
            id="user-001",
            email="test@example.com",
            name="Test User",
            role=UserRole.ANALYST,
            tenant_id="mep-sa-001",
        )

        assert user.id == "user-001"
        assert user.role == UserRole.ANALYST


class TestKPIThresholds:
    """Tests for KPIThresholds model."""

    def test_kpi_thresholds_creation(self):
        """Test KPIThresholds creation with all required fields."""
        thresholds = KPIThresholds(
            green_min=70.0,
            green_max=100.0,
            amber_min=50.0,
            amber_max=69.9,
            red_min=0.0,
            red_max=49.9,
        )

        assert thresholds.green_min == 70.0
        assert thresholds.amber_min == 50.0
        assert thresholds.red_max == 49.9


class TestKPIDefinition:
    """Tests for KPIDefinition model."""

    def test_kpi_definition_creation(self):
        """Test KPIDefinition creation with all required fields."""
        definition = KPIDefinition(
            id="sustainability_index",
            display_name_en="Sustainability Index",
            display_name_ar="مؤشر الاستدامة",
            description_en="Overall sustainability score",
            description_ar="الدرجة العامة للاستدامة",
            formula_human_readable="Weighted average of component KPIs",
            unit="%",
            higher_is_better=True,
            category="environment",
        )

        assert definition.id == "sustainability_index"
        assert definition.higher_is_better is True
        assert definition.category == "environment"
