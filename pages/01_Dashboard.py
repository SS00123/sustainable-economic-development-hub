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
from analytics_hub_platform.ui.ui_components import initialize_page_session_state

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
