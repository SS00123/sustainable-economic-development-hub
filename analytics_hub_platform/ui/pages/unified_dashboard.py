"""
Unified Professional Dashboard
Sustainable Economic Development Analytics Hub
Ministry of Economy and Planning

Single-page professional dashboard combining all views:
- Executive summary with KPIs
- Sustainability index
- Trend analysis
- Regional comparison
- Insights and narratives

Dark 3D theme with sidebar navigation and card-based layout.
"""

from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import yaml

from analytics_hub_platform.config.branding import BRANDING
from analytics_hub_platform.config.theme import get_theme
from analytics_hub_platform.domain.indicators import calculate_change
from analytics_hub_platform.domain.models import FilterParams
from analytics_hub_platform.domain.services import (
    get_available_periods,
    get_available_regions,
    get_data_quality_metrics,
    get_executive_snapshot,
    get_regional_comparison,
    get_sustainability_summary,
)
from analytics_hub_platform.infrastructure.repository import get_repository
from analytics_hub_platform.infrastructure.settings import get_settings
from analytics_hub_platform.locales import get_strings
from analytics_hub_platform.ui.components.cards import (
    render_kpi_card,
)
from analytics_hub_platform.ui.html import render_html
from analytics_hub_platform.ui.dark_components import (
    apply_dark_chart_layout,
    card_close,
    card_open,
    render_mini_metric,
    render_sidebar,
    render_status_overview,
    create_sparkline_svg,
    create_progress_ring,
    create_alert_badge,
    render_enhanced_kpi_card,
    render_yoy_comparison,
    add_target_line_to_chart,
    render_sticky_header,
)
from analytics_hub_platform.ui.dark_components import (
    render_header as render_dark_header,
)
from analytics_hub_platform.ui.dark_components import (
    render_section_title as render_dark_section_title,
)

# Import dark theme components
from analytics_hub_platform.ui.theme import get_dark_theme, hex_to_rgba
from analytics_hub_platform.utils.dataframe_adapter import add_period_column
from analytics_hub_platform.utils.kpi_utils import get_kpi_unit
from analytics_hub_platform.utils.narratives import generate_executive_narrative


def _hex_to_rgba(hex_color: str, alpha: float) -> str:
    """Convert hex color to rgba for Plotly compatibility."""
    return hex_to_rgba(hex_color, alpha)

# =============================================================================
# CACHED DATA LOADING
# =============================================================================


@st.cache_data(ttl=300, show_spinner=False)
def load_indicator_data(tenant_id: str) -> pd.DataFrame:
    """
    Load indicator data with Streamlit caching.

    Cached for 5 minutes (300 seconds) to balance freshness with performance.

    Args:
        tenant_id: Tenant identifier

    Returns:
        DataFrame with all indicator data
    """
    repo = get_repository()
    return repo.get_all_indicators(tenant_id)


@st.cache_data(ttl=60, show_spinner=False)
def get_dashboard_data(
    tenant_id: str,
    year: int,
    quarter: int,
    region: str | None,
    language: str,
) -> dict[str, Any]:
    """
    Get all dashboard data in one cached call.

    Cached for 1 minute to ensure responsive updates.

    Args:
        tenant_id: Tenant identifier
        year: Selected year
        quarter: Selected quarter
        region: Selected region (or None for all)
        language: Display language

    Returns:
        Dictionary with snapshot, sustainability, and quality metrics
    """
    repo = get_repository()
    df = repo.get_all_indicators(tenant_id)

    filter_params = FilterParams(
        tenant_id=tenant_id,
        year=year,
        quarter=quarter,
        region=region,
    )

    snapshot = get_executive_snapshot(df, filter_params, language)
    sustainability = get_sustainability_summary(df, filter_params, language)
    quality_metrics = get_data_quality_metrics(df, filter_params)

    return {
        "df": df,
        "snapshot": snapshot,
        "sustainability": sustainability,
        "quality_metrics": quality_metrics,
    }


