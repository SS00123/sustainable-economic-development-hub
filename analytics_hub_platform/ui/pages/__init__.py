"""
Analytics Hub Platform - UI Pages Module
Sustainable Economic Development Analytics Hub
Eng. Sultan Albuqami

The main dashboard renderer is unified_dashboard.render_unified_dashboard().
Legacy view files (executive_view, director_view, etc.) were removed as dead code.
"""

from analytics_hub_platform.ui.pages.unified_dashboard import render_unified_dashboard

__all__ = [
    "render_unified_dashboard",
]
