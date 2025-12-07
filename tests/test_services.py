"""
Service Layer Tests
Sustainable Economic Development Analytics Hub

Tests for domain services.
"""

import pytest
import pandas as pd
import numpy as np

from analytics_hub_platform.domain.services import (
    get_sustainability_summary,
    get_regional_comparison,
    get_indicator_timeseries,
    get_data_quality_metrics,
)
from analytics_hub_platform.domain.models import FilterParams


class TestSustainabilitySummary:
    """Tests for sustainability summary service."""
    
    def test_get_sustainability_summary(self, sample_indicator_data, sample_filter_params):
        """Test getting sustainability summary."""
        summary = get_sustainability_summary(sample_indicator_data, sample_filter_params)
        
        assert "sustainability_index" in summary
        assert "co2_per_gdp" in summary
        assert "renewable_energy_pct" in summary
        assert "data_quality_score" in summary
        
        # Values should be in expected ranges
        assert 0 <= summary["sustainability_index"] <= 100
        assert summary["co2_per_gdp"] >= 0
    
    def test_get_sustainability_summary_empty_data(self, sample_filter_params):
        """Test summary with empty data."""
        empty_df = pd.DataFrame()
        
        summary = get_sustainability_summary(empty_df, sample_filter_params)
        
        assert summary["sustainability_index"] == 0
    
    def test_get_sustainability_summary_with_region_filter(self, sample_indicator_data):
        """Test summary with region filter."""
        params = FilterParams(
            tenant_id="test_tenant",
            year=2024,
            region="Riyadh",
        )
        
        summary = get_sustainability_summary(sample_indicator_data, params)
        
        assert "sustainability_index" in summary


class TestRegionalComparison:
    """Tests for regional comparison service."""
    
    def test_get_regional_comparison(self, sample_indicator_data, sample_filter_params):
        """Test getting regional comparison."""
        comparisons = get_regional_comparison(
            sample_indicator_data,
            sample_filter_params,
            indicator="sustainability_index",
        )
        
        assert len(comparisons) > 0
        
        # Check structure
        first = comparisons[0]
        assert "region" in first
        assert "value" in first
        assert "rank" in first
        
        # Ranks should be sequential
        ranks = [c["rank"] for c in comparisons]
        assert ranks == list(range(1, len(ranks) + 1))
    
    def test_get_regional_comparison_sorted(self, sample_indicator_data, sample_filter_params):
        """Test that regional comparison is sorted by value."""
        comparisons = get_regional_comparison(
            sample_indicator_data,
            sample_filter_params,
            indicator="sustainability_index",
        )
        
        values = [c["value"] for c in comparisons]
        assert values == sorted(values, reverse=True)


class TestIndicatorTimeseries:
    """Tests for indicator time series service."""
    
    def test_get_indicator_timeseries(self, sample_indicator_data, sample_filter_params):
        """Test getting indicator time series."""
        timeseries = get_indicator_timeseries(
            sample_indicator_data,
            sample_filter_params,
            indicator="sustainability_index",
        )
        
        assert len(timeseries) > 0
        
        # Check structure
        first = timeseries[0]
        assert "period" in first
        assert "value" in first
        assert "year" in first
        assert "quarter" in first
    
    def test_get_indicator_timeseries_sorted(self, sample_indicator_data, sample_filter_params):
        """Test that time series is sorted chronologically."""
        timeseries = get_indicator_timeseries(
            sample_indicator_data,
            sample_filter_params,
            indicator="sustainability_index",
        )
        
        # Create sortable tuples
        periods = [(t["year"], t["quarter"]) for t in timeseries]
        assert periods == sorted(periods)
    
    def test_get_indicator_timeseries_with_region(self, sample_indicator_data):
        """Test time series filtered by region."""
        params = FilterParams(
            tenant_id="test_tenant",
            region="Riyadh",
        )
        
        timeseries = get_indicator_timeseries(
            sample_indicator_data,
            params,
            indicator="sustainability_index",
        )
        
        assert len(timeseries) > 0


class TestDataQualityMetrics:
    """Tests for data quality metrics service."""
    
    def test_get_data_quality_metrics(self, sample_indicator_data, sample_filter_params):
        """Test getting data quality metrics."""
        metrics = get_data_quality_metrics(sample_indicator_data, sample_filter_params)
        
        assert "completeness" in metrics
        assert "avg_quality_score" in metrics
        assert "records_count" in metrics
        assert "missing_by_kpi" in metrics
        
        # Completeness should be 0-100
        assert 0 <= metrics["completeness"] <= 100
        
        # Records count should match data
        assert metrics["records_count"] > 0
    
    def test_get_data_quality_metrics_with_missing(self, sample_filter_params):
        """Test quality metrics with missing values."""
        data = pd.DataFrame({
            "tenant_id": ["test"] * 10,
            "year": [2024] * 10,
            "quarter": [4] * 10,
            "region": ["Riyadh"] * 10,
            "sustainability_index": [50, None, 60, None, 70, 55, None, 65, 75, 80],
            "co2_per_gdp": [0.4] * 10,
            "data_quality_score": [80] * 10,
        })
        
        metrics = get_data_quality_metrics(data, sample_filter_params)
        
        # Should detect missing values
        assert metrics["completeness"] < 100
        assert "sustainability_index" in metrics["missing_by_kpi"]
    
    def test_get_data_quality_metrics_empty(self, sample_filter_params):
        """Test quality metrics with empty data."""
        empty_df = pd.DataFrame()
        
        metrics = get_data_quality_metrics(empty_df, sample_filter_params)
        
        assert metrics["completeness"] == 0
        assert metrics["records_count"] == 0
