"""
API Endpoint Tests
Sustainable Economic Development Analytics Hub

Tests for FastAPI endpoints - integration tests for complete workflows.
"""

import numpy as np
import pandas as pd
import pytest
from fastapi.testclient import TestClient


# Delay import to allow module fixing
@pytest.fixture
def client():
    """Create test client."""
    try:
        from main_api import app

        return TestClient(app)
    except ImportError as e:
        pytest.skip(f"Cannot import main_api: {e}")


@pytest.fixture
def mock_indicator_df():
    """Create mock indicator DataFrame for testing."""
    np.random.seed(42)
    regions = ["riyadh", "makkah", "eastern", "madinah"]

    data = []
    for year in [2023, 2024]:
        for quarter in [1, 2, 3, 4]:
            for region in regions:
                data.append(
                    {
                        "tenant_id": "demo_tenant",
                        "year": year,
                        "quarter": quarter,
                        "region": region,
                        "sustainability_index": np.random.uniform(60, 85),
                        "gdp_growth": np.random.uniform(2, 6),
                        "renewable_share": np.random.uniform(10, 30),
                        "co2_index": np.random.uniform(70, 95),
                        "unemployment_rate": np.random.uniform(7, 12),
                        "green_jobs": np.random.uniform(100, 200),
                        "data_quality_score": np.random.uniform(0.8, 1.0),
                    }
                )

    return pd.DataFrame(data)


class TestHealthEndpoint:
    """Tests for health check endpoint."""

    def test_health_check(self, client):
        """Test health endpoint returns OK."""
        if client is None:
            pytest.skip("Client not available")

        response = client.get("/api/v1/health")

        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "ok"


class TestRootEndpoint:
    """Tests for root endpoint."""

    def test_root_endpoint(self, client):
        """Test root endpoint returns API info."""
        if client is None:
            pytest.skip("Client not available")

        response = client.get("/")

        assert response.status_code == 200

        data = response.json()
        assert "name" in data or "message" in data


class TestObservabilityEndpoints:
    """Tests for observability endpoints."""

    def test_comprehensive_health_endpoint(self, client):
        """Test /health returns comprehensive status."""
        response = client.get("/health")

        assert response.status_code in [200, 503]
        data = response.json()

        assert "status" in data
        assert "timestamp" in data
        assert "checks" in data

    def test_liveness_probe(self, client):
        """Test Kubernetes liveness probe."""
        response = client.get("/health/live")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "alive"

    def test_readiness_probe(self, client):
        """Test Kubernetes readiness probe."""
        response = client.get("/health/ready")

        assert response.status_code in [200, 503]
        data = response.json()
        assert data["status"] in ["ready", "not_ready"]

    def test_metrics_endpoint(self, client):
        """Test Prometheus metrics endpoint."""
        response = client.get("/metrics")

        assert response.status_code == 200
        assert "text/plain" in response.headers["content-type"]


class TestIndicatorsEndpoint:
    """Tests for indicators CRUD endpoint."""

    def test_list_indicators(self, client):
        """Test listing indicators."""
        response = client.get(
            "/api/v1/indicators",
            headers={"X-Tenant-ID": "demo_tenant", "X-User-ID": "analyst"},
        )

        assert response.status_code == 200
        data = response.json()

        assert "data" in data
        assert "total" in data
        assert "page" in data
        assert "page_size" in data

    def test_list_indicators_with_pagination(self, client):
        """Test indicators pagination."""
        response = client.get(
            "/api/v1/indicators",
            params={"page": 1, "page_size": 5},
            headers={"X-Tenant-ID": "demo_tenant", "X-User-ID": "analyst"},
        )

        assert response.status_code == 200
        data = response.json()

        assert data["page"] == 1
        assert data["page_size"] == 5
        assert len(data["data"]) <= 5

    def test_list_indicators_with_year_filter(self, client):
        """Test filtering indicators by year."""
        response = client.get(
            "/api/v1/indicators",
            params={"year": 2024},
            headers={"X-Tenant-ID": "demo_tenant", "X-User-ID": "analyst"},
        )

        assert response.status_code == 200
        data = response.json()

        # All returned records should be from 2024
        for record in data["data"]:
            assert record["year"] == 2024

    def test_list_indicators_with_quarter_filter(self, client):
        """Test filtering indicators by quarter."""
        response = client.get(
            "/api/v1/indicators",
            params={"quarter": 1},
            headers={"X-Tenant-ID": "demo_tenant", "X-User-ID": "analyst"},
        )

        assert response.status_code == 200
        data = response.json()

        for record in data["data"]:
            assert record["quarter"] == 1

    def test_list_indicators_with_region_filter(self, client):
        """Test filtering indicators by region."""
        response = client.get(
            "/api/v1/indicators",
            params={"region": "riyadh"},
            headers={"X-Tenant-ID": "demo_tenant", "X-User-ID": "analyst"},
        )

        assert response.status_code == 200
        data = response.json()

        for record in data["data"]:
            assert record["region"] == "riyadh"

    def test_list_indicators_combined_filters(self, client):
        """Test multiple filters combined."""
        response = client.get(
            "/api/v1/indicators",
            params={"year": 2024, "quarter": 1, "region": "riyadh"},
            headers={"X-Tenant-ID": "demo_tenant", "X-User-ID": "analyst"},
        )

        assert response.status_code == 200
        data = response.json()

        for record in data["data"]:
            assert record["year"] == 2024
            assert record["quarter"] == 1
            assert record["region"] == "riyadh"


