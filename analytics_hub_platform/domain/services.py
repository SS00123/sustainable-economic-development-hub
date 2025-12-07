"""
Domain Services
Sustainable Economic Development Analytics Hub
Ministry of Economy and Planning

This module contains business services that orchestrate
domain logic and data access for specific use cases.
Services are the primary interface for UI and API layers.
"""

from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime

import pandas as pd
import yaml
from pathlib import Path

from analytics_hub_platform.domain.models import (
    FilterParams,
    KPIStatus,
    SummaryMetrics,
    TimeSeriesPoint,
    RegionalComparison,
    IndicatorRecord,
    KPIThresholds,
)
from analytics_hub_platform.domain.indicators import (
    calculate_sustainability_index,
    get_sustainability_breakdown,
    get_kpi_status,
    calculate_change,
    get_change_direction,
    normalize_to_100,
)


def _load_kpi_catalog() -> Dict[str, Any]:
    """Load KPI catalog from YAML file."""
    catalog_path = Path(__file__).parent.parent / "config" / "kpi_catalog.yaml"
    if catalog_path.exists():
        with open(catalog_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    return {"kpis": []}


def _get_kpi_thresholds(kpi_id: str, catalog: Dict[str, Any]) -> Optional[KPIThresholds]:
    """Get thresholds for a specific KPI from catalog."""
    for kpi in catalog.get("kpis", []):
        if kpi.get("id") == kpi_id and kpi.get("thresholds"):
            return KPIThresholds(**kpi["thresholds"])
    return None


def _get_kpi_higher_is_better(kpi_id: str, catalog: Dict[str, Any]) -> bool:
    """Get higher_is_better flag for a specific KPI from catalog."""
    for kpi in catalog.get("kpis", []):
        if kpi.get("id") == kpi_id:
            return kpi.get("higher_is_better", True)
    return True


def get_executive_snapshot(
    df: pd.DataFrame,
    filters: FilterParams,
    language: str = "en"
) -> Dict[str, Any]:
    """
    Get executive-level snapshot of key indicators.
    
    This is the primary data source for the Executive View dashboard,
    providing a high-level overview suitable for ministers and executives.
    
    Args:
        df: DataFrame with indicator data
        filters: Filter parameters
        language: Display language ("en" or "ar")
        
    Returns:
        Dictionary with key metrics and their statuses
    """
    catalog = _load_kpi_catalog()
    
    # Get current period data
    current = df[
        (df["year"] == filters.year) & 
        (df["quarter"] == filters.quarter)
    ]
    
    if filters.region and filters.region != "all":
        current = current[current["region"] == filters.region]
    
    # Get previous period for comparison
    prev_year = filters.year
    prev_quarter = filters.quarter - 1
    if prev_quarter == 0:
        prev_quarter = 4
        prev_year -= 1
    
    previous = df[
        (df["year"] == prev_year) & 
        (df["quarter"] == prev_quarter)
    ]
    
    if filters.region and filters.region != "all":
        previous = previous[previous["region"] == filters.region]
    
    # Aggregate current period
    if len(current) > 0:
        current_agg = current.mean(numeric_only=True)
    else:
        current_agg = pd.Series()
    
    if len(previous) > 0:
        previous_agg = previous.mean(numeric_only=True)
    else:
        previous_agg = pd.Series()
    
    # Build snapshot
    key_kpis = [
        "sustainability_index",
        "gdp_growth",
        "renewable_share",
        "co2_index",
        "green_jobs",
        "unemployment_rate",
        "data_quality_score",
        "export_diversity_index",
        "water_efficiency",
        "air_quality_index",
    ]
    
    snapshot = {
        "period": f"Q{filters.quarter} {filters.year}",
        "comparison_period": f"Q{prev_quarter} {prev_year}",
        "metrics": {},
        "top_improvements": [],
        "top_deteriorations": [],
    }
    
    changes = []
    
    for kpi_id in key_kpis:
        current_val = current_agg.get(kpi_id)
        previous_val = previous_agg.get(kpi_id)
        
        if pd.isna(current_val):
            current_val = None
        else:
            current_val = round(float(current_val), 2)
        
        if pd.isna(previous_val):
            previous_val = None
        else:
            previous_val = round(float(previous_val), 2)
        
        abs_change, pct_change = calculate_change(current_val, previous_val)
        
        thresholds = _get_kpi_thresholds(kpi_id, catalog)
        higher_is_better = _get_kpi_higher_is_better(kpi_id, catalog)
        status = get_kpi_status(current_val, thresholds, higher_is_better)
        
        # Get display name from catalog
        display_name = kpi_id
        for kpi in catalog.get("kpis", []):
            if kpi.get("id") == kpi_id:
                name_key = f"display_name_{language}"
                display_name = kpi.get(name_key, kpi.get("display_name_en", kpi_id))
                break
        
        metric = {
            "value": current_val,
            "previous_value": previous_val,
            "change": abs_change,
            "change_percent": pct_change,
            "status": status.value,
            "display_name": display_name,
            "higher_is_better": higher_is_better,
        }
        
        snapshot["metrics"][kpi_id] = metric
        
        # Track changes for improvements/deteriorations
        if pct_change is not None:
            direction = get_change_direction(abs_change, higher_is_better)
            changes.append({
                "kpi_id": kpi_id,
                "display_name": display_name,
                "change_percent": pct_change,
                "direction": direction,
            })
    
    # Sort by change magnitude
    improvements = [c for c in changes if c["direction"] == "positive"]
    deteriorations = [c for c in changes if c["direction"] == "negative"]
    
    improvements.sort(key=lambda x: abs(x["change_percent"]), reverse=True)
    deteriorations.sort(key=lambda x: abs(x["change_percent"]), reverse=True)
    
    snapshot["top_improvements"] = improvements[:3]
    snapshot["top_deteriorations"] = deteriorations[:3]
    
    return snapshot


def get_sustainability_summary(
    df: pd.DataFrame,
    filters: FilterParams,
    language: str = "en"
) -> Dict[str, Any]:
    """
    Get detailed sustainability index breakdown.
    
    Args:
        df: DataFrame with indicator data
        filters: Filter parameters
        language: Display language
        
    Returns:
        Dictionary with sustainability index and component breakdown
    """
    catalog = _load_kpi_catalog()
    
    # Get current period data
    current = df[
        (df["year"] == filters.year) & 
        (df["quarter"] == filters.quarter)
    ]
    
    if filters.region and filters.region != "all":
        current = current[current["region"] == filters.region]
    
    if len(current) == 0:
        return {"index": None, "breakdown": [], "status": "unknown"}
    
    # Aggregate across regions if needed
    indicators = current.mean(numeric_only=True).to_dict()
    
    # Calculate index
    sustainability_index = calculate_sustainability_index(indicators, catalog)
    
    # Get breakdown
    breakdown = get_sustainability_breakdown(indicators, catalog)
    
    # Localize names
    name_key = f"name_{language}"
    for item in breakdown:
        item["name"] = item.get(name_key, item.get("name_en"))
    
    # Get status
    thresholds = _get_kpi_thresholds("sustainability_index", catalog)
    status = get_kpi_status(sustainability_index, thresholds, True)
    
    return {
        "index": sustainability_index,
        "breakdown": breakdown,
        "status": status.value,
        "period": f"Q{filters.quarter} {filters.year}",
    }


def get_kpi_timeseries(
    df: pd.DataFrame,
    kpi_id: str,
    filters: FilterParams,
    years: Optional[List[int]] = None
) -> List[TimeSeriesPoint]:
    """
    Get time series data for a specific KPI.
    
    Args:
        df: DataFrame with indicator data
        kpi_id: The KPI identifier
        filters: Filter parameters
        years: Optional list of years to include
        
    Returns:
        List of TimeSeriesPoint objects
    """
    catalog = _load_kpi_catalog()
    
    # Filter data
    data = df.copy()
    
    if filters.region and filters.region != "all":
        data = data[data["region"] == filters.region]
    
    if years:
        data = data[data["year"].isin(years)]
    
    if len(data) == 0:
        return []
    
    # Aggregate by year/quarter
    grouped = data.groupby(["year", "quarter"]).agg({kpi_id: "mean"}).reset_index()
    grouped = grouped.sort_values(["year", "quarter"])
    
    thresholds = _get_kpi_thresholds(kpi_id, catalog)
    higher_is_better = _get_kpi_higher_is_better(kpi_id, catalog)
    
    timeseries = []
    for _, row in grouped.iterrows():
        value = row[kpi_id]
        if pd.isna(value):
            continue
        
        value = round(float(value), 2)
        status = get_kpi_status(value, thresholds, higher_is_better)
        
        timeseries.append(TimeSeriesPoint(
            period=f"{int(row['year'])}-Q{int(row['quarter'])}",
            value=value,
            status=status,
        ))
    
    return timeseries


def get_regional_comparison(
    df: pd.DataFrame,
    kpi_id: str,
    filters: FilterParams,
    language: str = "en"
) -> RegionalComparison:
    """
    Get regional comparison for a specific KPI.
    
    Args:
        df: DataFrame with indicator data
        kpi_id: The KPI identifier
        filters: Filter parameters
        language: Display language
        
    Returns:
        RegionalComparison object
    """
    catalog = _load_kpi_catalog()
    
    # Filter to current period
    data = df[
        (df["year"] == filters.year) & 
        (df["quarter"] == filters.quarter)
    ]
    
    if len(data) == 0:
        return RegionalComparison(
            kpi_id=kpi_id,
            kpi_name=kpi_id,
            regions=[],
            values=[],
            statuses=[],
            national_average=0.0,
        )
    
    # Aggregate by region
    grouped = data.groupby("region").agg({kpi_id: "mean"}).reset_index()
    grouped = grouped.sort_values(kpi_id, ascending=False)
    
    thresholds = _get_kpi_thresholds(kpi_id, catalog)
    higher_is_better = _get_kpi_higher_is_better(kpi_id, catalog)
    
    # Get display name
    display_name = kpi_id
    for kpi in catalog.get("kpis", []):
        if kpi.get("id") == kpi_id:
            name_key = f"display_name_{language}"
            display_name = kpi.get(name_key, kpi.get("display_name_en", kpi_id))
            break
    
    regions = []
    values = []
    statuses = []
    
    for _, row in grouped.iterrows():
        value = row[kpi_id]
        if pd.isna(value):
            continue
        
        value = round(float(value), 2)
        status = get_kpi_status(value, thresholds, higher_is_better)
        
        regions.append(row["region"])
        values.append(value)
        statuses.append(status)
    
    national_avg = sum(values) / len(values) if values else 0.0
    
    return RegionalComparison(
        kpi_id=kpi_id,
        kpi_name=display_name,
        regions=regions,
        values=values,
        statuses=statuses,
        national_average=round(national_avg, 2),
    )


def get_data_quality_metrics(
    df: pd.DataFrame,
    filters: FilterParams
) -> Dict[str, Any]:
    """
    Get data quality metrics for analyst view.
    
    Args:
        df: DataFrame with indicator data
        filters: Filter parameters
        
    Returns:
        Dictionary with data quality metrics
    """
    # Filter to current period
    data = df[
        (df["year"] == filters.year) & 
        (df["quarter"] == filters.quarter)
    ]
    
    if filters.region and filters.region != "all":
        data = data[data["region"] == filters.region]
    
    if len(data) == 0:
        return {
            "completeness": 0.0,
            "records_count": 0,
            "missing_by_kpi": {},
            "last_update": None,
        }
    
    # Calculate completeness
    kpi_columns = [
        "gdp_growth", "gdp_total", "foreign_investment", "export_diversity_index",
        "economic_complexity", "unemployment_rate", "green_jobs", "skills_gap_index",
        "social_progress_score", "digital_readiness", "innovation_index",
        "co2_index", "co2_total", "renewable_share", "energy_intensity",
        "water_efficiency", "waste_recycling_rate", "forest_coverage", "air_quality_index",
    ]
    
    available_columns = [c for c in kpi_columns if c in data.columns]
    
    total_cells = len(data) * len(available_columns)
    missing_cells = data[available_columns].isna().sum().sum()
    completeness = ((total_cells - missing_cells) / total_cells * 100) if total_cells > 0 else 0.0
    
    # Missing by KPI
    missing_by_kpi = {}
    for col in available_columns:
        missing_count = data[col].isna().sum()
        total_count = len(data)
        missing_by_kpi[col] = {
            "missing": int(missing_count),
            "total": int(total_count),
            "percent": round((missing_count / total_count) * 100, 1) if total_count > 0 else 0,
        }
    
    # Last update
    last_update = None
    if "load_timestamp" in data.columns:
        timestamps = data["load_timestamp"].dropna()
        if len(timestamps) > 0:
            last_update = timestamps.max()
    
    # Average data quality score
    avg_quality = data["data_quality_score"].mean() if "data_quality_score" in data.columns else None
    if pd.notna(avg_quality):
        avg_quality = round(float(avg_quality), 1)
    
    return {
        "completeness": round(completeness, 1),
        "records_count": len(data),
        "missing_by_kpi": missing_by_kpi,
        "last_update": last_update,
        "avg_quality_score": avg_quality,
    }


def get_available_periods(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Get list of available time periods in the data.
    
    Args:
        df: DataFrame with indicator data
        
    Returns:
        List of period dictionaries with year, quarter, and label
    """
    if len(df) == 0:
        return []
    
    periods = df[["year", "quarter"]].drop_duplicates()
    periods = periods.sort_values(["year", "quarter"], ascending=False)
    
    result = []
    for _, row in periods.iterrows():
        result.append({
            "year": int(row["year"]),
            "quarter": int(row["quarter"]),
            "label": f"Q{int(row['quarter'])} {int(row['year'])}",
        })
    
    return result


def get_available_regions(df: pd.DataFrame) -> List[str]:
    """
    Get list of available regions in the data.
    
    Args:
        df: DataFrame with indicator data
        
    Returns:
        List of region names
    """
    if len(df) == 0:
        return []
    
    return sorted(df["region"].unique().tolist())
