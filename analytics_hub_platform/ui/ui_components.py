"""
Reusable UI Components
Production-grade card, metric, and chart components for consistent styling
"""

from __future__ import annotations
from analytics_hub_platform.app.components import (
    card_container,
    info_banner,
    initialize_page_session_state,
    metric_card,
    mini_stat,
    page_container,
    render_page_header,
    section_header,
    spacer,
    status_pills,
)
from analytics_hub_platform.app.styles.compat import (
    COLORS,
    RADIUS,
    SHADOWS,
    SPACING,
    TYPOGRAPHY,
    get_gradient,
    get_status_color,
)
from analytics_hub_platform.app.styles.charts import apply_chart_theme, apply_dark_chart_layout


__all__ = [
    "COLORS",
    "SPACING",
    "TYPOGRAPHY",
    "RADIUS",
    "SHADOWS",
    "get_gradient",
    "get_status_color",
    "initialize_page_session_state",
    "render_page_header",
    "page_container",
    "section_header",
    "card_container",
    "metric_card",
    "status_pills",
    "apply_chart_theme",
    "apply_dark_chart_layout",
    "mini_stat",
    "info_banner",
    "spacer",
]
