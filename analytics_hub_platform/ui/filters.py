"""
Global Filters
Sustainable Economic Development Analytics Hub
Ministry of Economy and Planning

This module provides the global filter bar component used across all pages.
Filters include year, quarter, region, and language selection.
"""

from dataclasses import dataclass

import streamlit as st

from analytics_hub_platform.config.config import get_config
from analytics_hub_platform.infrastructure.repository import get_repository
from analytics_hub_platform.infrastructure.settings import get_settings


@dataclass
class FilterState:
    """Current state of global filters."""

    year: int
    quarter: int
    region: str
    language: str
    role: str
    tenant_id: str


def _initialize_session_state() -> None:
    """Initialize session state with default filter values."""
    config = get_config()
    settings = get_settings()

    if "filter_year" not in st.session_state:
        st.session_state.filter_year = config.default_year

    if "filter_quarter" not in st.session_state:
        st.session_state.filter_quarter = config.default_quarter

    if "filter_region" not in st.session_state:
        st.session_state.filter_region = config.default_region

    if "filter_language" not in st.session_state:
        st.session_state.filter_language = config.default_language

    if "user_role" not in st.session_state:
        st.session_state.user_role = "director"

    if "tenant_id" not in st.session_state:
        st.session_state.tenant_id = settings.default_tenant_id


def get_filter_state() -> FilterState:
    """
    Get the current filter state from session.

    Returns:
        FilterState with current selections
    """
    _initialize_session_state()

    return FilterState(
        year=st.session_state.filter_year,
        quarter=st.session_state.filter_quarter,
        region=st.session_state.filter_region,
        language=st.session_state.filter_language,
        role=st.session_state.user_role,
        tenant_id=st.session_state.tenant_id,
    )


