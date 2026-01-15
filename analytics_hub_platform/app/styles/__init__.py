"""
Styling helpers for the application layer.

This package provides the design token system for the Analytics Hub.

Canonical Imports:
    from analytics_hub_platform.app.styles import colors, typography, spacing

Legacy Imports (deprecated, prefer tokens):
    from analytics_hub_platform.app.styles import COLORS, SPACING
"""

# New canonical token system
from .tokens import (
    colors,
    typography,
    spacing,
    radius,
    shadows,
    transitions,
    get_status_color,
    get_status_bg,
    get_domain_color,
    get_gradient,
    hex_to_rgba,
    get_chart_layout_config,
)

# Legacy compat layer (deprecated - for backward compatibility)
from .compat import COLORS, RADIUS, SHADOWS, SPACING, TYPOGRAPHY

# Chart styling
from .charts import apply_chart_theme, apply_dark_chart_layout

__all__ = [
    # === Canonical Token API ===
    "colors",
    "typography",
    "spacing",
    "radius",
    "shadows",
    "transitions",
    "get_status_color",
    "get_status_bg",
    "get_domain_color",
    "get_gradient",
    "hex_to_rgba",
    "get_chart_layout_config",
    # === Legacy Compat (deprecated) ===
    "COLORS",
    "RADIUS",
    "SHADOWS",
    "SPACING",
    "TYPOGRAPHY",
    # === Chart Helpers ===
    "apply_chart_theme",
    "apply_dark_chart_layout",
]
