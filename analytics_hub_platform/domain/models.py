"""
Domain Models
Sustainable Economic Development Analytics Hub
Ministry of Economy and Planning

This module defines the core domain models used throughout the platform.
Models are designed to be:
- Multi-tenant ready (tenant_id on all relevant entities)
- Type-safe with Pydantic validation
- Extensible for future requirements
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


def utc_now() -> datetime:
    """Return current UTC datetime (timezone-aware)."""
    return datetime.now(timezone.utc)


class UserRole(str, Enum):
    """
    User roles for role-based access control.

    Extension Point: Add new roles here as the platform expands.
    Future integration: These roles will map to SSO groups (e.g., Azure AD).
    """

    MINISTER = "minister"
    EXECUTIVE = "executive"
    DIRECTOR = "director"
    ANALYST = "analyst"
    ADMIN = "admin"
    VIEWER = "viewer"  # Read-only access


class KPIStatus(str, Enum):
    """Status classification for KPI values."""

    GREEN = "green"  # On track / good performance
    AMBER = "amber"  # At risk / needs attention
    RED = "red"  # Critical / action required
    UNKNOWN = "unknown"  # Cannot determine status


class Tenant(BaseModel):
    """
    Tenant model for multi-tenant support.

    In the current PoC, there is one tenant (Ministry of Economy and Planning).
    The architecture supports multiple tenants for future expansion to other
    ministries or government departments.
    """

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Unique tenant identifier")
    name: str = Field(..., description="Tenant display name")
    name_ar: str | None = Field(None, description="Arabic display name")
    country_code: str = Field(default="SA", description="ISO country code")
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)

    # Configuration overrides for this tenant
    config_overrides: dict[str, Any] | None = Field(default=None)


class User(BaseModel):
    """
    User model for authentication and authorization.

    Extension Point: Add SSO-related fields when integrating with identity provider.
    Future fields: sso_id, last_login, mfa_enabled, etc.
    """

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Unique user identifier")
    tenant_id: str = Field(..., description="Tenant this user belongs to")
    email: str = Field(..., description="User email address")
    name: str = Field(..., description="User display name")
    name_ar: str | None = Field(None, description="Arabic display name")
    role: UserRole = Field(default=UserRole.VIEWER)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)

    # Preferences
    preferred_language: str = Field(default="en")

    def can_export(self) -> bool:
        """Check if user has export permissions."""
        return self.role in [
            UserRole.MINISTER,
            UserRole.EXECUTIVE,
            UserRole.DIRECTOR,
            UserRole.ANALYST,
            UserRole.ADMIN,
        ]

    def can_edit_config(self) -> bool:
        """Check if user can edit platform configuration."""
        return self.role == UserRole.ADMIN

    def get_default_view(self) -> str:
        """Get the default view for this user's role."""
        view_map = {
            UserRole.MINISTER: "executive",
            UserRole.EXECUTIVE: "executive",
            UserRole.DIRECTOR: "director",
            UserRole.ANALYST: "analyst",
            UserRole.ADMIN: "admin",
            UserRole.VIEWER: "executive",
        }
        return view_map.get(self.role, "executive")


class KPIThresholds(BaseModel):
    """Threshold configuration for a single KPI."""

    green_min: float
    green_max: float
    amber_min: float
    amber_max: float
    red_min: float
    red_max: float


class KPIDefinition(BaseModel):
    """
    Complete KPI definition from the catalog.

    This model represents a single KPI with all its metadata,
    loaded from kpi_catalog.yaml.
    """

    id: str
    display_name_en: str
    display_name_ar: str
    description_en: str
    description_ar: str
    formula_human_readable: str
    unit: str
    higher_is_better: bool | None
    category: str
    min_value: float | None = None
    max_value: float | None = None
    thresholds: KPIThresholds | None = None
    default_weight_in_sustainability_index: float = 0.0

    def get_display_name(self, language: str = "en") -> str:
        """Get display name in specified language."""
        if language == "ar":
            return self.display_name_ar
        return self.display_name_en

    def get_description(self, language: str = "en") -> str:
        """Get description in specified language."""
        if language == "ar":
            return self.description_ar
        return self.description_en


