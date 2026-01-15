"""Gauge chart components for KPI visualization.

Provides reusable gauge charts:
- Sustainability index gauge
- Generic KPI gauges with targets
- Status badge rendering

Usage:
    from analytics_hub_platform.app.components.gauge_charts import (
        render_sustainability_gauge,
        render_kpi_gauge,
        render_status_badge,
    )
"""

from __future__ import annotations

from typing import Literal

import plotly.graph_objects as go
import streamlit as st

from analytics_hub_platform.app.styles.tokens import (
    colors,
    spacing,
    radius,
    typography,
)
from analytics_hub_platform.ui.html import render_html


def render_sustainability_gauge(
    value: float,
    target: float = 70,
    status: Literal["green", "amber", "red"] | str = "unknown",
    height: int = 350,
    show_status_badge: bool = True,
) -> None:
    """Render a sustainability index gauge with target threshold.

    Args:
        value: Current sustainability index value (0-100)
        target: Target value for threshold indicator
        status: Current status (green/amber/red)
        height: Chart height in pixels
        show_status_badge: Whether to show status badge below
    """
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number+delta",
            value=value,
            number={"suffix": "/100", "font": {"size": 48, "color": "#fff"}},
            delta={"reference": target, "increasing": {"color": colors.status_green}},
            domain={"x": [0, 1], "y": [0, 1]},
            gauge={
                "axis": {
                    "range": [0, 100],
                    "tickwidth": 2,
                    "tickcolor": "#374151",
                    "dtick": 10,
                    "tickfont": {"size": 12, "color": colors.text_muted},
                },
                "bar": {"color": colors.accent_purple, "thickness": 0.75},
                "bgcolor": colors.bg_card,
                "borderwidth": 0,
                "steps": [
                    {"range": [0, 50], "color": f"{colors.status_red}30"},
                    {"range": [50, 70], "color": f"{colors.status_amber}30"},
                    {"range": [70, 100], "color": f"{colors.status_green}30"},
                ],
                "threshold": {
                    "line": {"color": colors.status_green, "width": 4},
                    "thickness": 0.85,
                    "value": target,
                },
            },
        )
    )

    fig.update_layout(
        height=height,
        margin={"l": 40, "r": 40, "t": 40, "b": 40},
        paper_bgcolor="rgba(0,0,0,0)",
    )

    st.plotly_chart(fig, use_container_width=True)

    if show_status_badge:
        render_status_badge(status, target)


def render_kpi_gauge(
    value: float,
    min_val: float = 0,
    max_val: float = 100,
    target: float | None = None,
    title: str | None = None,
    unit: str = "",
    height: int = 280,
    color: str | None = None,
) -> None:
    """Render a generic KPI gauge.

    Args:
        value: Current value
        min_val: Minimum gauge value
        max_val: Maximum gauge value
        target: Optional target line
        title: Optional title above gauge
        unit: Unit suffix (e.g., '%', 'M')
        height: Chart height in pixels
        color: Custom gauge bar color
    """
    bar_color = color or colors.accent_primary

    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=value,
            number={"suffix": unit, "font": {"size": 36, "color": "#fff"}},
            domain={"x": [0, 1], "y": [0, 1]},
            gauge={
                "axis": {
                    "range": [min_val, max_val],
                    "tickwidth": 2,
                    "tickcolor": "#374151",
                    "tickfont": {"size": 11, "color": colors.text_muted},
                },
                "bar": {"color": bar_color, "thickness": 0.7},
                "bgcolor": colors.bg_card,
                "borderwidth": 0,
            },
        )
    )

    if target is not None:
        fig.add_annotation(
            x=0.5,
            y=0.25,
            text=f"Target: {target}{unit}",
            showarrow=False,
            font={"size": 12, "color": colors.text_muted},
        )

    fig.update_layout(
        height=height,
        margin={"l": 30, "r": 30, "t": 30, "b": 20},
        paper_bgcolor="rgba(0,0,0,0)",
    )

    if title:
        st.caption(title)

    st.plotly_chart(fig, use_container_width=True)


def render_status_badge(
    status: Literal["green", "amber", "red"] | str,
    target: float = 70,
) -> None:
    """Render a centered status badge.

    Args:
        status: Status level (green/amber/red)
        target: Target value to display
    """
    status = str(status).lower()

    status_config = {
        "green": {
            "color": colors.status_green,
            "text": "On Track",
        },
        "amber": {
            "color": colors.status_amber,
            "text": "At Risk",
        },
        "red": {
            "color": colors.status_red,
            "text": "Critical",
        },
    }

    config = status_config.get(status, status_config["amber"])
    status_color = config["color"]
    status_text = config["text"]

    render_html(f"""
        <div style="text-align: center; margin-top: {spacing.md};">
            <span style="
                background: {status_color}30;
                color: {status_color};
                padding: {spacing.sm} {spacing.lg};
                border-radius: {radius.md};
                font-size: {typography.body};
                font-weight: {typography.weight_semibold};
            ">
                {status_text} • Target: {target}/100
            </span>
        </div>
    """)


__all__ = [
    "render_sustainability_gauge",
    "render_kpi_gauge",
    "render_status_badge",
]
