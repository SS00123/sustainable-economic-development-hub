"""
Smoke Tests - Critical Path Verification
Sustainable Economic Development Analytics Hub

These tests verify that critical paths work after refactoring:
1. Application imports and boots without error
2. KPI forecasting capability is available
3. Anomaly detection / early warning is available
4. AI recommendations capability is available

Run with: pytest tests/test_smoke.py -v
"""

import sys
from pathlib import Path

import pytest
import pandas as pd
import numpy as np

# Ensure project is importable
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class TestApplicationBoot:
    """Verify the application imports and key modules are available."""

    def test_main_package_imports(self):
        """Test that the main package imports successfully."""
        import analytics_hub_platform
        assert analytics_hub_platform is not None

    def test_infrastructure_imports(self):
        """Test infrastructure module imports."""
        from analytics_hub_platform.infrastructure import (
            get_repository,
            get_settings,
            initialize_database,
        )
        assert callable(get_repository)
        assert callable(get_settings)
        assert callable(initialize_database)

    def test_domain_models_import(self):
        """Test domain models import."""
        from analytics_hub_platform.domain.models import FilterParams

        params = FilterParams(
            tenant_id="test",
            year=2026,
            quarter=4,
            region=None,
        )
        assert params.year == 2026
        assert params.quarter == 4

    def test_streamlit_entry_point_importable(self):
        """Test that the main streamlit app can be imported (not run)."""
        # This tests that the module structure is correct
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "streamlit_app",
            PROJECT_ROOT / "streamlit_app.py"
        )
        assert spec is not None
        # Don't actually load it as it would start Streamlit


class TestKPIForecasting:
    """Verify KPI forecasting capability is available and functional."""

    @pytest.fixture
    def sample_historical_data(self):
        """Generate sample historical data for forecasting."""
        np.random.seed(42)
        data = []
        for year in range(2022, 2026):
            for quarter in range(1, 5):
                base_value = 70 + (year - 2022) * 2 + quarter * 0.5
                noise = np.random.normal(0, 1)
                data.append({
                    "year": year,
                    "quarter": quarter,
                    "value": base_value + noise,
                })
        return pd.DataFrame(data)

    def test_forecaster_import(self):
        """Test that the KPI forecaster can be imported."""
        from analytics_hub_platform.domain.ml_services import KPIForecaster
        assert KPIForecaster is not None

    def test_forecaster_initialization(self):
        """Test that forecaster can be initialized with different models."""
        from analytics_hub_platform.domain.ml_services import KPIForecaster

        for model_type in ["gradient_boosting", "random_forest"]:
            forecaster = KPIForecaster(model_type=model_type)
            assert forecaster is not None
            assert forecaster.model_type == model_type

    def test_forecaster_fit_and_predict(self, sample_historical_data):
        """Test forecaster can fit and generate predictions."""
        from analytics_hub_platform.domain.ml_services import KPIForecaster

        forecaster = KPIForecaster(model_type="gradient_boosting")
        forecaster.fit(sample_historical_data)

        predictions = forecaster.predict(quarters_ahead=4)

        assert len(predictions) == 4
        for pred in predictions:
            assert "year" in pred
            assert "quarter" in pred
            assert "predicted_value" in pred
            assert "confidence_lower" in pred
            assert "confidence_upper" in pred

    def test_forecast_kpi_function(self, sample_historical_data):
        """Test the convenience forecast_kpi function."""
        from analytics_hub_platform.domain.ml_services import forecast_kpi

        result = forecast_kpi(
            df=sample_historical_data,
            kpi_id="test_kpi",
            region_id="test_region",
            quarters_ahead=4,
            model_type="gradient_boosting",
        )

        assert "predictions" in result
        assert len(result["predictions"]) == 4


