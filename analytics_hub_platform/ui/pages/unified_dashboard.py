"""
Unified Professional Dashboard
Sustainable Economic Development Analytics Hub
Ministry of Economy and Planning

Single-page professional dashboard combining all views:
- Executive summary with KPIs
- Sustainability index
- Trend analysis
- Regional comparison
- Insights and narratives

No sidebar, no tabs - one seamless scrolling experience.
"""

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import yaml
from pathlib import Path

from analytics_hub_platform.config.theme import get_theme
from analytics_hub_platform.config.branding import BRANDING
from analytics_hub_platform.infrastructure.repository import get_repository
from analytics_hub_platform.infrastructure.settings import get_settings
from analytics_hub_platform.domain.models import FilterParams
from analytics_hub_platform.domain.services import (
    get_executive_snapshot,
    get_sustainability_summary,
    get_data_quality_metrics,
)
from analytics_hub_platform.domain.indicators import calculate_change
from analytics_hub_platform.utils.narratives import generate_executive_narrative
from analytics_hub_platform.utils.kpi_utils import get_kpi_unit
from analytics_hub_platform.locale import get_strings


def render_unified_dashboard() -> None:
    """Render the unified professional dashboard - single page, no sidebar/tabs."""
    theme = get_theme()
    
    # Get filter state from session
    year = st.session_state.get("year", 2024)
    quarter = st.session_state.get("quarter", 4)
    region = st.session_state.get("region", "all")
    language = st.session_state.get("language", "en")
    strings = get_strings(language)
    
    # =========================================================================
    # PROFESSIONAL HEADER
    # =========================================================================
    header_html = f"""
    <div style="
        background: linear-gradient(135deg, {theme.colors.primary} 0%, {theme.colors.secondary} 100%);
        padding: 32px 40px;
        border-radius: 16px;
        margin-bottom: 32px;
        box-shadow: 0 10px 40px -10px rgba(18, 67, 109, 0.3);
        position: relative;
        overflow: hidden;
    ">
        <div style="
            position: absolute;
            top: -50px;
            right: -50px;
            width: 200px;
            height: 200px;
            background: rgba(255,255,255,0.05);
            border-radius: 50%;
        "></div>
        <div style="
            position: absolute;
            bottom: -30px;
            left: 30%;
            width: 100px;
            height: 100px;
            background: rgba(255,255,255,0.03);
            border-radius: 50%;
        "></div>
        
        <div style="display: flex; justify-content: space-between; align-items: flex-start; position: relative; z-index: 1;">
            <div>
                <div style="display: flex; align-items: center; gap: 16px; margin-bottom: 8px;">
                    <span style="font-size: 40px;">🌱</span>
                    <h1 style="
                        color: white;
                        margin: 0;
                        font-size: 32px;
                        font-weight: 700;
                        letter-spacing: -0.5px;
                    ">Sustainable Economic Development</h1>
                </div>
                <p style="
                    color: rgba(255,255,255,0.9);
                    font-size: 16px;
                    margin: 0 0 0 56px;
                    font-weight: 500;
                ">Analytics Hub • Ministry of Economy and Planning</p>
            </div>
            <div style="text-align: right;">
                <div style="
                    background: rgba(255,255,255,0.15);
                    padding: 12px 20px;
                    border-radius: 8px;
                    backdrop-filter: blur(10px);
                ">
                    <p style="color: rgba(255,255,255,0.8); margin: 0; font-size: 12px; text-transform: uppercase; letter-spacing: 1px;">Reporting Period</p>
                    <p style="color: white; margin: 4px 0 0 0; font-size: 20px; font-weight: 700;">Q{quarter} {year}</p>
                </div>
            </div>
        </div>
    </div>
    """
    components.html(header_html, height=180)
    
    # =========================================================================
    # INLINE FILTERS
    # =========================================================================
    with st.container():
        col_f1, col_f2, col_f3, col_f4 = st.columns([1, 1, 1, 2])
        with col_f1:
            new_year = st.selectbox("Year", [2024, 2023, 2022, 2021], index=[2024, 2023, 2022, 2021].index(year), key="filter_year")
        with col_f2:
            new_quarter = st.selectbox("Quarter", [1, 2, 3, 4], index=quarter - 1, key="filter_quarter")
        with col_f3:
            regions = ["all", "Riyadh", "Makkah", "Eastern Province", "Madinah", "Qassim", "Asir", "Tabuk", "Hail", "Northern Borders", "Jazan", "Najran", "Al Bahah", "Al Jawf"]
            new_region = st.selectbox("Region", regions, index=regions.index(region) if region in regions else 0, key="filter_region")
        with col_f4:
            st.markdown("")  # Spacer
        
        # Update session state if changed
        if new_year != year or new_quarter != quarter or new_region != region:
            st.session_state["year"] = new_year
            st.session_state["quarter"] = new_quarter
            st.session_state["region"] = new_region
            st.rerun()
    
    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
    
    # =========================================================================
    # LOAD DATA
    # =========================================================================
    try:
        repo = get_repository()
        settings = get_settings()
        
        filter_params = FilterParams(
            tenant_id=settings.default_tenant_id,
            year=year,
            quarter=quarter,
            region=region if region != "all" else None,
        )
        
        df = repo.get_all_indicators(settings.default_tenant_id)
        snapshot = get_executive_snapshot(df, filter_params, language)
        sustainability = get_sustainability_summary(df, filter_params, language)
        catalog = _get_catalog()
        metrics = _enrich_metrics(df, snapshot.get("metrics", {}), filter_params, catalog)
        quality_metrics = get_data_quality_metrics(df, filter_params)
        
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return
    
    # Check for no data
    if snapshot.get("status") == "no_data" or sustainability.get("status") == "no_data":
        st.warning(f"⚠️ No data available for Q{quarter} {year}. Please select a different period.")
        return
    
    # =========================================================================
    # METADATA ROW: Data Freshness & Coverage
    # =========================================================================
    meta_col1, meta_col2, meta_col3, meta_col4 = st.columns(4)
    
    total_records = len(df)
    total_kpis = len(metrics)
    avg_quality = quality_metrics.get("avg_quality_score", 0)
    last_update = quality_metrics.get("last_update")
    update_str = last_update.strftime("%Y-%m-%d") if last_update else "N/A"
    
    with meta_col1:
        st.metric("📊 Total KPIs", f"{total_kpis}", help="Number of tracked indicators")
    with meta_col2:
        st.metric("📈 Data Records", f"{total_records:,}", help="Total data points in database")
    with meta_col3:
        st.metric("✅ Data Quality", f"{avg_quality:.1f}/100", help="Average quality score")
    with meta_col4:
        st.metric("🕒 Last Updated", update_str, help="Most recent data refresh")
    
    st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)
    
    # =========================================================================
    # SECTION 1: SUSTAINABILITY INDEX (Hero Section)
    # =========================================================================
    _render_section_title("🌱 Sustainability Index", "Composite score measuring sustainable development progress")
    
    col_gauge, col_details = st.columns([2, 1])
    
    with col_gauge:
        index_value = sustainability.get("index", 0) or 0
        
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=index_value,
            number={'suffix': "", 'font': {'size': 48, 'color': theme.colors.primary}},
            delta={'reference': 70, 'increasing': {'color': theme.colors.status_green}, 'decreasing': {'color': theme.colors.status_red}},
            domain={'x': [0, 1], 'y': [0, 1]},
            gauge={
                'axis': {'range': [0, 100], 'tickwidth': 2, 'tickcolor': theme.colors.text_muted, 'tickmode': 'linear', 'tick0': 0, 'dtick': 10},
                'bar': {'color': theme.colors.primary, 'thickness': 0.75},
                'bgcolor': theme.colors.surface_alt,
                'borderwidth': 0,
                'steps': [
                    {'range': [0, 50], 'color': theme.colors.status_red_bg},
                    {'range': [50, 70], 'color': theme.colors.status_amber_bg},
                    {'range': [70, 100], 'color': theme.colors.status_green_bg},
                ],
                'threshold': {
                    'line': {'color': theme.colors.secondary, 'width': 4},
                    'thickness': 0.8,
                    'value': 70
                }
            },
            title={'text': "Target: 70", 'font': {'size': 14, 'color': theme.colors.text_muted}}
        ))
        
        fig.update_layout(
            height=280,
            margin=dict(l=30, r=30, t=30, b=10),
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family=theme.typography.font_family),
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col_details:
        status = sustainability.get("status", "unknown")
        status_color = theme.colors.status_green if status == "green" else theme.colors.status_amber if status == "amber" else theme.colors.status_red
        status_label = "On Track" if status == "green" else "At Risk" if status == "amber" else "Critical"
        
        details_html = f"""
        <div style="padding: 16px;">
            <div style="
                display: inline-block;
                background: {status_color}20;
                color: {status_color};
                padding: 8px 20px;
                border-radius: 20px;
                font-weight: 600;
                font-size: 14px;
                margin-bottom: 20px;
            ">● {status_label}</div>
            
            <h4 style="color: {theme.colors.text_muted}; margin: 20px 0 12px 0; font-size: 13px; text-transform: uppercase; letter-spacing: 1px;">Top Contributors</h4>
        </div>
        """
        components.html(details_html, height=100)
        
        breakdown = sustainability.get("breakdown", [])[:4]
        for item in breakdown:
            name = item.get("name", item.get("name_en", ""))
            contribution = item.get("contribution", 0) or 0
            item_status = item.get("status", "neutral")
            emoji = "🟢" if item_status == "green" else "🟡" if item_status == "amber" else "🔴" if item_status == "red" else "⚪"
            st.markdown(f"{emoji} **{name}**: {contribution:.1f} pts")
    
    st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)
    
    # =========================================================================
    # SECTION 2: KEY PERFORMANCE INDICATORS
    # =========================================================================
    _render_section_title("📊 Key Performance Indicators", "Core metrics for Q" + str(quarter) + " " + str(year))
    
    # Economic block
    _render_subgrid("Economic Performance", [
        "gdp_growth", "gdp_total", "foreign_investment", "export_diversity_index", "economic_complexity",
    ], metrics, theme)

    # Labor & skills
    _render_subgrid("Labor & Skills", [
        "unemployment_rate", "green_jobs", "skills_gap_index", "population",
    ], metrics, theme, columns=4)

    # Social & digital
    _render_subgrid("Social & Digital", [
        "social_progress_score", "digital_readiness", "innovation_index",
    ], metrics, theme, columns=3)

    # Environmental / sustainability
    _render_subgrid("Environmental & Sustainability", [
        "sustainability_index", "co2_index", "co2_total", "renewable_share", "energy_intensity",
        "water_efficiency", "waste_recycling_rate", "forest_coverage", "air_quality_index",
        "co2_per_gdp", "co2_per_capita",
    ], metrics, theme, columns=4)

    # Data quality
    _render_subgrid("Data Quality", [
        "data_quality_score",
    ], metrics, theme, columns=1)
    
    # Section divider
    st.markdown("---")
    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
    
    # =========================================================================
    # SECTION 3: TREND ANALYSIS
    # =========================================================================
    _render_section_title("📈 Trend Analysis", "Historical performance over time")
    
    trend_col1, trend_col2 = st.columns([3, 1])
    
    with trend_col2:
        kpi_options = {
            "sustainability_index": "Sustainability Index",
            "gdp_growth": "GDP Growth",
            "renewable_share": "Renewable Energy",
            "co2_index": "CO2 Intensity",
            "unemployment_rate": "Unemployment",
            "green_jobs": "Green Jobs",
        }
        selected_kpi = st.selectbox("Select Indicator", list(kpi_options.keys()), format_func=lambda x: kpi_options[x], key="trend_kpi")
    
    with trend_col1:
        trend_df = df.copy()
        if region != "all":
            trend_df = trend_df[trend_df["region"] == region]
        
        trend_agg = trend_df.groupby(["year", "quarter"]).agg({selected_kpi: "mean"}).reset_index()
        trend_agg["period"] = trend_agg.apply(lambda r: f"Q{int(r['quarter'])} {int(r['year'])}", axis=1)
        trend_agg = trend_agg.sort_values(["year", "quarter"])
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=trend_agg["period"],
            y=trend_agg[selected_kpi],
            mode="lines+markers",
            name=kpi_options[selected_kpi],
            line=dict(color=theme.colors.primary, width=3),
            marker=dict(size=10, color=theme.colors.primary),
            fill='tozeroy',
            fillcolor=f'rgba(18, 67, 109, 0.1)',
            hovertemplate='<b>%{x}</b><br>Value: %{y:.1f}<extra></extra>',
        ))
        
        # Add trend line
        if len(trend_agg) > 2:
            x_numeric = np.arange(len(trend_agg))
            z = np.polyfit(x_numeric, trend_agg[selected_kpi].values, 1)
            p = np.poly1d(z)
            fig.add_trace(go.Scatter(
                x=trend_agg["period"],
                y=p(x_numeric),
                mode="lines",
                name="Trend",
                line=dict(color=theme.colors.secondary, width=2, dash="dash"),
            ))
        
        fig.update_layout(
            height=350,
            margin=dict(l=20, r=20, t=20, b=40),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.05)'),
            yaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.05)'),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            font=dict(family=theme.typography.font_family),
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Section divider
    st.markdown("---")
    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
    
    # =========================================================================
    # SECTION 4: REGIONAL COMPARISON
    # =========================================================================
    _render_section_title("🗺️ Regional Comparison", "Performance across regions for current period")
    
    regional_df = df[(df["year"] == year) & (df["quarter"] == quarter)].copy()
    
    if len(regional_df) > 0:
        reg_col1, reg_col2 = st.columns([2, 1])
        
        with reg_col1:
            regional_agg = regional_df.groupby("region").agg({"sustainability_index": "mean"}).reset_index()
            regional_agg = regional_agg.sort_values("sustainability_index", ascending=True)
            national_avg = regional_agg["sustainability_index"].mean()
            
            colors = [theme.colors.status_green if v >= national_avg else theme.colors.status_amber for v in regional_agg["sustainability_index"]]
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                y=regional_agg["region"],
                x=regional_agg["sustainability_index"],
                orientation='h',
                marker_color=colors,
                text=[f"{v:.1f}" for v in regional_agg["sustainability_index"]],
                textposition="outside",
            ))
            fig.add_vline(x=national_avg, line_dash="dash", line_color=theme.colors.primary, annotation_text=f"Avg: {national_avg:.1f}")
            
            fig.update_layout(
                height=400,
                margin=dict(l=20, r=60, t=20, b=20),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.05)', title="Sustainability Index"),
                yaxis=dict(showgrid=False),
                font=dict(family=theme.typography.font_family),
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with reg_col2:
            st.markdown("**📊 Regional Statistics**")
            st.metric("National Average", f"{national_avg:.1f}")
            st.metric("Highest", f"{regional_agg['sustainability_index'].max():.1f}")
            st.metric("Lowest", f"{regional_agg['sustainability_index'].min():.1f}")
            
            st.markdown("---")
            st.markdown("**🏆 Top 3 Regions**")
            for _, row in regional_agg.tail(3).iloc[::-1].iterrows():
                st.markdown(f"• {row['region']}: **{row['sustainability_index']:.1f}**")
    else:
        st.info("No regional data available for this period.")
    
    # Section divider
    st.markdown("---")
    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    # =========================================================================
    # SECTION 5: ENVIRONMENTAL & SUSTAINABILITY TRENDS (MULTI-KPI)
    # =========================================================================
    _render_section_title("🌿 Sustainability & Environmental Trends", "Multi-indicator performance over time")

    env_kpis = [
        "co2_index", "renewable_share", "energy_intensity", "water_efficiency",
        "waste_recycling_rate", "air_quality_index", "forest_coverage", "green_jobs",
    ]

    trend_env = df.groupby(["year", "quarter"]).agg({k: "mean" for k in env_kpis}).reset_index()
    trend_env["period"] = trend_env.apply(lambda r: f"Q{int(r['quarter'])} {int(r['year'])}", axis=1)
    trend_env = trend_env.sort_values(["year", "quarter"])

    fig_env = go.Figure()
    palette = [
        theme.colors.primary, theme.colors.secondary, theme.colors.success,
        "#0891B2", "#7C3AED", "#D97706", "#059669", "#EC4899",
    ]
    label_map = {
        "co2_index": "CO2 Intensity",
        "renewable_share": "Renewables %",
        "energy_intensity": "Energy Intensity",
        "water_efficiency": "Water Efficiency",
        "waste_recycling_rate": "Recycling Rate",
        "air_quality_index": "Air Quality",
        "forest_coverage": "Forest Coverage",
        "green_jobs": "Green Jobs",
    }

    for i, kpi in enumerate(env_kpis):
        if kpi not in trend_env.columns:
            continue
        fig_env.add_trace(go.Scatter(
            x=trend_env["period"],
            y=trend_env[kpi],
            mode="lines+markers",
            name=label_map.get(kpi, kpi),
            line=dict(color=palette[i % len(palette)], width=2),
            hovertemplate='<b>%{fullData.name}</b><br>%{x}<br>Value: %{y:.1f}<extra></extra>',
        ))

    fig_env.update_layout(
        height=420,
        margin=dict(l=20, r=20, t=20, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.05)'),
        yaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.05)'),
        font=dict(family=theme.typography.font_family),
    )
    st.plotly_chart(fig_env, use_container_width=True)

    # Section divider
    st.markdown("---")
    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    # =========================================================================
    # SECTION 6: DATA QUALITY
    # =========================================================================
    _render_section_title("✅ Data Quality Overview", "Completeness and quality health for current period")

    dq_col1, dq_col2, dq_col3, dq_col4 = st.columns(4)
    completeness = quality_metrics.get("completeness", 0)
    avg_quality = quality_metrics.get("avg_quality_score") or 0
    records = quality_metrics.get("records_count", 0)
    last_update = quality_metrics.get("last_update")
    update_str = last_update.strftime("%Y-%m-%d") if last_update else "N/A"

    with dq_col1:
        st.metric("Data Completeness", f"{completeness:.1f}%")
    with dq_col2:
        st.metric("Quality Score", f"{avg_quality:.1f}")
    with dq_col3:
        st.metric("Records", f"{records:,}")
    with dq_col4:
        st.metric("Last Updated", update_str)

    missing_by_kpi = quality_metrics.get("missing_by_kpi", {})
    if missing_by_kpi:
        st.markdown("---")
        _render_section_title("📉 Completeness by Indicator", "Identify gaps across KPIs")

        completeness_data = [
            {"Indicator": k, "Completeness": 100 - v.get("percent", 0)} for k, v in missing_by_kpi.items()
        ]
        comp_df = pd.DataFrame(completeness_data)
        comp_df = comp_df.sort_values("Completeness", ascending=True)

        colors = [
            theme.colors.status_green if v >= 90 else theme.colors.status_amber if v >= 70 else theme.colors.status_red
            for v in comp_df["Completeness"]
        ]

        fig_comp = go.Figure()
        fig_comp.add_trace(go.Bar(
            x=comp_df["Completeness"],
            y=comp_df["Indicator"],
            orientation="h",
            marker_color=colors,
            text=[f"{v:.1f}%" for v in comp_df["Completeness"]],
            textposition="outside",
        ))
        fig_comp.add_vline(x=90, line_dash="dash", line_color=theme.colors.status_green, annotation_text="Target 90%")
        fig_comp.update_layout(
            height=420,
            margin=dict(l=20, r=80, t=20, b=20),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis_title="Completeness (%)",
            xaxis_range=[0, 105],
            font=dict(family=theme.typography.font_family),
        )
        st.plotly_chart(fig_comp, use_container_width=True)
    
    # Section divider
    st.markdown("---")
    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
    
    # =========================================================================
    # SECTION 7: INSIGHTS & NARRATIVE
    # =========================================================================
    _render_section_title("💡 Strategic Insights & Analysis", "AI-generated executive briefing with actionable recommendations")
    
    narrative = generate_executive_narrative(snapshot, language)
    
    # Render narrative in a professional styled container
    narrative_html = f"""
    <div style="
        background: linear-gradient(to bottom right, {theme.colors.surface} 0%, {theme.colors.surface_alt} 100%);
        border: 1px solid {theme.colors.border};
        border-left: 4px solid {theme.colors.primary};
        border-radius: 12px;
        padding: 32px;
        line-height: 1.9;
        font-size: 14.5px;
        color: {theme.colors.text_secondary};
        box-shadow: {theme.shadows.md};
        max-height: 600px;
        overflow-y: auto;
    ">
        <style>
            /* Markdown styling for narrative */
            h3 {{
                color: {theme.colors.text_primary};
                font-size: 18px;
                font-weight: 700;
                margin: 24px 0 12px 0;
                padding-bottom: 8px;
                border-bottom: 2px solid {theme.colors.border};
            }}
            h3:first-child {{
                margin-top: 0;
            }}
            strong {{
                color: {theme.colors.text_primary};
                font-weight: 600;
            }}
            em {{
                color: {theme.colors.text_muted};
                font-style: italic;
            }}
            hr {{
                border: none;
                border-top: 1px solid {theme.colors.border};
                margin: 20px 0;
                opacity: 0.5;
            }}
            ul {{
                margin: 8px 0;
                padding-left: 0;
                list-style: none;
            }}
            li {{
                margin: 6px 0;
                padding-left: 0;
            }}
            p {{
                margin: 12px 0;
            }}
        </style>
        {narrative.replace(chr(10), '<br>')}
    </div>
    """
    st.markdown(narrative_html, unsafe_allow_html=True)
    
    st.markdown("<div style='height: 48px;'></div>", unsafe_allow_html=True)
    
    # =========================================================================
    # PROFESSIONAL FOOTER
    # =========================================================================
    footer_html = f"""
    <div style="
        border-top: 1px solid {theme.colors.border};
        padding: 24px 0;
        text-align: center;
        background: {theme.colors.surface_alt};
        border-radius: 0 0 12px 12px;
        margin-top: 24px;
    ">
        <p style="color: {theme.colors.text_muted}; font-size: 12px; margin: 0 0 8px 0;">
            Sustainable Economic Development Analytics Hub • Ministry of Economy and Planning
        </p>
        <p style="color: {theme.colors.text_muted}; font-size: 11px; margin: 0;">
            Developed by {BRANDING["author_name"]} • {BRANDING["author_mobile"]} • {BRANDING["author_email"]}
        </p>
    </div>
    """
    components.html(footer_html, height=100)


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def _render_section_title(title: str, subtitle: str = "") -> None:
    """Render a professional section title."""
    theme = get_theme()
    html = f"""
    <div style="margin: 8px 0 20px 0;">
        <h2 style="
            color: {theme.colors.text_primary};
            font-size: 22px;
            font-weight: 700;
            margin: 0 0 4px 0;
            display: flex;
            align-items: center;
            gap: 8px;
        ">{title}</h2>
        <p style="
            color: {theme.colors.text_muted};
            font-size: 14px;
            margin: 0;
        ">{subtitle}</p>
    </div>
    """
    components.html(html, height=70)


