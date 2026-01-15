"""
Dashboard API Router
Sustainable Economic Development Analytics Hub
Ministry of Economy and Planning

Provides REST API endpoints for the React frontend dashboard.
These endpoints match the frontend's expected API contract.
"""

from fastapi import APIRouter, Query

from analytics_hub_platform.api.dependencies import (
    IndicatorRepository,
    get_current_tenant,
    get_indicator_repository,
)
from analytics_hub_platform.config.config import get_config
from analytics_hub_platform.domain.models import FilterParams
from analytics_hub_platform.domain.services import (
    get_available_periods,
    get_available_regions,
    get_data_quality_metrics,
    get_executive_snapshot,
    get_kpi_timeseries,
    get_regional_comparison,
    get_sustainability_summary,
)
from fastapi import Depends
from pydantic import BaseModel


# =============================================================================
# RESPONSE MODELS (matching frontend TypeScript interfaces)
# =============================================================================


class PeriodSchema(BaseModel):
    """Time period for data filtering."""
    year: int
    quarter: int
    label: str


class FiltersResponse(BaseModel):
    """Available filter options for the dashboard."""
    periods: list[PeriodSchema]
    regions: list[str]
    current_period: PeriodSchema


class MetricSchema(BaseModel):
    """KPI metric with change tracking."""
    value: float | None = None
    previous_value: float | None = None
    change: float | None = None
    change_percent: float | None = None
    status: str = "unknown"
    display_name: str = ""
    higher_is_better: bool = True


class ChangeItem(BaseModel):
    """Top improvement/deterioration item."""
    kpi_id: str
    display_name: str
    change_percent: float
    direction: str


class SustainabilityBreakdown(BaseModel):
    """Pillar breakdown for sustainability index."""
    id: str
    name: str
    name_ar: str | None = None
    score: float | None = None
    status: str = "unknown"


class HeroResponse(BaseModel):
    """Hero section data with gauge and KPI cards."""
    period: str
    comparison_period: str
    sustainability_index: float | None = None
    sustainability_status: str = "unknown"
    sustainability_breakdown: list[SustainabilityBreakdown] = []
    metrics: dict[str, MetricSchema] = {}
    top_improvements: list[ChangeItem] = []
    top_deteriorations: list[ChangeItem] = []


class PillarSchema(BaseModel):
    """Sustainability pillar details."""
    id: str
    name: str
    name_ar: str | None = None
    score: float | None = None
    status: str = "unknown"
    kpis: list[MetricSchema] = []


class PillarsResponse(BaseModel):
    """Pillars breakdown response."""
    period: str
    pillars: list[PillarSchema]


class RegionDataSchema(BaseModel):
    """Regional data point."""
    region: str
    value: float
    status: str
    rank: int | None = None


class RegionalComparisonResponse(BaseModel):
    """Regional comparison data."""
    kpi_id: str
    kpi_name: str
    period: str
    regions: list[RegionDataSchema]
    national_average: float


class MapDataPoint(BaseModel):
    """Map visualization data point."""
    region: str
    region_ar: str | None = None
    latitude: float
    longitude: float
    value: float
    status: str


class MapResponse(BaseModel):
    """Map visualization response."""
    kpi_id: str
    kpi_name: str
    period: str
    data: list[MapDataPoint]
    national_average: float


class KPIMissingInfo(BaseModel):
    """Missing data info for a KPI."""
    kpi_id: str
    display_name: str
    missing: int
    total: int
    percent: float


class DataQualityResponse(BaseModel):
    """Data quality metrics response."""
    period: str
    completeness: float
    records_count: int
    avg_quality_score: float | None = None
    last_update: str | None = None
    missing_by_kpi: list[KPIMissingInfo] = []


class InsightSchema(BaseModel):
    """AI-generated insight."""
    id: str
    type: str
    title: str
    title_ar: str | None = None
    description: str
    description_ar: str | None = None
    kpi_id: str | None = None
    value: float | None = None
    change_percent: float | None = None


class InsightsResponse(BaseModel):
    """Insights response."""
    period: str
    insights: list[InsightSchema]


