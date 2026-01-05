"""
Streamlit Application Entry Point
Sustainable Economic Development Analytics Hub
Ministry of Economy and Planning

Multi-page structure:
- Dashboard (Minister View)
- KPIs
- Trends
- Data
- Advanced Analytics
- Settings

Run with: streamlit run streamlit_app.py
"""

import streamlit as st

# Page configuration (must be first Streamlit command)
st.set_page_config(
    page_title="Sustainable Economic Development – Minister View",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        "Get Help": "https://ministry.gov.sa/help",
        "Report a bug": "mailto:sultan_mutep@hotmail.com",
        "About": """
        # Sustainable Economic Development Analytics Hub

        **Ministry of Economy and Planning**

        Data-driven insights for sustainable development policy.

        Version 2.0.0 – Multi-Page Architecture
        """,
    },
)

from analytics_hub_platform.infrastructure.db_init import initialize_database
from analytics_hub_platform.ui.theme import get_dark_css
from analytics_hub_platform.ui.html import (
    render_html,
    render_rtl_aware_container_start,
    render_rtl_aware_container_end,
)
from analytics_hub_platform.ui.pages.unified_dashboard import render_unified_dashboard


def initialize_session_state() -> None:
    """Initialize session state variables with sensible defaults."""
    defaults = {
        "year": 2026,
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


def main() -> None:
    """Main application entry point - redirects to Dashboard page."""
    # Initialize session
    initialize_session_state()

    # Initialize database on first run
    if not st.session_state.get("initialized"):
        initialize_database()
        st.session_state["initialized"] = True

    # Get current language for RTL support
    language = st.session_state.get("language", "en")

    # Apply dark CSS using safe renderer
    render_html(get_dark_css())

    # Apply RTL wrapper if Arabic
    render_rtl_aware_container_start(language)

    # Render the executive dashboard
    render_unified_dashboard()

    # Close RTL wrapper
    render_rtl_aware_container_end()


if __name__ == "__main__":
    main()
