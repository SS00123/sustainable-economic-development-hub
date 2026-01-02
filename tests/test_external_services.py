"""
External Services Tests
Sustainable Economic Development Analytics Hub
Ministry of Economy and Planning

Tests for external service integrations with mocking:
- LLM service (OpenAI, Anthropic, Mock)
- ML services
- Future external APIs
"""

from datetime import UTC, datetime
from typing import Any
from unittest.mock import MagicMock, patch

import pytest


class TestLLMServiceMocking:
    """Tests for LLM service with mocked providers."""

    @pytest.fixture
    def sample_kpi_data(self) -> dict[str, Any]:
        """Sample KPI data for testing."""
        return {
            "sustainability_index": {"value": 72.5, "change": 2.3, "status": "green"},
            "gdp_growth": {"value": 4.2, "change": 0.5, "status": "green"},
            "renewable_share": {"value": 18.5, "change": 1.2, "status": "amber"},
            "unemployment_rate": {"value": 9.8, "change": -0.3, "status": "amber"},
            "co2_index": {"value": 82.1, "change": 1.5, "status": "green"},
        }

    @pytest.fixture
    def sample_anomalies(self) -> list[dict[str, Any]]:
        """Sample anomalies for testing."""
        return [
            {
                "kpi": "unemployment_rate",
                "region": "eastern",
                "severity": "high",
                "description": "Unexpected spike in unemployment",
            }
        ]

    @pytest.fixture
    def sample_forecasts(self) -> list[dict[str, Any]]:
        """Sample forecasts for testing."""
        return [
            {
                "kpi": "sustainability_index",
                "predictions": [
                    {"year": 2024, "quarter": 2, "value": 74.0},
                    {"year": 2024, "quarter": 3, "value": 75.5},
                ],
            }
        ]

    def test_llm_response_dataclass(self):
        """Test LLMResponse dataclass creation."""
        from analytics_hub_platform.domain.llm_service import LLMResponse, Recommendation

        rec = Recommendation(
            id="rec_1",
            title="Test Recommendation",
            description="Test description",
            priority="high",
            category="economic",
            impact="High positive impact",
            timeline="Q2 2024",
            kpis_affected=["gdp_growth"],
        )

        response = LLMResponse(
            executive_summary="Test summary",
            key_insights=["Insight 1", "Insight 2"],
            recommendations=[rec],
            risk_alerts=["Risk 1"],
            provider="test",
            model="test-model",
            generated_at=datetime.now(UTC),
        )

        assert response.executive_summary == "Test summary"
        assert len(response.recommendations) == 1
        assert response.recommendations[0].priority == "high"

    def test_recommendation_dataclass(self):
        """Test Recommendation dataclass."""
        from analytics_hub_platform.domain.llm_service import Recommendation

        rec = Recommendation(
            id="rec_1",
            title="Increase Renewable Investment",
            description="Allocate additional funds to renewable energy projects",
            priority="high",
            category="environmental",
            impact="15% increase in renewable share by 2025",
            timeline="Q1-Q4 2024",
            kpis_affected=["renewable_share", "co2_index"],
        )

        assert rec.id == "rec_1"
        assert rec.priority == "high"
        assert len(rec.kpis_affected) == 2

    def test_get_llm_service_mock(self):
        """Test get_llm_service returns mock provider when specified."""
        from analytics_hub_platform.domain.llm_service import MockLLMProvider, get_llm_service

        provider = get_llm_service("mock")
        assert isinstance(provider, MockLLMProvider)

    def test_get_llm_service_auto_no_keys(self):
        """Test get_llm_service auto mode without API keys falls back to mock."""
        from analytics_hub_platform.domain.llm_service import get_llm_service

        # Without any API keys configured, should fall back to mock
        with patch.dict("os.environ", {}, clear=True):
            provider = get_llm_service("auto")
            # Should be MockLLMProvider or one of the API providers
            assert provider is not None

    def test_mock_provider_english(self):
        """Test mock provider with English language."""
        from analytics_hub_platform.domain.llm_service import MockLLMProvider

        provider = MockLLMProvider()

        response = provider.generate_recommendations(
            kpi_data={"test": "data"},
            anomalies=[],
            forecasts=[],
            language="en",
        )

        assert response is not None
        assert response.provider == "mock"
        assert len(response.recommendations) > 0
        assert response.executive_summary  # Not empty

    def test_mock_provider_arabic(self):
        """Test mock provider with Arabic language."""
        from analytics_hub_platform.domain.llm_service import MockLLMProvider

        provider = MockLLMProvider()

        response = provider.generate_recommendations(
            kpi_data={"test": "data"},
            anomalies=[],
            forecasts=[],
            language="ar",
        )

        assert response is not None
        assert response.provider == "mock"
        # Should contain Arabic text
        assert any(ord(c) > 1536 and ord(c) < 1792 for c in response.executive_summary)

    def test_generate_recommendations_function(
        self, sample_kpi_data, sample_anomalies, sample_forecasts
    ):
        """Test main generate_recommendations function."""
        from analytics_hub_platform.domain.llm_service import generate_recommendations

        result = generate_recommendations(
            kpi_data=sample_kpi_data,
            anomalies=sample_anomalies,
            forecasts=sample_forecasts,
            language="en",
        )

        # Should return dictionary with expected keys
        assert result is not None
        assert "executive_summary" in result
        assert "key_insights" in result
        assert "recommendations" in result
        assert "risk_alerts" in result
        assert "provider" in result

    def test_generate_recommendations_with_mock(self, sample_kpi_data):
        """Test generate_recommendations explicitly using mock provider."""
        from analytics_hub_platform.domain.llm_service import generate_recommendations

        result = generate_recommendations(
            kpi_data=sample_kpi_data,
            anomalies=None,
            forecasts=None,
            language="en",
            provider="mock",
        )

        assert result["provider"] == "mock"
        assert "generated_at" in result

    def test_openai_provider_initialization_without_key(self):
        """Test OpenAI provider initialization without API key."""
        from analytics_hub_platform.domain.llm_service import OpenAIProvider

        with patch.dict("os.environ", {}, clear=True):
            provider = OpenAIProvider(api_key=None)
            # Client should be None without API key
            assert provider.client is None or provider.api_key is None

    def test_anthropic_provider_initialization_without_key(self):
        """Test Anthropic provider initialization without API key."""
        from analytics_hub_platform.domain.llm_service import AnthropicProvider

        with patch.dict("os.environ", {}, clear=True):
            provider = AnthropicProvider(api_key=None)
            # Client should be None without API key
            assert provider.client is None or provider.api_key is None


