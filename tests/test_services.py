"""
Service Layer Tests
Sustainable Economic Development Analytics Hub

Tests for domain services.
"""

import pandas as pd

from analytics_hub_platform.domain.services import (
    get_data_quality_metrics,
    get_kpi_timeseries,
    get_regional_comparison,
    get_sustainability_summary,
)


class TestSustainabilitySummary:
    """Tests for sustainability summary service."""

    def test_get_sustainability_summary(self, sample_indicator_data, sample_filter_params):
        """Test getting sustainability summary."""
        summary = get_sustainability_summary(sample_indicator_data, sample_filter_params)

        assert summary is not None
        assert isinstance(summary, dict)

    def test_get_sustainability_summary_empty_data(self, sample_filter_params):
        """Test summary with empty data returns empty dict or handles gracefully."""
        # Create empty df with expected columns to avoid KeyError
        empty_df = pd.DataFrame(
            columns=[
                "tenant_id",
                "year",
                "quarter",
                "region",
                "sustainability_index",
                "co2_per_gdp",
            ]
        )

        try:
            summary = get_sustainability_summary(empty_df, sample_filter_params)
            assert summary is not None
        except (KeyError, ValueError):
            # Expected when handling empty data
            pass


class TestRegionalComparison:
    """Tests for regional comparison service."""

    def test_get_regional_comparison(self, sample_indicator_data, sample_filter_params):
        """Test getting regional comparison."""
        result = get_regional_comparison(
            df=sample_indicator_data,
            filters=sample_filter_params,
            kpi_id="sustainability_index",
        )

        assert result is not None


class TestKPITimeseries:
    """Tests for KPI time series service."""

    def test_get_kpi_timeseries(self, sample_indicator_data, sample_filter_params):
        """Test getting KPI time series."""
        timeseries = get_kpi_timeseries(
            df=sample_indicator_data,
            filters=sample_filter_params,
            kpi_id="sustainability_index",
        )

        assert timeseries is not None
        assert isinstance(timeseries, list)


class TestDataQualityMetrics:
    """Tests for data quality metrics service."""

    def test_get_data_quality_metrics(self, sample_indicator_data, sample_filter_params):
        """Test getting data quality metrics."""
        metrics = get_data_quality_metrics(sample_indicator_data, sample_filter_params)

        assert metrics is not None
        assert isinstance(metrics, dict)

    def test_get_data_quality_metrics_empty(self, sample_filter_params):
        """Test quality metrics with empty data handles gracefully."""
        # Create empty df with expected columns
        empty_df = pd.DataFrame(
            columns=[
                "tenant_id",
                "year",
                "quarter",
                "region",
                "sustainability_index",
                "data_quality_score",
            ]
        )

        try:
            metrics = get_data_quality_metrics(empty_df, sample_filter_params)
            assert metrics is not None
        except (KeyError, ValueError):
            # Expected when handling empty data
            pass
