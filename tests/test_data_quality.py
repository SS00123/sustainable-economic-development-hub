"""
Tests for Data Quality Module
Sustainable Economic Development Analytics Hub

Tests:
- Completeness checks
- Timeliness checks
- Validity checks
- Outlier detection
- DQ report generation
"""

from datetime import datetime, timedelta, timezone
import pytest
import pandas as pd
import numpy as np

from analytics_hub_platform.infrastructure.data_quality import (
    DQCheck,
    DQReport,
    check_completeness,
    check_indicator_coverage,
    check_data_freshness,
    check_temporal_coverage,
    check_range_validity,
    check_referential_integrity,
    check_outliers,
    check_quarter_over_quarter_changes,
)


# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def complete_dataframe() -> pd.DataFrame:
    """Create a complete DataFrame with all required fields."""
    return pd.DataFrame({
        "tenant_id": ["test"] * 8,
        "year": [2024, 2024, 2024, 2024, 2025, 2025, 2025, 2025],
        "quarter": [1, 2, 3, 4, 1, 2, 3, 4],
        "region": ["Riyadh"] * 8,
        "gdp_growth": [3.5, 3.8, 4.0, 4.2, 4.5, 4.8, 5.0, 5.2],
        "gdp_total": [850, 870, 890, 910, 930, 950, 970, 990],
        "unemployment_rate": [11.2, 11.0, 10.8, 10.5, 10.2, 10.0, 9.8, 9.5],
        "renewable_share": [12.5, 13.0, 13.5, 14.0, 14.5, 15.0, 15.5, 16.0],
        "load_timestamp": [datetime.now(timezone.utc)] * 8,
    })


@pytest.fixture
def incomplete_dataframe() -> pd.DataFrame:
    """Create a DataFrame with missing values."""
    return pd.DataFrame({
        "tenant_id": ["test", "test", None, "test"],
        "year": [2024, 2024, 2024, None],
        "quarter": [1, 2, 3, 4],
        "region": ["Riyadh", None, "Makkah", "Eastern"],
        "gdp_growth": [3.5, None, None, 4.2],
    })


@pytest.fixture
def outlier_dataframe() -> pd.DataFrame:
    """Create a DataFrame with outliers."""
    np.random.seed(42)
    normal_values = np.random.normal(50, 5, 20)  # Mean 50, std 5

    # Add outliers
    outlier_values = list(normal_values) + [100, -10, 120]  # Clear outliers

    return pd.DataFrame({
        "tenant_id": ["test"] * 23,
        "year": [2024] * 23,
        "quarter": [1] * 23,
        "region": ["Riyadh"] * 23,
        "score": outlier_values,
    })


@pytest.fixture
def stale_dataframe() -> pd.DataFrame:
    """Create a DataFrame with old data."""
    old_timestamp = datetime.now(timezone.utc) - timedelta(days=60)
    return pd.DataFrame({
        "tenant_id": ["test"],
        "year": [2024],
        "quarter": [1],
        "region": ["Riyadh"],
        "gdp_growth": [3.5],
        "load_timestamp": [old_timestamp],
    })


# =============================================================================
# COMPLETENESS TESTS
# =============================================================================


class TestCompletenessChecks:
    """Tests for completeness checks."""

    def test_complete_data_passes(self, complete_dataframe):
        """Test that complete data passes completeness check."""
        result = check_completeness(
            complete_dataframe,
            ["tenant_id", "year", "quarter", "region"]
        )

        assert result.passed == True  # Use == for numpy bool compatibility
        assert result.score >= 95
        assert result.category == "completeness"

    def test_incomplete_data_detected(self, incomplete_dataframe):
        """Test that missing values are detected."""
        result = check_completeness(
            incomplete_dataframe,
            ["tenant_id", "year", "quarter", "region"]
        )

        assert result.passed == False  # Use == for numpy bool compatibility
        assert result.score < 95
        assert result.details["total_nulls"] > 0

    def test_empty_dataframe(self):
        """Test handling of empty DataFrame."""
        df = pd.DataFrame()
        result = check_completeness(df, ["tenant_id"])

        assert result.passed is False
        assert result.score == 0

    def test_indicator_coverage(self, complete_dataframe):
        """Test indicator coverage check."""
        result = check_indicator_coverage(
            complete_dataframe,
            ["gdp_growth", "unemployment_rate", "renewable_share", "missing_col"]
        )

        assert result.category == "completeness"
        # Should have high coverage for present columns
        assert result.score > 50


# =============================================================================
# TIMELINESS TESTS
# =============================================================================


