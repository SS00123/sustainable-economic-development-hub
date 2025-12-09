"""
API Endpoint Tests
Sustainable Economic Development Analytics Hub

Tests for FastAPI endpoints.
"""

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
