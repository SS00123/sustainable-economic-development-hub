"""Plotly chart styling helpers."""

from __future__ import annotations

import plotly.graph_objects as go

from analytics_hub_platform.app.styles.compat import COLORS


def apply_chart_theme(fig: go.Figure, height: int = 400) -> go.Figure:
    """Apply consistent dark theme styling to Plotly charts."""
    fig.update_layout(
        height=height,
        margin={"l": 18, "r": 16, "t": 22, "b": 18},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": COLORS.text_muted, "size": 12},
        legend={
            "orientation": "h",
            "yanchor": "top",
            "y": 1.12,
            "xanchor": "center",
            "x": 0.5,
            "bgcolor": COLORS.bg_card,
            "bordercolor": COLORS.border_light,
            "borderwidth": 1,
            "font": {"color": COLORS.text_muted, "size": 11},
        },
        xaxis={
            "showgrid": True,
            "gridcolor": "rgba(255,255,255,0.05)",
            "zeroline": False,
            "tickfont": {"color": COLORS.text_muted, "size": 11},
            "title": {"font": {"color": COLORS.text_muted, "size": 12}},
            "linecolor": "rgba(255,255,255,0.10)",
            "mirror": False,
        },
        yaxis={
            "showgrid": True,
            "gridcolor": "rgba(255,255,255,0.07)",
            "zeroline": False,
            "tickfont": {"color": COLORS.text_muted, "size": 11},
            "title": {"font": {"color": COLORS.text_muted, "size": 12}},
            "linecolor": "rgba(255,255,255,0.10)",
            "mirror": False,
        },
    )
    return fig


def apply_dark_chart_layout(fig: go.Figure, height: int = 300, show_grid: bool = True) -> go.Figure:
    """Apply premium dark theme styling to a Plotly figure.

    This is the canonical implementation for the legacy API.
    """

    grid_color = "rgba(255,255,255,0.06)" if show_grid else "rgba(0,0,0,0)"

    fig.update_layout(
        height=height,
        margin={"l": 20, "r": 20, "t": 30, "b": 24},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={
            "color": COLORS.text_secondary,
            "size": 12,
            "family": "'Inter', -apple-system, BlinkMacSystemFont, sans-serif",
        },
        legend={
            "orientation": "h",
            "yanchor": "top",
            "y": 1.14,
            "xanchor": "center",
            "x": 0.5,
            "bgcolor": "rgba(15, 23, 42, 0.9)",
            "bordercolor": "rgba(168, 85, 247, 0.2)",
            "borderwidth": 1,
            "font": {"color": COLORS.text_secondary, "size": 11},
            "itemsizing": "constant",
        },
        xaxis={
            "showgrid": show_grid,
            "gridcolor": grid_color,
            "gridwidth": 1,
            "zeroline": False,
            "tickfont": {"color": COLORS.text_muted, "size": 11},
            "title": {"font": {"color": COLORS.text_secondary, "size": 12}},
            "linecolor": "rgba(255,255,255,0.1)",
            "linewidth": 1,
            "mirror": False,
            "tickcolor": "rgba(255,255,255,0.1)",
        },
        yaxis={
            "showgrid": show_grid,
            "gridcolor": grid_color,
            "gridwidth": 1,
            "zeroline": False,
            "tickfont": {"color": COLORS.text_muted, "size": 11},
            "title": {"font": {"color": COLORS.text_secondary, "size": 12}},
            "linecolor": "rgba(255,255,255,0.1)",
            "linewidth": 1,
            "mirror": False,
            "tickcolor": "rgba(255,255,255,0.1)",
        },
        hoverlabel={
            "bgcolor": "rgba(15, 23, 42, 0.95)",
            "bordercolor": "rgba(168, 85, 247, 0.4)",
            "font": {"color": "white", "size": 12},
        },
    )
    return fig