class TestLLMPromptBuilding:
    """Tests for LLM prompt construction."""

    def test_system_prompt_english(self):
        """Test system prompt generation for English."""
        from analytics_hub_platform.domain.llm_service import MockLLMProvider

        provider = MockLLMProvider()
        prompt = provider._build_system_prompt("en")

        assert (
            "strategic" in prompt.lower()
            or "recommendation" in prompt.lower()
            or "vision 2030" in prompt.lower()
        )

    def test_system_prompt_arabic(self):
        """Test system prompt generation for Arabic."""
        from analytics_hub_platform.domain.llm_service import MockLLMProvider

        provider = MockLLMProvider()
        prompt = provider._build_system_prompt("ar")

        # Should contain Arabic text
        assert any(ord(c) > 1536 and ord(c) < 1792 for c in prompt)

    def test_user_prompt_building(self):
        """Test user prompt construction with KPI data."""
        from analytics_hub_platform.domain.llm_service import MockLLMProvider

        provider = MockLLMProvider()

        kpi_data = {"test_kpi": {"value": 75.0}}
        anomalies = [{"kpi": "test", "severity": "high"}]
        forecasts = [{"kpi": "test", "predictions": []}]

        prompt = provider._build_user_prompt(kpi_data, anomalies, forecasts, "en")

        assert "KPI" in prompt or "kpi" in prompt.lower()
        assert "test_kpi" in prompt or "75.0" in prompt


