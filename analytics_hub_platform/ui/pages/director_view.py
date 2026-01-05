"""
Director View Page
Sustainable Economic Development Analytics Hub
Ministry of Economy and Planning

This page provides a detailed analytics view for directors and
heads of analytics. It features:
- Same KPIs as executive view with additional controls
- Regional comparisons
- Multiple charts and visualizations
- Trend analysis
- Rule-based explanations
"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components

from analytics_hub_platform.config.theme import get_theme
from analytics_hub_platform.domain.models import FilterParams
from analytics_hub_platform.domain.services import (
    get_executive_snapshot,
    get_sustainability_summary,
)
from analytics_hub_platform.ui.html import render_html
from analytics_hub_platform.infrastructure.repository import get_repository
from analytics_hub_platform.infrastructure.settings import get_settings
from analytics_hub_platform.locales import get_strings
from analytics_hub_platform.ui.filters import get_filter_state
from analytics_hub_platform.ui.layout import (
    inject_custom_css,
    render_footer,
    render_header,
    render_kpi_card,
    render_section_header,
)
from analytics_hub_platform.utils.kpi_utils import get_kpi_unit
from analytics_hub_platform.utils.narratives import generate_director_narrative


def render_director_view() -> None:
    """Render the director/analytics dashboard view."""
    inject_custom_css()
    theme = get_theme()

    # Get filter state
    filters = get_filter_state()
    strings = get_strings(filters.language)

    # Header
    render_header(
        title=strings.get("director_title", "Analytics Dashboard"),
        subtitle=strings.get("director_subtitle", "Detailed Analysis and Regional Comparisons"),
        language=filters.language,
    )

    # Load data
    try:
        repo = get_repository()
        settings = get_settings()

        filter_params = FilterParams(
            tenant_id=settings.default_tenant_id,
            year=filters.year,
            quarter=filters.quarter,
            region=filters.region if filters.region != "all" else None,
        )

        df = repo.get_all_indicators(settings.default_tenant_id)
        snapshot = get_executive_snapshot(df, filter_params, filters.language) or {}
        sustainability = get_sustainability_summary(df, filter_params, filters.language) or {}

    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return

    # Check for no data
    if snapshot.get("status") == "no_data" or sustainability.get("status") == "no_data":
        st.warning(
            f"⚠️ No data available for the selected period (Q{filters.quarter} {filters.year}) and region. Please select a different time period or region."
        )
        render_footer(filters.language)
        return

    # Tabs for different analysis views
    tab1, tab2, tab3, tab4 = st.tabs(
        ["📊 Overview", "📈 Trends", "🗺️ Regional Analysis", "🌱 Sustainability Deep Dive"]
    )

    with tab1:
        render_overview_tab(snapshot, sustainability, theme, filters)

    with tab2:
        render_trends_tab(df, theme, filters)

    with tab3:
        render_regional_tab(df, theme, filters)

    with tab4:
        render_sustainability_tab(sustainability, df, theme, filters)

    # Footer
    render_footer(filters.language)


def render_overview_tab(snapshot: dict, sustainability: dict, theme, filters) -> None:
    """Render the overview tab with KPIs and summary."""

    # Key Metrics Row
    render_section_header(title="Key Metrics", icon="📊")

    metrics = snapshot.get("metrics", {})

    # Primary KPIs
    col1, col2, col3, col4, col5 = st.columns(5)

    primary_kpis = [
        ("sustainability_index", col1),
        ("gdp_growth", col2),
        ("renewable_share", col3),
        ("unemployment_rate", col4),
        ("green_jobs", col5),
    ]

    for kpi_id, col in primary_kpis:
        with col:
            kpi = metrics.get(kpi_id, {})
            render_kpi_card(
                label=kpi.get("display_name", kpi_id),
                value=kpi.get("value", 0) or 0,
                delta=kpi.get("change_percent"),
                status=kpi.get("status", "neutral"),
                unit=get_kpi_unit(kpi_id),
                higher_is_better=kpi.get("higher_is_better", True),
            )

    render_html("<br>")

    # Secondary KPIs
    col1, col2, col3, col4, col5 = st.columns(5)

    secondary_kpis = [
        ("co2_index", col1),
        ("export_diversity_index", col2),
        ("water_efficiency", col3),
        ("air_quality_index", col4),
        ("data_quality_score", col5),
    ]

    for kpi_id, col in secondary_kpis:
        with col:
            kpi = metrics.get(kpi_id, {})
            render_kpi_card(
                label=kpi.get("display_name", kpi_id),
                value=kpi.get("value", 0) or 0,
                delta=kpi.get("change_percent"),
                status=kpi.get("status", "neutral"),
                unit=get_kpi_unit(kpi_id),
                higher_is_better=kpi.get("higher_is_better", True),
            )

    st.markdown("---")

    # Analysis and Insights
    render_section_header(title="Analysis & Insights", icon="💡")

    col_left, col_right = st.columns([2, 1])

    with col_left:
        narrative = generate_director_narrative(snapshot, filters.language)
        narrative_html = f"""
        <div style="
            background: {theme.colors.surface};
            border: 1px solid {theme.colors.border};
            border-radius: 12px;
            padding: 24px;
            line-height: 1.8;
        ">
            {narrative}
        </div>
        """
        components.html(narrative_html, height=300, scrolling=True)

    with col_right:
        # Quick stats
        st.markdown("**📈 Period Summary**")
        st.markdown(f"**Period:** Q{filters.quarter} {filters.year}")
        st.markdown(
            f"**Region:** {filters.region.title() if filters.region != 'all' else 'All Regions'}"
        )

        improvements = snapshot.get("top_improvements", [])
        deteriorations = snapshot.get("top_deteriorations", [])

        st.markdown(f"**Improvements:** {len(improvements)}")
        st.markdown(f"**Deteriorations:** {len(deteriorations)}")

        sus_index = sustainability.get("index")
        if sus_index is not None:
            st.metric(
                "Sustainability Index",
                f"{sus_index:.1f}",
                delta=None,
            )


def render_trends_tab(df: pd.DataFrame, theme, filters) -> None:
    """Render the trends analysis tab."""

    render_section_header(title="Time Series Analysis", icon="📈")

    # KPI selector
    col1, col2 = st.columns([1, 3])

    with col1:
        kpi_options = {
            "sustainability_index": "Sustainability Index",
            "gdp_growth": "GDP Growth",
            "renewable_share": "Renewable Energy Share",
            "co2_index": "CO2 Intensity Index",
            "unemployment_rate": "Unemployment Rate",
            "green_jobs": "Green Jobs",
            "water_efficiency": "Water Efficiency",
            "air_quality_index": "Air Quality Index",
        }

        selected_kpi = st.selectbox(
            "Select Indicator",
            options=list(kpi_options.keys()),
            format_func=lambda x: kpi_options[x],
        )

        show_trend = st.checkbox("Show Trend Line", value=True)

    with col2:
        # Filter data for trend
        trend_df = df.copy()
        if filters.region != "all":
            trend_df = trend_df[trend_df["region"] == filters.region]

        # Aggregate by year/quarter
        trend_agg = trend_df.groupby(["year", "quarter"]).agg({selected_kpi: "mean"}).reset_index()

        trend_agg["period"] = trend_agg.apply(
            lambda r: f"Q{int(r['quarter'])} {int(r['year'])}", axis=1
        )
        trend_agg = trend_agg.sort_values(["year", "quarter"])

        # Create chart
        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=trend_agg["period"],
                y=trend_agg[selected_kpi],
                mode="lines+markers",
                name=kpi_options[selected_kpi],
                line={"color": theme.colors.primary, "width": 3},
                marker={"size": 8},
            )
        )

        if show_trend and len(trend_agg) > 2:
            # Add simple linear trend
            import numpy as np

            x_numeric = np.arange(len(trend_agg))
            z = np.polyfit(x_numeric, trend_agg[selected_kpi].values, 1)
            p = np.poly1d(z)

            fig.add_trace(
                go.Scatter(
                    x=trend_agg["period"],
                    y=p(x_numeric),
                    mode="lines",
                    name="Trend",
                    line={"color": theme.colors.secondary, "width": 2, "dash": "dash"},
                )
            )

        fig.update_layout(
            height=400,
            margin={"l": 20, "r": 20, "t": 40, "b": 20},
            xaxis_title="Period",
            yaxis_title=kpi_options[selected_kpi],
            legend={"orientation": "h", "yanchor": "bottom", "y": 1.02},
            font={"family": theme.typography.font_family},
        )

        st.plotly_chart(fig, width="stretch")

    st.markdown("---")

    # Multi-KPI comparison
    render_section_header(title="Multi-Indicator Comparison", icon="📊")

    compare_kpis = st.multiselect(
        "Select indicators to compare",
        options=list(kpi_options.keys()),
        default=["sustainability_index", "renewable_share"],
        format_func=lambda x: kpi_options[x],
        max_selections=4,
    )

    if compare_kpis:
        compare_df = (
            trend_df.groupby(["year", "quarter"])
            .agg(dict.fromkeys(compare_kpis, "mean"))
            .reset_index()
        )
        compare_df["period"] = compare_df.apply(
            lambda r: f"Q{int(r['quarter'])} {int(r['year'])}", axis=1
        )
        compare_df = compare_df.sort_values(["year", "quarter"])

        fig = go.Figure()
        colors = [
            theme.colors.primary,
            theme.colors.secondary,
            theme.colors.success,
            theme.colors.warning,
        ]

        for i, kpi in enumerate(compare_kpis):
            fig.add_trace(
                go.Scatter(
                    x=compare_df["period"],
                    y=compare_df[kpi],
                    mode="lines+markers",
                    name=kpi_options[kpi],
                    line={"color": colors[i % len(colors)], "width": 2},
                )
            )

        fig.update_layout(
            height=350,
            margin={"l": 20, "r": 20, "t": 40, "b": 20},
            legend={"orientation": "h", "yanchor": "bottom", "y": 1.02},
            font={"family": theme.typography.font_family},
        )

        st.plotly_chart(fig, width="stretch")


def render_regional_tab(df: pd.DataFrame, theme, filters) -> None:
    """Render the regional comparison tab."""

    render_section_header(title="Regional Comparison", icon="🗺️")

    # Filter to current period
    regional_df = df[(df["year"] == filters.year) & (df["quarter"] == filters.quarter)].copy()

    if len(regional_df) == 0:
        st.warning("No data available for the selected period.")
        return

    # KPI selector
    kpi_options = {
        "sustainability_index": "Sustainability Index",
        "gdp_growth": "GDP Growth",
        "renewable_share": "Renewable Energy Share",
        "unemployment_rate": "Unemployment Rate",
        "green_jobs": "Green Jobs",
        "co2_index": "CO2 Intensity",
    }

    selected_kpi = st.selectbox(
        "Select Indicator for Regional Comparison",
        options=list(kpi_options.keys()),
        format_func=lambda x: kpi_options[x],
        key="regional_kpi_selector",
    )

    # Aggregate by region
    regional_agg = regional_df.groupby("region").agg({selected_kpi: "mean"}).reset_index()
    regional_agg = regional_agg.sort_values(selected_kpi, ascending=False)

    # Calculate national average
    national_avg = regional_agg[selected_kpi].mean()

    col1, col2 = st.columns([2, 1])

    with col1:
        # Bar chart
        fig = go.Figure()

        # Color bars based on comparison to average
        colors = [
            theme.colors.status_green if v >= national_avg else theme.colors.status_amber
            for v in regional_agg[selected_kpi]
        ]

        fig.add_trace(
            go.Bar(
                x=regional_agg["region"],
                y=regional_agg[selected_kpi],
                marker_color=colors,
            )
        )

        # Add average line
        fig.add_hline(
            y=national_avg,
            line_dash="dash",
            line_color=theme.colors.primary,
            annotation_text=f"National Avg: {national_avg:.1f}",
            annotation_position="top right",
        )

        fig.update_layout(
            height=400,
            margin={"l": 20, "r": 20, "t": 40, "b": 100},
            xaxis_title="Region",
            yaxis_title=kpi_options[selected_kpi],
            xaxis_tickangle=-45,
            font={"family": theme.typography.font_family},
        )

        st.plotly_chart(fig, width="stretch")

    with col2:
        st.markdown("**📊 Statistics**")
        st.metric("National Average", f"{national_avg:.2f}")
        st.metric("Highest", f"{regional_agg[selected_kpi].max():.2f}")
        st.metric("Lowest", f"{regional_agg[selected_kpi].min():.2f}")
        st.metric("Std Dev", f"{regional_agg[selected_kpi].std():.2f}")

        # Top and bottom regions
        st.markdown("---")
        st.markdown("**🏆 Top Regions**")
        for _, row in regional_agg.head(3).iterrows():
            st.markdown(f"• {row['region']}: **{row[selected_kpi]:.1f}**")

        st.markdown("**⚠️ Needs Attention**")
        for _, row in regional_agg.tail(3).iterrows():
            st.markdown(f"• {row['region']}: **{row[selected_kpi]:.1f}**")


def render_sustainability_tab(sustainability: dict, df: pd.DataFrame, theme, filters) -> None:
    """Render the sustainability deep dive tab."""

    render_section_header(title="Sustainability Index Breakdown", icon="🌱")

    breakdown = sustainability.get("breakdown", [])

    if not breakdown:
        st.warning("No sustainability breakdown available.")
        return

    # Create breakdown chart
    breakdown_df = pd.DataFrame(breakdown)
    breakdown_df = breakdown_df[breakdown_df["contribution"].notna()]

    if len(breakdown_df) == 0:
        st.warning("Insufficient data for sustainability breakdown.")
        return

    col1, col2 = st.columns([2, 1])

    with col1:
        fig = go.Figure()

        # Sort by contribution
        breakdown_df = breakdown_df.sort_values("contribution", ascending=True)

        colors = [
            theme.colors.status_green
            if s == "green"
            else theme.colors.status_amber
            if s == "amber"
            else theme.colors.status_red
            if s == "red"
            else theme.colors.text_muted
            for s in breakdown_df["status"]
        ]

        fig.add_trace(
            go.Bar(
                x=breakdown_df["contribution"],
                y=breakdown_df["name"],
                orientation="h",
                marker_color=colors,
                text=[f"{v:.1f}" for v in breakdown_df["contribution"]],
                textposition="outside",
            )
        )

        fig.update_layout(
            height=400,
            margin={"l": 20, "r": 80, "t": 40, "b": 20},
            xaxis_title="Contribution to Index",
            font={"family": theme.typography.font_family},
        )

        st.plotly_chart(fig, width="stretch")

    with col2:
        st.markdown("**📋 Component Details**")

        for item in breakdown:
            name = item.get("name", "")
            raw_value = item.get("raw_value")
            weight = item.get("weight", 0)
            status = item.get("status", "unknown")
            unit = item.get("unit", "")

            status_emoji = (
                "🟢"
                if status == "green"
                else "🟡"
                if status == "amber"
                else "🔴"
                if status == "red"
                else "⚪"
            )

            if raw_value is not None:
                st.markdown(f"{status_emoji} **{name}**")
                st.markdown(f"   Value: {raw_value:.1f} {unit} (Weight: {weight:.0%})")

