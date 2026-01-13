"""
Pillar Section Components
Economic, Labor, Social, and Environmental pillar sections.
"""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from analytics_hub_platform.ui.ui_components import apply_dark_chart_layout
from analytics_hub_platform.ui.dark_components import (
    card_close,
    card_open,
)
from analytics_hub_platform.ui.theme import hex_to_rgba
from analytics_hub_platform.ui.html import render_html
from analytics_hub_platform.utils.dataframe_adapter import add_period_column
from analytics_hub_platform.utils.kpi_utils import get_kpi_unit


def _hex_to_rgba(hex_color: str, alpha: float) -> str:
    """Convert hex color to rgba for Plotly compatibility."""
    return hex_to_rgba(hex_color, alpha)


def render_pillar_section_economic(
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


def render_pillar_section_labor(
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


def render_pillar_section_social(
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


def render_pillar_section_environmental(
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