def _render_kpi_card(kpi: dict, kpi_id: str, theme) -> None:
    """Render a professional KPI card with icon, delta, and status pill."""
    value = kpi.get("value", 0) or 0
    label = kpi.get("display_name", kpi_id.replace("_", " ").title())
    delta = kpi.get("change_percent")
    status = kpi.get("status", "neutral")
    unit = get_kpi_unit(kpi_id)

    category = kpi.get("category")
    category_icon = kpi.get("category_icon", "")

    # Domain colors by category
    domain_color = {
        "economic": theme.colors.primary,
        "labor": "#7C3AED",
        "social": "#0EA5E9",
        "environmental": theme.colors.eco_green,
        "composite": theme.colors.secondary,
        "data_quality": theme.colors.status_amber,
    }.get(category, theme.colors.primary)

    # Status colors
    status_color = (
        theme.colors.status_green
        if status == "green"
        else theme.colors.status_amber
        if status == "amber"
        else theme.colors.status_red
        if status == "red"
        else theme.colors.text_muted
    )

    status_label = {
        "green": "On Track",
        "amber": "Watch",
        "red": "Needs Attention",
    }.get(status, "Neutral")

    # Delta display
    delta_html = ""
    if delta is not None:
        delta_color = (
            theme.colors.status_green
            if delta > 0
            else theme.colors.status_red
            if delta < 0
            else theme.colors.text_muted
        )
        delta_arrow = "↑" if delta > 0 else "↓" if delta < 0 else "→"
        delta_html = (
            f'<span style="color: {delta_color}; font-size: 12px; font-weight: 600;">'
            f"{delta_arrow} {abs(delta):.1f}%"  # noqa: ISC003
            "</span>"
        )

    card_html = f"""
    <div style="
        background: {theme.colors.surface};
        border: 1px solid {theme.colors.border};
        border-radius: 10px;
        padding: 14px 16px 12px 16px;
        box-shadow: {theme.shadows.sm};
    ">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
            <div style="display: flex; align-items: center; gap: 6px;">
                <span style="font-size: 14px; color: {domain_color};">{category_icon}</span>
                <span style="
                    color: {theme.colors.text_muted};
                    font-size: 11px;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                ">{label}</span>
            </div>
        </div>
        <div style="display: flex; align-items: baseline; gap: 8px; margin-bottom: 6px;">
            <span style="
                color: {theme.colors.text_primary};
                font-size: 26px;
                font-weight: 700;
            ">{value:.1f}</span>
            <span style="
                color: {theme.colors.text_muted};
                font-size: 13px;
            ">{unit}</span>
        </div>
        <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 2px;">
            <div>{delta_html}</div>
            <div style="
                padding: 2px 10px;
                border-radius: 999px;
                font-size: 11px;
                font-weight: 600;
                color: {status_color};
                background: {status_color}20;
            ">{status_label}</div>
        </div>
    </div>
    """
    components.html(card_html, height=132)


