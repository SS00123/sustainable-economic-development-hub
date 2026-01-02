"""
Deprecated: Excel/CSV Importer
This module has been consolidated.

Please use: analytics_hub_platform.utils.excel_importer instead
"""

import warnings

from analytics_hub_platform.utils.excel_importer import ExcelCSVImporter

warnings.warn(
    "data.excel_importer is deprecated. Use analytics_hub_platform.utils.excel_importer instead.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = ["ExcelCSVImporter"]
