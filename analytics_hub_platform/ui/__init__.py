"""
Analytics Hub Platform - UI Module
Sustainable Economic Development Analytics Hub
Ministry of Economy and Planning

This module contains Streamlit UI components and pages.
"""

from analytics_hub_platform.ui.layout import (
    render_header,
    render_footer,
    render_kpi_card,
    render_section_header,
    render_status_badge,
    inject_custom_css,
)
from analytics_hub_platform.ui.filters import (
    render_global_filters,
    get_filter_state,
    FilterState,
)
# Dark theme components
from analytics_hub_platform.ui.dark_theme import (
    get_dark_theme,
    get_dark_css,
    DarkColorPalette,
    DarkTheme,
)
from analytics_hub_platform.ui.dark_components import (
    inject_dark_theme,
    render_sidebar,
    render_header as render_dark_header,
    card_open,
    card_close,
    render_kpi_card as render_dark_kpi_card,
    render_mini_metric,
    apply_dark_chart_layout,
    render_line_chart_card,
    render_horizontal_bar_card,
    render_donut_chart_card,
    render_grouped_bar_card,
    render_section_title,
    render_status_overview,
)

__all__ = [
    # Original layout exports
    "render_header",
    "render_footer",
    "render_kpi_card",
    "render_section_header",
    "render_status_badge",
    "inject_custom_css",
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
