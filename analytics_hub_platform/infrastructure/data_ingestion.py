"""
Data Ingestion Module
Sustainable Economic Development Analytics Hub

Provides functionality for:
- Excel/CSV file upload and validation
- Schema validation against data contract
- Data quality checks
- SQLite insertion with batch tracking
"""

import hashlib
import io
import uuid
from datetime import datetime, timezone
from typing import Any

import pandas as pd
from pydantic import BaseModel, Field, field_validator

from analytics_hub_platform.infrastructure.db_init import (
    get_engine,
    sustainability_indicators,
)
from analytics_hub_platform.infrastructure.prod_logging import get_correlated_logger

logger = get_correlated_logger("analytics_hub.ingestion")


# =============================================================================
# DATA CONTRACT DEFINITIONS
# =============================================================================

# Required columns for upload
REQUIRED_COLUMNS = [
    "tenant_id",
    "year",
    "quarter",
    "region",
]

# Numeric indicator columns
INDICATOR_COLUMNS = [
    "gdp_growth",
    "gdp_total",
    "foreign_investment",
    "export_diversity_index",
    "economic_complexity",
    "unemployment_rate",
    "green_jobs",
    "skills_gap_index",
    "social_progress_score",
    "digital_readiness",
    "innovation_index",
    "population",
    "co2_index",
    "co2_total",
    "renewable_share",
    "energy_intensity",
    "water_efficiency",
    "waste_recycling_rate",
    "forest_coverage",
    "air_quality_index",
]

# Valid ranges for each field (min, max)
FIELD_RANGES: dict[str, tuple[float, float]] = {
    "year": (2020, 2030),
    "quarter": (1, 4),
    "gdp_growth": (-20.0, 30.0),
    "gdp_total": (0, 5000),
    "foreign_investment": (0, 500),
    "export_diversity_index": (0, 100),
    "economic_complexity": (-5.0, 5.0),
    "unemployment_rate": (0, 50),
    "green_jobs": (0, 10000),
    "skills_gap_index": (0, 100),
    "social_progress_score": (0, 100),
    "digital_readiness": (0, 100),
    "innovation_index": (0, 100),
    "population": (0, 50),
    "co2_index": (0, 100),
    "co2_total": (0, 1000),
    "renewable_share": (0, 100),
    "energy_intensity": (0, 50),
    "water_efficiency": (0, 100),
    "waste_recycling_rate": (0, 100),
    "forest_coverage": (0, 100),
    "air_quality_index": (0, 500),
}

# Valid Saudi regions
VALID_REGIONS = [
    "Riyadh",
    "Makkah",
    "Madinah",
    "Qassim",
    "Eastern",
    "Asir",
    "Tabuk",
    "Hail",
    "Northern Borders",
    "Jazan",
    "Najran",
    "Bahah",
    "Jawf",
    # Arabic names as alternatives
    "الرياض",
    "مكة المكرمة",
    "المدينة المنورة",
    "القصيم",
    "الشرقية",
    "عسير",
    "تبوك",
    "حائل",
    "الحدود الشمالية",
    "جازان",
    "نجران",
    "الباحة",
    "الجوف",
]


# =============================================================================
# VALIDATION MODELS
# =============================================================================


class ValidationResult(BaseModel):
    """Result of a validation check."""

    is_valid: bool = True
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    row_count: int = 0
    valid_row_count: int = 0
    invalid_row_indices: list[int] = Field(default_factory=list)


class IngestionResult(BaseModel):
    """Result of a data ingestion operation."""

    success: bool = False
    batch_id: str = ""
    rows_inserted: int = 0
    rows_updated: int = 0
    rows_skipped: int = 0
    validation: ValidationResult = Field(default_factory=ValidationResult)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    message: str = ""


# =============================================================================
# FILE PARSING
# =============================================================================


def parse_upload_file(
    file_content: bytes | io.BytesIO,
    filename: str,
) -> tuple[pd.DataFrame | None, str]:
    """
    Parse uploaded file (Excel or CSV) into DataFrame.

    Args:
        file_content: File content as bytes or BytesIO
        filename: Original filename for type detection

    Returns:
        Tuple of (DataFrame or None, error message)
    """
    try:
        if isinstance(file_content, bytes):
            file_content = io.BytesIO(file_content)

        if filename.lower().endswith((".xlsx", ".xls")):
            df = pd.read_excel(file_content)
        elif filename.lower().endswith(".csv"):
            df = pd.read_csv(file_content)
        else:
            return None, f"Unsupported file type: {filename}"

        logger.info(f"Parsed file {filename}: {len(df)} rows, {len(df.columns)} columns")
        return df, ""

    except Exception as e:
        logger.error(f"Failed to parse file {filename}: {e}")
        return None, str(e)


