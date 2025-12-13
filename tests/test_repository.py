"""
Repository and Caching Tests
Sustainable Economic Development Analytics Hub
Ministry of Economy and Planning

Tests for repository queries and caching behavior.
"""

import pytest
import pandas as pd
from datetime import datetime

from analytics_hub_platform.infrastructure.repository import Repository
from analytics_hub_platform.infrastructure.caching import CacheManager, get_cache_manager
from analytics_hub_platform.domain.models import FilterParams


class TestRepository:
    """Tests for Repository class."""
    
    @pytest.fixture
    def repository(self):
        """Create repository instance."""
        return Repository()
    
    def test_repository_initialization(self, repository):
        """Test repository initializes correctly."""
        assert repository is not None
        assert repository._engine is not None
    
    def test_get_all_indicators_returns_dataframe(self, repository):
        """Test get_all_indicators returns a DataFrame."""
        result = repository.get_all_indicators(
            tenant_id="mep-sa-001",
            filters=None
        )
        
        assert isinstance(result, pd.DataFrame)
        # May be empty or have data, but should be DataFrame
    
    def test_get_all_indicators_with_filters(self, repository):
        """Test get_all_indicators with filters."""
        filters = FilterParams(
            tenant_id="mep-sa-001",
            year=2024,
            quarter=4,
            region="all"
        )
        
        result = repository.get_all_indicators(
            tenant_id="mep-sa-001",
            filters=filters
        )
        
        assert isinstance(result, pd.DataFrame)
        
        if not result.empty:
            # Verify filters were applied
            assert all(result["year"] == 2024)
            assert all(result["quarter"] == 4)
    
    def test_get_latest_snapshot_returns_dataframe(self, repository):
        """Test get_latest_snapshot returns a DataFrame."""
        result = repository.get_latest_snapshot(
            tenant_id="mep-sa-001",
            filters=None
        )
        
        assert isinstance(result, pd.DataFrame)
    
    def test_get_available_periods_returns_list(self, repository):
        """Test get_available_periods returns a list."""
        result = repository.get_available_periods(tenant_id="mep-sa-001")
        
        assert isinstance(result, list)
        
        if result:
            # Check structure of period objects
            period = result[0]
            assert "year" in period
            assert "quarter" in period
            assert "label" in period
    
    def test_get_indicator_timeseries_with_invalid_indicator(self, repository):
        """Test get_indicator_timeseries with invalid indicator."""
        result = repository.get_indicator_timeseries(
            tenant_id="mep-sa-001",
            indicator_id="nonexistent_indicator",
            region="all"
        )
        
        # Should return empty DataFrame, not crash
        assert isinstance(result, pd.DataFrame)


class TestCacheManager:
    """Tests for CacheManager class."""
    
    @pytest.fixture
    def cache(self):
        """Create cache manager instance."""
        return CacheManager(default_ttl=60, enabled=True)
    
    def test_cache_initialization(self, cache):
        """Test cache initializes correctly."""
        assert cache is not None
        assert cache._enabled is True
        assert cache._default_ttl == 60
        assert cache._hits == 0
        assert cache._misses == 0
    
    def test_cache_set_and_get(self, cache):
        """Test basic cache set and get."""
        cache.set("test_key", "test_value")
        
        result = cache.get("test_key")
        
        assert result == "test_value"
        assert cache._hits == 1
        assert cache._misses == 0
    
    def test_cache_miss(self, cache):
        """Test cache miss for non-existent key."""
        result = cache.get("nonexistent_key")
        
        assert result is None
        assert cache._hits == 0
        assert cache._misses == 1
    
    def test_cache_set_with_custom_ttl(self, cache):
        """Test cache set with custom TTL."""
        cache.set("test_key", "test_value", ttl=120)
        
        result = cache.get("test_key")
        
        assert result == "test_value"
    
    def test_cache_delete(self, cache):
        """Test cache delete."""
        cache.set("test_key", "test_value")
        
        deleted = cache.delete("test_key")
        
        assert deleted is True
        
        result = cache.get("test_key")
        assert result is None
    
    def test_cache_delete_nonexistent(self, cache):
        """Test delete of non-existent key."""
        deleted = cache.delete("nonexistent_key")
        
        assert deleted is False
    
    def test_cache_clear(self, cache):
        """Test cache clear."""
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        
        cache.clear()
        
        assert cache.get("key1") is None
        assert cache.get("key2") is None
        assert cache._hits == 0
        assert cache._misses == 2
    
    def test_cache_stats(self, cache):
        """Test cache statistics."""
        cache.set("key1", "value1")
        cache.get("key1")  # hit
        cache.get("nonexistent")  # miss
        
        stats = cache.get_stats()
        
        assert stats["enabled"] is True
        assert stats["entries"] == 1
        assert stats["hits"] == 1
        assert stats["misses"] == 1
        assert stats["hit_rate"] == 50.0
    
    def test_cache_disabled(self):
        """Test cache behavior when disabled."""
        cache = CacheManager(enabled=False)
        
        cache.set("test_key", "test_value")
        result = cache.get("test_key")
        
        # Should return None when disabled
        assert result is None
    
    def test_get_cache_manager_singleton(self):
        """Test get_cache_manager returns singleton."""
        cache1 = get_cache_manager()
        cache2 = get_cache_manager()
        
        assert cache1 is cache2


class TestCacheIntegration:
    """Integration tests for caching with repository."""
    
    @pytest.fixture
    def repository(self):
        """Create repository instance."""
        return Repository()
    
    @pytest.fixture
    def cache(self):
        """Create cache manager instance."""
        cache = CacheManager(default_ttl=60, enabled=True)
        cache.clear()  # Start fresh
        return cache
    
    def test_repository_cache_hit_miss(self, repository, cache):
        """Test cache hit/miss behavior with repository queries."""
        # First query - cache miss
        cache.clear()
        initial_stats = cache.get_stats()
        
        # Set a test value in cache
        cache_key = "test_query_key"
        test_data = pd.DataFrame({"test": [1, 2, 3]})
        cache.set(cache_key, test_data)
        
        # Query cache - should be hit
        result = cache.get(cache_key)
        assert result is not None
        
        # Check stats
        stats_after = cache.get_stats()
        assert stats_after["hits"] > initial_stats["hits"]
    
    def test_cache_with_different_keys(self, cache):
        """Test that different keys store different values."""
        cache.set("key1", {"data": "value1"})
        cache.set("key2", {"data": "value2"})
        
        assert cache.get("key1") == {"data": "value1"}
        assert cache.get("key2") == {"data": "value2"}
    
    def test_cache_complex_objects(self, cache):
        """Test caching complex objects like DataFrames."""
        df = pd.DataFrame({
            "year": [2024, 2024],
            "quarter": [3, 4],
            "value": [100.5, 105.2]
        })
        
        cache.set("complex_key", df)
        
        result = cache.get("complex_key")
        
        assert isinstance(result, pd.DataFrame)
        assert result.equals(df)
