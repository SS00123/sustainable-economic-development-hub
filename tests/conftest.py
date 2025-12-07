"""
pytest Configuration
Sustainable Economic Development Analytics Hub

Shared fixtures and configuration for tests.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
import tempfile
import os

# Ensure test environment
os.environ["ANALYTICS_HUB_ENV"] = "test"
os.environ["ANALYTICS_HUB_DEBUG"] = "true"


@pytest.fixture(scope="session")
def test_db_path():
    """Create a temporary database for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_analytics.db"
        yield str(db_path)


@pytest.fixture
def sample_indicator_data():
    """Generate sample indicator data for testing."""
    regions = ["Riyadh", "Eastern Province", "Makkah", "Madinah", "Qassim"]
    years = [2023, 2024]
    quarters = [1, 2, 3, 4]
    
    data = []
    for year in years:
        for quarter in quarters:
            for region in regions:
                data.append({
                    "tenant_id": "test_tenant",
                    "year": year,
                    "quarter": quarter,
                    "region": region,
                    "sustainability_index": np.random.uniform(50, 80),
                    "co2_per_gdp": np.random.uniform(0.3, 0.6),
                    "co2_per_capita": np.random.uniform(15, 20),
                    "renewable_energy_pct": np.random.uniform(5, 20),
                    "green_investment_pct": np.random.uniform(2, 10),
                    "energy_intensity": np.random.uniform(4, 6),
                    "water_efficiency": np.random.uniform(60, 80),
                    "recycling_rate": np.random.uniform(10, 30),
                    "waste_diversion_rate": np.random.uniform(20, 40),
                    "green_building_pct": np.random.uniform(5, 15),
                    "public_transit_pct": np.random.uniform(10, 25),
                    "green_jobs_pct": np.random.uniform(2, 8),
                    "gdp_growth": np.random.uniform(2, 5),
                    "employment_rate": np.random.uniform(88, 95),
                    "data_quality_score": np.random.uniform(70, 95),
                    "created_at": datetime.utcnow().isoformat(),
                })
    
    return pd.DataFrame(data)


@pytest.fixture
def sample_kpi_thresholds():
    """Sample KPI thresholds for testing."""
    return {
        "sustainability_index": {
            "green": ">= 70",
            "amber": "50-69",
            "red": "< 50",
            "higher_is_better": True,
        },
        "co2_per_gdp": {
            "green": "<= 0.35",
            "amber": "0.36-0.50",
            "red": "> 0.50",
            "higher_is_better": False,
        },
        "renewable_energy_pct": {
            "green": ">= 15",
            "amber": "8-14",
            "red": "< 8",
            "higher_is_better": True,
        },
    }


@pytest.fixture
def sample_filter_params():
    """Sample filter parameters for testing."""
    from analytics_hub_platform.domain.models import FilterParams
    
    return FilterParams(
        tenant_id="test_tenant",
        year=2024,
        quarter=4,
        region=None,
    )


@pytest.fixture
def mock_settings():
    """Mock settings for testing."""
    from analytics_hub_platform.infrastructure.settings import Settings
    
    return Settings(
        environment="test",
        debug=True,
        db_path=":memory:",
        default_tenant_id="test_tenant",
    )


@pytest.fixture
def mock_repository(sample_indicator_data):
    """Mock repository with sample data."""
    from unittest.mock import MagicMock
    
    repo = MagicMock()
    repo.get_all_indicators.return_value = sample_indicator_data
    repo.get_latest_snapshot.return_value = sample_indicator_data.iloc[-5:]
    
    return repo


# Markers
def pytest_configure(config):
    """Configure custom markers."""
    config.addinivalue_line("markers", "slow: marks tests as slow running")
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "api: marks tests as API tests")
