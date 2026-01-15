"""
Data Quality Module
Sustainable Economic Development Analytics Hub

Provides data quality checks including:
- Completeness analysis
- Timeliness checks
- Outlier detection
- Validity checks
- DQ scoring and reporting
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

import numpy as np
import pandas as pd

from analytics_hub_platform.infrastructure.db_init import get_engine, sustainability_indicators
from analytics_hub_platform.infrastructure.prod_logging import get_correlated_logger

logger = get_correlated_logger("analytics_hub.data_quality")


# =============================================================================
# DATA QUALITY MODELS
# =============================================================================


@dataclass
class DQCheck:
    """Result of a single data quality check."""

    name: str
    category: str  # completeness, timeliness, validity, consistency, outliers
    passed: bool
    score: float  # 0-100
    message: str
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class DQReport:
    """Complete data quality report."""

    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    tenant_id: str = ""
    overall_score: float = 0.0
    checks: list[DQCheck] = field(default_factory=list)
    summary: dict[str, Any] = field(default_factory=dict)

    @property
    def passed_checks(self) -> int:
        return sum(1 for c in self.checks if c.passed)

    @property
    def failed_checks(self) -> int:
        return sum(1 for c in self.checks if not c.passed)

    @property
    def status(self) -> str:
        if self.overall_score >= 90:
            return "excellent"
        elif self.overall_score >= 70:
            return "good"
        elif self.overall_score >= 50:
            return "fair"
        else:
            return "poor"


# =============================================================================
# COMPLETENESS CHECKS
# =============================================================================


def check_completeness(df: pd.DataFrame, required_columns: list[str]) -> DQCheck:
    """
    Check for missing values in required columns.

    Args:
        df: DataFrame to check
        required_columns: List of columns that should have no nulls

    Returns:
        DQCheck result
    """
    total_cells = len(df) * len(required_columns)
    if total_cells == 0:
        return DQCheck(
            name="Required Fields Completeness",
            category="completeness",
            passed=False,
            score=0.0,
            message="No data to check",
        )

    present_columns = [c for c in required_columns if c in df.columns]
    if not present_columns:
        return DQCheck(
            name="Required Fields Completeness",
            category="completeness",
            passed=False,
            score=0.0,
            message="Required columns not found",
        )

    null_counts = df[present_columns].isnull().sum()
    total_nulls = null_counts.sum()
    completeness = ((total_cells - total_nulls) / total_cells) * 100

    column_details = {col: int(null_counts[col]) for col in present_columns if null_counts[col] > 0}

    return DQCheck(
        name="Required Fields Completeness",
        category="completeness",
        passed=completeness >= 95,
        score=round(completeness, 2),
        message=f"{completeness:.1f}% complete ({total_nulls} nulls in {len(df)} rows)",
        details={"null_counts_by_column": column_details, "total_nulls": int(total_nulls)},
    )


def check_indicator_coverage(df: pd.DataFrame, indicator_columns: list[str]) -> DQCheck:
    """
    Check coverage of indicator columns.

    Args:
        df: DataFrame to check
        indicator_columns: List of indicator columns

    Returns:
        DQCheck result
    """
    present_columns = [c for c in indicator_columns if c in df.columns]
    _coverage = (len(present_columns) / len(indicator_columns)) * 100 if indicator_columns else 0  # noqa: F841

    non_null_coverage = {}
    for col in present_columns:
        non_null_pct = (1 - df[col].isnull().mean()) * 100
        non_null_coverage[col] = round(non_null_pct, 1)

    avg_coverage = np.mean(list(non_null_coverage.values())) if non_null_coverage else 0

    return DQCheck(
        name="Indicator Coverage",
        category="completeness",
        passed=bool(avg_coverage >= 80),
        score=float(round(avg_coverage, 2)),
        message=f"{len(present_columns)}/{len(indicator_columns)} columns present, {avg_coverage:.1f}% average fill rate",
        details={"columns_present": present_columns, "coverage_by_column": non_null_coverage},
    )


# =============================================================================
# TIMELINESS CHECKS
# =============================================================================


def check_data_freshness(df: pd.DataFrame, max_age_days: int = 45) -> DQCheck:
    """
    Check if data was loaded recently.

    Args:
        df: DataFrame with load_timestamp column
        max_age_days: Maximum acceptable age in days

    Returns:
        DQCheck result
    """
    if "load_timestamp" not in df.columns:
        return DQCheck(
            name="Data Freshness",
            category="timeliness",
            passed=True,
            score=100.0,
            message="No load_timestamp column (skipped)",
        )

    now = datetime.now(timezone.utc)
    max_load = pd.to_datetime(df["load_timestamp"]).max()

    if pd.isna(max_load):
        return DQCheck(
            name="Data Freshness",
            category="timeliness",
            passed=False,
            score=0.0,
            message="No valid load timestamps found",
        )

    # Handle timezone
    if max_load.tzinfo is None:
        max_load = max_load.replace(tzinfo=timezone.utc)

    age_days = (now - max_load).days
    freshness_score = max(0, 100 - (age_days / max_age_days * 100))

    return DQCheck(
        name="Data Freshness",
        category="timeliness",
        passed=age_days <= max_age_days,
        score=round(min(100, freshness_score), 2),
        message=f"Most recent data is {age_days} days old (max: {max_age_days})",
        details={"last_load": str(max_load), "age_days": age_days},
    )


def check_temporal_coverage(df: pd.DataFrame, min_quarters: int = 8) -> DQCheck:
    """
    Check for sufficient historical data.

    Args:
        df: DataFrame with year and quarter columns
        min_quarters: Minimum number of quarters required

    Returns:
        DQCheck result
    """
    if "year" not in df.columns or "quarter" not in df.columns:
        return DQCheck(
            name="Temporal Coverage",
            category="timeliness",
            passed=False,
            score=0.0,
            message="Missing year/quarter columns",
        )

    periods = df[["year", "quarter"]].drop_duplicates()
    num_periods = len(periods)

    coverage_score = min(100, (num_periods / min_quarters) * 100)

    return DQCheck(
        name="Temporal Coverage",
        category="timeliness",
        passed=num_periods >= min_quarters,
        score=round(coverage_score, 2),
        message=f"{num_periods} quarters of data (min: {min_quarters})",
        details={"quarters_available": num_periods, "min_required": min_quarters},
    )


# =============================================================================
# VALIDITY CHECKS
# =============================================================================


def check_range_validity(df: pd.DataFrame, field_ranges: dict[str, tuple[float, float]]) -> DQCheck:
    """
    Check if values are within expected ranges.

    Args:
        df: DataFrame to check
        field_ranges: Dict of field -> (min, max)

    Returns:
        DQCheck result
    """
    total_values = 0
    out_of_range = 0
    violations = {}

    for col, (min_val, max_val) in field_ranges.items():
        if col not in df.columns:
            continue

        values = df[col].dropna()
        total_values += len(values)

        below = (values < min_val).sum()
        above = (values > max_val).sum()
        violations_count = below + above

        if violations_count > 0:
            out_of_range += violations_count
            violations[col] = {
                "below_min": int(below),
                "above_max": int(above),
                "min": min_val,
                "max": max_val,
            }

    validity_score = ((total_values - out_of_range) / total_values * 100) if total_values > 0 else 100

    return DQCheck(
        name="Range Validity",
        category="validity",
        passed=validity_score >= 99,
        score=round(validity_score, 2),
        message=f"{out_of_range} values out of range ({validity_score:.1f}% valid)",
        details={"violations": violations, "total_checked": total_values},
    )


def check_referential_integrity(df: pd.DataFrame, valid_values: dict[str, list]) -> DQCheck:
    """
    Check if categorical values are in allowed lists.

    Args:
        df: DataFrame to check
        valid_values: Dict of column -> allowed values

    Returns:
        DQCheck result
    """
    violations = {}
    total_checked = 0

    for col, allowed in valid_values.items():
        if col not in df.columns:
            continue

        values = df[col].dropna()
        total_checked += len(values)
        invalid = values[~values.isin(allowed)]

        if len(invalid) > 0:
            violations[col] = invalid.unique().tolist()[:10]  # Limit to 10 examples

    validity_score = 100 if not violations else max(0, 100 - len(violations) * 10)

    return DQCheck(
        name="Referential Integrity",
        category="validity",
        passed=len(violations) == 0,
        score=validity_score,
        message=f"{len(violations)} columns with invalid values" if violations else "All values valid",
        details={"violations": violations},
    )


# =============================================================================
# OUTLIER DETECTION
# =============================================================================


def check_outliers(df: pd.DataFrame, numeric_columns: list[str], z_threshold: float = 3.0) -> DQCheck:
    """
    Detect outliers using z-score method.

    Args:
        df: DataFrame to check
        numeric_columns: List of numeric columns to check
        z_threshold: Z-score threshold for outlier detection

    Returns:
        DQCheck result
    """
    outliers = {}
    total_values = 0
    total_outliers = 0

    for col in numeric_columns:
        if col not in df.columns:
            continue

        values = df[col].dropna()
        if len(values) < 10:  # Need enough data for meaningful z-scores
            continue

        total_values += len(values)

        mean = values.mean()
        std = values.std()

        if std == 0:
            continue

        z_scores = np.abs((values - mean) / std)
        outlier_mask = z_scores > z_threshold
        outlier_count = outlier_mask.sum()

        if outlier_count > 0:
            total_outliers += outlier_count
            outliers[col] = {
                "count": int(outlier_count),
                "percentage": round(outlier_count / len(values) * 100, 2),
                "examples": values[outlier_mask].head(5).tolist(),
            }

    outlier_rate = (total_outliers / total_values * 100) if total_values > 0 else 0
    score = max(0, 100 - outlier_rate * 10)

    return DQCheck(
        name="Outlier Detection",
        category="outliers",
        passed=outlier_rate < 5,
        score=round(score, 2),
        message=f"{total_outliers} outliers detected ({outlier_rate:.2f}%)",
        details={"outliers_by_column": outliers, "z_threshold": z_threshold},
    )


def check_quarter_over_quarter_changes(
    df: pd.DataFrame,
    value_column: str,
    max_change_pct: float = 50.0,
) -> DQCheck:
    """
    Check for unusually large quarter-over-quarter changes.

    Args:
        df: DataFrame with year, quarter, and value columns
        value_column: Column to check for changes
        max_change_pct: Maximum acceptable percentage change

    Returns:
        DQCheck result
    """
    if value_column not in df.columns or "year" not in df.columns or "quarter" not in df.columns:
        return DQCheck(
            name=f"QoQ Changes ({value_column})",
            category="outliers",
            passed=True,
            score=100.0,
            message="Columns not available (skipped)",
        )

    # Sort and calculate changes
    df_sorted = df.sort_values(["year", "quarter"])
    df_sorted["_prev"] = df_sorted[value_column].shift(1)
    df_sorted["_change_pct"] = (
        (df_sorted[value_column] - df_sorted["_prev"]) / df_sorted["_prev"].abs() * 100
    )

    # Find excessive changes
    excessive = df_sorted[df_sorted["_change_pct"].abs() > max_change_pct]

    if len(excessive) > 0:
        examples = excessive[["year", "quarter", value_column, "_change_pct"]].head(5).to_dict("records")
    else:
        examples = []

    score = max(0, 100 - len(excessive) * 10)

    return DQCheck(
        name=f"QoQ Changes ({value_column})",
        category="outliers",
        passed=len(excessive) == 0,
        score=round(score, 2),
        message=f"{len(excessive)} excessive quarter-over-quarter changes",
        details={"max_change_pct": max_change_pct, "examples": examples},
    )


# =============================================================================
# MAIN DQ REPORT GENERATION
# =============================================================================


def generate_dq_report(tenant_id: str) -> DQReport:
    """
    Generate a complete data quality report for a tenant.

    Args:
        tenant_id: Tenant identifier

    Returns:
        DQReport with all checks
    """
    from analytics_hub_platform.infrastructure.data_ingestion import (
        FIELD_RANGES,
        INDICATOR_COLUMNS,
        REQUIRED_COLUMNS,
        VALID_REGIONS,
    )

    report = DQReport(tenant_id=tenant_id)

    # Load data
    engine = get_engine()
    from sqlalchemy import select

    with engine.connect() as conn:
        query = select(sustainability_indicators).where(
            sustainability_indicators.c.tenant_id == tenant_id
        )
        df = pd.read_sql(query, conn)

    if len(df) == 0:
        report.overall_score = 0
        report.checks.append(
            DQCheck(
                name="Data Availability",
                category="completeness",
                passed=False,
                score=0,
                message="No data found for tenant",
            )
        )
        return report

    # Run all checks
    report.checks.extend(
        [
            # Completeness
            check_completeness(df, REQUIRED_COLUMNS),
            check_indicator_coverage(df, INDICATOR_COLUMNS),
            # Timeliness
            check_data_freshness(df),
            check_temporal_coverage(df),
            # Validity
            check_range_validity(df, FIELD_RANGES),
            check_referential_integrity(df, {"region": VALID_REGIONS}),
            # Outliers
            check_outliers(df, INDICATOR_COLUMNS),
            check_quarter_over_quarter_changes(df, "gdp_growth"),
            check_quarter_over_quarter_changes(df, "unemployment_rate"),
        ]
    )

    # Calculate overall score (weighted average)
    weights = {
        "completeness": 0.30,
        "timeliness": 0.20,
        "validity": 0.25,
        "outliers": 0.15,
        "consistency": 0.10,
    }

    category_scores = {}
    for check in report.checks:
        if check.category not in category_scores:
            category_scores[check.category] = []
        category_scores[check.category].append(check.score)

    weighted_score = 0
    total_weight = 0
    for category, scores in category_scores.items():
        weight = weights.get(category, 0.1)
        weighted_score += np.mean(scores) * weight
        total_weight += weight

    report.overall_score = round(weighted_score / total_weight, 2) if total_weight > 0 else 0

    # Summary
    report.summary = {
        "total_rows": len(df),
        "unique_periods": df[["year", "quarter"]].drop_duplicates().shape[0],
        "unique_regions": df["region"].nunique(),
        "checks_passed": report.passed_checks,
        "checks_failed": report.failed_checks,
        "category_scores": {k: round(np.mean(v), 2) for k, v in category_scores.items()},
    }

    logger.info(f"DQ report generated: score={report.overall_score}, status={report.status}")

    return report