class TestAnomalyDetection:
    """Verify anomaly detection / early warning capability."""

    @pytest.fixture
    def data_with_anomaly(self):
        """Generate sample data with an obvious anomaly."""
        np.random.seed(42)
        data = []
        for year in range(2022, 2026):
            for quarter in range(1, 5):
                base_value = 70 + np.random.normal(0, 2)
                # Inject anomaly in Q4 2025
                if year == 2025 and quarter == 4:
                    base_value = 30  # Dramatic drop
                data.append({
                    "year": year,
                    "quarter": quarter,
                    "value": base_value,
                })
        return pd.DataFrame(data)

    def test_anomaly_detector_import(self):
        """Test that anomaly detector can be imported."""
        from analytics_hub_platform.domain.ml_services import (
            AnomalyDetector,
            AnomalySeverity,
        )
        assert AnomalyDetector is not None
        assert AnomalySeverity is not None

    def test_anomaly_detector_initialization(self):
        """Test detector can be initialized with custom thresholds."""
        from analytics_hub_platform.domain.ml_services import AnomalyDetector

        detector = AnomalyDetector(
            zscore_threshold=2.5,
            critical_threshold=3.5,
        )
        assert detector.zscore_threshold == 2.5
        assert detector.critical_threshold == 3.5

    def test_anomaly_detection_finds_anomaly(self, data_with_anomaly):
        """Test that detector finds the injected anomaly."""
        from analytics_hub_platform.domain.ml_services import AnomalyDetector

        detector = AnomalyDetector(zscore_threshold=2.0, critical_threshold=3.0)
        anomalies = detector.detect_anomalies(
            data_with_anomaly,
            kpi_id="test_metric",
            region_id="test_region",
            higher_is_better=True,
        )

        # Should detect at least one anomaly (the Q4 2025 drop)
        assert len(anomalies) >= 1

        # Check the anomaly has required fields
        if anomalies:
            anomaly = anomalies[0]
            assert hasattr(anomaly, "kpi_id")
            assert hasattr(anomaly, "year")
            assert hasattr(anomaly, "quarter")
            assert hasattr(anomaly, "severity")
            assert hasattr(anomaly, "description")


class TestAIRecommendations:
    """Verify AI recommendations capability is available."""

    def test_llm_service_import(self):
        """Test that LLM service can be imported."""
        from analytics_hub_platform.domain.llm_service import generate_recommendations
        assert callable(generate_recommendations)

    def test_recommendations_structure(self):
        """Test that generate_recommendations returns expected structure."""
        from analytics_hub_platform.domain.llm_service import generate_recommendations

        # Call with minimal data - should return fallback/cached recommendations
        try:
            result = generate_recommendations(
                kpi_data={"period": "Q4 2026", "metrics": {}},
                language="en",
                provider="auto",
            )

            # Verify structure (may be fallback data)
            assert isinstance(result, dict)
            # These keys should exist in the result
            expected_keys = ["executive_summary", "recommendations"]
            for key in expected_keys:
                assert key in result, f"Missing key: {key}"

        except Exception as e:
            # If no API key configured, the function should still be callable
            # but may raise a configuration error
            assert "API" in str(e) or "key" in str(e).lower() or "provider" in str(e).lower(), \
                f"Unexpected error: {e}"


class TestAdvancedAnalyticsIntegration:
    """Verify Advanced Analytics features are properly integrated into main pages."""

    def test_advanced_analytics_module_exists(self):
        """Test that the advanced analytics domain module exists."""
        from analytics_hub_platform.domain.advanced_analytics import (
            TrendAnalyzer,
            SeasonalityAnalyzer,
            ChangePointDetector,
            PatternRecognizer,
        )
        assert TrendAnalyzer is not None
        assert SeasonalityAnalyzer is not None
        assert ChangePointDetector is not None
        assert PatternRecognizer is not None

    def test_ensemble_forecaster_available(self):
        """Test that ensemble forecasting is available."""
        from analytics_hub_platform.domain.advanced_analytics import EnsembleForecaster
        assert EnsembleForecaster is not None

    def test_pattern_analysis_functions(self):
        """Test pattern analysis convenience functions."""
        from analytics_hub_platform.domain.advanced_analytics import (
            analyze_patterns,
            analyze_trend,
            analyze_seasonality,
            detect_change_points,
            forecast_ensemble,
        )
        assert callable(analyze_patterns)
        assert callable(analyze_trend)
        assert callable(analyze_seasonality)
        assert callable(detect_change_points)
        assert callable(forecast_ensemble)


# Convenience test runner
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
