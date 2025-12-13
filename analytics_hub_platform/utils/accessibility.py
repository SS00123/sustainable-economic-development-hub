"""
Accessibility Utility
Sustainable Economic Development Analytics Hub
Ministry of Economy and Planning

Accessibility features and WCAG compliance helpers.
"""

from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from enum import Enum


class ContrastLevel(str, Enum):
    """WCAG contrast level requirements."""
    AA = "AA"  # 4.5:1 for normal text, 3:1 for large text
    AAA = "AAA"  # 7:1 for normal text, 4.5:1 for large text


class FontSize(str, Enum):
    """Accessibility font size options."""
    SMALL = "small"
    NORMAL = "normal"
    LARGE = "large"
    EXTRA_LARGE = "extra_large"


@dataclass
class AccessibilityConfig:
    """Accessibility configuration settings."""
    
    # Visual settings
    high_contrast: bool = False
    font_size: FontSize = FontSize.NORMAL
    reduce_motion: bool = False
    
    # Color settings
    color_blind_friendly: bool = True
    contrast_level: ContrastLevel = ContrastLevel.AA
    
    # Interaction settings
    keyboard_navigation: bool = True
    focus_indicators: bool = True
    
    # Content settings
    alt_text_required: bool = True
    aria_labels: bool = True
    
    # Timing
    extended_timeouts: bool = False
    auto_refresh_disabled: bool = False
    
    def to_css_vars(self) -> Dict[str, str]:
        """Convert config to CSS custom properties."""
        font_sizes = {
            FontSize.SMALL: "14px",
            FontSize.NORMAL: "16px",
            FontSize.LARGE: "18px",
            FontSize.EXTRA_LARGE: "20px",
        }
        
        return {
            "--a11y-font-size-base": font_sizes[self.font_size],
            "--a11y-motion": "none" if self.reduce_motion else "all",
            "--a11y-focus-outline": "3px solid #2563eb" if self.focus_indicators else "none",
            "--a11y-contrast-mode": "high" if self.high_contrast else "normal",
        }


# Color palettes for different types of color blindness
COLOR_BLIND_PALETTES = {
    "deuteranopia": {  # Red-green (most common)
        "positive": "#0077BB",  # Blue
        "warning": "#EE7733",   # Orange
        "negative": "#CC3311",  # Red-orange
        "neutral": "#009988",   # Teal
    },
    "protanopia": {  # Red-green
        "positive": "#004488",  # Dark blue
        "warning": "#DDAA33",   # Gold
        "negative": "#BB5566",  # Pink
        "neutral": "#000000",   # Black
    },
    "tritanopia": {  # Blue-yellow (rare)
        "positive": "#117733",  # Green
        "warning": "#882255",   # Magenta
        "negative": "#AA4499",  # Purple
        "neutral": "#44AA99",   # Teal
    },
    "default": {  # Standard accessible palette
        "positive": "#2E7D32",  # Green
        "warning": "#D97706",   # Amber
        "negative": "#B91C1C",  # Red
        "neutral": "#64748B",   # Slate
    },
}


def get_accessibility_config() -> AccessibilityConfig:
    """
    Get current accessibility configuration.
    
    In production, this would load from user preferences.
    
    Returns:
        AccessibilityConfig object
    """
    # Default configuration with accessibility best practices
    return AccessibilityConfig(
        high_contrast=False,
        font_size=FontSize.NORMAL,
        reduce_motion=False,
        color_blind_friendly=True,
        contrast_level=ContrastLevel.AA,
        keyboard_navigation=True,
        focus_indicators=True,
        alt_text_required=True,
        aria_labels=True,
    )


def get_accessible_color(
    semantic: str,
    color_blind_mode: Optional[str] = None,
) -> str:
    """
    Get accessible color for semantic meaning.
    
    Args:
        semantic: Semantic meaning (positive, warning, negative, neutral)
        color_blind_mode: Color blindness type or None for default
    
    Returns:
        Hex color code
    """
    palette = COLOR_BLIND_PALETTES.get(color_blind_mode, COLOR_BLIND_PALETTES["default"])
    return palette.get(semantic, palette["neutral"])


