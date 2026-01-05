"""
Tests for Data Ingestion Module
Sustainable Economic Development Analytics Hub

Tests:
- File parsing (CSV/Excel)
- Schema validation
- Data type validation
- Range validation
- Region validation
- Duplicate detection
- Template generation
"""

from pathlib import Path
import pytest
import pandas as pd
import io

# Import the modules under test
from analytics_hub_platform.infrastructure.data_ingestion import (
    parse_upload_file,
    validate_schema,
    validate_data_types,
    validate_ranges,
    validate_regions,
    validate_duplicates,
    validate_upload,
    generate_upload_template,
    REQUIRED_COLUMNS,
    INDICATOR_COLUMNS,
    FIELD_RANGES,
    VALID_REGIONS,
)


# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def sample_good_csv() -> bytes:
    """Load good sample CSV from fixtures."""
    fixture_path = Path(__file__).parent / "fixtures" / "sample_good.csv"
    return fixture_path.read_bytes()


@pytest.fixture
def sample_bad_csv() -> bytes:
    """Load bad sample CSV from fixtures."""
    fixture_path = Path(__file__).parent / "fixtures" / "sample_bad.csv"
    return fixture_path.read_bytes()


@pytest.fixture
def sample_missing_columns_csv() -> bytes:
    """Load CSV with missing required columns."""
    fixture_path = Path(__file__).parent / "fixtures" / "sample_missing_columns.csv"
    return fixture_path.read_bytes()


@pytest.fixture
def good_dataframe() -> pd.DataFrame:
    """Create a valid DataFrame for testing."""
    return pd.DataFrame({
        "tenant_id": ["ministry_economy", "ministry_economy"],
        "year": [2024, 2024],
        "quarter": [1, 2],
        "region": ["Riyadh", "Makkah"],
        "gdp_growth": [3.5, 2.8],
        "gdp_total": [850.5, 420.0],
        "foreign_investment": [45.2, 22.1],
        "unemployment_rate": [11.2, 12.5],
        "renewable_share": [12.5, 10.0],
    })


@pytest.fixture
def bad_dataframe() -> pd.DataFrame:
    """Create an invalid DataFrame for testing."""
    return pd.DataFrame({
        "tenant_id": ["ministry_economy", "ministry_economy", ""],
        "year": [2024, 2024, 2024],
        "quarter": [1, 5, 2],  # Invalid quarter 5
        "region": ["Riyadh", "InvalidRegion", "Makkah"],  # Invalid region
        "gdp_growth": [50.0, 2.8, -25.0],  # Out of range values
        "unemployment_rate": [11.2, 60.0, 12.5],  # Out of range
    })


# =============================================================================
# FILE PARSING TESTS
# =============================================================================


class TestFileParsing:
    """Tests for file parsing functionality."""

    def test_parse_csv_success(self, sample_good_csv):
        """Test parsing valid CSV file."""
        df, error = parse_upload_file(sample_good_csv, "test.csv")
        
        assert df is not None
        assert error == ""
        assert len(df) == 8
        assert "tenant_id" in df.columns
        assert "gdp_growth" in df.columns

    def test_parse_csv_bad_data(self, sample_bad_csv):
        """Test parsing CSV with problematic data (should still parse)."""
        df, error = parse_upload_file(sample_bad_csv, "test.csv")
        
        assert df is not None
        assert error == ""
        assert len(df) > 0

    def test_parse_unsupported_format(self):
        """Test parsing unsupported file format."""
        df, error = parse_upload_file(b"test data", "test.txt")
        
        assert df is None
        assert "Unsupported file type" in error

    def test_parse_invalid_csv(self):
        """Test parsing invalid CSV content."""
        invalid_csv = b"\x00\x01\x02\x03"  # Binary garbage
        df, error = parse_upload_file(invalid_csv, "test.csv")
        
        # Pandas may parse this as empty or fail
        # Either outcome is acceptable
        assert df is None or len(df) == 0 or error != ""