def _render_subgrid(title: str, kpis: list, metrics: dict, theme, columns: int = 4) -> None:
    """Render a titled KPI subgrid for a list of KPI ids."""
    _render_section_title(f"{title}")
    cols = st.columns(columns)
    for idx, kpi_id in enumerate(kpis):
        col = cols[idx % columns]
        with col:
            _render_kpi_card(metrics.get(kpi_id, {}), kpi_id, theme)
        if (idx + 1) % columns == 0 and idx + 1 < len(kpis):
            st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)


# =============================================================================
# DATA HELPERS
# =============================================================================

def _get_catalog() -> dict:
    """Load KPI catalog from YAML (cached by Streamlit)."""
    if "_kpi_catalog_cache" not in st.session_state:
        catalog_path = Path(__file__).parent.parent.parent / "config" / "kpi_catalog.yaml"
        if catalog_path.exists():
            with open(catalog_path, "r", encoding="utf-8") as f:
                st.session_state["_kpi_catalog_cache"] = yaml.safe_load(f)
        else:
            st.session_state["_kpi_catalog_cache"] = {"kpis": []}
    return st.session_state.get("_kpi_catalog_cache", {"kpis": []})


def _enrich_metrics(df: pd.DataFrame, base_metrics: dict, filters: FilterParams, catalog: dict) -> dict:
    """Ensure all KPIs in catalog exist in metrics, computing current values if missing.

    Also attaches domain category and icon metadata for consistent KPI card styling.
    """
    metrics = {**base_metrics}

    # Build lookup maps from catalog
    name_map = {}
    category_map = {}
    categories_cfg = {c.get("id"): c for c in catalog.get("categories", [])}

    for kpi in catalog.get("kpis", []):
        kpi_id = kpi.get("id")
        if not kpi_id:
            continue
        name_map[kpi_id] = kpi.get("display_name_en", kpi_id)
        cat_id = kpi.get("category")
        category_map[kpi_id] = cat_id

        # Attach category + icon to existing snapshot metrics
        if kpi_id in metrics:
            metrics[kpi_id].setdefault("display_name", name_map[kpi_id])
            metrics[kpi_id]["category"] = cat_id
            if cat_id in categories_cfg:
                metrics[kpi_id]["category_icon"] = categories_cfg[cat_id].get("icon", "")

    target_kpis = [k.get("id") for k in catalog.get("kpis", []) if k.get("id")]
    for kpi_id in target_kpis:
        if kpi_id not in metrics:
            metric = _calc_metric_from_df(df, filters, kpi_id, name_map)
            # Attach category + icon on computed metrics
            cat_id = category_map.get(kpi_id)
            if cat_id:
                metric["category"] = cat_id
                if cat_id in categories_cfg:
                    metric["category_icon"] = categories_cfg[cat_id].get("icon", "")
            metrics[kpi_id] = metric

    return metrics


