"""Trend chart components for time-series visualization.

Provides reusable trend line charts with:
- Primary series with fill
- Optional trend line overlay
- Configurable styling via tokens

Usage:
    from analytics_hub_platform.app.components.trend_charts import (
        render_trend_line_chart,
        render_multi_series_chart,
    )
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
import plotly.graph_objects as go
import streamlit as st

from analytics_hub_platform.app.styles.tokens import colors
from analytics_hub_platform.app.styles.charts import apply_chart_theme

if TYPE_CHECKING:
    import pandas as pd


def render_trend_line_chart(
    df: "pd.DataFrame",
    x_column: str,
    y_column: str,
    title: str | None = None,
    show_trend_line: bool = True,
    primary_color: str | None = None,
    trend_color: str | None = None,
    fill_opacity: float = 0.15,
    height: int = 350,
    show_markers: bool = True,
    hover_template: str = "<b>%{x}</b><br>Value: %{y:.1f}<extra></extra>",
) -> None:
    """Render a trend line chart with optional regression trend overlay.

    Args:
        df: DataFrame with x and y data
        x_column: Column name for x-axis (typically 'period')
        y_column: Column name for y-axis values
        title: Optional chart title (shown in legend)
        show_trend_line: Whether to show linear regression trend line
        primary_color: Color for main series (default: purple)
        trend_color: Color for trend line (default: cyan)
        fill_opacity: Opacity for area fill (0-1)
        height: Chart height in pixels
        show_markers: Whether to show point markers
        hover_template: Plotly hover template
    """
    primary_color = primary_color or colors.accent_purple
    trend_color = trend_color or colors.accent_primary

    fig = go.Figure()

    # Primary series
    fill_rgba = f"rgba({_hex_to_rgb(primary_color)}, {fill_opacity})"
    fig.add_trace(
        go.Scatter(
            x=df[x_column],
            y=df[y_column],
            mode="lines+markers" if show_markers else "lines",
            name=title or y_column.replace("_", " ").title(),
            line={"color": primary_color, "width": 3},
            marker={"size": 10, "color": primary_color} if show_markers else None,
            fill="tozeroy",
            fillcolor=fill_rgba,
            hovertemplate=hover_template,
        )
    )

    # Trend line (linear regression)
    if show_trend_line and len(df) > 2:
        x_numeric = np.arange(len(df))
        y_values = df[y_column].to_numpy(dtype=float)

        # Handle NaN values
        mask = ~np.isnan(y_values)
        if mask.sum() > 2:
            z = np.polyfit(x_numeric[mask], y_values[mask], 1)
            p = np.poly1d(z)

            fig.add_trace(
                go.Scatter(
                    x=df[x_column],
                    y=p(x_numeric),
                    mode="lines",
                    name="Trend",
                    line={"color": trend_color, "width": 2, "dash": "dash"},
                )
            )

    apply_chart_theme(fig, height=height)
    st.plotly_chart(fig, use_container_width=True)


def render_multi_series_chart(
    df: "pd.DataFrame",
    x_column: str,
    y_columns: list[str],
    labels: dict[str, str] | None = None,
    height: int = 420,
    line_width: int = 2,
) -> None:
    """Render a multi-series line chart for comparing multiple indicators.

    Args:
        df: DataFrame with x and y data
        x_column: Column name for x-axis
        y_columns: List of column names for y-axis series
        labels: Optional mapping of column names to display labels
        height: Chart height in pixels
        line_width: Width of lines
    """
    labels = labels or {}
    chart_colors = list(colors.chart_palette)

    fig = go.Figure()

    for i, col in enumerate(y_columns):
        if col not in df.columns:
            continue

        display_name = labels.get(col, col.replace("_", " ").title())
        color = chart_colors[i % len(chart_colors)]

        fig.add_trace(
            go.Scatter(
                x=df[x_column],
                y=df[col],
                mode="lines+markers",
                name=display_name,
                line={"color": color, "width": line_width},
                hovertemplate=f"<b>{display_name}</b><br>%{{x}}<br>Value: %{{y:.1f}}<extra></extra>",
            )
        )

    apply_chart_theme(fig, height=height)
    st.plotly_chart(fig, use_container_width=True)


def _hex_to_rgb(hex_color: str) -> str:
    """Convert hex color to RGB string for rgba()."""
    hex_color = hex_color.lstrip("#")
    if len(hex_color) == 3:
        hex_color = "".join([c * 2 for c in hex_color])
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    return f"{r}, {g}, {b}"


__all__ = [
    "render_trend_line_chart",
    "render_multi_series_chart",
]
