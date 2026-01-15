"""
Tests for Repository and Data Access
"""

import pandas as pd


class TestRepository:
    """Tests for Repository class."""

    def test_repository_singleton(self, test_db):
        """Test that get_repository returns singleton."""
        from analytics_hub_platform.infrastructure.repository import get_repository

        repo1 = get_repository()
        repo2 = get_repository()

        assert repo1 is repo2

    def test_get_all_indicators(self, test_db):
        """Test fetching all indicators."""
        from analytics_hub_platform.infrastructure.repository import get_repository

        repo = get_repository()
        df = repo.get_all_indicators("ministry_economy")

        assert isinstance(df, pd.DataFrame)
        # May be empty if no data seeded, but should still be a DataFrame
        assert hasattr(df, 'columns')

    def test_get_indicators_with_filter(self, test_db, sample_filter_params):
        """Test fetching indicators with filter params."""
        from analytics_hub_platform.infrastructure.repository import get_repository

        repo = get_repository()
        df = repo.get_all_indicators(sample_filter_params.tenant_id, filters=sample_filter_params)

        assert isinstance(df, pd.DataFrame)
        # All rows should match the filter year/quarter
        if len(df) > 0:
            assert (df["year"] == sample_filter_params.year).all()
            assert (df["quarter"] == sample_filter_params.quarter).all()

    def test_get_available_periods(self, test_db):
        """Test fetching available periods."""
        from analytics_hub_platform.infrastructure.repository import get_repository

        repo = get_repository()
        periods = repo.get_available_periods("ministry_economy")

        assert isinstance(periods, list)
        # Each period should have year, quarter, and label
        for period in periods:
            assert "year" in period
            assert "quarter" in period
            assert "label" in period

    def test_get_available_regions(self, test_db):
        """Test fetching available regions."""
        from analytics_hub_platform.infrastructure.repository import get_repository

        repo = get_repository()
        regions = repo.get_available_regions("ministry_economy")

        assert isinstance(regions, list)


class TestDatabaseInitialization:
    """Tests for database initialization."""

    def test_initialize_database(self):
        """Test database initialization."""
        from analytics_hub_platform.infrastructure.db_init import initialize_database

        # Should not raise any exceptions
        initialize_database()

    def test_get_engine(self):
        """Test getting database engine."""
        from analytics_hub_platform.infrastructure.db_init import get_engine

        engine = get_engine()

        assert engine is not None
        # Engine should be reusable (cached)
        engine2 = get_engine()
        assert engine is engine2


class TestDataIntegrity:
    """Tests for data integrity."""

    def test_no_null_required_fields(self, test_db):
        """Test that required fields have no nulls."""
        from analytics_hub_platform.infrastructure.repository import get_repository

        repo = get_repository()
        df = repo.get_all_indicators("ministry_economy")

        required_fields = ["year", "quarter", "region"]
        for field in required_fields:
            if field in df.columns:
                assert df[field].notna().all(), f"Null values found in {field}"

    def test_year_range_valid(self, test_db):
        """Test that years are in valid range."""
        from analytics_hub_platform.infrastructure.repository import get_repository

        repo = get_repository()
        df = repo.get_all_indicators("ministry_economy")

        if "year" in df.columns and len(df) > 0:
            assert df["year"].min() >= 2020
            assert df["year"].max() <= 2030

    def test_quarter_range_valid(self, test_db):
        """Test that quarters are 1-4."""
        from analytics_hub_platform.infrastructure.repository import get_repository

        repo = get_repository()
        df = repo.get_all_indicators("ministry_economy")

        if "quarter" in df.columns and len(df) > 0:
            assert df["quarter"].min() >= 1
            assert df["quarter"].max() <= 4