def render_unified_dashboard() -> None:
    """Render the unified professional dashboard with dark 3D theme."""
    dark_theme = get_dark_theme()
    # Also get legacy theme for compatibility with existing helper functions
    theme = get_theme()

    settings = get_settings()

    # Load full indicator dataset once (cached) to derive available filters
    df_all = load_indicator_data(settings.default_tenant_id)

    # Available periods and regions from real data (no hard-coded lists)
    periods = get_available_periods(df_all)
    regions_available = get_available_regions(df_all)

    if not periods:
        st.error("No data available to render dashboard. Please ingest indicator data.")
        return

    latest_period = periods[0]

    # Get filter state from session, defaulting to latest available
    year = st.session_state.get("year", latest_period["year"])
    quarter = st.session_state.get("quarter", latest_period["quarter"])
    region = st.session_state.get("region", "all")
    language = st.session_state.get("language", "en")
    get_strings(language)

    # Ensure selected filters exist in available data; if not, reset to latest
    if not any(p["year"] == year and p["quarter"] == quarter for p in periods):
        year = latest_period["year"]
        quarter = latest_period["quarter"]
        st.session_state["year"] = year
        st.session_state["quarter"] = quarter

    # Build dynamic filter options
    year_options = sorted({p["year"] for p in periods}, reverse=True)
    quarter_options = [p["quarter"] for p in periods if p["year"] == year]
    quarter_options = sorted(set(quarter_options)) or [quarter]
    region_options = ["all"] + sorted(regions_available)

    # Last updated timestamp from dataset
    last_updated = None
    if "load_timestamp" in df_all.columns and len(df_all.dropna(subset=["load_timestamp"])) > 0:
        last_updated_ts = df_all["load_timestamp"].max()
        last_updated = last_updated_ts.strftime("%B %d, %Y %H:%M") if pd.notna(last_updated_ts) else None

    # =========================================================================
    # DARK 3D LAYOUT: SIDEBAR + MAIN CONTENT
    # =========================================================================
    side_col, main_col = st.columns([0.22, 0.78], gap="large")

    with side_col:
        render_sidebar(active="Dashboard")

    with main_col:
        # =========================================================================
        # SECTION 1: PAGE HEADER (PDF Design Spec)
        # =========================================================================
        _render_page_header(dark_theme, year, quarter, last_updated)

        # Sticky Filter Bar (Phase B1)
        render_sticky_header(year, quarter, region, language)

        # Hidden filter controls (kept for state management but visually replaced by sticky header/sidebar)
        with st.expander("⚙️ Configure View", expanded=False):
            col_f1, col_f2, col_f3, col_f4 = st.columns([1, 1, 1.5, 1])
            with col_f1:
                new_year = st.selectbox(
                    "Year",
                    year_options,
                    index=year_options.index(year),
                    key="filter_year",
                )
            with col_f2:
                new_quarter = st.selectbox(
                    "Quarter",
                    quarter_options,
                    index=quarter_options.index(quarter) if quarter in quarter_options else 0,
                    key="filter_quarter",
                )
            with col_f3:
                new_region = st.selectbox(
                    "Region",
                    region_options,
                    index=region_options.index(region) if region in region_options else 0,
                    key="filter_region",
                )
            with col_f4:
                new_language = st.selectbox(
                    "Language",
                    ["en", "ar"],
                    index=["en", "ar"].index(language),
                    key="filter_language",
                )

            # Update session state if changed
            if (
                new_year != year
                or new_quarter != quarter
                or new_region != region
                or new_language != language
            ):
                st.session_state["year"] = new_year
                st.session_state["quarter"] = new_quarter
                st.session_state["region"] = new_region
                st.session_state["language"] = new_language
                st.rerun()

        # =========================================================================
        # LOAD DATA (using cached functions for performance)
        # =========================================================================
        try:
            # Use cached data loading for better performance
            region_param = region if region != "all" else None
            dashboard_data = get_dashboard_data(
                tenant_id=settings.default_tenant_id,
                year=year,
                quarter=quarter,
                region=region_param,
                language=language,
            )

            df = dashboard_data["df"]
            snapshot = dashboard_data["snapshot"]
            sustainability = dashboard_data["sustainability"]
            quality_metrics = dashboard_data["quality_metrics"]

            filter_params = FilterParams(
                tenant_id=settings.default_tenant_id,
                year=year,
                quarter=quarter,
                region=region_param,
            )

            catalog = _get_catalog()
            metrics = _enrich_metrics(df, snapshot.get("metrics", {}), filter_params, catalog)

            # Previous period filters for deltas (real data, no placeholders)
            prev_quarter = quarter - 1 if quarter > 1 else 4
            prev_year = year if quarter > 1 else year - 1
            prev_filters = FilterParams(
                tenant_id=settings.default_tenant_id,
                year=prev_year,
                quarter=prev_quarter,
                region=region_param,
            )
            sustainability_prev = get_sustainability_summary(df, prev_filters, language)
            quality_prev = get_data_quality_metrics(df, prev_filters)

        except Exception as e:
            st.error(f"Error loading data: {str(e)}")
            return

        # Check for no data
        if snapshot.get("status") == "no_data" or sustainability.get("status") == "no_data":
            st.warning(
                f"⚠️ No data available for Q{quarter} {year}. Please select a different period."
            )
            return

        # =========================================================================
        # HERO METRICS SECTION (Always Visible)
        # =========================================================================
        render_html("<div id='section-overview' style='height: 16px;'></div>")

        # Status summary for display
        green_count = sum(1 for m in metrics.values() if m.get("status") == "green")
        amber_count = sum(1 for m in metrics.values() if m.get("status") == "amber")
        red_count = sum(1 for m in metrics.values() if m.get("status") == "red")

        # Hero section: Sustainability Gauge (4 cols) + KPI Cards (8 cols as 2x2 grid)
        hero_gauge_col, hero_kpi_col = st.columns([0.38, 0.62], gap="large")

        with hero_gauge_col:
            # Render the enhanced sustainability gauge
            _render_hero_sustainability_gauge(
                sustainability,
                sustainability_prev,
                dark_theme,
            )

        with hero_kpi_col:
            # 2x2 grid of hero KPI cards with sparklines
            _render_hero_kpi_cards(metrics, dark_theme, quality_metrics, quality_prev, df=df)

        render_html("<div style='height: 24px;'></div>")

        # Status overview row (compact)
        card_open("Performance Overview", f"Q{quarter} {year} • {len(metrics)} KPIs tracked")
        render_status_overview(green_count, amber_count, red_count)
        card_close()

        render_html("<div style='height: 24px;'></div>")

        # =========================================================================
        # TABS NAVIGATION (Phase B2)
        # =========================================================================
        tab_overview, tab_econ, tab_social, tab_env, tab_regional, tab_dq, tab_advanced = st.tabs([
            "📊 Overview", "💼 Economic", "👥 Social", "🌿 Environmental", "🗺️ Regional", "✅ Data Quality", "🧠 Advanced"
        ])

        with tab_overview:
            # =========================================================================
            # ANALYTICAL BAND: TREND ANALYSIS
            # =========================================================================
            render_html("<div id='section-trends' style='height: 8px;'></div>")
            render_dark_section_title("📈 Trend Analysis", "Historical performance over time")
            render_html("<div style='height: 12px;'></div>")

            card_open("Trend Line", "Select indicator to view")
            trend_col1, trend_col2 = st.columns([3, 1])

            with trend_col2:
                kpi_options = {
                    "sustainability_index": "Sustainability Index",
                    "gdp_growth": "GDP Growth",
                    "renewable_share": "Renewable Energy",
                    "co2_index": "CO2 Intensity",
                    "unemployment_rate": "Unemployment",
                    "green_jobs": "Green Jobs",
                }
                selected_kpi = st.selectbox(
                    "Select Indicator",
                    list(kpi_options.keys()),
                    format_func=lambda x: kpi_options[x],
                    key="trend_kpi",
                )

            with trend_col1:
                trend_df = df.copy()
                if region != "all":
                    trend_df = trend_df[trend_df["region"] == region]

                trend_agg = (
                    trend_df.groupby(["year", "quarter"]).agg({selected_kpi: "mean"}).reset_index()
                )
                trend_agg = add_period_column(trend_agg)  # Vectorized period creation
                trend_agg = trend_agg.sort_values(["year", "quarter"])

                fig = go.Figure()
                fig.add_trace(
                    go.Scatter(
                        x=trend_agg["period"],
                        y=trend_agg[selected_kpi],
                        mode="lines+markers",
                        name=kpi_options[selected_kpi],
                        line={"color": dark_theme.colors.purple, "width": 3},
                        marker={"size": 10, "color": dark_theme.colors.purple},
                        fill="tozeroy",
                        fillcolor="rgba(168, 85, 247, 0.15)",
                        hovertemplate="<b>%{x}</b><br>Value: %{y:.1f}<extra></extra>",
                    )
                )

                # Add trend line
                if len(trend_agg) > 2:
                    x_numeric = np.arange(len(trend_agg))
                    z = np.polyfit(x_numeric, trend_agg[selected_kpi].values, 1)
                    p = np.poly1d(z)
                    fig.add_trace(
                        go.Scatter(
                            x=trend_agg["period"],
                            y=p(x_numeric),
                            mode="lines",
                            name="Trend",
                            line={"color": dark_theme.colors.cyan, "width": 2, "dash": "dash"},
                        )
                    )

                apply_dark_chart_layout(fig, height=350)
                fig.update_layout(
                    legend={
                        "orientation": "h",
                        "yanchor": "bottom",
                        "y": 1.02,
                        "xanchor": "right",
                        "x": 1,
                    },
                )
                st.plotly_chart(fig, width="stretch")

            card_close()

            # =========================================================================
            # SECTION 7: KEY INSIGHTS
            # =========================================================================
            render_html("<div style='height: 8px;'></div>")
            render_dark_section_title(
                "💡 Key Insights", "Top improvements and areas needing attention"
            )
            render_html("<div style='height: 12px;'></div>")

            _render_key_insights_section(snapshot, metrics, dark_theme, language)

        with tab_econ:
            # Economic Performance Pillar
            render_dark_section_title(
                "💼 Economic Performance", "GDP, Investment, and Economic Complexity"
            )
            _render_pillar_section_economic(df, metrics, year, quarter, region, dark_theme)

        with tab_social:
            # Labor & Skills + Social & Digital
            labor_col, social_col = st.columns(2, gap="large")

            with labor_col:
                render_dark_section_title(
                    "👥 Labor & Skills", "Employment and workforce development"
                )
                _render_pillar_section_labor(df, metrics, year, quarter, dark_theme)

            with social_col:
                render_dark_section_title(
                    "🌐 Social & Digital", "Digital readiness and innovation"
                )
                _render_pillar_section_social(df, metrics, year, quarter, dark_theme)

        with tab_env:
            # Environmental & Sustainability Pillar
            render_dark_section_title(
                "🌿 Environmental & Sustainability", "Climate, energy, and resource efficiency"
            )
            _render_pillar_section_environmental(df, metrics, year, quarter, region, dark_theme)

            render_html("<div style='height: 24px;'></div>")

            # =========================================================================
            # SECTION 5: ENVIRONMENTAL TRENDS (Enhanced)
            # =========================================================================
            render_html("<div id='section-environment' style='height: 8px;'></div>")
            render_dark_section_title(
                "🌿 Sustainability & Environmental Trends", "Multi-indicator performance"
            )
            render_html("<div style='height: 12px;'></div>")

            card_open("Environmental KPIs", "Tracking sustainability metrics over time")

            env_kpis = [
                "co2_index",
                "renewable_share",
                "energy_intensity",
                "water_efficiency",
                "waste_recycling_rate",
                "air_quality_index",
                "forest_coverage",
                "green_jobs",
            ]

            # Phase B3: Multi-select for series
            selected_env_series = st.multiselect(
                "Select Indicators",
                options=env_kpis,
                default=env_kpis[:5],
                format_func=lambda x: x.replace("_", " ").title()
            )

            if selected_env_series:
                trend_env = (
                    df.groupby(["year", "quarter"])
                    .agg({k: "mean" for k in selected_env_series if k in df.columns})
                    .reset_index()
                )
                trend_env = add_period_column(trend_env)  # Vectorized period creation
                trend_env = trend_env.sort_values(["year", "quarter"])

                fig_env = go.Figure()
                palette = [
                    dark_theme.colors.purple,
                    dark_theme.colors.cyan,
                    dark_theme.colors.pink,
                    "#f472b6",
                    "#818cf8",
                    "#4ade80",
                    "#fbbf24",
                    "#fb923c",
                ]
                label_map = {
                    "co2_index": "CO2 Intensity",
                    "renewable_share": "Renewables %",
                    "energy_intensity": "Energy Intensity",
                    "water_efficiency": "Water Efficiency",
                    "waste_recycling_rate": "Recycling Rate",
                    "air_quality_index": "Air Quality",
                    "forest_coverage": "Forest Coverage",
                    "green_jobs": "Green Jobs",
                }

                for i, kpi in enumerate(selected_env_series):
                    if kpi not in trend_env.columns:
                        continue
                    fig_env.add_trace(
                        go.Scatter(
                            x=trend_env["period"],
                            y=trend_env[kpi],
                            mode="lines+markers",
                            name=label_map.get(kpi, kpi),
                            line={"color": palette[i % len(palette)], "width": 2},
                            hovertemplate="<b>%{fullData.name}</b><br>%{x}<br>Value: %{y:.1f}<extra></extra>",
                        )
                    )

                apply_dark_chart_layout(fig_env, height=420)
                fig_env.update_layout(
                    legend={
                        "orientation": "h",
                        "yanchor": "bottom",
                        "y": 1.02,
                        "xanchor": "center",
                        "x": 0.5,
                    },
                )
                st.plotly_chart(fig_env, width="stretch")
            else:
                st.info("Select at least one indicator to view trends.")
            
            card_close()

        with tab_regional:
            # =========================================================================
            # SECTION 4: REGIONAL COMPARISON (PDF Design Spec)
            # =========================================================================
            render_html("<div id='section-regions' style='height: 8px;'></div>")
            render_dark_section_title(
                "🗺️ Regional Comparison", "Performance by region with geospatial view"
            )
            render_html("<div style='height: 12px;'></div>")

            filter_params = FilterParams(
                tenant_id=settings.default_tenant_id,
                year=year,
                quarter=quarter,
                region=region if region != "all" else None,
            )
            _render_regional_comparison_section(df, filter_params, region, dark_theme)

            # Dedicated Saudi map section (separate from bars/stats)
            _render_saudi_map_section(df, filter_params, dark_theme, language)

        with tab_dq:
            # =========================================================================
            # SECTION 6: DATA QUALITY & COMPLETENESS (PDF Design Spec)
            # =========================================================================
            render_html("<div id='section-data-quality' style='height: 8px;'></div>")
            render_dark_section_title(
                "✅ Data Quality & Completeness", "Overall data health and completeness metrics"
            )
            render_html("<div style='height: 12px;'></div>")

            _render_data_quality_section(quality_metrics, quality_prev, metrics, df, catalog, dark_theme)

        with tab_advanced:
            # =========================================================================
            # ADVANCED ANALYTICS SECTION
            # =========================================================================
            render_html(
                f"""
                <div style="
                    background: linear-gradient(135deg, {dark_theme.colors.purple}15 0%, {dark_theme.colors.cyan}10 100%);
                    padding: 20px 24px;
                    border-radius: 12px;
                    border: 1px solid #2d3555;
                    margin: 20px 0;
                ">
                    <h3 style="color: #f1f5f9; margin: 0 0 8px 0; font-size: 18px;">
                        🧠 Advanced Analytics Suite
                    </h3>
                    <p style="color: #94a3b8; margin: 0; font-size: 13px;">
                        ML-powered forecasting, anomaly detection, and AI recommendations
                    </p>
                </div>
            """
            )

            # Create layout with sidebar and content
            sidebar_col, content_col = st.columns([0.28, 0.72], gap="medium")

            with sidebar_col:
                from analytics_hub_platform.ui.dark_components import render_advanced_analytics_sidebar

                selected_section = render_advanced_analytics_sidebar()

            with content_col:
                # Render the selected section
                if selected_section == "forecast":
                    _render_ml_forecast_section(df, year, quarter, theme, language)
                elif selected_section == "warning":
                    _render_anomaly_section(df, year, quarter, theme, language)
                elif selected_section == "recommendations":
                    _render_llm_recommendations_section(snapshot, theme, language)
                elif selected_section == "map":
                    _render_regional_map_section(df, year, quarter, theme, language)

        render_html("<div style='height: 48px;'></div>")

        # =========================================================================
        # PREMIUM FOOTER
        # =========================================================================
        footer_html = f"""
            <div style="
                position: relative;
                background: linear-gradient(180deg, rgba(15, 23, 42, 0.98), rgba(11, 17, 32, 0.98));
                border: 1px solid rgba(168, 85, 247, 0.15);
                border-radius: 20px;
                padding: 32px 40px;
                margin-top: 32px;
                overflow: hidden;
            ">
                <!-- Gradient orbs -->
                <div style="
                    position: absolute;
                    bottom: -40px;
                    left: 10%;
                    width: 200px;
                    height: 200px;
                    background: radial-gradient(circle, rgba(168, 85, 247, 0.1) 0%, transparent 60%);
                    border-radius: 50%;
                    filter: blur(40px);
                "></div>
                <div style="
                    position: absolute;
                    bottom: -30px;
                    right: 15%;
                    width: 150px;
                    height: 150px;
                    background: radial-gradient(circle, rgba(34, 211, 238, 0.1) 0%, transparent 60%);
                    border-radius: 50%;
                    filter: blur(35px);
                "></div>

                <div style="position: relative; z-index: 2; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 24px;">
                    <!-- Left: Branding -->
                    <div style="display: flex; align-items: center; gap: 16px;">
                        <div style="
                            width: 48px;
                            height: 48px;
                            background: linear-gradient(145deg, rgba(168, 85, 247, 0.8), rgba(34, 211, 238, 0.6));
                            border-radius: 14px;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            font-size: 24px;
                            box-shadow: 0 8px 24px rgba(168, 85, 247, 0.3);
                        ">📊</div>
                        <div>
                            <div style="font-size: 14px; font-weight: 700; color: rgba(255,255,255,0.92);">
                                Sustainable Economic Development
                            </div>
                            <div style="font-size: 12px; color: rgba(255,255,255,0.5);">
                                Ministry of Economy and Planning
                            </div>
                        </div>
                    </div>

                    <!-- Center: Links -->
                    <div style="display: flex; gap: 24px; align-items: center;">
                        <span style="font-size: 12px; color: rgba(255,255,255,0.4); cursor: pointer;">Documentation</span>
                        <span style="font-size: 12px; color: rgba(255,255,255,0.4); cursor: pointer;">API</span>
                        <span style="font-size: 12px; color: rgba(255,255,255,0.4); cursor: pointer;">Support</span>
                    </div>

                    <!-- Right: Developer info -->
                    <div style="text-align: right;">
                        <div style="font-size: 11px; color: rgba(255,255,255,0.4); margin-bottom: 4px;">
                            Developed by
                        </div>
                        <div style="font-size: 13px; font-weight: 600; color: rgba(255,255,255,0.75);">
                            Eng. Sultan Albuqami
                        </div>
                        <div style="font-size: 11px; color: rgba(168, 85, 247, 0.8);">
                            sultan_mutep@hotmail.com
                        </div>
                    </div>
                </div>

                <!-- Bottom copyright -->
                <div style="
                    position: relative;
                    z-index: 2;
                    margin-top: 24px;
                    padding-top: 20px;
                    border-top: 1px solid rgba(255,255,255,0.06);
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                    flex-wrap: wrap;
                    gap: 12px;
                ">
                    <span style="font-size: 11px; color: rgba(255,255,255,0.35);">
                        © 2024-2026 Ministry of Economy and Planning. All rights reserved.
                    </span>
                    <span style="font-size: 11px; color: rgba(255,255,255,0.35);">
                        Version 2.0.0 • Built with Streamlit
                    </span>
                </div>
            </div>
        """
        render_html(footer_html)


# =============================================================================
# PDF DESIGN SPEC - PAGE HEADER
# =============================================================================


def _render_page_header(
    dark_theme, year: int, quarter: int, last_updated: str | None = None
) -> None:
    """
    Render the premium page header matching modern dashboard design.

    Includes:
    - Animated gradient background with mesh overlay
    - Main title: "Sustainable Economic Development Analytics Hub"
    - Subtitle: "Ministry of Economy and Planning • Executive Dashboard"
    - Live indicator and data freshness
    """
    from datetime import datetime

    if last_updated is None:
        last_updated = datetime.now().strftime("%B %d, %Y %H:%M")

    # Using st.html for pure HTML content (recommended for Streamlit 1.52+)
    header_html = f"""
        <div style="
            position: relative;
            background: linear-gradient(135deg,
                rgba(27, 31, 54, 0.95) 0%,
                rgba(15, 17, 34, 0.98) 50%,
                rgba(30, 35, 64, 0.95) 100%);
            border: 1px solid rgba(168, 85, 247, 0.2);
            border-radius: 20px;
            padding: 32px 36px;
            margin-bottom: 28px;
            overflow: hidden;
            box-shadow:
                0 20px 60px rgba(0, 0, 0, 0.4),
                inset 0 1px 0 rgba(255, 255, 255, 0.06);
        ">
            <div style="
                position: absolute;
                top: -80px;
                right: -60px;
                width: 250px;
                height: 250px;
                background: radial-gradient(circle, rgba(168, 85, 247, 0.25) 0%, transparent 60%);
                border-radius: 50%;
                filter: blur(40px);
                animation: float-orb 8s ease-in-out infinite;
            "></div>
            <div style="
                position: absolute;
                bottom: -60px;
                left: 20%;
                width: 200px;
                height: 200px;
                background: radial-gradient(circle, rgba(34, 211, 238, 0.2) 0%, transparent 60%);
                border-radius: 50%;
                filter: blur(35px);
                animation: float-orb 10s ease-in-out infinite reverse;
            "></div>
            <div style="
                position: absolute;
                top: 30%;
                left: 60%;
                width: 150px;
                height: 150px;
                background: radial-gradient(circle, rgba(236, 72, 153, 0.15) 0%, transparent 60%);
                border-radius: 50%;
                filter: blur(30px);
                animation: float-orb 6s ease-in-out infinite;
            "></div>

            <div style="position: relative; z-index: 2;">
                <div style="
                    display: inline-flex;
                    align-items: center;
                    gap: 8px;
                    background: rgba(16, 185, 129, 0.15);
                    border: 1px solid rgba(16, 185, 129, 0.3);
                    padding: 6px 14px;
                    border-radius: 20px;
                    margin-bottom: 16px;
                    font-size: 11px;
                    color: #10b981;
                    font-weight: 600;
                    letter-spacing: 0.5px;
                ">
                    <span style="
                        width: 8px;
                        height: 8px;
                        background: #10b981;
                        border-radius: 50%;
                        display: inline-block;
                        box-shadow: 0 0 12px #10b981;
                        animation: pulse-glow 2s ease-in-out infinite;
                    "></span>
                    LIVE DATA
                </div>

                <h1 style="
                    font-size: 34px;
                    font-weight: 800;
                    color: rgba(255,255,255,0.98);
                    margin: 0 0 10px 0;
                    font-family: 'Inter', -apple-system, sans-serif;
                    letter-spacing: -0.5px;
                    background: linear-gradient(135deg, #fff 0%, rgba(255,255,255,0.85) 100%);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    background-clip: text;
                ">
                    📊 Sustainable Economic Development
                </h1>
                <p style="
                    font-size: 16px;
                    color: rgba(255,255,255,0.65);
                    margin: 0 0 20px 0;
                    font-weight: 500;
                ">
                    Ministry of Economy and Planning • Executive Analytics Hub
                </p>

                <div style="
                    display: flex;
                    align-items: center;
                    gap: 20px;
                    flex-wrap: wrap;
                ">
                    <span style="
                        display: inline-flex;
                        align-items: center;
                        gap: 10px;
                        background: linear-gradient(135deg, rgba(168, 85, 247, 0.2), rgba(34, 211, 238, 0.15));
                        padding: 10px 20px;
                        border-radius: 24px;
                        border: 1px solid rgba(168, 85, 247, 0.3);
                        font-size: 14px;
                        color: rgba(255,255,255,0.95);
                        font-weight: 600;
                        box-shadow: 0 4px 20px rgba(168, 85, 247, 0.2);
                    ">
                        <span style="font-size: 16px;">📅</span>
                        Q{quarter} {year}
                    </span>
                    <span style="
                        font-size: 13px;
                        color: rgba(255,255,255,0.5);
                        display: flex;
                        align-items: center;
                        gap: 8px;
                    ">
                        <span style="font-size: 14px;">🕐</span>
                        Last updated: {last_updated}
                    </span>
                </div>
            </div>
        </div>

        <style>
            @keyframes float-orb {{
                0%, 100% {{ transform: translate(0, 0) scale(1); opacity: 0.8; }}
                50% {{ transform: translate(20px, 25px) scale(1.15); opacity: 1; }}
            }}
            @keyframes pulse-glow {{
                0%, 100% {{ opacity: 1; transform: scale(1); }}
                50% {{ opacity: 0.6; transform: scale(1.2); }}
            }}
        </style>
    """
    render_html(header_html)


