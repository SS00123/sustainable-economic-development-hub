"""Chart helper components: target lines and YoY comparisons.

Canonical implementations migrated from ui.dark_components.
"""

from __future__ import annotations

import plotly.graph_objects as go

from analytics_hub_platform.ui.html import render_html


def add_target_line_to_chart(
    fig: go.Figure,
    target_value: float,
    target_label: str = "Target",
    line_color: str = "#10b981",
) -> go.Figure:
    """
    Add a horizontal target line to a Plotly figure.

    Args:
        fig: Plotly figure to modify
        target_value: Y-axis value for target line
        target_label: Label for the target line
        line_color: Color of the target line

    Returns:
        Modified Plotly figure
    """
    fig.add_hline(
        y=target_value,
        line_dash="dash",
        line_color=line_color,
        line_width=2,
        annotation_text=f"🎯 {target_label}: {target_value:.1f}",
        annotation_position="top right",
        annotation_font_size=11,
        annotation_font_color=line_color,
    )
    return fig


def render_yoy_comparison(
    kpi_name: str,
    current_year: int,
    current_value: float,
    previous_year: int,
    previous_value: float,
    unit: str = "",
    icon: str = "📈",
) -> None:
    """
    Render a Year-over-Year comparison card.

    Args:
        kpi_name: Name of the KPI
        current_year: Current year
        current_value: Value for current year
        previous_year: Previous year
        previous_value: Value for previous year
        unit: Unit suffix (e.g., '%', ' SAR')
        icon: Icon emoji
    """
    change = current_value - previous_value
    pct_change = ((current_value - previous_value) / previous_value * 100) if previous_value != 0 else 0
    change_class = "positive" if change >= 0 else "negative"
    arrow = "→"

    html = f"""
    <div class="yoy-comparison">
        <div class="yoy-year">
            <div class="year-label">{previous_year}</div>
            <div class="year-value">{previous_value:.1f}{unit}</div>
        </div>
        <div class="yoy-divider">
            <span class="yoy-arrow">{arrow}</span>
            <span class="yoy-change {change_class}">
                {"+" if change >= 0 else ""}{pct_change:.1f}%
            </span>
        </div>
        <div class="yoy-year">
            <div class="year-label">{current_year}</div>
            <div class="year-value">{current_value:.1f}{unit}</div>
        </div>
    </div>
    """

    render_html(f'<div style="margin-bottom:8px; color:rgba(255,255,255,0.7); font-size:13px">{icon} {kpi_name}</div>')
    render_html(html)
