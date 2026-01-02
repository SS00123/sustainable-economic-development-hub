"""
Performance Tests
Sustainable Economic Development Analytics Hub
Ministry of Economy and Planning

Tests for performance benchmarking:
- Query performance
- Caching effectiveness
- DataFrame operations
- Memory usage patterns
"""

import sys
import time
from collections.abc import Callable
from functools import wraps
from typing import Any

import numpy as np
import pandas as pd
import pytest

# Performance threshold constants (in seconds)
FAST_OPERATION_THRESHOLD = 0.1  # 100ms
MEDIUM_OPERATION_THRESHOLD = 0.5  # 500ms
SLOW_OPERATION_THRESHOLD = 2.0  # 2 seconds


def measure_time(func: Callable) -> Callable:
    """Decorator to measure execution time of a function."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        execution_time = end_time - start_time
        return result, execution_time

    return wrapper


def measure_memory(obj: Any) -> int:
    """Get approximate memory size of an object in bytes."""
    return sys.getsizeof(obj)


class TestCachingPerformance:
    """Test caching effectiveness."""

    def test_kpi_catalog_caching(self):
        """Test that KPI catalog is cached effectively."""
        from analytics_hub_platform.domain.services import _load_kpi_catalog

        # Clear cache first
        _load_kpi_catalog.cache_clear()

        # First call - cold cache
        start = time.perf_counter()
        catalog1 = _load_kpi_catalog()
        first_time = time.perf_counter() - start

        # Second call - warm cache
        start = time.perf_counter()
        catalog2 = _load_kpi_catalog()
        second_time = time.perf_counter() - start

        # Cache should be significantly faster
        assert catalog1 is catalog2, "Cache should return same object"
        assert second_time < first_time or second_time < 0.001, "Cached call should be faster"

    def test_lru_cache_on_indicators(self):
        """Test LRU cache on indicator functions."""
        from analytics_hub_platform.domain.indicators import _load_kpi_catalog

        # Clear cache
        _load_kpi_catalog.cache_clear()

        # First call
        start = time.perf_counter()
        _load_kpi_catalog()
        time.perf_counter() - start

        # Second call (cached)
        start = time.perf_counter()
        _load_kpi_catalog()
        second_time = time.perf_counter() - start

        # Verify caching works
        cache_info = _load_kpi_catalog.cache_info()
        assert cache_info.hits >= 1, "Should have cache hits"
        assert second_time < 0.001, "Cached call should be sub-millisecond"

    def test_cache_manager_performance(self):
        """Test CacheManager get/set performance."""
        from analytics_hub_platform.infrastructure.caching import get_cache

        cache = get_cache()
        cache.clear()

        # Test set performance
        set_times = []
        for i in range(100):
            start = time.perf_counter()
            cache.set(f"test_key_{i}", {"data": i, "values": list(range(100))})
            set_times.append(time.perf_counter() - start)

        avg_set_time = sum(set_times) / len(set_times)
        assert avg_set_time < 0.01, f"Average set time {avg_set_time:.4f}s should be < 10ms"

        # Test get performance
        get_times = []
        for i in range(100):
            start = time.perf_counter()
            cache.get(f"test_key_{i}")
            get_times.append(time.perf_counter() - start)

        avg_get_time = sum(get_times) / len(get_times)
        assert avg_get_time < 0.001, f"Average get time {avg_get_time:.4f}s should be < 1ms"

        cache.clear()


class TestDataFramePerformance:
    """Test DataFrame operation performance."""

    @pytest.fixture
    def large_dataframe(self) -> pd.DataFrame:
        """Create a large test DataFrame."""
        np.random.seed(42)
        n_rows = 10000

        return pd.DataFrame(
            {
                "year": np.random.choice([2022, 2023, 2024], n_rows),
                "quarter": np.random.choice([1, 2, 3, 4], n_rows),
                "region": np.random.choice(["riyadh", "makkah", "eastern", "madinah"], n_rows),
                "sustainability_index": np.random.uniform(40, 90, n_rows),
                "gdp_growth": np.random.uniform(-2, 8, n_rows),
                "renewable_share": np.random.uniform(0, 50, n_rows),
                "co2_index": np.random.uniform(50, 100, n_rows),
                "unemployment_rate": np.random.uniform(5, 15, n_rows),
                "green_jobs": np.random.uniform(50, 300, n_rows),
            }
        )

    def test_vectorized_period_creation(self, large_dataframe):
        """Test vectorized period creation vs apply."""
        from analytics_hub_platform.utils.dataframe_adapter import add_period_column

        df = large_dataframe.copy()

        # Vectorized approach
        start = time.perf_counter()
        df_vectorized = add_period_column(df.copy())
        vectorized_time = time.perf_counter() - start

        # Apply approach (for comparison)
        df_apply = df.copy()
        start = time.perf_counter()
        df_apply["period"] = df_apply.apply(
            lambda r: f"Q{int(r['quarter'])} {int(r['year'])}", axis=1
        )
        apply_time = time.perf_counter() - start

        # Vectorized should be faster
        speedup = apply_time / vectorized_time if vectorized_time > 0 else float("inf")
        assert speedup > 1, f"Vectorized should be faster (speedup: {speedup:.1f}x)"

        # Results should match
        assert list(df_vectorized["period"]) == list(df_apply["period"])

    def test_groupby_aggregation_performance(self, large_dataframe):
        """Test groupby aggregation performance."""
        df = large_dataframe

        start = time.perf_counter()
        result = (
            df.groupby(["year", "quarter"])
            .agg(
                {
                    "sustainability_index": "mean",
                    "gdp_growth": "mean",
                    "renewable_share": "mean",
                }
            )
            .reset_index()
        )
        elapsed = time.perf_counter() - start

        assert elapsed < FAST_OPERATION_THRESHOLD, (
            f"Groupby took {elapsed:.3f}s, should be < {FAST_OPERATION_THRESHOLD}s"
        )
        assert len(result) == 12  # 3 years * 4 quarters

    def test_filtering_performance(self, large_dataframe):
        """Test DataFrame filtering performance."""
        df = large_dataframe

        start = time.perf_counter()
        # Multiple filters
        df[(df["year"] == 2024) & (df["quarter"] == 1) & (df["region"] == "riyadh")]
        elapsed = time.perf_counter() - start

        assert elapsed < 0.01, f"Filtering took {elapsed:.3f}s, should be < 10ms"

    def test_batch_change_calculation(self, large_dataframe):
        """Test batch change calculation performance."""
        from analytics_hub_platform.utils.dataframe_adapter import batch_calculate_change

        df = large_dataframe
        current = df["sustainability_index"]
        previous = df["sustainability_index"].shift(1)

        start = time.perf_counter()
        abs_change, pct_change = batch_calculate_change(current, previous)
        elapsed = time.perf_counter() - start

        assert elapsed < 0.01, f"Batch calculation took {elapsed:.3f}s, should be < 10ms"
        assert len(abs_change) == len(df)


class TestRepositoryPerformance:
    """Test repository query performance."""

    @pytest.fixture
    def repository(self):
        """Get repository instance."""
        from analytics_hub_platform.infrastructure.repository import get_repository

        return get_repository()

    def test_get_all_indicators_performance(self, repository):
        """Test get_all_indicators query performance."""
        start = time.perf_counter()
        df = repository.get_all_indicators("demo_tenant")
        elapsed = time.perf_counter() - start

        assert elapsed < MEDIUM_OPERATION_THRESHOLD, f"Query took {elapsed:.3f}s"
        assert isinstance(df, pd.DataFrame)

    def test_get_available_periods_performance(self, repository):
        """Test get_available_periods query performance."""
        start = time.perf_counter()
        periods = repository.get_available_periods("demo_tenant")
        elapsed = time.perf_counter() - start

        assert elapsed < FAST_OPERATION_THRESHOLD, f"Query took {elapsed:.3f}s"
        assert isinstance(periods, list)

    def test_get_available_regions_performance(self, repository):
        """Test get_available_regions query performance."""
        start = time.perf_counter()
        regions = repository.get_available_regions("demo_tenant")
        elapsed = time.perf_counter() - start

        assert elapsed < FAST_OPERATION_THRESHOLD, f"Query took {elapsed:.3f}s"
        assert isinstance(regions, list)


class TestServicePerformance:
    """Test service layer performance."""

    @pytest.fixture
    def sample_data(self) -> pd.DataFrame:
        """Create sample data for service tests."""
        np.random.seed(42)
        n_rows = 1000

        regions = ["riyadh", "makkah", "eastern", "madinah", "qassim"]

        return pd.DataFrame(
            {
                "year": np.repeat([2023, 2024], n_rows // 2),
                "quarter": np.tile([1, 2, 3, 4], n_rows // 4),
                "region": np.random.choice(regions, n_rows),
                "sustainability_index": np.random.uniform(40, 90, n_rows),
                "gdp_growth": np.random.uniform(1, 6, n_rows),
                "renewable_share": np.random.uniform(5, 30, n_rows),
                "co2_index": np.random.uniform(60, 95, n_rows),
                "green_jobs": np.random.uniform(80, 200, n_rows),
                "unemployment_rate": np.random.uniform(7, 13, n_rows),
                "data_quality_score": np.random.uniform(0.7, 1.0, n_rows),
                "export_diversity_index": np.random.uniform(0.4, 0.8, n_rows),
                "water_efficiency": np.random.uniform(50, 80, n_rows),
                "air_quality_index": np.random.uniform(60, 90, n_rows),
            }
        )

    def test_executive_snapshot_performance(self, sample_data):
        """Test executive snapshot generation performance."""
        from analytics_hub_platform.domain.models import FilterParams
        from analytics_hub_platform.domain.services import get_executive_snapshot

        filters = FilterParams(
            tenant_id="test",
            year=2024,
            quarter=1,
            region=None,
        )

        start = time.perf_counter()
        snapshot = get_executive_snapshot(sample_data, filters, "en")
        elapsed = time.perf_counter() - start

        assert elapsed < FAST_OPERATION_THRESHOLD, f"Snapshot took {elapsed:.3f}s"
        assert "metrics" in snapshot

    def test_sustainability_summary_performance(self, sample_data):
        """Test sustainability summary generation performance."""
        from analytics_hub_platform.domain.models import FilterParams
        from analytics_hub_platform.domain.services import get_sustainability_summary

        filters = FilterParams(
            tenant_id="test",
            year=2024,
            quarter=1,
            region=None,
        )

        start = time.perf_counter()
        summary = get_sustainability_summary(sample_data, filters, "en")
        elapsed = time.perf_counter() - start

        assert elapsed < FAST_OPERATION_THRESHOLD, f"Summary took {elapsed:.3f}s"
        assert "index" in summary or "status" in summary

    def test_data_quality_metrics_performance(self, sample_data):
        """Test data quality metrics generation performance."""
        from analytics_hub_platform.domain.models import FilterParams
        from analytics_hub_platform.domain.services import get_data_quality_metrics

        filters = FilterParams(
            tenant_id="test",
            year=2024,
            quarter=1,
            region=None,
        )

        start = time.perf_counter()
        get_data_quality_metrics(sample_data, filters)
        elapsed = time.perf_counter() - start

        assert elapsed < FAST_OPERATION_THRESHOLD, f"Quality metrics took {elapsed:.3f}s"


class TestIndicatorPerformance:
    """Test indicator calculation performance."""

    def test_sustainability_index_calculation(self):
        """Test sustainability index calculation performance."""
        from analytics_hub_platform.domain.indicators import calculate_sustainability_index

        indicators = {
            "co2_index": 85.0,
            "renewable_share": 25.0,
            "energy_intensity": 6.0,
            "water_efficiency": 65.0,
            "waste_recycling_rate": 35.0,
            "air_quality_index": 75.0,
            "forest_coverage": 3.0,
            "green_jobs": 150.0,
        }

        # Run multiple times to measure
        times = []
        for _ in range(100):
            start = time.perf_counter()
            calculate_sustainability_index(indicators)
            times.append(time.perf_counter() - start)

        avg_time = sum(times) / len(times)
        assert avg_time < 0.01, f"Average calculation time {avg_time:.4f}s should be < 10ms"

    def test_normalize_to_100_batch(self):
        """Test batch normalization performance."""
        from analytics_hub_platform.domain.indicators import normalize_to_100

        values = list(range(1000))

        start = time.perf_counter()
        for v in values:
            normalize_to_100(float(v), 0.0, 1000.0)
        elapsed = time.perf_counter() - start

        assert elapsed < 0.1, f"Batch normalization took {elapsed:.3f}s"


class TestMemoryUsage:
    """Test memory usage patterns."""

    def test_dataframe_memory_efficiency(self):
        """Test DataFrame memory usage is reasonable."""
        np.random.seed(42)

        # Create a DataFrame similar to what we use
        df = pd.DataFrame(
            {
                "year": np.random.choice([2022, 2023, 2024], 10000),
                "quarter": np.random.choice([1, 2, 3, 4], 10000),
                "region": np.random.choice(["riyadh", "makkah"], 10000),
                "value": np.random.uniform(0, 100, 10000),
            }
        )

        # Check memory usage
        memory_mb = df.memory_usage(deep=True).sum() / (1024 * 1024)

        # Should be less than 10MB for 10k rows
        assert memory_mb < 10, f"DataFrame uses {memory_mb:.2f}MB, should be < 10MB"

    def test_cache_memory_bounds(self):
        """Test that cache memory usage is bounded."""
        from analytics_hub_platform.infrastructure.caching import get_cache

        cache = get_cache()
        cache.clear()

        # Add many items
        for i in range(1000):
            cache.set(f"key_{i}", {"data": list(range(100))})

        # Check stats
        stats = cache.get_stats()

        # Max size should be enforced
        assert stats.get("size", 0) <= cache._max_size


class TestConcurrencyPerformance:
    """Test performance under concurrent load."""

    def test_concurrent_cache_access(self):
        """Test cache performance under concurrent access."""
        import threading

        from analytics_hub_platform.infrastructure.caching import get_cache

        cache = get_cache()
        cache.clear()

        results = []
        errors = []

        def worker(worker_id):
            try:
                for i in range(100):
                    cache.set(f"worker_{worker_id}_key_{i}", {"data": i})
                    cache.get(f"worker_{worker_id}_key_{i}")
                results.append(worker_id)
            except Exception as e:
                errors.append(str(e))

        # Create multiple threads
        threads = [threading.Thread(target=worker, args=(i,)) for i in range(10)]

        start = time.perf_counter()
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        elapsed = time.perf_counter() - start

        assert len(errors) == 0, f"Errors during concurrent access: {errors}"
        assert len(results) == 10, "All workers should complete"
        assert elapsed < 5.0, f"Concurrent operations took {elapsed:.2f}s"

        cache.clear()
