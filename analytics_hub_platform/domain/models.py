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
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict, field_validator


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
    GREEN = "green"      # On track / good performance
    AMBER = "amber"      # At risk / needs attention
    RED = "red"          # Critical / action required
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
    name_ar: Optional[str] = Field(None, description="Arabic display name")
    country_code: str = Field(default="SA", description="ISO country code")
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
    
    # Configuration overrides for this tenant
    config_overrides: Optional[Dict[str, Any]] = Field(default=None)


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
    name_ar: Optional[str] = Field(None, description="Arabic display name")
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
    higher_is_better: Optional[bool]
    category: str
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    thresholds: Optional[KPIThresholds] = None
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
    
    id: Optional[int] = None
    tenant_id: str
    year: int
    quarter: int
    region: str
    
    # Economic indicators
    gdp_growth: Optional[float] = None
    gdp_total: Optional[float] = None
    foreign_investment: Optional[float] = None
    export_diversity_index: Optional[float] = None
    economic_complexity: Optional[float] = None
    population: Optional[float] = None
    
    # Labor indicators
    unemployment_rate: Optional[float] = None
    green_jobs: Optional[float] = None
    skills_gap_index: Optional[float] = None
    
    # Social indicators
    social_progress_score: Optional[float] = None
    digital_readiness: Optional[float] = None
    innovation_index: Optional[float] = None
    
    # Environmental indicators
    co2_index: Optional[float] = None
    co2_total: Optional[float] = None
    renewable_share: Optional[float] = None
    energy_intensity: Optional[float] = None
    water_efficiency: Optional[float] = None
    waste_recycling_rate: Optional[float] = None
    forest_coverage: Optional[float] = None
    air_quality_index: Optional[float] = None
    
    # Derived indicators
    co2_per_gdp: Optional[float] = None
    co2_per_capita: Optional[float] = None
    
    # Quality and composite
    data_quality_score: Optional[float] = None
    sustainability_index: Optional[float] = None
    
    # Metadata
    source_system: Optional[str] = None
    load_timestamp: Optional[datetime] = None
    load_batch_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, excluding None values."""
        return {k: v for k, v in self.model_dump().items() if v is not None}
    
    def get_kpi_value(self, kpi_id: str) -> Optional[float]:
        """Get the value of a specific KPI by its ID."""
        return getattr(self, kpi_id, None)


class FilterParams(BaseModel):
    """
    Filter parameters for data queries.
    
    Used throughout the application to standardize filtering.
    """
    tenant_id: str
    year: Optional[int] = Field(None, ge=2000, le=2100)
    quarter: Optional[int] = Field(None, ge=1, le=4)
    region: Optional[str] = None
    years: Optional[List[int]] = None  # For multi-year queries
    regions: Optional[List[str]] = None  # For multi-region queries
    
    @field_validator('quarter')
    @classmethod
    def validate_quarter(cls, v: Optional[int]) -> Optional[int]:
        """Validate quarter is between 1 and 4."""
        if v is not None and (v < 1 or v > 4):
            raise ValueError('Quarter must be between 1 and 4')
        return v
    
    def to_query_params(self) -> Dict[str, Any]:
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
    
    top_improvements: List[Dict[str, Any]] = Field(default_factory=list)
    top_deteriorations: List[Dict[str, Any]] = Field(default_factory=list)


class TimeSeriesPoint(BaseModel):
    """A single point in a time series."""
    period: str  # e.g., "2024-Q1"
    value: float
    status: Optional[KPIStatus] = None


class RegionalComparison(BaseModel):
    """Regional comparison data for a single KPI."""
    kpi_id: str
    kpi_name: str
    regions: List[str]
    values: List[float]
    statuses: List[KPIStatus]
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
    sustainability_index: Optional[float] = None  # Composite sustainability score 0-100
    top_performers: List[Dict[str, Any]] = Field(default_factory=list)
    attention_needed: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Time context
    period: str = ""
    comparison_period: Optional[str] = None
    
    def calculate_percentages(self) -> None:
        """Calculate percentages based on counts."""
        if self.total_indicators > 0:
            self.on_target_percentage = (self.on_target_count / self.total_indicators) * 100
            self.warning_percentage = (self.warning_count / self.total_indicators) * 100
            self.critical_percentage = (self.critical_count / self.total_indicators) * 100
