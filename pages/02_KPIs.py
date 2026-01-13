"""
KPIs Page
Detailed Key Performance Indicators with comprehensive breakdown

Displays:
- Large Sustainability Gauge
- Economic Performance Metrics
- Labor & Skills Metrics
- Social & Digital Metrics
- Environmental & Sustainability Metrics
"""

from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from analytics_hub_platform.ui.html import render_html
import yaml

# Page configuration
st.set_page_config(
    page_title="Key Performance Indicators",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Import application modules
from analytics_hub_platform.domain.indicators import calculate_change
from analytics_hub_platform.domain.models import FilterParams
from analytics_hub_platform.domain.services import (
    get_executive_snapshot,
    get_sustainability_summary,
)
from analytics_hub_platform.infrastructure.db_init import initialize_database
from analytics_hub_platform.infrastructure.repository import get_repository
from analytics_hub_platform.infrastructure.settings import get_settings
from analytics_hub_platform.ui.dark_components import render_sidebar
from analytics_hub_platform.ui.theme import get_dark_css, get_dark_theme
from analytics_hub_platform.ui.html import render_html
from analytics_hub_platform.ui.ui_components import (
    initialize_page_session_state,
    metric_card,
    render_page_header,
    section_header,
    spacer,
)
from analytics_hub_platform.ui.theme import colors, get_chart_layout_config
from analytics_hub_platform.utils.dataframe_adapter import add_period_column


def get_catalog() -> dict:
    """Load KPI catalog from YAML"""
    if "_kpi_catalog_cache" not in st.session_state:
        catalog_path = (
            Path(__file__).parent.parent / "analytics_hub_platform" / "config" / "kpi_catalog.yaml"
        )
        if catalog_path.exists():
            with open(catalog_path, encoding="utf-8") as f:
                st.session_state["_kpi_catalog_cache"] = yaml.safe_load(f)
        else:
            st.session_state["_kpi_catalog_cache"] = {"kpis": [], "categories": []}
    return st.session_state.get("_kpi_catalog_cache", {"kpis": [], "categories": []})


def enrich_metrics(
    df: pd.DataFrame, base_metrics: dict, filters: FilterParams, catalog: dict
) -> dict:
    """Enrich metrics with catalog data and compute missing values"""
    metrics = {**base_metrics}

    name_map = {}
    for kpi in catalog.get("kpis", []):
        kpi_id = kpi.get("id")
        if kpi_id:
            name_map[kpi_id] = kpi.get("display_name_en", kpi_id)

    # Ensure all catalog KPIs exist in metrics
    for kpi in catalog.get("kpis", []):
        kpi_id = kpi.get("id")
        if not kpi_id or kpi_id in metrics:
            continue

        # Compute metric from dataframe
        current = df[(df["year"] == filters.year) & (df["quarter"] == filters.quarter)]
        if filters.region and filters.region != "all":
            current = current[current["region"] == filters.region]

        if filters.year is None or filters.quarter is None:
            continue

        prev_year: int = int(filters.year)
        prev_quarter: int = filters.quarter - 1
        if prev_quarter == 0:
            prev_quarter = 4
            prev_year -= 1

        previous = df[(df["year"] == prev_year) & (df["quarter"] == prev_quarter)]
        if filters.region and filters.region != "all":
            previous = previous[previous["region"] == filters.region]

        current_val = (
            float(current[kpi_id].mean())
            if kpi_id in current and len(current) > 0 and not current[kpi_id].isna().all()
            else None
        )
        previous_val = (
            float(previous[kpi_id].mean())
            if kpi_id in previous and len(previous) > 0 and not previous[kpi_id].isna().all()
            else None
        )

        abs_change, pct_change = calculate_change(current_val, previous_val)

        metrics[kpi_id] = {
            "value": current_val if current_val is not None else 0,
            "previous_value": previous_val,
            "change": abs_change,
            "change_percent": pct_change,
            "status": "neutral",
            "display_name": name_map.get(kpi_id, kpi_id.replace("_", " ").title()),
            "higher_is_better": True,
        }

    return metrics


def format_kpi_value(kpi_id: str, val: float) -> str:
    """Format KPI value with appropriate unit and scale."""
    if val is None:
        return "N/A"

    # Percentage KPIs
    percentage_kpis = [
        "gdp_growth", "unemployment_rate", "renewable_share",
        "waste_recycling_rate", "water_efficiency", "forest_coverage",
    ]
    if kpi_id in percentage_kpis or "rate" in kpi_id or "share" in kpi_id:
        return f"{val:.1f}%"

    # Monetary KPIs
    monetary_kpis = ["gdp_total", "foreign_investment", "fdi"]
    if kpi_id in monetary_kpis:
        if abs(val) >= 1_000_000:
            return f"{val / 1_000_000:.1f}T SAR"
        elif abs(val) >= 1_000:
            return f"{val / 1_000:.1f}B SAR"
        else:
            return f"{val:.1f}M SAR"

    # Population
    if kpi_id == "population":
        if abs(val) >= 1:
            return f"{val:.1f}M"
        else:
            return f"{val * 1000:.0f}K"

    # Jobs count
    if kpi_id == "green_jobs":
        if abs(val) >= 1000:
            return f"{val / 1000:.1f}M"
        else:
            return f"{val:.1f}K"

    # CO2 emissions
    if kpi_id == "co2_total":
        return f"{val:.1f} Mt"

    # Energy intensity
    if kpi_id == "energy_intensity":
        return f"{val:.1f} MJ/$"

    # Index values
    index_kpis = [
        "sustainability_index", "economic_complexity", "export_diversity_index",
        "skills_gap_index", "social_progress_score", "digital_readiness",
        "innovation_index", "co2_index", "air_quality_index",
    ]
    if kpi_id in index_kpis or "index" in kpi_id or "score" in kpi_id:
        return f"{val:.1f}"

    # Default formatting
    if abs(val) >= 1_000_000_000:
        return f"{val / 1_000_000_000:.1f}B"
    elif abs(val) >= 1_000_000:
        return f"{val / 1_000_000:.1f}M"
    elif abs(val) >= 1_000:
        return f"{val / 1_000:.1f}K"
    else:
        return f"{val:.1f}"


# Initialize
initialize_page_session_state()
if not st.session_state.get("initialized"):
    initialize_database()
    st.session_state["initialized"] = True

# Apply dark theme using safe renderer
render_html(get_dark_css())
dark_theme = get_dark_theme()

# Layout
side_col, main_col = st.columns([0.2, 0.8], gap="large")

with side_col:
    render_sidebar(active="KPIs")

with main_col:
    # Header
    render_page_header(
        "Key Performance Indicators",
        "Comprehensive breakdown of all tracked metrics",
        "📈"
    )

    # Filters
    col_f1, col_f2, col_f3, col_f4 = st.columns([1, 1, 1.5, 1])
    with col_f1:
        year = st.selectbox(
            "Year",
            [2026, 2025, 2024, 2023, 2022, 2021, 2020],
            index=[2026, 2025, 2024, 2023, 2022, 2021, 2020].index(st.session_state.year),
            key="kpi_filter_year",
        )
    with col_f2:
        quarter = st.selectbox(
            "Quarter", [1, 2, 3, 4], index=st.session_state.quarter - 1, key="kpi_filter_quarter"
        )
    with col_f3:
        regions = [
            "all", "Riyadh", "Makkah", "Eastern Province", "Madinah", "Qassim",
            "Asir", "Tabuk", "Hail", "Northern Borders", "Jazan", "Najran",
            "Al Bahah", "Al Jawf",
        ]
        region = st.selectbox(
            "Region", regions, index=regions.index(st.session_state.region), key="kpi_filter_region"
        )
    with col_f4:
        language = st.selectbox(
            "Language",
            ["en", "ar"],
            index=["en", "ar"].index(st.session_state.language),
            key="kpi_filter_language",
        )

    # Update session state
    if (
        year != st.session_state.year
        or quarter != st.session_state.quarter
        or region != st.session_state.region
        or language != st.session_state.language
    ):
        st.session_state.year = year
        st.session_state.quarter = quarter
        st.session_state.region = region
        st.session_state.language = language
        st.rerun()

    spacer("md")

    # Load data
    try:
        settings = get_settings()
        repo = get_repository()
        df = repo.get_all_indicators(settings.default_tenant_id)

        region_param = region if region != "all" else None
        filter_params = FilterParams(
            tenant_id=settings.default_tenant_id,
            year=year,
            quarter=quarter,
            region=region_param,
        )

        snapshot = get_executive_snapshot(df, filter_params, language)
        sustainability = get_sustainability_summary(df, filter_params, language)

        catalog = get_catalog()
        metrics = enrich_metrics(df, snapshot.get("metrics", {}), filter_params, catalog)

        # Large Sustainability Gauge
        section_header(
            "Sustainability Index", "Overall composite score for sustainable development", "🌱"
        )

        index_value = sustainability.get("index", 0) or 0
        status = sustainability.get("status", "unknown")

        fig = go.Figure(
            go.Indicator(
                mode="gauge+number+delta",
                value=index_value,
                number={"suffix": "/100", "font": {"size": 48, "color": "#fff"}},
                delta={"reference": 70, "increasing": {"color": colors.green}},
                domain={"x": [0, 1], "y": [0, 1]},
                gauge={
                    "axis": {
                        "range": [0, 100],
                        "tickwidth": 2,
                        "tickcolor": "#374151",
                        "dtick": 10,
                        "tickfont": {"size": 12, "color": colors.text_muted},
                    },
                    "bar": {"color": colors.purple, "thickness": 0.75},
                    "bgcolor": colors.bg_card,
                    "borderwidth": 0,
                    "steps": [
                        {"range": [0, 50], "color": "rgba(239, 68, 68, 0.3)"},
                        {"range": [50, 70], "color": "rgba(245, 158, 11, 0.3)"},
                        {"range": [70, 100], "color": "rgba(34, 197, 94, 0.3)"},
                    ],
                    "threshold": {
                        "line": {"color": colors.green, "width": 4},
                        "thickness": 0.85,
                        "value": 70,
                    },
                },
            )
        )

        fig.update_layout(
            height=350,
            margin={"l": 40, "r": 40, "t": 40, "b": 40},
            paper_bgcolor="rgba(0,0,0,0)",
        )

        with st.container():
            st.plotly_chart(fig, use_container_width=True)

            status_color = (
                colors.green if status == "green"
                else colors.amber if status == "amber"
                else colors.red
            )
            status_text = (
                "On Track" if status == "green"
                else "At Risk" if status == "amber"
                else "Critical"
            )
            render_html(
                f"""
                <div style="text-align: center; margin-top: 16px;">
                    <span style="background: {status_color}30; color: {status_color}; padding: 8px 20px;
                                border-radius: 8px; font-size: 15px; font-weight: 600;">
                        {status_text} • Target: 70/100
                    </span>
                </div>
                """
            )

        spacer("lg")

        # Economic KPIs
        section_header(
            "Economic Performance", "GDP, investment, and economic diversification metrics", "💼"
        )

        economic_kpis = [
            "gdp_growth", "gdp_total", "foreign_investment",
            "export_diversity_index", "economic_complexity",
        ]
        cols = st.columns(5)
        for i, kpi_id in enumerate(economic_kpis):
            if kpi_id not in metrics:
                continue
            kpi = metrics[kpi_id]
            with cols[i % 5]:
                val = kpi.get("value", 0) or 0
                change = kpi.get("change_percent", 0) or 0
                status = kpi.get("status", "neutral")
                label = kpi.get("display_name", kpi_id.replace("_", " ").title())
                display_val = format_kpi_value(kpi_id, val)
                metric_card(label, display_val, delta=change, status=status)

        spacer("lg")

        # Labor KPIs
        section_header("Labor & Skills", "Employment, workforce, and skills development", "👥")

        labor_kpis = ["unemployment_rate", "green_jobs", "skills_gap_index", "population"]
        cols = st.columns(4)
        for i, kpi_id in enumerate(labor_kpis):
            if kpi_id not in metrics:
                continue
            kpi = metrics[kpi_id]
            with cols[i % 4]:
                val = kpi.get("value", 0) or 0
                change = kpi.get("change_percent", 0) or 0
                status = kpi.get("status", "neutral")
                label = kpi.get("display_name", kpi_id.replace("_", " ").title())
                display_val = format_kpi_value(kpi_id, val)
                metric_card(label, display_val, delta=change, status=status)

        spacer("lg")

        # Social & Digital KPIs
        section_header(
            "Social & Digital", "Social progress, digital readiness, and innovation", "🌐"
        )

        digital_kpis = ["social_progress_score", "digital_readiness", "innovation_index"]
        cols = st.columns(3)
        for i, kpi_id in enumerate(digital_kpis):
            if kpi_id not in metrics:
                continue
            kpi = metrics[kpi_id]
            with cols[i % 3]:
                val = kpi.get("value", 0) or 0
                change = kpi.get("change_percent", 0) or 0
                status = kpi.get("status", "neutral")
                label = kpi.get("display_name", kpi_id.replace("_", " ").title())
                display_val = format_kpi_value(kpi_id, val)
                metric_card(label, display_val, delta=change, status=status)

        spacer("lg")

        # Environmental KPIs
        section_header(
            "Environmental & Sustainability", "Climate, energy, and environmental metrics", "🌿"
        )

        env_kpis = [
            "co2_index", "co2_total", "renewable_share", "energy_intensity",
            "water_efficiency", "waste_recycling_rate", "forest_coverage", "air_quality_index",
        ]
        cols = st.columns(4)
        for i, kpi_id in enumerate(env_kpis):
            if kpi_id not in metrics:
                continue
            kpi = metrics[kpi_id]
            with cols[i % 4]:
                val = kpi.get("value", 0) or 0
                change = kpi.get("change_percent", 0) or 0
                status = kpi.get("status", "neutral")
                label = kpi.get("display_name", kpi_id.replace("_", " ").title())
                display_val = format_kpi_value(kpi_id, val)
                metric_card(label, display_val, delta=change, status=status)

        spacer("lg")

        # KPI Forecasting Section
        section_header("KPI Forecasting", "ML-powered predictions for key indicators", "🔮")

        try:
            from analytics_hub_platform.domain.ml_services import KPIForecaster

            forecast_kpis = [
                "sustainability_index", "gdp_growth",
                "non_oil_gdp_share", "unemployment_rate",
                "co2_index", "renewable_share"
            ]
            available_forecast_kpis = [k for k in forecast_kpis if k in df.columns]

            if available_forecast_kpis:
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    selected_forecast_kpi = st.selectbox(
                        "Select KPI to Forecast",
                        available_forecast_kpis,
                        format_func=lambda x: metrics.get(x, {}).get("display_name", x.replace("_", " ").title()),
                        key="forecast_kpi",
                    )
                with col2:
                    periods = st.slider("Quarters Ahead", 2, 12, 8, key="periods")
                with col3:
                    model_type = st.selectbox(
                        "Model",
                        ["gradient_boosting", "random_forest"],
                        format_func=lambda x: x.replace("_", " ").title(),
                        key="model",
                    )

                hist_df = (
                    df.groupby(["year", "quarter"])
                    .agg({selected_forecast_kpi: "mean"})
                    .reset_index()
                )
                hist_df = hist_df.rename(columns={selected_forecast_kpi: "value"}).dropna()
                hist_df = hist_df.sort_values(["year", "quarter"])

                if len(hist_df) >= 8:
                    with st.spinner("Generating forecast..."):
                        forecaster = KPIForecaster(model_type=model_type)
                        forecaster.fit(hist_df)
                        predictions = forecaster.predict(quarters_ahead=periods)

                    # Visualization
                    fig = go.Figure()

                    hist_df = add_period_column(hist_df)
                    fig.add_trace(
                        go.Scatter(
                            x=hist_df["period"],
                            y=hist_df["value"],
                            mode="lines+markers",
                            name="Historical",
                            line={"color": colors.purple, "width": 2},
                            marker={"size": 6},
                        )
                    )

                    forecast_periods = [f"Q{p['quarter']} {p['year']}" for p in predictions]
                    forecast_values = [p["predicted_value"] for p in predictions]
                    forecast_lower = [p["confidence_lower"] for p in predictions]
                    forecast_upper = [p["confidence_upper"] for p in predictions]

                    fig.add_trace(
                        go.Scatter(
                            x=forecast_periods,
                            y=forecast_values,
                            mode="lines+markers",
                            name="Forecast",
                            line={"color": colors.cyan, "width": 2, "dash": "dash"},
                            marker={"size": 6, "symbol": "diamond"},
                        )
                    )

                    fig.add_trace(
                        go.Scatter(
                            x=forecast_periods + forecast_periods[::-1],
                            y=forecast_upper + forecast_lower[::-1],
                            fill="toself",
                            fillcolor="rgba(16, 185, 129, 0.1)",
                            line={"color": "rgba(0,0,0,0)"},
                            name="95% Confidence",
                        )
                    )

                    config = get_chart_layout_config()
                    config["height"] = 400
                    fig.update_layout(**config)
                    st.plotly_chart(fig, use_container_width=True)

                    with st.expander("📋 View Forecast Details"):
                        forecast_df = pd.DataFrame(predictions)
                        forecast_df = add_period_column(forecast_df)
                        st.dataframe(
                            forecast_df[["period", "predicted_value", "confidence_lower", "confidence_upper"]].round(2),
                            use_container_width=True,
                            hide_index=True,
                        )
                else:
                    st.warning("⚠️ Not enough historical data (need at least 8 quarters)")
            else:
                st.info("No KPI data available for forecasting")

        except ImportError:
             st.warning("⚠️ Forecasting module not available")
        except Exception as e:
            st.warning(f"⚠️ Forecasting unavailable: {str(e)}")

    except Exception as e:
        st.error(f"Error loading KPI data: {str(e)}")
        import traceback
        st.code(traceback.format_exc())