class TimeSeriesPointSchema(BaseModel):
    """Time series data point."""
    period: str
    value: float
    status: str


class TimeSeriesResponse(BaseModel):
    """Time series response."""
    kpi_id: str
    kpi_name: str
    data: list[TimeSeriesPointSchema]


# =============================================================================
# REGION COORDINATES (for map visualization)
# =============================================================================

REGION_COORDINATES = {
    "Riyadh": {"lat": 24.7136, "lng": 46.6753, "ar": "الرياض"},
    "Makkah": {"lat": 21.3891, "lng": 39.8579, "ar": "مكة المكرمة"},
    "Madinah": {"lat": 24.5247, "lng": 39.5692, "ar": "المدينة المنورة"},
    "Eastern": {"lat": 26.4207, "lng": 50.0888, "ar": "المنطقة الشرقية"},
    "Qassim": {"lat": 26.3260, "lng": 43.9750, "ar": "القصيم"},
    "Asir": {"lat": 18.2164, "lng": 42.5053, "ar": "عسير"},
    "Tabuk": {"lat": 28.3838, "lng": 36.5550, "ar": "تبوك"},
    "Hail": {"lat": 27.5236, "lng": 41.6983, "ar": "حائل"},
    "Northern Borders": {"lat": 30.9843, "lng": 41.1183, "ar": "الحدود الشمالية"},
    "Jazan": {"lat": 16.8893, "lng": 42.5706, "ar": "جازان"},
    "Najran": {"lat": 17.4922, "lng": 44.1277, "ar": "نجران"},
    "Al Bahah": {"lat": 20.0129, "lng": 41.4677, "ar": "الباحة"},
    "Al Jawf": {"lat": 29.8868, "lng": 39.3206, "ar": "الجوف"},
}


def _get_default_period(repo: IndicatorRepository, tenant_id: str) -> tuple[int, int]:
    """Get the most recent period from the data."""
    df = repo.get_all_indicators(tenant_id)
    if df.empty:
        return 2024, 4  # Fallback default

    latest = df.sort_values(["year", "quarter"], ascending=False).iloc[0]
    return int(latest["year"]), int(latest["quarter"])