def _calc_metric_from_df(df: pd.DataFrame, filters: FilterParams, kpi_id: str, name_map: dict) -> dict:
    """Compute simple current value and delta for a KPI from dataframe when not in snapshot."""
    current = df[(df["year"] == filters.year) & (df["quarter"] == filters.quarter)]
    if filters.region and filters.region != "all":
        current = current[current["region"] == filters.region]

    prev_year = filters.year
    prev_quarter = filters.quarter - 1
    if prev_quarter == 0:
        prev_quarter = 4
        prev_year -= 1

    previous = df[(df["year"] == prev_year) & (df["quarter"] == prev_quarter)]
    if filters.region and filters.region != "all":
        previous = previous[previous["region"] == filters.region]

    current_val = float(current[kpi_id].mean()) if kpi_id in current and len(current) > 0 and not current[kpi_id].isna().all() else None
    previous_val = float(previous[kpi_id].mean()) if kpi_id in previous and len(previous) > 0 and not previous[kpi_id].isna().all() else None

    abs_change, pct_change = calculate_change(current_val, previous_val)

    return {
        "value": current_val if current_val is not None else 0,
        "previous_value": previous_val,
        "change": abs_change,
        "change_percent": pct_change,
        "status": "neutral",
        "display_name": name_map.get(kpi_id, kpi_id.replace("_", " ").title()),
        "higher_is_better": True,
    }
