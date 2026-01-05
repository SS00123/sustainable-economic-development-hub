"""
Analytics Hub Platform - UI Module
Sustainable Economic Development Analytics Hub
Ministry of Economy and Planning

This module contains Streamlit UI components and pages.
"""

from analytics_hub_platform.ui.dark_components import (
    apply_dark_chart_layout,
    card_close,
    card_open,
    inject_dark_theme,
    render_donut_chart_card,
    render_grouped_bar_card,
    render_horizontal_bar_card,
    render_line_chart_card,
    render_mini_metric,
    render_section_title,
    render_sidebar,
    render_status_overview,
)
from analytics_hub_platform.ui.dark_components import (
    render_header as render_dark_header,
)
from analytics_hub_platform.ui.dark_components import (
    render_kpi_card as render_dark_kpi_card,
)

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
from analytics_hub_platform.ui.layout import (
    inject_custom_css,
    render_footer,
    render_header,
    render_kpi_card,
    render_section_header,
    render_status_badge,
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
