"""Legacy chart-card helpers.

These functions preserve the legacy public API that used to live in
`analytics_hub_platform.ui.dark_components`, while implementing the behavior
using the canonical `app.components` + `app.styles` building blocks.

They are intentionally simple and stable: the goal is to avoid callers needing
`ui.dark_components` for common chart card patterns.
"""

from __future__ import annotations

from typing import Any

import pandas as pd
import plotly.graph_objects as go

from analytics_hub_platform.app.components.cards import card_container
from analytics_hub_platform.app.styles.charts import apply_dark_chart_layout


def render_line_chart_card(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    title: str,
    subtitle: str = "",
    show_glow: bool = True,
    color: str = "#a855f7",
    fill_gradient: bool = True,
) -> None:
    """Render a line chart inside a styled card.

    Signature kept for backward compatibility.
    """

    with card_container(title=title, subtitle=subtitle):
        fig = go.Figure()

        if len(df) == 0 or x_col not in df.columns or y_col not in df.columns:
            apply_dark_chart_layout(fig, height=240)
            return

        if fill_gradient:
            # rgba conversion from #RRGGBB
            r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
            fig.add_trace(
                go.Scatter(
                    x=df[x_col],
                    y=df[y_col],
                    mode="lines",
                    fill="tozeroy",
                    fillcolor=f"rgba({r}, {g}, {b}, 0.12)",
                    line={"color": "rgba(0,0,0,0)", "width": 0},
                    hoverinfo="skip",
                    showlegend=False,
                )
            )

        if show_glow:
            r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
            fig.add_trace(
                go.Scatter(
                    x=df[x_col],
                    y=df[y_col],
                    mode="lines",
                    line={
                        "color": f"rgba({r}, {g}, {b}, 0.25)",
                        "width": 12,
                        "shape": "spline",
                    },
                    hoverinfo="skip",
                    showlegend=False,
                )
            )

        fig.add_trace(
            go.Scatter(
                x=df[x_col],
                y=df[y_col],
                mode="lines+markers",
                line={"color": color, "width": 2, "shape": "spline"},
                marker={"size": 5, "color": color},
                hovertemplate="%{x}<br>Value: %{y:.2f}<extra></extra>",
                showlegend=False,
            )
        )

        apply_dark_chart_layout(fig, height=240)

        # Using render_html-free rendering keeps this compatible with existing pages.
        import streamlit as st

        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def _bar_card(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    title: str,
    subtitle: str,
    orientation: str,
    color: str,
    height: int,
    extra_bar_kwargs: dict[str, Any] | None = None,
) -> None:
    with card_container(title=title, subtitle=subtitle):
        fig = go.Figure()
        extra_bar_kwargs = extra_bar_kwargs or {}

        if len(df) and x_col in df.columns and y_col in df.columns:
            fig.add_trace(
                go.Bar(
                    x=df[x_col] if orientation == "v" else df[y_col],
                    y=df[y_col] if orientation == "v" else df[x_col],
                    marker_color=color,
                    orientation=orientation,
                    **extra_bar_kwargs,
                )
            )

        apply_dark_chart_layout(fig, height=height)

        import streamlit as st

        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def render_horizontal_bar_card(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    title: str,
    subtitle: str = "",
    color: str = "#22d3ee",
    height: int = 320,
) -> None:
    """Render a horizontal bar chart inside a card."""

    _bar_card(
        df=df,
        x_col=x_col,
        y_col=y_col,
        title=title,
        subtitle=subtitle,
        orientation="h",
        color=color,
        height=height,
    )


def render_grouped_bar_card(
    df: pd.DataFrame,
    x_col: str,
    y_cols: list[str],
    title: str,
    subtitle: str = "",
    colors: list[str] | None = None,
    height: int = 360,
) -> None:
    """Render a grouped bar chart inside a card."""

    colors = colors or ["#a855f7", "#22d3ee", "#ec4899", "#10b981"]

    with card_container(title=title, subtitle=subtitle):
        fig = go.Figure()

        if len(df) and x_col in df.columns:
            for idx, y_col in enumerate(y_cols):
                if y_col not in df.columns:
                    continue
                fig.add_trace(
                    go.Bar(
                        x=df[x_col],
                        y=df[y_col],
                        name=y_col.replace("_", " ").title(),
                        marker_color=colors[idx % len(colors)],
                    )
                )

        fig.update_layout(barmode="group")
        apply_dark_chart_layout(fig, height=height)

        import streamlit as st

        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def render_donut_chart_card(
    labels: list[str],
    values: list[float],
    title: str,
    subtitle: str = "",
    colors: list[str] | None = None,
    height: int = 320,
) -> None:
    """Render a donut/pie chart inside a card."""

    colors = colors or ["#a855f7", "#22d3ee", "#ec4899", "#10b981", "#f59e0b"]

    with card_container(title=title, subtitle=subtitle):
        fig = go.Figure(
            data=[
                go.Pie(
                    labels=labels,
                    values=values,
                    hole=0.58,
                    marker={"colors": colors},
                    textinfo="percent",
                )
            ]
        )

        apply_dark_chart_layout(fig, height=height, show_grid=False)

        import streamlit as st

        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


__all__ = [
    "render_line_chart_card",
    "render_horizontal_bar_card",
    "render_grouped_bar_card",
    "render_donut_chart_card",
]
