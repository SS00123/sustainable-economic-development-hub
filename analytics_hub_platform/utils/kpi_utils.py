"""
KPI Utility Functions
Sustainable Economic Development Analytics Hub
Ministry of Economy and Planning

Shared utilities for KPI display formatting.
"""

from typing import Dict


# KPI unit mappings
KPI_UNITS: Dict[str, str] = {
    "gdp_growth": "%",
    "gdp_total": "M SAR",
    "foreign_investment": "M SAR",
    "export_diversity_index": "",
    "economic_complexity": "",
    "unemployment_rate": "%",
    "green_jobs": "K",
    "skills_gap_index": "",
    "social_progress_score": "",
    "digital_readiness": "",
    "innovation_index": "",
    "co2_index": "",
    "co2_total": "MT",
    "renewable_share": "%",
    "energy_intensity": "MJ/SAR",
    "water_efficiency": "",
    "waste_recycling_rate": "%",
    "forest_coverage": "%",
    "air_quality_index": "AQI",
    "co2_per_gdp": "t/M SAR",
    "co2_per_capita": "t/cap",
    "data_quality_score": "",
    "sustainability_index": "",
}

# KPIs whose base value is a percentage (delta should show "pp" for percentage points)
PERCENTAGE_KPIS = {
    "gdp_growth",
    "unemployment_rate",
    "renewable_share",
    "waste_recycling_rate",
    "forest_coverage",
}


def get_kpi_unit(kpi_id: str) -> str:
    """
    Get display unit for a KPI.
    
    Args:
        kpi_id: The KPI identifier
        
    Returns:
        Unit string (e.g., "%", "M SAR", "K")
    """
    return KPI_UNITS.get(kpi_id, "")


def get_delta_suffix(kpi_id: str) -> str:
    """
    Get delta suffix for a KPI.
    
    For KPIs whose main value is already a percentage, 
    the change is in percentage points (pp).
    For others, the change is a percentage (%).
    
    Args:
        kpi_id: The KPI identifier
        
    Returns:
        Delta suffix string (" pp" or "%")
    """
    return " pp" if kpi_id in PERCENTAGE_KPIS else "%"


def format_kpi_value(value: float, kpi_id: str, decimals: int = 2) -> str:
    """
    Format a KPI value with its unit.
    
    Args:
        value: The numeric value
        kpi_id: The KPI identifier
        decimals: Number of decimal places
        
    Returns:
        Formatted string with unit
    """
    unit = get_kpi_unit(kpi_id)
    formatted = f"{value:,.{decimals}f}"
    return f"{formatted}{unit}" if unit else formatted


def format_delta(delta: float, kpi_id: str, show_sign: bool = True) -> str:
    """
    Format a delta/change value with appropriate suffix.
    
    Args:
        delta: The change value
        kpi_id: The KPI identifier
        show_sign: Whether to show + sign for positive values
        
    Returns:
        Formatted delta string (e.g., "+2.5%", "-1.3 pp")
    """
    suffix = get_delta_suffix(kpi_id)
    if show_sign and delta > 0:
        return f"+{delta:.1f}{suffix}"
    return f"{delta:.1f}{suffix}"