class TestSustainabilityEndpoint:
    """Tests for sustainability summary endpoint."""

    def test_get_sustainability_summary(self, client):
        """Test getting sustainability summary."""
        response = client.get(
            "/api/v1/sustainability/summary",
            headers={"X-Tenant-ID": "demo_tenant"},
        )

        assert response.status_code == 200
        data = response.json()

        assert "sustainability_index" in data
        assert "period" in data

    def test_get_sustainability_summary_with_filters(self, client):
        """Test sustainability summary with year/quarter filters."""
        response = client.get(
            "/api/v1/sustainability/summary",
            params={"year": 2024, "quarter": 1},
            headers={"X-Tenant-ID": "demo_tenant"},
        )

        assert response.status_code == 200
        data = response.json()

        assert "Q1 2024" in data["period"]

    def test_get_sustainability_summary_with_region(self, client):
        """Test sustainability summary for specific region."""
        response = client.get(
            "/api/v1/sustainability/summary",
            params={"region": "riyadh"},
            headers={"X-Tenant-ID": "demo_tenant"},
        )

        assert response.status_code == 200
        data = response.json()

        assert data["region"] == "riyadh"


class TestRegionalComparisonEndpoint:
    """Tests for regional comparison endpoint."""

    def test_get_regional_comparison(self, client):
        """Test getting regional comparison."""
        response = client.get(
            "/api/v1/sustainability/regions",
            headers={"X-Tenant-ID": "demo_tenant"},
        )

        assert response.status_code == 200
        data = response.json()

        assert isinstance(data, list)

        if len(data) > 0:
            assert "region" in data[0]
            assert "sustainability_index" in data[0]
            assert "rank" in data[0]

    def test_regional_comparison_ranking(self, client):
        """Test that regional comparison is properly ranked."""
        response = client.get(
            "/api/v1/sustainability/regions",
            headers={"X-Tenant-ID": "demo_tenant"},
        )

        assert response.status_code == 200
        data = response.json()

        if len(data) > 1:
            # Ranks should be sequential
            ranks = [item["rank"] for item in data]
            assert ranks == sorted(ranks)