class TestTimelinessChecks:
    """Tests for timeliness checks."""

    def test_fresh_data_passes(self, complete_dataframe):
        """Test that recent data passes freshness check."""
        result = check_data_freshness(complete_dataframe, max_age_days=45)

        assert result.passed is True
        assert result.score >= 90
        assert result.category == "timeliness"

    def test_stale_data_detected(self, stale_dataframe):
        """Test that stale data is detected."""
        result = check_data_freshness(stale_dataframe, max_age_days=45)

        assert result.passed is False
        assert result.details["age_days"] > 45

    def test_no_timestamp_column(self):
        """Test handling when load_timestamp column is missing."""
        df = pd.DataFrame({"tenant_id": ["test"]})
        result = check_data_freshness(df)

        # Should skip check gracefully
        assert result.passed is True
        assert "skipped" in result.message.lower()

    def test_temporal_coverage_sufficient(self, complete_dataframe):
        """Test temporal coverage with sufficient quarters."""
        result = check_temporal_coverage(complete_dataframe, min_quarters=8)

        assert result.passed is True
        assert result.details["quarters_available"] >= 8

    def test_temporal_coverage_insufficient(self):
        """Test temporal coverage with insufficient quarters."""
        df = pd.DataFrame({
            "year": [2024, 2024],
            "quarter": [1, 2],
        })
        result = check_temporal_coverage(df, min_quarters=8)

        assert result.passed is False
        assert result.details["quarters_available"] < 8


# =============================================================================
# VALIDITY TESTS
# =============================================================================


class TestValidityChecks:
    """Tests for validity checks."""

    def test_valid_ranges_pass(self):
        """Test that values within ranges pass."""
        df = pd.DataFrame({
            "gdp_growth": [3.5, 4.0, 5.0],
            "unemployment_rate": [10, 11, 12],
        })

        result = check_range_validity(df, {
            "gdp_growth": (-20, 30),
            "unemployment_rate": (0, 50),
        })

        assert result.passed is True
        assert result.score >= 99

    def test_out_of_range_detected(self):
        """Test that out-of-range values are detected."""
        df = pd.DataFrame({
            "gdp_growth": [50.0, -25.0, 3.5],  # Two out of range
            "unemployment_rate": [10, 60, 12],  # One out of range
        })

        result = check_range_validity(df, {
            "gdp_growth": (-20, 30),
            "unemployment_rate": (0, 50),
        })

        assert result.passed == False  # Use == for numpy bool compatibility
        assert result.details["violations"]["gdp_growth"]["above_max"] > 0
        assert result.details["violations"]["gdp_growth"]["below_min"] > 0

    def test_referential_integrity_valid(self):
        """Test referential integrity with valid values."""
        df = pd.DataFrame({
            "region": ["Riyadh", "Makkah", "Eastern"],
        })

        result = check_referential_integrity(df, {
            "region": ["Riyadh", "Makkah", "Eastern", "Madinah"],
        })

        assert result.passed is True
        assert len(result.details["violations"]) == 0

    def test_referential_integrity_violations(self):
        """Test referential integrity with invalid values."""
        df = pd.DataFrame({
            "region": ["Riyadh", "InvalidCity", "AnotherBad"],
        })

        result = check_referential_integrity(df, {
            "region": ["Riyadh", "Makkah", "Eastern"],
        })

        assert result.passed is False
        assert "region" in result.details["violations"]


# =============================================================================
# OUTLIER DETECTION TESTS
# =============================================================================


class TestOutlierDetection:
    """Tests for outlier detection."""

    def test_no_outliers_in_normal_data(self):
        """Test that normal data has no outliers."""
        np.random.seed(42)
        df = pd.DataFrame({
            "score": np.random.normal(50, 5, 100),  # Normal distribution
        })

        result = check_outliers(df, ["score"], z_threshold=3.0)

        assert result.category == "outliers"
        # Should have few or no outliers
        assert result.score >= 90

    def test_outliers_detected(self, outlier_dataframe):
        """Test that outliers are detected."""
        result = check_outliers(outlier_dataframe, ["score"], z_threshold=2.5)

        # Should detect the extreme values we added
        assert result.details["outliers_by_column"].get("score") is not None

    def test_insufficient_data_skipped(self):
        """Test that small datasets are skipped."""
        df = pd.DataFrame({
            "score": [1, 2, 3, 4, 5],  # Only 5 values
        })

        result = check_outliers(df, ["score"])

        # Should not flag issues with small data
        assert result.score == 100 or "outliers_by_column" not in result.details or len(result.details["outliers_by_column"]) == 0

    def test_qoq_normal_changes(self):
        """Test quarter-over-quarter with normal changes."""
        df = pd.DataFrame({
            "year": [2024, 2024, 2024, 2024],
            "quarter": [1, 2, 3, 4],
            "gdp_growth": [3.0, 3.2, 3.5, 3.8],  # Small incremental changes
        })

        result = check_quarter_over_quarter_changes(df, "gdp_growth", max_change_pct=50)

        assert result.passed is True

    def test_qoq_excessive_changes(self):
        """Test quarter-over-quarter with excessive changes."""
        df = pd.DataFrame({
            "year": [2024, 2024, 2024, 2024],
            "quarter": [1, 2, 3, 4],
            "gdp_growth": [3.0, 10.0, 3.5, 15.0],  # Large jumps
        })

        result = check_quarter_over_quarter_changes(df, "gdp_growth", max_change_pct=50)

        assert result.passed is False
        assert len(result.details["examples"]) > 0


