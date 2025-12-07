"""
Theme Configuration
Sustainable Economic Development Analytics Hub
Ministry of Economy and Planning

This module defines the visual theme for the analytics platform,
including colors, typography, spacing, and component styles.
The theme is designed for a professional, government-grade appearance
with a sustainability emphasis.
"""

from dataclasses import dataclass, field
from typing import Dict, Optional
from functools import lru_cache


@dataclass
class ColorPalette:
    """
    Color palette for the Analytics Hub.
    
    Designed for a professional, government-grade appearance
    with sustainability-focused accent colors.
    """
    
    # Primary brand colors
    primary: str = "#003366"      # Deep navy blue - main brand color
    secondary: str = "#006B8F"    # Teal/blue - secondary accents
    
    # Status colors
    success: str = "#2E7D32"      # Green - good/on-track status
    warning: str = "#D97706"      # Amber - warning/attention
    error: str = "#B91C1C"        # Red - critical/alert
    
    # Background colors
    background: str = "#F5F7FA"   # Overall app background
    surface: str = "#FFFFFF"      # Cards, panels, modals
    surface_alt: str = "#F8FAFC"  # Alternate surface (subtle differentiation)
    
    # Border and divider colors
    border: str = "#E5E7EB"       # Light grey borders
    divider: str = "#D1D5DB"      # Dividers between sections
    
    # Text colors
    text_primary: str = "#1F2933"   # Main text
    text_secondary: str = "#4B5563"  # Secondary text
    text_muted: str = "#6B7280"      # Labels, subtitles, hints
    text_inverse: str = "#FFFFFF"    # Text on dark backgrounds
    
    # Chart colors (ordered for multi-series charts)
    chart_palette: tuple = (
        "#003366",  # Primary
        "#006B8F",  # Secondary
        "#2E7D32",  # Green
        "#0891B2",  # Cyan
        "#7C3AED",  # Purple
        "#D97706",  # Amber
        "#DC2626",  # Red
        "#059669",  # Emerald
        "#4F46E5",  # Indigo
        "#EC4899",  # Pink
    )
    
    # Status indicator colors (for KPI cards)
    status_green: str = "#10B981"      # On track
    status_green_bg: str = "#D1FAE5"   # Green background
    status_amber: str = "#F59E0B"      # At risk
    status_amber_bg: str = "#FEF3C7"   # Amber background
    status_red: str = "#EF4444"        # Critical
    status_red_bg: str = "#FEE2E2"     # Red background
    
    # Sustainability-specific colors
    eco_green: str = "#15803D"         # Environmental positive
    eco_green_light: str = "#BBF7D0"   # Light environmental
    
    def get_status_color(self, status: str) -> str:
        """Get color for a status value."""
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
        """Get background color for a status value."""
        status_map = {
            "green": self.status_green_bg,
            "amber": self.status_amber_bg,
            "red": self.status_red_bg,
        }
        return status_map.get(status.lower(), self.surface)


@dataclass
class Typography:
    """Typography settings for consistent text styling."""
    
    # Font family stack
    font_family: str = '"Segoe UI", "Roboto", "Source Sans 3", system-ui, -apple-system, BlinkMacSystemFont, sans-serif'
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


@dataclass
class Shadows:
    """Box shadow definitions."""
    
    none: str = "none"
    sm: str = "0 1px 2px 0 rgba(0, 0, 0, 0.05)"
    md: str = "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)"
    lg: str = "0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)"
    xl: str = "0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)"
    
    # Component-specific
    card: str = "0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)"
    dropdown: str = "0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)"