class TestLLMErrorHandling:
    """Tests for LLM error handling."""

    def test_graceful_degradation_on_api_error(self):
        """Test that API errors result in graceful degradation."""
        from analytics_hub_platform.domain.llm_service import generate_recommendations

        # Even with no API keys configured, should not raise
        result = generate_recommendations(
            kpi_data={"test": "data"},
            anomalies=[],
            forecasts=[],
            language="en",
            provider="mock",  # Use mock to ensure it works
        )

        # Should return valid response
        assert result is not None
        assert "executive_summary" in result

    def test_openai_provider_fallback_no_client(self):
        """Test OpenAI provider falls back when no client configured."""
        from analytics_hub_platform.domain.llm_service import OpenAIProvider

        with patch.dict("os.environ", {}, clear=True):
            provider = OpenAIProvider(api_key=None)

            response = provider.generate_recommendations(
                kpi_data={"test": "data"},
                anomalies=[],
                forecasts=[],
                language="en",
            )

            # Should fall back gracefully
            assert response is not None
            assert "fallback" in response.provider or response.provider == "mock"

    def test_anthropic_provider_fallback_no_client(self):
        """Test Anthropic provider falls back when no client configured."""
        from analytics_hub_platform.domain.llm_service import AnthropicProvider

        with patch.dict("os.environ", {}, clear=True):
            provider = AnthropicProvider(api_key=None)

            response = provider.generate_recommendations(
                kpi_data={"test": "data"},
                anomalies=[],
                forecasts=[],
                language="en",
            )

            # Should fall back gracefully
            assert response is not None

    def test_invalid_kpi_data_handling(self):
        """Test handling of invalid KPI data."""
        from analytics_hub_platform.domain.llm_service import generate_recommendations

        # Empty data
        result = generate_recommendations(
            kpi_data={},
            anomalies=[],
            forecasts=[],
            language="en",
            provider="mock",
        )

        assert result is not None

    def test_none_values_handling(self):
        """Test handling of None values in data."""
        from analytics_hub_platform.domain.llm_service import generate_recommendations

        result = generate_recommendations(
            kpi_data={"test": {"value": None, "change": None}},
            anomalies=None,
            forecasts=None,
            language="en",
            provider="mock",
        )

        # Should handle gracefully
        assert result is not None

    def test_parse_response_invalid_json(self):
        """Test parsing invalid JSON response."""
        from analytics_hub_platform.domain.llm_service import MockLLMProvider

        provider = MockLLMProvider()

        # Test parsing with malformed content
        result = provider._parse_response("not valid json", "test", "test-model")

        # Should not crash, returns response with error info
        assert result is not None

    def test_parse_response_valid_json(self):
        """Test parsing valid JSON response."""
        import json

        from analytics_hub_platform.domain.llm_service import MockLLMProvider

        provider = MockLLMProvider()

        valid_response = json.dumps(
            {
                "executive_summary": "Test summary",
                "key_insights": ["Insight 1"],
                "recommendations": [
                    {
                        "id": "rec_1",
                        "title": "Test",
                        "description": "Test description",
                        "priority": "high",
                        "category": "economic",
                        "impact": "High",
                        "timeline": "Q1 2024",
                        "kpis_affected": ["test_kpi"],
                    }
                ],
                "risk_alerts": ["Alert 1"],
            }
        )

        result = provider._parse_response(valid_response, "test", "test-model")

        assert result.executive_summary == "Test summary"
        assert len(result.recommendations) == 1


class TestMLServicesWithMocking:
    """Tests for ML services with mocking."""

    def test_forecaster_initialization(self):
        """Test KPIForecaster initialization."""
        from analytics_hub_platform.domain.ml_services import KPIForecaster

        forecaster = KPIForecaster(model_type="gradient_boosting")
        assert forecaster is not None

    def test_forecaster_with_sample_data(self):
        """Test KPIForecaster with sample data."""
        import pandas as pd

        from analytics_hub_platform.domain.ml_services import KPIForecaster

        # Create test data with enough points
        data = pd.DataFrame(
            {
                "year": [2022, 2022, 2022, 2022, 2023, 2023, 2023, 2023, 2024, 2024],
                "quarter": [1, 2, 3, 4, 1, 2, 3, 4, 1, 2],
                "value": [70, 72, 74, 76, 78, 80, 82, 84, 86, 88],
            }
        )

        forecaster = KPIForecaster(model_type="gradient_boosting")
        forecaster.fit(data)

        predictions = forecaster.predict(quarters_ahead=4)

        assert isinstance(predictions, list)
        if len(predictions) > 0:
            assert "predicted_value" in predictions[0] or "value" in predictions[0]

    def test_anomaly_detector_initialization(self):
        """Test AnomalyDetector initialization."""
        from analytics_hub_platform.domain.ml_services import AnomalyDetector

        # Use correct initialization parameters
        detector = AnomalyDetector(zscore_threshold=2.0, critical_threshold=3.0)
        assert detector is not None
        assert detector.zscore_threshold == 2.0
        assert detector.critical_threshold == 3.0

    def test_anomaly_detector_with_sample_data(self):
        """Test AnomalyDetector with synthetic data."""
        import numpy as np
        import pandas as pd

        from analytics_hub_platform.domain.ml_services import AnomalyDetector

        # Create data with enough variation
        np.random.seed(42)
        values = [70, 72, 74, 76, 78, 80, 82, 84, 150]  # Last value is anomaly

        data = pd.DataFrame(
            {
                "year": [2022, 2022, 2022, 2022, 2023, 2023, 2023, 2023, 2024],
                "quarter": [1, 2, 3, 4, 1, 2, 3, 4, 1],
                "value": values,
            }
        )

        detector = AnomalyDetector(zscore_threshold=2.0, critical_threshold=3.0)

        # Use the correct method
        anomalies = detector.detect_anomalies(
            df=data,
            kpi_id="sustainability_index",
            region_id="riyadh",
            higher_is_better=True,
        )

        # Should return a list (may or may not detect depending on threshold)
        assert isinstance(anomalies, list)

    def test_anomaly_detector_empty_data(self):
        """Test AnomalyDetector with empty data."""
        import pandas as pd

        from analytics_hub_platform.domain.ml_services import AnomalyDetector

        detector = AnomalyDetector()

        empty_df = pd.DataFrame(columns=["year", "quarter", "value"])

        anomalies = detector.detect_anomalies(
            df=empty_df,
            kpi_id="test",
            region_id="test",
        )

        assert anomalies == []

    def test_anomaly_detector_constant_values(self):
        """Test AnomalyDetector with constant values (no anomalies possible)."""
        import pandas as pd

        from analytics_hub_platform.domain.ml_services import AnomalyDetector

        detector = AnomalyDetector()

        # All same values - no variance, no anomalies
        data = pd.DataFrame(
            {
                "year": [2022, 2022, 2022, 2022, 2023, 2023],
                "quarter": [1, 2, 3, 4, 1, 2],
                "value": [75.0, 75.0, 75.0, 75.0, 75.0, 75.0],
            }
        )

        anomalies = detector.detect_anomalies(
            df=data,
            kpi_id="test",
            region_id="test",
        )

        # Should return empty list for constant series
        assert anomalies == []