def render_global_filters(
    show_year: bool = True,
    show_quarter: bool = True,
    show_region: bool = True,
    show_language: bool = True,
    show_role: bool = True,
    compact: bool = False,
) -> FilterState:
    """
    Render the global filter bar in the sidebar.

    Args:
        show_year: Whether to show year filter
        show_quarter: Whether to show quarter filter
        show_region: Whether to show region filter
        show_language: Whether to show language filter
        show_role: Whether to show role selector (for demo purposes)
        compact: Whether to use compact layout

    Returns:
        FilterState with current selections
    """
    _initialize_session_state()
    config = get_config()
    settings = get_settings()

    # Try to get available periods and regions from database
    try:
        repo = get_repository()
        available_periods = repo.get_available_periods(settings.default_tenant_id)
        available_regions = repo.get_available_regions(settings.default_tenant_id)
    except Exception:
        # Fallback to config values if database not available
        available_periods = [
            {"year": y, "quarter": q, "label": f"Q{q} {y}"}
            for y in config.available_years
            for q in [1, 2, 3, 4]
        ]
        available_regions = config.regions

    # Extract unique years
    years = sorted({p["year"] for p in available_periods}, reverse=True)
    if not years:
        years = config.available_years

    # Note: Renders directly without st.sidebar context since caller handles that
    st.markdown("### 🎯 Filters")
    st.markdown("---")

    # Role selector (for demo - simulates different user personas)
    if show_role:
        roles = {
            "minister": "👔 Minister / Executive",
            "director": "📊 Director / Head of Analytics",
            "analyst": "🔬 Data Analyst",
            "admin": "⚙️ Administrator",
        }

        # Normalize user_role to lowercase for matching
        current_role = (
            st.session_state.user_role.lower() if st.session_state.user_role else "director"
        )
        if current_role not in roles:
            current_role = "director"

        selected_role = st.selectbox(
            "View As (Demo)",
            options=list(roles.keys()),
            format_func=lambda x: roles[x],
            index=list(roles.keys()).index(current_role),
            key="role_selector",
            help="Select a role to view the dashboard from that persona's perspective",
        )
        st.session_state.user_role = selected_role
        st.markdown("---")

    # Time period filters
    if show_year or show_quarter:
        st.markdown("**📅 Time Period**")

        col1, col2 = st.columns(2) if not compact else (st, st)

        if show_year:
            with col1 if not compact else st:
                selected_year = st.selectbox(
                    "Year",
                    options=years,
                    index=years.index(st.session_state.filter_year)
                    if st.session_state.filter_year in years
                    else 0,
                    key="year_selector",
                )
                st.session_state.filter_year = selected_year

        if show_quarter:
            with col2 if not compact else st:
                selected_quarter = st.selectbox(
                    "Quarter",
                    options=[1, 2, 3, 4],
                    format_func=lambda x: f"Q{x}",
                    index=st.session_state.filter_quarter - 1,
                    key="quarter_selector",
                )
                st.session_state.filter_quarter = selected_quarter

    # Region filter
    if show_region:
        st.markdown("**🗺️ Region**")

        region_options = ["all"] + available_regions
        region_labels = {"all": "🌍 All Regions"}
        region_labels.update({r: r for r in available_regions})

        current_region = st.session_state.filter_region
        if current_region not in region_options:
            current_region = "all"

        selected_region = st.selectbox(
            "Region",
            options=region_options,
            format_func=lambda x: region_labels.get(x, x),
            index=region_options.index(current_region),
            key="region_selector",
        )
        st.session_state.filter_region = selected_region

    # Language filter
    if show_language:
        st.markdown("**🌐 Language**")

        languages = {
            "en": "🇬🇧 English",
            "ar": "🇸🇦 العربية",
        }

        selected_language = st.radio(
            "Display Language",
            options=list(languages.keys()),
            format_func=lambda x: languages[x],
            index=list(languages.keys()).index(st.session_state.filter_language),
            key="language_selector",
            horizontal=True,
        )
        st.session_state.filter_language = selected_language

    st.markdown("---")

    # Show current selection summary
    st.markdown("**Current Selection:**")
    st.markdown(f"""
    - **Period:** Q{st.session_state.filter_quarter} {st.session_state.filter_year}
    - **Region:** {st.session_state.filter_region.title() if st.session_state.filter_region != "all" else "All Regions"}
    - **Language:** {"English" if st.session_state.filter_language == "en" else "Arabic"}
    """)

    return get_filter_state()


def render_period_comparison_filters() -> tuple:
    """
    Render filters for period comparison views.

    Returns:
        Tuple of (current_period, comparison_period) as (year, quarter) tuples
    """
    _initialize_session_state()

    st.markdown("**📊 Period Comparison**")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("Current Period")
        current_year = st.session_state.filter_year
        current_quarter = st.session_state.filter_quarter
        st.info(f"Q{current_quarter} {current_year}")

    with col2:
        st.markdown("Compare To")
        compare_options = [
            ("prev_quarter", "Previous Quarter"),
            ("prev_year", "Same Quarter Last Year"),
            ("custom", "Custom Period"),
        ]

        compare_type = st.selectbox(
            "Comparison Type",
            options=[c[0] for c in compare_options],
            format_func=lambda x: dict(compare_options)[x],
            label_visibility="collapsed",
        )

        if compare_type == "prev_quarter":
            comp_quarter = current_quarter - 1
            comp_year = current_year
            if comp_quarter == 0:
                comp_quarter = 4
                comp_year -= 1
        elif compare_type == "prev_year":
            comp_quarter = current_quarter
            comp_year = current_year - 1
        else:
            comp_year = st.number_input(
                "Year", value=current_year - 1, min_value=2020, max_value=2024
            )
            comp_quarter = st.selectbox(
                "Quarter", options=[1, 2, 3, 4], format_func=lambda x: f"Q{x}"
            )

        st.info(f"Q{comp_quarter} {comp_year}")

    return (current_year, current_quarter), (comp_year, comp_quarter)
