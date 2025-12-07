"""
Utils Package
Sustainable Economic Development Analytics Hub
Ministry of Economy and Planning

Utility functions for exports, help system, accessibility, and more.
"""

from analytics_hub_platform.utils.export_pdf import generate_pdf_report
from analytics_hub_platform.utils.export_ppt import generate_ppt_presentation
from analytics_hub_platform.utils.export_excel import generate_excel_workbook
from analytics_hub_platform.utils.narratives import generate_narrative
from analytics_hub_platform.utils.validators import (
    validate_indicator_data,
    validate_filter_params,
)
from analytics_hub_platform.utils.help_system import get_help_content, get_tooltip
from analytics_hub_platform.utils.accessibility import get_accessibility_config
from analytics_hub_platform.utils.preferences import get_user_preferences, save_user_preferences

__all__ = [
    "generate_pdf_report",
    "generate_ppt_presentation",
    "generate_excel_workbook",
    "generate_narrative",
    "validate_indicator_data",
    "validate_filter_params",
    "get_help_content",
    "get_tooltip",
    "get_accessibility_config",
    "get_user_preferences",
    "save_user_preferences",
]
