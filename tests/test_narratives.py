"""
Narrative Generation Tests
Sustainable Economic Development Analytics Hub

Tests for narrative generation utilities.
"""

from analytics_hub_platform.domain.models import DashboardSummary
from analytics_hub_platform.utils.narratives import (
    _format_signed_percent,
    _get_item_name,
    _get_item_value,
    _plural,
    generate_director_narrative,
    generate_executive_narrative,
    generate_narrative,
)


class TestHelperFunctions:
    """Tests for helper functions."""

    def test_plural_singular(self):
        """Test plural function with singular value."""
        assert _plural(1, "indicator", "indicators") == "indicator"

    def test_plural_plural(self):
        """Test plural function with plural value."""
        assert _plural(0, "indicator", "indicators") == "indicators"
        assert _plural(2, "indicator", "indicators") == "indicators"
        assert _plural(100, "indicator", "indicators") == "indicators"

    def test_get_item_name_display_name(self):
        """Test _get_item_name with display_name."""
        item = {"display_name": "GDP Growth", "name": "gdp", "kpi_name": "gdp_growth"}
        assert _get_item_name(item) == "GDP Growth"

    def test_get_item_name_fallback_name(self):
        """Test _get_item_name fallback to name."""
        item = {"name": "GDP Growth", "kpi_name": "gdp_growth"}
        assert _get_item_name(item) == "GDP Growth"

    def test_get_item_name_fallback_kpi_name(self):
        """Test _get_item_name fallback to kpi_name."""
        item = {"kpi_name": "gdp_growth"}
        assert _get_item_name(item) == "gdp_growth"

    def test_get_item_name_unknown(self):
        """Test _get_item_name returns Unknown for empty dict."""
        item = {}
        assert _get_item_name(item) == "Unknown"

    def test_get_item_value_change_percent(self):
        """Test _get_item_value with change_percent."""
        item = {"change_percent": 5.5, "value": 10.0}
        assert _get_item_value(item) == 5.5

    def test_get_item_value_fallback_value(self):
        """Test _get_item_value fallback to value."""
        item = {"value": 10.0}
        assert _get_item_value(item) == 10.0

    def test_get_item_value_default(self):
        """Test _get_item_value returns 0 for empty dict."""
        item = {}
        assert _get_item_value(item) == 0.0

    def test_format_signed_percent_positive(self):
        """Test positive percentage formatting."""
        assert _format_signed_percent(5.5) == "+5.5%"

    def test_format_signed_percent_negative(self):
        """Test negative percentage formatting."""
        assert _format_signed_percent(-3.2) == "-3.2%"

    def test_format_signed_percent_zero(self):
        """Test zero percentage formatting."""
        assert _format_signed_percent(0) == "0.0%"


class TestExecutiveNarrative:
    """Tests for executive narrative generation."""

    def test_generate_executive_narrative_dict(self):
        """Test narrative generation from dict snapshot."""
        snapshot = {
            "period": "Q4 2024",
            "metrics": {
                "sustainability_index": {"value": 72.5, "status": "green"},
                "gdp_growth": {"value": 3.2, "status": "green"},
                "unemployment_rate": {"value": 5.5, "status": "amber"},
            },
            "top_improvements": [
                {"display_name": "GDP Growth", "change_percent": 1.5},
            ],
            "top_deteriorations": [
                {"display_name": "Unemployment", "change_percent": -0.5},
            ],
        }

        narrative = generate_executive_narrative(snapshot, "en")

        assert narrative is not None
        assert len(narrative) > 0
        assert "Sustainability" in narrative or "indicator" in narrative

    def test_generate_executive_narrative_empty(self):
        """Test narrative with empty snapshot."""
        snapshot = {
            "period": "Q4 2024",
            "metrics": {},
            "top_improvements": [],
            "top_deteriorations": [],
        }

        narrative = generate_executive_narrative(snapshot, "en")

        assert narrative is not None

    def test_generate_executive_narrative_arabic(self):
        """Test Arabic narrative generation."""
        snapshot = {
            "period": "Q4 2024",
            "metrics": {
                "sustainability_index": {"value": 72.5, "status": "green"},
            },
            "top_improvements": [],
            "top_deteriorations": [],
        }

        narrative = generate_executive_narrative(snapshot, "ar")

        assert narrative is not None