# =============================================================================
# VALIDATION FUNCTIONS
# =============================================================================


def validate_schema(df: pd.DataFrame) -> ValidationResult:
    """
    Validate DataFrame schema against data contract.

    Args:
        df: DataFrame to validate

    Returns:
        ValidationResult with schema validation results
    """
    result = ValidationResult(row_count=len(df))

    # Check required columns
    missing_columns = set(REQUIRED_COLUMNS) - set(df.columns)
    if missing_columns:
        result.is_valid = False
        result.errors.append(f"Missing required columns: {missing_columns}")

    # Check for at least some indicator columns
    present_indicators = set(INDICATOR_COLUMNS) & set(df.columns)
    if len(present_indicators) == 0:
        result.is_valid = False
        result.errors.append("No indicator columns found in upload")
    elif len(present_indicators) < len(INDICATOR_COLUMNS):
        missing_indicators = set(INDICATOR_COLUMNS) - present_indicators
        result.warnings.append(f"Optional indicator columns missing: {missing_indicators}")

    return result


def validate_data_types(df: pd.DataFrame) -> ValidationResult:
    """
    Validate data types for each column.

    Args:
        df: DataFrame to validate

    Returns:
        ValidationResult with type validation results
    """
    result = ValidationResult(row_count=len(df))

    # year and quarter must be integers
    for col in ["year", "quarter"]:
        if col in df.columns:
            try:
                df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")
                null_count = df[col].isna().sum()
                if null_count > 0:
                    result.warnings.append(f"{col}: {null_count} values could not be converted to integer")
            except Exception as e:
                result.errors.append(f"Failed to convert {col} to integer: {e}")
                result.is_valid = False

    # Indicator columns must be numeric
    for col in INDICATOR_COLUMNS:
        if col in df.columns:
            try:
                df[col] = pd.to_numeric(df[col], errors="coerce")
            except Exception:
                result.warnings.append(f"{col}: contains non-numeric values")

    return result


def validate_ranges(df: pd.DataFrame) -> ValidationResult:
    """
    Validate values are within allowed ranges.

    Args:
        df: DataFrame to validate

    Returns:
        ValidationResult with range validation results
    """
    result = ValidationResult(row_count=len(df))
    result.valid_row_count = len(df)

    for col, (min_val, max_val) in FIELD_RANGES.items():
        if col not in df.columns:
            continue

        # Find out-of-range values
        out_of_range = df[(df[col] < min_val) | (df[col] > max_val)]

        if len(out_of_range) > 0:
            result.warnings.append(
                f"{col}: {len(out_of_range)} values outside range [{min_val}, {max_val}]"
            )
            result.invalid_row_indices.extend(out_of_range.index.tolist())

    # Deduplicate invalid indices
    result.invalid_row_indices = list(set(result.invalid_row_indices))
    result.valid_row_count = len(df) - len(result.invalid_row_indices)

    return result


def validate_regions(df: pd.DataFrame) -> ValidationResult:
    """
    Validate region values against allowed list.

    Args:
        df: DataFrame to validate

    Returns:
        ValidationResult with region validation results
    """
    result = ValidationResult(row_count=len(df))

    if "region" not in df.columns:
        return result

    unique_regions = df["region"].dropna().unique()
    invalid_regions = [r for r in unique_regions if r not in VALID_REGIONS]

    if invalid_regions:
        result.warnings.append(f"Unknown regions found: {invalid_regions}")

    return result


def validate_duplicates(df: pd.DataFrame) -> ValidationResult:
    """
    Check for duplicate rows based on primary key.

    Args:
        df: DataFrame to validate

    Returns:
        ValidationResult with duplicate check results
    """
    result = ValidationResult(row_count=len(df))

    key_cols = ["tenant_id", "year", "quarter", "region"]
    present_keys = [c for c in key_cols if c in df.columns]

    if len(present_keys) == len(key_cols):
        duplicates = df[df.duplicated(subset=key_cols, keep=False)]
        if len(duplicates) > 0:
            result.warnings.append(
                f"Found {len(duplicates)} duplicate rows based on (tenant_id, year, quarter, region)"
            )
            result.invalid_row_indices = duplicates.index.tolist()

    return result


