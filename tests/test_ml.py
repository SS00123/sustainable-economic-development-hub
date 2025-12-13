"""
Unit tests for ML modules - forecasting and anomaly detection.
Updated to match actual module APIs.
"""

import pytest
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import List

from analytics_hub_platform.infrastructure.exceptions import (
    InsufficientDataError,
    ConstantSeriesError,
    DataError,
)


class TestKPIForecaster:
    """Tests for the KPI forecasting module."""
    
    @pytest.fixture
    def sample_df(self) -> pd.DataFrame:
        """Generate sample KPI DataFrame with trend and seasonality."""
        np.random.seed(42)
        n_points = 24  # 6 years of quarterly data
        
        years = []
        quarters = []
        for y in range(2018, 2024):
            for q in range(1, 5):
                years.append(y)
                quarters.append(q)
        
        trend = np.linspace(0, 2, n_points)
        seasonal = 0.3 * np.sin(2 * np.pi * np.arange(n_points) / 4)
        noise = np.random.normal(0, 0.1, n_points)
        values = 5 + trend + seasonal + noise
        
        return pd.DataFrame({
            "year": years,
            "quarter": quarters,
            "value": values
        })
    
    def test_forecaster_import(self):
        """Test that forecaster module imports correctly."""
        from analytics_hub_platform.domain.ml_services import KPIForecaster
        assert KPIForecaster is not None
    
    def test_forecaster_initialization(self):
        """Test forecaster initialization with default parameters."""
        from analytics_hub_platform.domain.ml_services import KPIForecaster
        forecaster = KPIForecaster()
        assert forecaster is not None
        assert forecaster.model_type in ["random_forest", "gradient_boosting"]
    
    def test_forecaster_fit(self, sample_df):
        """Test fitting the forecaster."""
        from analytics_hub_platform.domain.ml_services import KPIForecaster
        forecaster = KPIForecaster()
        forecaster.fit(sample_df)
        assert forecaster._is_fitted
    
    def test_forecaster_predict(self, sample_df):
        """Test generating predictions."""
        from analytics_hub_platform.domain.ml_services import KPIForecaster
        forecaster = KPIForecaster()
        forecaster.fit(sample_df)
        
        predictions = forecaster.predict(quarters_ahead=4)
        
        assert len(predictions) == 4
        assert all(isinstance(p, dict) for p in predictions)
    
    def test_forecaster_insufficient_data(self):
        """Test that forecaster handles insufficient data gracefully."""
        from analytics_hub_platform.domain.ml_services import KPIForecaster
        forecaster = KPIForecaster()
        
        short_df = pd.DataFrame({
            "year": [2024, 2024, 2024],
            "quarter": [1, 2, 3],
            "value": [1.0, 2.0, 3.0]
        })
        
        # Should raise an error for insufficient data
        with pytest.raises(InsufficientDataError):
            forecaster.fit(short_df)
    
    def test_forecaster_constant_series(self):
        """Test that forecaster handles constant series (zero variance)."""
        from analytics_hub_platform.domain.ml_services import KPIForecaster
        forecaster = KPIForecaster()
        
        # All values identical
        constant_df = pd.DataFrame({
            "year": [2023] * 8,
            "quarter": [1, 2, 3, 4, 1, 2, 3, 4],
            "value": [5.0] * 8
        })
        constant_df.loc[constant_df["quarter"].duplicated(keep='first'), "year"] = 2024
        
        # Should raise an error for constant series
        with pytest.raises(ConstantSeriesError):
            forecaster.fit(constant_df)
    
    def test_forecaster_with_nan_values(self):
        """Test that forecaster rejects data with NaN values."""
        from analytics_hub_platform.domain.ml_services import KPIForecaster
        forecaster = KPIForecaster()
        
        nan_df = pd.DataFrame({
            "year": [2023] * 8,
            "quarter": [1, 2, 3, 4, 1, 2, 3, 4],
            "value": [1.0, 2.0, np.nan, 4.0, 5.0, 6.0, 7.0, 8.0]
        })
        nan_df.loc[nan_df["quarter"].duplicated(keep='first'), "year"] = 2024
        
        # Should raise an error for NaN values
        with pytest.raises(DataError):
            forecaster.fit(nan_df)
    
    def test_forecaster_minimal_valid_data(self):
        """Test forecaster with exactly 4 data points (minimum)."""
        from analytics_hub_platform.domain.ml_services import KPIForecaster
        forecaster = KPIForecaster()
        
        minimal_df = pd.DataFrame({
            "year": [2024, 2024, 2024, 2024],
            "quarter": [1, 2, 3, 4],
            "value": [1.0, 2.0, 3.0, 4.0]
        })
        
        # Should work with 4 points
        forecaster.fit(minimal_df)
        predictions = forecaster.predict(quarters_ahead=2)
        
        assert len(predictions) == 2
        assert all(isinstance(p, dict) for p in predictions)


