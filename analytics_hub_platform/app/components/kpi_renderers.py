"""KPI renderer components: cards for displaying KPI metrics.

Canonical implementations migrated from ui.dark_components.
"""

from __future__ import annotations

import numpy as np
import plotly.graph_objects as go
import streamlit as st

from analytics_hub_platform.ui.html import render_html
from analytics_hub_platform.ui.theme import get_dark_theme
from analytics_hub_platform.app.components.card_wrappers import card_open, card_close
from analytics_hub_platform.app.components.kpi_svg import (
    create_alert_badge,
    create_sparkline_svg,
)


def render_kpi_card(
    title: str,
    value: str | float | int,
    delta: float | None = None,
    unit: str = "",
    subtitle: str = "",
    height: int = 140,
    accent_color: str | None = None,
    icon: str = "",
) -> None:
    """
    Render a premium KPI metric card with glassmorphism dark theme.

    Args:
        title: KPI label/name
        value: Current value
        delta: Change percentage from previous period
        unit: Unit suffix for the value
        subtitle: Additional context text
        height: Card height in pixels
        accent_color: Optional accent color for glow effect
        icon: Optional emoji/icon to display
    """
    theme = get_dark_theme()

    # Format value
    if isinstance(value, float):
        display_value = f"{value:,.1f}" if value < 1000 else f"{value:,.0f}"
    elif isinstance(value, int):
        display_value = f"{value:,}"
    else:
        display_value = str(value)

    # Delta HTML with enhanced styling
    delta_html = ""
    if delta is not None:
        if delta >= 0:
            delta_class = "positive"
            arrow = "↑"
            glow_color = theme.colors.green
        else:
            delta_class = "negative"
            arrow = "↓"
            glow_color = theme.colors.red
        delta_html = f"""
        <div class='delta {delta_class}' style='
            display: inline-flex;
            align-items: center;
            gap: 4px;
            margin-top: 12px;
            box-shadow: 0 0 20px {glow_color}20;
        '>
            <span style="font-size: 14px;">{arrow}</span>
            <span>{abs(delta):.1f}%</span>
        </div>
        """

    # Accent glow effect
    accent_style = ""
    if accent_color:
        accent_style = f"""
            border-left: 3px solid {accent_color};
            box-shadow:
                0 4px 6px rgba(0, 0, 0, 0.1),
                0 20px 50px rgba(0, 0, 0, 0.4),
                -6px 0 30px {accent_color}20,
                inset 0 1px 0 rgba(255, 255, 255, 0.08);
        """

    # Icon display
    icon_html = ""
    if icon:
        icon_html = f"""
        <div style="
            position: absolute;
            top: 16px;
            right: 16px;
            font-size: 28px;
            opacity: 0.4;
            filter: grayscale(20%);
        ">{icon}</div>
        """

    card_html = f"""
    <div class="dark-card" style="min-height: {height - 20}px; position: relative; {accent_style}">
        {icon_html}
        <div class="card-title" style="margin-bottom: 8px;">{title}</div>
        <div style="display: flex; align-items: baseline; flex-wrap: wrap; margin-top: 8px;">
            <span class="card-value" style="
                font-size: 36px;
                font-weight: 800;
                background: linear-gradient(135deg, rgba(255,255,255,0.98), rgba(255,255,255,0.82));
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                letter-spacing: -0.5px;
            ">{display_value}</span>
            <span style="font-size: 14px; color: rgba(255,255,255,0.5); margin-left: 6px; font-weight: 500;">{unit}</span>
        </div>
        {delta_html}
        <div class="card-sub" style="margin-top: 10px; font-size: 12px; line-height: 1.4;">{subtitle}</div>
    </div>
    """
    render_html(card_html)


