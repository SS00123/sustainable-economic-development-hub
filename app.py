"""
Streamlit Application Entry Point
Sustainable Economic Development Analytics Hub
Ministry of Economy and Planning

Main Streamlit application for the analytics dashboard.
Run with: streamlit run app.py
"""

import streamlit as st

# Page configuration must be first Streamlit command
st.set_page_config(
    page_title="Sustainable Economic Development Analytics Hub",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
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
from analytics_hub_platform.infrastructure.settings import get_settings
from analytics_hub_platform.ui.layout import inject_custom_css, render_footer
from analytics_hub_platform.ui.filters import render_global_filters, get_filter_state
from analytics_hub_platform.ui.pages import (
    render_executive_view,
    render_director_view,
    render_analyst_view,
    render_sustainability_trends,
    render_data_quality_view,
    render_admin_console,
)
from analytics_hub_platform.locale import get_strings
from analytics_hub_platform.config.branding import BRANDING


def initialize_session_state() -> None:
    """Initialize session state variables."""
    defaults = {
        "current_page": "executive",
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


def render_sidebar() -> str:
    """
    Render sidebar navigation.
    
    Returns:
        Selected page key
    """
    filters = get_filter_state()
    strings = get_strings(filters.language)
    
    with st.sidebar:
        # Logo and title
        st.markdown(f"""
        <div style="text-align: center; padding: 20px 0;">
            <h2 style="color: #003366; margin: 0;">🌱</h2>
            <h3 style="color: #003366; margin: 5px 0; font-size: 16px;">
                {strings.get("app_title", "Analytics Hub")}
            </h3>
            <p style="color: #64748B; font-size: 12px; margin: 0;">
                {strings.get("app_subtitle", "Ministry of Economy and Planning")}
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        # Navigation
        st.markdown("### " + strings.get("nav_home", "Navigation"))
        
        pages = {
            "executive": ("📊", strings.get("nav_executive", "Executive Dashboard")),
            "director": ("📈", strings.get("nav_director", "Director Dashboard")),
            "analyst": ("🔍", strings.get("nav_analyst", "Analyst Dashboard")),
            "sustainability": ("🌿", strings.get("nav_sustainability", "Sustainability Trends")),
            "data_quality": ("✅", strings.get("nav_data_quality", "Data Quality")),
            "admin": ("⚙️", strings.get("nav_admin", "Administration")),
        }
        
        selected_page = st.session_state.get("current_page", "executive")
        
        for page_key, (icon, label) in pages.items():
            is_selected = selected_page == page_key
            button_type = "primary" if is_selected else "secondary"
            
            if st.button(
                f"{icon} {label}",
                key=f"nav_{page_key}",
                use_container_width=True,
                type=button_type,
            ):
                st.session_state["current_page"] = page_key
                st.rerun()
        
        st.divider()
        
        # Global filters
        render_global_filters()
        
        st.divider()
        
        # Branding footer
        st.markdown(f"""
        <div style="text-align: center; padding: 10px 0; font-size: 11px; color: #64748B;">
            <p style="margin: 2px 0;">{BRANDING["author_name"]}</p>
            <p style="margin: 2px 0;">{BRANDING["author_email"]}</p>
            <p style="margin: 2px 0;">{BRANDING["author_mobile"]}</p>
        </div>
        """, unsafe_allow_html=True)
    
    return st.session_state.get("current_page", "executive")


def main() -> None:
    """Main application entry point."""
    # Initialize
    initialize_session_state()
    
    # Initialize database on first run
    if not st.session_state.get("initialized"):
        initialize_database()
        st.session_state["initialized"] = True
    
    # Inject custom CSS
    inject_custom_css()
    
    # Render sidebar and get selected page
    current_page = render_sidebar()
    
    # Route to appropriate page
    page_renderers = {
        "executive": render_executive_view,
        "director": render_director_view,
        "analyst": render_analyst_view,
        "sustainability": render_sustainability_trends,
        "data_quality": render_data_quality_view,
        "admin": render_admin_console,
    }
    
    renderer = page_renderers.get(current_page, render_executive_view)
    
    try:
        renderer()
    except Exception as e:
        st.error(f"Error rendering page: {str(e)}")
        st.exception(e)


if __name__ == "__main__":
    main()
