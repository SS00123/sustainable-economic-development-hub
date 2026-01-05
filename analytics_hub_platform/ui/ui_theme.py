"""
UI Theme Constants
Centralized color palette, spacing, and design tokens for consistent styling

DEPRECATED: This module is deprecated and will be removed in a future version.
Please use `analytics_hub_platform.ui.theme` instead.
"""

import warnings
from dataclasses import dataclass

warnings.warn(
    "analytics_hub_platform.ui.ui_theme is deprecated. Use analytics_hub_platform.ui.theme instead.",
    DeprecationWarning,
    stacklevel=2,
)


@dataclass
class ColorPalette:
    """Dark 3D theme color palette"""

    # Primary brand colors
    purple: str = "#a855f7"  # Primary accent
    cyan: str = "#22d3ee"  # Secondary accent
    pink: str = "#ec4899"  # Tertiary accent

    # Background colors
    bg_primary: str = "#0f1629"
    bg_secondary: str = "#1a1f3a"
    bg_card: str = "#1e2340"
    bg_card_hover: str = "#252a4a"

    # Text colors
    text_primary: str = "#f1f5f9"
    text_secondary: str = "#e2e8f0"
    text_muted: str = "#94a3b8"
    text_disabled: str = "#64748b"

    # Status colors
    status_green: str = "#10b981"
    status_amber: str = "#f59e0b"
    status_red: str = "#ef4444"

    # Border and divider colors
    border: str = "#2d3555"
    border_light: str = "rgba(255,255,255,0.08)"
    divider: str = "rgba(255,255,255,0.06)"

    # Gradient colors
    gradient_start: str = "#a855f7"
    gradient_end: str = "#22d3ee"

    # Chart colors
    chart_purple: str = "#a855f7"
    chart_cyan: str = "#22d3ee"
    chart_pink: str = "#ec4899"
    chart_green: str = "#4ade80"
    chart_orange: str = "#fb923c"
    chart_blue: str = "#60a5fa"
    chart_yellow: str = "#fbbf24"
    chart_indigo: str = "#818cf8"


@dataclass
class Spacing:
    """Consistent spacing units"""

    xs: str = "4px"
    sm: str = "8px"
    md: str = "16px"
    lg: str = "24px"
    xl: str = "32px"
    xxl: str = "48px"


@dataclass
class Typography:
    """Typography scale"""

    heading1: str = "24px"
    heading2: str = "20px"
    heading3: str = "18px"
    heading4: str = "16px"
    body: str = "14px"
    caption: str = "12px"
    tiny: str = "11px"


@dataclass
class BorderRadius:
    """Border radius scale"""

    sm: str = "6px"
    md: str = "8px"
    lg: str = "12px"
    xl: str = "16px"
    full: str = "9999px"


@dataclass
class Shadows:
    """Box shadow definitions"""

    sm: str = "0 1px 2px 0 rgba(0, 0, 0, 0.05)"
    md: str = "0 4px 6px -1px rgba(0, 0, 0, 0.1)"
    lg: str = "0 10px 15px -3px rgba(0, 0, 0, 0.1)"
    xl: str = "0 20px 25px -5px rgba(0, 0, 0, 0.1)"
    glow_purple: str = "0 4px 20px rgba(168, 85, 247, 0.3)"
    glow_cyan: str = "0 4px 20px rgba(34, 211, 238, 0.3)"


# Global theme instance
COLORS = ColorPalette()
SPACING = Spacing()
TYPOGRAPHY = Typography()
RADIUS = BorderRadius()
SHADOWS = Shadows()


def get_chart_colors() -> list[str]:
    """Get ordered list of chart colors for multi-series charts"""
    return [
        COLORS.chart_purple,
        COLORS.chart_cyan,
        COLORS.chart_pink,
        COLORS.chart_green,
        COLORS.chart_orange,
        COLORS.chart_blue,
        COLORS.chart_yellow,
        COLORS.chart_indigo,
    ]


def get_status_color(status: str) -> str:
    """Get color for status value"""
    status_map = {
        "green": COLORS.status_green,
        "amber": COLORS.status_amber,
        "red": COLORS.status_red,
        "on_track": COLORS.status_green,
        "at_risk": COLORS.status_amber,
        "off_track": COLORS.status_red,
    }
    return status_map.get(status.lower(), COLORS.text_muted)


def get_gradient(start_color: str = None, end_color: str = None, angle: int = 135) -> str:
    """Generate CSS linear gradient string"""
    start = start_color or COLORS.gradient_start
    end = end_color or COLORS.gradient_end
    return f"linear-gradient({angle}deg, {start} 0%, {end} 100%)"
