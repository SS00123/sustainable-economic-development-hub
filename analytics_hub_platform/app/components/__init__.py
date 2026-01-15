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
from .theme import inject_dark_theme
from .chart_cards import (
    render_donut_chart_card,
    render_grouped_bar_card,
    render_horizontal_bar_card,
    render_line_chart_card,
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
from .sidebar import render_sidebar
from .kpi_svg import (
    create_alert_badge,
    create_progress_ring,
    create_sparkline_svg,
)
# Canonical imports from new modules (no longer via legacy_dark)
from .section import (
    render_section_title,
    render_status_overview,
)
from .card_wrappers import (
    card_open,
    card_close,
)
from .kpi_renderers import (
    render_kpi_card,
    render_enhanced_kpi_card,
    render_mini_metric,
)
from .header_components import (
    render_header,
    render_sticky_header,
)
from .chart_helpers import (
    add_target_line_to_chart,
    render_yoy_comparison,
)
# Trust signals component
from .trust_signals import (
    render_data_freshness,
    render_data_source,
    render_confidence_badge,
    render_quality_tier,
    render_trust_bar,
)
# New extracted chart components (A2 compliance)
from .trend_charts import (
    render_trend_line_chart,
    render_multi_series_chart,
)
from .anomaly_display import (
    render_anomaly_card,
    render_anomaly_list,
    render_all_clear,
)
from .regional_charts import (
    render_regional_bar_chart,
    render_regional_stats_panel,
    render_regional_comparison,
)
from .gauge_charts import (
    render_sustainability_gauge,
    render_kpi_gauge,
    render_status_badge,
)
from .forecast_charts import (
    render_forecast_chart,
    render_forecast_details,
    render_forecast_section,
)
from .info_panels import (
    render_theme_info_box,
    render_config_display,
    render_gradient_info_box,
    render_stat_card,
)
# Dashboard quick actions and enhancements
from .dashboard_actions import (
    render_quick_actions_bar,
    render_smart_alerts,
    render_comparison_panel,
    render_data_freshness_badge,
    render_kpi_drill_down,
    render_theme_toggle,
    render_bookmark_share_button,
    render_mobile_view_toggle,
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
    # Navigation
    "render_sidebar",
    # Trust signals
    "render_data_freshness",
    "render_data_source",
    "render_confidence_badge",
    "render_quality_tier",
    "render_trust_bar",
    # Trend charts (extracted)
    "render_trend_line_chart",
    "render_multi_series_chart",
    # Anomaly display (extracted)
    "render_anomaly_card",
    "render_anomaly_list",
    "render_all_clear",
    # Regional charts (extracted)
    "render_regional_bar_chart",
    "render_regional_stats_panel",
    "render_regional_comparison",
    # Gauge charts (extracted)
    "render_sustainability_gauge",
    "render_kpi_gauge",
    "render_status_badge",
    # Forecast charts (extracted)
    "render_forecast_chart",
    "render_forecast_details",
    "render_forecast_section",
    # Info panels (extracted)
    "render_theme_info_box",
    "render_config_display",
    "render_gradient_info_box",
    "render_stat_card",
    # Dashboard quick actions
    "render_quick_actions_bar",
    "render_smart_alerts",
    "render_comparison_panel",
    "render_data_freshness_badge",
    "render_kpi_drill_down",
    "render_theme_toggle",
    "render_bookmark_share_button",
    "render_mobile_view_toggle",
    # Legacy dark components (compat)
    "add_target_line_to_chart",
    "card_close",
    "card_open",
    "create_alert_badge",
    "create_progress_ring",
    "create_sparkline_svg",
    "inject_dark_theme",
    "render_donut_chart_card",
    "render_grouped_bar_card",
    "render_horizontal_bar_card",
    "render_line_chart_card",
    "render_kpi_card",
    "render_enhanced_kpi_card",
    "render_header",
    "render_mini_metric",
    "render_section_title",
    "render_status_overview",
    "render_sticky_header",
    "render_yoy_comparison",
]
