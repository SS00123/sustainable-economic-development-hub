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
from analytics_hub_platform.ui.page_init import initialize_page
from analytics_hub_platform.app.components import (
    render_sidebar,
    render_page_header,
    section_header,
    spacer,
)
from analytics_hub_platform.app.components.info_panels import render_theme_info_box


# Initialize page (session state, database, theme)
initialize_page()

# Settings-specific defaults
if "sustainability_target" not in st.session_state:
    st.session_state["sustainability_target"] = 70
if "gdp_target" not in st.session_state:
    st.session_state["gdp_target"] = 5.0

# Layout
side_col, main_col = st.columns([0.2, 0.8], gap="large")

with side_col:
    render_sidebar(active="Settings")

with main_col:
    # Header
    render_page_header(
        "Settings",
        "Configure language, theme, and target preferences",
        "⚙️"
    )

    spacer("md")

    # Language & Display Settings
    section_header("Language & Display", "Customize language and display preferences", "🌐")

    with st.container():
        col1, col2 = st.columns(2)

        with col1:
            language = st.selectbox(
                "Display Language",
                ["en", "ar"],
                index=["en", "ar"].index(st.session_state.language),
                format_func=lambda x: "English" if x == "en" else "العربية",
                key="settings_language",
                help="Select the display language for the dashboard",
            )

            if language != st.session_state.language:
                st.session_state.language = language
                st.success("✅ Language updated")

        with col2:
            # Dark theme is the production theme - display as read-only info
            render_theme_info_box(
                theme_name="Dark Theme",
                theme_icon="🌙",
                description="Professional dark theme optimized for executive dashboards",
            )

    spacer("lg")

    # Target Configuration
    section_header("Performance Targets", "Set target thresholds for KPIs", "🎯")

    with st.container():
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
                key="settings_sustainability_target",
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
                key="settings_gdp_target",
            )

            if gdp_target != st.session_state.gdp_target:
                st.session_state.gdp_target = gdp_target
                st.success(f"✅ GDP growth target updated to {gdp_target}%")

    spacer("lg")

    # Default Period Settings
    section_header("Default Period", "Set default time period for dashboard views", "📅")

    with st.container():
        col1, col2 = st.columns(2)

        with col1:
            default_year = st.selectbox(
                "Default Year",
                [2026, 2025, 2024, 2023, 2022, 2021, 2020],
                index=[2026, 2025, 2024, 2023, 2022, 2021, 2020].index(st.session_state.year),
                key="settings_year",
            )

            if default_year != st.session_state.year:
                st.session_state.year = default_year
                st.success(f"✅ Default year updated to {default_year}")

        with col2:
            default_quarter = st.selectbox(
                "Default Quarter",
                [1, 2, 3, 4],
                index=st.session_state.quarter - 1,
                key="settings_quarter",
            )

            if default_quarter != st.session_state.quarter:
                st.session_state.quarter = default_quarter
                st.success(f"✅ Default quarter updated to Q{default_quarter}")

    spacer("lg")

    # About Section
    section_header("About", "System information and version details", "ℹ️")

    with st.container():
        st.markdown("""
        **Sustainable Economic Development Analytics Hub**
        Ministry of Economy and Planning

        **Version:** 2.0.0 – Dark Theme
        **Last Updated:** January 2026
        **Framework:** Streamlit + Plotly

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
        📧 sultan_mutep@hotmail.com
        📞 0553112800
        """)

    spacer("lg")

    # Reset Settings
    section_header("Reset", "Reset all settings to default values", "🔄")

    with st.container():
        st.warning("⚠️ This will reset all preferences to their default values")

        if st.button("Reset All Settings", type="secondary"):
            st.session_state.language = "en"
            st.session_state.theme = "dark"
            st.session_state.year = 2026
            st.session_state.quarter = 4
            st.session_state.region = "all"
            st.session_state.sustainability_target = 70
            st.session_state.gdp_target = 5.0
            st.success("✅ All settings have been reset to defaults")
            st.rerun()
