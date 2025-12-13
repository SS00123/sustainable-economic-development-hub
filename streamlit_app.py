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
        "Report a bug": "mailto:support@ministry.gov.sa",
        "About": """
        # Sustainable Economic Development Analytics Hub
        
        **Ministry of Economy and Planning**
        
        Data-driven insights for sustainable development policy.
        
        Version 2.0.0 – Multi-Page Architecture
        """,
    },
)

from analytics_hub_platform.infrastructure.db_init import initialize_database


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


def main() -> None:
    """Main application entry point - redirects to Dashboard page."""
    # Initialize session
    initialize_session_state()

    # Initialize database on first run
    if not st.session_state.get("initialized"):
        initialize_database()
        st.session_state["initialized"] = True

    # Welcome page
    st.markdown("""
    # 📊 Sustainable Economic Development Analytics Hub
    
    **Ministry of Economy and Planning**
    
    Welcome to the Analytics Hub. Please use the sidebar navigation to access different sections:
    
    - **📊 Dashboard** - Executive overview for ministerial briefing
    - **📈 KPIs** - Detailed key performance indicators
    - **📊 Trends** - Historical analysis and time-series
    - **📋 Data** - Data quality and raw data view
    - **🧠 Advanced Analytics** - ML forecasting and AI insights
    - **⚙️ Settings** - Configuration and preferences
    
    ---
    
    💡 **Tip:** Use the sidebar menu (▶️) to navigate between pages.
    """)


if __name__ == "__main__":
    main()