class TestAnomalyDetector:
    """Tests for the anomaly detection module."""
    
    @pytest.fixture
    def normal_df(self) -> pd.DataFrame:
        """Generate normal KPI DataFrame."""
        np.random.seed(42)
        years = []
        quarters = []
        for y in range(2019, 2024):
            for q in range(1, 5):
                years.append(y)
                quarters.append(q)
        
        values = np.random.normal(5.0, 0.5, 20).tolist()
        return pd.DataFrame({
            "year": years,
            "quarter": quarters,
            "value": values
        })
    
    @pytest.fixture
    def anomaly_df(self) -> pd.DataFrame:
        """Generate DataFrame with clear anomalies."""
        np.random.seed(42)
        years = []
        quarters = []
        for y in range(2019, 2024):
            for q in range(1, 5):
                years.append(y)
                quarters.append(q)
        
        values = np.random.normal(5.0, 0.5, 20).tolist()
        values[5] = 12.0   # High anomaly
        values[15] = -2.0  # Low anomaly
        
        return pd.DataFrame({
            "year": years,
            "quarter": quarters,
            "value": values
        })
    
    def test_detector_import(self):
        """Test that anomaly detector imports correctly."""
        from analytics_hub_platform.domain.ml_services import AnomalyDetector
        assert AnomalyDetector is not None
    
    def test_detector_initialization(self):
        """Test detector initialization."""
        from analytics_hub_platform.domain.ml_services import AnomalyDetector
        detector = AnomalyDetector()
        assert detector is not None
    
    def test_detector_with_zscore_threshold(self):
        """Test detector with zscore_threshold parameter."""
        from analytics_hub_platform.domain.ml_services import AnomalyDetector
        detector = AnomalyDetector(zscore_threshold=3.0)
        assert detector.zscore_threshold == 3.0
    
    def test_detect_zscore_anomalies(self, anomaly_df):
        """Test Z-score based anomaly detection."""
        from analytics_hub_platform.domain.ml_services import AnomalyDetector
        detector = AnomalyDetector(zscore_threshold=2.5)
        
        anomalies = detector.detect_zscore_anomalies(
            df=anomaly_df,
            kpi_id="TEST_KPI",
            region_id="TEST_REGION"
        )
        
        # Should detect the injected anomalies
        assert len(anomalies) >= 1
        
        # Check anomaly structure (returns AnomalyResult dataclass)
        for anomaly in anomalies:
            assert hasattr(anomaly, "actual_value")
            assert hasattr(anomaly, "expected_value")
            assert hasattr(anomaly, "severity")
    
    def test_detect_isolation_forest(self, anomaly_df):
        """Test detection using Isolation Forest method."""
        from analytics_hub_platform.domain.ml_services import AnomalyDetector
        detector = AnomalyDetector()
        
        # Need more data for isolation forest
        extended_df = pd.concat([anomaly_df, anomaly_df]).reset_index(drop=True)
        extended_df["year"] = list(range(2015, 2025)) * 4
        extended_df = extended_df.head(40)
        
        # Create proper year/quarter
        years = []
        quarters = []
        for y in range(2015, 2025):
            for q in range(1, 5):
                years.append(y)
                quarters.append(q)
        extended_df = pd.DataFrame({
            "year": years,
            "quarter": quarters,
            "value": np.random.normal(5.0, 0.5, 40)
        })
        extended_df.loc[10, "value"] = 15.0  # Anomaly
        
        anomalies = detector.detect_isolation_forest_anomalies(
            df=extended_df,
            kpi_id="TEST_KPI",
            region_id="TEST_REGION"
        )
        
        assert isinstance(anomalies, list)
    
    def test_anomaly_detector_empty_data(self):
        """Test that anomaly detector handles empty data gracefully."""
        from analytics_hub_platform.domain.ml_services import AnomalyDetector
        detector = AnomalyDetector()
        
        empty_df = pd.DataFrame({"year": [], "quarter": [], "value": []})
        anomalies = detector.detect_anomalies(
            df=empty_df,
            kpi_id="TEST_KPI",
            region_id="TEST_REGION"
        )
        
        # Should return empty list, not crash
        assert anomalies == []
    
    def test_anomaly_detector_constant_series(self):
        """Test that anomaly detector handles constant series (no variance)."""
        from analytics_hub_platform.domain.ml_services import AnomalyDetector
        detector = AnomalyDetector()
        
        # All values identical
        constant_df = pd.DataFrame({
            "year": [2023] * 8,
            "quarter": [1, 2, 3, 4, 1, 2, 3, 4],
            "value": [5.0] * 8
        })
        constant_df.loc[constant_df["quarter"].duplicated(keep='first'), "year"] = 2024
        
        anomalies = detector.detect_anomalies(
            df=constant_df,
            kpi_id="TEST_KPI",
            region_id="TEST_REGION"
        )
        
        # No anomalies in constant series
        assert anomalies == []
    
    def test_anomaly_detector_with_nan(self):
        """Test that anomaly detector filters out NaN values."""
        from analytics_hub_platform.domain.ml_services import AnomalyDetector
        detector = AnomalyDetector()
        
        nan_df = pd.DataFrame({
            "year": [2023] * 8,
            "quarter": [1, 2, 3, 4, 1, 2, 3, 4],
            "value": [1.0, 2.0, np.nan, 4.0, 5.0, 6.0, 7.0, 8.0]
        })
        nan_df.loc[nan_df["quarter"].duplicated(keep='first'), "year"] = 2024
        
        # Should handle NaN gracefully (filter them out)
        anomalies = detector.detect_anomalies(
            df=nan_df,
            kpi_id="TEST_KPI",
            region_id="TEST_REGION"
        )
        
        # Should work without crashing
        assert isinstance(anomalies, list)


