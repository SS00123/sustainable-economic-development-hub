"""
DataFrame Adapter
Sustainable Economic Development Analytics Hub
Ministry of Economy and Planning

This module provides adapter functions to convert between pandas DataFrames
and domain models, keeping domain logic independent of DataFrame operations.

Design Pattern:
- Domain services work with domain models (IndicatorRecord, SummaryMetrics, etc.)
- DataFrame adapters handle all pandas-specific transformations
- Clear separation of concerns for maintainability
"""

from datetime import datetime, timezone

import numpy as np
import pandas as pd

from analytics_hub_platform.domain.models import (
    IndicatorRecord,
    KPIStatus,
    RegionalComparison,
    TimeSeriesPoint,
)

# =============================================================================
# VECTORIZED UTILITIES (Performance optimizations)
# =============================================================================


def add_period_column(
    df: pd.DataFrame,
    year_col: str = "year",
    quarter_col: str = "quarter",
    period_col: str = "period",
) -> pd.DataFrame:
    """
    Add period column using vectorized string operations.

    This is significantly faster than df.apply(lambda r: f"Q{r['quarter']} {r['year']}", axis=1)
    for large DataFrames.

    Args:
        df: DataFrame with year and quarter columns
        year_col: Name of year column
        quarter_col: Name of quarter column
        period_col: Name for new period column

    Returns:
        DataFrame with added period column

    Example:
        >>> df = add_period_column(df)  # Creates 'period' column with values like 'Q1 2024'
    """
    if df.empty:
        df[period_col] = []
        return df

    # Vectorized string concatenation - much faster than apply()
    df[period_col] = "Q" + df[quarter_col].astype(str) + " " + df[year_col].astype(str)
    return df


def create_period_series(
    year: pd.Series,
    quarter: pd.Series,
) -> pd.Series:
    """
    Create period strings from year and quarter series.

    Vectorized operation for high performance.

    Args:
        year: Series of year values
        quarter: Series of quarter values

    Returns:
        Series of period strings like 'Q1 2024'
    """
    return "Q" + quarter.astype(str) + " " + year.astype(str)


def batch_calculate_change(
    current: pd.Series,
    previous: pd.Series,
) -> tuple[pd.Series, pd.Series]:
    """
    Calculate absolute and percent change for entire columns.

    Vectorized operation - much faster than row-by-row calculation.

    Args:
        current: Series of current values
        previous: Series of previous values

    Returns:
        Tuple of (absolute_change, percent_change) Series
    """
    abs_change = current - previous

    # Handle division by zero
    with np.errstate(divide="ignore", invalid="ignore"):
        pct_change = np.where(previous != 0, (abs_change / previous) * 100, np.nan)

    return pd.Series(abs_change), pd.Series(pct_change)


def vectorized_status(
    values: pd.Series,
    green_threshold: float,
    amber_threshold: float,
    higher_is_better: bool = True,
) -> pd.Series:
    """
    Determine status for entire column using vectorized operations.

    Args:
        values: Series of values to evaluate
        green_threshold: Threshold for green status
        amber_threshold: Threshold for amber status
        higher_is_better: If True, higher values are better

    Returns:
        Series of status strings ('green', 'amber', 'red')
    """
    if higher_is_better:
        conditions = [
            values >= green_threshold,
            values >= amber_threshold,
        ]
    else:
        conditions = [
            values <= green_threshold,
            values <= amber_threshold,
        ]

    choices = ["green", "amber"]
    return pd.Series(np.select(conditions, choices, default="red"))


def dataframe_to_indicator_records(df: pd.DataFrame) -> list[IndicatorRecord]:
    """
    Convert DataFrame to list of IndicatorRecord domain models.

    Args:
        df: DataFrame with indicator data (must have: tenant_id, kpi_id,
            year, quarter, region, value)

    Returns:
        List of IndicatorRecord objects

    Example:
        >>> df = repository.get_all_indicators(tenant_id, filters)
        >>> records = dataframe_to_indicator_records(df)
        >>> for record in records:
        ...     print(f"{record.kpi_id}: {record.value}")
    """
    if df.empty:
        return []

    required_cols = ["tenant_id", "kpi_id", "year", "quarter", "region", "value"]
    missing = [col for col in required_cols if col not in df.columns]

    if missing:
        raise ValueError(f"DataFrame missing required columns: {missing}")

    records = []
    for _, row in df.iterrows():
        record = IndicatorRecord(
            tenant_id=str(row["tenant_id"]),
            kpi_id=str(row["kpi_id"]),
            year=int(row["year"]),
            quarter=int(row["quarter"]),
            region=str(row["region"]),
            value=float(row["value"]),
            unit=str(row.get("unit", "")),
            target_value=float(row["target_value"]) if pd.notna(row.get("target_value")) else None,
            data_quality_score=float(row.get("data_quality_score", 1.0)),
            source=str(row.get("source", "")),
            notes=str(row.get("notes", "")),
            created_at=row.get("created_at", datetime.now(timezone.utc)),
            updated_at=row.get("updated_at", datetime.now(timezone.utc)),
        )
        records.append(record)

    return records