def create_dashboard_router() -> APIRouter:
    """
    Create and configure the dashboard API router.

    Returns:
        Configured APIRouter instance with all dashboard endpoints.
    """
    router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

    @router.get("/filters", response_model=FiltersResponse)
    async def get_filters(
        language: str = Query(default="en", description="Language code (en/ar)"),
        tenant_id: str = Depends(get_current_tenant),
        repo: IndicatorRepository = Depends(get_indicator_repository),
    ) -> FiltersResponse:
        """
        Get available filter options for the dashboard.

        Returns list of available periods, regions, and the current period.
        """
        df = repo.get_all_indicators(tenant_id)
        periods_data = get_available_periods(df)
        regions = get_available_regions(df)

        periods = [
            PeriodSchema(year=p["year"], quarter=p["quarter"], label=p["label"])
            for p in periods_data
        ]

        # Current period is the most recent one
        current = periods[0] if periods else PeriodSchema(year=2024, quarter=4, label="Q4 2024")

        return FiltersResponse(periods=periods, regions=regions, current_period=current)

    @router.get("/hero", response_model=HeroResponse)
    async def get_hero_data(
        year: int | None = Query(default=None, description="Year"),
        quarter: int | None = Query(default=None, ge=1, le=4, description="Quarter (1-4)"),
        region: str | None = Query(default=None, description="Region filter"),
        language: str = Query(default="en", description="Language code (en/ar)"),
        tenant_id: str = Depends(get_current_tenant),
        repo: IndicatorRepository = Depends(get_indicator_repository),
    ) -> HeroResponse:
        """
        Get hero section data including sustainability gauge and KPI cards.
        """
        df = repo.get_all_indicators(tenant_id)
        _config = get_config()  # Reserved for future use

        # Use default period if not specified
        if year is None or quarter is None:
            year, quarter = _get_default_period(repo, tenant_id)

        filters = FilterParams(
            tenant_id=tenant_id,
            year=year,
            quarter=quarter,
            region=region,
        )

        # Get executive snapshot
        snapshot = get_executive_snapshot(df, filters, language)

        # Get sustainability summary
        sustainability = get_sustainability_summary(df, filters, language)

        # Build metrics dict
        metrics = {}
        for kpi_id, data in snapshot.get("metrics", {}).items():
            metrics[kpi_id] = MetricSchema(
                value=data.get("value"),
                previous_value=data.get("previous_value"),
                change=data.get("change"),
                change_percent=data.get("change_percent"),
                status=data.get("status", "unknown"),
                display_name=data.get("display_name", kpi_id),
                higher_is_better=data.get("higher_is_better", True),
            )

        # Build improvements/deteriorations
        improvements = [
            ChangeItem(
                kpi_id=item["kpi_id"],
                display_name=item["display_name"],
                change_percent=item["change_percent"],
                direction=item["direction"],
            )
            for item in snapshot.get("top_improvements", [])
        ]

        deteriorations = [
            ChangeItem(
                kpi_id=item["kpi_id"],
                display_name=item["display_name"],
                change_percent=item["change_percent"],
                direction=item["direction"],
            )
            for item in snapshot.get("top_deteriorations", [])
        ]

        # Build breakdown
        breakdown = [
            SustainabilityBreakdown(
                id=item.get("id", ""),
                name=item.get("name", item.get("name_en", "")),
                name_ar=item.get("name_ar"),
                score=item.get("score"),
                status=item.get("status", "unknown"),
            )
            for item in sustainability.get("breakdown", [])
        ]

        return HeroResponse(
            period=snapshot.get("period", f"Q{quarter} {year}"),
            comparison_period=snapshot.get("comparison_period", ""),
            sustainability_index=sustainability.get("index"),
            sustainability_status=sustainability.get("status", "unknown"),
            sustainability_breakdown=breakdown,
            metrics=metrics,
            top_improvements=improvements,
            top_deteriorations=deteriorations,
        )

    @router.get("/pillars", response_model=PillarsResponse)
    async def get_pillars_data(
        year: int | None = Query(default=None, description="Year"),
        quarter: int | None = Query(default=None, ge=1, le=4, description="Quarter (1-4)"),
        region: str | None = Query(default=None, description="Region filter"),
        language: str = Query(default="en", description="Language code (en/ar)"),
        tenant_id: str = Depends(get_current_tenant),
        repo: IndicatorRepository = Depends(get_indicator_repository),
    ) -> PillarsResponse:
        """
        Get sustainability pillars breakdown.
        """
        df = repo.get_all_indicators(tenant_id)

        if year is None or quarter is None:
            year, quarter = _get_default_period(repo, tenant_id)

        filters = FilterParams(tenant_id=tenant_id, year=year, quarter=quarter, region=region)
        sustainability = get_sustainability_summary(df, filters, language)

        pillars = []
        for item in sustainability.get("breakdown", []):
            pillar = PillarSchema(
                id=item.get("id", ""),
                name=item.get("name", item.get("name_en", "")),
                name_ar=item.get("name_ar"),
                score=item.get("score"),
                status=item.get("status", "unknown"),
                kpis=[],
            )
            pillars.append(pillar)

        return PillarsResponse(
            period=sustainability.get("period", f"Q{quarter} {year}"),
            pillars=pillars,
        )

    @router.get("/regions", response_model=RegionalComparisonResponse)
    async def get_regional_data(
        kpi_id: str = Query(default="sustainability_index", description="KPI to compare"),
        year: int | None = Query(default=None, description="Year"),
        quarter: int | None = Query(default=None, ge=1, le=4, description="Quarter (1-4)"),
        language: str = Query(default="en", description="Language code (en/ar)"),
        tenant_id: str = Depends(get_current_tenant),
        repo: IndicatorRepository = Depends(get_indicator_repository),
    ) -> RegionalComparisonResponse:
        """
        Get regional comparison data for a specific KPI.
        """
        df = repo.get_all_indicators(tenant_id)

        if year is None or quarter is None:
            year, quarter = _get_default_period(repo, tenant_id)

        filters = FilterParams(tenant_id=tenant_id, year=year, quarter=quarter)
        comparison = get_regional_comparison(df, kpi_id, filters, language)

        regions = []
        for i, (region, value, status) in enumerate(
            zip(comparison.regions, comparison.values, comparison.statuses)
        ):
            regions.append(
                RegionDataSchema(
                    region=region,
                    value=value,
                    status=status.value if hasattr(status, "value") else str(status),
                    rank=i + 1,
                )
            )

        return RegionalComparisonResponse(
            kpi_id=comparison.kpi_id,
            kpi_name=comparison.kpi_name,
            period=f"Q{quarter} {year}",
            regions=regions,
            national_average=comparison.national_average,
        )

    @router.get("/map", response_model=MapResponse)
    async def get_map_data(
        kpi_id: str = Query(default="sustainability_index", description="KPI to visualize"),
        year: int | None = Query(default=None, description="Year"),
        quarter: int | None = Query(default=None, ge=1, le=4, description="Quarter (1-4)"),
        language: str = Query(default="en", description="Language code (en/ar)"),
        tenant_id: str = Depends(get_current_tenant),
        repo: IndicatorRepository = Depends(get_indicator_repository),
    ) -> MapResponse:
        """
        Get map visualization data for Saudi Arabia regions.
        """
        df = repo.get_all_indicators(tenant_id)

        if year is None or quarter is None:
            year, quarter = _get_default_period(repo, tenant_id)

        filters = FilterParams(tenant_id=tenant_id, year=year, quarter=quarter)
        comparison = get_regional_comparison(df, kpi_id, filters, language)

        data = []
        for region, value, status in zip(
            comparison.regions, comparison.values, comparison.statuses
        ):
            coords = REGION_COORDINATES.get(region, {"lat": 24.0, "lng": 45.0, "ar": region})
            data.append(
                MapDataPoint(
                    region=region,
                    region_ar=coords.get("ar"),
                    latitude=coords["lat"],
                    longitude=coords["lng"],
                    value=value,
                    status=status.value if hasattr(status, "value") else str(status),
                )
            )

        return MapResponse(
            kpi_id=comparison.kpi_id,
            kpi_name=comparison.kpi_name,
            period=f"Q{quarter} {year}",
            data=data,
            national_average=comparison.national_average,
        )

    @router.get("/quality", response_model=DataQualityResponse)
    async def get_quality_data(
        year: int | None = Query(default=None, description="Year"),
        quarter: int | None = Query(default=None, ge=1, le=4, description="Quarter (1-4)"),
        region: str | None = Query(default=None, description="Region filter"),
        language: str = Query(default="en", description="Language code (en/ar)"),
        tenant_id: str = Depends(get_current_tenant),
        repo: IndicatorRepository = Depends(get_indicator_repository),
    ) -> DataQualityResponse:
        """
        Get data quality metrics for the analyst view.
        """
        df = repo.get_all_indicators(tenant_id)

        if year is None or quarter is None:
            year, quarter = _get_default_period(repo, tenant_id)

        filters = FilterParams(tenant_id=tenant_id, year=year, quarter=quarter, region=region)
        quality = get_data_quality_metrics(df, filters)

        # Convert missing_by_kpi dict to list
        missing_list = []
        for kpi_id, info in quality.get("missing_by_kpi", {}).items():
            missing_list.append(
                KPIMissingInfo(
                    kpi_id=kpi_id,
                    display_name=kpi_id.replace("_", " ").title(),
                    missing=info.get("missing", 0),
                    total=info.get("total", 0),
                    percent=info.get("percent", 0),
                )
            )

        last_update = quality.get("last_update")
        last_update_str = last_update.isoformat() if last_update else None

        return DataQualityResponse(
            period=f"Q{quarter} {year}",
            completeness=quality.get("completeness", 0),
            records_count=quality.get("records_count", 0),
            avg_quality_score=quality.get("avg_quality_score"),
            last_update=last_update_str,
            missing_by_kpi=missing_list,
        )

    @router.get("/insights", response_model=InsightsResponse)
    async def get_insights_data(
        year: int | None = Query(default=None, description="Year"),
        quarter: int | None = Query(default=None, ge=1, le=4, description="Quarter (1-4)"),
        region: str | None = Query(default=None, description="Region filter"),
        language: str = Query(default="en", description="Language code (en/ar)"),
        tenant_id: str = Depends(get_current_tenant),
        repo: IndicatorRepository = Depends(get_indicator_repository),
    ) -> InsightsResponse:
        """
        Get AI-generated insights for the current period.
        """
        df = repo.get_all_indicators(tenant_id)

        if year is None or quarter is None:
            year, quarter = _get_default_period(repo, tenant_id)

        filters = FilterParams(tenant_id=tenant_id, year=year, quarter=quarter, region=region)

        # Get snapshot for generating insights
        snapshot = get_executive_snapshot(df, filters, language)

        insights = []

        # Generate insights from top improvements
        for i, item in enumerate(snapshot.get("top_improvements", [])[:2]):
            insights.append(
                InsightSchema(
                    id=f"improvement_{i}",
                    type="improvement",
                    title=f"{item['display_name']} improved",
                    title_ar=None,
                    description=f"{item['display_name']} improved by {abs(item['change_percent']):.1f}% compared to the previous quarter.",
                    description_ar=None,
                    kpi_id=item["kpi_id"],
                    change_percent=item["change_percent"],
                )
            )

        # Generate insights from deteriorations
        for i, item in enumerate(snapshot.get("top_deteriorations", [])[:2]):
            insights.append(
                InsightSchema(
                    id=f"attention_{i}",
                    type="attention",
                    title=f"{item['display_name']} needs attention",
                    title_ar=None,
                    description=f"{item['display_name']} declined by {abs(item['change_percent']):.1f}% and requires monitoring.",
                    description_ar=None,
                    kpi_id=item["kpi_id"],
                    change_percent=item["change_percent"],
                )
            )

        # Add sustainability index insight if available
        sustainability = get_sustainability_summary(df, filters, language)
        index_value = sustainability.get("index")
        if index_value is not None:
            status = sustainability.get("status", "unknown")
            if status == "good":
                insights.append(
                    InsightSchema(
                        id="sustainability_good",
                        type="success",
                        title="Strong sustainability performance",
                        description=f"The sustainability index of {index_value:.1f} indicates strong overall performance across economic, social, and environmental pillars.",
                        value=index_value,
                    )
                )
            elif status == "moderate":
                insights.append(
                    InsightSchema(
                        id="sustainability_moderate",
                        type="info",
                        title="Moderate sustainability progress",
                        description=f"The sustainability index of {index_value:.1f} shows room for improvement in key areas.",
                        value=index_value,
                    )
                )

        return InsightsResponse(
            period=f"Q{quarter} {year}",
            insights=insights,
        )

    @router.get("/timeseries", response_model=TimeSeriesResponse)
    async def get_timeseries_data(
        kpi_id: str = Query(description="KPI identifier"),
        region: str | None = Query(default=None, description="Region filter"),
        years: str | None = Query(default=None, description="Comma-separated years"),
        language: str = Query(default="en", description="Language code (en/ar)"),
        tenant_id: str = Depends(get_current_tenant),
        repo: IndicatorRepository = Depends(get_indicator_repository),
    ) -> TimeSeriesResponse:
        """
        Get time series data for a specific KPI.
        """
        df = repo.get_all_indicators(tenant_id)

        # Parse years if provided
        years_list = None
        if years:
            years_list = [int(y.strip()) for y in years.split(",")]

        filters = FilterParams(tenant_id=tenant_id, region=region, year=None, quarter=None)
        timeseries = get_kpi_timeseries(df, kpi_id, filters, years_list)

        data = [
            TimeSeriesPointSchema(
                period=point.period,
                value=point.value,
                status=point.status.value if point.status and hasattr(point.status, "value") else str(point.status or "unknown"),
            )
            for point in timeseries
        ]

        # Get display name
        display_name = kpi_id.replace("_", " ").title()

        return TimeSeriesResponse(
            kpi_id=kpi_id,
            kpi_name=display_name,
            data=data,
        )

    return router