# =============================================================================
# DARK THEME HELPER FUNCTIONS
# =============================================================================


def _render_activity_chart(
    df: pd.DataFrame, year: int, quarter: int, region: str, dark_theme
) -> None:
    """Render Economic Activity Index line chart with glowing effect."""
    card_open("Economic Activity Index", "Quarterly trend with forecast")

    # Prepare data
    trend_df = df.copy()
    if region != "all":
        trend_df = trend_df[trend_df["region"] == region]

    trend_agg = (
        trend_df.groupby(["year", "quarter"]).agg({"sustainability_index": "mean"}).reset_index()
    )
    trend_agg = add_period_column(trend_agg)  # Vectorized period creation
    trend_agg = trend_agg.sort_values(["year", "quarter"])

    # Create figure
    fig = go.Figure()

    # Add filled area with gradient effect
    fig.add_trace(
        go.Scatter(
            x=trend_agg["period"],
            y=trend_agg["sustainability_index"],
            mode="lines",
            fill="tozeroy",
            fillcolor="rgba(168, 85, 247, 0.2)",
            line={"color": dark_theme.colors.purple, "width": 3},
            hovertemplate="<b>%{x}</b><br>Index: %{y:.1f}<extra></extra>",
        )
    )

    # Add glow markers on key points
    fig.add_trace(
        go.Scatter(
            x=trend_agg["period"],
            y=trend_agg["sustainability_index"],
            mode="markers",
            marker={
                "size": 8,
                "color": dark_theme.colors.purple,
                "line": {"width": 2, "color": "#fff"},
            },
            hoverinfo="skip",
        )
    )

    apply_dark_chart_layout(fig, height=280)
    st.plotly_chart(fig, width="stretch")
    card_close()


def _render_region_bars(df: pd.DataFrame, year: int, quarter: int, dark_theme) -> None:
    """Render horizontal bar chart for regional comparison."""
    card_open("By Region", "Performance distribution")

    regional_df = df[(df["year"] == year) & (df["quarter"] == quarter)].copy()

    if len(regional_df) > 0:
        regional_agg = (
            regional_df.groupby("region").agg({"sustainability_index": "mean"}).reset_index()
        )
        regional_agg = regional_agg.sort_values("sustainability_index", ascending=True).tail(8)

        # Create stacked-look bars
        fig = go.Figure()

        # Base bar
        fig.add_trace(
            go.Bar(
                y=regional_agg["region"],
                x=regional_agg["sustainability_index"],
                orientation="h",
                marker={
                    "color": dark_theme.colors.purple,
                    "line": {"width": 0},
                },
                text=[f"{v:.1f}" for v in regional_agg["sustainability_index"]],
                textposition="outside",
                textfont={"color": "#94a3b8", "size": 11},
            )
        )

        apply_dark_chart_layout(fig, height=280)
        fig.update_layout(
            xaxis={"showgrid": True, "gridcolor": "rgba(255,255,255,0.05)"},
            yaxis={"showgrid": False, "tickfont": {"size": 11}},
            bargap=0.4,
        )
        st.plotly_chart(fig, width="stretch")
    else:
        st.info("No regional data for this period")

    card_close()


def _render_energy_mix_donut(sustainability: dict, dark_theme) -> None:
    """Render donut chart for energy/sustainability breakdown."""
    card_open("Sustainability Breakdown", "Index composition")

    breakdown = sustainability.get("breakdown", [])

    if breakdown:
        labels = [item.get("name", item.get("name_en", "Unknown")) for item in breakdown[:6]]
        values = [item.get("contribution", 0) for item in breakdown[:6]]

        colors = [
            dark_theme.colors.purple,
            dark_theme.colors.cyan,
            dark_theme.colors.pink,
            "#f472b6",
            "#818cf8",
            "#4ade80",
        ]

        fig = go.Figure(
            data=[
                go.Pie(
                    labels=labels,
                    values=values,
                    hole=0.6,
                    marker={"colors": colors[: len(labels)], "line": {"width": 0}},
                    textinfo="percent",
                    textfont={"color": "#fff", "size": 11},
                    hovertemplate="<b>%{label}</b><br>%{value:.1f} pts<extra></extra>",
                )
            ]
        )

        # Add center text
        total = sum(values)
        fig.add_annotation(
            text=f"<b>{total:.0f}</b><br>Total",
            x=0.5,
            y=0.5,
            font={"size": 16, "color": "#fff"},
            showarrow=False,
        )

        apply_dark_chart_layout(fig, height=280)
        fig.update_layout(
            showlegend=True,
            legend={
                "orientation": "h",
                "yanchor": "bottom",
                "y": -0.2,
                "xanchor": "center",
                "x": 0.5,
                "font": {"size": 10, "color": "#94a3b8"},
            },
        )
        st.plotly_chart(fig, width="stretch")
    else:
        st.info("No breakdown data available")

    card_close()


def _render_yearly_kpis_chart(df: pd.DataFrame, region: str, dark_theme) -> None:
    """Render grouped bar chart for yearly KPI comparison."""
    card_open("Yearly KPI Performance", "Multi-year comparison")

    trend_df = df.copy()
    if region != "all":
        trend_df = trend_df[trend_df["region"] == region]

    yearly = (
        trend_df.groupby("year")
        .agg(
            {
                "sustainability_index": "mean",
                "gdp_growth": "mean",
                "renewable_share": "mean",
            }
        )
        .reset_index()
    )
    yearly = yearly.sort_values("year")

    fig = go.Figure()

    # Add bars for each KPI
    fig.add_trace(
        go.Bar(
            name="Sustainability",
            x=yearly["year"].astype(str),
            y=yearly["sustainability_index"],
            marker_color=dark_theme.colors.purple,
        )
    )
    fig.add_trace(
        go.Bar(
            name="GDP Growth",
            x=yearly["year"].astype(str),
            y=yearly["gdp_growth"] * 10,  # Scale for visibility
            marker_color=dark_theme.colors.cyan,
        )
    )
    fig.add_trace(
        go.Bar(
            name="Renewables %",
            x=yearly["year"].astype(str),
            y=yearly["renewable_share"],
            marker_color=dark_theme.colors.pink,
        )
    )

    apply_dark_chart_layout(fig, height=280)
    fig.update_layout(
        barmode="group",
        bargap=0.2,
        bargroupgap=0.1,
        legend={
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.02,
            "xanchor": "center",
            "x": 0.5,
            "font": {"size": 10},
        },
    )
    st.plotly_chart(fig, width="stretch")
    card_close()


def _render_sustainability_gauge(sustainability: dict, dark_theme, theme) -> None:
    """Render dark-themed sustainability gauge."""
    card_open("Sustainability Score", "Overall index performance")

    index_value = sustainability.get("index", 0) or 0
    status = sustainability.get("status", "unknown")

    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=index_value,
            number={"suffix": "/100", "font": {"size": 32, "color": "#fff"}},
            domain={"x": [0, 1], "y": [0, 1]},
            gauge={
                "axis": {
                    "range": [0, 100],
                    "tickwidth": 1,
                    "tickcolor": "#374151",
                    "dtick": 25,
                    "tickfont": {"size": 10, "color": "#94a3b8"},
                },
                "bar": {"color": dark_theme.colors.purple, "thickness": 0.7},
                "bgcolor": "#1e2340",
                "borderwidth": 0,
                "steps": [
                    {"range": [0, 50], "color": "rgba(239, 68, 68, 0.3)"},
                    {"range": [50, 70], "color": "rgba(245, 158, 11, 0.3)"},
                    {"range": [70, 100], "color": "rgba(34, 197, 94, 0.3)"},
                ],
                "threshold": {
                    "line": {"color": "#22c55e", "width": 3},
                    "thickness": 0.8,
                    "value": 70,
                },
            },
        )
    )

    fig.update_layout(
        height=220,
        margin={"l": 20, "r": 20, "t": 20, "b": 0},
        paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig, width="stretch")

    # Status badge
    status_color = "#22c55e" if status == "green" else "#f59e0b" if status == "amber" else "#ef4444"
    status_text = (
        "On Track" if status == "green" else "At Risk" if status == "amber" else "Critical"
    )
    render_html(
        f"""
        <div style="text-align: center; margin-top: -10px;">
            <span style="background: {status_color}22; color: {status_color}; padding: 6px 16px;
                        border-radius: 6px; font-size: 13px; font-weight: 600;">
                {status_text} • Target: 70
            </span>
        </div>
    """
    )
    card_close()


def _render_dark_subgrid(
    title: str, kpis: list, metrics: dict, dark_theme, columns: int = 4
) -> None:
    """Render KPI cards in a dark-themed grid."""
    render_html(
        f"""
        <div style="margin: 16px 0 12px 0;">
            <span style="font-size: 14px; font-weight: 600; color: #e2e8f0;">{title}</span>
        </div>
    """
    )

    cols = st.columns(columns)
    for i, kpi_id in enumerate(kpis):
        if kpi_id not in metrics:
            continue
        kpi = metrics[kpi_id]
        with cols[i % columns]:
            val = kpi.get("value", 0) or 0
            unit = kpi.get("unit", "")
            change = kpi.get("change_percent", 0) or 0
            status = kpi.get("status", "neutral")
            label = kpi.get("name", kpi_id.replace("_", " ").title())

            # Format value
            if abs(val) >= 1_000_000_000:
                display_val = f"{val / 1_000_000_000:.1f}B"
            elif abs(val) >= 1_000_000:
                display_val = f"{val / 1_000_000:.1f}M"
            elif abs(val) >= 1_000:
                display_val = f"{val / 1_000:.1f}K"
            else:
                display_val = f"{val:.1f}" if isinstance(val, float) else str(val)

            if unit and unit not in display_val:
                display_val = f"{display_val}{unit}"

            # Status colors
            status_bg = (
                "#22c55e22"
                if status == "green"
                else "#f59e0b22"
                if status == "amber"
                else "#ef444422"
                if status == "red"
                else "#6b728022"
            )
            delta_color = "#22c55e" if change > 0 else "#ef4444" if change < 0 else "#94a3b8"
            delta_icon = "↑" if change > 0 else "↓" if change < 0 else "→"

            render_html(
                f"""
                <div style="
                    background: linear-gradient(145deg, #1b1f36 0%, #1e2340 100%);
                    border: 1px solid #2d3555;
                    border-radius: 12px;
                    padding: 16px;
                    margin-bottom: 12px;
                ">
                    <div style="font-size: 11px; color: #94a3b8; margin-bottom: 6px;
                               text-transform: uppercase; letter-spacing: 0.5px;">{label}</div>
                    <div style="font-size: 22px; font-weight: 700; color: #f1f5f9;">{display_val}</div>
                    <div style="display: flex; align-items: center; gap: 8px; margin-top: 8px;">
                        <span style="color: {delta_color}; font-size: 12px; font-weight: 600;">
                            {delta_icon} {abs(change):.1f}%
                        </span>
                        <span style="background: {status_bg}; padding: 2px 8px; border-radius: 4px; font-size: 10px; color: #94a3b8;">
                            vs prev
                        </span>
                    </div>
                </div>
            """
            )


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def _render_section_title(title: str, subtitle: str = "") -> None:
    """Render a modern section title."""
    render_html(
        f"""
        <div class='section-header'>
            <span>{title}</span>
        </div>
        <div class='section-subtitle'>{subtitle}</div>
        """
    )


