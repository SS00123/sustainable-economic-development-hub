"""
API Routers
Sustainable Economic Development Analytics Hub
Ministry of Economy and Planning

FastAPI route definitions for REST API endpoints.
"""

import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, ConfigDict, Field

from analytics_hub_platform.api.dependencies import (
    FilterDependency,
    IndicatorRepository,
    PaginationParams,
    get_current_tenant,
    get_filters,
    get_indicator_repository,
    get_pagination,
    require_analyst,
)
from analytics_hub_platform.config.config import REGIONS, get_config
from analytics_hub_platform.domain.models import FilterParams
from analytics_hub_platform.domain.services import (
    get_data_quality_metrics,
    get_sustainability_summary,
)
from analytics_hub_platform.infrastructure.exceptions import (
    AnalyticsHubError,
    DataError,
    NotFoundError,
    ValidationError,
)


# Response Models
class HealthResponse(BaseModel):
    """Health check response."""

    status: str = "ok"
    timestamp: str
    version: str


class IndicatorResponse(BaseModel):
    """Single indicator record response with all sustainability metrics."""

    id: int = Field(..., description="Unique record identifier")
    tenant_id: str = Field(..., description="Tenant/organization identifier")
    year: int = Field(..., ge=2015, le=2030, description="Reporting year")
    quarter: int = Field(..., ge=1, le=4, description="Reporting quarter (1-4)")
    region: str = Field(..., description="Saudi region identifier")
    sustainability_index: float | None = Field(
        None, ge=0, le=100, description="Composite sustainability score (0-100)"
    )
    co2_per_gdp: float | None = Field(None, description="CO2 emissions per unit GDP (kg/$)")
    co2_per_capita: float | None = Field(None, description="CO2 emissions per capita (tonnes)")
    renewable_energy_pct: float | None = Field(
        None, ge=0, le=100, description="Renewable energy share (%)"
    )
    green_investment_pct: float | None = Field(
        None, ge=0, le=100, description="Green investment share (%)"
    )
    gdp_growth: float | None = Field(None, description="GDP growth rate (%)")
    employment_rate: float | None = Field(None, ge=0, le=100, description="Employment rate (%)")
    data_quality_score: float | None = Field(
        None, ge=0, le=100, description="Data quality score (0-100)"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 1,
                "tenant_id": "ministry_mep",
                "year": 2024,
                "quarter": 1,
                "region": "riyadh",
                "sustainability_index": 72.5,
                "co2_per_gdp": 0.45,
                "co2_per_capita": 18.2,
                "renewable_energy_pct": 12.5,
                "green_investment_pct": 8.3,
                "gdp_growth": 4.2,
                "employment_rate": 94.5,
                "data_quality_score": 98.5,
            }
        }
    )


class IndicatorListResponse(BaseModel):
    """Paginated list of indicator records."""

    data: list[IndicatorResponse] = Field(..., description="List of indicator records")
    total: int = Field(..., description="Total number of matching records")
    page: int = Field(..., ge=1, description="Current page number")
    page_size: int = Field(..., ge=1, le=100, description="Records per page")
    total_pages: int = Field(..., ge=0, description="Total number of pages")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "data": [
                    {
                        "id": 1,
                        "tenant_id": "ministry_mep",
                        "year": 2024,
                        "quarter": 1,
                        "region": "riyadh",
                        "sustainability_index": 72.5,
                    }
                ],
                "total": 150,
                "page": 1,
                "page_size": 20,
                "total_pages": 8,
            }
        }
    )


class SustainabilitySummaryResponse(BaseModel):
    """Aggregated sustainability metrics summary."""

    sustainability_index: float = Field(..., description="Current sustainability index value")
    sustainability_trend: float = Field(..., description="Quarter-over-quarter change")
    co2_per_gdp: float = Field(..., description="CO2 intensity per GDP")
    co2_per_capita: float = Field(..., description="Per-capita CO2 emissions")
    renewable_energy_pct: float = Field(..., description="Renewable energy share")
    green_investment_pct: float = Field(..., description="Green investment share")
    data_quality_score: float = Field(..., description="Data quality score")
    period: str = Field(..., description="Reporting period (e.g., 'Q1 2024')")
    region: str | None = Field(None, description="Region filter applied, or 'all'")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "sustainability_index": 72.5,
                "sustainability_trend": 2.3,
                "co2_per_gdp": 0.45,
                "co2_per_capita": 18.2,
                "renewable_energy_pct": 12.5,
                "green_investment_pct": 8.3,
                "data_quality_score": 98.5,
                "period": "Q1 2024",
                "region": "all",
            }
        }
    )


class RegionalComparisonResponse(BaseModel):
    """Regional comparison with ranking."""

    region: str = Field(..., description="Region identifier")
    sustainability_index: float = Field(..., description="Average sustainability index")
    rank: int = Field(..., ge=1, description="Performance ranking (1 = best)")

    model_config = ConfigDict(
        json_schema_extra={"example": {"region": "riyadh", "sustainability_index": 78.5, "rank": 1}}
    )


