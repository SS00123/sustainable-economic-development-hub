"""
Analytics Hub Platform - UI Module
Sustainable Economic Development Analytics Hub
Eng. Sultan Albuqami

This module contains Streamlit UI components and pages.
Callers should prefer importing from `analytics_hub_platform.app.components`.
"""

from analytics_hub_platform.app.components import (
    card_close,
    card_open,
    inject_dark_theme,
    render_donut_chart_card,
    render_grouped_bar_card,
    render_horizontal_bar_card,
    render_line_chart_card,
    render_header as render_dark_header,
    render_kpi_card as render_dark_kpi_card,
    render_mini_metric,
    render_section_title,
    render_sidebar,
    render_status_overview,
)

from analytics_hub_platform.ui.ui_components import apply_dark_chart_layout

# Dark theme components
from analytics_hub_platform.ui.theme import (
    DarkColorPalette,
    DarkTheme,
    get_dark_css,
    get_dark_theme,
)
from analytics_hub_platform.ui.filters import (
    FilterState,
    get_filter_state,
    render_global_filters,
)

__all__ = [
    # Filter components
    "render_global_filters",
    "get_filter_state",
    "FilterState",
    # Dark theme exports
    "get_dark_theme",
    "get_dark_css",
    "DarkColorPalette",
    "DarkTheme",
    "inject_dark_theme",
    "render_sidebar",
    "render_dark_header",
    "card_open",
    "card_close",
    "render_dark_kpi_card",
    "render_mini_metric",
    "apply_dark_chart_layout",
    "render_line_chart_card",
    "render_horizontal_bar_card",
    "render_donut_chart_card",
    "render_grouped_bar_card",
    "render_section_title",
    "render_status_overview",
]
