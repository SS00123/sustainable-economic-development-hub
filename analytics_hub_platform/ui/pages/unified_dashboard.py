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
    get_data_quality_metrics,
    get_executive_snapshot,
    get_sustainability_summary,
)
from analytics_hub_platform.infrastructure.repository import get_repository
from analytics_hub_platform.infrastructure.settings import get_settings
from analytics_hub_platform.locale import get_strings
from analytics_hub_platform.ui.components.cards import (
    render_kpi_card,
)
from analytics_hub_platform.ui.dark_components import (
    apply_dark_chart_layout,
    card_close,
    card_open,
    render_mini_metric,
    render_sidebar,
    render_status_overview,
)
from analytics_hub_platform.ui.dark_components import (
    render_header as render_dark_header,
)
from analytics_hub_platform.ui.dark_components import (
    render_section_title as render_dark_section_title,
)

# Import dark theme components
from analytics_hub_platform.ui.dark_theme import get_dark_theme
from analytics_hub_platform.utils.dataframe_adapter import add_period_column
from analytics_hub_platform.utils.kpi_utils import get_kpi_unit
from analytics_hub_platform.utils.narratives import generate_executive_narrative

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

    # Get filter state from session
    year = st.session_state.get("year", 2024)
    quarter = st.session_state.get("quarter", 4)
    region = st.session_state.get("region", "all")
    language = st.session_state.get("language", "en")
    get_strings(language)

    # =========================================================================
    # DARK 3D LAYOUT: SIDEBAR + MAIN CONTENT
    # =========================================================================
    side_col, main_col = st.columns([0.22, 0.78], gap="large")

    with side_col:
        render_sidebar(active="Dashboard")

    with main_col:
        # Top header bar
        datetime.now().date()
        period_text = f"Q{quarter} {year}"
        render_dark_header(title="Overview", period_text=f"Period: {period_text}")

        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

        # Compact filter row
        with st.container():
            col_f1, col_f2, col_f3, col_f4 = st.columns([1, 1, 1.5, 1])
            with col_f1:
                new_year = st.selectbox(
                    "Year",
                    [2024, 2023, 2022, 2021],
                    index=[2024, 2023, 2022, 2021].index(year),
                    key="filter_year",
                )
            with col_f2:
                new_quarter = st.selectbox(
                    "Quarter", [1, 2, 3, 4], index=quarter - 1, key="filter_quarter"
                )
            with col_f3:
                regions = [
                    "all",
                    "Riyadh",
                    "Makkah",
                    "Eastern Province",
                    "Madinah",
                    "Qassim",
                    "Asir",
                    "Tabuk",
                    "Hail",
                    "Northern Borders",
                    "Jazan",
                    "Najran",
                    "Al Bahah",
                    "Al Jawf",
                ]
                new_region = st.selectbox(
                    "Region",
                    regions,
                    index=regions.index(region) if region in regions else 0,
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
            settings = get_settings()

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
        # TOP ROW: ECONOMIC ACTIVITY INDEX + BY REGION
        # =========================================================================
        st.markdown(
            "<div id='section-overview' style='height: 16px;'></div>", unsafe_allow_html=True
        )

        # Status summary for display
        green_count = sum(1 for m in metrics.values() if m.get("status") == "green")
        amber_count = sum(1 for m in metrics.values() if m.get("status") == "amber")
        red_count = sum(1 for m in metrics.values() if m.get("status") == "red")

        # Status overview row
        card_open("Performance Overview", f"Q{quarter} {year} • {len(metrics)} KPIs tracked")
        render_status_overview(green_count, amber_count, red_count)
        card_close()

        st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

        r1c1, r1c2 = st.columns([0.48, 0.52], gap="large")

        with r1c1:
            # Economic Activity Index - Line chart with trend
            _render_activity_chart(df, year, quarter, region, dark_theme)

        with r1c2:
            # By Region - Horizontal bars
            _render_region_bars(df, year, quarter, dark_theme)

        st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

        # =========================================================================
        # MIDDLE ROW: ENERGY MIX DONUT + MINI METRICS
        # =========================================================================
        r2c1, r2c2 = st.columns([0.42, 0.58], gap="large")

        with r2c1:
            # Energy Mix / Sustainability breakdown donut
            _render_energy_mix_donut(sustainability, dark_theme)

        with r2c2:
            # Two mini metric cards side by side
            m1, m2 = st.columns(2, gap="large")

            # Green Jobs metric
            green_jobs = metrics.get("green_jobs", {})
            green_jobs_val = green_jobs.get("value", 0) or 0
            green_jobs_delta = green_jobs.get("change_percent", 0) or 0

            with m1:
                render_mini_metric(
                    title="New Green Jobs",
                    value=f"{green_jobs_val / 1000:.1f}K"
                    if green_jobs_val >= 1000
                    else str(int(green_jobs_val)),
                    delta=float(green_jobs_delta),
                    ring_percent=min(90, max(10, green_jobs_val / 1000)),
                    subtitle="vs previous period",
                )

            # FDI / Investment metric
            fdi = metrics.get("foreign_investment", metrics.get("fdi", {}))
            fdi_val = fdi.get("value", 0) or 0
            fdi_delta = fdi.get("change_percent", 0) or 0

            with m2:
                render_mini_metric(
                    title="Foreign Investment",
                    value=f"{fdi_val:.1f}B" if fdi_val >= 1 else f"{fdi_val * 1000:.0f}M",
                    delta=float(fdi_delta),
                    ring_percent=min(95, max(15, 50 + fdi_delta)),
                    subtitle="FDI inflows",
                )

        st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

        # =========================================================================
        # BOTTOM ROW: YEARLY KPIs GROUPED BAR CHART
        # =========================================================================
        _render_yearly_kpis_chart(df, region, dark_theme)

        st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

        # =========================================================================
        # SECTION: SUSTAINABILITY INDEX
        # =========================================================================
        render_dark_section_title(
            "🌱 Sustainability Index", "Composite score for sustainable development"
        )
        _render_sustainability_gauge(sustainability, dark_theme, theme)

        st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

        # =========================================================================
        # SECTION: KEY PERFORMANCE INDICATORS
        # =========================================================================
        st.markdown("<div id='section-kpis'></div>", unsafe_allow_html=True)
        render_dark_section_title(
            "📊 Key Performance Indicators", f"Core metrics for Q{quarter} {year}"
        )

        # KPI subgrids by category
        _render_dark_subgrid(
            "Economic Performance",
            [
                "gdp_growth",
                "gdp_total",
                "foreign_investment",
                "export_diversity_index",
                "economic_complexity",
            ],
            metrics,
            dark_theme,
        )

        _render_dark_subgrid(
            "Labor & Skills",
            [
                "unemployment_rate",
                "green_jobs",
                "skills_gap_index",
                "population",
            ],
            metrics,
            dark_theme,
            columns=4,
        )

        _render_dark_subgrid(
            "Social & Digital",
            [
                "social_progress_score",
                "digital_readiness",
                "innovation_index",
            ],
            metrics,
            dark_theme,
            columns=3,
        )

        _render_dark_subgrid(
            "Environmental & Sustainability",
            [
                "sustainability_index",
                "co2_index",
                "co2_total",
                "renewable_share",
                "energy_intensity",
                "water_efficiency",
                "waste_recycling_rate",
                "forest_coverage",
                "air_quality_index",
            ],
            metrics,
            dark_theme,
            columns=4,
        )

        st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

        # =========================================================================
        # SECTION 3: TREND ANALYSIS
        # =========================================================================
        st.markdown("<div id='section-trends' style='height: 8px;'></div>", unsafe_allow_html=True)
        render_dark_section_title("📈 Trend Analysis", "Historical performance over time")
        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

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
        # SECTION 4: REGIONAL COMPARISON
        # =========================================================================
        st.markdown("<div id='section-regions' style='height: 8px;'></div>", unsafe_allow_html=True)
        render_dark_section_title("🗺️ Regional Comparison", "Performance across regions")
        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

        card_open("Regional Performance", "Sustainability index by region")
        regional_df = df[(df["year"] == year) & (df["quarter"] == quarter)].copy()

        if len(regional_df) > 0:
            reg_col1, reg_col2 = st.columns([2, 1])

            with reg_col1:
                regional_agg = (
                    regional_df.groupby("region")
                    .agg({"sustainability_index": "mean"})
                    .reset_index()
                )
                regional_agg = regional_agg.sort_values("sustainability_index", ascending=True)
                national_avg = regional_agg["sustainability_index"].mean()

                colors = [
                    dark_theme.colors.purple if v >= national_avg else dark_theme.colors.pink
                    for v in regional_agg["sustainability_index"]
                ]

                fig = go.Figure()
                fig.add_trace(
                    go.Bar(
                        y=regional_agg["region"],
                        x=regional_agg["sustainability_index"],
                        orientation="h",
                        marker_color=colors,
                        text=[f"{v:.1f}" for v in regional_agg["sustainability_index"]],
                        textposition="outside",
                        textfont={"color": "#94a3b8"},
                    )
                )
                fig.add_vline(
                    x=national_avg,
                    line_dash="dash",
                    line_color=dark_theme.colors.cyan,
                    annotation_text=f"Avg: {national_avg:.1f}",
                    annotation_font={"color": "#94a3b8"},
                )

                apply_dark_chart_layout(fig, height=400)
                fig.update_layout(
                    xaxis={
                        "showgrid": True,
                        "gridcolor": "rgba(255,255,255,0.05)",
                        "title": "Sustainability Index",
                        "title_font": {"color": "#94a3b8"},
                    },
                    yaxis={"showgrid": False},
                )
                st.plotly_chart(fig, width="stretch")

            with reg_col2:
                st.markdown(
                    """
                    <div style="color: #e2e8f0; font-size: 14px; font-weight: 600; margin-bottom: 16px;">
                        📊 Regional Statistics
                    </div>
                """,
                    unsafe_allow_html=True,
                )

                for label, value in [
                    ("National Average", f"{national_avg:.1f}"),
                    ("Highest", f"{regional_agg['sustainability_index'].max():.1f}"),
                    ("Lowest", f"{regional_agg['sustainability_index'].min():.1f}"),
                ]:
                    st.markdown(
                        f"""
                        <div style="background: #1e2340; padding: 12px; border-radius: 8px; margin-bottom: 8px;">
                            <div style="font-size: 11px; color: #94a3b8;">{label}</div>
                            <div style="font-size: 18px; font-weight: 700; color: #f1f5f9;">{value}</div>
                        </div>
                    """,
                        unsafe_allow_html=True,
                    )

                st.markdown(
                    """
                    <div style="color: #e2e8f0; font-size: 13px; font-weight: 600; margin: 16px 0 8px 0;">
                        🏆 Top 3 Regions
                    </div>
                """,
                    unsafe_allow_html=True,
                )
                for _, row in regional_agg.tail(3).iloc[::-1].iterrows():
                    st.markdown(
                        f"""
                        <div style="color: #94a3b8; font-size: 12px; padding: 4px 0;">
                            • {row["region"]}: <b style="color: #a855f7;">{row["sustainability_index"]:.1f}</b>
                        </div>
                    """,
                        unsafe_allow_html=True,
                    )
        else:
            st.info("No regional data available for this period.")

        card_close()

        # =========================================================================
        # SECTION 5: ENVIRONMENTAL TRENDS
        # =========================================================================
        st.markdown(
            "<div id='section-environment' style='height: 8px;'></div>", unsafe_allow_html=True
        )
        render_dark_section_title(
            "🌿 Sustainability & Environmental Trends", "Multi-indicator performance"
        )
        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

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

        trend_env = (
            df.groupby(["year", "quarter"])
            .agg({k: "mean" for k in env_kpis if k in df.columns})
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

        for i, kpi in enumerate(env_kpis):
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
        card_close()

        # =========================================================================
        # SECTION 6: DATA QUALITY
        # =========================================================================
        st.markdown(
            "<div id='section-data-quality' style='height: 8px;'></div>", unsafe_allow_html=True
        )
        render_dark_section_title("✅ Data Quality Overview", "Completeness and quality metrics")
        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

        card_open("Quality Metrics", "Data health indicators")

        dq_col1, dq_col2, dq_col3, dq_col4 = st.columns(4)
        completeness = quality_metrics.get("completeness", 0)
        avg_quality = quality_metrics.get("avg_quality_score") or 0
        records = quality_metrics.get("records_count", 0)
        last_update = quality_metrics.get("last_update")
        update_str = last_update.strftime("%Y-%m-%d") if last_update else "N/A"

        for col, (label_text, value_text) in zip(
            [dq_col1, dq_col2, dq_col3, dq_col4],
            [
                ("Completeness", f"{completeness:.1f}%"),
                ("Quality Score", f"{avg_quality:.1f}"),
                ("Records", f"{records:,}"),
                ("Last Updated", update_str),
            ],
            strict=False,
        ):
            with col:
                st.markdown(
                    f"""
                    <div style="background: #1e2340; padding: 16px; border-radius: 8px; text-align: center;">
                        <div style="font-size: 11px; color: #94a3b8; text-transform: uppercase;">{label_text}</div>
                        <div style="font-size: 20px; font-weight: 700; color: #f1f5f9; margin-top: 4px;">{value_text}</div>
                    </div>
                """,
                    unsafe_allow_html=True,
                )

        card_close()

        # =========================================================================
        # SECTION 7: INSIGHTS & NARRATIVE
        # =========================================================================
        st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
        render_dark_section_title("💡 Strategic Insights", "AI-generated executive briefing")
        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

        card_open("Executive Summary", "Key findings and recommendations")
        narrative = generate_executive_narrative(snapshot, language)

        st.markdown(
            f"""
            <div style="
                background: linear-gradient(145deg, #1e2340 0%, #252a4a 100%);
                border-left: 4px solid {dark_theme.colors.purple};
                border-radius: 8px;
                padding: 24px;
                line-height: 1.8;
                font-size: 14px;
                color: #cbd5e1;
                max-height: 500px;
                overflow-y: auto;
            ">
                {narrative.replace(chr(10), "<br>")}
            </div>
        """,
            unsafe_allow_html=True,
        )
        card_close()

        # =========================================================================
        # ADVANCED ANALYTICS SECTION
        # =========================================================================
        st.markdown(
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
        """,
            unsafe_allow_html=True,
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

        st.markdown("<div style='height: 48px;'></div>", unsafe_allow_html=True)

        # =========================================================================
        # PROFESSIONAL FOOTER
        # =========================================================================
        st.markdown(
            f"""
            <div style="
                border-top: 1px solid #2d3555;
                padding: 24px 0;
                text-align: center;
                background: #121532;
                border-radius: 0 0 12px 12px;
                margin-top: 24px;
            ">
                <p style="color: #64748b; font-size: 12px; margin: 0 0 8px 0;">
                    Sustainable Economic Development Analytics Hub • Ministry of Economy and Planning
                </p>
                <p style="color: #64748b; font-size: 11px; margin: 0;">
                    Developed by {BRANDING["author_name"]} • {BRANDING["author_mobile"]} • {BRANDING["author_email"]}
                </p>
            </div>
        """,
            unsafe_allow_html=True,
        )


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
    st.markdown(
        f"""
        <div style="text-align: center; margin-top: -10px;">
            <span style="background: {status_color}22; color: {status_color}; padding: 6px 16px;
                        border-radius: 6px; font-size: 13px; font-weight: 600;">
                {status_text} • Target: 70
            </span>
        </div>
    """,
        unsafe_allow_html=True,
    )
    card_close()


def _render_dark_subgrid(
    title: str, kpis: list, metrics: dict, dark_theme, columns: int = 4
) -> None:
    """Render KPI cards in a dark-themed grid."""
    st.markdown(
        f"""
        <div style="margin: 16px 0 12px 0;">
            <span style="font-size: 14px; font-weight: 600; color: #e2e8f0;">{title}</span>
        </div>
    """,
        unsafe_allow_html=True,
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

            st.markdown(
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
            """,
                unsafe_allow_html=True,
            )


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def _render_section_title(title: str, subtitle: str = "") -> None:
    """Render a modern section title."""
    st.markdown(
        f"""
        <div class='section-header'>
            <span>{title}</span>
        </div>
        <div class='section-subtitle'>{subtitle}</div>
        """,
        unsafe_allow_html=True,
    )


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
    st.markdown("<div class='modern-card' style='padding: 20px;'>", unsafe_allow_html=True)
    st.markdown(
        f"<h3 style='margin: 0 0 16px 0; color: #0f172a; font-size: 15px; font-weight: 600;'>{title}</h3>",
        unsafe_allow_html=True,
    )
    cols = st.columns(columns)
    for idx, kpi_id in enumerate(kpis):
        col = cols[idx % columns]
        with col:
            _render_kpi_card(metrics.get(kpi_id, {}), kpi_id, theme)
    st.markdown("</div>", unsafe_allow_html=True)


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
                width=None,
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

        st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

        if not all_anomalies:
            # Show healthy status with detail
            st.markdown(
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
            """,
                unsafe_allow_html=True,
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

                st.markdown(
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
                """,
                    unsafe_allow_html=True,
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
        st.markdown(
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
        """,
            unsafe_allow_html=True,
        )

        # Key Insights
        insights = result.get("key_insights", [])
        if insights:
            st.markdown("**💡 Key Insights**")
            for insight in insights:
                st.markdown(f"• {insight}")

        st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

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

                st.markdown(
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
                """,
                    unsafe_allow_html=True,
                )

        # Risk Alerts
        risk_alerts = result.get("risk_alerts", [])
        if risk_alerts:
            st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
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