class TestDirectorNarrative:
    """Tests for director narrative generation."""

    def test_generate_director_narrative(self):
        """Test director narrative generation."""
        snapshot = {
            "period": "Q4 2024",
            "metrics": {
                "sustainability_index": {"value": 72.5, "status": "green"},
                "gdp_growth": {"value": 3.2, "status": "green"},
            },
            "top_improvements": [
                {"display_name": "Renewable Share", "change_percent": 2.5},
            ],
            "top_deteriorations": [],
        }

        narrative = generate_director_narrative(snapshot, "en")

        assert narrative is not None
        assert "Performance" in narrative or "indicator" in narrative


class TestDashboardSummaryNarrative:
    """Tests for narrative from DashboardSummary."""

    def test_generate_narrative_from_summary(self):
        """Test narrative from DashboardSummary object."""
        summary = DashboardSummary(
            total_indicators=10,
            on_target_count=6,
            warning_count=3,
            critical_count=1,
            improving_count=4,
            declining_count=2,
            average_achievement=75.0,
            sustainability_index=72.5,
            top_performers=[],
            attention_needed=[],
            period="Q4 2024",
        )

        narrative = generate_narrative(summary, "en")

        assert narrative is not None
        assert "72.5" in narrative or "Sustainability" in narrative


class TestLLMService:
    """Tests for LLM service with error handling."""

    def test_mock_llm_provider_english(self):
        """Test MockLLMProvider with English."""
        from analytics_hub_platform.domain.llm_service import MockLLMProvider

        provider = MockLLMProvider()
        response = provider.generate_recommendations(
            kpi_data={"test": "data"}, anomalies=[], forecasts=[], language="en"
        )

        assert response is not None
        assert response.provider == "mock"
        assert response.model == "mock-v1"
        assert response.executive_summary is not None
        assert len(response.key_insights) > 0
        assert len(response.recommendations) > 0

    def test_mock_llm_provider_arabic(self):
        """Test MockLLMProvider with Arabic."""
        from analytics_hub_platform.domain.llm_service import MockLLMProvider

        provider = MockLLMProvider()
        response = provider.generate_recommendations(
            kpi_data={"test": "data"}, anomalies=[], forecasts=[], language="ar"
        )

        assert response is not None
        assert response.provider == "mock"
        assert "رؤية" in response.executive_summary or "مؤشرات" in response.executive_summary

    def test_get_llm_service_auto(self):
        """Test auto LLM service selection."""
        from analytics_hub_platform.domain.llm_service import get_llm_service

        # Should return mock provider when no API keys available
        service = get_llm_service("auto")

        assert service is not None

    def test_get_llm_service_mock(self):
        """Test explicit mock provider selection."""
        from analytics_hub_platform.domain.llm_service import MockLLMProvider, get_llm_service

        service = get_llm_service("mock")

        assert isinstance(service, MockLLMProvider)

    def test_generate_recommendations_function(self):
        """Test high-level generate_recommendations function."""
        from analytics_hub_platform.domain.llm_service import generate_recommendations

        result = generate_recommendations(
            kpi_data={"sustainability_index": 75.0},
            anomalies=[{"kpi_id": "gdp", "severity": "warning"}],
            forecasts=[{"kpi_id": "gdp", "predicted_value": 3.5}],
            language="en",
            provider="mock",
        )

        assert result is not None
        assert "executive_summary" in result
        assert "key_insights" in result
        assert "recommendations" in result
        assert "provider" in result
        assert result["provider"] == "mock"

    def test_llm_response_serialization(self):
        """Test that LLM responses can be serialized."""
        import json

        from analytics_hub_platform.domain.llm_service import generate_recommendations

        result = generate_recommendations(
            kpi_data={"test": "data"}, anomalies=[], forecasts=[], language="en", provider="mock"
        )

        # Should be JSON serializable
        json_str = json.dumps(result, default=str)
        assert json_str is not None
        assert len(json_str) > 0
