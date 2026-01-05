"""
Test Suite Configuration
Sustainable Economic Development Analytics Hub
"""

import sys
from pathlib import Path

import pytest

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture(scope="session")
def test_db():
    """Create a test database for the session."""
    from analytics_hub_platform.infrastructure.db_init import initialize_database
    
    # Initialize with test data
    initialize_database()
    yield
    # Cleanup happens automatically with SQLite in-memory


@pytest.fixture
def sample_filter_params():
    """Sample filter parameters for testing."""
    from analytics_hub_platform.domain.models import FilterParams
    
    return FilterParams(
        tenant_id="ministry_economy",
        year=2026,
        quarter=4,
        region=None,
    )


@pytest.fixture
def sample_dataframe():
    """Sample DataFrame for testing."""
    import pandas as pd
    import numpy as np
    
    np.random.seed(42)
    
    return pd.DataFrame({
        "year": [2025, 2025, 2026, 2026] * 3,
        "quarter": [3, 4, 3, 4] * 3,
        "region": ["Riyadh"] * 4 + ["Makkah"] * 4 + ["Eastern"] * 4,
        "gdp_growth": np.random.uniform(2.0, 5.0, 12),
        "unemployment_rate": np.random.uniform(4.0, 8.0, 12),
        "sustainability_index": np.random.uniform(60, 85, 12),
        "co2_index": np.random.uniform(20, 40, 12),
    })