# =============================================================================
# SCHEMA VALIDATION TESTS
# =============================================================================


class TestSchemaValidation:
    """Tests for schema validation."""

    def test_valid_schema(self, good_dataframe):
        """Test validation of complete schema."""
        result = validate_schema(good_dataframe)
        
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_missing_required_columns(self, sample_missing_columns_csv):
        """Test detection of missing required columns."""
        df, _ = parse_upload_file(sample_missing_columns_csv, "test.csv")
        result = validate_schema(df)
        
        assert result.is_valid is False
        assert len(result.errors) > 0
        assert any("Missing required columns" in e for e in result.errors)

    def test_missing_indicator_columns(self):
        """Test warning when indicator columns are missing."""
        df = pd.DataFrame({
            "tenant_id": ["test"],
            "year": [2024],
            "quarter": [1],
            "region": ["Riyadh"],
        })
        result = validate_schema(df)
        
        # Should fail because no indicators
        assert result.is_valid is False or len(result.warnings) > 0


# =============================================================================
# DATA TYPE VALIDATION TESTS
# =============================================================================


class TestDataTypeValidation:
    """Tests for data type validation."""

    def test_valid_types(self, good_dataframe):
        """Test validation of correct data types."""
        result = validate_data_types(good_dataframe)
        
        # Should pass without errors
        assert result.is_valid is True

    def test_non_numeric_in_integer_column(self):
        """Test detection of non-numeric values in integer columns."""
        df = pd.DataFrame({
            "tenant_id": ["test"],
            "year": ["abc"],  # Non-numeric
            "quarter": [1],
            "region": ["Riyadh"],
        })
        result = validate_data_types(df)
        
        # Should have warnings about conversion
        assert len(result.warnings) > 0 or not result.is_valid


# =============================================================================
# RANGE VALIDATION TESTS
# =============================================================================


class TestRangeValidation:
    """Tests for value range validation."""

    def test_valid_ranges(self, good_dataframe):
        """Test validation with all values in range."""
        result = validate_ranges(good_dataframe)
        
        assert result.valid_row_count == len(good_dataframe)
        assert len(result.warnings) == 0

    def test_out_of_range_values(self, bad_dataframe):
        """Test detection of out-of-range values."""
        result = validate_ranges(bad_dataframe)
        
        assert len(result.warnings) > 0
        assert result.valid_row_count < len(bad_dataframe)

    def test_gdp_growth_range(self):
        """Test specific GDP growth range validation."""
        df = pd.DataFrame({
            "tenant_id": ["test", "test"],
            "year": [2024, 2024],
            "quarter": [1, 2],
            "region": ["Riyadh", "Riyadh"],
            "gdp_growth": [-25.0, 35.0],  # Both out of range [-20, 30]
        })
        result = validate_ranges(df)
        
        assert len(result.warnings) > 0
        assert "gdp_growth" in str(result.warnings)


# =============================================================================
# REGION VALIDATION TESTS
# =============================================================================


class TestRegionValidation:
    """Tests for region validation."""

    def test_valid_regions(self, good_dataframe):
        """Test validation with valid regions."""
        result = validate_regions(good_dataframe)
        
        assert len(result.warnings) == 0

    def test_invalid_region(self, bad_dataframe):
        """Test detection of invalid regions."""
        result = validate_regions(bad_dataframe)
        
        assert len(result.warnings) > 0
        assert "InvalidRegion" in str(result.warnings)

    def test_arabic_region_names(self):
        """Test acceptance of Arabic region names."""
        df = pd.DataFrame({
            "tenant_id": ["test"],
            "year": [2024],
            "quarter": [1],
            "region": ["الرياض"],  # Riyadh in Arabic
            "gdp_growth": [3.5],
        })
        result = validate_regions(df)
        
        assert len(result.warnings) == 0


# =============================================================================
# DUPLICATE DETECTION TESTS
# =============================================================================