# =============================================================================
# DQ REPORT TESTS
# =============================================================================


class TestDQReport:
    """Tests for DQ report dataclass."""

    def test_report_initialization(self):
        """Test report initialization."""
        report = DQReport(tenant_id="test")

        assert report.tenant_id == "test"
        assert report.overall_score == 0.0
        assert len(report.checks) == 0

    def test_report_status_excellent(self):
        """Test report status for excellent score."""
        report = DQReport(overall_score=95)
        assert report.status == "excellent"

    def test_report_status_good(self):
        """Test report status for good score."""
        report = DQReport(overall_score=75)
        assert report.status == "good"

    def test_report_status_fair(self):
        """Test report status for fair score."""
        report = DQReport(overall_score=55)
        assert report.status == "fair"

    def test_report_status_poor(self):
        """Test report status for poor score."""
        report = DQReport(overall_score=35)
        assert report.status == "poor"

    def test_report_check_counts(self):
        """Test passed/failed check counting."""
        report = DQReport()
        report.checks = [
            DQCheck(name="Check1", category="test", passed=True, score=100, message="OK"),
            DQCheck(name="Check2", category="test", passed=True, score=100, message="OK"),
            DQCheck(name="Check3", category="test", passed=False, score=50, message="Fail"),
        ]

        assert report.passed_checks == 2
        assert report.failed_checks == 1


# =============================================================================
# DQ CHECK TESTS
# =============================================================================


class TestDQCheck:
    """Tests for DQ check dataclass."""

    def test_check_creation(self):
        """Test DQ check creation."""
        check = DQCheck(
            name="Test Check",
            category="completeness",
            passed=True,
            score=95.5,
            message="All data complete",
        )

        assert check.name == "Test Check"
        assert check.category == "completeness"
        assert check.passed is True
        assert check.score == 95.5
        assert check.message == "All data complete"

    def test_check_with_details(self):
        """Test DQ check with details."""
        check = DQCheck(
            name="Test Check",
            category="validity",
            passed=False,
            score=80,
            message="Some issues found",
            details={"violations": {"column1": 5}},
        )

        assert "violations" in check.details
        assert check.details["violations"]["column1"] == 5


# =============================================================================
# EDGE CASE TESTS
# =============================================================================


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_empty_dataframe_handling(self):
        """Test handling of empty DataFrame in various checks."""
        df = pd.DataFrame()

        # Completeness
        result = check_completeness(df, ["col1"])
        assert result.passed is False

        # Coverage
        result = check_indicator_coverage(df, ["col1"])
        assert result.score == 0

    def test_all_null_column(self):
        """Test handling of column with all null values."""
        df = pd.DataFrame({
            "tenant_id": [None, None, None],
            "year": [2024, 2024, 2024],
        })

        result = check_completeness(df, ["tenant_id"])
        assert result.passed == False  # Use == for numpy bool compatibility
        assert result.details["total_nulls"] == 3

    def test_single_row_dataframe(self):
        """Test handling of single-row DataFrame."""
        df = pd.DataFrame({
            "year": [2024],
            "quarter": [1],
            "value": [100],
        })

        # Temporal coverage should fail with single quarter
        result = check_temporal_coverage(df, min_quarters=8)
        assert result.passed is False

    def test_zero_std_outlier_check(self):
        """Test outlier check with zero standard deviation."""
        df = pd.DataFrame({
            "constant": [50] * 20,  # All same value
        })

        result = check_outliers(df, ["constant"])
        # Should handle gracefully (no division by zero)
        assert result.score >= 0
