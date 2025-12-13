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
from analytics_hub_platform.utils.wcag_compliance import (
    get_wcag_compliant_css,
    accessible_card,
    accessible_metric,
    accessible_chart_wrapper,
    accessible_data_table,
    inject_skip_link,
    inject_live_region,
    get_rtl_css,
    set_document_direction,
    get_keyboard_navigation_js,
    announce,
    format_number_accessible,
    get_accessibility_statement,
    WCAGLevel,
    AccessibleComponentConfig,
)
from .synthetic_generator import SyntheticDataGenerator, REGIONS
from .excel_importer import ExcelCSVImporter

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
    "SyntheticDataGenerator",
    "REGIONS",
    "ExcelCSVImporter",
    # WCAG 2.1 AA Compliance
    "get_wcag_compliant_css",
    "accessible_card",
    "accessible_metric",
    "accessible_chart_wrapper",
    "accessible_data_table",
    "inject_skip_link",
    "inject_live_region",
    "get_rtl_css",
    "set_document_direction",
    "get_keyboard_navigation_js",
    "announce",
    "format_number_accessible",
    "get_accessibility_statement",
    "WCAGLevel",
    "AccessibleComponentConfig",
]
