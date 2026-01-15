"""
Design System & Governance Page.

This page serves as the living source of truth for the Analytics Hub design system.
It reflects the token contract and component library implementation.
"""

import streamlit as st
import pandas as pd
import dataclasses
from typing import Any, Callable, TYPE_CHECKING

# Type stubs for Pylance - actual imports happen below
if TYPE_CHECKING:
    pass

# Initialize token variables with None (will be set in try block)
colors: Any = None
typography: Any = None
spacing: Any = None
radius: Any = None
shadows: Any = None
transitions: Any = None
render_color_swatch: Callable[..., Any] | None = None
render_spacing_bar: Callable[..., Any] | None = None
render_radius_box: Callable[..., Any] | None = None
render_shadow_card: Callable[..., Any] | None = None
render_typography_sample: Callable[..., Any] | None = None

# Safe Imports for Tokens
try:
    from analytics_hub_platform.app.styles.tokens import (
        colors as _colors,
        typography as _typography,
        spacing as _spacing,
        radius as _radius,
        shadows as _shadows,
        transitions as _transitions,
    )
    # Helper module for rendering tokens visually
    from analytics_hub_platform.app.components.design_system_helpers import (
        render_color_swatch as _render_color_swatch,
        render_spacing_bar as _render_spacing_bar,
        render_radius_box as _render_radius_box,
        render_shadow_card as _render_shadow_card,
        render_typography_sample as _render_typography_sample,
    )
    # Assign to module-level variables
    colors = _colors
    typography = _typography
    spacing = _spacing
    radius = _radius
    shadows = _shadows
    transitions = _transitions
    render_color_swatch = _render_color_swatch
    render_spacing_bar = _render_spacing_bar
    render_radius_box = _render_radius_box
    render_shadow_card = _render_shadow_card
    render_typography_sample = _render_typography_sample
    TOKENS_AVAILABLE = True
except ImportError as e:
    st.error(f"Critical Token Import Error: {e}")
    TOKENS_AVAILABLE = False

# Component Library Imports (with fallbacks)
# Wrapped in try/except to prevent page crash if components are missing or broken
render_kpi_card: Callable[..., Any] | None = None
render_filter_bar: Callable[..., Any] | None = None
render_data_freshness: Callable[..., Any] | None = None
render_confidence_badge: Callable[..., Any] | None = None
render_trust_bar: Callable[..., Any] | None = None
render_alert_card: Callable[..., Any] | None = None
section_header: Callable[..., Any] | None = None
render_empty_state: Callable[..., Any] | None = None
render_loading_state: Callable[..., Any] | None = None
render_error_state: Callable[..., Any] | None = None
render_line_chart_card: Callable[..., Any] | None = None
render_donut_chart_card: Callable[..., Any] | None = None


try:
    from analytics_hub_platform.app.components.kpi_renderers import render_kpi_card
    from analytics_hub_platform.app.components.filter_bar import render_filter_bar
    from analytics_hub_platform.app.components.trust_signals import (
        render_data_freshness,
        render_confidence_badge,
        render_trust_bar
    )
    from analytics_hub_platform.app.components.alert_card import render_alert_card
    from analytics_hub_platform.app.components.headers import section_header
    from analytics_hub_platform.app.components.empty_states import (
        render_empty_state,
        render_loading_state,
        render_error_state
    )
    from analytics_hub_platform.app.components.chart_cards import (
        render_line_chart_card,
        render_donut_chart_card,
    )
    COMPONENTS_AVAILABLE = True
    IMPORT_ERROR = ""
except ImportError as e:
    COMPONENTS_AVAILABLE = False
    IMPORT_ERROR = str(e)


