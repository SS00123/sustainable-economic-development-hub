"""
Analytics Hub Platform - Domain Module
Sustainable Economic Development Analytics Hub
Ministry of Economy and Planning

This module contains domain models, business logic, and services.
"""

from analytics_hub_platform.domain.models import (
    Tenant,
    User,
    UserRole,
    IndicatorRecord,
    KPIDefinition,
    KPIThresholds,
    KPIStatus,
    FilterParams,
)
from analytics_hub_platform.domain.indicators import (
    co2_per_gdp,
    co2_per_capita,
    energy_intensity,
    normalize_to_100,
    calculate_sustainability_index,
    get_kpi_status,
)
from analytics_hub_platform.domain.services import (
    get_sustainability_summary,
    get_executive_snapshot,
    get_kpi_timeseries,
    get_regional_comparison,
)

__all__ = [
    # Models
    "Tenant",
    "User",
    "UserRole",
    "IndicatorRecord",
    "KPIDefinition",
    "KPIThresholds",
    "KPIStatus",
    "FilterParams",
    # Indicators
    "co2_per_gdp",
    "co2_per_capita",
    "energy_intensity",
    "normalize_to_100",
    "calculate_sustainability_index",
    "get_kpi_status",
    # Services
    "get_sustainability_summary",
    "get_executive_snapshot",
    "get_kpi_timeseries",
    "get_regional_comparison",
]