class TimeSeriesPoint(BaseModel):
    """Time series data point."""

    period: str
    value: float


class TimeSeriesResponse(BaseModel):
    """Time series response."""

    indicator: str
    data: list[TimeSeriesPoint]


class DataQualityResponse(BaseModel):
    """Data quality metrics response."""

    completeness: float
    avg_quality_score: float
    records_count: int
    last_update: str | None = None
    missing_by_kpi: dict


class ErrorResponse(BaseModel):
    """Error response model for API errors."""

    detail: str = Field(..., description="Human-readable error message")
    code: str | None = Field(None, description="Machine-readable error code")
    error_type: str | None = Field(None, description="Error type/category")
    correlation_id: str | None = Field(None, description="Request correlation ID for debugging")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "detail": "Invalid quarter value. Must be between 1 and 4.",
                "code": "VALIDATION_ERROR",
                "correlation_id": "req-abc123-def456",
            }
        }
    )


logger = logging.getLogger(__name__)


def handle_exception(e: Exception) -> HTTPException:
    """
    Convert exceptions to appropriate HTTP responses.

    Args:
        e: Exception to handle

    Returns:
        HTTPException with appropriate status code
    """
    if isinstance(e, ValidationError):
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    elif isinstance(e, NotFoundError):
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    elif isinstance(e, DataError):
        return HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )
    elif isinstance(e, AnalyticsHubError):
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
    else:
        # Log unexpected errors
        logger.exception("Unexpected error in API endpoint")
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal error occurred. Please try again later.",
        )


