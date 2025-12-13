"""
Excel/CSV Importer
Sustainable Economic Development Analytics Hub
Ministry of Economy and Planning

Canonical implementation for loading and validating indicator data
from Excel or CSV files.
"""

from typing import List, Optional, Union, BinaryIO
from pathlib import Path
import pandas as pd
from io import BytesIO


class ExcelCSVImporter:
    """
    Excel and CSV importer for indicator data.
    
    Features:
    - Load .xlsx or .csv files from path or file-like objects
    - Validate required columns
    - Clean and normalize data
    - Return DataFrame ready for repository layer
    
    Usage:
        # From file path
        importer = ExcelCSVImporter()
        df = importer.load_file("data/indicators.xlsx")
        
        # From Streamlit file uploader
        df = importer.load_file(uploaded_file)
        
        # Validate columns
        missing = importer.validate_columns(df, ["kpi_id", "year", "quarter"])
        if missing:
            raise ValueError(f"Missing columns: {missing}")
    """

    # Standard indicator schema
    REQUIRED_COLUMNS = [
        "tenant_id",
        "kpi_id", 
        "year",
        "quarter",
        "region",
        "value"
    ]
    
    OPTIONAL_COLUMNS = [
        "unit",
        "target_value",
        "data_quality_score",
        "source",
        "notes"
    ]

    def __init__(self) -> None:
        """Initialize the importer."""
        pass

    def load_file(
        self,
        file_path_or_buffer: Union[str, Path, BinaryIO],
        sheet_name: Optional[str] = None,
        validate: bool = True
    ) -> pd.DataFrame:
        """
        Load Excel or CSV file and return DataFrame.
        
        Args:
            file_path_or_buffer: File path string, Path object, or file-like buffer
            sheet_name: Excel sheet name (None = first sheet)
            validate: Whether to validate required columns
            
        Returns:
            DataFrame with indicator data
            
        Raises:
            ValueError: If file format unsupported or validation fails
            FileNotFoundError: If file path doesn't exist
        """
        # Determine file type
        if isinstance(file_path_or_buffer, (str, Path)):
            file_path = Path(file_path_or_buffer)
            
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            # Load based on extension
            if file_path.suffix.lower() in [".xlsx", ".xls"]:
                df = pd.read_excel(file_path, sheet_name=sheet_name or 0)
            elif file_path.suffix.lower() == ".csv":
                df = pd.read_csv(file_path)
            else:
                raise ValueError(
                    f"Unsupported file format: {file_path.suffix}. "
                    "Use .xlsx, .xls, or .csv"
                )
        else:
            # File-like object (e.g., from Streamlit uploader)
            # Try to detect format from name attribute if available
            file_name = getattr(file_path_or_buffer, "name", "")
            
            if file_name.endswith(".csv"):
                df = pd.read_csv(file_path_or_buffer)
            else:
                # Default to Excel for file uploads
                df = pd.read_excel(file_path_or_buffer, sheet_name=sheet_name or 0)
        
        # Clean column names (strip whitespace, lowercase)
        df.columns = df.columns.str.strip().str.lower()
        
        # Validate if requested
        if validate:
            missing = self.validate_columns(df, self.REQUIRED_COLUMNS)
            if missing:
                raise ValueError(
                    f"Missing required columns: {', '.join(missing)}. "
                    f"Expected columns: {', '.join(self.REQUIRED_COLUMNS)}"
                )
        
        # Clean and normalize data
        df = self._clean_dataframe(df)
        
        return df
    
    def validate_columns(
        self,
        df: pd.DataFrame,
        required_columns: Optional[List[str]] = None
    ) -> List[str]:
        """
        Validate that DataFrame contains required columns.
        
        Args:
            df: DataFrame to validate
            required_columns: List of required column names (uses default if None)
            
        Returns:
            List of missing column names (empty if all present)
        """
        required = required_columns or self.REQUIRED_COLUMNS
        
        # Normalize column names for comparison
        df_cols = set(df.columns.str.strip().str.lower())
        required_cols = set(col.strip().lower() for col in required)
        
        missing = [col for col in required_cols if col not in df_cols]
        return missing
    
    def _clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and normalize DataFrame.
        
        Args:
            df: Raw DataFrame
            
        Returns:
            Cleaned DataFrame
        """
        df = df.copy()
        
        # Remove rows with missing required values
        for col in self.REQUIRED_COLUMNS:
            if col in df.columns:
                df = df[df[col].notna()]
        
        # Convert numeric columns
        if "year" in df.columns:
            df["year"] = pd.to_numeric(df["year"], errors="coerce")
        if "quarter" in df.columns:
            df["quarter"] = pd.to_numeric(df["quarter"], errors="coerce")
        if "value" in df.columns:
            df["value"] = pd.to_numeric(df["value"], errors="coerce")
        if "target_value" in df.columns:
            df["target_value"] = pd.to_numeric(df["target_value"], errors="coerce")
        
        # Strip whitespace from string columns
        str_cols = ["tenant_id", "kpi_id", "region", "unit", "source"]
        for col in str_cols:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip()
        
        # Remove any completely empty rows
        df = df.dropna(how="all")
        
        # Sort by year, quarter for consistent ordering
        if "year" in df.columns and "quarter" in df.columns:
            df = df.sort_values(["year", "quarter"])
        
        # Reset index
        df = df.reset_index(drop=True)
        
        return df
    
    def get_sample_template(self) -> pd.DataFrame:
        """
        Get a sample template DataFrame with required columns.
        
        Returns:
            Empty DataFrame with required columns
        """
        return pd.DataFrame(columns=self.REQUIRED_COLUMNS + self.OPTIONAL_COLUMNS)


__all__ = ["ExcelCSVImporter"]