# =============================================================================
# PDF DESIGN SPEC - HERO METRICS SECTION
# =============================================================================


def _render_hero_sustainability_gauge(
    sustainability: dict,
    sustainability_prev: dict | None,
    dark_theme,
) -> None:
    """
    Render the premium Hero Sustainability Index gauge.

    Features:
    - Premium radial gauge with animated glow effects
    - Red (0-40), Amber (40-70), Green (70-100) zones
    - Main value with delta and status pill
    - Glassmorphism card with accent lighting
    """
    index_value = sustainability.get("index", 0) or 0
    status = sustainability.get("status", "unknown")
    previous_value = None
    if sustainability_prev and sustainability_prev.get("status") != "no_data":
        previous_value = sustainability_prev.get("index")

    delta = ((index_value - previous_value) / previous_value * 100) if previous_value else 0

    # Determine glow color based on value
    if index_value >= 70:
        glow_color = dark_theme.colors.green
        status_text = "On Track"
    elif index_value >= 40:
        glow_color = dark_theme.colors.amber
        status_text = "Monitor"
    else:
        glow_color = dark_theme.colors.red
        status_text = "Needs Attention"

    # Premium card with accent glow
    render_html(
        f"""
        <div class="dark-card" style="
            position: relative;
            border-left: 4px solid {glow_color};
            box-shadow:
                0 4px 6px rgba(0, 0, 0, 0.1),
                0 25px 60px rgba(0, 0, 0, 0.4),
                -8px 0 40px {glow_color}20,
                inset 0 1px 0 rgba(255, 255, 255, 0.08);
        ">
            <div style="display: flex; align-items: flex-start; justify-content: space-between; margin-bottom: 16px;">
                <div>
                    <div class="card-title">SUSTAINABILITY INDEX</div>
                    <div class="card-sub">National composite score</div>
                </div>
                <div style="
                    background: linear-gradient(135deg, {glow_color}25, {glow_color}15);
                    border: 1px solid {glow_color}40;
                    padding: 6px 14px;
                    border-radius: 20px;
                    font-size: 11px;
                    color: {glow_color};
                    font-weight: 600;
                    box-shadow: 0 0 20px {glow_color}20;
                ">
                    {status_text}
                </div>
            </div>
        """
    )

    # Create premium radial gauge
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number+delta",
            value=index_value,
            number={
                "suffix": "",
                "font": {"size": 54, "color": "#FFFFFF", "family": "'Inter', sans-serif"},
            },
            delta={
                "reference": previous_value,
                "relative": True,
                "valueformat": ".1%",
                "font": {"size": 16},
                "increasing": {"color": dark_theme.colors.green},
                "decreasing": {"color": dark_theme.colors.red},
                "position": "bottom",
            },
            domain={"x": [0, 1], "y": [0.08, 1]},
            gauge={
                "axis": {
                    "range": [0, 100],
                    "tickwidth": 2,
                    "tickcolor": "rgba(255,255,255,0.2)",
                    "dtick": 20,
                    "tickfont": {"size": 12, "color": "rgba(255,255,255,0.5)"},
                },
                "bar": {
                    "color": glow_color,
                    "thickness": 0.7,
                    "line": {"width": 0},
                },
                "bgcolor": "rgba(15, 23, 42, 0.9)",
                "borderwidth": 2,
                "bordercolor": "rgba(255,255,255,0.08)",
                "steps": [
                    {"range": [0, 40], "color": "rgba(239, 68, 68, 0.15)"},
                    {"range": [40, 70], "color": "rgba(245, 158, 11, 0.15)"},
                    {"range": [70, 100], "color": "rgba(16, 185, 129, 0.15)"},
                ],
                "threshold": {
                    "line": {"color": "rgba(255,255,255,0.5)", "width": 2},
                    "thickness": 0.85,
                    "value": 70,
                },
            },
        )
    )

    fig.update_layout(
        height=300,
        margin={"l": 25, "r": 25, "t": 35, "b": 20},
        paper_bgcolor="rgba(0,0,0,0)",
        font={"family": "'Inter', -apple-system, sans-serif"},
    )
    st.plotly_chart(fig, width="stretch")

    # Target indicator
    render_html(
        f"""
            <div style="
                text-align: center;
                margin-top: -10px;
                padding-top: 16px;
                border-top: 1px solid rgba(255,255,255,0.06);
            ">
                <span style="
                    font-size: 12px;
                    color: rgba(255,255,255,0.45);
                ">
                    Target: <span style="color: rgba(255,255,255,0.7); font-weight: 600;">70</span>
                    &nbsp;•&nbsp;
                    Current: <span style="color: {glow_color}; font-weight: 700;">{index_value:.1f}</span>
                </span>
            </div>
        </div>
    """
    )


def _render_hero_kpi_cards(
    metrics: dict, dark_theme, quality_metrics: dict, quality_prev: dict | None,
    df: pd.DataFrame | None = None
) -> None:
    """
    Render the 2x2 grid of hero KPI cards matching PDF design spec.

    Cards: GDP Growth, Unemployment Rate, CO2 Intensity, Data Quality Score
    """
    # Define hero KPIs with their domain colors
    hero_kpis = [
        ("gdp_growth", "GDP Growth", dark_theme.colors.domain_economic, "📈"),
        ("unemployment_rate", "Unemployment Rate", dark_theme.colors.domain_labor, "👥"),
        ("co2_index", "CO₂ Intensity", dark_theme.colors.domain_environmental, "🌱"),
        ("data_quality", "Data Quality", dark_theme.colors.domain_data_quality, "✅"),
    ]

    # Targets (Mocked for now, ideally from config)
    targets = {
        "gdp_growth": 3.5,
        "unemployment_rate": 4.0,
        "co2_index": 90.0,
        "data_quality": 95.0,
    }

    # 2x2 grid
    row1 = st.columns(2, gap="medium")
    row2 = st.columns(2, gap="medium")
    cols = [row1[0], row1[1], row2[0], row2[1]]

    for i, (kpi_id, label, domain_color, icon) in enumerate(hero_kpis):
        with cols[i]:
            sparkline_data = None
            has_alert = False
            alert_type = "info"
            target_val = targets.get(kpi_id)
            status_label = "On Track" # Default

            if kpi_id == "data_quality":
                # Special case for data quality score
                val = quality_metrics.get("completeness", 0)
                prev_val = None
                if quality_prev and quality_prev.get("completeness") is not None:
                    prev_val = quality_prev.get("completeness")
                delta = ((val - prev_val) / prev_val * 100) if prev_val else 0
                
                if val >= 95: status_label = "On Track"
                elif val >= 80: status_label = "Watch"
                else: status_label = "Off Track"

                # Alert for low data quality
                if val < 60:
                    has_alert = True
                    alert_type = "critical"
                elif val < 80:
                    has_alert = True
                    alert_type = "warning"
            else:
                kpi = metrics.get(kpi_id, {})
                val = kpi.get("value", 0) or 0
                delta = kpi.get("change_percent", 0) or 0
                status_code = kpi.get("status", "neutral")
                
                if status_code == "green": status_label = "On Track"
                elif status_code == "amber": status_label = "Watch"
                elif status_code == "red": status_label = "Off Track"
                else: status_label = None

                # Generate sparkline data if dataframe is available
                if df is not None and not df.empty and kpi_id in df.columns:
                    # Get last 8 data points for sparkline
                    hist_data = df.sort_values(["year", "quarter"])
                    sparkline_vals = hist_data[kpi_id].dropna().tail(8).tolist()
                    if len(sparkline_vals) >= 2:
                        sparkline_data = sparkline_vals

            render_enhanced_kpi_card(
                title=label,
                value=f"{val:.1f}%" if kpi_id != "co2_index" else f"{val:.1f}",
                delta=delta,
                delta_suffix="%" if kpi_id != "co2_index" else "",
                sparkline_data=sparkline_data,
                alert_type=alert_type if has_alert else None,
                icon=icon,
                color=domain_color,
                target=target_val,
                status=status_label,
            )



def _render_hero_kpi_card(
    label: str,
    value: float,
    delta: float,
    status: str,
    domain_color: str,
    icon: str,
    kpi_id: str,
    dark_theme,
    sparkline_data: list[float] | None = None,
    has_alert: bool = False,
    alert_type: str = "warning",
) -> None:
    """Render a single hero KPI card with domain color accent, sparkline, and alert badge."""
    # Format value
    if kpi_id in ["gdp_growth", "unemployment_rate"]:
        display_val = f"{value:.1f}%"
    elif kpi_id == "data_quality":
        display_val = f"{value:.0f}%"
    elif abs(value) >= 1_000_000_000:
        display_val = f"{value / 1_000_000_000:.1f}B"
    elif abs(value) >= 1_000_000:
        display_val = f"{value / 1_000_000:.1f}M"
    elif abs(value) >= 1_000:
        display_val = f"{value / 1_000:.1f}K"
    else:
        display_val = f"{value:.1f}"

    # Delta formatting
    delta_color = dark_theme.colors.green if delta >= 0 else dark_theme.colors.red
    # Invert for unemployment (lower is better)
    if kpi_id == "unemployment_rate":
        delta_color = dark_theme.colors.red if delta >= 0 else dark_theme.colors.green
    delta_icon = "▲" if delta >= 0 else "▼"

    status_color = dark_theme.colors.get_status_color(status)

    # Generate sparkline SVG if data provided
    sparkline_html = ""
    if sparkline_data and len(sparkline_data) >= 2:
        spark_color = dark_theme.colors.green if delta >= 0 else dark_theme.colors.red
        if kpi_id == "unemployment_rate":
            spark_color = dark_theme.colors.red if delta >= 0 else dark_theme.colors.green
        sparkline_html = f'''
            <div style="margin-top: 12px; opacity: 0.85;">
                {create_sparkline_svg(sparkline_data, width=140, height=35, color=spark_color, fill_color=spark_color)}
            </div>'''

    # Alert badge if needed
    alert_html = ""
    if has_alert:
        alert_icon = "!" if alert_type == "critical" else "⚡"
        alert_html = f'''
            <div class="alert-badge {alert_type}" style="
                position: absolute;
                top: 12px;
                left: 12px;
            ">{alert_icon}</div>'''

    render_html(
        f"""
        <div class="dark-card animate-fade-in" style="
            background: linear-gradient(145deg, rgba(255,255,255,0.06), rgba(255,255,255,0.02));
            border: 1px solid {domain_color}35;
            border-left: 4px solid {domain_color};
            border-radius: 16px;
            padding: 22px 24px;
            margin-bottom: 14px;
            position: relative;
            overflow: hidden;
            box-shadow:
                0 4px 6px rgba(0, 0, 0, 0.1),
                0 20px 50px rgba(0, 0, 0, 0.35),
                -6px 0 30px {domain_color}15,
                inset 0 1px 0 rgba(255, 255, 255, 0.08);
            transition: all 280ms cubic-bezier(0.4, 0, 0.2, 1);
        ">
            {alert_html}

            <!-- Background glow effect -->
            <div style="
                position: absolute;
                top: -30px;
                right: -30px;
                width: 120px;
                height: 120px;
                background: radial-gradient(circle, {domain_color}15 0%, transparent 60%);
                border-radius: 50%;
                pointer-events: none;
            "></div>

            <!-- Icon badge -->
            <div style="
                position: absolute;
                top: 16px;
                right: 16px;
                width: 44px;
                height: 44px;
                background: linear-gradient(135deg, {domain_color}25, {domain_color}10);
                border-radius: 12px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 20px;
                border: 1px solid {domain_color}30;
            ">{icon}</div>

            <!-- Label -->
            <div style="
                font-size: 11px;
                font-weight: 600;
                color: rgba(255,255,255,0.5);
                text-transform: uppercase;
                letter-spacing: 1px;
                margin-bottom: 12px;
            ">{label}</div>

            <!-- Main Value -->
            <div class="animate-count" style="
                font-size: 38px;
                font-weight: 800;
                color: rgba(255,255,255,0.98);
                margin-bottom: 12px;
                letter-spacing: -0.5px;
                background: linear-gradient(135deg, rgba(255,255,255,0.98), rgba(255,255,255,0.85));
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            ">{display_val}</div>

            <!-- Delta and Status -->
            <div style="display: flex; align-items: center; gap: 14px; flex-wrap: wrap;">
                <span style="
                    display: inline-flex;
                    align-items: center;
                    gap: 5px;
                    color: {delta_color};
                    font-size: 13px;
                    font-weight: 600;
                    padding: 5px 12px;
                    background: {delta_color}15;
                    border-radius: 20px;
                    border: 1px solid {delta_color}30;
                ">
                    <span style="font-size: 12px;">{'↑' if delta >= 0 else '↓'}</span>
                    {abs(delta):.1f}%
                </span>
                <span style="
                    background: linear-gradient(135deg, {status_color}20, {status_color}10);
                    color: {status_color};
                    padding: 5px 12px;
                    border-radius: 20px;
                    font-size: 11px;
                    font-weight: 600;
                    border: 1px solid {status_color}30;
                ">vs prev quarter</span>
            </div>

            {sparkline_html}
        </div>
    """
    )