def indicator_records_to_dataframe(records: list[IndicatorRecord]) -> pd.DataFrame:
    """
    Convert list of IndicatorRecord domain models to DataFrame.

    Args:
        records: List of IndicatorRecord objects

    Returns:
        DataFrame with indicator data

    Example:
        >>> records = [IndicatorRecord(...), IndicatorRecord(...)]
        >>> df = indicator_records_to_dataframe(records)
        >>> repository.save_indicators(df)
    """
    if not records:
        return pd.DataFrame()

    data = [
        {
            "tenant_id": r.tenant_id,
            "kpi_id": r.kpi_id,
            "year": r.year,
            "quarter": r.quarter,
            "region": r.region,
            "value": r.value,
            "unit": r.unit,
            "target_value": r.target_value,
            "data_quality_score": r.data_quality_score,
            "source": r.source,
            "notes": r.notes,
            "created_at": r.created_at,
            "updated_at": r.updated_at,
        }
        for r in records
    ]

    return pd.DataFrame(data)


def dataframe_to_timeseries(df: pd.DataFrame, value_column: str = "value") -> list[TimeSeriesPoint]:
    """
    Convert DataFrame to list of TimeSeriesPoint domain models.

    Args:
        df: DataFrame with time series data (must have: year, quarter, value_column)
        value_column: Name of the value column (default: 'value')

    Returns:
        List of TimeSeriesPoint objects sorted by time

    Example:
        >>> df = repository.get_indicator_timeseries(tenant_id, 'gdp_growth')
        >>> timeseries = dataframe_to_timeseries(df)
        >>> for point in timeseries:
        ...     print(f"Q{point.quarter} {point.year}: {point.value}")
    """
    if df.empty:
        return []

    required_cols = ["year", "quarter", value_column]
    missing = [col for col in required_cols if col not in df.columns]

    if missing:
        raise ValueError(f"DataFrame missing required columns: {missing}")

    # Sort by time
    df = df.sort_values(["year", "quarter"])

    points = []
    for _, row in df.iterrows():
        point = TimeSeriesPoint(
            period=f"Q{int(row['quarter'])} {int(row['year'])}",
            year=int(row["year"]),
            quarter=int(row["quarter"]),
            value=float(row[value_column]),
            label=row.get("label", f"Q{int(row['quarter'])} {int(row['year'])}"),
        )
        points.append(point)

    return points


def dataframe_to_regional_comparisons(
    df: pd.DataFrame, kpi_id: str, value_column: str | None = None
) -> list[RegionalComparison]:
    """
    Convert DataFrame to list of RegionalComparison domain models.

    Args:
        df: DataFrame with regional data (must have: region, and either value_column or kpi_id)
        kpi_id: KPI identifier
        value_column: Optional specific value column (defaults to kpi_id)

    Returns:
        List of RegionalComparison objects

    Example:
        >>> df = repository.get_regional_data(tenant_id, 2024, 4)
        >>> comparisons = dataframe_to_regional_comparisons(df, 'gdp_growth')
        >>> for comp in comparisons:
        ...     print(f"{comp.region}: {comp.value}")
    """
    if df.empty:
        return []

    value_col = value_column or kpi_id

    if "region" not in df.columns or value_col not in df.columns:
        raise ValueError(f"DataFrame must have 'region' and '{value_col}' columns")

    comparisons = []
    for _, row in df.iterrows():
        comparison = RegionalComparison(
            region=str(row["region"]),
            region_name=str(row.get("region_name", row["region"])),
            value=float(row[value_col]),
            status=KPIStatus(row.get("status", "unknown")),
            rank=int(row["rank"]) if "rank" in row and pd.notna(row["rank"]) else None,
        )
        comparisons.append(comparison)

    return comparisons


