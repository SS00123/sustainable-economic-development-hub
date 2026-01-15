"""
Theme Configuration (DEPRECATED)
Sustainable Economic Development Analytics Hub
Ministry of Economy and Planning

⚠️ DEPRECATED: This module is deprecated.
   Please use analytics_hub_platform.ui.theme instead.

   from analytics_hub_platform.ui.theme import get_theme, Theme, colors, spacing

   This file is kept for backwards compatibility only and will be removed in a future version.
"""

import warnings

warnings.warn(
    "analytics_hub_platform.config.theme is deprecated. "
    "Use analytics_hub_platform.ui.theme instead.",
    DeprecationWarning,
    stacklevel=2,
)

from dataclasses import dataclass, field
from functools import lru_cache


# ---------------------------------------------------------------------
#  Color palette
# ---------------------------------------------------------------------
@dataclass
class ColorPalette:
    """
    Color palette for the Analytics Hub.

    Designed for a professional, government-grade appearance
    with sustainability-focused accent colors.
    """

    # Primary brand colors
    primary: str = "#12436D"  # Deep blue - main brand color
    secondary: str = "#1B7F8C"  # Teal/blue - secondary accents

    # Status colors
    success: str = "#1C7C54"  # Green - good/on-track status
    warning: str = "#D97706"  # Amber - warning/attention
    error: str = "#B91C1C"  # Red - critical/alert

    # Background colors
    background: str = "#F4F7FB"  # Overall app background
    surface: str = "#FFFFFF"  # Cards, panels, modals
    surface_alt: str = "#F9FAFB"  # Alternate surface (subtle differentiation)

    # Border and divider colors
    border: str = "#E2E8F0"  # Light grey borders
    divider: str = "#D1D5DB"  # Dividers between sections

    # Text colors
    text_primary: str = "#111827"  # Main text
    text_secondary: str = "#374151"  # Secondary text
    text_muted: str = "#6B7280"  # Labels, subtitles, hints
    text_inverse: str = "#FFFFFF"  # Text on dark backgrounds

    # Chart colors (ordered for multi-series charts)
    chart_palette: tuple = (
        "#12436D",  # Primary
        "#1B7F8C",  # Secondary
        "#1C7C54",  # Green
        "#0891B2",  # Cyan
        "#7C3AED",  # Purple
        "#D97706",  # Amber
        "#DC2626",  # Red
        "#059669",  # Emerald
        "#4F46E5",  # Indigo
        "#EC4899",  # Pink
    )

    # Status indicator colors (for KPI cards)
    status_green: str = "#10B981"  # On track
    status_green_bg: str = "#D1FAE5"  # Green background
    status_amber: str = "#F59E0B"  # At risk
    status_amber_bg: str = "#FEF3C7"  # Amber background
    status_red: str = "#EF4444"  # Critical
    status_red_bg: str = "#FEE2E2"  # Red background

    # Sustainability-specific colors
    eco_green: str = "#15803D"  # Environmental positive
    eco_green_light: str = "#BBF7D0"  # Light environmental

    def get_status_color(self, status: str) -> str:
        """Return color for a status value."""
        status_map = {
            "green": self.status_green,
            "amber": self.status_amber,
            "red": self.status_red,
            "success": self.success,
            "warning": self.warning,
            "error": self.error,
        }
        return status_map.get(status.lower(), self.text_muted)

    def get_status_background(self, status: str) -> str:
        """Return background color for a status value."""
        status_map = {
            "green": self.status_green_bg,
            "amber": self.status_amber_bg,
            "red": self.status_red_bg,
        }
        return status_map.get(status.lower(), self.surface)


# ---------------------------------------------------------------------
#  Typography
# ---------------------------------------------------------------------
@dataclass
class Typography:
    """Typography settings for consistent text styling."""

    # Font family stack
    font_family: str = (
        '"Segoe UI", "Roboto", "Source Sans 3", system-ui, '
        "-apple-system, BlinkMacSystemFont, sans-serif"
    )
    font_family_arabic: str = '"Segoe UI", "Tahoma", "Arial", sans-serif'
    font_family_mono: str = '"Consolas", "Monaco", "Courier New", monospace'

    # Font sizes (in pixels)
    size_xs: int = 11
    size_sm: int = 12
    size_base: int = 14
    size_lg: int = 16
    size_xl: int = 18
    size_2xl: int = 20
    size_3xl: int = 24
    size_4xl: int = 28
    size_5xl: int = 32

    # Font weights
    weight_normal: int = 400
    weight_medium: int = 500
    weight_semibold: int = 600
    weight_bold: int = 700

    # Line heights
    line_height_tight: float = 1.25
    line_height_normal: float = 1.5
    line_height_relaxed: float = 1.75

    # Specific element styles
    page_title_size: int = 28
    page_title_weight: int = 700
    section_title_size: int = 20
    section_title_weight: int = 600
    kpi_value_size: int = 32
    kpi_value_weight: int = 700
    kpi_label_size: int = 12
    body_size: int = 14


