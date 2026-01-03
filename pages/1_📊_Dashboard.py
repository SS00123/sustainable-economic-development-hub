"""
Dashboard (Minister View)
Executive Overview Page - Full executive dashboard matching PDF design spec

Renders the complete unified dashboard including:
- Hero section: Sustainability gauge + 2×2 KPI cards (GDP, Unemployment, CO2, Data Quality)
- Pillar sections: Economic, Labor & Skills, Social & Digital, Environmental
- Trend analysis and Regional comparison
- Saudi Arabia map
- Data Quality & Completeness
- Key Insights (Improvements / Needs Attention)
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
from analytics_hub_platform.ui.dark_theme import get_dark_css
from analytics_hub_platform.ui.pages.unified_dashboard import render_unified_dashboard


def initialize_session_state() -> None:
    """Initialize session state variables with sensible defaults."""
    defaults = {
        "year": 2024,
        "quarter": 4,
        "region": "all",
        "language": "en",
        "user_role": "EXECUTIVE",
        "initialized": False,
        "theme": "dark",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# Initialize session state
initialize_session_state()

# Initialize database on first run
if not st.session_state.get("initialized"):
    initialize_database()
    st.session_state["initialized"] = True

# Apply dark theme CSS
st.markdown(get_dark_css(), unsafe_allow_html=True)

# Render the full unified dashboard (matches PDF design spec)
render_unified_dashboard()
