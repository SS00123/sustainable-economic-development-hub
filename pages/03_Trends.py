"""
Trends Page
Time-series Analysis and Historical Performance

Displays:
- Selectable indicator trends over time
- Regional comparison charts
- Environmental multi-indicator trends
- Volatility and variance analysis
"""

import numpy as np
import plotly.graph_objects as go
import streamlit as st
from analytics_hub_platform.ui.html import render_html

# Page configuration
st.set_page_config(
    page_title="Trend Analysis",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Import application modules
from analytics_hub_platform.infrastructure.db_init import initialize_database
from analytics_hub_platform.infrastructure.repository import get_repository
from analytics_hub_platform.infrastructure.settings import get_settings
from analytics_hub_platform.ui.dark_components import card_close, card_open, render_sidebar
from analytics_hub_platform.ui.theme import get_dark_css, get_dark_theme
from analytics_hub_platform.ui.html import render_html
from analytics_hub_platform.ui.theme import colors, get_chart_layout_config
from analytics_hub_platform.ui.ui_components import (
    initialize_page_session_state,
    render_page_header,
    section_header,
    spacer,
)
from analytics_hub_platform.utils.dataframe_adapter import add_period_column


def apply_chart_theme(fig: go.Figure, height: int = 400) -> None:
    """Apply dark theme to Plotly chart."""
    config = get_chart_layout_config()
    config["height"] = height
    fig.update_layout(**config)


# Initialize
initialize_page_session_state()
if not st.session_state.get("initialized"):
    initialize_database()
    st.session_state["initialized"] = True

# Apply dark theme using safe renderer
render_html(get_dark_css())
dark_theme = get_dark_theme()

# Layout
side_col, main_col = st.columns([0.2, 0.8], gap="large")

with side_col:
    render_sidebar(active="Trends")

with main_col:
    # Header
    render_page_header(
        "Trend Analysis",
        "Historical performance and time-series analysis",
        "📊"
    )

    # Filters
    col_f1, col_f2 = st.columns([1, 3])
    with col_f1:
        region = st.selectbox(
            "Region",
            [
                "all", "Riyadh", "Makkah", "Eastern Province", "Madinah", "Qassim",
                "Asir", "Tabuk", "Hail", "Northern Borders", "Jazan", "Najran",
                "Al Bahah", "Al Jawf",
            ],
            index=0,
            key="trend_filter_region",
        )
    with col_f2:
        st.info("💡 Analyze historical trends to identify patterns and forecast future performance")

    spacer("md")

    # Load data
    try:
        settings = get_settings()
        repo = get_repository()
        df = repo.get_all_indicators(settings.default_tenant_id)

        # Section 1: Single Indicator Trend
        section_header(
            "Indicator Trends", "Select an indicator to view historical performance", "📈"
        )

        with st.container():
            col1, col2 = st.columns([3, 1])

            with col2:
                kpi_options = {
                    "sustainability_index": "Sustainability Index",
                    "gdp_growth": "GDP Growth",
                    "renewable_share": "Renewable Energy",
                    "co2_index": "CO2 Intensity",
                    "unemployment_rate": "Unemployment",
                    "green_jobs": "Green Jobs",
                    "digital_readiness": "Digital Readiness",
                    "innovation_index": "Innovation Index",
                }
                selected_kpi = st.selectbox(
                    "Select Indicator",
                    list(kpi_options.keys()),
                    format_func=lambda x: kpi_options[x],
                    key="trend_kpi",
                )

            with col1:
                trend_df = df.copy()
                if region != "all":
                    trend_df = trend_df[trend_df["region"] == region]

                trend_agg = (
                    trend_df.groupby(["year", "quarter"]).agg({selected_kpi: "mean"}).reset_index()
                )
                trend_agg = add_period_column(trend_agg)
                trend_agg = trend_agg.sort_values(["year", "quarter"])

                fig = go.Figure()
                fig.add_trace(
                    go.Scatter(
                        x=trend_agg["period"],
                        y=trend_agg[selected_kpi],
                        mode="lines+markers",
                        name=kpi_options[selected_kpi],
                        line={"color": colors.purple, "width": 3},
                        marker={"size": 10, "color": colors.purple},
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
                            line={"color": colors.cyan, "width": 2, "dash": "dash"},
                        )
                    )

                apply_chart_theme(fig, height=350)
                st.plotly_chart(fig, use_container_width=True)

        spacer("lg")

        # Section 2: Regional Comparison
        section_header("Regional Comparison", "Performance across regions for current period", "🗺️")

        year = st.session_state.year
        quarter = st.session_state.quarter

        card_open("Regional Performance", f"Sustainability Index by Region - Q{quarter} {year}")
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

                bar_colors = [
                    colors.purple if v >= national_avg else colors.pink
                    for v in regional_agg["sustainability_index"]
                ]

                fig = go.Figure()
                fig.add_trace(
                    go.Bar(
                        y=regional_agg["region"],
                        x=regional_agg["sustainability_index"],
                        orientation="h",
                        marker_color=bar_colors,
                        text=[f"{v:.1f}" for v in regional_agg["sustainability_index"]],
                        textposition="outside",
                        textfont={"color": colors.text_muted},
                    )
                )
                fig.add_vline(
                    x=national_avg,
                    line_dash="dash",
                    line_color=colors.cyan,
                    annotation_text=f"Avg: {national_avg:.1f}",
                    annotation_font={"color": colors.text_muted},
                )

                apply_chart_theme(fig, height=450)
                fig.update_layout(
                    xaxis={"showgrid": True, "title": "Sustainability Index"},
                    yaxis={"showgrid": False},
                )
                st.plotly_chart(fig, use_container_width=True)

            with reg_col2:
                render_html(
                    f"""
                    <div style="color: {colors.text_secondary}; font-size: 14px; font-weight: 600; margin-bottom: 16px;">
                        📊 Regional Statistics
                    </div>
                    """
                )

                for label, value in [
                    ("National Average", f"{national_avg:.1f}"),
                    ("Highest", f"{regional_agg['sustainability_index'].max():.1f}"),
                    ("Lowest", f"{regional_agg['sustainability_index'].min():.1f}"),
                    ("Std Dev", f"{regional_agg['sustainability_index'].std():.1f}"),
                ]:
                    render_html(
                        f"""
                        <div style="background: {colors.bg_card}; padding: 12px; border-radius: 8px; margin-bottom: 8px;">
                            <div style="font-size: 11px; color: {colors.text_muted};">{label}</div>
                            <div style="font-size: 18px; font-weight: 700; color: {colors.text_primary};">{value}</div>
                        </div>
                        """
                    )
        else:
            st.info("No regional data available")

        card_close()

        spacer("lg")

        # Section 3: Environmental Multi-Indicator Trends
        section_header(
            "Environmental Trends", "Multi-indicator sustainability performance over time", "🌿"
        )

        card_open("Environmental KPIs", "Tracking sustainability metrics")

        env_kpis = [
            "co2_index", "renewable_share", "energy_intensity", "water_efficiency",
            "waste_recycling_rate", "air_quality_index", "forest_coverage", "green_jobs",
        ]

        trend_env = (
            df.groupby(["year", "quarter"])
            .agg({k: "mean" for k in env_kpis if k in df.columns})
            .reset_index()
        )
        trend_env = add_period_column(trend_env)
        trend_env = trend_env.sort_values(["year", "quarter"])

        fig_env = go.Figure()
        chart_colors = list(colors.chart_palette)
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
                    line={"color": chart_colors[i % len(chart_colors)], "width": 2},
                    hovertemplate="<b>%{fullData.name}</b><br>%{x}<br>Value: %{y:.1f}<extra></extra>",
                )
            )

        apply_chart_theme(fig_env, height=420)
        st.plotly_chart(fig_env, use_container_width=True)
        card_close()

    except Exception as e:
        st.error(f"Error loading trend data: {str(e)}")
        import traceback
        st.code(traceback.format_exc())