def main():
    st.set_page_config(
        page_title="Design System",
        page_icon="🎨",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.title("🎨 Design System & Governance")
    st.markdown(
        """
        This page serves as the verified reference for the Analytics Hub design system.
        It renders the actual code tokens and components used in the application.
        """
    )

    if not TOKENS_AVAILABLE:
        st.stop()

    # Developer UX: Top-level selectbox navigation
    current_view = st.selectbox(
        "Select View:",
        ["Foundations", "Components", "Governance"],
        index=0,
        key="ds_view_selector"
    )

    st.divider()

    # ==============================================================================
    # VIEW: FOUNDATIONS (Tokens)
    # ==============================================================================
    if current_view == "Foundations":
        st.header("Design Tokens")
        st.info("Values are read directly from `app/styles/tokens.py`.")

        # --- COLORS ---
        with st.expander("Colors", expanded=True):
            st.caption("Backgrounds, Text, Status, and Domain colors.")

            # Iterate through all color attributes
            cols = st.columns(2)
            assert colors is not None  # Guarded by TOKENS_AVAILABLE check above
            color_items = [(k, v) for k, v in dataclasses.asdict(colors).items() if isinstance(v, str)]

            # Split into reasonable groups based on prefix
            groups = {
                "Backgrounds (bg_*)": [x for x in color_items if x[0].startswith("bg_")],
                "Text (text_*)": [x for x in color_items if x[0].startswith("text_")],
                "Status (status_*)": [x for x in color_items if x[0].startswith("status_")],
                "Accent (accent_*)": [x for x in color_items if x[0].startswith("accent_")],
                "Domain (domain_*)": [x for x in color_items if x[0].startswith("domain_")],
                "Other": [x for x in color_items if not any(x[0].startswith(p) for p in ["bg_", "text_", "status_", "accent_", "domain_"])]
            }

            col_idx = 0
            for group_name, items in groups.items():
                if not items:
                    continue
                with cols[col_idx % 2]:
                    st.subheader(group_name)
                    for token_name, token_value in items:
                        if render_color_swatch:
                            render_color_swatch(token_name, token_value)
                col_idx += 1

            st.subheader("Chart Palette")
            st.write("Sequential colors for multi-series charts.")
            pal_cols = st.columns(5)
            for i, color_hex in enumerate(colors.chart_palette):
                with pal_cols[i % 5]:
                    if render_color_swatch:
                        render_color_swatch(f"chart_{i}", color_hex)

        # --- TYPOGRAPHY ---
        with st.expander("Typography", expanded=False):
            assert typography is not None
            st.caption(f"Font Families: {typography.family_base}")

            t_cols = st.columns(2)
            with t_cols[0]:
                st.subheader("Headings")
                if render_typography_sample:
                    render_typography_sample("hero", typography.hero, str(typography.weight_extrabold))
                    render_typography_sample("h1", typography.h1, str(typography.weight_bold))
                    render_typography_sample("h2", typography.h2, str(typography.weight_semibold))
                    render_typography_sample("h3", typography.h3, str(typography.weight_medium))
                    render_typography_sample("h4", typography.h4, str(typography.weight_medium))

            with t_cols[1]:
                st.subheader("Body")
                if render_typography_sample:
                    render_typography_sample("body", typography.body, str(typography.weight_regular))
                    render_typography_sample("caption", typography.caption, str(typography.weight_regular))
                    render_typography_sample("small", typography.small, str(typography.weight_regular))
                    render_typography_sample("tiny", typography.tiny, str(typography.weight_regular))

        # --- SPACING ---
        with st.expander("Spacing", expanded=False):
            st.caption("8pt Grid System")
            cols = st.columns(2)
            assert spacing is not None
            spacing_items = list(dataclasses.asdict(spacing).items())
            half = len(spacing_items) // 2

            with cols[0]:
                for i, (k, v) in enumerate(spacing_items):
                    if i <= half and render_spacing_bar:
                        render_spacing_bar(k, v)
            with cols[1]:
                for i, (k, v) in enumerate(spacing_items):
                    if i > half and render_spacing_bar:
                        render_spacing_bar(k, v)

        # --- RADIUS ---
        with st.expander("Radius", expanded=False):
            st.write("Border Radius tokens using `border-radius`")
            cols = st.columns(6)
            assert radius is not None
            for i, (k, v) in enumerate(dataclasses.asdict(radius).items()):
                with cols[i % 6]:
                    if render_radius_box:
                        render_radius_box(k, v)

        # --- SHADOWS ---
        with st.expander("Shadows", expanded=False):
            st.write("Shadow and Glow effects")
            assert shadows is not None
            shadow_items = dataclasses.asdict(shadows).items()
            for k, v in shadow_items:
                if render_shadow_card:
                    render_shadow_card(k, v)

    # ==============================================================================
    # VIEW: COMPONENTS (Catalog)
    # ==============================================================================
    elif current_view == "Components":
        st.header("Component Catalog")

        if not COMPONENTS_AVAILABLE:
            st.error(f"⚠️ Components could not be loaded. Error: {IMPORT_ERROR}")
        else:
            # --- KPI CARDS ---
            with st.expander("KPI Cards", expanded=True):
                st.markdown("`render_kpi_card`")
                cols = st.columns(3)
                with cols[0]:
                    if render_kpi_card:
                        render_kpi_card(
                            title="Total Revenue",
                            value=12500000,
                            delta=12.5,
                            unit=" SAR",
                            subtitle="vs last year"
                        )
                with cols[1]:
                    if render_kpi_card:
                        render_kpi_card(
                            title="Active Projects",
                            value=42,
                            delta=-2.1,
                            unit="",
                            subtitle="vs last month",
                            accent_color="red"
                        )
                with cols[2]:
                    if render_kpi_card:
                        render_kpi_card(
                            title="Efficiency Score",
                            value=98.5,
                            unit="%",
                            subtitle="Excellent",
                            accent_color="green"
                        )

            # --- FILTER BAR ---
            with st.expander("Filter Bar"):
                st.markdown("`render_filter_bar`")
                if render_filter_bar:
                    render_filter_bar(
                        years=[2024, 2025, 2026],
                        show_year=True,
                        show_quarter=True,
                        show_region=True,
                        key_prefix="demo_filter"
                    )

            # --- CHART CARDS ---
            with st.expander("Chart Cards"):
                st.markdown("`render_line_chart_card`, `render_donut_chart_card`")
                # Demo Data using numpy/pandas
                import numpy as np
                sample_df = pd.DataFrame({
                    "period": pd.date_range("2025-01", periods=12, freq="M"),
                    "value": np.cumsum(np.random.randn(12) * 10 + 50)
                })
                cols = st.columns(2)
                with cols[0]:
                    if render_line_chart_card:
                        render_line_chart_card(
                            df=sample_df,
                            x_col="period",
                            y_col="value",
                            title="Monthly Trend",
                            subtitle="Sample time series"
                        )
                with cols[1]:
                    if render_donut_chart_card:
                        render_donut_chart_card(
                            labels=["Economic", "Labor", "Social", "Environmental"],
                            values=[35, 25, 22, 18],
                            title="Sector Distribution",
                            subtitle="By pillar"
                        )

            # --- TRUST SIGNALS ---
            with st.expander("Trust Signals"):
                st.markdown("`render_trust_bar`, `render_data_freshness`, `render_confidence_badge`")
                if render_trust_bar:
                    render_trust_bar(
                        source="National Data Center",
                        last_updated="2026-01-14 10:00:00",
                        confidence=0.98
                    )
                st.divider()
                c1, c2, c3 = st.columns(3)
                with c1:
                    if render_data_freshness:
                        render_data_freshness(show_live_dot=True)
                with c2:
                    if render_confidence_badge:
                        render_confidence_badge(0.95)
                with c3:
                    if render_confidence_badge:
                        render_confidence_badge(0.65)

            # --- ALERTS ---
            with st.expander("Alerts & Notifications"):
                st.markdown("`render_alert_card`")
                if render_alert_card:
                    render_alert_card(
                        title="Data Sync Delay",
                        description="The economic indicators feed is delayed by 2 hours.",
                        severity="warning"
                    )
                    render_alert_card(
                        title="System Operational",
                        description="All systems are running normally.",
                        severity="info"
                    )
                    render_alert_card(
                        title="Critical Threshold",
                        description="Unemployment KPI has breached the lower threshold.",
                        severity="critical"
                    )

            # --- SECTION HEADERS ---
            with st.expander("Headers"):
                st.markdown("`section_header`")
                if section_header:
                    section_header(
                        title="Strategic Overview",
                        subtitle="High-level performance metrics for the current quarter",
                        icon="📊"
                    )

            # --- EMPTY STATES ---
            with st.expander("State Patterns (Empty/Loading/Error)"):
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.caption("Empty State")
                    if render_empty_state:
                        render_empty_state("No projects found", "Adjust filters to see results")
                with c2:
                    st.caption("Loading State")
                    if render_loading_state:
                        render_loading_state("Fetching live data...")
                with c3:
                    st.caption("Error State")
                    if render_error_state:
                        render_error_state("Connection Failed", "Unable to reach data warehouse")


    # ==============================================================================
    # VIEW: GOVERNANCE (Rules)
    # ==============================================================================
    elif current_view == "Governance":
        st.header("Governance Rules")

        st.markdown(
            """
            ### 1. Source of Truth
            *   **Tokens**: All styles (colors, spacing, typography) MUST come from `app/styles/tokens.py`.
            *   **Components**: UI patterns MUST be imported from `app/components/`.
            *   **Prohibited**: Hardcoded hex values, inline CSS strings, or ad-hoc `st.markdown` styling.

            ### 2. Contribution Process
            1.  **Check Existing**: Before building, check this catalog.
            2.  **Extend Tokens**: If a new color/spacing is needed, add it to `tokens.py` first (requires approval).
            3.  **Build Component**: Create a reusable function in `app/components/`.
            4.  **Register**: Add the new component to this Design System page.

            ### 3. Do's and Don'ts
            | Do ✅ | Don't ❌ |
            | :--- | :--- |
            | Use `section_header` for headers | Use `st.header("Title")` directly |
            | Use `colors.status_green` | Use `"#00FF00"` |
            | Use `render_kpi_card` | Create a custom container with stats |
            | Use `render_error_state` for errors | Use `st.error` raw (unless simple validation) |

            ### 4. Component Standards
            *   All components must support a `key` argument if they have interactivity.
            *   All components must use `tokens.spacing` for padding/margins.
            *   All components must use Python type hints.
            """
        )

    # ==============================================================================
    # FOOTER DIAGNOSTICS
    # ==============================================================================
    st.divider()
    diag_cols = st.columns(4)
    with diag_cols[0]:
        color_count = len(dataclasses.asdict(colors)) if colors else 0
        st.caption(f"Color Tokens: {color_count}")
    with diag_cols[1]:
        typo_count = len(dataclasses.asdict(typography)) if typography else 0
        st.caption(f"Typo Tokens: {typo_count}")
    with diag_cols[2]:
        spacing_count = len(dataclasses.asdict(spacing)) if spacing else 0
        st.caption(f"Spacing Tokens: {spacing_count}")
    with diag_cols[3]:
        st.caption("v1.0.0-foundation")

if __name__ == "__main__":
    main()