class IndicatorRecord(BaseModel):
    """
    A single indicator record from the database.

    This is the main data model representing a row of KPI data
    for a specific tenant, year, quarter, and region.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int | None = None
    tenant_id: str
    year: int
    quarter: int
    region: str

    # Economic indicators
    gdp_growth: float | None = None
    gdp_total: float | None = None
    foreign_investment: float | None = None
    export_diversity_index: float | None = None
    economic_complexity: float | None = None
    population: float | None = None

    # Labor indicators
    unemployment_rate: float | None = None
    green_jobs: float | None = None
    skills_gap_index: float | None = None

    # Social indicators
    social_progress_score: float | None = None
    digital_readiness: float | None = None
    innovation_index: float | None = None

    # Environmental indicators
    co2_index: float | None = None
    co2_total: float | None = None
    renewable_share: float | None = None
    energy_intensity: float | None = None
    water_efficiency: float | None = None
    waste_recycling_rate: float | None = None
    forest_coverage: float | None = None
    air_quality_index: float | None = None

    # Derived indicators
    co2_per_gdp: float | None = None
    co2_per_capita: float | None = None

    # Quality and composite
    data_quality_score: float | None = None
    sustainability_index: float | None = None

    # Metadata
    source_system: str | None = None
    load_timestamp: datetime | None = None
    load_batch_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary, excluding None values."""
        return {k: v for k, v in self.model_dump().items() if v is not None}

    def get_kpi_value(self, kpi_id: str) -> float | None:
        """Get the value of a specific KPI by its ID."""
        return getattr(self, kpi_id, None)


class FilterParams(BaseModel):
    """
    Filter parameters for data queries.

    Used throughout the application to standardize filtering.
    """

    tenant_id: str
    year: int | None = Field(None, ge=2000, le=2100)
    quarter: int | None = Field(None, ge=1, le=4)
    region: str | None = None
    years: list[int] | None = None  # For multi-year queries
    regions: list[str] | None = None  # For multi-region queries

    @field_validator("quarter")
    @classmethod
    def validate_quarter(cls, v: int | None) -> int | None:
        """Validate quarter is between 1 and 4."""
        if v is not None and (v < 1 or v > 4):
            raise ValueError("Quarter must be between 1 and 4")
        return v

    def to_query_params(self) -> dict[str, Any]:
        """Convert to query parameters dictionary."""
        params = {"tenant_id": self.tenant_id}
        if self.year:
            params["year"] = self.year
        if self.quarter:
            params["quarter"] = self.quarter
        if self.region and self.region != "all":
            params["region"] = self.region
        return params


class SummaryMetrics(BaseModel):
    """Aggregated summary metrics for dashboards."""

    sustainability_index: float
    sustainability_index_change: float
    sustainability_status: KPIStatus

    gdp_growth: float
    gdp_growth_change: float
    gdp_growth_status: KPIStatus

    renewable_share: float
    renewable_share_change: float
    renewable_share_status: KPIStatus

    co2_index: float
    co2_index_change: float
    co2_index_status: KPIStatus

    green_jobs: float
    green_jobs_change: float
    green_jobs_status: KPIStatus

    unemployment_rate: float
    unemployment_rate_change: float
    unemployment_rate_status: KPIStatus

    data_quality_score: float
    data_quality_status: KPIStatus

    period_label: str  # e.g., "Q4 2024"
    comparison_label: str  # e.g., "vs Q3 2024"

    top_improvements: list[dict[str, Any]] = Field(default_factory=list)
    top_deteriorations: list[dict[str, Any]] = Field(default_factory=list)


class TimeSeriesPoint(BaseModel):
    """A single point in a time series."""

    period: str  # e.g., "2024-Q1"
    value: float
    status: KPIStatus | None = None


class RegionalComparison(BaseModel):
    """Regional comparison data for a single KPI."""

    kpi_id: str
    kpi_name: str
    regions: list[str]
    values: list[float]
    statuses: list[KPIStatus]
    national_average: float


class DashboardSummary(BaseModel):
    """
    Summary data for executive dashboard view.

    Contains aggregated metrics and status counts for quick overview.
    """

    total_indicators: int = 0
    on_target_count: int = 0
    warning_count: int = 0
    critical_count: int = 0
    improving_count: int = 0
    declining_count: int = 0

    # Overall percentages
    on_target_percentage: float = 0.0
    warning_percentage: float = 0.0
    critical_percentage: float = 0.0

    # Key metrics
    average_achievement: float = 0.0
    sustainability_index: float | None = None  # Composite sustainability score 0-100
    top_performers: list[dict[str, Any]] = Field(default_factory=list)
    attention_needed: list[dict[str, Any]] = Field(default_factory=list)

    # Time context
    period: str = ""
    comparison_period: str | None = None

    def calculate_percentages(self) -> None:
        """Calculate percentages based on counts."""
        if self.total_indicators > 0:
            self.on_target_percentage = (self.on_target_count / self.total_indicators) * 100
            self.warning_percentage = (self.warning_count / self.total_indicators) * 100
            self.critical_percentage = (self.critical_count / self.total_indicators) * 100