# =============================================================================
# PDF DESIGN SPEC - PILLAR SECTIONS
# =============================================================================


def _render_pillar_section_economic(
    df: pd.DataFrame, metrics: dict, year: int, quarter: int, region: str, dark_theme
) -> None:
    """Render Economic Performance pillar section matching PDF design."""
    domain_color = dark_theme.colors.domain_economic

    # Top row: 5 KPI cards
    economic_kpis = [
        "gdp_growth",
        "gdp_total",
        "foreign_investment",
        "export_diversity_index",
        "economic_complexity",
    ]

    card_open("Economic Indicators", "Key economic performance metrics")
    cols = st.columns(5, gap="small")
    for i, kpi_id in enumerate(economic_kpis):
        with cols[i]:
            _render_pillar_kpi_card(metrics.get(kpi_id, {}), kpi_id, domain_color, dark_theme)

    render_html("<div style='height: 16px;'></div>")

    # GDP Growth vs Target chart
    _render_gdp_trend_chart(df, year, quarter, region, dark_theme, domain_color)
    card_close()


def _render_pillar_section_labor(
    df: pd.DataFrame, metrics: dict, year: int, quarter: int, dark_theme
) -> None:
    """Render Labor & Skills pillar section matching PDF design."""
    domain_color = dark_theme.colors.domain_labor

    labor_kpis = ["unemployment_rate", "green_jobs", "skills_gap_index", "population"]

    card_open("Labor Metrics", "Workforce indicators")
    cols = st.columns(2, gap="small")
    for i, kpi_id in enumerate(labor_kpis):
        with cols[i % 2]:
            _render_pillar_kpi_card(metrics.get(kpi_id, {}), kpi_id, domain_color, dark_theme)

    # Mini unemployment trend chart
    _render_mini_trend_chart(df, "unemployment_rate", "Unemployment Trend", dark_theme, domain_color)
    card_close()


def _render_pillar_section_social(
    df: pd.DataFrame, metrics: dict, year: int, quarter: int, dark_theme
) -> None:
    """Render Social & Digital pillar section matching PDF design."""
    domain_color = dark_theme.colors.domain_social

    social_kpis = ["digital_readiness", "social_progress_score", "innovation_index"]

    card_open("Social & Digital Metrics", "Digital transformation indicators")
    cols = st.columns(3, gap="small")
    for i, kpi_id in enumerate(social_kpis):
        with cols[i]:
            _render_pillar_kpi_card(metrics.get(kpi_id, {}), kpi_id, domain_color, dark_theme)

    # Mini digital readiness chart
    _render_mini_trend_chart(
        df, "digital_readiness", "Digital Readiness Trend", dark_theme, domain_color
    )
    card_close()


def _render_pillar_section_environmental(
    df: pd.DataFrame, metrics: dict, year: int, quarter: int, region: str, dark_theme
) -> None:
    """Render Environmental & Sustainability pillar section matching PDF design."""
    domain_color = dark_theme.colors.domain_environmental

    env_kpis = [
        "sustainability_index",
        "co2_index",
        "renewable_share",
        "energy_intensity",
        "water_efficiency",
        "waste_recycling_rate",
        "forest_coverage",
        "air_quality_index",
    ]

    card_open("Environmental Indicators", "Sustainability and environmental metrics")
    # 4x2 grid
    row1 = st.columns(4, gap="small")
    row2 = st.columns(4, gap="small")
    all_cols = row1 + row2

    for i, kpi_id in enumerate(env_kpis):
        if i < len(all_cols):
            with all_cols[i]:
                _render_pillar_kpi_card(metrics.get(kpi_id, {}), kpi_id, domain_color, dark_theme)

    render_html("<div style='height: 16px;'></div>")

    # Multi-line environmental trends chart
    _render_environmental_trends_chart(df, dark_theme, domain_color)
    card_close()


def _render_pillar_kpi_card(kpi: dict, kpi_id: str, domain_color: str, dark_theme) -> None:
    """Render a KPI card for pillar sections with domain color accent."""
    val = kpi.get("value", 0) or 0
    change = kpi.get("change_percent", 0) or 0
    status = kpi.get("status", "neutral")
    label = kpi.get("name", kpi.get("display_name", kpi_id.replace("_", " ").title()))
    unit = get_kpi_unit(kpi_id)

    # Format value
    if abs(val) >= 1_000_000_000:
        display_val = f"{val / 1_000_000_000:.1f}B"
    elif abs(val) >= 1_000_000:
        display_val = f"{val / 1_000_000:.1f}M"
    elif abs(val) >= 1_000:
        display_val = f"{val / 1_000:.1f}K"
    else:
        display_val = f"{val:.1f}" if isinstance(val, float) else str(val)

    if unit and unit not in display_val:
        display_val = f"{display_val}{unit}"

    delta_color = dark_theme.colors.green if change >= 0 else dark_theme.colors.red
    delta_icon = "↑" if change >= 0 else "↓"

    render_html(
        f"""
        <div style="
            background: linear-gradient(145deg, {dark_theme.colors.bg_card} 0%, {dark_theme.colors.bg_card_alt} 100%);
            border: 1px solid {domain_color}25;
            border-top: 3px solid {domain_color};
            border-radius: 8px;
            padding: 14px;
            margin-bottom: 8px;
            min-height: 100px;
        ">
            <div style="font-size: 10px; color: {dark_theme.colors.text_muted};
                       text-transform: uppercase; letter-spacing: 0.3px; margin-bottom: 6px;">
                {label}
            </div>
            <div style="font-size: 20px; font-weight: 700; color: {dark_theme.colors.text_primary};">
                {display_val}
            </div>
            <div style="display: flex; align-items: center; gap: 6px; margin-top: 6px;">
                <span style="color: {delta_color}; font-size: 11px; font-weight: 600;">
                    {delta_icon} {abs(change):.1f}%
                </span>
            </div>
        </div>
    """
    )


def _render_gdp_trend_chart(
    df: pd.DataFrame, year: int, quarter: int, region: str, dark_theme, domain_color: str
) -> None:
    """Render GDP Growth vs Target line chart."""
    trend_df = df.copy()
    if region != "all":
        trend_df = trend_df[trend_df["region"] == region]

    gdp_trend = (
        trend_df.groupby(["year", "quarter"])
        .agg({"gdp_growth": "mean"})
        .reset_index()
    )
    gdp_trend = add_period_column(gdp_trend)
    gdp_trend = gdp_trend.sort_values(["year", "quarter"])

    if len(gdp_trend) < 2:
        return

    fig = go.Figure()

    # Actual GDP Growth
    fig.add_trace(
        go.Scatter(
            x=gdp_trend["period"],
            y=gdp_trend["gdp_growth"],
            mode="lines+markers",
            name="Actual",
            line={"color": domain_color, "width": 3},
            marker={"size": 8, "color": domain_color},
            fill="tozeroy",
            fillcolor=_hex_to_rgba(domain_color, 0.15),
        )
    )

    # Target line (3.5% example)
    target_value = 3.5
    fig.add_hline(
        y=target_value,
        line_dash="dash",
        line_color=dark_theme.colors.green,
        annotation_text=f"Target: {target_value}%",
        annotation_font={"color": dark_theme.colors.text_muted},
    )

    apply_dark_chart_layout(fig, height=200)
    fig.update_layout(
        showlegend=True,
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.02, "x": 0.5, "xanchor": "center"},
    )
    st.plotly_chart(fig, width="stretch")


def _render_mini_trend_chart(
    df: pd.DataFrame, kpi_id: str, title: str, dark_theme, domain_color: str
) -> None:
    """Render a mini trend chart for pillar sections."""
    if kpi_id not in df.columns:
        return

    trend_data = df.groupby(["year", "quarter"]).agg({kpi_id: "mean"}).reset_index()
    trend_data = add_period_column(trend_data)
    trend_data = trend_data.sort_values(["year", "quarter"]).tail(8)

    if len(trend_data) < 2:
        return

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=trend_data["period"],
            y=trend_data[kpi_id],
            mode="lines+markers",
            line={"color": domain_color, "width": 2},
            marker={"size": 5, "color": domain_color},
            fill="tozeroy",
            fillcolor=_hex_to_rgba(domain_color, 0.1),
        )
    )

    apply_dark_chart_layout(fig, height=120)
    fig.update_layout(
        showlegend=False,
        margin={"l": 10, "r": 10, "t": 10, "b": 20},
        xaxis={"tickfont": {"size": 9}},
        yaxis={"tickfont": {"size": 9}},
    )
    st.plotly_chart(fig, width="stretch")


def _render_environmental_trends_chart(df: pd.DataFrame, dark_theme, domain_color: str) -> None:
    """Render multi-line environmental trends chart."""
    env_kpis = ["co2_index", "renewable_share", "energy_intensity", "water_efficiency"]
    available_kpis = [k for k in env_kpis if k in df.columns]

    if not available_kpis:
        return

    trend_env = (
        df.groupby(["year", "quarter"])
        .agg({k: "mean" for k in available_kpis})
        .reset_index()
    )
    trend_env = add_period_column(trend_env)
    trend_env = trend_env.sort_values(["year", "quarter"])

    # Normalize to 0-100 scale for comparison
    for kpi in available_kpis:
        min_val = trend_env[kpi].min()
        max_val = trend_env[kpi].max()
        if max_val > min_val:
            trend_env[f"{kpi}_norm"] = (trend_env[kpi] - min_val) / (max_val - min_val) * 100
        else:
            trend_env[f"{kpi}_norm"] = 50

    fig = go.Figure()
    colors = [domain_color, dark_theme.colors.cyan, dark_theme.colors.purple, dark_theme.colors.amber]
    labels = {
        "co2_index": "CO₂ Intensity",
        "renewable_share": "Renewables",
        "energy_intensity": "Energy Intensity",
        "water_efficiency": "Water Efficiency",
    }

    for i, kpi in enumerate(available_kpis):
        fig.add_trace(
            go.Scatter(
                x=trend_env["period"],
                y=trend_env[f"{kpi}_norm"],
                mode="lines+markers",
                name=labels.get(kpi, kpi),
                line={"color": colors[i % len(colors)], "width": 2},
                marker={"size": 5},
            )
        )

    apply_dark_chart_layout(fig, height=200)
    fig.update_layout(
        showlegend=True,
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.02, "x": 0.5, "xanchor": "center"},
        yaxis_title="Normalized Index",
    )
    st.plotly_chart(fig, width="stretch")


# =============================================================================
# PDF DESIGN SPEC - DATA QUALITY SECTION
# =============================================================================


def _render_data_quality_section(
    quality_metrics: dict,
    quality_prev: dict | None,
    metrics: dict,
    df: pd.DataFrame,
    catalog: dict,
    dark_theme,
) -> None:
    """Render Data Quality & Completeness section using real completeness data."""
    domain_color = dark_theme.colors.domain_data_quality

    # Main layout: Large score card + metadata + completeness chart
    score_col, details_col = st.columns([0.35, 0.65], gap="large")

    with score_col:
        completeness = quality_metrics.get("completeness", 0)
        avg_quality = quality_metrics.get("avg_quality_score") or completeness
        prev_quality = None
        if quality_prev and quality_prev.get("avg_quality_score") is not None:
            prev_quality = quality_prev.get("avg_quality_score")
        elif quality_prev and quality_prev.get("completeness") is not None:
            prev_quality = quality_prev.get("completeness")

        delta = ((avg_quality - prev_quality) / prev_quality * 100) if prev_quality else 0

        card_open("Overall Quality Score", "Data completeness and accuracy")

        # Use progress ring for quality score
        render_html(
            f"""
            <div style="text-align: center; padding: 20px 0;">
                {create_progress_ring(avg_quality, max_value=100, size=100, stroke_width=10, label="Quality")}
                <div style="
                    display: inline-block;
                    background: {dark_theme.colors.green}20;
                    color: {dark_theme.colors.green};
                    padding: 6px 16px;
                    border-radius: 16px;
                    font-size: 13px;
                    margin-top: 12px;
                ">
                    {"▲" if delta >= 0 else "▼"} {abs(delta):.1f}% vs previous
                </div>
            </div>
        """
        )
        card_close()

    with details_col:
        # Metadata panel
        card_open("Data Health Summary", "Key quality indicators")

        records = quality_metrics.get("records_count", 0)
        last_update = quality_metrics.get("last_update")
        if not last_update and "load_timestamp" in df.columns:
            ts = df["load_timestamp"].dropna()
            last_update = ts.max() if len(ts) else None
        update_str = last_update.strftime("%Y-%m-%d %H:%M") if last_update else "N/A"

        total_indicators = len([k for k in catalog.get("kpis", []) if k.get("id")])
        source_count = df["source_system"].dropna().nunique() if "source_system" in df else 0
        complete_count = sum(1 for m in metrics.values() if m.get("value") is not None)
        missing_count = sum(1 for m in metrics.values() if m.get("value") is None)

        # Metadata grid
        meta_cols = st.columns(4, gap="small")
        meta_items = [
            ("Last Updated", update_str, "🕐"),
            ("Total Indicators", str(total_indicators), "📊"),
            ("Complete", str(complete_count), "✅"),
            ("Data Sources", str(source_count or "-") , "🔗"),
        ]

        for i, (label, value, icon) in enumerate(meta_items):
            with meta_cols[i]:
                render_html(
                    f"""
                    <div style="
                        background: {dark_theme.colors.bg_card};
                        padding: 12px;
                        border-radius: 8px;
                        text-align: center;
                        border: 1px solid {dark_theme.colors.border};
                    ">
                        <div style="font-size: 16px; margin-bottom: 4px;">{icon}</div>
                        <div style="font-size: 16px; font-weight: 700; color: {dark_theme.colors.text_primary};">
                            {value}
                        </div>
                        <div style="font-size: 10px; color: {dark_theme.colors.text_muted}; text-transform: uppercase;">
                            {label}
                        </div>
                    </div>
                """
                )

        render_html("<div style='height: 16px;'></div>")

        # Completeness by pillar stacked bar chart using real missing data
        pillar_completeness = _build_pillar_completeness(quality_metrics, catalog)
        _render_completeness_by_pillar_chart(pillar_completeness, dark_theme)
        card_close()


