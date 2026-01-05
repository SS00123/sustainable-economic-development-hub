"""
Dashboard Section Components
Modular sections extracted from the unified dashboard for maintainability.

Each section handles a specific part of the dashboard:
- header: Page header with title, live indicator, period info
- hero: Sustainability gauge and hero KPI cards
- pillars: Economic, Labor, Environmental pillar sections
- insights: Key insights, YoY comparison, regional analysis
"""

from analytics_hub_platform.ui.sections.header import render_page_header
from analytics_hub_platform.ui.sections.hero import (
    render_hero_kpi_cards,
    render_hero_sustainability_gauge,
)
from analytics_hub_platform.ui.sections.pillars import (
    render_pillar_section_economic,
    render_pillar_section_environmental,
    render_pillar_section_labor,
)
from analytics_hub_platform.ui.sections.insights import (
    render_key_insights_section,
    render_regional_comparison_section,
    render_yoy_comparison_section,
)

__all__ = [
    "render_page_header",
    "render_hero_sustainability_gauge",
    "render_hero_kpi_cards",
    "render_pillar_section_economic",
    "render_pillar_section_labor",
    "render_pillar_section_environmental",
    "render_key_insights_section",
    "render_regional_comparison_section",
    "render_yoy_comparison_section",
]