def validate_upload(df: pd.DataFrame) -> ValidationResult:
    """
    Run all validation checks on uploaded data.

    Args:
        df: DataFrame to validate

    Returns:
        Combined ValidationResult
    """
    combined = ValidationResult(row_count=len(df))

    # Run all validations
    validations = [
        validate_schema(df),
        validate_data_types(df),
        validate_ranges(df),
        validate_regions(df),
        validate_duplicates(df),
    ]

    for v in validations:
        combined.errors.extend(v.errors)
        combined.warnings.extend(v.warnings)
        combined.invalid_row_indices.extend(v.invalid_row_indices)
        if not v.is_valid:
            combined.is_valid = False

    # Deduplicate
    combined.invalid_row_indices = list(set(combined.invalid_row_indices))
    combined.valid_row_count = len(df) - len(combined.invalid_row_indices)

    logger.info(
        f"Validation complete: {combined.valid_row_count}/{len(df)} valid rows, "
        f"{len(combined.errors)} errors, {len(combined.warnings)} warnings"
    )

    return combined


# =============================================================================
# DATA TRANSFORMATION
# =============================================================================


def prepare_for_insert(
    df: pd.DataFrame,
    tenant_id: str,
    batch_id: str,
    source_system: str = "manual_upload",
) -> pd.DataFrame:
    """
    Prepare DataFrame for database insertion.

    Args:
        df: Validated DataFrame
        tenant_id: Tenant identifier
        batch_id: Batch identifier for tracking
        source_system: Source system identifier

    Returns:
        DataFrame ready for insertion
    """
    df = df.copy()

    # Ensure tenant_id is set
    df["tenant_id"] = tenant_id

    # Add metadata columns
    df["load_timestamp"] = datetime.now(timezone.utc)
    df["load_batch_id"] = batch_id
    df["source_system"] = source_system

    # Calculate derived fields if base fields present
    if "co2_total" in df.columns and "gdp_total" in df.columns:
        df["co2_per_gdp"] = df["co2_total"] / df["gdp_total"].replace(0, pd.NA)

    if "co2_total" in df.columns and "population" in df.columns:
        df["co2_per_capita"] = df["co2_total"] / df["population"].replace(0, pd.NA)

    # Calculate sustainability index if not present
    if "sustainability_index" not in df.columns:
        df["sustainability_index"] = calculate_sustainability_index(df)

    # Keep only columns that exist in the table
    table_columns = [c.name for c in sustainability_indicators.columns]
    df = df[[c for c in df.columns if c in table_columns]]

    return df


def calculate_sustainability_index(df: pd.DataFrame) -> pd.Series:
    """
    Calculate composite sustainability index.

    Formula: 35% economic + 35% social + 30% environmental
    """
    index = pd.Series(50.0, index=df.index)  # Default value

    # Economic component (normalized GDP growth)
    if "gdp_growth" in df.columns:
        economic = (df["gdp_growth"] + 20) / 50 * 100  # Normalize -20 to 30 => 0 to 100
        economic = economic.clip(0, 100)
        index = index * 0.65 + economic * 0.35

    # Social component (inverse unemployment)
    if "unemployment_rate" in df.columns:
        social = 100 - df["unemployment_rate"] * 2  # Lower unemployment = higher score
        social = social.clip(0, 100)
        index = index * 0.65 + social * 0.35

    # Environmental component
    if "renewable_share" in df.columns:
        index = index * 0.70 + df["renewable_share"] * 0.30

    return index.round(2)


# =============================================================================
# DATABASE OPERATIONS
# =============================================================================