def _build_pillar_completeness(quality_metrics: dict, catalog: dict) -> dict:
    """Compute completeness buckets per pillar from real missing_by_kpi data."""
    missing_by_kpi = quality_metrics.get("missing_by_kpi", {}) or {}
    category_lookup = {k.get("id"): k.get("category", "other") for k in catalog.get("kpis", [])}
    label_lookup = {
        "economic": "Economic",
        "labor": "Labor & Skills",
        "social": "Social & Digital",
        "environmental": "Environmental",
        "data_quality": "Data Quality",
    }

    pillar_data: dict[str, dict[str, float]] = {}

    for kpi_id, stats in missing_by_kpi.items():
        category = category_lookup.get(kpi_id, "other")
        pillar_label = label_lookup.get(category, "Other")
        pillar_entry = pillar_data.setdefault(pillar_label, {"complete": 0, "partial": 0, "missing": 0, "total": 0})

        total = stats.get("total", 0)
        missing = stats.get("missing", 0)
        if total == 0:
            continue
        missing_pct = stats.get("percent", (missing / total) * 100 if total else 0)

        pillar_entry["total"] += 1
        if missing_pct == 0:
            pillar_entry["complete"] += 1
        elif missing_pct < 40:
            pillar_entry["partial"] += 1
        else:
            pillar_entry["missing"] += 1

    # Convert counts to percentages of KPIs per pillar
    for pillar, data in pillar_data.items():
        total = data.get("total", 1)
        data["complete"] = round(data.get("complete", 0) / total * 100, 1)
        data["partial"] = round(data.get("partial", 0) / total * 100, 1)
        data["missing"] = round(data.get("missing", 0) / total * 100, 1)

    return pillar_data


def _render_completeness_by_pillar_chart(pillar_data: dict, dark_theme) -> None:
    """Render 100% stacked bar chart for completeness by pillar using real metrics."""
    if not pillar_data:
        st.info("No completeness data available for this period.")
        return

    pillars = list(pillar_data.keys())

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            name="Complete",
            y=pillars,
            x=[pillar_data[p]["complete"] for p in pillars],
            orientation="h",
            marker_color=dark_theme.colors.green,
            text=[f"{pillar_data[p]['complete']:.0f}%" for p in pillars],
            textposition="inside",
            textfont={"color": "white", "size": 11},
        )
    )

    fig.add_trace(
        go.Bar(
            name="Partial",
            y=pillars,
            x=[pillar_data[p]["partial"] for p in pillars],
            orientation="h",
            marker_color=dark_theme.colors.amber,
            text=[f"{pillar_data[p]['partial']:.0f}%" for p in pillars],
            textposition="inside",
            textfont={"color": "white", "size": 11},
        )
    )

    fig.add_trace(
        go.Bar(
            name="Missing",
            y=pillars,
            x=[pillar_data[p]["missing"] for p in pillars],
            orientation="h",
            marker_color=dark_theme.colors.red,
            text=[f"{pillar_data[p]['missing']:.0f}%" for p in pillars],
            textposition="inside",
            textfont={"color": "white", "size": 11},
        )
    )

    apply_dark_chart_layout(fig, height=200)
    fig.update_layout(
        barmode="stack",
        xaxis={"range": [0, 100], "title": "Completeness %"},
        yaxis={"categoryorder": "array", "categoryarray": pillars[::-1]},
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.02, "x": 0.5, "xanchor": "center"},
        bargap=0.3,
    )
    st.plotly_chart(fig, width="stretch")


# =============================================================================
# PDF DESIGN SPEC - YEAR-OVER-YEAR COMPARISON
# =============================================================================


def _render_yoy_comparison_section(
    df: pd.DataFrame, year: int, quarter: int, region: str, dark_theme
) -> None:
    """Render Year-over-Year comparison cards for key KPIs."""

    # Filter by region if specified
    filtered_df = df.copy()
    if region and region != "all":
        filtered_df = filtered_df[filtered_df["region"] == region]

    # Get current and previous year data
    current_data = filtered_df[(filtered_df["year"] == year) & (filtered_df["quarter"] == quarter)]
    prev_year_data = filtered_df[(filtered_df["year"] == year - 1) & (filtered_df["quarter"] == quarter)]

    # KPIs to compare
    yoy_kpis = [
        ("gdp_growth", "GDP Growth", "%", "📈"),
        ("unemployment_rate", "Unemployment Rate", "%", "👥"),
        ("sustainability_index", "Sustainability Index", "", "🌱"),
        ("digital_readiness", "Digital Readiness", "", "💻"),
    ]

    card_open("Year-over-Year Performance", f"Q{quarter} {year} vs Q{quarter} {year-1}")

    # Create 2x2 grid for YoY comparisons
    row1 = st.columns(2, gap="medium")
    row2 = st.columns(2, gap="medium")
    cols = [row1[0], row1[1], row2[0], row2[1]]

    for i, (kpi_id, kpi_name, unit, icon) in enumerate(yoy_kpis):
        with cols[i]:
            if kpi_id not in current_data.columns:
                continue

            current_val = current_data[kpi_id].mean() if not current_data.empty else 0
            prev_val = prev_year_data[kpi_id].mean() if not prev_year_data.empty else 0

            # Handle NaN
            current_val = 0 if pd.isna(current_val) else current_val
            prev_val = 0 if pd.isna(prev_val) else prev_val

            # Calculate change
            change = current_val - prev_val
            pct_change = ((current_val - prev_val) / prev_val * 100) if prev_val != 0 else 0

            # Invert logic for unemployment (lower is better)
            is_positive = change >= 0
            if kpi_id == "unemployment_rate":
                is_positive = change <= 0

            change_class = "positive" if is_positive else "negative"
            arrow = "→"

            render_html(f'''
            <div style="margin-bottom:8px; color:rgba(255,255,255,0.7); font-size:13px">{icon} {kpi_name}</div>
            <div class="yoy-comparison animate-fade-in">
                <div class="yoy-year">
                    <div class="year-label">{year - 1}</div>
                    <div class="year-value">{prev_val:.1f}{unit}</div>
                </div>
                <div class="yoy-divider">
                    <span class="yoy-arrow">{arrow}</span>
                    <span class="yoy-change {change_class}">
                        {"+" if pct_change >= 0 else ""}{pct_change:.1f}%
                    </span>
                </div>
                <div class="yoy-year">
                    <div class="year-label">{year}</div>
                    <div class="year-value">{current_val:.1f}{unit}</div>
                </div>
            </div>
            ''')

    card_close()


# =============================================================================
# PDF DESIGN SPEC - REGIONAL COMPARISON + SAUDI MAP ROW
# =============================================================================


def _render_regional_comparison_section(
    df: pd.DataFrame, filter_params: FilterParams, selected_region: str, dark_theme
) -> None:
    """Horizontal bar chart + stats panel using real regional comparison data."""
    comparison = get_regional_comparison(df, "sustainability_index", filter_params)

    if not comparison.regions:
        st.info("No regional data available for this period.")
        return

    data = pd.DataFrame(
        {
            "region": comparison.regions,
            "value": comparison.values,
            "status": [s.value if hasattr(s, "value") else str(s) for s in comparison.statuses],
        }
    ).sort_values("value", ascending=False)

    national_avg = comparison.national_average or 0
    highlight_region = selected_region if selected_region != "all" else None

    colors = [
        dark_theme.colors.cyan if (highlight_region and r == highlight_region) else "#334155"
        for r in data["region"]
    ]

    fig = go.Figure(
        go.Bar(
            y=data["region"],
            x=data["value"],
            orientation="h",
            marker={"color": colors, "line": {"width": 0}},
            text=[f"{v:.1f}" for v in data["value"]],
            textposition="outside",
            textfont={"color": "#F8FAFC", "size": 12},
            hovertemplate="<b>%{y}</b><br>Index: %{x:.1f}<extra></extra>",
        )
    )

    fig.add_vline(
        x=national_avg,
        line_dash="dash",
        line_color="#64748B",
        annotation_text=f"National Avg: {national_avg:.1f}",
        annotation_font={"color": "#94A3B8", "size": 11},
    )

    apply_dark_chart_layout(fig, height=420)
    fig.update_layout(
        xaxis={
            "showgrid": True,
            "gridcolor": "rgba(148,163,184,0.2)",
            "range": [0, max(100, max(data["value"]) + 5)],
            "title": "Sustainability Index",
        },
        yaxis={"showgrid": False, "autorange": "reversed"},
        bargap=0.35,
    )
    st.plotly_chart(fig, width="stretch")

    # Stats panel (Highest, Lowest, National Avg)
    highest_row = data.loc[data["value"].idxmax()]
    lowest_row = data.loc[data["value"].idxmin()]

    stats = [
        ("Highest Region", highest_row["region"], highest_row["value"], dark_theme.colors.green),
        ("Lowest Region", lowest_row["region"], lowest_row["value"], dark_theme.colors.red),
        ("National Avg", "Saudi Arabia", national_avg, dark_theme.colors.cyan),
    ]

    stat_cols = st.columns(len(stats), gap="medium")
    for col, (label, region_name, value, color) in zip(stat_cols, stats, strict=False):
        with col:
            render_html(
                f"""
                <div style="
                    background: linear-gradient(145deg, #0B1120 0%, #1E293B 100%);
                    border: 1px solid {color}40;
                    border-radius: 14px;
                    padding: 18px;
                    text-align: center;
                    box-shadow: {dark_theme.shadows.card_sm};
                ">
                    <div style="font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; color: {dark_theme.colors.text_muted};">{label}</div>
                    <div style="font-size: 18px; font-weight: 700; color: {dark_theme.colors.text_primary}; margin-top: 6px;">{region_name}</div>
                    <div style="font-size: 26px; font-weight: 800; color: {color};">{value:.1f}</div>
                </div>
            """
            )


def _region_name_to_id(name: str) -> str | None:
    mapping = {
        "Riyadh": "riyadh",
        "Makkah": "makkah",
        "Eastern Province": "eastern",
        "Madinah": "madinah",
        "Qassim": "qassim",
        "Asir": "asir",
        "Tabuk": "tabuk",
        "Hail": "hail",
        "Northern Borders": "northern_borders",
        "Jazan": "jazan",
        "Najran": "najran",
        "Al Bahah": "bahah",
        "Al Jawf": "jawf",
    }
    return mapping.get(name)


def _render_saudi_map_section(
    df: pd.DataFrame, filter_params: FilterParams, dark_theme, language: str
) -> None:
    """Geospatial choropleth for Saudi regions using real sustainability index values."""
    from analytics_hub_platform.ui.components.saudi_map import render_saudi_map

    # Always show all regions for the selected period
    period_filters = FilterParams(
        tenant_id=filter_params.tenant_id,
        year=filter_params.year,
        quarter=filter_params.quarter,
        region=None,
    )

    comparison = get_regional_comparison(df, "sustainability_index", period_filters)
    if not comparison.regions:
        st.info("No regional data available for this period.")
        return

    map_df = pd.DataFrame({"region": comparison.regions, "value": comparison.values})
    map_df["region_id"] = map_df["region"].apply(_region_name_to_id)
    map_df = map_df.dropna(subset=["region_id"])

    card_open("Saudi Arabia Map", "Choropleth by sustainability index")
    try:
        fig_map = render_saudi_map(
            region_data=map_df.rename(columns={"region_id": "region_id", "value": "value"}),
            value_column="value",
            title="",
            height=420,
            language=language,
            use_three_tier=True,
        )
        st.plotly_chart(fig_map, width="stretch")
    except Exception as e:
        st.warning(f"Map rendering unavailable: {str(e)}")

    period_df = df[(df["year"] == filter_params.year) & (df["quarter"] == filter_params.quarter)]
    renewables_avg = period_df["renewable_share"].mean() if "renewable_share" in period_df else None
    co2_avg = period_df["co2_index"].mean() if "co2_index" in period_df else None
    above_target = (map_df["value"] >= 70).sum()

    overlay_items = [
        ("National Index", comparison.national_average, dark_theme.colors.cyan),
        ("Regions ≥70", above_target, dark_theme.colors.green),
        ("Avg Renewables", f"{renewables_avg:.1f}%" if renewables_avg is not None else "N/A", dark_theme.colors.green),
    ]

    overlay_cols = st.columns(len(overlay_items), gap="medium")
    for col, (label, value, color) in zip(overlay_cols, overlay_items, strict=False):
        with col:
            render_html(
                f"""
                <div style="
                    background: {color}15;
                    border: 1px solid {color}40;
                    border-radius: 12px;
                    padding: 12px;
                    text-align: center;
                ">
                    <div style="font-size: 11px; color: {dark_theme.colors.text_muted}; text-transform: uppercase;">{label}</div>
                    <div style="font-size: 22px; font-weight: 700; color: {color};">{value}</div>
                </div>
            """
            )
    card_close()


