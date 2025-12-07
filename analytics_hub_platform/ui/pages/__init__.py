"""
Analytics Hub Platform - UI Pages Module
Sustainable Economic Development Analytics Hub
Ministry of Economy and Planning
"""

from analytics_hub_platform.ui.pages.executive_view import render_executive_view
from analytics_hub_platform.ui.pages.director_view import render_director_view
from analytics_hub_platform.ui.pages.analyst_view import render_analyst_view
from analytics_hub_platform.ui.pages.sustainability_trends import render_sustainability_trends
from analytics_hub_platform.ui.pages.data_quality_view import render_data_quality_view
from analytics_hub_platform.ui.pages.admin_console import render_admin_console

__all__ = [
    "render_executive_view",
    "render_director_view",
    "render_analyst_view",
    "render_sustainability_trends",
    "render_data_quality_view",
    "render_admin_console",
]
