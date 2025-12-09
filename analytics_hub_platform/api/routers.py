"""
API Routers
Sustainable Economic Development Analytics Hub
Ministry of Economy and Planning

FastAPI route definitions for REST API endpoints.
"""

import logging
from typing import Optional, List
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from analytics_hub_platform.api.dependencies import (
    get_current_tenant,
    get_indicator_repository,
    get_filters,
    get_pagination,
    require_analyst,
    FilterDependency,
    PaginationParams,
    IndicatorRepository,
)
from analytics_hub_platform.domain.models import FilterParams
from analytics_hub_platform.domain.services import (
    get_sustainability_summary,
    get_data_quality_metrics,
)
from analytics_hub_platform.config.config import get_config, REGIONS


# Response Models
class HealthResponse(BaseModel):
    """Health check response."""
    status: str = "ok"
    timestamp: str
    version: str


class IndicatorResponse(BaseModel):
    """Single indicator record response."""
    id: int
    tenant_id: str
    year: int
    quarter: int
    region: str
    sustainability_index: Optional[float] = None
    co2_per_gdp: Optional[float] = None
    co2_per_capita: Optional[float] = None
    renewable_energy_pct: Optional[float] = None
    green_investment_pct: Optional[float] = None
    gdp_growth: Optional[float] = None
    employment_rate: Optional[float] = None
    data_quality_score: Optional[float] = None


class IndicatorListResponse(BaseModel):
    """Paginated list of indicators."""
    data: List[IndicatorResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class SustainabilitySummaryResponse(BaseModel):
    """Sustainability summary response."""
    sustainability_index: float
    sustainability_trend: float
    co2_per_gdp: float
    co2_per_capita: float
    renewable_energy_pct: float
    green_investment_pct: float
    data_quality_score: float
    period: str
    region: Optional[str] = None


class RegionalComparisonResponse(BaseModel):
    """Regional comparison item."""
    region: str
    sustainability_index: float
    rank: int


class TimeSeriesPoint(BaseModel):
    """Time series data point."""
    period: str
    value: float


class TimeSeriesResponse(BaseModel):
    """Time series response."""
    indicator: str
    data: List[TimeSeriesPoint]


class DataQualityResponse(BaseModel):
    """Data quality metrics response."""
    completeness: float
    avg_quality_score: float
    records_count: int
    last_update: Optional[str] = None
    missing_by_kpi: dict


class ErrorResponse(BaseModel):
    """Error response."""
    detail: str
    code: Optional[str] = None
    error_type: Optional[str] = None


logger = logging.getLogger(__name__)


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
            timestamp=datetime.utcnow().isoformat(),
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
            df_page = df.iloc[pagination.offset:pagination.offset + pagination.limit]
            
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
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e),
            )
    
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
        region: Optional[str] = Query(default=None),
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
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e),
            )
    
    # Regional comparison
    @router.get(
        "/sustainability/regions",
        response_model=List[RegionalComparisonResponse],
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
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e),
            )
    
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
        region: Optional[str] = Query(default=None),
        repo: IndicatorRepository = Depends(get_indicator_repository),
    ):
        """
        Get time series data for a specific indicator.
        """
        valid_indicators = [
            "sustainability_index", "co2_per_gdp", "co2_per_capita",
            "renewable_energy_pct", "green_investment_pct", "gdp_growth",
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
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e),
            )
    
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
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e),
            )
    
    # Regions reference data
    @router.get(
        "/reference/regions",
        response_model=List[str],
        tags=["Reference"],
        summary="Get list of regions",
    )
    async def get_regions():
        """Get list of Saudi regions."""
        return REGIONS
    
    # Years reference data
    @router.get(
        "/reference/years",
        response_model=List[int],
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
