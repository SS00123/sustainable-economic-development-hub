"""
Dashboard (Minister View)
Executive Overview Page - Focused, high-level snapshot for ministerial briefing

Displays:
- Economic Activity Index
- Regional Performance Bars
- Energy/Sustainability Mix
- Key Metrics (Green Jobs, FDI)
- Yearly KPIs
- Compact Sustainability Gauge
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from pathlib import Path

# Page configuration
st.set_page_config(
    page_title="Dashboard – Minister View",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Import application modules
from analytics_hub_platform.infrastructure.db_init import initialize_database
from analytics_hub_platform.infrastructure.settings import get_settings
from analytics_hub_platform.infrastructure.repository import get_repository
from analytics_hub_platform.domain.models import FilterParams
from analytics_hub_platform.domain.services import get_executive_snapshot, get_sustainability_summary
from analytics_hub_platform.utils.dataframe_adapter import add_period_column
from analytics_hub_platform.ui.dark_theme import get_dark_css, get_dark_theme
from analytics_hub_platform.ui.ui_theme import COLORS, SPACING
from analytics_hub_platform.ui.ui_components import (
    section_header, metric_card, status_pills, apply_chart_theme, spacer, card_container
)
from analytics_hub_platform.ui.dark_components import (
    render_sidebar, card_open, card_close, render_mini_metric,
)


# Initialize session state
def initialize_session_state() -> None:
    """Initialize session state variables"""
    defaults = {
        "year": 2024,
        "quarter": 4,
        "region": "all",
        "language": "en",
        "initialized": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# Initialize
initialize_session_state()
if not st.session_state.get("initialized"):
    initialize_database()
    st.session_state["initialized"] = True

# Apply dark theme
st.markdown(get_dark_css(), unsafe_allow_html=True)
dark_theme = get_dark_theme()

# Layout
side_col, main_col = st.columns([0.22, 0.78], gap="large")

with side_col:
    render_sidebar(active="Dashboard")

with main_col:
    # Header
    st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, {COLORS.purple} 0%, {COLORS.cyan} 100%);
            padding: 24px 28px;
            border-radius: 12px;
            margin-bottom: 20px;
        ">
            <h1 style="color: white; margin: 0; font-size: 28px; font-weight: 700;">
                📊 Dashboard – Minister View
            </h1>
            <p style="color: rgba(255,255,255,0.9); margin: 8px 0 0 0; font-size: 14px;">
                Executive snapshot of sustainable economic development indicators
            </p>
            <p style="color: rgba(255,255,255,0.7); margin: 12px 0 0 0; font-size: 12px;">
                Developed by Eng. Sultan Albuqami · <a href="mailto:sultan_mutep@hotmail.com" style="color: rgba(255,255,255,0.9); text-decoration: none;">sultan_mutep@hotmail.com</a>
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Filters
    col_f1, col_f2, col_f3, col_f4 = st.columns([1, 1, 1.5, 1])
    with col_f1:
        year = st.selectbox("Year", [2024, 2023, 2022, 2021], 
            index=[2024, 2023, 2022, 2021].index(st.session_state.year), key="filter_year")
    with col_f2:
        quarter = st.selectbox("Quarter", [1, 2, 3, 4], 
            index=st.session_state.quarter - 1, key="filter_quarter")
    with col_f3:
        regions = ["all", "Riyadh", "Makkah", "Eastern Province", "Madinah", "Qassim", 
                  "Asir", "Tabuk", "Hail", "Northern Borders", "Jazan", "Najran", "Al Bahah", "Al Jawf"]
        region = st.selectbox("Region", regions, 
            index=regions.index(st.session_state.region), key="filter_region")
    with col_f4:
        language = st.selectbox("Language", ["en", "ar"], 
            index=["en", "ar"].index(st.session_state.language), key="filter_language")
    
    # Update session state
    if (year != st.session_state.year or quarter != st.session_state.quarter or 
        region != st.session_state.region or language != st.session_state.language):
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
        metrics = snapshot.get("metrics", {})
        
        # Status overview
        green_count = sum(1 for m in metrics.values() if m.get("status") == "green")
        amber_count = sum(1 for m in metrics.values() if m.get("status") == "amber")
        red_count = sum(1 for m in metrics.values() if m.get("status") == "red")
        
        with card_container("Performance Overview", f"Q{quarter} {year} • {len(metrics)} KPIs tracked"):
            status_pills(green_count, amber_count, red_count)
        
        spacer("md")
        
        # Row 1: Economic Activity + Regional Bars
        r1c1, r1c2 = st.columns([0.48, 0.52], gap="large")
        
        with r1c1:
            card_open("Economic Activity Index", "Quarterly trend")
            
            trend_df = df.copy()
            if region != "all":
                trend_df = trend_df[trend_df["region"] == region]
            
            trend_agg = trend_df.groupby(["year", "quarter"]).agg({"sustainability_index": "mean"}).reset_index()
            trend_agg = add_period_column(trend_agg)
            trend_agg = trend_agg.sort_values(["year", "quarter"])
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=trend_agg["period"],
                y=trend_agg["sustainability_index"],
                mode="lines",
                fill='tozeroy',
                fillcolor=f'rgba(168, 85, 247, 0.2)',
                line=dict(color=COLORS.purple, width=3),
                hovertemplate='<b>%{x}</b><br>Index: %{y:.1f}<extra></extra>',
            ))
            fig.add_trace(go.Scatter(
                x=trend_agg["period"],
                y=trend_agg["sustainability_index"],
                mode="markers",
                marker=dict(size=8, color=COLORS.purple, line=dict(width=2, color="#fff")),
                hoverinfo="skip",
            ))
            
            apply_chart_theme(fig, height=280)
            st.plotly_chart(fig, width='stretch')
            card_close()
        
        with r1c2:
            card_open("Performance by Region", "Top 8 regions")
            
            regional_df = df[(df["year"] == year) & (df["quarter"] == quarter)].copy()
            
            if len(regional_df) > 0:
                regional_agg = regional_df.groupby("region").agg({"sustainability_index": "mean"}).reset_index()
                regional_agg = regional_agg.sort_values("sustainability_index", ascending=True).tail(8)
                
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    y=regional_agg["region"],
                    x=regional_agg["sustainability_index"],
                    orientation='h',
                    marker=dict(color=COLORS.purple),
                    text=[f"{v:.1f}" for v in regional_agg["sustainability_index"]],
                    textposition="outside",
                    textfont=dict(color=COLORS.text_muted, size=11),
                ))
                
                apply_chart_theme(fig, height=280)
                fig.update_layout(
                    xaxis=dict(showgrid=True),
                    yaxis=dict(showgrid=False, tickfont=dict(size=11)),
                    bargap=0.4,
                )
                st.plotly_chart(fig, width='stretch')
            else:
                st.info("No regional data available")
            
            card_close()
        
        spacer("md")
        
        # Row 2: Energy Mix + Mini Metrics
        r2c1, r2c2 = st.columns([0.42, 0.58], gap="large")
        
        with r2c1:
            card_open("Sustainability Breakdown", "Index composition")
            
            breakdown = sustainability.get("breakdown", [])
            
            if breakdown:
                labels = [item.get("name", item.get("name_en", "Unknown")) for item in breakdown[:6]]
                values = [item.get("contribution", 0) for item in breakdown[:6]]
                
                colors = [COLORS.purple, COLORS.cyan, COLORS.pink, "#f472b6", "#818cf8", "#4ade80"]
                
                fig = go.Figure(data=[go.Pie(
                    labels=labels,
                    values=values,
                    hole=0.6,
                    marker=dict(colors=colors[:len(labels)], line=dict(width=0)),
                    textinfo='percent',
                    textfont=dict(color="#fff", size=11),
                    hovertemplate='<b>%{label}</b><br>%{value:.1f} pts<extra></extra>',
                )])
                
                total = sum(values)
                fig.add_annotation(
                    text=f"<b>{total:.0f}</b><br>Total",
                    x=0.5, y=0.5,
                    font=dict(size=16, color="#fff"),
                    showarrow=False,
                )
                
                apply_chart_theme(fig, height=280)
                fig.update_layout(
                    showlegend=True, 
                    legend=dict(
                        orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5,
                        font=dict(size=10, color=COLORS.text_muted),
                    )
                )
                st.plotly_chart(fig, width='stretch')
            else:
                st.info("No breakdown data available")
            
            card_close()
        
        with r2c2:
            m1, m2 = st.columns(2, gap="large")
            
            green_jobs = metrics.get("green_jobs", {})
            green_jobs_val = green_jobs.get("value", 0) or 0
            green_jobs_delta = green_jobs.get("change_percent", 0) or 0
            
            with m1:
                render_mini_metric(
                    title="New Green Jobs",
                    value=f"{green_jobs_val/1000:.1f}K" if green_jobs_val >= 1000 else str(int(green_jobs_val)),
                    delta=float(green_jobs_delta),
                    ring_percent=min(90, max(10, green_jobs_val / 1000)),
                    subtitle="vs previous period",
                )
            
            fdi = metrics.get("foreign_investment", metrics.get("fdi", {}))
            fdi_val = fdi.get("value", 0) or 0
            fdi_delta = fdi.get("change_percent", 0) or 0
            
            with m2:
                render_mini_metric(
                    title="Foreign Investment",
                    value=f"{fdi_val:.1f}B" if fdi_val >= 1 else f"{fdi_val*1000:.0f}M",
                    delta=float(fdi_delta),
                    ring_percent=min(95, max(15, 50 + fdi_delta)),
                    subtitle="FDI inflows",
                )
        
        spacer("md")
        
        # Row 3: Yearly KPIs
        card_open("Yearly KPI Performance", "Multi-year comparison")
        
        trend_df = df.copy()
        if region != "all":
            trend_df = trend_df[trend_df["region"] == region]
        
        yearly = trend_df.groupby("year").agg({
            "sustainability_index": "mean",
            "gdp_growth": "mean",
            "renewable_share": "mean",
        }).reset_index()
        yearly = yearly.sort_values("year")
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            name="Sustainability",
            x=yearly["year"].astype(str),
            y=yearly["sustainability_index"],
            marker_color=COLORS.purple,
        ))
        fig.add_trace(go.Bar(
            name="GDP Growth",
            x=yearly["year"].astype(str),
            y=yearly["gdp_growth"] * 10,
            marker_color=COLORS.cyan,
        ))
        fig.add_trace(go.Bar(
            name="Renewables %",
            x=yearly["year"].astype(str),
            y=yearly["renewable_share"],
            marker_color=COLORS.pink,
        ))
        
        apply_chart_theme(fig, height=280)
        fig.update_layout(
            barmode='group',
            bargap=0.2,
            bargroupgap=0.1,
        )
        st.plotly_chart(fig, width='stretch')
        card_close()
        
        spacer("md")
        
        # Compact Sustainability Gauge
        card_open("Sustainability Index", "Overall performance score")
        
        index_value = sustainability.get("index", 0) or 0
        status = sustainability.get("status", "unknown")
        
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=index_value,
            number={'suffix': "/100", 'font': {'size': 32, 'color': '#fff'}},
            domain={'x': [0, 1], 'y': [0, 1]},
            gauge={
                'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': '#374151', 
                        'dtick': 25, 'tickfont': {'size': 10, 'color': COLORS.text_muted}},
                'bar': {'color': COLORS.purple, 'thickness': 0.7},
                'bgcolor': COLORS.bg_card,
                'borderwidth': 0,
                'steps': [
                    {'range': [0, 50], 'color': 'rgba(239, 68, 68, 0.3)'},
                    {'range': [50, 70], 'color': 'rgba(245, 158, 11, 0.3)'},
                    {'range': [70, 100], 'color': 'rgba(34, 197, 94, 0.3)'},
                ],
                'threshold': {
                    'line': {'color': COLORS.status_green, 'width': 3},
                    'thickness': 0.8,
                    'value': 70
                }
            },
        ))
        
        fig.update_layout(
            height=220,
            margin=dict(l=20, r=20, t=20, b=0),
            paper_bgcolor='rgba(0,0,0,0)',
        )
        st.plotly_chart(fig, width='stretch')
        
        status_color = COLORS.status_green if status == 'green' else COLORS.status_amber if status == 'amber' else COLORS.status_red
        status_text = 'On Track' if status == 'green' else 'At Risk' if status == 'amber' else 'Critical'
        st.markdown(f"""
            <div style="text-align: center; margin-top: -10px;">
                <span style="background: {status_color}22; color: {status_color}; padding: 6px 16px; 
                            border-radius: 6px; font-size: 13px; font-weight: 600;">
                    {status_text} • Target: 70
                </span>
            </div>
        """, unsafe_allow_html=True)
        card_close()
        
    except Exception as e:
        st.error(f"Error loading dashboard data: {str(e)}")
        import traceback
        st.code(traceback.format_exc())
