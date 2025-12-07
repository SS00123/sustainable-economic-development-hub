"""
Sustainability Trends Page
Sustainable Economic Development Analytics Hub
Ministry of Economy and Planning

Dedicated page for sustainability trends and environmental indicators.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from analytics_hub_platform.ui.layout import (
    render_header,
    render_footer,
    render_section_header,
    inject_custom_css,
)
from analytics_hub_platform.ui.filters import get_filter_state
from analytics_hub_platform.config.theme import get_theme
from analytics_hub_platform.infrastructure.repository import get_repository
from analytics_hub_platform.infrastructure.settings import get_settings
from analytics_hub_platform.domain.models import FilterParams
from analytics_hub_platform.domain.services import get_sustainability_summary
from analytics_hub_platform.locale import get_strings


def render_sustainability_trends() -> None:
    """Render the sustainability trends page."""
    inject_custom_css()
    theme = get_theme()
    
    filters = get_filter_state()
    strings = get_strings(filters.language)
    
    render_header(
        title=strings.get("sustainability_title", "Sustainability Trends"),
        subtitle=strings.get("sustainability_subtitle", "Environmental and Green Economy Indicators"),
        language=filters.language,
    )
    
    try:
        repo = get_repository()
        settings = get_settings()
        df = repo.get_all_indicators(settings.default_tenant_id)
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return
    
    # Environmental KPIs
    env_kpis = [
        "co2_index", "renewable_share", "energy_intensity",
        "water_efficiency", "waste_recycling_rate", "air_quality_index",
        "forest_coverage", "green_jobs"
    ]
    
    render_section_header(title="Environmental Performance Over Time", icon="🌿")
    
    # Aggregate data by period
    trend_df = df.groupby(["year", "quarter"]).agg({
        kpi: "mean" for kpi in env_kpis
    }).reset_index()
    trend_df["period"] = trend_df.apply(lambda r: f"Q{int(r['quarter'])} {int(r['year'])}", axis=1)
    trend_df = trend_df.sort_values(["year", "quarter"])
    
    # Multi-line chart
    fig = go.Figure()
    
    colors = [
        theme.colors.primary, theme.colors.secondary, theme.colors.success,
        "#0891B2", "#7C3AED", "#D97706", "#059669", "#EC4899"
    ]
    
    kpi_labels = {
        "co2_index": "CO2 Intensity",
        "renewable_share": "Renewable Share (%)",
        "energy_intensity": "Energy Intensity",
        "water_efficiency": "Water Efficiency",
        "waste_recycling_rate": "Recycling Rate (%)",
        "air_quality_index": "Air Quality Index",
        "forest_coverage": "Forest Coverage (%)",
        "green_jobs": "Green Jobs (K)",
    }
    
    for i, kpi in enumerate(env_kpis):
        fig.add_trace(go.Scatter(
            x=trend_df["period"],
            y=trend_df[kpi],
            mode="lines+markers",
            name=kpi_labels.get(kpi, kpi),
            line=dict(color=colors[i % len(colors)], width=2),
        ))
    
    fig.update_layout(
        height=500,
        margin=dict(l=20, r=20, t=40, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
        xaxis_title="Period",
        font=dict(family=theme.typography.font_family),
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Sustainability Index Trend
    render_section_header(title="Sustainability Index Evolution", icon="📈")
    
    sus_trend = df.groupby(["year", "quarter"]).agg({
        "sustainability_index": "mean"
    }).reset_index()
    sus_trend["period"] = sus_trend.apply(lambda r: f"Q{int(r['quarter'])} {int(r['year'])}", axis=1)
    sus_trend = sus_trend.sort_values(["year", "quarter"])
    
    fig2 = go.Figure()
    
    fig2.add_trace(go.Scatter(
        x=sus_trend["period"],
        y=sus_trend["sustainability_index"],
        mode="lines+markers+text",
        text=[f"{v:.1f}" for v in sus_trend["sustainability_index"]],
        textposition="top center",
        line=dict(color=theme.colors.success, width=3),
        marker=dict(size=10),
        fill="tozeroy",
        fillcolor=f"rgba({int(theme.colors.success[1:3], 16)}, {int(theme.colors.success[3:5], 16)}, {int(theme.colors.success[5:7], 16)}, 0.2)",
    ))
    
    fig2.add_hline(y=70, line_dash="dash", line_color=theme.colors.status_amber,
                   annotation_text="Target: 70", annotation_position="right")
    
    fig2.update_layout(
        height=350,
        margin=dict(l=20, r=20, t=40, b=20),
        yaxis_range=[0, 100],
        xaxis_title="Period",
        yaxis_title="Sustainability Index",
        font=dict(family=theme.typography.font_family),
    )
    
    st.plotly_chart(fig2, use_container_width=True)
    
    # Footer
    render_footer(filters.language)