# ---------------------------------------------------------------------
#  Spacing
# ---------------------------------------------------------------------
@dataclass
class Spacing:
    """Spacing system based on 8px base unit."""

    # Base unit
    unit: int = 8

    # Named sizes
    xs: int = 4
    sm: int = 8
    md: int = 16
    lg: int = 24
    xl: int = 32
    xxl: int = 48

    # Component-specific spacing
    card_padding: int = 20
    section_gap: int = 24
    page_margin: int = 32
    inline_gap: int = 8


# ---------------------------------------------------------------------
#  Border radius
# ---------------------------------------------------------------------
@dataclass
class BorderRadius:
    """Border radius values for rounded corners."""

    none: int = 0
    sm: int = 4
    md: int = 8
    lg: int = 12
    xl: int = 16
    full: str = "9999px"

    # Component-specific
    card: int = 12
    button: int = 8
    input: int = 6
    badge: int = 4


# ---------------------------------------------------------------------
#  Shadows
# ---------------------------------------------------------------------
@dataclass
class Shadows:
    """Box shadow definitions."""

    none: str = "none"
    sm: str = "0 1px 2px 0 rgba(0, 0, 0, 0.05)"
    md: str = "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)"
    lg: str = "0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)"
    xl: str = "0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)"

    # Component-specific
    card: str = "0 1px 3px 0 rgba(15, 23, 42, 0.12)"
    dropdown: str = "0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)"


# ---------------------------------------------------------------------
#  Component styles
# ---------------------------------------------------------------------
@dataclass
class ComponentStyles:
    """Pre-defined component style configurations."""

    # KPI Card styles
    kpi_card: dict = field(
        default_factory=lambda: {
            "background": "#FFFFFF",
            "border": "1px solid #E2E8F0",
            "border_radius": "12px",
            "padding": "20px",
            "shadow": "0 1px 3px 0 rgba(15, 23, 42, 0.12)",
            "min_height": "140px",
        }
    )

    # Section header styles
    section_header: dict = field(
        default_factory=lambda: {
            "font_size": "20px",
            "font_weight": "600",
            "color": "#111827",
            "margin_bottom": "16px",
            "padding_bottom": "8px",
            "border_bottom": "2px solid #12436D",
        }
    )

    # Status badge/pill styles
    status_badge: dict = field(
        default_factory=lambda: {
            "padding": "4px 12px",
            "border_radius": "16px",
            "font_size": "12px",
            "font_weight": "600",
            "text_transform": "uppercase",
        }
    )

    # Data table styles
    data_table: dict = field(
        default_factory=lambda: {
            "header_bg": "#F4F7FB",
            "header_color": "#111827",
            "row_hover_bg": "#F9FAFB",
            "border_color": "#E2E8F0",
            "cell_padding": "12px 16px",
        }
    )

    # Alert/notification box styles
    alert_box: dict = field(
        default_factory=lambda: {
            "padding": "16px",
            "border_radius": "8px",
            "border_left_width": "4px",
        }
    )

    # Button styles
    primary_button: dict = field(
        default_factory=lambda: {
            "background": "#12436D",
            "color": "#FFFFFF",
            "padding": "10px 20px",
            "border_radius": "8px",
            "font_weight": "600",
            "hover_background": "#0B2B48",
        }
    )

    secondary_button: dict = field(
        default_factory=lambda: {
            "background": "#FFFFFF",
            "color": "#12436D",
            "border": "1px solid #12436D",
            "padding": "10px 20px",
            "border_radius": "8px",
            "font_weight": "600",
        }
    )