@dataclass
class ComponentStyles:
    """Pre-defined component style configurations."""
    
    # KPI Card styles
    kpi_card: Dict = field(default_factory=lambda: {
        "background": "#FFFFFF",
        "border": "1px solid #E5E7EB",
        "border_radius": "12px",
        "padding": "20px",
        "shadow": "0 1px 3px 0 rgba(0, 0, 0, 0.1)",
        "min_height": "140px",
    })
    
    # Section header styles
    section_header: Dict = field(default_factory=lambda: {
        "font_size": "20px",
        "font_weight": "600",
        "color": "#1F2933",
        "margin_bottom": "16px",
        "padding_bottom": "8px",
        "border_bottom": "2px solid #003366",
    })
    
    # Status badge/pill styles
    status_badge: Dict = field(default_factory=lambda: {
        "padding": "4px 12px",
        "border_radius": "16px",
        "font_size": "12px",
        "font_weight": "600",
        "text_transform": "uppercase",
    })
    
    # Data table styles
    data_table: Dict = field(default_factory=lambda: {
        "header_bg": "#F5F7FA",
        "header_color": "#1F2933",
        "row_hover_bg": "#F8FAFC",
        "border_color": "#E5E7EB",
        "cell_padding": "12px 16px",
    })
    
    # Alert/notification box styles
    alert_box: Dict = field(default_factory=lambda: {
        "padding": "16px",
        "border_radius": "8px",
        "border_left_width": "4px",
    })
    
    # Button styles
    primary_button: Dict = field(default_factory=lambda: {
        "background": "#003366",
        "color": "#FFFFFF",
        "padding": "10px 20px",
        "border_radius": "8px",
        "font_weight": "600",
        "hover_background": "#002244",
    })
    
    secondary_button: Dict = field(default_factory=lambda: {
        "background": "#FFFFFF",
        "color": "#003366",
        "border": "1px solid #003366",
        "padding": "10px 20px",
        "border_radius": "8px",
        "font_weight": "600",
    })


@dataclass
class Theme:
    """
    Complete theme configuration for the Analytics Hub.
    
    This theme is designed for:
    - Professional, government-grade appearance
    - Accessibility and readability
    - Sustainability/environmental emphasis
    - Executive presentation quality
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
            background: {c['background']};
            border: {c['border']};
            border-radius: {c['border_radius']};
            padding: {c['padding']};
            box-shadow: {c['shadow']};
            min-height: {c['min_height']};
        """
    
    def get_streamlit_custom_css(self) -> str:
        """Generate custom CSS for Streamlit app."""
        return f"""
        <style>
            /* Main container */
            .main .block-container {{
                padding-top: {self.spacing.lg}px;
                padding-bottom: {self.spacing.lg}px;
                max-width: 1400px;
            }}
            
            /* Headers */
            h1 {{
                color: {self.colors.primary} !important;
                font-weight: {self.typography.weight_bold};
            }}
            
            h2, h3 {{
                color: {self.colors.text_primary} !important;
                font-weight: {self.typography.weight_semibold};
            }}
            
            /* Metrics/KPI styling */
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
            
            /* Cards */
            .stCard {{
                background: {self.colors.surface};
                border: 1px solid {self.colors.border};
                border-radius: {self.border_radius.card}px;
                padding: {self.spacing.card_padding}px;
                box-shadow: {self.shadows.card};
            }}
            
            /* Sidebar */
            [data-testid="stSidebar"] {{
                background-color: {self.colors.surface};
                border-right: 1px solid {self.colors.border};
            }}
            
            /* Buttons */
            .stButton > button {{
                background-color: {self.colors.primary};
                color: {self.colors.text_inverse};
                border-radius: {self.border_radius.button}px;
                font-weight: {self.typography.weight_semibold};
                transition: background-color 0.2s ease;
            }}
            
            .stButton > button:hover {{
                background-color: #002244;
            }}
            
            /* Tables */
            .stDataFrame {{
                border: 1px solid {self.colors.border};
                border-radius: {self.border_radius.md}px;
            }}
            
            /* Tabs */
            .stTabs [data-baseweb="tab-list"] {{
                gap: {self.spacing.sm}px;
            }}
            
            .stTabs [data-baseweb="tab"] {{
                border-radius: {self.border_radius.sm}px {self.border_radius.sm}px 0 0;
            }}
            
            /* Selectbox */
            .stSelectbox [data-baseweb="select"] {{
                border-radius: {self.border_radius.input}px;
            }}
            
            /* Dividers */
            hr {{
                border-color: {self.colors.divider};
                margin: {self.spacing.lg}px 0;
            }}
            
            /* Status badges */
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
        </style>
        """


# Global theme instance
_theme_instance: Optional[Theme] = None


@lru_cache(maxsize=1)
def get_theme() -> Theme:
    """Get the global theme configuration."""
    global _theme_instance
    if _theme_instance is None:
        _theme_instance = Theme()
    return _theme_instance
