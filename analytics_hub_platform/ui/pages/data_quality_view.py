"""
Data Quality View Page
Sustainable Economic Development Analytics Hub
Ministry of Economy and Planning

Dedicated page for data quality monitoring and governance.
"""

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from analytics_hub_platform.ui.layout import (
    render_header,
    render_footer,
    render_section_header,
    inject_custom_css,
    render_kpi_card,
)
from analytics_hub_platform.ui.filters import get_filter_state
from analytics_hub_platform.config.theme import get_theme
from analytics_hub_platform.infrastructure.repository import get_repository
from analytics_hub_platform.infrastructure.settings import get_settings
from analytics_hub_platform.domain.models import FilterParams
from analytics_hub_platform.domain.services import get_data_quality_metrics
from analytics_hub_platform.locale import get_strings


def render_data_quality_view() -> None:
    """Render the data quality monitoring page."""
    inject_custom_css()
    theme = get_theme()
    
    filters = get_filter_state()
    strings = get_strings(filters.language)
    
    render_header(
        title=strings.get("data_quality_title", "Data Quality Dashboard"),
        subtitle=strings.get("data_quality_subtitle", "Monitoring Data Completeness and Accuracy"),
        language=filters.language,
    )
    
    try:
        repo = get_repository()
        settings = get_settings()
        df = repo.get_all_indicators(settings.default_tenant_id)
        
        filter_params = FilterParams(
            tenant_id=settings.default_tenant_id,
            year=filters.year,
            quarter=filters.quarter,
            region=filters.region if filters.region != "all" else None,
        )
        
        quality_metrics = get_data_quality_metrics(df, filter_params)
        
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return
    
    # Quality Score Cards
    render_section_header(title="Quality Overview", icon="✅")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        completeness = quality_metrics.get("completeness", 0)
        status = "green" if completeness >= 90 else "amber" if completeness >= 70 else "red"
        render_kpi_card(
            label="Data Completeness",
            value=completeness,
            unit="%",
            status=status,
            higher_is_better=True,
        )
    
    with col2:
        avg_quality = quality_metrics.get("avg_quality_score") or 0
        status = "green" if avg_quality >= 80 else "amber" if avg_quality >= 60 else "red"
        render_kpi_card(
            label="Quality Score",
            value=avg_quality,
            unit="",
            status=status,
            higher_is_better=True,
        )
    
    with col3:
        records = quality_metrics.get("records_count", 0)
        render_kpi_card(
            label="Records Count",
            value=records,
            unit="",
            status="neutral",
        )
    
    with col4:
        last_update = quality_metrics.get("last_update")
        update_str = last_update.strftime("%Y-%m-%d") if last_update else "N/A"
        last_update_html = f"""
        <div style="
            background: {theme.colors.surface};
            border: 1px solid {theme.colors.border};
            border-radius: 12px;
            padding: 20px;
            min-height: 120px;
        ">
            <p style="color: {theme.colors.text_muted}; font-size: 12px; text-transform: uppercase;">Last Updated</p>
            <p style="color: {theme.colors.text_primary}; font-size: 24px; font-weight: 700;">{update_str}</p>
        </div>
        """
        components.html(last_update_html, height=140)
    
    st.markdown("---")
    
    # Completeness by Indicator
    render_section_header(title="Completeness by Indicator", icon="📊")
    
    missing_by_kpi = quality_metrics.get("missing_by_kpi", {})
    
    if missing_by_kpi:
        completeness_data = [
            {"Indicator": kpi, "Completeness": 100 - info["percent"]}
            for kpi, info in missing_by_kpi.items()
        ]
        comp_df = pd.DataFrame(completeness_data)
        comp_df = comp_df.sort_values("Completeness", ascending=True)
        
        fig = go.Figure()
        
        colors = [
            theme.colors.status_green if v >= 90
            else theme.colors.status_amber if v >= 70
            else theme.colors.status_red
            for v in comp_df["Completeness"]
        ]
        
        fig.add_trace(go.Bar(
            x=comp_df["Completeness"],
            y=comp_df["Indicator"],
            orientation="h",
            marker_color=colors,
            text=[f"{v:.1f}%" for v in comp_df["Completeness"]],
            textposition="outside",
        ))
        
        fig.add_vline(x=90, line_dash="dash", line_color=theme.colors.status_green,
                     annotation_text="Target: 90%")
        
        fig.update_layout(
            height=500,
            margin=dict(l=20, r=80, t=20, b=20),
            xaxis_title="Completeness (%)",
            xaxis_range=[0, 105],
            font=dict(family=theme.typography.font_family),
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Quality Trend Over Time
    render_section_header(title="Quality Score Trend", icon="📈")
    
    quality_trend = df.groupby(["year", "quarter"]).agg({
        "data_quality_score": "mean"
    }).reset_index()
    quality_trend["period"] = quality_trend.apply(lambda r: f"Q{int(r['quarter'])} {int(r['year'])}", axis=1)
    quality_trend = quality_trend.sort_values(["year", "quarter"])
    
    fig2 = go.Figure()
    
    fig2.add_trace(go.Scatter(
        x=quality_trend["period"],
        y=quality_trend["data_quality_score"],
        mode="lines+markers",
        line=dict(color=theme.colors.primary, width=3),
        marker=dict(size=8),
    ))
    
    fig2.add_hline(y=80, line_dash="dash", line_color=theme.colors.status_green,
                   annotation_text="Target: 80")
    
    fig2.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=20, b=20),
        yaxis_range=[0, 100],
        xaxis_title="Period",
        yaxis_title="Quality Score",
        font=dict(family=theme.typography.font_family),
    )
    
    st.plotly_chart(fig2, use_container_width=True)
    
    # Footer
    render_footer(filters.language)
