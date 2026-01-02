"""
Analytics Hub Platform - Domain Module
Sustainable Economic Development Analytics Hub
Ministry of Economy and Planning

This module contains domain models, business logic, and services.
"""

from analytics_hub_platform.domain.indicators import (
    calculate_sustainability_index,
    co2_per_capita,
    co2_per_gdp,
    energy_intensity,
    get_kpi_status,
    normalize_to_100,
)
from analytics_hub_platform.domain.llm_service import (
    generate_recommendations,
    get_llm_service,
)
from analytics_hub_platform.domain.ml_services import (
    AnomalyDetector,
    AnomalySeverity,
    KPIForecaster,
    detect_kpi_anomalies,
    forecast_kpi,
)
from analytics_hub_platform.domain.models import (
    FilterParams,
    IndicatorRecord,
    KPIDefinition,
    KPIStatus,
    KPIThresholds,
    Tenant,
    User,
    UserRole,
)
from analytics_hub_platform.domain.services import (
    get_executive_snapshot,
    get_kpi_timeseries,
    get_regional_comparison,
    get_sustainability_summary,
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
    # ML Services
    "KPIForecaster",
    "AnomalyDetector",
    "AnomalySeverity",
    "forecast_kpi",
    "detect_kpi_anomalies",
    # LLM Services
    "generate_recommendations",
    "get_llm_service",
]
