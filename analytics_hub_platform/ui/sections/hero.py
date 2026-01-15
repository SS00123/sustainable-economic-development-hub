"""
Hero Section Component
Sustainability gauge and main KPI cards.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from analytics_hub_platform.app.components import create_sparkline_svg
from analytics_hub_platform.ui.html import render_html

if TYPE_CHECKING:
    pass


def render_hero_sustainability_gauge(
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
    previous_value = None
    if sustainability_prev and sustainability_prev.get("status") != "no_data":
        previous_value = sustainability_prev.get("index")

    _delta = ((index_value - previous_value) / previous_value * 100) if previous_value else 0  # noqa: F841

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


def render_hero_kpi_cards(
    metrics: dict,
    dark_theme,
    quality_metrics: dict,
    quality_prev: dict | None,
    df: pd.DataFrame | None = None,
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

    # 2x2 grid
    row1 = st.columns(2, gap="medium")
    row2 = st.columns(2, gap="medium")
    cols = [row1[0], row1[1], row2[0], row2[1]]

    for i, (kpi_id, label, domain_color, icon) in enumerate(hero_kpis):
        with cols[i]:
            sparkline_data = None
            has_alert = False
            alert_type = "info"

            if kpi_id == "data_quality":
                # Special case for data quality score
                val = quality_metrics.get("completeness", 0)
                prev_val = None
                if quality_prev and quality_prev.get("completeness") is not None:
                    prev_val = quality_prev.get("completeness")
                delta = ((val - prev_val) / prev_val * 100) if prev_val else 0
                status = "green" if val >= 80 else "amber" if val >= 60 else "red"
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
                status = kpi.get("status", "neutral")

                # Generate sparkline data from historical data
                if df is not None and not df.empty and kpi_id in df.columns:
                    hist_data = df.sort_values(["year", "quarter"])
                    sparkline_vals = hist_data[kpi_id].dropna().tail(8).tolist()
                    if len(sparkline_vals) >= 2:
                        sparkline_data = sparkline_vals

                # Check for alerts based on status
                if status == "red":
                    has_alert = True
                    alert_type = "critical"
                elif status == "amber":
                    has_alert = True
                    alert_type = "warning"

            _render_hero_kpi_card(
                label=label,
                value=val,
                delta=delta,
                status=status,
                domain_color=domain_color,
                icon=icon,
                kpi_id=kpi_id,
                dark_theme=dark_theme,
                sparkline_data=sparkline_data,
                has_alert=has_alert,
                alert_type=alert_type,
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
