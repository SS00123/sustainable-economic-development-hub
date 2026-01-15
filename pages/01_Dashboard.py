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
- AI Strategic Recommendations
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
from analytics_hub_platform.ui.page_init import initialize_page
from analytics_hub_platform.ui.pages.unified_dashboard import render_unified_dashboard

# Initialize page (session state, database, theme)
initialize_page()

# Render the full unified dashboard (includes AI recommendations)
render_unified_dashboard()


