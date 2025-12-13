"""
Executive View Page
Sustainable Economic Development Analytics Hub
Ministry of Economy and Planning

This page provides a high-level executive dashboard designed for
ministers and top leadership. It features:
- Key KPIs with status indicators
- Sustainability index prominently displayed
- Simple, clean design with minimal interaction
- Rule-based narrative summaries
"""

import streamlit as st
import streamlit.components.v1 as components
import plotly.express as px
import plotly.graph_objects as go

from analytics_hub_platform.ui.layout import (
    render_header,
    render_footer,
    render_kpi_card,
    render_section_header,
    render_status_badge,
    inject_custom_css,
    render_alert_box,
)
from analytics_hub_platform.ui.filters import get_filter_state
from analytics_hub_platform.config.theme import get_theme
from analytics_hub_platform.infrastructure.repository import get_repository
from analytics_hub_platform.infrastructure.settings import get_settings
from analytics_hub_platform.domain.models import FilterParams
from analytics_hub_platform.domain.services import get_executive_snapshot, get_sustainability_summary
from analytics_hub_platform.utils.narratives import generate_executive_narrative
from analytics_hub_platform.utils.kpi_utils import get_kpi_unit, get_delta_suffix
from analytics_hub_platform.locale import get_strings


def render_executive_view() -> None:
    """Render the executive dashboard view."""
    inject_custom_css()
    theme = get_theme()
    
    # Get filter state
    filters = get_filter_state()
    strings = get_strings(filters.language)
    
    # Header
    render_header(
        title=strings.get("executive_title", "Executive Dashboard"),
        subtitle=strings.get("executive_subtitle", "Key Performance Indicators at a Glance"),
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
        snapshot = get_executive_snapshot(df, filter_params, filters.language)
        sustainability = get_sustainability_summary(df, filter_params, filters.language)
        
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return
    
    # Check for no data
    if snapshot.get("status") == "no_data" or sustainability.get("status") == "no_data":
        st.warning(f"⚠️ No data available for the selected period (Q{filters.quarter} {filters.year}) and region. Please select a different time period or region.")
        render_footer(filters.language)
        return
    
    # Sustainability Index - Prominent Display
    render_section_header(
        title=strings.get("sustainability_index", "Sustainability Index"),
        description=strings.get("sustainability_desc", "Composite sustainability and development score"),
        icon="🌱"
    )
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        index_value = sustainability.get("index", 0) or 0
        
        # Gauge chart for sustainability index
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=index_value,
            domain={'x': [0, 1], 'y': [0, 1]},
            gauge={
                'axis': {'range': [0, 100], 'tickwidth': 1},
                'bar': {'color': theme.colors.primary},
                'steps': [
                    {'range': [0, 50], 'color': theme.colors.status_red_bg},
                    {'range': [50, 70], 'color': theme.colors.status_amber_bg},
                    {'range': [70, 100], 'color': theme.colors.status_green_bg},
                ],
                'threshold': {
                    'line': {'color': theme.colors.primary, 'width': 4},
                    'thickness': 0.75,
                    'value': index_value
                }
            },
            title={'text': "Overall Score", 'font': {'size': 16}},
        ))
        
        fig.update_layout(
            height=300,
            margin=dict(l=20, r=20, t=40, b=20),
            font=dict(family=theme.typography.font_family),
        )
        
        st.plotly_chart(fig, width="stretch")
    
    with col2:
        status = sustainability.get("status", "unknown") if sustainability else "unknown"
        status_labels = {"green": "On Track", "amber": "At Risk", "red": "Critical"}
        
        status_html = f"""
        <div style="text-align: center; padding: 20px;">
            <h3 style="color: {theme.colors.text_muted}; margin-bottom: 16px;">Status</h3>
            {render_status_badge(status, status_labels.get(status, "Unknown"))}
        </div>
        """
        components.html(status_html, height=100)
        
        period_html = f"""
        <div style="text-align: center; padding: 20px;">
            <p style="color: {theme.colors.text_muted}; font-size: 12px;">Period</p>
            <p style="color: {theme.colors.text_primary}; font-size: 18px; font-weight: 600;">
                Q{filters.quarter} {filters.year}
            </p>
        </div>
        """
        components.html(period_html, height=80)
    
    with col3:
        # Top contributors to index
        breakdown = sustainability.get("breakdown", [])[:3]
        
        contributors_header = f"""
        <div style="padding: 10px;">
            <h4 style="color: {theme.colors.text_muted}; margin-bottom: 12px;">Top Contributors</h4>
        </div>
        """
        components.html(contributors_header, height=50)
        
        for item in breakdown:
            name = item.get("name", item.get("name_en", ""))
            contribution = item.get("contribution", 0) or 0
            st.markdown(f"• {name}: **{contribution:.1f}** pts")
    
    st.markdown("---")
    
    # Key KPIs Grid
    render_section_header(
        title=strings.get("key_kpis", "Key Performance Indicators"),
        icon="📊"
    )
    
    metrics = snapshot.get("metrics", {})
    
    # First row - Economic
    row1_kpis = ["gdp_growth", "renewable_share", "co2_index", "green_jobs"]
    cols1 = st.columns(4)
    
    for col, kpi_id in zip(cols1, row1_kpis):
        with col:
            kpi = metrics.get(kpi_id, {})
            kpi_value = kpi.get("value")
            if kpi_value is None:
                kpi_value = 0
            render_kpi_card(
                label=kpi.get("display_name", kpi_id),
                value=float(kpi_value) if kpi_value is not None else 0.0,
                delta=kpi.get("change_percent"),
                delta_suffix=get_delta_suffix(kpi_id),
                status=kpi.get("status", "neutral"),
                unit=get_kpi_unit(kpi_id),
                higher_is_better=kpi.get("higher_is_better", True),
            )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Second row
    row2_kpis = ["unemployment_rate", "export_diversity_index", "water_efficiency", "air_quality_index"]
    cols2 = st.columns(4)
    
    for col, kpi_id in zip(cols2, row2_kpis):
        with col:
            kpi = metrics.get(kpi_id, {})
            kpi_value = kpi.get("value")
            if kpi_value is None:
                kpi_value = 0
            render_kpi_card(
                label=kpi.get("display_name", kpi_id),
                value=float(kpi_value) if kpi_value is not None else 0.0,
                delta=kpi.get("change_percent"),
                delta_suffix=get_delta_suffix(kpi_id),
                status=kpi.get("status", "neutral"),
                unit=get_kpi_unit(kpi_id),
                higher_is_better=kpi.get("higher_is_better", True),
            )
    
    st.markdown("---")
    
    # Narrative Summary
    render_section_header(
        title=strings.get("summary", "Summary"),
        description=strings.get("summary_desc", "Key insights from current period"),
        icon="📝"
    )
    
    narrative = generate_executive_narrative(snapshot, filters.language)
    
    # Render narrative with components.html for proper HTML rendering
    narrative_html = f"""
    <div style="
        color: #4B5563;
        font-size: 14px;
        margin: 8px 0 8px 0;
        font-family: 'Segoe UI', 'Roboto', 'Source Sans 3', system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
    ">{narrative}</div>
    """
    components.html(narrative_html, height=400, scrolling=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Improvements and Deteriorations
    col_imp, col_det = st.columns(2)
    
    with col_imp:
        improvements_header = f"""
        <h4 style="color: {theme.colors.status_green};">📈 Top Improvements</h4>
        """
        components.html(improvements_header, height=40)
        
        improvements = snapshot.get("top_improvements", [])
        if improvements:
            for item in improvements:
                st.markdown(f"• **{item['display_name']}**: +{abs(item['change_percent']):.1f}%")
        else:
            st.markdown("*No significant improvements*")
    
    with col_det:
        attention_header = f"""
        <h4 style="color: {theme.colors.status_red};">📉 Areas Needing Attention</h4>
        """
        components.html(attention_header, height=40)
        
        deteriorations = snapshot.get("top_deteriorations", [])
        if deteriorations:
            for item in deteriorations:
                st.markdown(f"• **{item['display_name']}**: {item['change_percent']:.1f}%")
        else:
            st.markdown("*No significant deteriorations*")
    
    # Footer
    render_footer(filters.language)
