"""
API Endpoint Tests
Sustainable Economic Development Analytics Hub

Tests for FastAPI endpoints.
"""

import pytest
from fastapi.testclient import TestClient

from main_api import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


class TestHealthEndpoint:
    """Tests for health check endpoint."""
    
    def test_health_check(self, client):
        """Test health endpoint returns OK."""
        response = client.get("/api/v1/health")
        
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "ok"
        assert "timestamp" in data
        assert "version" in data


class TestRootEndpoint:
    """Tests for root endpoint."""
    
    def test_root_endpoint(self, client):
        """Test root endpoint returns API info."""
        response = client.get("/")
        
        assert response.status_code == 200
        
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "docs" in data


@pytest.mark.api
class TestIndicatorsEndpoint:
    """Tests for indicators endpoint."""
    
    def test_list_indicators(self, client):
        """Test listing indicators."""
        response = client.get(
            "/api/v1/indicators",
            headers={"X-Tenant-ID": "test_tenant"},
        )
        
        assert response.status_code == 200
        
        data = response.json()
        assert "data" in data
        assert "total" in data
        assert "page" in data
        assert "page_size" in data
    
    def test_list_indicators_with_filters(self, client):
        """Test listing indicators with filters."""
        response = client.get(
            "/api/v1/indicators",
            params={"year": 2024, "quarter": 4},
            headers={"X-Tenant-ID": "test_tenant"},
        )
        
        assert response.status_code == 200
    
    def test_list_indicators_pagination(self, client):
        """Test indicator pagination."""
        response = client.get(
            "/api/v1/indicators",
            params={"page": 1, "page_size": 10},
            headers={"X-Tenant-ID": "test_tenant"},
        )
        
        assert response.status_code == 200
        
        data = response.json()
        assert data["page"] == 1
        assert data["page_size"] == 10


@pytest.mark.api
class TestSustainabilityEndpoints:
    """Tests for sustainability endpoints."""
    
    def test_get_summary(self, client):
        """Test sustainability summary endpoint."""
        response = client.get(
            "/api/v1/sustainability/summary",
            params={"year": 2024, "quarter": 4},
            headers={"X-Tenant-ID": "test_tenant"},
        )
        
        assert response.status_code == 200
        
        data = response.json()
        assert "sustainability_index" in data
        assert "period" in data
    
    def test_get_regional_comparison(self, client):
        """Test regional comparison endpoint."""
        response = client.get(
            "/api/v1/sustainability/regions",
            params={"year": 2024},
            headers={"X-Tenant-ID": "test_tenant"},
        )
        
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        
        if len(data) > 0:
            assert "region" in data[0]
            assert "sustainability_index" in data[0]
            assert "rank" in data[0]
    
    def test_get_timeseries(self, client):
        """Test time series endpoint."""
        response = client.get(
            "/api/v1/sustainability/timeseries/sustainability_index",
            headers={"X-Tenant-ID": "test_tenant"},
        )
        
        assert response.status_code == 200
        
        data = response.json()
        assert data["indicator"] == "sustainability_index"
        assert "data" in data
    
    def test_get_timeseries_invalid_indicator(self, client):
        """Test time series with invalid indicator."""
        response = client.get(
            "/api/v1/sustainability/timeseries/invalid_indicator",
            headers={"X-Tenant-ID": "test_tenant"},
        )
        
        assert response.status_code == 400


@pytest.mark.api
class TestDataQualityEndpoint:
    """Tests for data quality endpoint."""
    
    def test_get_data_quality(self, client):
        """Test data quality endpoint."""
        response = client.get(
            "/api/v1/data-quality",
            headers={"X-Tenant-ID": "test_tenant"},
        )
        
        assert response.status_code == 200
        
        data = response.json()
        assert "completeness" in data
        assert "avg_quality_score" in data
        assert "records_count" in data


@pytest.mark.api
class TestReferenceEndpoints:
    """Tests for reference data endpoints."""
    
    def test_get_regions(self, client):
        """Test regions reference endpoint."""
        response = client.get("/api/v1/reference/regions")
        
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert "Riyadh" in data
    
    def test_get_years(self, client):
        """Test years reference endpoint."""
        response = client.get(
            "/api/v1/reference/years",
            headers={"X-Tenant-ID": "test_tenant"},
        )
        
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
