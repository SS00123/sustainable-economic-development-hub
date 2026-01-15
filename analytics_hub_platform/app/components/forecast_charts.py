"""Forecast visualization components.

Provides reusable forecast charts:
- Historical + forecast line charts
- Confidence interval bands
- Forecast detail tables

Usage:
    from analytics_hub_platform.app.components.forecast_charts import (
        render_forecast_chart,
        render_forecast_details,
    )
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import plotly.graph_objects as go
import streamlit as st

from analytics_hub_platform.app.styles.tokens import colors
from analytics_hub_platform.ui.theme import get_chart_layout_config

if TYPE_CHECKING:
    import pandas as pd


def render_forecast_chart(
    historical_df: "pd.DataFrame",
    predictions: list[dict],
    x_column: str = "period",
    y_column: str = "value",
    title: str | None = None,
    height: int = 400,
    historical_color: str | None = None,
    forecast_color: str | None = None,
    confidence_color: str = "rgba(16, 185, 129, 0.1)",
) -> None:
    """Render a forecast chart with historical data and predictions.

    Args:
        historical_df: DataFrame with historical data (must have x_column and y_column)
        predictions: List of prediction dicts with year, quarter, predicted_value,
                     confidence_lower, confidence_upper
        x_column: Column name for x-axis in historical data
        y_column: Column name for y-axis in historical data
        title: Optional chart title
        height: Chart height in pixels
        historical_color: Color for historical line
        forecast_color: Color for forecast line
        confidence_color: Fill color for confidence band
    """
    historical_color = historical_color or colors.accent_purple
    forecast_color = forecast_color or colors.accent_primary

    fig = go.Figure()

    # Historical data
    fig.add_trace(
        go.Scatter(
            x=historical_df[x_column],
            y=historical_df[y_column],
            mode="lines+markers",
            name="Historical",
            line={"color": historical_color, "width": 2},
            marker={"size": 6},
        )
    )

    # Forecast data
    if predictions:
        forecast_periods = [f"Q{p['quarter']} {p['year']}" for p in predictions]
        forecast_values = [p["predicted_value"] for p in predictions]
        forecast_lower = [p.get("confidence_lower", p["predicted_value"] * 0.9) for p in predictions]
        forecast_upper = [p.get("confidence_upper", p["predicted_value"] * 1.1) for p in predictions]

        # Forecast line
        fig.add_trace(
            go.Scatter(
                x=forecast_periods,
                y=forecast_values,
                mode="lines+markers",
                name="Forecast",
                line={"color": forecast_color, "width": 2, "dash": "dash"},
                marker={"size": 6, "symbol": "diamond"},
            )
        )

        # Confidence band
        fig.add_trace(
            go.Scatter(
                x=forecast_periods + forecast_periods[::-1],
                y=forecast_upper + forecast_lower[::-1],
                fill="toself",
                fillcolor=confidence_color,
                line={"color": "rgba(0,0,0,0)"},
                name="95% Confidence",
            )
        )

    # Apply theme
    config = get_chart_layout_config()
    config["height"] = height
    if title:
        config["title"] = {"text": title, "font": {"color": colors.text_primary}}
    fig.update_layout(**config)

    st.plotly_chart(fig, use_container_width=True)


def render_forecast_details(
    predictions: list[dict],
    title: str = "📋 View Forecast Details",
    expanded: bool = False,
) -> None:
    """Render forecast details in an expandable table.

    Args:
        predictions: List of prediction dicts
        title: Expander title
        expanded: Whether to expand by default
    """
    import pandas as pd
    from analytics_hub_platform.utils.dataframe_adapter import add_period_column

    with st.expander(title, expanded=expanded):
        if not predictions:
            st.info("No forecast data available")
            return

        forecast_df = pd.DataFrame(predictions)
        forecast_df = add_period_column(forecast_df)

        display_columns = ["period", "predicted_value"]
        if "confidence_lower" in forecast_df.columns:
            display_columns.append("confidence_lower")
        if "confidence_upper" in forecast_df.columns:
            display_columns.append("confidence_upper")

        st.dataframe(
            forecast_df[display_columns].round(2),
            use_container_width=True,
            hide_index=True,
        )


def render_forecast_section(
    historical_df: "pd.DataFrame",
    predictions: list[dict],
    kpi_name: str = "KPI",
    x_column: str = "period",
    y_column: str = "value",
) -> None:
    """Render a complete forecast section with chart and details.

    Args:
        historical_df: DataFrame with historical data
        predictions: List of prediction dicts
        kpi_name: Name of the KPI being forecast
        x_column: Column name for x-axis
        y_column: Column name for y-axis
    """
    render_forecast_chart(
        historical_df=historical_df,
        predictions=predictions,
        x_column=x_column,
        y_column=y_column,
        title=f"{kpi_name} Forecast",
    )

    render_forecast_details(predictions)


__all__ = [
    "render_forecast_chart",
    "render_forecast_details",
    "render_forecast_section",
]
