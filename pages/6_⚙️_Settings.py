"""
Settings Page
Configuration and Preferences

Displays:
- Language selection
- Theme preferences
- Target configuration
- User preferences
"""

import streamlit as st

# Page configuration
st.set_page_config(
    page_title="Settings",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Import application modules
from analytics_hub_platform.infrastructure.db_init import initialize_database
from analytics_hub_platform.ui.dark_theme import get_dark_css
from analytics_hub_platform.ui.ui_theme import COLORS
from analytics_hub_platform.ui.ui_components import section_header, spacer, info_banner, card_container
from analytics_hub_platform.ui.dark_components import render_sidebar


# Initialize session state
def initialize_session_state() -> None:
    defaults = {
        "year": 2024,
        "quarter": 4,
        "region": "all",
        "language": "en",
        "theme": "dark",
        "sustainability_target": 70,
        "gdp_target": 5.0,
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

# Layout
side_col, main_col = st.columns([0.22, 0.78], gap="large")

with side_col:
    render_sidebar(active="Settings")

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
                ⚙️ Settings
            </h1>
            <p style="color: rgba(255,255,255,0.9); margin: 8px 0 0 0; font-size: 14px;">
                Configure language, theme, and target preferences
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    spacer("md")
    
    # Language & Display Settings
    section_header("Language & Display", "Customize language and display preferences", "🌐")
    
    with card_container():
        col1, col2 = st.columns(2)
        
        with col1:
            language = st.selectbox(
                "Display Language",
                ["en", "ar"],
                index=["en", "ar"].index(st.session_state.language),
                format_func=lambda x: "English" if x == "en" else "العربية",
                key="settings_language",
                help="Select the display language for the dashboard"
            )
            
            if language != st.session_state.language:
                st.session_state.language = language
                st.success("✅ Language updated")
        
        with col2:
            theme = st.selectbox(
                "Theme",
                ["dark", "light"],
                index=["dark", "light"].index(st.session_state.theme),
                format_func=lambda x: "🌙 Dark Theme" if x == "dark" else "☀️ Light Theme",
                key="settings_theme",
                help="Select visual theme (currently only dark theme is fully supported)"
            )
            
            if theme != st.session_state.theme:
                st.session_state.theme = theme
                if theme == "light":
                    st.warning("⚠️ Light theme support coming soon. Dark theme will continue to be used.")
    
    spacer("lg")
    
    # Target Configuration
    section_header("Performance Targets", "Set target thresholds for KPIs", "🎯")
    
    with card_container():
        st.markdown("Configure target values for key performance indicators. These targets are used for status calculations.")
        
        spacer("sm")
        
        col1, col2 = st.columns(2)
        
        with col1:
            sustainability_target = st.number_input(
                "Sustainability Index Target",
                min_value=0,
                max_value=100,
                value=st.session_state.sustainability_target,
                step=5,
                help="Target value for overall sustainability index (0-100)",
                key="settings_sustainability_target"
            )
            
            if sustainability_target != st.session_state.sustainability_target:
                st.session_state.sustainability_target = sustainability_target
                st.success(f"✅ Sustainability target updated to {sustainability_target}")
        
        with col2:
            gdp_target = st.number_input(
                "GDP Growth Target (%)",
                min_value=0.0,
                max_value=20.0,
                value=st.session_state.gdp_target,
                step=0.5,
                help="Target annual GDP growth percentage",
                key="settings_gdp_target"
            )
            
            if gdp_target != st.session_state.gdp_target:
                st.session_state.gdp_target = gdp_target
                st.success(f"✅ GDP growth target updated to {gdp_target}%")
    
    spacer("lg")
    
    # Default Period Settings
    section_header("Default Period", "Set default time period for dashboard views", "📅")
    
    with card_container():
        col1, col2 = st.columns(2)
        
        with col1:
            default_year = st.selectbox(
                "Default Year",
                [2024, 2023, 2022, 2021],
                index=[2024, 2023, 2022, 2021].index(st.session_state.year),
                key="settings_year"
            )
            
            if default_year != st.session_state.year:
                st.session_state.year = default_year
                st.success(f"✅ Default year updated to {default_year}")
        
        with col2:
            default_quarter = st.selectbox(
                "Default Quarter",
                [1, 2, 3, 4],
                index=st.session_state.quarter - 1,
                key="settings_quarter"
            )
            
            if default_quarter != st.session_state.quarter:
                st.session_state.quarter = default_quarter
                st.success(f"✅ Default quarter updated to Q{default_quarter}")
    
    spacer("lg")
    
    # About Section
    section_header("About", "System information and version details", "ℹ️")
    
    with card_container():
        st.markdown(f"""
        **Sustainable Economic Development Analytics Hub**  
        Ministry of Economy and Planning
        
        **Version:** 2.0.0 – Dark Theme  
        **Last Updated:** December 2025  
        **Framework:** Streamlit + FastAPI + Plotly
        
        ---
        
        **Features:**
        - Executive dashboard with minister view
        - Comprehensive KPI tracking
        - Trend analysis and forecasting
        - ML-powered anomaly detection
        - AI strategic recommendations
        - Regional performance mapping
        - Data quality monitoring
        
        ---
        
        **Support:**  
        📧 support@ministry.gov.sa  
        📞 +966 XX XXX XXXX
        """)
    
    spacer("lg")
    
    # Reset Settings
    section_header("Reset", "Reset all settings to default values", "🔄")
    
    with card_container():
        st.warning("⚠️ This will reset all preferences to their default values")
        
        if st.button("Reset All Settings", type="secondary"):
            st.session_state.language = "en"
            st.session_state.theme = "dark"
            st.session_state.year = 2024
            st.session_state.quarter = 4
            st.session_state.region = "all"
            st.session_state.sustainability_target = 70
            st.session_state.gdp_target = 5.0
            st.success("✅ All settings have been reset to defaults")
            st.rerun()