def generate_alt_text(
    chart_type: str,
    title: str,
    summary_stats: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Generate descriptive alt text for charts.
    
    Args:
        chart_type: Type of chart (line, bar, pie, etc.)
        title: Chart title
        summary_stats: Optional summary statistics
    
    Returns:
        Alt text string
    """
    base = f"{chart_type.capitalize()} chart showing {title}."
    
    if summary_stats:
        details = []
        if "min" in summary_stats and "max" in summary_stats:
            details.append(f"Values range from {summary_stats['min']} to {summary_stats['max']}.")
        if "trend" in summary_stats:
            details.append(f"Overall trend is {summary_stats['trend']}.")
        if "count" in summary_stats:
            details.append(f"Contains {summary_stats['count']} data points.")
        
        if details:
            base += " " + " ".join(details)
    
    return base


def generate_aria_label(
    element_type: str,
    value: Any,
    context: Optional[str] = None,
) -> str:
    """
    Generate ARIA label for interactive elements.
    
    Args:
        element_type: Type of element (button, input, etc.)
        value: Current value or action
        context: Additional context
    
    Returns:
        ARIA label string
    """
    label_parts = [str(value)]
    
    if context:
        label_parts.append(context)
    
    if element_type == "button":
        label_parts.append("button")
    elif element_type == "input":
        label_parts.append("input field")
    elif element_type == "select":
        label_parts.append("dropdown menu")
    
    return ", ".join(label_parts)


def get_font_size_multiplier(font_size: FontSize) -> float:
    """
    Get font size multiplier for scaling.
    
    Args:
        font_size: Accessibility font size setting
    
    Returns:
        Multiplier value
    """
    multipliers = {
        FontSize.SMALL: 0.875,
        FontSize.NORMAL: 1.0,
        FontSize.LARGE: 1.125,
        FontSize.EXTRA_LARGE: 1.25,
    }
    return multipliers.get(font_size, 1.0)


def check_contrast_ratio(
    foreground: str,
    background: str,
) -> float:
    """
    Calculate contrast ratio between two colors.
    
    Args:
        foreground: Hex color code for foreground
        background: Hex color code for background
    
    Returns:
        Contrast ratio (1-21)
    """
    def hex_to_luminance(hex_color: str) -> float:
        """Calculate relative luminance of a color."""
        hex_color = hex_color.lstrip("#")
        r, g, b = tuple(int(hex_color[i:i+2], 16) / 255 for i in (0, 2, 4))
        
        def adjust(c: float) -> float:
            return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
        
        return 0.2126 * adjust(r) + 0.7152 * adjust(g) + 0.0722 * adjust(b)
    
    l1 = hex_to_luminance(foreground)
    l2 = hex_to_luminance(background)
    
    lighter = max(l1, l2)
    darker = min(l1, l2)
    
    return (lighter + 0.05) / (darker + 0.05)


def meets_wcag_contrast(
    foreground: str,
    background: str,
    level: ContrastLevel = ContrastLevel.AA,
    is_large_text: bool = False,
) -> bool:
    """
    Check if color combination meets WCAG contrast requirements.
    
    Args:
        foreground: Foreground color hex
        background: Background color hex
        level: WCAG level to check (AA or AAA)
        is_large_text: Whether text is large (14pt bold or 18pt+)
    
    Returns:
        True if contrast requirements are met
    """
    ratio = check_contrast_ratio(foreground, background)
    
    if level == ContrastLevel.AA:
        threshold = 3.0 if is_large_text else 4.5
    else:  # AAA
        threshold = 4.5 if is_large_text else 7.0
    
    return ratio >= threshold


def get_accessible_text_color(
    background: str,
    light_text: str = "#FFFFFF",
    dark_text: str = "#111827",
    level: ContrastLevel = ContrastLevel.AA
) -> str:
    """
    Get accessible text color (light or dark) based on background.
    
    Automatically selects light or dark text color based on which
    provides better contrast against the background.
    
    Args:
        background: Background color hex
        light_text: Light text option (default white)
        dark_text: Dark text option (default dark gray)
        level: WCAG level to meet
    
    Returns:
        Hex color for text that meets WCAG contrast requirements
    """
    light_ratio = check_contrast_ratio(light_text, background)
    dark_ratio = check_contrast_ratio(dark_text, background)
    
    # Return whichever provides better contrast
    return light_text if light_ratio > dark_ratio else dark_text


def validate_theme_colors(theme_colors: Dict[str, str]) -> Dict[str, str]:
    """
    Validate theme colors for accessibility and return warnings.
    
    Args:
        theme_colors: Dictionary of color definitions from theme
    
    Returns:
        Dictionary mapping color pairs to warning messages
    """
    warnings = {}
    
    # Common text/background combinations to check
    checks = [
        ("text_primary", "background", False),
        ("text_secondary", "background", False),
        ("text_muted", "surface", False),
        ("text_inverse", "primary", False),
        ("text_inverse", "secondary", False),
    ]
    
    for fg_key, bg_key, is_large in checks:
        if fg_key in theme_colors and bg_key in theme_colors:
            fg = theme_colors[fg_key]
            bg = theme_colors[bg_key]
            
            if not meets_wcag_contrast(fg, bg, ContrastLevel.AA, is_large):
                ratio = check_contrast_ratio(fg, bg)
                warnings[f"{fg_key}_on_{bg_key}"] = (
                    f"Low contrast: {fg_key} on {bg_key} "
                    f"(ratio: {ratio:.2f}, needs 4.5+)"
                )
    
    return warnings


def get_accessible_css() -> str:
    """
    Generate CSS for accessibility features.
    
    Returns:
        CSS string
    """
    return """
    /* Accessibility CSS */
    
    /* Focus indicators */
    :focus {
        outline: 3px solid #2563eb !important;
        outline-offset: 2px;
    }
    
    /* Reduce motion */
    @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after {
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: 0.01ms !important;
        }
    }
    
    /* High contrast mode */
    @media (prefers-contrast: high) {
        .kpi-card {
            border-width: 2px !important;
        }
        
        .status-indicator {
            font-weight: bold !important;
        }
    }
    
    /* Skip link */
    .skip-link {
        position: absolute;
        top: -40px;
        left: 0;
        background: #003366;
        color: white;
        padding: 8px 16px;
        z-index: 100;
    }
    
    .skip-link:focus {
        top: 0;
    }
    
    /* Screen reader only content */
    .sr-only {
        position: absolute;
        width: 1px;
        height: 1px;
        padding: 0;
        margin: -1px;
        overflow: hidden;
        clip: rect(0, 0, 0, 0);
        white-space: nowrap;
        border: 0;
    }
    """


# Alias for backward compatibility
calculate_contrast_ratio = check_contrast_ratio