# ---------------------------------------------------------------------
#  Theme root object
# ---------------------------------------------------------------------
@dataclass
class Theme:
    """
    Complete theme configuration for the Analytics Hub.
    """

    colors: ColorPalette = field(default_factory=ColorPalette)
    typography: Typography = field(default_factory=Typography)
    spacing: Spacing = field(default_factory=Spacing)
    border_radius: BorderRadius = field(default_factory=BorderRadius)
    shadows: Shadows = field(default_factory=Shadows)
    components: ComponentStyles = field(default_factory=ComponentStyles)

    def get_kpi_card_css(self) -> str:
        """Generate CSS for KPI cards."""
        c = self.components.kpi_card
        return f"""
            background: {c["background"]};
            border: {c["border"]};
            border-radius: {c["border_radius"]};
            padding: {c["padding"]};
            box-shadow: {c["shadow"]};
            min-height: {c["min_height"]};
        """

    def get_streamlit_custom_css(self) -> str:
        """Generate custom CSS for the Streamlit app."""
        return f"""
        <style>
            /* ROOT & GLOBAL --------------------------------------- */
            html, body {{
                font-family: {self.typography.font_family};
                background-color: {self.colors.background};
                color: {self.colors.text_primary};
            }}

            [data-testid="stAppViewContainer"] > .main {{
                background-color: {self.colors.background};
            }}

            /* MAIN CONTAINER -------------------------------------- */
            .main .block-container {{
                padding-top: {self.spacing.lg}px;
                padding-bottom: {self.spacing.lg}px;
                max-width: 1400px;
            }}

            /* TITLES & HEADINGS ----------------------------------- */
            h1 {{
                color: {self.colors.primary} !important;
                font-weight: {self.typography.page_title_weight};
                font-size: {self.typography.page_title_size}px;
                letter-spacing: -0.5px;
            }}

            h2, h3 {{
                color: {self.colors.text_primary} !important;
                font-weight: {self.typography.section_title_weight};
            }}

            /* KPI METRICS ---------------------------------------- */
            [data-testid="stMetricValue"] {{
                font-size: {self.typography.kpi_value_size}px !important;
                font-weight: {self.typography.kpi_value_weight} !important;
                color: {self.colors.text_primary} !important;
            }}

            [data-testid="stMetricLabel"] {{
                font-size: {self.typography.kpi_label_size}px !important;
                color: {self.colors.text_muted} !important;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}

            /* CARDS ---------------------------------------------- */
            .stCard {{
                background: {self.colors.surface};
                border: 1px solid {self.colors.border};
                border-radius: {self.border_radius.card}px;
                padding: {self.spacing.card_padding}px;
                box-shadow: {self.shadows.card};
            }}

            /* SIDEBAR -------------------------------------------- */
            [data-testid="stSidebar"] {{
                background-color: {self.colors.surface};
                border-right: 1px solid {self.colors.border};
            }}

            [data-testid="stSidebar"] > div:first-child {{
                padding-top: 0 !important;
            }}

            /* Hide default sidebar title */
            [data-testid="stSidebar"] h1 {{
                display: none;
            }}

            /* BUTTONS -------------------------------------------- */
            .main .stButton > button {{
                background-color: {self.components.primary_button["background"]};
                color: {self.components.primary_button["color"]};
                border-radius: {self.border_radius.button}px;
                font-weight: {self.typography.weight_semibold};
                transition: all 0.2s ease;
                border: none;
            }}

            .main .stButton > button:hover {{
                background-color: {self.components.primary_button["hover_background"]};
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            }}

            /* Secondary buttons (wrap button with class="secondary-button") */
            .main .secondary-button > button {{
                background-color: {self.components.secondary_button["background"]};
                color: {self.components.secondary_button["color"]};
                border-radius: {self.border_radius.button}px;
                border: {self.components.secondary_button["border"]};
                font-weight: {self.typography.weight_semibold};
            }}

            /* TABLES & DATA FRAMES ------------------------------- */
            .stDataFrame {{
                border: 1px solid {self.colors.border};
                border-radius: {self.border_radius.md}px;
            }}

            /* TABS ----------------------------------------------- */
            .stTabs [data-baseweb="tab-list"] {{
                gap: {self.spacing.sm}px;
                background-color: transparent;
            }}

            .stTabs [data-baseweb="tab"] {{
                border-radius: {self.border_radius.sm}px {self.border_radius.sm}px 0 0;
                padding: 10px 20px;
                font-weight: 500;
            }}

            .stTabs [aria-selected="true"] {{
                background-color: {self.colors.primary} !important;
                color: white !important;
            }}

            /* FORM ELEMENTS -------------------------------------- */
            .stSelectbox [data-baseweb="select"] {{
                border-radius: {self.border_radius.input}px;
            }}

            .stNumberInput input {{
                border-radius: {self.border_radius.input}px;
            }}

            /* DIVIDERS ------------------------------------------ */
            hr {{
                border-color: {self.colors.divider};
                margin: {self.spacing.lg}px 0;
            }}

            /* STATUS BADGES -------------------------------------- */
            .status-green {{
                background-color: {self.colors.status_green_bg};
                color: {self.colors.status_green};
                padding: 4px 12px;
                border-radius: 16px;
                font-size: 12px;
                font-weight: 600;
            }}

            .status-amber {{
                background-color: {self.colors.status_amber_bg};
                color: {self.colors.status_amber};
                padding: 4px 12px;
                border-radius: 16px;
                font-size: 12px;
                font-weight: 600;
            }}

            .status-red {{
                background-color: {self.colors.status_red_bg};
                color: {self.colors.status_red};
                padding: 4px 12px;
                border-radius: 16px;
                font-size: 12px;
                font-weight: 600;
            }}

            /* PLOTLY CHARTS -------------------------------------- */
            .js-plotly-plot {{
                border-radius: {self.border_radius.md}px;
            }}

            /* EXPANDERS ------------------------------------------ */
            .streamlit-expanderHeader {{
                font-weight: {self.typography.weight_semibold};
                color: {self.colors.text_primary};
            }}

            /* ALERTS --------------------------------------------- */
            .stAlert {{
                border-radius: {self.border_radius.md}px;
            }}
        </style>
        """


# ---------------------------------------------------------------------
#  Global theme accessor
# ---------------------------------------------------------------------
_theme_instance: Theme | None = None


@lru_cache(maxsize=1)
def get_theme() -> Theme:
    """Return the global theme configuration."""
    global _theme_instance
    if _theme_instance is None:
        _theme_instance = Theme()
    return _theme_instance
