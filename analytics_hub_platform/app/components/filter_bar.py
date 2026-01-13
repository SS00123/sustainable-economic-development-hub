"""Filter bar components for consistent filtering UI."""

from __future__ import annotations

from typing import Any

import streamlit as st


def render_filter_bar(
    years: list[int] | None = None,
    quarters: list[int] | None = None,
    regions: list[str] | None = None,
    kpis: list[str] | None = None,
    default_year: int | None = None,
    default_quarter: int | None = None,
    default_region: str = "all",
    default_kpi: str | None = None,
    show_year: bool = True,
    show_quarter: bool = True,
    show_region: bool = True,
    show_kpi: bool = False,
    key_prefix: str = "filter",
) -> dict[str, Any]:
    """Render a horizontal filter bar with period, region, and KPI selectors.

    Args:
        years: List of available years
        quarters: List of available quarters (default 1-4)
        regions: List of available regions
        kpis: List of available KPIs (for KPI selector)
        default_year: Default selected year
        default_quarter: Default selected quarter
        default_region: Default selected region
        default_kpi: Default selected KPI
        show_year: Whether to show year selector
        show_quarter: Whether to show quarter selector
        show_region: Whether to show region selector
        show_kpi: Whether to show KPI selector
        key_prefix: Prefix for session state keys

    Returns:
        Dictionary with selected values: year, quarter, region, kpi
    """
    if years is None:
        years = list(range(2020, 2027))
    if quarters is None:
        quarters = [1, 2, 3, 4]
    if regions is None:
        regions = ["all"]

    # Calculate number of visible columns
    visible = sum([show_year, show_quarter, show_region, show_kpi])
    if visible == 0:
        return {}

    cols = st.columns(visible)
    col_idx = 0

    result: dict[str, Any] = {}

    if show_year:
        with cols[col_idx]:
            result["year"] = st.selectbox(
                "Year",
                options=years,
                index=years.index(default_year) if default_year in years else len(years) - 1,
                key=f"{key_prefix}_year",
            )
        col_idx += 1

    if show_quarter:
        with cols[col_idx]:
            result["quarter"] = st.selectbox(
                "Quarter",
                options=quarters,
                index=quarters.index(default_quarter) if default_quarter in quarters else 0,
                key=f"{key_prefix}_quarter",
                format_func=lambda x: f"Q{x}",
            )
        col_idx += 1

    if show_region:
        with cols[col_idx]:
            region_options = regions if "all" in regions else ["all"] + regions
            result["region"] = st.selectbox(
                "Region",
                options=region_options,
                index=region_options.index(default_region) if default_region in region_options else 0,
                key=f"{key_prefix}_region",
                format_func=lambda x: "All Regions" if x == "all" else x,
            )
        col_idx += 1

    if show_kpi and kpis:
        with cols[col_idx]:
            result["kpi"] = st.selectbox(
                "KPI",
                options=kpis,
                index=kpis.index(default_kpi) if default_kpi in kpis else 0,
                key=f"{key_prefix}_kpi",
            )

    return result


def render_period_selector(
    years: list[int] | None = None,
    quarters: list[int] | None = None,
    default_year: int | None = None,
    default_quarter: int | None = None,
    key_prefix: str = "period",
) -> tuple[int, int]:
    """Render a compact period selector (year + quarter).

    Returns:
        Tuple of (year, quarter)
    """
    result = render_filter_bar(
        years=years,
        quarters=quarters,
        default_year=default_year,
        default_quarter=default_quarter,
        show_year=True,
        show_quarter=True,
        show_region=False,
        show_kpi=False,
        key_prefix=key_prefix,
    )
    return result.get("year", 2025), result.get("quarter", 1)


__all__ = [
    "render_filter_bar",
    "render_period_selector",
]
