"""
Constants Module
Sustainable Economic Development Analytics Hub
Ministry of Economy and Planning

Centralized constants and configuration values used across the platform.
This module provides a single source of truth for commonly used values.
"""

from typing import Dict, List, Tuple, Final
from enum import Enum, auto


# ============================================
# SAUDI ARABIA REGIONS
# ============================================

SAUDI_REGIONS: Final[List[str]] = [
    "Riyadh",
    "Makkah",
    "Madinah",
    "Eastern Province",
    "Qassim",
    "Asir",
    "Tabuk",
    "Hail",
    "Northern Borders",
    "Jazan",
    "Najran",
    "Al Bahah",
    "Al Jawf",
]

# Regional characteristics for data generation
REGION_PROFILES: Final[Dict[str, Dict]] = {
    "Riyadh": {"gdp_base": 800000, "population": 8.7, "urban": True},
    "Makkah": {"gdp_base": 450000, "population": 9.0, "urban": True},
    "Madinah": {"gdp_base": 150000, "population": 2.2, "urban": True},
    "Eastern Province": {"gdp_base": 650000, "population": 5.0, "urban": True},
    "Qassim": {"gdp_base": 80000, "population": 1.5, "urban": False},
    "Asir": {"gdp_base": 75000, "population": 2.3, "urban": False},
    "Tabuk": {"gdp_base": 55000, "population": 0.95, "urban": False},
    "Hail": {"gdp_base": 45000, "population": 0.75, "urban": False},
    "Northern Borders": {"gdp_base": 35000, "population": 0.4, "urban": False},
    "Jazan": {"gdp_base": 45000, "population": 1.7, "urban": False},
    "Najran": {"gdp_base": 30000, "population": 0.6, "urban": False},
    "Al Bahah": {"gdp_base": 25000, "population": 0.5, "urban": False},
    "Al Jawf": {"gdp_base": 28000, "population": 0.55, "urban": False},
}


# ============================================
# TIME CONSTANTS
# ============================================

class Quarter(int, Enum):
    """Quarter enumeration."""
    Q1 = 1
    Q2 = 2
    Q3 = 3
    Q4 = 4


QUARTERS: Final[Tuple[int, ...]] = (1, 2, 3, 4)
MIN_YEAR: Final[int] = 2019
MAX_YEAR: Final[int] = 2030
DEFAULT_YEAR: Final[int] = 2024
DEFAULT_QUARTER: Final[int] = 4


# ============================================
# KPI THRESHOLDS
# ============================================

# Sustainability Index thresholds
SUSTAINABILITY_INDEX_GREEN: Final[float] = 70.0
SUSTAINABILITY_INDEX_AMBER: Final[float] = 50.0

# CO2 thresholds (kg CO2 per SAR GDP)
CO2_PER_GDP_GREEN: Final[float] = 0.35
CO2_PER_GDP_AMBER: Final[float] = 0.50

# Renewable energy thresholds (percentage)
RENEWABLE_ENERGY_GREEN: Final[float] = 15.0
RENEWABLE_ENERGY_AMBER: Final[float] = 8.0

# Green investment thresholds (percentage)
GREEN_INVESTMENT_GREEN: Final[float] = 8.0
GREEN_INVESTMENT_AMBER: Final[float] = 4.0

# Data quality thresholds
DATA_QUALITY_GREEN: Final[float] = 80.0
DATA_QUALITY_AMBER: Final[float] = 60.0


def get_kpi_status(value: float, green_threshold: float, amber_threshold: float, higher_is_better: bool = True) -> str:
    """
    Determine KPI status based on thresholds.
    
    Args:
        value: Current KPI value
        green_threshold: Threshold for green status
        amber_threshold: Threshold for amber status
        higher_is_better: If True, values above green are good
    
    Returns:
        Status string: 'green', 'amber', or 'red'
    """
    if higher_is_better:
        if value >= green_threshold:
            return "green"
        elif value >= amber_threshold:
            return "amber"
        else:
            return "red"
    else:
        if value <= green_threshold:
            return "green"
        elif value <= amber_threshold:
            return "amber"
        else:
            return "red"


# ============================================
# ML CONSTANTS
# ============================================

# Minimum data points for ML operations
ML_MIN_FORECAST_POINTS: Final[int] = 4
ML_MIN_ANOMALY_POINTS: Final[int] = 4
ML_DEFAULT_FORECAST_QUARTERS: Final[int] = 4

# Z-score thresholds for anomaly detection
ANOMALY_ZSCORE_WARNING: Final[float] = 2.5
ANOMALY_ZSCORE_CRITICAL: Final[float] = 3.5

# Default rolling window for statistics
DEFAULT_ROLLING_WINDOW: Final[int] = 8


# ============================================
# API CONSTANTS
# ============================================

# Rate limiting defaults
DEFAULT_RATE_LIMIT: Final[int] = 60  # requests per minute
DEFAULT_RATE_WINDOW: Final[int] = 60  # seconds

# Pagination defaults
DEFAULT_PAGE_SIZE: Final[int] = 20
MAX_PAGE_SIZE: Final[int] = 100
MIN_PAGE_SIZE: Final[int] = 1