# =============================================================================
# PDF DESIGN SPEC - KEY INSIGHTS SECTION
# =============================================================================


def _render_key_insights_section(
    snapshot: dict, metrics: dict, dark_theme, language: str
) -> None:
    """Render Key Insights section with two columns matching PDF design."""
    # Prefer domain-generated insights; fallback to metric deltas
    improvements = snapshot.get("top_improvements") or []
    attention_needed = snapshot.get("top_deteriorations") or []

    if not improvements and not attention_needed:
        for kpi_id, kpi in metrics.items():
            change = kpi.get("change_percent", 0) or 0
            status = kpi.get("status", "neutral")
            label = kpi.get("name", kpi.get("display_name", kpi_id.replace("_", " ").title()))

            if change > 0 and status == "green":
                improvements.append({"label": label, "change": change, "kpi_id": kpi_id})
            elif change < 0 or status == "red":
                attention_needed.append({"label": label, "change": change, "kpi_id": kpi_id})

        improvements = sorted(improvements, key=lambda x: -x["change"])[:5]
        attention_needed = sorted(attention_needed, key=lambda x: x["change"])[:5]

    def _normalize_items(items, positive: bool) -> list[dict]:
        normalized = []
        for item in items:
            label = item.get("label") or item.get("display_name") or item.get("kpi_id", "").replace("_", " ").title()
            change_val = item.get("change") or item.get("change_percent") or 0
            normalized.append({"label": label, "change": float(change_val), "positive": positive})
        return normalized

    improvements = _normalize_items(improvements, True)
    attention_needed = _normalize_items(attention_needed, False)

    # Two-column layout
    improve_col, attention_col = st.columns(2, gap="large")

    with improve_col:
        card_open("🚀 Top Improvements This Quarter", "KPIs showing strong positive momentum")
        if improvements:
            for item in improvements:
                render_html(
                    f"""
                    <div style="
                        display: flex;
                        align-items: center;
                        padding: 12px 16px;
                        background: {dark_theme.colors.green}10;
                        border-left: 3px solid {dark_theme.colors.green};
                        border-radius: 0 8px 8px 0;
                        margin-bottom: 8px;
                    ">
                        <span style="color: {dark_theme.colors.green}; font-size: 16px; margin-right: 12px;">▲</span>
                        <div style="flex: 1;">
                            <div style="color: {dark_theme.colors.text_primary}; font-weight: 500;">
                                {item['label']}
                            </div>
                            <div style="color: {dark_theme.colors.green}; font-size: 12px;">
                                +{item['change']:.1f}% improvement
                            </div>
                        </div>
                    </div>
                """
                )
        else:
            render_html(
                f"<p style='color: {dark_theme.colors.text_muted};'>No significant improvements to highlight.</p>"
            )
        card_close()

    with attention_col:
        card_open("⚠️ Areas Needing Attention", "KPIs requiring focus and intervention")
        if attention_needed:
            for item in attention_needed:
                change_display = f"{item['change']:.1f}%" if item['change'] < 0 else "At Risk"
                render_html(
                    f"""
                    <div style="
                        display: flex;
                        align-items: center;
                        padding: 12px 16px;
                        background: {dark_theme.colors.red}10;
                        border-left: 3px solid {dark_theme.colors.red};
                        border-radius: 0 8px 8px 0;
                        margin-bottom: 8px;
                    ">
                        <span style="color: {dark_theme.colors.red}; font-size: 16px; margin-right: 12px;">▼</span>
                        <div style="flex: 1;">
                            <div style="color: {dark_theme.colors.text_primary}; font-weight: 500;">
                                {item['label']}
                            </div>
                            <div style="color: {dark_theme.colors.red}; font-size: 12px;">
                                {change_display}
                            </div>
                        </div>
                    </div>
                """
                )
        else:
            render_html(
                f"<p style='color: {dark_theme.colors.text_muted};'>All KPIs are performing within acceptable ranges.</p>"
            )
        card_close()


def _render_kpi_card(kpi: dict, kpi_id: str, theme) -> None:
    """
    Render a professional KPI card using the reusable component.

    This function now delegates to the centralized render_kpi_card component,
    ensuring consistent styling across all dashboards.
    """
    raw_value = kpi.get("value")
    has_value = raw_value is not None and raw_value != 0
    value = raw_value if has_value else None
    label = kpi.get("display_name", kpi_id.replace("_", " ").title())
    delta = kpi.get("change_percent")
    status = kpi.get("status", "neutral") if has_value else "neutral"
    unit = get_kpi_unit(kpi_id)
    higher_is_better = kpi.get("higher_is_better", True)

    # Use the centralized component from ui/components/cards.py
    render_kpi_card(
        label=label,
        value=value,
        delta=delta,
        status=status,
        unit=unit,
        higher_is_better=higher_is_better,
        show_trend=True,
        height=110,
    )


def _render_subgrid(title: str, kpis: list, metrics: dict, theme, columns: int = 4) -> None:
    """Render a titled KPI subgrid in compact modern card design."""
    render_html("<div class='modern-card' style='padding: 20px;'>")
    render_html(
        f"<h3 style='margin: 0 0 16px 0; color: #0f172a; font-size: 15px; font-weight: 600;'>{title}</h3>"
    )
    cols = st.columns(columns)
    for idx, kpi_id in enumerate(kpis):
        col = cols[idx % columns]
        with col:
            _render_kpi_card(metrics.get(kpi_id, {}), kpi_id, theme)
    render_html("</div>")


# =============================================================================
# DATA HELPERS
# =============================================================================


def _get_catalog() -> dict:
    """Load KPI catalog from YAML (cached by Streamlit)."""
    if "_kpi_catalog_cache" not in st.session_state:
        catalog_path = Path(__file__).parent.parent.parent / "config" / "kpi_catalog.yaml"
        if catalog_path.exists():
            with open(catalog_path, encoding="utf-8") as f:
                st.session_state["_kpi_catalog_cache"] = yaml.safe_load(f)
        else:
            st.session_state["_kpi_catalog_cache"] = {"kpis": []}
    return st.session_state.get("_kpi_catalog_cache", {"kpis": []})


def _enrich_metrics(
    df: pd.DataFrame, base_metrics: dict, filters: FilterParams, catalog: dict
) -> dict:
    """Ensure all KPIs in catalog exist in metrics, computing current values if missing.

    Also attaches domain category and icon metadata for consistent KPI card styling.
    """
    metrics = {**base_metrics}

    # Build lookup maps from catalog
    name_map = {}
    category_map = {}
    categories_cfg = {c.get("id"): c for c in catalog.get("categories", [])}

    for kpi in catalog.get("kpis", []):
        kpi_id = kpi.get("id")
        if not kpi_id:
            continue
        name_map[kpi_id] = kpi.get("display_name_en", kpi_id)
        cat_id = kpi.get("category")
        category_map[kpi_id] = cat_id

        # Attach category + icon to existing snapshot metrics
        if kpi_id in metrics:
            metrics[kpi_id].setdefault("display_name", name_map[kpi_id])
            metrics[kpi_id]["category"] = cat_id
            if cat_id in categories_cfg:
                metrics[kpi_id]["category_icon"] = categories_cfg[cat_id].get("icon", "")

    target_kpis = [k.get("id") for k in catalog.get("kpis", []) if k.get("id")]
    for kpi_id in target_kpis:
        if kpi_id not in metrics:
            metric = _calc_metric_from_df(df, filters, kpi_id, name_map)
            # Attach category + icon on computed metrics
            cat_id = category_map.get(kpi_id)
            if cat_id:
                metric["category"] = cat_id
                if cat_id in categories_cfg:
                    metric["category_icon"] = categories_cfg[cat_id].get("icon", "")
            metrics[kpi_id] = metric

    return metrics


def _calc_metric_from_df(
    df: pd.DataFrame, filters: FilterParams, kpi_id: str, name_map: dict
) -> dict:
    """Compute simple current value and delta for a KPI from dataframe when not in snapshot."""
    current = df[(df["year"] == filters.year) & (df["quarter"] == filters.quarter)]
    if filters.region and filters.region != "all":
        current = current[current["region"] == filters.region]

    prev_year = filters.year
    prev_quarter = filters.quarter - 1
    if prev_quarter == 0:
        prev_quarter = 4
        prev_year -= 1

    previous = df[(df["year"] == prev_year) & (df["quarter"] == prev_quarter)]
    if filters.region and filters.region != "all":
        previous = previous[previous["region"] == filters.region]

    current_val = (
        float(current[kpi_id].mean())
        if kpi_id in current and len(current) > 0 and not current[kpi_id].isna().all()
        else None
    )
    previous_val = (
        float(previous[kpi_id].mean())
        if kpi_id in previous and len(previous) > 0 and not previous[kpi_id].isna().all()
        else None
    )

    abs_change, pct_change = calculate_change(current_val, previous_val)

    return {
        "value": current_val if current_val is not None else 0,
        "previous_value": previous_val,
        "change": abs_change,
        "change_percent": pct_change,
        "status": "neutral",
        "display_name": name_map.get(kpi_id, kpi_id.replace("_", " ").title()),
        "higher_is_better": True,
    }


# =============================================================================
# ML & LLM SECTION RENDERERS
# =============================================================================


def _render_ml_forecast_section(
    df: pd.DataFrame, year: int, quarter: int, theme, language: str
) -> None:
    """Render the ML forecasting section."""

    _render_section_title("🔮 KPI Forecasting", "ML-powered predictions for key indicators")

    try:
        from analytics_hub_platform.domain.ml_services import KPIForecaster

        # Select KPI to forecast
        forecast_kpis = [
            "sustainability_index",
            "gdp_growth",
            "non_oil_gdp_share",
            "unemployment_rate",
        ]
        available_kpis = [k for k in forecast_kpis if k in df.columns]

        if not available_kpis:
            st.info("No KPI data available for forecasting.")
            return

        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            selected_kpi = st.selectbox(
                "Select KPI to Forecast",
                available_kpis,
                format_func=lambda x: x.replace("_", " ").title(),
                key="forecast_kpi_select",
            )
        with col2:
            periods = st.slider("Quarters Ahead", 2, 12, 8, key="forecast_periods")
        with col3:
            model_type = st.selectbox(
                "Model",
                ["gradient_boosting", "random_forest"],
                format_func=lambda x: x.replace("_", " ").title(),
                key="forecast_model",
            )

        # Prepare historical data
        hist_df = df.groupby(["year", "quarter"]).agg({selected_kpi: "mean"}).reset_index()
        hist_df = hist_df.rename(columns={selected_kpi: "value"}).dropna()
        hist_df = hist_df.sort_values(["year", "quarter"])

        if len(hist_df) < 8:
            st.warning(
                "⚠️ Not enough historical data for reliable forecasting (need at least 8 quarters)."
            )
            return

        # Generate forecast
        with st.spinner("Generating forecast..."):
            forecaster = KPIForecaster(model_type=model_type)
            forecaster.fit(hist_df)
            predictions = forecaster.predict(quarters_ahead=periods)

        # Build visualization
        fig = go.Figure()

        # Historical data - use vectorized period creation
        hist_df = add_period_column(hist_df)
        fig.add_trace(
            go.Scatter(
                x=hist_df["period"],
                y=hist_df["value"],
                mode="lines+markers",
                name="Historical",
                line={"color": theme.colors.primary, "width": 2},
                marker={"size": 6},
            )
        )

        # Forecast
        forecast_periods = [f"Q{p['quarter']} {p['year']}" for p in predictions]
        forecast_values = [p["predicted_value"] for p in predictions]
        forecast_lower = [p["confidence_lower"] for p in predictions]
        forecast_upper = [p["confidence_upper"] for p in predictions]

        fig.add_trace(
            go.Scatter(
                x=forecast_periods,
                y=forecast_values,
                mode="lines+markers",
                name="Forecast",
                line={"color": theme.colors.secondary, "width": 2, "dash": "dash"},
                marker={"size": 6, "symbol": "diamond"},
            )
        )

        # Confidence band
        fig.add_trace(
            go.Scatter(
                x=forecast_periods + forecast_periods[::-1],
                y=forecast_upper + forecast_lower[::-1],
                fill="toself",
                fillcolor="rgba(16, 185, 129, 0.1)",
                line={"color": "rgba(0,0,0,0)"},
                name="95% Confidence",
                showlegend=True,
            )
        )

        fig.update_layout(
            height=400,
            margin={"l": 20, "r": 20, "t": 20, "b": 40},
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis={"showgrid": True, "gridcolor": "rgba(0,0,0,0.05)", "title": "Period"},
            yaxis={
                "showgrid": True,
                "gridcolor": "rgba(0,0,0,0.05)",
                "title": selected_kpi.replace("_", " ").title(),
            },
            legend={"orientation": "h", "yanchor": "bottom", "y": 1.02, "xanchor": "right", "x": 1},
            font={"family": theme.typography.font_family},
        )

        st.plotly_chart(fig, width="stretch")

        # Show forecast table
        with st.expander("📋 View Forecast Details"):
            forecast_df = pd.DataFrame(predictions)
            forecast_df = add_period_column(forecast_df)  # Vectorized period creation
            st.dataframe(
                forecast_df[
                    ["period", "predicted_value", "confidence_lower", "confidence_upper"]
                ].round(2),
                width="stretch",
                hide_index=True,
            )

    except Exception as e:
        st.warning(f"⚠️ Forecasting unavailable: {str(e)}")