class TestDuplicateDetection:
    """Tests for duplicate detection."""

    def test_no_duplicates(self, good_dataframe):
        """Test with no duplicates."""
        result = validate_duplicates(good_dataframe)
        
        assert len(result.warnings) == 0
        assert len(result.invalid_row_indices) == 0

    def test_duplicate_detection(self):
        """Test detection of duplicate rows."""
        df = pd.DataFrame({
            "tenant_id": ["test", "test"],
            "year": [2024, 2024],
            "quarter": [1, 1],
            "region": ["Riyadh", "Riyadh"],  # Same key
            "gdp_growth": [3.5, 4.0],
        })
        result = validate_duplicates(df)
        
        assert len(result.warnings) > 0
        assert "duplicate" in str(result.warnings).lower()


# =============================================================================
# COMBINED VALIDATION TESTS
# =============================================================================


class TestCombinedValidation:
    """Tests for combined validation pipeline."""

    def test_validate_good_data(self, sample_good_csv):
        """Test full validation of good data."""
        df, _ = parse_upload_file(sample_good_csv, "test.csv")
        result = validate_upload(df)
        
        assert result.is_valid is True
        assert len(result.errors) == 0
        assert result.valid_row_count == len(df)

    def test_validate_bad_data(self, sample_bad_csv):
        """Test full validation of bad data detects issues."""
        df, _ = parse_upload_file(sample_bad_csv, "test.csv")
        result = validate_upload(df)
        
        # Should have warnings (may or may not be fatal errors)
        assert len(result.warnings) > 0 or len(result.errors) > 0


# =============================================================================
# TEMPLATE GENERATION TESTS
# =============================================================================


class TestTemplateGeneration:
    """Tests for template generation."""

    def test_generate_template(self):
        """Test template generation."""
        template = generate_upload_template()
        
        assert template is not None
        assert len(template) == 1  # One sample row
        
        # Check required columns present
        for col in REQUIRED_COLUMNS:
            assert col in template.columns
        
        # Check some indicator columns present
        assert "gdp_growth" in template.columns
        assert "unemployment_rate" in template.columns

    def test_template_sample_values_in_range(self):
        """Test that template sample values are within valid ranges."""
        template = generate_upload_template()
        
        for col, (min_val, max_val) in FIELD_RANGES.items():
            if col in template.columns:
                value = template[col].iloc[0]
                assert min_val <= value <= max_val, f"{col}={value} not in [{min_val}, {max_val}]"


# =============================================================================
# CONSTANTS TESTS
# =============================================================================


class TestConstants:
    """Tests for module constants."""

    def test_required_columns_defined(self):
        """Test that required columns are defined."""
        assert len(REQUIRED_COLUMNS) >= 4
        assert "tenant_id" in REQUIRED_COLUMNS
        assert "year" in REQUIRED_COLUMNS
        assert "quarter" in REQUIRED_COLUMNS
        assert "region" in REQUIRED_COLUMNS

    def test_indicator_columns_defined(self):
        """Test that indicator columns are defined."""
        assert len(INDICATOR_COLUMNS) >= 10
        assert "gdp_growth" in INDICATOR_COLUMNS
        assert "unemployment_rate" in INDICATOR_COLUMNS
        assert "renewable_share" in INDICATOR_COLUMNS

    def test_valid_regions_defined(self):
        """Test that valid regions include Saudi regions."""
        assert "Riyadh" in VALID_REGIONS
        assert "Makkah" in VALID_REGIONS
        assert "Eastern" in VALID_REGIONS
        # Check Arabic names
        assert "الرياض" in VALID_REGIONS

    def test_field_ranges_defined(self):
        """Test that field ranges are defined."""
        assert "gdp_growth" in FIELD_RANGES
        assert FIELD_RANGES["gdp_growth"] == (-20.0, 30.0)
        assert "unemployment_rate" in FIELD_RANGES
        assert FIELD_RANGES["unemployment_rate"] == (0, 50)