# Cache TTL defaults (seconds)
CACHE_TTL_SHORT: Final[int] = 60       # 1 minute
CACHE_TTL_MEDIUM: Final[int] = 300     # 5 minutes
CACHE_TTL_LONG: Final[int] = 3600      # 1 hour
CACHE_TTL_LLM: Final[int] = 3600       # 1 hour for LLM responses


# ============================================
# EXPORT CONSTANTS
# ============================================

EXPORT_FORMATS: Final[Tuple[str, ...]] = ("pdf", "excel", "pptx", "csv")
MAX_EXPORT_ROWS: Final[int] = 10000
DEFAULT_CHART_WIDTH: Final[int] = 800
DEFAULT_CHART_HEIGHT: Final[int] = 400


# ============================================
# UI CONSTANTS
# ============================================

# Chart colors (Vision 2030 aligned palette)
CHART_COLORS: Final[Dict[str, str]] = {
    "primary": "#1f77b4",
    "secondary": "#2ca02c",
    "accent": "#ff7f0e",
    "warning": "#d62728",
    "success": "#2ca02c",
    "info": "#17becf",
    "neutral": "#7f7f7f",
}

# Status colors
STATUS_COLORS: Final[Dict[str, str]] = {
    "green": "#2ca02c",
    "amber": "#ff7f0e",
    "red": "#d62728",
    "unknown": "#7f7f7f",
}

# Map colors for regional visualization
MAP_COLORS: Final[Dict[str, str]] = {
    "high": "#2ca02c",
    "medium": "#ffcc00",
    "low": "#d62728",
    "no_data": "#e0e0e0",
}


# ============================================
# VALIDATION CONSTANTS
# ============================================

# String length limits
MAX_TENANT_ID_LENGTH: Final[int] = 50
MIN_TENANT_ID_LENGTH: Final[int] = 2
MAX_EMAIL_LENGTH: Final[int] = 200
MAX_NAME_LENGTH: Final[int] = 200
MAX_DESCRIPTION_LENGTH: Final[int] = 2000

# Numeric ranges
PERCENTAGE_MIN: Final[float] = 0.0
PERCENTAGE_MAX: Final[float] = 100.0
YEAR_MIN: Final[int] = 1900
YEAR_MAX: Final[int] = 2100


# ============================================
# HELPER FUNCTIONS
# ============================================

def get_valid_regions() -> List[str]:
    """Get list of valid Saudi regions."""
    return list(SAUDI_REGIONS)


def is_valid_region(region: str) -> bool:
    """Check if region name is valid (case-insensitive)."""
    return region.lower() in [r.lower() for r in SAUDI_REGIONS]


def is_valid_quarter(quarter: int) -> bool:
    """Check if quarter value is valid."""
    return quarter in QUARTERS


def is_valid_year(year: int) -> bool:
    """Check if year is in valid range."""
    return YEAR_MIN <= year <= YEAR_MAX


__all__ = [
    # Regions
    "SAUDI_REGIONS",
    "REGION_PROFILES",
    "get_valid_regions",
    "is_valid_region",
    # Time
    "Quarter",
    "QUARTERS",
    "MIN_YEAR",
    "MAX_YEAR",
    "DEFAULT_YEAR",
    "DEFAULT_QUARTER",
    "is_valid_quarter",
    "is_valid_year",
    # KPI Thresholds
    "SUSTAINABILITY_INDEX_GREEN",
    "SUSTAINABILITY_INDEX_AMBER",
    "CO2_PER_GDP_GREEN",
    "CO2_PER_GDP_AMBER",
    "RENEWABLE_ENERGY_GREEN",
    "RENEWABLE_ENERGY_AMBER",
    "GREEN_INVESTMENT_GREEN",
    "GREEN_INVESTMENT_AMBER",
    "DATA_QUALITY_GREEN",
    "DATA_QUALITY_AMBER",
    "get_kpi_status",
    # ML
    "ML_MIN_FORECAST_POINTS",
    "ML_MIN_ANOMALY_POINTS",
    "ML_DEFAULT_FORECAST_QUARTERS",
    "ANOMALY_ZSCORE_WARNING",
    "ANOMALY_ZSCORE_CRITICAL",
    "DEFAULT_ROLLING_WINDOW",
    # API
    "DEFAULT_RATE_LIMIT",
    "DEFAULT_RATE_WINDOW",
    "DEFAULT_PAGE_SIZE",
    "MAX_PAGE_SIZE",
    "MIN_PAGE_SIZE",
    "CACHE_TTL_SHORT",
    "CACHE_TTL_MEDIUM",
    "CACHE_TTL_LONG",
    "CACHE_TTL_LLM",
    # Export
    "EXPORT_FORMATS",
    "MAX_EXPORT_ROWS",
    "DEFAULT_CHART_WIDTH",
    "DEFAULT_CHART_HEIGHT",
    # UI
    "CHART_COLORS",
    "STATUS_COLORS",
    "MAP_COLORS",
    # Validation
    "MAX_TENANT_ID_LENGTH",
    "MIN_TENANT_ID_LENGTH",
    "MAX_EMAIL_LENGTH",
    "MAX_NAME_LENGTH",
    "MAX_DESCRIPTION_LENGTH",
    "PERCENTAGE_MIN",
    "PERCENTAGE_MAX",
    "YEAR_MIN",
    "YEAR_MAX",
]
