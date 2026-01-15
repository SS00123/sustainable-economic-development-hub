"""
Data Validators Utility
Sustainable Economic Development Analytics Hub
Eng. Sultan Albuqami

Validation functions for data integrity and input validation.
"""

from typing import Any

import pandas as pd

from analytics_hub_platform.config.config import REGIONS
from analytics_hub_platform.domain.models import FilterParams
from analytics_hub_platform.infrastructure.exceptions import ValidationError

# Re-export ValidationError for backwards compatibility
__all__ = ["ValidationError", "ValidationResult", "validate_indicator_data"]


class ValidationResult:
    """Result of a validation operation."""

    def __init__(
        self,
        is_valid: bool = True,
        errors: list[str] | None = None,
        warnings: list[str] | None = None,
    ):
        self.is_valid = is_valid
        self.errors = errors or []
        self.warnings = warnings or []

    def add_error(self, message: str) -> None:
        """Add an error message."""
        self.errors.append(message)
        self.is_valid = False

    def add_warning(self, message: str) -> None:
        """Add a warning message."""
        self.warnings.append(message)

    def merge(self, other: "ValidationResult") -> "ValidationResult":
        """Merge another validation result into this one."""
        self.errors.extend(other.errors)
        self.warnings.extend(other.warnings)
        if not other.is_valid:
            self.is_valid = False
        return self


def validate_indicator_data(
    data: pd.DataFrame,
    required_columns: list[str] | None = None,
    strict: bool = False,
) -> ValidationResult:
    """
    Validate indicator DataFrame structure and data quality.

    Args:
        data: DataFrame to validate
        required_columns: List of required column names
        strict: If True, raise exceptions on errors

    Returns:
        ValidationResult with errors and warnings
    """
    result = ValidationResult()

    # Check if DataFrame is empty
    if data is None:
        result.add_error("Data is None")
        if strict:
            raise ValidationError("Data is None")
        return result

    if data.empty:
        result.add_warning("DataFrame is empty")
        return result

    # Default required columns
    if required_columns is None:
        required_columns = [
            "year",
            "quarter",
            "region",
            "sustainability_index",
        ]

    # Check required columns
    missing_cols = [col for col in required_columns if col not in data.columns]
    if missing_cols:
        result.add_error(f"Missing required columns: {', '.join(missing_cols)}")

    # Validate year values
    if "year" in data.columns:
        invalid_years = data[~data["year"].between(2000, 2100)]["year"].unique()
        if len(invalid_years) > 0:
            result.add_warning(f"Unusual year values detected: {invalid_years.tolist()}")

    # Validate quarter values
    if "quarter" in data.columns:
        invalid_quarters = data[~data["quarter"].isin([1, 2, 3, 4])]["quarter"].unique()
        if len(invalid_quarters) > 0:
            result.add_error(f"Invalid quarter values: {invalid_quarters.tolist()}")

    # Validate region values
    if "region" in data.columns:
        valid_regions = set(REGIONS)
        data_regions = set(data["region"].unique())
        unknown_regions = data_regions - valid_regions
        if unknown_regions:
            result.add_warning(f"Unknown regions: {unknown_regions}")

    # Validate percentage columns (should be 0-100)
    pct_columns = [
        "renewable_energy_pct",
        "green_investment_pct",
        "recycling_rate",
        "waste_diversion_rate",
        "green_building_pct",
        "public_transit_pct",
    ]

    for col in pct_columns:
        if col in data.columns:
            out_of_range = data[~data[col].between(0, 100, inclusive="both")]
            if len(out_of_range) > 0:
                result.add_warning(
                    f"{col}: {len(out_of_range)} records have values outside 0-100 range"
                )

    # Check for missing values in critical columns
    critical_cols = ["year", "quarter", "region", "tenant_id"]
    for col in critical_cols:
        if col in data.columns:
            missing_count = data[col].isna().sum()
            if missing_count > 0:
                result.add_error(f"{col}: {missing_count} missing values")

    # Check for duplicates
    if all(col in data.columns for col in ["year", "quarter", "region", "tenant_id"]):
        duplicates = data.duplicated(subset=["year", "quarter", "region", "tenant_id"])
        dup_count = duplicates.sum()
        if dup_count > 0:
            result.add_warning(f"{dup_count} duplicate records detected")

    # Data quality score validation
    if "data_quality_score" in data.columns:
        low_quality = data[data["data_quality_score"] < 50]
        if len(low_quality) > 0:
            result.add_warning(f"{len(low_quality)} records have low data quality score (<50)")

    if strict and not result.is_valid:
        raise ValidationError(f"Validation failed: {'; '.join(result.errors)}")

    return result


