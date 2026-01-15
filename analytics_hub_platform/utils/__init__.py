"""
Utils Package
Sustainable Economic Development Analytics Hub
Eng. Sultan Albuqami

Utility functions for exports, help system, accessibility, and more.
"""

from analytics_hub_platform.utils.accessibility import get_accessibility_config
from analytics_hub_platform.utils.export_excel import generate_excel_workbook
from analytics_hub_platform.utils.export_pdf import generate_pdf_report
from analytics_hub_platform.utils.export_ppt import generate_ppt_presentation
from analytics_hub_platform.utils.help_system import get_help_content, get_tooltip
from analytics_hub_platform.utils.narratives import generate_narrative
from analytics_hub_platform.utils.preferences import get_user_preferences, save_user_preferences
from analytics_hub_platform.utils.validators import (
    validate_filter_params,
    validate_indicator_data,
)
from analytics_hub_platform.utils.wcag_compliance import (
    AccessibleComponentConfig,
    WCAGLevel,
    accessible_card,
    accessible_chart_wrapper,
    accessible_data_table,
    accessible_metric,
    announce,
    format_number_accessible,
    get_accessibility_statement,
    get_keyboard_navigation_js,
    get_rtl_css,
    get_wcag_compliant_css,
    inject_live_region,
    inject_skip_link,
    set_document_direction,
)

from .excel_importer import ExcelCSVImporter
from .synthetic_generator import REGIONS, SyntheticDataGenerator

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