def create_api_router() -> APIRouter:
    """
    Create and configure the main API router.

    Returns:
        Configured APIRouter instance
    """
    router = APIRouter()
    config = get_config()

    # Health check
    @router.get(
        "/health",
        response_model=HealthResponse,
        tags=["System"],
        summary="Health check endpoint",
    )
    async def health_check():
        """Check API health status."""
        return HealthResponse(
            status="ok",
            timestamp=datetime.now(timezone.utc).isoformat(),
            version="1.0.0",
        )

    # Indicators CRUD
    @router.get(
        "/indicators",
        response_model=IndicatorListResponse,
        tags=["Indicators"],
        summary="List sustainability indicators",
        dependencies=[Depends(require_analyst)],
    )
    async def list_indicators(
        tenant_id: str = Depends(get_current_tenant),
        filters: FilterDependency = Depends(get_filters),
        pagination: PaginationParams = Depends(get_pagination),
        repo: IndicatorRepository = Depends(get_indicator_repository),
    ):
        """
        Get paginated list of sustainability indicators.

        Supports filtering by year, quarter, and region.
        """
        try:
            df = repo.get_all_indicators(tenant_id)

            # Apply filters
            if filters.year:
                df = df[df["year"] == filters.year]
            if filters.quarter:
                df = df[df["quarter"] == filters.quarter]
            if filters.region:
                df = df[df["region"] == filters.region]

            total = len(df)
            total_pages = (total + pagination.page_size - 1) // pagination.page_size

            # Paginate
            df_page = df.iloc[pagination.offset : pagination.offset + pagination.limit]

            data = [
                IndicatorResponse(
                    id=idx,
                    tenant_id=row.get("tenant_id", tenant_id),
                    year=int(row["year"]),
                    quarter=int(row["quarter"]),
                    region=row["region"],
                    sustainability_index=row.get("sustainability_index"),
                    co2_per_gdp=row.get("co2_per_gdp"),
                    co2_per_capita=row.get("co2_per_capita"),
                    renewable_energy_pct=row.get("renewable_energy_pct"),
                    green_investment_pct=row.get("green_investment_pct"),
                    gdp_growth=row.get("gdp_growth"),
                    employment_rate=row.get("employment_rate"),
                    data_quality_score=row.get("data_quality_score"),
                )
                for idx, row in df_page.iterrows()
            ]

            return IndicatorListResponse(
                data=data,
                total=total,
                page=pagination.page,
                page_size=pagination.page_size,
                total_pages=total_pages,
            )

        except HTTPException:
            raise
        except Exception as e:
            raise handle_exception(e)

    # Sustainability summary
    @router.get(
        "/sustainability/summary",
        response_model=SustainabilitySummaryResponse,
        tags=["Sustainability"],
        summary="Get sustainability summary",
    )
    async def get_summary(
        tenant_id: str = Depends(get_current_tenant),
        year: int = Query(default=None),
        quarter: int = Query(default=None, ge=1, le=4),
        region: str | None = Query(default=None),
        repo: IndicatorRepository = Depends(get_indicator_repository),
    ):
        """
        Get aggregated sustainability summary for a period.
        """
        try:
            df = repo.get_all_indicators(tenant_id)

            filter_params = FilterParams(
                tenant_id=tenant_id,
                year=year or config.default_year,
                quarter=quarter or config.default_quarter,
                region=region,
            )

            summary = get_sustainability_summary(df, filter_params)

            period = f"Q{filter_params.quarter} {filter_params.year}"

            return SustainabilitySummaryResponse(
                sustainability_index=summary.get("sustainability_index", 0),
                sustainability_trend=summary.get("sustainability_trend", 0),
                co2_per_gdp=summary.get("co2_per_gdp", 0),
                co2_per_capita=summary.get("co2_per_capita", 0),
                renewable_energy_pct=summary.get("renewable_energy_pct", 0),
                green_investment_pct=summary.get("green_investment_pct", 0),
                data_quality_score=summary.get("data_quality_score", 0),
                period=period,
                region=region,
            )

        except HTTPException:
            raise
        except Exception as e:
            raise handle_exception(e)

    # Regional comparison
    @router.get(
        "/sustainability/regions",
        response_model=list[RegionalComparisonResponse],
        tags=["Sustainability"],
        summary="Get regional sustainability comparison",
    )
    async def get_regional_comparison(
        tenant_id: str = Depends(get_current_tenant),
        year: int = Query(default=None),
        quarter: int = Query(default=None, ge=1, le=4),
        repo: IndicatorRepository = Depends(get_indicator_repository),
    ):
        """
        Compare sustainability index across regions.
        """
        try:
            df = repo.get_all_indicators(tenant_id)

            # Filter by period
            if year:
                df = df[df["year"] == year]
            if quarter:
                df = df[df["quarter"] == quarter]

            # Aggregate by region
            regional = df.groupby("region")["sustainability_index"].mean().reset_index()
            regional = regional.sort_values("sustainability_index", ascending=False)
            regional["rank"] = range(1, len(regional) + 1)

            return [
                RegionalComparisonResponse(
                    region=row["region"],
                    sustainability_index=round(row["sustainability_index"], 2),
                    rank=row["rank"],
                )
                for _, row in regional.iterrows()
            ]

        except HTTPException:
            raise
        except Exception as e:
            raise handle_exception(e)

    # Time series
    @router.get(
        "/sustainability/timeseries/{indicator}",
        response_model=TimeSeriesResponse,
        tags=["Sustainability"],
        summary="Get indicator time series",
    )
    async def get_timeseries(
        indicator: str,
        tenant_id: str = Depends(get_current_tenant),
        region: str | None = Query(default=None),
        repo: IndicatorRepository = Depends(get_indicator_repository),
    ):
        """
        Get time series data for a specific indicator.
        """
        valid_indicators = [
            "sustainability_index",
            "co2_per_gdp",
            "co2_per_capita",
            "renewable_energy_pct",
            "green_investment_pct",
            "gdp_growth",
        ]

        if indicator not in valid_indicators:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid indicator. Must be one of: {valid_indicators}",
            )

        try:
            df = repo.get_all_indicators(tenant_id)

            if region:
                df = df[df["region"] == region]

            # Aggregate by period
            ts = df.groupby(["year", "quarter"])[indicator].mean().reset_index()
            ts["period"] = ts.apply(lambda r: f"Q{int(r['quarter'])} {int(r['year'])}", axis=1)
            ts = ts.sort_values(["year", "quarter"])

            return TimeSeriesResponse(
                indicator=indicator,
                data=[
                    TimeSeriesPoint(
                        period=row["period"],
                        value=round(row[indicator], 2),
                    )
                    for _, row in ts.iterrows()
                ],
            )

        except HTTPException:
            raise
        except Exception as e:
            raise handle_exception(e)

    # Data quality
    @router.get(
        "/data-quality",
        response_model=DataQualityResponse,
        tags=["Data Quality"],
        summary="Get data quality metrics",
    )
    async def get_data_quality(
        tenant_id: str = Depends(get_current_tenant),
        repo: IndicatorRepository = Depends(get_indicator_repository),
    ):
        """
        Get data quality metrics including completeness and freshness.
        """
        try:
            df = repo.get_all_indicators(tenant_id)

            filter_params = FilterParams(tenant_id=tenant_id)
            metrics = get_data_quality_metrics(df, filter_params)

            last_update = metrics.get("last_update")
            last_update_str = last_update.isoformat() if last_update else None

            return DataQualityResponse(
                completeness=metrics.get("completeness", 0),
                avg_quality_score=metrics.get("avg_quality_score", 0),
                records_count=metrics.get("records_count", 0),
                last_update=last_update_str,
                missing_by_kpi=metrics.get("missing_by_kpi", {}),
            )

        except HTTPException:
            raise
        except Exception as e:
            raise handle_exception(e)

    # Regions reference data
    @router.get(
        "/reference/regions",
        response_model=list[str],
        tags=["Reference"],
        summary="Get list of regions",
    )
    async def get_regions():
        """Get list of Saudi regions."""
        return REGIONS

    # Years reference data
    @router.get(
        "/reference/years",
        response_model=list[int],
        tags=["Reference"],
        summary="Get available years",
    )
    async def get_years(
        tenant_id: str = Depends(get_current_tenant),
        repo: IndicatorRepository = Depends(get_indicator_repository),
    ):
        """Get list of years with data."""
        try:
            df = repo.get_all_indicators(tenant_id)
            years = sorted(df["year"].unique().tolist())
            return [int(y) for y in years]
        except Exception:
            return list(range(2019, 2025))

    return router
