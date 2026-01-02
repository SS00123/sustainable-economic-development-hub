"""
KPI Utilities Tests
Sustainable Economic Development Analytics Hub

Tests for KPI utility functions.
"""

from analytics_hub_platform.utils.kpi_utils import (
    KPI_UNITS,
    PERCENTAGE_KPIS,
    format_delta,
    format_kpi_value,
    get_delta_suffix,
    get_kpi_unit,
)


class TestGetKpiUnit:
    """Tests for get_kpi_unit function."""

    def test_gdp_growth_unit(self):
        """Test GDP growth returns percentage."""
        assert get_kpi_unit("gdp_growth") == "%"

    def test_gdp_total_unit(self):
        """Test GDP total returns M SAR."""
        assert get_kpi_unit("gdp_total") == "M SAR"

    def test_green_jobs_unit(self):
        """Test green jobs returns K (thousands)."""
        assert get_kpi_unit("green_jobs") == "K"

    def test_sustainability_index_unit(self):
        """Test sustainability index has no unit."""
        assert get_kpi_unit("sustainability_index") == ""

    def test_unknown_kpi_unit(self):
        """Test unknown KPI returns empty string."""
        assert get_kpi_unit("unknown_kpi") == ""

    def test_co2_per_gdp_unit(self):
        """Test CO2 per GDP unit."""
        assert get_kpi_unit("co2_per_gdp") == "t/M SAR"


class TestGetDeltaSuffix:
    """Tests for get_delta_suffix function."""

    def test_percentage_kpi_returns_pp(self):
        """Test percentage KPIs return ' pp' suffix."""
        assert get_delta_suffix("gdp_growth") == " pp"
        assert get_delta_suffix("unemployment_rate") == " pp"
        assert get_delta_suffix("renewable_share") == " pp"

    def test_non_percentage_kpi_returns_percent(self):
        """Test non-percentage KPIs return '%' suffix."""
        assert get_delta_suffix("sustainability_index") == "%"
        assert get_delta_suffix("green_jobs") == "%"
        assert get_delta_suffix("co2_index") == "%"

    def test_unknown_kpi_returns_percent(self):
        """Test unknown KPI returns '%' suffix."""
        assert get_delta_suffix("unknown_kpi") == "%"


class TestFormatKpiValue:
    """Tests for format_kpi_value function."""

    def test_format_with_unit(self):
        """Test formatting with unit suffix."""
        result = format_kpi_value(3.25, "gdp_growth")
        assert result == "3.25%"

    def test_format_without_unit(self):
        """Test formatting without unit suffix."""
        result = format_kpi_value(72.5, "sustainability_index")
        assert result == "72.50"

    def test_format_with_thousands_separator(self):
        """Test formatting large numbers with thousands separator."""
        result = format_kpi_value(1234567.89, "gdp_total")
        assert result == "1,234,567.89M SAR"

    def test_format_custom_decimals(self):
        """Test formatting with custom decimal places."""
        result = format_kpi_value(3.256789, "gdp_growth", decimals=1)
        assert result == "3.3%"


class TestFormatDelta:
    """Tests for format_delta function."""

    def test_positive_delta_with_sign(self):
        """Test positive delta with sign."""
        result = format_delta(2.5, "sustainability_index", show_sign=True)
        assert result == "+2.5%"

    def test_negative_delta(self):
        """Test negative delta."""
        result = format_delta(-1.3, "sustainability_index")
        assert result == "-1.3%"

    def test_delta_for_percentage_kpi(self):
        """Test delta for percentage KPI uses pp."""
        result = format_delta(1.5, "gdp_growth")
        assert result == "+1.5 pp"

    def test_delta_without_sign(self):
        """Test delta without sign for positive value."""
        result = format_delta(2.5, "sustainability_index", show_sign=False)
        assert result == "2.5%"


class TestConstants:
    """Tests for module constants."""

    def test_kpi_units_not_empty(self):
        """Test KPI_UNITS is populated."""
        assert len(KPI_UNITS) > 0

    def test_percentage_kpis_not_empty(self):
        """Test PERCENTAGE_KPIS is populated."""
        assert len(PERCENTAGE_KPIS) > 0

    def test_gdp_growth_is_percentage_kpi(self):
        """Test gdp_growth is in PERCENTAGE_KPIS."""
        assert "gdp_growth" in PERCENTAGE_KPIS
