"""Regional comparison chart components.

Provides reusable regional visualization:
- Horizontal bar charts with benchmark lines
- Regional statistics panels
- Comparison layouts

Usage:
    from analytics_hub_platform.app.components.regional_charts import (
        render_regional_bar_chart,
        render_regional_stats_panel,
    )
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import plotly.graph_objects as go
import streamlit as st

from analytics_hub_platform.app.styles.tokens import (
    colors,
    spacing,
    radius,
    typography,
)
from analytics_hub_platform.app.styles.charts import apply_chart_theme
from analytics_hub_platform.ui.html import render_html

if TYPE_CHECKING:
    import pandas as pd


def render_regional_bar_chart(
    df: "pd.DataFrame",
    region_column: str = "region",
    value_column: str = "sustainability_index",
    title: str | None = None,
    height: int = 450,
    show_benchmark: bool = True,
    benchmark_value: float | None = None,
    above_color: str | None = None,
    below_color: str | None = None,
) -> float:
    """Render a horizontal bar chart comparing regions.

    Args:
        df: DataFrame with region and value columns
        region_column: Column name for regions
        value_column: Column name for values
        title: Optional x-axis title
        height: Chart height in pixels
        show_benchmark: Whether to show benchmark line
        benchmark_value: Custom benchmark (default: mean)
        above_color: Color for bars above benchmark
        below_color: Color for bars below benchmark

    Returns:
        The benchmark value used (for stats panel)
    """
    above_color = above_color or colors.accent_purple
    below_color = below_color or colors.accent_pink

    # Sort by value
    sorted_df = df.sort_values(value_column, ascending=True)

    # Calculate benchmark
    avg_value = benchmark_value if benchmark_value is not None else sorted_df[value_column].mean()

    # Assign colors based on benchmark
    bar_colors = [
        above_color if v >= avg_value else below_color
        for v in sorted_df[value_column]
    ]

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            y=sorted_df[region_column],
            x=sorted_df[value_column],
            orientation="h",
            marker_color=bar_colors,
            text=[f"{v:.1f}" for v in sorted_df[value_column]],
            textposition="outside",
            textfont={"color": colors.text_muted},
        )
    )

    if show_benchmark:
        fig.add_vline(
            x=avg_value,
            line_dash="dash",
            line_color=colors.accent_primary,
            annotation_text=f"Avg: {avg_value:.1f}",
            annotation_font={"color": colors.text_muted},
        )

    apply_chart_theme(fig, height=height)
    fig.update_layout(
        xaxis={"showgrid": True, "title": title or value_column.replace("_", " ").title()},
        yaxis={"showgrid": False},
    )
    st.plotly_chart(fig, use_container_width=True)

    return avg_value


def render_regional_stats_panel(
    df: "pd.DataFrame",
    value_column: str = "sustainability_index",
    national_avg: float | None = None,
) -> None:
    """Render a statistics summary panel for regional data.

    Args:
        df: DataFrame with regional data
        value_column: Column name for values
        national_avg: Pre-calculated national average (optional)
    """
    if value_column not in df.columns:
        return

    values = df[value_column]
    avg = national_avg if national_avg is not None else values.mean()

    stats = [
        ("National Average", f"{avg:.1f}"),
        ("Highest", f"{values.max():.1f}"),
        ("Lowest", f"{values.min():.1f}"),
        ("Std Dev", f"{values.std():.1f}"),
    ]

    render_html(f"""
        <div style="color: {colors.text_secondary}; font-size: {typography.body}; font-weight: {typography.weight_semibold}; margin-bottom: {spacing.md};">
            📊 Regional Statistics
        </div>
    """)

    for label, value in stats:
        render_html(f"""
            <div style="background: {colors.bg_card}; padding: {spacing.md}; border-radius: {radius.md}; margin-bottom: {spacing.sm};">
                <div style="font-size: {typography.small}; color: {colors.text_muted};">{label}</div>
                <div style="font-size: {typography.h4}; font-weight: {typography.weight_bold}; color: {colors.text_primary};">{value}</div>
            </div>
        """)


def render_regional_comparison(
    df: "pd.DataFrame",
    region_column: str = "region",
    value_column: str = "sustainability_index",
    title: str | None = None,
    chart_height: int = 450,
) -> None:
    """Render a complete regional comparison with chart and stats.

    Args:
        df: DataFrame with regional data
        region_column: Column name for regions
        value_column: Column name for values
        title: Optional x-axis title for chart
        chart_height: Chart height in pixels
    """
    if len(df) == 0:
        st.info("No regional data available")
        return

    col1, col2 = st.columns([2, 1])

    with col1:
        # Aggregate if needed
        if region_column in df.columns and value_column in df.columns:
            regional_agg = (
                df.groupby(region_column)
                .agg({value_column: "mean"})
                .reset_index()
            )
            avg_value = render_regional_bar_chart(
                regional_agg,
                region_column=region_column,
                value_column=value_column,
                title=title,
                height=chart_height,
            )
        else:
            avg_value = 0
            st.warning(f"Missing columns: {region_column} or {value_column}")

    with col2:
        if region_column in df.columns and value_column in df.columns:
            render_regional_stats_panel(
                df.groupby(region_column).agg({value_column: "mean"}).reset_index(),
                value_column=value_column,
                national_avg=avg_value,
            )


__all__ = [
    "render_regional_bar_chart",
    "render_regional_stats_panel",
    "render_regional_comparison",
]