def insert_data(
    df: pd.DataFrame,
    replace_existing: bool = False,
) -> tuple[int, int, int]:
    """
    Insert data into the database.

    Args:
        df: Prepared DataFrame
        replace_existing: If True, replace existing records; if False, skip duplicates

    Returns:
        Tuple of (inserted, updated, skipped) counts
    """
    engine = get_engine()

    inserted = 0
    updated = 0
    skipped = 0

    with engine.begin() as conn:
        for _, row in df.iterrows():
            try:
                # Check if record exists
                from sqlalchemy import and_, select

                existing = conn.execute(
                    select(sustainability_indicators).where(
                        and_(
                            sustainability_indicators.c.tenant_id == row["tenant_id"],
                            sustainability_indicators.c.year == row["year"],
                            sustainability_indicators.c.quarter == row["quarter"],
                            sustainability_indicators.c.region == row["region"],
                        )
                    )
                ).fetchone()

                if existing:
                    if replace_existing:
                        # Update existing record
                        from sqlalchemy import update

                        conn.execute(
                            update(sustainability_indicators)
                            .where(sustainability_indicators.c.id == existing.id)
                            .values(**row.dropna().to_dict())
                        )
                        updated += 1
                    else:
                        skipped += 1
                else:
                    # Insert new record
                    conn.execute(
                        sustainability_indicators.insert().values(**row.dropna().to_dict())
                    )
                    inserted += 1

            except Exception as e:
                logger.error(f"Failed to insert row: {e}")
                skipped += 1

    logger.info(f"Database operation complete: {inserted} inserted, {updated} updated, {skipped} skipped")
    return inserted, updated, skipped


# =============================================================================
# MAIN INGESTION FUNCTION
# =============================================================================


def ingest_file(
    file_content: bytes | io.BytesIO,
    filename: str,
    tenant_id: str,
    source_system: str = "manual_upload",
    replace_existing: bool = False,
    validate_only: bool = False,
) -> IngestionResult:
    """
    Main entry point for data ingestion.

    Args:
        file_content: Uploaded file content
        filename: Original filename
        tenant_id: Tenant identifier
        source_system: Source system identifier
        replace_existing: If True, update existing records
        validate_only: If True, only validate without inserting

    Returns:
        IngestionResult with operation details
    """
    # Generate batch ID
    batch_id = f"batch_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"

    result = IngestionResult(batch_id=batch_id)

    # Step 1: Parse file
    df, parse_error = parse_upload_file(file_content, filename)
    if df is None:
        result.message = f"Failed to parse file: {parse_error}"
        result.validation.errors.append(parse_error)
        return result

    # Step 2: Validate
    result.validation = validate_upload(df)

    if not result.validation.is_valid:
        result.message = "Validation failed with errors"
        return result

    if validate_only:
        result.success = True
        result.message = "Validation passed (dry run)"
        return result

    # Step 3: Prepare and insert
    try:
        prepared_df = prepare_for_insert(df, tenant_id, batch_id, source_system)
        inserted, updated, skipped = insert_data(prepared_df, replace_existing)

        result.rows_inserted = inserted
        result.rows_updated = updated
        result.rows_skipped = skipped
        result.success = True
        result.message = f"Successfully processed {inserted + updated} rows"

    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        result.message = f"Ingestion failed: {e}"

    return result


# =============================================================================
# TEMPLATE GENERATION
# =============================================================================


def generate_upload_template() -> pd.DataFrame:
    """
    Generate an empty template DataFrame for data upload.

    Returns:
        DataFrame with correct columns and sample data
    """
    columns = REQUIRED_COLUMNS + INDICATOR_COLUMNS + ["source_system", "data_quality_score"]

    # Create sample row
    sample_data = {
        "tenant_id": "ministry_economy",
        "year": 2026,
        "quarter": 1,
        "region": "Riyadh",
        "gdp_growth": 3.5,
        "gdp_total": 850.0,
        "foreign_investment": 25.0,
        "export_diversity_index": 65.0,
        "economic_complexity": 0.5,
        "unemployment_rate": 8.5,
        "green_jobs": 150.0,
        "skills_gap_index": 45.0,
        "social_progress_score": 72.0,
        "digital_readiness": 78.0,
        "innovation_index": 55.0,
        "population": 8.5,
        "co2_index": 68.0,
        "co2_total": 120.0,
        "renewable_share": 12.0,
        "energy_intensity": 8.5,
        "water_efficiency": 55.0,
        "waste_recycling_rate": 15.0,
        "forest_coverage": 0.5,
        "air_quality_index": 85.0,
        "source_system": "manual_upload",
        "data_quality_score": 95.0,
    }

    return pd.DataFrame([sample_data])


def export_template_excel(output_path: str | None = None) -> bytes | None:
    """
    Export upload template as Excel file.

    Args:
        output_path: If provided, save to file; otherwise return bytes

    Returns:
        Excel file bytes if no output_path, else None
    """
    template = generate_upload_template()

    if output_path:
        template.to_excel(output_path, index=False, sheet_name="Data")
        return None
    else:
        buffer = io.BytesIO()
        template.to_excel(buffer, index=False, sheet_name="Data")
        buffer.seek(0)
        return buffer.getvalue()