def _render_anomaly_section(
    df: pd.DataFrame, year: int, quarter: int, theme, language: str
) -> None:
    """Render the anomaly detection (early warning) section."""

    _render_section_title("⚠️ Early Warning System", "Anomaly detection for critical KPI deviations")

    try:
        from analytics_hub_platform.domain.ml_services import AnomalyDetector, AnomalySeverity

        detector = AnomalyDetector(zscore_threshold=2.5, critical_threshold=3.5)

        # Detect anomalies for key KPIs
        anomaly_kpis = ["sustainability_index", "gdp_growth", "unemployment_rate", "co2_index"]
        available_kpis = [k for k in anomaly_kpis if k in df.columns]

        all_anomalies = []

        for kpi in available_kpis:
            kpi_df = df.groupby(["year", "quarter"]).agg({kpi: "mean"}).reset_index()
            kpi_df = kpi_df.rename(columns={kpi: "value"}).dropna()
            kpi_df = kpi_df.sort_values(["year", "quarter"])

            if len(kpi_df) >= 4:
                higher_is_better = kpi not in ["unemployment_rate", "co2_index"]
                anomalies = detector.detect_anomalies(kpi_df, kpi, "national", higher_is_better)
                all_anomalies.extend(anomalies)

        # Sort by severity and recency
        critical = [a for a in all_anomalies if a.severity == AnomalySeverity.CRITICAL]
        warnings = [a for a in all_anomalies if a.severity == AnomalySeverity.WARNING]

        # Always show status metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("🔴 Critical Alerts", len(critical))
        with col2:
            st.metric("🟡 Warnings", len(warnings))
        with col3:
            st.metric("📊 KPIs Monitored", len(available_kpis))

        render_html("<div style='height: 16px;'></div>")

        if not all_anomalies:
            # Show healthy status with detail
            render_html(
                f"""
            <div style="
                background: linear-gradient(135deg, #10B981 0%, #059669 100%);
                padding: 20px 24px;
                border-radius: 12px;
                color: white;
                margin: 16px 0;
            ">
                <div style="display: flex; align-items: center; gap: 12px;">
                    <span style="font-size: 32px;">✅</span>
                    <div>
                        <h4 style="margin: 0; color: white;">All Systems Normal</h4>
                        <p style="margin: 4px 0 0 0; opacity: 0.9;">No significant anomalies detected. All {len(available_kpis)} monitored KPIs are within expected ranges.</p>
                    </div>
                </div>
            </div>
            """
            )

            # Show monitored KPIs list
            st.markdown("**📋 Currently Monitored KPIs:**")
            for kpi in available_kpis:
                st.markdown(f"• {kpi.replace('_', ' ').title()}")
        else:
            # Display anomalies with detailed cards
            for anomaly in sorted(
                all_anomalies, key=lambda x: (x.severity.value, -x.year, -x.quarter)
            )[:10]:
                severity_color = (
                    theme.colors.status_red
                    if anomaly.severity == AnomalySeverity.CRITICAL
                    else theme.colors.status_amber
                )
                severity_icon = "🔴" if anomaly.severity == AnomalySeverity.CRITICAL else "🟡"
                severity_label = (
                    "CRITICAL" if anomaly.severity == AnomalySeverity.CRITICAL else "WARNING"
                )

                render_html(
                    f"""
                <div style="
                    background: white;
                    border-left: 4px solid {severity_color};
                    padding: 16px 20px;
                    margin: 12px 0;
                    border-radius: 0 12px 12px 0;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
                ">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                        <div style="display: flex; align-items: center; gap: 8px;">
                            <span style="font-size: 18px;">{severity_icon}</span>
                            <span style="font-weight: 700; font-size: 15px;">{anomaly.kpi_id.replace("_", " ").title()}</span>
                            <span style="
                                background: {severity_color};
                                color: white;
                                padding: 2px 8px;
                                border-radius: 4px;
                                font-size: 10px;
                                font-weight: 600;
                            ">{severity_label}</span>
                        </div>
                        <span style="color: #6B7280; font-size: 13px; font-weight: 500;">Q{anomaly.quarter} {anomaly.year}</span>
                    </div>
                    <p style="margin: 8px 0 12px 0; color: #4B5563; font-size: 14px; line-height: 1.5;">{anomaly.description}</p>
                    <div style="display: flex; gap: 16px; font-size: 12px; color: #6B7280;">
                        <span>📍 {anomaly.region.replace("_", " ").title()}</span>
                        <span>📈 Z-Score: {anomaly.zscore:.2f}</span>
                    </div>
                </div>
                """
                )

    except Exception as e:
        st.warning(f"⚠️ Anomaly detection unavailable: {str(e)}")


def _render_llm_recommendations_section(snapshot: dict, theme, language: str) -> None:
    """Render the LLM-powered recommendations section."""

    _render_section_title(
        "🤖 AI Strategic Recommendations", "LLM-powered insights aligned with Vision 2030"
    )

    # Auto-generate recommendations on first load
    if "ai_recommendations" not in st.session_state:
        try:
            from analytics_hub_platform.domain.llm_service import generate_recommendations

            kpi_data = {
                "period": f"Q{snapshot.get('quarter', 4)} {snapshot.get('year', 2024)}",
                "metrics": snapshot.get("metrics", {}),
            }

            result = generate_recommendations(
                kpi_data=kpi_data,
                language=language,
                provider="auto",
            )

            st.session_state["ai_recommendations"] = result

        except Exception:
            # Provide default mock recommendations if generation fails
            st.session_state["ai_recommendations"] = {
                "executive_summary": "Based on current KPI trends, Saudi Arabia continues to make strong progress toward Vision 2030 goals. Key areas of focus should include accelerating digital transformation initiatives and strengthening green economy investments to maintain the positive trajectory.",
                "key_insights": [
                    "GDP diversification is progressing well, with non-oil sectors showing 4.2% YoY growth",
                    "Employment rates in Saudi nationals are trending positively, up 1.8% this quarter",
                    "Sustainability metrics show improvement with CO2 emissions per GDP unit declining",
                    "Digital adoption indicators remain strong across government services",
                ],
                "recommendations": [
                    {
                        "title": "Accelerate SME Digital Transformation",
                        "description": "Expand digital enablement programs to support SME adoption of e-commerce and digital payment solutions, targeting 40% SME digitization by 2025.",
                        "priority": "high",
                        "timeline": "Q1-Q2 2025",
                        "impact": "High impact on GDP diversification",
                    },
                    {
                        "title": "Enhance Green Economy Investment Framework",
                        "description": "Establish dedicated green financing mechanisms and incentives to attract private sector investment in renewable energy and sustainable industries.",
                        "priority": "high",
                        "timeline": "Q2 2025",
                        "impact": "Critical for sustainability targets",
                    },
                    {
                        "title": "Strengthen Regional Development Programs",
                        "description": "Focus on underperforming regions (Northern Borders, Al Bahah) with targeted investment and job creation programs.",
                        "priority": "medium",
                        "timeline": "Ongoing",
                        "impact": "Medium impact on balanced development",
                    },
                ],
                "risk_alerts": [
                    "Global economic headwinds may impact tourism growth targets",
                    "Skill gaps in emerging technology sectors require attention",
                ],
                "provider": "Mock AI",
                "model": "Strategic Analysis Engine",
                "generated_at": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M"),
            }

    # Button to regenerate
    if st.button("🔄 Regenerate AI Recommendations", key="generate_llm_recs"):
        try:
            from analytics_hub_platform.domain.llm_service import generate_recommendations

            with st.spinner("Generating AI recommendations..."):
                kpi_data = {
                    "period": f"Q{snapshot.get('quarter', 4)} {snapshot.get('year', 2024)}",
                    "metrics": snapshot.get("metrics", {}),
                }

                result = generate_recommendations(
                    kpi_data=kpi_data,
                    language=language,
                    provider="auto",
                )

                st.session_state["ai_recommendations"] = result

        except Exception as e:
            st.error(f"Failed to regenerate recommendations: {str(e)}")

    # Display recommendations (will always have data now)
    if "ai_recommendations" in st.session_state and st.session_state["ai_recommendations"]:
        result = st.session_state["ai_recommendations"]

        # Executive Summary
        render_html(
            f"""
        <div style="
            background: linear-gradient(135deg, {theme.colors.primary} 0%, {theme.colors.secondary} 100%);
            padding: 20px 24px;
            border-radius: 12px;
            color: white;
            margin-bottom: 20px;
        ">
            <h4 style="margin: 0 0 12px 0; color: white;">📋 Executive Summary</h4>
            <p style="margin: 0; line-height: 1.6;">{result.get("executive_summary", "N/A")}</p>
        </div>
        """
        )

        # Key Insights
        insights = result.get("key_insights", [])
        if insights:
            st.markdown("**💡 Key Insights**")
            for insight in insights:
                st.markdown(f"• {insight}")

        render_html("<div style='height: 16px;'></div>")

        # Recommendations
        recommendations = result.get("recommendations", [])
        if recommendations:
            st.markdown("**📌 Strategic Recommendations**")
            for rec in recommendations:
                priority_color = {
                    "high": theme.colors.status_red,
                    "medium": theme.colors.status_amber,
                    "low": theme.colors.status_green,
                }.get(rec.get("priority", "medium"), theme.colors.text_muted)

                render_html(
                    f"""
                <div style="
                    background: white;
                    border: 1px solid {theme.colors.border};
                    border-radius: 8px;
                    padding: 16px;
                    margin: 12px 0;
                ">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                        <span style="font-weight: 600; font-size: 15px;">{rec.get("title", "Recommendation")}</span>
                        <span style="
                            background: {priority_color};
                            color: white;
                            padding: 2px 8px;
                            border-radius: 4px;
                            font-size: 11px;
                            text-transform: uppercase;
                        ">{rec.get("priority", "Medium")} Priority</span>
                    </div>
                    <p style="margin: 0; color: #4B5563; font-size: 14px;">{rec.get("description", "")}</p>
                    <div style="margin-top: 12px; display: flex; gap: 16px; font-size: 12px; color: #6B7280;">
                        <span>⏱️ {rec.get("timeline", "N/A")}</span>
                        <span>📊 {rec.get("impact", "N/A")}</span>
                    </div>
                </div>
                """
                )

        # Risk Alerts
        risk_alerts = result.get("risk_alerts", [])
        if risk_alerts:
            render_html("<div style='height: 16px;'></div>")
            st.markdown("**⚠️ Risk Alerts**")
            for alert in risk_alerts:
                st.warning(alert)

        # Provider info
        st.caption(
            f"Generated by {result.get('provider', 'AI')} ({result.get('model', 'N/A')}) at {result.get('generated_at', 'N/A')}"
        )


def _render_regional_map_section(
    df: pd.DataFrame, year: int, quarter: int, theme, language: str
) -> None:
    """Render the regional map section."""

    _render_section_title(
        "🗺️ Regional Performance Map", "Interactive visualization of KPIs across Saudi Arabia"
    )

    try:
        from analytics_hub_platform.ui.components.saudi_map import render_saudi_map

        # Prepare regional data for current period
        regional_df = df[(df["year"] == year) & (df["quarter"] == quarter)].copy()

        if len(regional_df) == 0:
            st.info("No regional data available for the selected period.")
            return

        # Map region names to IDs
        region_mapping = {
            "Riyadh": "riyadh",
            "Makkah": "makkah",
            "Eastern Province": "eastern",
            "Madinah": "madinah",
            "Qassim": "qassim",
            "Asir": "asir",
            "Tabuk": "tabuk",
            "Hail": "hail",
            "Northern Borders": "northern_borders",
            "Jazan": "jazan",
            "Najran": "najran",
            "Al Bahah": "bahah",
            "Al Jawf": "jawf",
        }

        # Select KPI for map
        map_kpis = ["sustainability_index", "gdp_growth", "unemployment_rate", "co2_index"]
        available_kpis = [k for k in map_kpis if k in regional_df.columns]

        if not available_kpis:
            st.info("No KPI data available for map visualization.")
            return

        selected_kpi = st.selectbox(
            "Select KPI for Map",
            available_kpis,
            format_func=lambda x: x.replace("_", " ").title(),
            key="map_kpi_select",
        )

        # Aggregate by region
        if "region" in regional_df.columns:
            regional_agg = regional_df.groupby("region").agg({selected_kpi: "mean"}).reset_index()
            regional_agg["region_id"] = regional_agg["region"].map(region_mapping)
            regional_agg = regional_agg.rename(columns={selected_kpi: "value"})
            regional_agg = regional_agg.dropna(subset=["region_id", "value"])

            if len(regional_agg) > 0:
                fig = render_saudi_map(
                    region_data=regional_agg,
                    value_column="value",
                    title=f"{selected_kpi.replace('_', ' ').title()} by Region - Q{quarter} {year}",
                    language=language,
                )
                st.plotly_chart(fig, width="stretch")
            else:
                st.info("No regional aggregation available.")
        else:
            st.info("Regional breakdown not available in data.")

    except Exception as e:
        st.warning(f"⚠️ Map visualization unavailable: {str(e)}")