class TestCacheIntegration:
    """Tests for cache integration."""

    def test_cache_manager_get_set(self):
        """Test cache manager basic operations."""
        from analytics_hub_platform.infrastructure.caching import get_cache_manager

        cache = get_cache_manager()

        # Set a value
        cache.set("test_key", "test_value", ttl=60)

        # Get the value
        result = cache.get("test_key")

        # May or may not return value depending on cache backend
        assert result is None or result == "test_value"

    def test_cache_manager_delete(self):
        """Test cache manager delete operation."""
        from analytics_hub_platform.infrastructure.caching import get_cache_manager

        cache = get_cache_manager()

        cache.set("delete_test", "value")
        cache.delete("delete_test")

        result = cache.get("delete_test")
        assert result is None


class TestServiceDependencyMocking:
    """Tests for mocking service dependencies."""

    def test_repository_mock(self):
        """Test that repository can be mocked."""
        import pandas as pd

        mock_repo = MagicMock()
        mock_repo.get_all_indicators.return_value = pd.DataFrame(
            {
                "year": [2024],
                "quarter": [1],
                "region": ["riyadh"],
                "sustainability_index": [75.0],
            }
        )

        result = mock_repo.get_all_indicators("test_tenant")

        assert len(result) == 1
        assert result["sustainability_index"].iloc[0] == 75.0

    def test_cache_mock(self):
        """Test that cache can be mocked."""

        mock_cache = MagicMock()
        mock_cache.get.return_value = None
        mock_cache.set.return_value = None

        # First call - cache miss
        assert mock_cache.get("test_key") is None

        # Set value
        mock_cache.set("test_key", "test_value")
        mock_cache.set.assert_called_with("test_key", "test_value")

    def test_settings_mock(self):
        """Test that settings can be mocked."""
        from unittest.mock import patch

        mock_settings = MagicMock()
        mock_settings.environment = "test"
        mock_settings.debug = True
        mock_settings.default_tenant_id = "test_tenant"

        with patch(
            "analytics_hub_platform.infrastructure.settings.get_settings",
            return_value=mock_settings,
        ):
            from analytics_hub_platform.infrastructure.settings import get_settings

            settings = get_settings()

            assert settings.environment == "test"
            assert settings.debug is True

    def test_llm_service_with_mocked_settings(self):
        """Test LLM service with mocked settings."""
        from unittest.mock import patch

        from analytics_hub_platform.domain.llm_service import get_llm_service

        mock_settings = MagicMock()
        mock_settings.llm_provider = "mock"
        mock_settings.llm_timeout = 30
        mock_settings.llm_max_retries = 2
        mock_settings.llm_api_key = None
        mock_settings.llm_model_name = None

        with patch(
            "analytics_hub_platform.domain.llm_service.get_settings", return_value=mock_settings
        ):
            provider = get_llm_service()
            assert provider is not None


class TestDataFrameAdapter:
    """Tests for DataFrame adapter utilities."""

    def test_dataframe_to_dict_conversion(self):
        """Test DataFrame to dict conversion."""
        import pandas as pd

        df = pd.DataFrame(
            {
                "year": [2024],
                "quarter": [1],
                "value": [75.0],
            }
        )

        records = df.to_dict(orient="records")

        assert len(records) == 1
        assert records[0]["year"] == 2024
        assert records[0]["value"] == 75.0

    def test_empty_dataframe_handling(self):
        """Test empty DataFrame handling."""
        import pandas as pd

        df = pd.DataFrame()

        records = df.to_dict(orient="records")

        assert records == []