def aggregate_by_period(
    df: pd.DataFrame, value_columns: list[str], aggregation: str = "mean"
) -> pd.DataFrame:
    """
    Aggregate DataFrame by time period (year, quarter).

    Args:
        df: DataFrame with time series data
        value_columns: Columns to aggregate
        aggregation: Aggregation function ('mean', 'sum', 'min', 'max')

    Returns:
        DataFrame aggregated by year and quarter

    Example:
        >>> df = repository.get_all_indicators(tenant_id)
        >>> agg_df = aggregate_by_period(df, ['gdp_growth', 'unemployment_rate'])
    """
    if df.empty:
        return df

    if "year" not in df.columns or "quarter" not in df.columns:
        raise ValueError("DataFrame must have 'year' and 'quarter' columns")

    # Filter to only existing columns
    existing_cols = [col for col in value_columns if col in df.columns]

    if not existing_cols:
        return pd.DataFrame()

    agg_func = dict.fromkeys(existing_cols, aggregation)

    result = df.groupby(["year", "quarter"]).agg(agg_func).reset_index()

    return result


def aggregate_by_region(
    df: pd.DataFrame, value_columns: list[str], aggregation: str = "mean"
) -> pd.DataFrame:
    """
    Aggregate DataFrame by region.

    Args:
        df: DataFrame with regional data
        value_columns: Columns to aggregate
        aggregation: Aggregation function ('mean', 'sum', 'min', 'max')

    Returns:
        DataFrame aggregated by region

    Example:
        >>> df = repository.get_all_indicators(tenant_id)
        >>> regional_df = aggregate_by_region(df, ['gdp_growth', 'unemployment_rate'])
    """
    if df.empty:
        return df

    if "region" not in df.columns:
        raise ValueError("DataFrame must have 'region' column")

    # Filter to only existing columns
    existing_cols = [col for col in value_columns if col in df.columns]

    if not existing_cols:
        return pd.DataFrame()

    agg_func = dict.fromkeys(existing_cols, aggregation)

    result = df.groupby("region").agg(agg_func).reset_index()

    return result


def calculate_period_changes(df: pd.DataFrame, value_column: str, periods: int = 1) -> pd.DataFrame:
    """
    Calculate period-over-period changes in a DataFrame.

    Args:
        df: DataFrame with time series data (must be sorted by year, quarter)
        value_column: Column to calculate changes for
        periods: Number of periods to look back (1 = quarter-over-quarter)

    Returns:
        DataFrame with added change columns (absolute and percentage)

    Example:
        >>> df = repository.get_indicator_timeseries(tenant_id, 'gdp_growth')
        >>> df_with_changes = calculate_period_changes(df, 'value')
        >>> # Now has 'value_change' and 'value_change_pct' columns
    """
    if df.empty or value_column not in df.columns:
        return df

    # Ensure sorted
    if "year" in df.columns and "quarter" in df.columns:
        df = df.sort_values(["year", "quarter"])

    # Calculate absolute change
    df[f"{value_column}_change"] = df[value_column].diff(periods)

    # Calculate percentage change
    df[f"{value_column}_change_pct"] = df[value_column].pct_change(periods) * 100

    return df


def filter_by_date_range(
    df: pd.DataFrame, start_year: int, start_quarter: int, end_year: int, end_quarter: int
) -> pd.DataFrame:
    """
    Filter DataFrame to a specific date range.

    Args:
        df: DataFrame with year and quarter columns
        start_year: Start year (inclusive)
        start_quarter: Start quarter (inclusive)
        end_year: End year (inclusive)
        end_quarter: End quarter (inclusive)

    Returns:
        Filtered DataFrame

    Example:
        >>> df = repository.get_all_indicators(tenant_id)
        >>> # Get data from Q1 2023 to Q4 2024
        >>> df_filtered = filter_by_date_range(df, 2023, 1, 2024, 4)
    """
    if df.empty:
        return df

    if "year" not in df.columns or "quarter" not in df.columns:
        raise ValueError("DataFrame must have 'year' and 'quarter' columns")

    # Create time index for comparison
    df = df.copy()
    df["_time_idx"] = df["year"] * 4 + df["quarter"]
    start_idx = start_year * 4 + start_quarter
    end_idx = end_year * 4 + end_quarter

    result = df[(df["_time_idx"] >= start_idx) & (df["_time_idx"] <= end_idx)]
    result = result.drop("_time_idx", axis=1)

    return result


__all__ = [
    "dataframe_to_indicator_records",
    "indicator_records_to_dataframe",
    "dataframe_to_timeseries",
    "dataframe_to_regional_comparisons",
    "aggregate_by_period",
    "aggregate_by_region",
    "calculate_period_changes",
    "filter_by_date_range",
]