class TestDataGenerator:
    """Tests for synthetic data generation."""
    
    def test_generator_import(self):
        """Test that generator imports correctly."""
        from analytics_hub_platform.utils.synthetic_generator import SyntheticDataGenerator
        assert SyntheticDataGenerator is not None
    
    def test_generator_initialization(self):
        """Test generator initialization."""
        from analytics_hub_platform.utils.synthetic_generator import SyntheticDataGenerator
        generator = SyntheticDataGenerator()
        assert generator is not None
        assert len(generator.regions) == 13  # Saudi Arabia has 13 regions
    
    def test_generate_kpi_values(self):
        """Test generating KPI values."""
        from analytics_hub_platform.utils.synthetic_generator import SyntheticDataGenerator
        generator = SyntheticDataGenerator(start_year=2022, end_year=2023)
        
        data = generator.generate_kpi_values()
        
        assert len(data) > 0
        assert isinstance(data, pd.DataFrame)
        assert "year" in data.columns
        assert "quarter" in data.columns
        assert "value" in data.columns
    
    def test_generate_regions_data(self):
        """Test generating regions data."""
        from analytics_hub_platform.utils.synthetic_generator import SyntheticDataGenerator
        generator = SyntheticDataGenerator()
        
        regions = generator.generate_regions_data()
        
        assert len(regions) == 13  # Saudi Arabia regions
        assert isinstance(regions, pd.DataFrame)


class TestExcelImporter:
    """Tests for Excel/CSV data import."""
    
    def test_importer_import(self):
        """Test that importer imports correctly."""
        from analytics_hub_platform.utils.excel_importer import ExcelCSVImporter
        assert ExcelCSVImporter is not None
    
    def test_importer_initialization(self):
        """Test importer initialization."""
        from analytics_hub_platform.utils.excel_importer import ExcelCSVImporter
        importer = ExcelCSVImporter()
        assert importer is not None
    
    def test_validate_columns(self):
        """Test column validation."""
        from analytics_hub_platform.utils.excel_importer import ExcelCSVImporter
        
        importer = ExcelCSVImporter()
        
        # Create test data with required columns
        valid_data = pd.DataFrame({
            "kpi_id": ["gdp_growth", "unemployment_rate"],
            "region_id": ["riyadh", "makkah"],
            "year": [2023, 2023],
            "quarter": [1, 1],
            "value": [3.5, 5.2]
        })
        
        required_cols = ["kpi_id", "region_id", "year", "quarter", "value"]
        issues = importer.validate_columns(valid_data, required_cols)
        assert isinstance(issues, list)
        assert len(issues) == 0  # All required columns exist


# Pytest configuration
@pytest.fixture(scope="session")
def setup_test_environment():
    """Set up test environment."""
    import os
    os.environ["ENVIRONMENT"] = "test"
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"
    yield
    

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
