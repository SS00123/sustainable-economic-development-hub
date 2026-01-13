"""Chart card component for consistent Plotly chart containers."""

from __future__ import annotations

from typing import TYPE_CHECKING

import streamlit as st

from analytics_hub_platform.app.styles.compat import (
    COLORS,
    RADIUS,
    SHADOWS,
    SPACING,
    TYPOGRAPHY,
)
from analytics_hub_platform.app.styles.charts import apply_chart_theme
from analytics_hub_platform.ui.html import render_html

if TYPE_CHECKING:
    import plotly.graph_objects as go


def chart_card_open(
    title: str = "",
    subtitle: str = "",
    help_text: str = "",
) -> None:
    """Open a chart card container.

    Use with chart_card_close() to wrap a Plotly chart.

    Args:
        title: Card title
        subtitle: Optional subtitle
        help_text: Optional help tooltip text
    """
    title_html = (
        f'<div style="font-size: {TYPOGRAPHY.heading4}; font-weight: 600; '
        f'color: {COLORS.text_primary}; margin-bottom: {SPACING.xs};">{title}</div>'
        if title
        else ""
    )
    subtitle_html = (
        f'<div style="font-size: {TYPOGRAPHY.caption}; color: {COLORS.text_muted}; '
        f'margin-bottom: {SPACING.md};">{subtitle}</div>'
        if subtitle
        else ""
    )
    help_html = (
        f'<span title="{help_text}" style="cursor: help; opacity: 0.6;">ⓘ</span>'
        if help_text
        else ""
    )

    render_html(
        f"""
        <div style="
            background: {COLORS.bg_card};
            border: 1px solid {COLORS.border};
            border-radius: {RADIUS.lg};
            padding: 20px 22px;
            box-shadow: {SHADOWS.md};
            margin-bottom: {SPACING.md};
            backdrop-filter: blur(10px);
        ">
        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
            <div>
                {title_html}
                {subtitle_html}
            </div>
            {help_html}
        </div>
    """
    )


def chart_card_close() -> None:
    """Close a chart card container."""
    render_html("</div>")


def render_chart_card(
    fig: "go.Figure",
    title: str = "",
    subtitle: str = "",
    help_text: str = "",
    use_container_width: bool = True,
    height: int | None = None,
) -> None:
    """Render a Plotly chart inside a styled card.

    Args:
        fig: Plotly figure to render
        title: Card title
        subtitle: Optional subtitle
        help_text: Optional help tooltip
        use_container_width: Whether to expand to container width
        height: Optional explicit height in pixels
    """
    # Apply theme
    apply_chart_theme(fig)

    if height:
        fig.update_layout(height=height)

    chart_card_open(title=title, subtitle=subtitle, help_text=help_text)
    st.plotly_chart(fig, use_container_width=use_container_width, key=None)
    chart_card_close()


__all__ = [
    "chart_card_open",
    "chart_card_close",
    "render_chart_card",
]
