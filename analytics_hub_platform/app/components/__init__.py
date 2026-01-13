"""Reusable Streamlit UI components.

This package is the forward-looking home for UI components. The legacy
`analytics_hub_platform.ui.ui_components` module re-exports these APIs for
backward compatibility.
"""

from .layout import initialize_page_session_state, page_container, spacer
from .headers import render_page_header, section_header
from .cards import (
    card_container,
    info_banner,
    metric_card,
    mini_stat,
    status_pills,
)
from .chart_card import (
    chart_card_open,
    chart_card_close,
    render_chart_card,
)
from .alert_card import (
    render_alert_card,
    render_alert_summary,
)
from .filter_bar import (
    render_filter_bar,
    render_period_selector,
)
from .empty_states import (
    render_empty_state,
    render_loading_state,
    render_error_state,
)

__all__ = [
    # Layout
    "initialize_page_session_state",
    "page_container",
    "spacer",
    # Headers
    "render_page_header",
    "section_header",
    # Cards
    "card_container",
    "info_banner",
    "metric_card",
    "mini_stat",
    "status_pills",
    # Chart cards
    "chart_card_open",
    "chart_card_close",
    "render_chart_card",
    # Alert cards
    "render_alert_card",
    "render_alert_summary",
    # Filter bar
    "render_filter_bar",
    "render_period_selector",
    # Empty states
    "render_empty_state",
    "render_loading_state",
    "render_error_state",
]