def render_mini_metric(
    title: str,
    value: str,
    delta: float,
    ring_percent: float,
    subtitle: str = "vs previous period",
    ring_color: str = "#a855f7",
) -> None:
    """
    Render a premium mini metric card with animated ring indicator.

    Args:
        title: Metric title
        value: Display value (e.g., "62.5K")
        delta: Change percentage
        ring_percent: Progress ring percentage (0-100)
        subtitle: Subtitle text
        ring_color: Color for the ring indicator
    """
    delta_class = "positive" if delta >= 0 else "negative"
    arrow = "↑" if delta >= 0 else "↓"

    right_html = f"""
    <span class='delta {delta_class}' style='font-size: 11px; padding: 3px 10px;'>
        <span style="font-size: 12px;">{arrow}</span> {abs(delta):.1f}%
    </span>
    """
    card_open(title=title, subtitle=subtitle, right_html=right_html, glow=True)

    c1, c2 = st.columns([0.55, 0.45], gap="small")
    with c1:
        render_html(
            f"""
            <div style='margin-top: 4px;'>
                <div class='card-value' style='
                    font-size: 28px;
                    font-weight: 800;
                    background: linear-gradient(135deg, rgba(255,255,255,0.98), rgba(255,255,255,0.8));
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    background-clip: text;
                '>{value}</div>
                <div style='margin-top: 10px; color: rgba(255,255,255,0.4); font-size: 11px; font-weight: 500;'>
                    Updated monthly
                </div>
            </div>
            """
        )
    with c2:
        ring = float(np.clip(ring_percent, 0, 100))
        # Create gradient colors for the ring
        fig = go.Figure(
            data=[
                go.Pie(
                    values=[ring, 100 - ring],
                    hole=0.76,
                    sort=False,
                    direction="clockwise",
                    marker={
                        "colors": [ring_color, "rgba(255,255,255,0.06)"],
                        "line": {"width": 0},
                    },
                    textinfo="none",
                    hoverinfo="skip",
                )
            ]
        )
        fig.update_layout(
            height=110,
            margin={"l": 0, "r": 0, "t": 0, "b": 0},
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            showlegend=False,
            annotations=[
                {
                    "text": f"<b>{ring:.0f}%</b>",
                    "x": 0.5,
                    "y": 0.5,
                    "showarrow": False,
                    "font": {"color": "rgba(255,255,255,0.88)", "size": 14},
                }
            ],
        )
        st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})

    card_close()


def render_enhanced_kpi_card(
    title: str,
    value: str | float,
    delta: float | None = None,
    delta_suffix: str = "%",
    sparkline_data: list[float] | None = None,
    alert_type: str | None = None,
    icon: str = "📊",
    color: str = "#a855f7",
    target: float | None = None,
    status: str | None = None,
) -> None:
    """
    Render an enhanced KPI card with sparkline and optional alert badge.

    Args:
        title: KPI title
        value: Main value to display
        delta: Change value (positive/negative)
        delta_suffix: Suffix for delta value
        sparkline_data: List of values for sparkline
        alert_type: Alert badge type ('critical', 'warning', 'info', None)
        icon: Icon emoji
        color: Accent color for the card
        target: Target value for comparison
        status: Status label ('On Track', 'Watch', 'Off Track')
    """
    delta_class = "positive" if delta and delta >= 0 else "negative"
    delta_icon = "↑" if delta and delta >= 0 else "↓"
    delta_html = ""
    if delta is not None:
        delta_html = f"""
        <span class="kpi-delta {delta_class}">
            {delta_icon} {abs(delta):.1f}{delta_suffix}
        </span>"""

    alert_html = create_alert_badge(alert_type) if alert_type else ""

    sparkline_html = ""
    if sparkline_data and len(sparkline_data) >= 2:
        spark_color = "#10b981" if delta and delta >= 0 else "#ef4444"
        sparkline_html = f"""
        <div class="sparkline-container">
            {create_sparkline_svg(sparkline_data, width=120, height=35, color=spark_color, fill_color=spark_color)}
        </div>"""

    # Target and Status HTML
    target_html = ""
    if target is not None:
        target_html = f"""
        <div style="font-size: 11px; color: rgba(255,255,255,0.5); margin-top: 4px;">
            Target: <span style="color: rgba(255,255,255,0.8);">{target}</span>
        </div>
        """

    status_html = ""
    if status:
        status_colors = {
            "On Track": "#10b981",
            "Watch": "#f59e0b",
            "Off Track": "#ef4444",
        }
        s_color = status_colors.get(status, "#a855f7")
        status_html = f"""
        <div style="
            display: inline-block;
            padding: 2px 8px;
            border-radius: 12px;
            background: {s_color}20;
            border: 1px solid {s_color}40;
            color: {s_color};
            font-size: 10px;
            font-weight: 600;
            text-transform: uppercase;
            margin-top: 6px;
        ">
            {status}
        </div>
        """

    html = f"""
    <div class="kpi-card-enhanced" style="--accent-color: {color}">
        {alert_html}
        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
            <div class="kpi-label">{icon} {title}</div>
            {status_html}
        </div>
        <div class="kpi-value">{value}</div>
        {delta_html}
        {target_html}
        {sparkline_html}
    </div>
    """
    render_html(html)
