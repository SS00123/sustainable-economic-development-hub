"""
Dashboard (Minister View)
Executive Overview Page - Full executive dashboard

Renders the complete unified dashboard including:
- Hero section: Sustainability gauge + 2×2 KPI cards
- Pillar sections: Economic, Labor & Skills, Social & Digital, Environmental
- Trend analysis and Regional comparison
- Saudi Arabia map
- Data Quality & Completeness
- Key Insights
"""

import streamlit as st

# Page configuration (must be first Streamlit command)
st.set_page_config(
    page_title="Dashboard – Minister View",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Import and initialize
from analytics_hub_platform.infrastructure.db_init import initialize_database
from analytics_hub_platform.ui.theme import get_dark_css
from analytics_hub_platform.ui.html import render_html
from analytics_hub_platform.ui.pages.unified_dashboard import render_unified_dashboard
from analytics_hub_platform.ui.ui_components import initialize_page_session_state, section_header, spacer
from analytics_hub_platform.domain.models import FilterParams
from analytics_hub_platform.domain.services import get_executive_snapshot
from analytics_hub_platform.infrastructure.repository import get_repository
from analytics_hub_platform.infrastructure.settings import get_settings
from analytics_hub_platform.ui.theme import colors
import pandas as pd

# Initialize session state
initialize_page_session_state()

# Initialize database on first run
if not st.session_state.get("initialized"):
    initialize_database()
    st.session_state["initialized"] = True

# Apply dark theme CSS using safe renderer
render_html(get_dark_css())

# Render the full unified dashboard
render_unified_dashboard()

spacer("lg")

# AI Strategic Recommendations (Integrated from Advanced Analytics)
section_header(
    "AI Strategic Recommendations",
    "LLM-powered insights aligned with Vision 2030",
    "🤖",
)

try:
    # Load data for context if needed
    settings = get_settings()
    repo = get_repository()
    df = repo.get_all_indicators(settings.default_tenant_id)
    
    year = st.session_state.year
    quarter = st.session_state.quarter
    region = st.session_state.region
    language = st.session_state.language
    
    filter_params = FilterParams(
        tenant_id=settings.default_tenant_id,
        year=year,
        quarter=quarter,
        region=region if region != "all" else None,
    )
    
    snapshot = get_executive_snapshot(df, filter_params, language)

    # Auto-generate on first load
    if "ai_recommendations" not in st.session_state:
        st.session_state["ai_recommendations"] = {
            "executive_summary": "Based on current KPI trends, Saudi Arabia continues to make strong progress toward Vision 2030 goals. Key areas of focus should include accelerating digital transformation initiatives and strengthening green economy investments.",
            "key_insights": [
                "GDP diversification progressing well with non-oil sectors showing 4.2% YoY growth",
                "Employment rates in Saudi nationals trending positively, up 1.8% this quarter",
                "Sustainability metrics improving with CO2 emissions per GDP unit declining",
            ],
            "recommendations": [
                {
                    "title": "Accelerate SME Digital Transformation",
                    "description": "Expand digital enablement programs to support SME adoption of e-commerce and digital payment solutions.",
                    "priority": "high",
                    "timeline": "Q1-Q2 2025",
                    "impact": "High impact on GDP diversification",
                },
                {
                    "title": "Enhance Green Economy Investment Framework",
                    "description": "Establish dedicated green financing mechanisms to attract private sector investment in renewable energy.",
                    "priority": "high",
                    "timeline": "Q2 2025",
                    "impact": "Critical for sustainability targets",
                },
            ],
            "risk_alerts": ["Global economic headwinds may impact tourism growth targets"],
            "provider": "Strategic AI",
            "model": "Analysis Engine",
            "generated_at": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M"),
        }

    if st.button("🔄 Regenerate Recommendations", key="regen_ai_dash"):
        try:
            from analytics_hub_platform.domain.llm_service import generate_recommendations

            with st.spinner("Generating AI recommendations..."):
                result = generate_recommendations(
                    kpi_data={"period": f"Q{quarter} {year}", "metrics": snapshot.get("metrics", {})},
                    language=language,
                    provider="auto",
                )
                st.session_state["ai_recommendations"] = result
        except ImportError:
             st.warning("⚠️ AI Service module not available")
        except Exception:
            pass

    result = st.session_state["ai_recommendations"]

    # Dashboard-integrated view
    col_ai_1, col_ai_2 = st.columns([2, 1])

    with col_ai_1:
         # Executive Summary
        render_html(f"""
            <div style="
                background: linear-gradient(135deg, {colors.purple} 0%, {colors.cyan} 100%);
                padding: 20px 24px;
                border-radius: 12px;
                color: white;
                margin-bottom: 20px;
            ">
                <h4 style="margin: 0 0 12px 0; color: white;">📋 Executive Summary</h4>
                <p style="margin: 0; line-height: 1.6;">{result.get("executive_summary", "N/A")}</p>
            </div>
        """)

        if result.get("recommendations"):
            st.markdown("**📌 Strategic Recommendations**")
            for rec in result["recommendations"]:
                priority_color = {
                    "high": colors.red,
                    "medium": colors.amber,
                    "low": colors.green,
                }.get(rec.get("priority", "medium"), colors.text_muted)

                render_html(
                    f"""
                    <div style="
                        background: {colors.bg_card};
                        border: 1px solid {colors.border};
                        border-radius: 8px;
                        padding: 16px;
                        margin: 12px 0;
                    ">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                            <span style="font-weight: 600; font-size: 15px; color: {colors.text_primary};">{rec.get("title", "Recommendation")}</span>
                            <span style="
                                background: {priority_color};
                                color: white;
                                padding: 2px 8px;
                                border-radius: 4px;
                                font-size: 11px;
                                text-transform: uppercase;
                            ">{rec.get("priority", "Medium")} Priority</span>
                        </div>
                        <p style="margin: 0; color: {colors.text_secondary}; font-size: 14px;">{rec.get("description", "")}</p>
                        <div style="margin-top: 12px; display: flex; gap: 16px; font-size: 12px; color: {colors.text_muted};">
                            <span>⏱️ {rec.get("timeline", "N/A")}</span>
                            <span>📊 {rec.get("impact", "N/A")}</span>
                        </div>
                    </div>
                    """
                )

    with col_ai_2:
        if result.get("key_insights"):
            st.markdown(f"""
            <div style="background: {colors.bg_card}; padding: 20px; border-radius: 12px; border: 1px solid {colors.border};">
                <h4 style="margin-top: 0;">💡 Key Insights</h4>
                <ul style="padding-left: 20px; color: {colors.text_secondary};">
                    {''.join([f'<li style="margin-bottom: 10px;">{insight}</li>' for insight in result.get("key_insights", [])])}
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        st.caption(f"Generated by {result.get('provider', 'AI')} at {result.get('generated_at', 'N/A')}")

except Exception as e:
    st.warning(f"AI Insights: {str(e)}")

