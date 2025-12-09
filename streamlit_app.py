"""
Streamlit Application Entry Point
Sustainable Economic Development Analytics Hub
Ministry of Economy and Planning

Run with: streamlit run app.py
"""

import streamlit as st

# Page configuration (must be first Streamlit command)
st.set_page_config(
    page_title="Sustainable Economic Development Analytics Hub",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        "Get Help": "https://ministry.gov.sa/help",
        "Report a bug": "mailto:support@ministry.gov.sa",
        "About": """
        # Sustainable Economic Development Analytics Hub
        
        **Ministry of Economy and Planning**
        
        Data-driven insights for sustainable development policy.
        
        Version 1.0.0
        """,
    },
)

from analytics_hub_platform.infrastructure.db_init import initialize_database
from analytics_hub_platform.ui.layout import inject_custom_css
from analytics_hub_platform.ui.pages.unified_dashboard import render_unified_dashboard


def initialize_session_state() -> None:
    """Initialize session state variables with sensible defaults."""
    defaults = {
        "year": 2024,
        "quarter": 4,
        "region": "all",
        "language": "en",
        "user_role": "ANALYST",
        "initialized": False,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def main() -> None:
    """Main application entry point."""
    # Initialize session
    initialize_session_state()

    # Initialize database on first run
    if not st.session_state.get("initialized"):
        initialize_database()
        st.session_state["initialized"] = True

    # Inject global CSS theme
    inject_custom_css()

    # Render unified professional dashboard (all in one page, no sidebar/tabs)
    render_unified_dashboard()


if __name__ == "__main__":
    main()