def validate_filter_params(
    params: FilterParams,
    strict: bool = False,
) -> ValidationResult:
    """
    Validate filter parameters.

    Args:
        params: FilterParams object to validate
        strict: If True, raise exceptions on errors

    Returns:
        ValidationResult with errors and warnings
    """
    result = ValidationResult()

    # Validate tenant_id
    if not params.tenant_id or not params.tenant_id.strip():
        result.add_error("tenant_id is required")

    # Validate year
    if params.year is not None:
        if not isinstance(params.year, int):
            result.add_error("year must be an integer")
        elif not 2000 <= params.year <= 2100:
            result.add_error(f"year {params.year} is out of valid range (2000-2100)")

    # Validate quarter
    if params.quarter is not None:
        if not isinstance(params.quarter, int):
            result.add_error("quarter must be an integer")
        elif params.quarter not in [1, 2, 3, 4]:
            result.add_error(f"quarter {params.quarter} must be 1, 2, 3, or 4")

    # Validate region
    if params.region is not None and params.region not in REGIONS:
        result.add_warning(f"region '{params.region}' is not in the standard regions list")

    # Validate date range
    if params.start_date and params.end_date and params.start_date > params.end_date:
        result.add_error("start_date cannot be after end_date")

    # Validate limit
    if params.limit is not None:
        if not isinstance(params.limit, int) or params.limit < 1:
            result.add_error("limit must be a positive integer")
        elif params.limit > 10000:
            result.add_warning("limit exceeds 10,000 - may impact performance")

    # Validate offset
    if params.offset is not None and (not isinstance(params.offset, int) or params.offset < 0):
        result.add_error("offset must be a non-negative integer")

    if strict and not result.is_valid:
        raise ValidationError(f"Filter validation failed: {'; '.join(result.errors)}")

    return result


def validate_kpi_value(
    kpi_id: str,
    value: Any,
    thresholds: dict[str, Any] | None = None,
) -> ValidationResult:
    """
    Validate a single KPI value.

    Args:
        kpi_id: KPI identifier
        value: Value to validate
        thresholds: Optional threshold definitions

    Returns:
        ValidationResult with status
    """
    result = ValidationResult()

    # Check if value is numeric
    if value is None:
        result.add_warning(f"{kpi_id}: value is null")
        return result

    if not isinstance(value, (int, float)):
        result.add_error(f"{kpi_id}: value must be numeric, got {type(value).__name__}")
        return result

    # Check for infinity/NaN
    if pd.isna(value):
        result.add_error(f"{kpi_id}: value is NaN")
        return result

    if isinstance(value, float) and (value == float("inf") or value == float("-inf")):
        result.add_error(f"{kpi_id}: value is infinite")
        return result

    # Threshold validation
    if thresholds:
        if "min" in thresholds and value < thresholds["min"]:
            result.add_warning(f"{kpi_id}: value {value} below minimum {thresholds['min']}")

        if "max" in thresholds and value > thresholds["max"]:
            result.add_warning(f"{kpi_id}: value {value} above maximum {thresholds['max']}")

    return result


def validate_export_request(
    format_type: str,
    row_count: int,
    max_rows: int = 100000,
) -> ValidationResult:
    """
    Validate an export request.

    Args:
        format_type: Export format (pdf, pptx, xlsx)
        row_count: Number of rows to export
        max_rows: Maximum allowed rows

    Returns:
        ValidationResult
    """
    result = ValidationResult()

    valid_formats = ["pdf", "pptx", "xlsx", "csv"]
    if format_type.lower() not in valid_formats:
        result.add_error(f"Invalid format: {format_type}. Must be one of {valid_formats}")

    if row_count > max_rows:
        result.add_error(f"Row count {row_count} exceeds maximum {max_rows}")

    if row_count > 50000:
        result.add_warning("Large export may take significant time")

    return result


def sanitize_string(
    value: str,
    max_length: int = 500,
    allow_html: bool = False,
) -> str:
    """
    Sanitize string input.

    Args:
        value: String to sanitize
        max_length: Maximum allowed length
        allow_html: Whether to allow HTML tags

    Returns:
        Sanitized string
    """
    if not isinstance(value, str):
        value = str(value)

    # Truncate
    value = value[:max_length]

    # Remove HTML if not allowed
    if not allow_html:
        import re

        value = re.sub(r"<[^>]+>", "", value)

    # Remove potentially dangerous characters
    value = value.replace("\x00", "")

    return value.strip()