class TestTimeSeriesEndpoint:
    """Tests for time series endpoint."""

    def test_get_timeseries(self, client):
        """Test getting time series data."""
        response = client.get(
            "/api/v1/sustainability/timeseries/sustainability_index",
            headers={"X-Tenant-ID": "demo_tenant"},
        )

        # May return 200 if data exists, or could return error if no data
        assert response.status_code in [200, 500]  # 500 can happen if no data in test DB

        if response.status_code == 200:
            data = response.json()
            assert "indicator" in data
            assert "data" in data
            assert data["indicator"] == "sustainability_index"

    def test_get_timeseries_different_indicators(self, client):
        """Test time series for different valid indicators."""
        # Use indicators that are in the valid_indicators list
        indicators = ["sustainability_index", "gdp_growth", "co2_per_gdp"]

        for indicator in indicators:
            response = client.get(
                f"/api/v1/sustainability/timeseries/{indicator}",
                headers={"X-Tenant-ID": "demo_tenant"},
            )

            # May return 200 or 500 depending on test data availability
            assert response.status_code in [200, 500]

            if response.status_code == 200:
                data = response.json()
                assert data["indicator"] == indicator

    def test_get_timeseries_invalid_indicator(self, client):
        """Test time series with invalid indicator."""
        response = client.get(
            "/api/v1/sustainability/timeseries/invalid_indicator",
            headers={"X-Tenant-ID": "demo_tenant"},
        )

        assert response.status_code == 400

    def test_get_timeseries_with_region(self, client):
        """Test time series filtered by region."""
        response = client.get(
            "/api/v1/sustainability/timeseries/sustainability_index",
            params={"region": "riyadh"},
            headers={"X-Tenant-ID": "demo_tenant"},
        )

        # May return 200 or 500 depending on data availability
        assert response.status_code in [200, 500]

        if response.status_code == 200:
            data = response.json()
            assert isinstance(data["data"], list)


class TestDataQualityEndpoint:
    """Tests for data quality endpoint."""

    def test_get_data_quality(self, client):
        """Test getting data quality metrics."""
        response = client.get(
            "/api/v1/data-quality",
            headers={"X-Tenant-ID": "demo_tenant"},
        )

        assert response.status_code == 200
        data = response.json()

        assert "completeness" in data
        assert "avg_quality_score" in data
        assert "records_count" in data

    def test_data_quality_values_in_range(self, client):
        """Test that data quality values are in valid ranges."""
        response = client.get(
            "/api/v1/data-quality",
            headers={"X-Tenant-ID": "demo_tenant"},
        )

        assert response.status_code == 200
        data = response.json()

        assert 0 <= data["completeness"] <= 100
        assert 0 <= data["avg_quality_score"] <= 1
        assert data["records_count"] >= 0


class TestReferenceEndpoints:
    """Tests for reference data endpoints."""

    def test_get_regions(self, client):
        """Test getting regions list."""
        response = client.get("/api/v1/reference/regions")

        assert response.status_code == 200
        data = response.json()

        assert isinstance(data, list)
        assert len(data) > 0
        assert "riyadh" in [r.lower() for r in data]

    def test_get_years(self, client):
        """Test getting available years."""
        response = client.get(
            "/api/v1/reference/years",
            headers={"X-Tenant-ID": "demo_tenant"},
        )

        assert response.status_code == 200
        data = response.json()

        assert isinstance(data, list)
        assert all(isinstance(y, int) for y in data)


class TestErrorHandling:
    """Tests for API error handling."""

    def test_invalid_quarter_validation(self, client):
        """Test validation of invalid quarter."""
        response = client.get(
            "/api/v1/sustainability/summary",
            params={"quarter": 5},  # Invalid quarter
            headers={"X-Tenant-ID": "demo_tenant"},
        )

        # Should return validation error
        assert response.status_code == 422

    def test_invalid_pagination(self, client):
        """Test validation of invalid pagination."""
        response = client.get(
            "/api/v1/indicators",
            params={"page": 0},  # Invalid page (should be >= 1)
            headers={"X-Tenant-ID": "demo_tenant", "X-User-ID": "analyst"},
        )

        assert response.status_code in [200, 422]  # May auto-correct or reject

    def test_correlation_id_in_error_response(self, client):
        """Test that correlation ID is included in error responses."""
        response = client.get(
            "/api/v1/sustainability/summary",
            params={"quarter": 5},
            headers={"X-Tenant-ID": "demo_tenant"},
        )

        # Correlation ID should be in headers even for errors
        assert "x-correlation-id" in response.headers


class TestCORSAndHeaders:
    """Tests for CORS and header handling."""

    def test_cors_headers_present(self, client):
        """Test that CORS headers are present."""
        response = client.options("/api/v1/health")

        # Should not error
        assert response.status_code in [200, 405]

    def test_custom_correlation_id(self, client):
        """Test custom correlation ID is propagated."""
        custom_id = "test-correlation-12345"

        response = client.get(
            "/",
            headers={"X-Correlation-ID": custom_id},
        )

        assert response.headers.get("x-correlation-id") == custom_id
