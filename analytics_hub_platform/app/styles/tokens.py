"""
Design Tokens - Single Source of Truth
Sustainable Economic Development Analytics Hub
Ministry of Economy and Planning

This module defines the canonical design tokens for the application.
All components and pages MUST reference these tokens - no inline styles.

Token Categories:
- Colors: Background, text, status, accent, domain-specific
- Typography: Font families, sizes, weights, line heights
- Spacing: 8pt grid system
- Radius: Border radius scale
- Shadows: Card and glow shadows (max 2 for performance)
- Transitions: Animation timing

Usage:
    from analytics_hub_platform.app.styles.tokens import (
        colors, typography, spacing, radius, shadows,
        get_status_color, get_domain_color, get_gradient,
    )

    # Direct access
    background = colors.bg_main
    heading_size = typography.h1

    # Status-based
    color = get_status_color("green")

Figma Alignment:
    Token names match Figma design system exactly:
    - bg/primary, bg/card, bg/surface → colors.bg_main, colors.bg_card
    - text/primary, text/secondary → colors.text_primary, colors.text_secondary
    - spacing/sm, spacing/md → spacing.sm, spacing.md
    - radius/card, radius/button → radius.card, radius.button
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Tuple

# Re-export utility functions from the canonical theme implementation
from analytics_hub_platform.ui.theme import (
    hex_to_rgba,
    get_gradient,
    get_chart_layout_config,
)


# =============================================================================
# COLOR TOKENS
# =============================================================================

@dataclass(frozen=True)
class ColorTokens:
    """
    Color tokens organized by role.

    Figma naming convention:
    - bg/* : Background colors
    - text/* : Text colors
    - status/* : Status indicator colors
    - accent/* : Brand accent colors
    - domain/* : Domain/pillar specific colors
    """

    # === Background Colors ===
    bg_deep: str = "#0B1120"        # Deepest background (hero, overlays)
    bg_main: str = "#111827"        # Main canvas background
    bg_card: str = "#1E293B"        # Card background
    bg_card_alt: str = "#1E2340"    # Alternate card (subtle differentiation)
    bg_hover: str = "#334155"       # Hover state
    bg_glass: str = "linear-gradient(135deg, rgba(255,255,255,0.08) 0%, rgba(255,255,255,0.02) 100%)"

    # === Text Colors ===
    text_primary: str = "rgba(255, 255, 255, 0.95)"    # Main body text
    text_secondary: str = "rgba(255, 255, 255, 0.78)"  # Secondary text
    text_muted: str = "rgba(255, 255, 255, 0.55)"      # Labels, captions
    text_subtle: str = "rgba(255, 255, 255, 0.35)"     # Hints, disabled

    # === Status Colors (with backgrounds) ===
    status_green: str = "#10B981"
    status_green_bg: str = "rgba(16, 185, 129, 0.15)"
    status_amber: str = "#F59E0B"
    status_amber_bg: str = "rgba(245, 158, 11, 0.15)"
    status_red: str = "#EF4444"
    status_red_bg: str = "rgba(239, 68, 68, 0.15)"

    # === Accent Colors ===
    accent_primary: str = "#06B6D4"     # Cyan - primary accent
    accent_secondary: str = "#3B82F6"   # Blue - secondary accent
    accent_purple: str = "#8B5CF6"      # Violet
    accent_pink: str = "#EC4899"        # Pink

    # === Domain/Pillar Colors ===
    domain_economic: str = "#3B82F6"       # Blue
    domain_labor: str = "#8B5CF6"          # Violet
    domain_social: str = "#06B6D4"         # Cyan
    domain_environmental: str = "#10B981"  # Green
    domain_data_quality: str = "#64748B"   # Slate

    # === Border Colors ===
    border: str = "rgba(255, 255, 255, 0.08)"
    border_light: str = "rgba(255, 255, 255, 0.12)"
    border_glow: str = "rgba(168, 85, 247, 0.3)"

    # === Chart Palette (10 colors for multi-series) ===
    chart_palette: Tuple[str, ...] = (
        "#06B6D4",  # Cyan
        "#3B82F6",  # Blue
        "#10B981",  # Green
        "#F59E0B",  # Amber
        "#EF4444",  # Red
        "#8B5CF6",  # Violet
        "#EC4899",  # Pink
        "#14B8A6",  # Teal
        "#F472B6",  # Light pink
        "#818CF8",  # Indigo
    )

    def get_status_color(self, status: str) -> str:
        """Get foreground color for status."""
        status_map = {
            "green": self.status_green,
            "amber": self.status_amber,
            "red": self.status_red,
            "success": self.status_green,
            "warning": self.status_amber,
            "error": self.status_red,
            "on_track": self.status_green,
            "at_risk": self.status_amber,
            "off_track": self.status_red,
        }
        return status_map.get(str(status).lower(), self.text_muted)

    def get_status_bg(self, status: str) -> str:
        """Get background color for status."""
        status_map = {
            "green": self.status_green_bg,
            "amber": self.status_amber_bg,
            "red": self.status_red_bg,
        }
        return status_map.get(str(status).lower(), "rgba(255,255,255,0.05)")

    def get_domain_color(self, domain: str) -> str:
        """Get color for domain/pillar."""
        domain_map = {
            "economic": self.domain_economic,
            "labor": self.domain_labor,
            "labor_skills": self.domain_labor,
            "social": self.domain_social,
            "social_digital": self.domain_social,
            "environmental": self.domain_environmental,
            "environment": self.domain_environmental,
            "data_quality": self.domain_data_quality,
        }
        return domain_map.get(str(domain).lower(), self.accent_primary)


# =============================================================================
# TYPOGRAPHY TOKENS
# =============================================================================

@dataclass(frozen=True)
class TypographyTokens:
    """
    Typography tokens following 8pt scale.

    Figma naming:
    - h1, h2, h3, h4: Heading sizes
    - body, caption, small: Body text sizes
    - weight/*: Font weights
    """

    # === Font Family ===
    family_base: str = "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
    family_arabic: str = "'Segoe UI', 'Tahoma', 'Arial', sans-serif"
    family_mono: str = "'JetBrains Mono', 'Consolas', 'Monaco', monospace"

    # === Size Scale (Figma: typography/size/*) ===
    hero: str = "48px"      # Hero numbers, gauges
    h1: str = "32px"        # Page titles
    h2: str = "24px"        # Section headers
    h3: str = "18px"        # Card titles
    h4: str = "16px"        # Sub-section titles
    body: str = "14px"      # Body text
    caption: str = "12px"   # Captions, labels
    small: str = "11px"     # Small text
    tiny: str = "10px"      # Tiny labels

    # === Font Weights (Figma: typography/weight/*) ===
    weight_regular: int = 400
    weight_medium: int = 500
    weight_semibold: int = 600
    weight_bold: int = 700
    weight_extrabold: int = 800

    # === Line Heights ===
    line_tight: float = 1.25
    line_normal: float = 1.5
    line_relaxed: float = 1.75


# =============================================================================
# SPACING TOKENS
# =============================================================================

@dataclass(frozen=True)
class SpacingTokens:
    """
    Spacing tokens based on 8pt grid.

    Figma naming: spacing/xs, spacing/sm, etc.
    """

    # === Base Scale ===
    xs: str = "4px"     # 0.5x base
    sm: str = "8px"     # 1x base
    md: str = "16px"    # 2x base
    lg: str = "24px"    # 3x base
    xl: str = "32px"    # 4x base
    xxl: str = "48px"   # 6x base

    # === Semantic Spacing ===
    page_margin: str = "32px"
    section_gap: str = "32px"
    card_gap: str = "24px"
    card_padding: str = "20px"
    row_gap: str = "20px"
    gutter: str = "16px"
    inline_gap: str = "8px"


# =============================================================================
# RADIUS TOKENS
# =============================================================================

@dataclass(frozen=True)
class RadiusTokens:
    """
    Border radius tokens.

    Figma naming: radius/xs, radius/sm, etc.
    """

    xs: str = "4px"
    sm: str = "6px"
    md: str = "8px"
    lg: str = "12px"
    xl: str = "16px"
    xxl: str = "20px"
    full: str = "9999px"

    # === Component-specific (Figma: radius/card, radius/button) ===
    card: str = "16px"
    button: str = "8px"
    input: str = "8px"
    badge: str = "20px"


# =============================================================================
# SHADOW TOKENS
# =============================================================================

@dataclass(frozen=True)
class ShadowTokens:
    """
    Shadow tokens - limited to 2 card variants for performance.

    Figma naming: shadow/card, shadow/card-hover
    """

    # === Card Shadows (max 2 for performance) ===
    card: str = "0 4px 6px rgba(0, 0, 0, 0.1), 0 20px 50px rgba(0, 0, 0, 0.4)"
    card_hover: str = "0 8px 16px rgba(0, 0, 0, 0.15), 0 30px 60px rgba(0, 0, 0, 0.45)"

    # === Subtle variant ===
    card_sm: str = "0 2px 4px rgba(0, 0, 0, 0.1), 0 10px 20px rgba(0, 0, 0, 0.3)"
    card_subtle: str = "0 4px 12px rgba(0, 0, 0, 0.25)"

    # === Glow Effects (used sparingly) ===
    glow_purple: str = "0 0 40px rgba(168, 85, 247, 0.15)"
    glow_cyan: str = "0 0 40px rgba(6, 182, 212, 0.15)"
    glow_green: str = "0 0 20px rgba(16, 185, 129, 0.3)"
    glow_amber: str = "0 0 20px rgba(245, 158, 11, 0.3)"
    glow_red: str = "0 0 20px rgba(239, 68, 68, 0.3)"

    # === Inset ===
    inset_highlight: str = "inset 0 1px 0 rgba(255, 255, 255, 0.08)"


# =============================================================================
# TRANSITION TOKENS
# =============================================================================

@dataclass(frozen=True)
class TransitionTokens:
    """Transition timing presets."""

    fast: str = "150ms ease"
    normal: str = "200ms ease"
    slow: str = "300ms ease"
    smooth: str = "280ms cubic-bezier(0.4, 0, 0.2, 1)"


# =============================================================================
# SINGLETON TOKEN INSTANCES
# =============================================================================

@lru_cache(maxsize=1)
def _get_color_tokens() -> ColorTokens:
    return ColorTokens()


@lru_cache(maxsize=1)
def _get_typography_tokens() -> TypographyTokens:
    return TypographyTokens()


@lru_cache(maxsize=1)
def _get_spacing_tokens() -> SpacingTokens:
    return SpacingTokens()


@lru_cache(maxsize=1)
def _get_radius_tokens() -> RadiusTokens:
    return RadiusTokens()


@lru_cache(maxsize=1)
def _get_shadow_tokens() -> ShadowTokens:
    return ShadowTokens()


@lru_cache(maxsize=1)
def _get_transition_tokens() -> TransitionTokens:
    return TransitionTokens()


# =============================================================================
# PUBLIC API
# =============================================================================

# Singleton token instances for direct import
colors = _get_color_tokens()
typography = _get_typography_tokens()
spacing = _get_spacing_tokens()
radius = _get_radius_tokens()
shadows = _get_shadow_tokens()
transitions = _get_transition_tokens()


def get_status_color(status: str) -> str:
    """Get foreground color for a status value."""
    return colors.get_status_color(status)


def get_status_bg(status: str) -> str:
    """Get background color for a status value."""
    return colors.get_status_bg(status)


def get_domain_color(domain: str) -> str:
    """Get color for a domain/pillar category."""
    return colors.get_domain_color(domain)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Token instances
    "colors",
    "typography",
    "spacing",
    "radius",
    "shadows",
    "transitions",
    # Token classes (for type hints)
    "ColorTokens",
    "TypographyTokens",
    "SpacingTokens",
    "RadiusTokens",
    "ShadowTokens",
    "TransitionTokens",
    # Helper functions
    "get_status_color",
    "get_status_bg",
    "get_domain_color",
    "get_gradient",
    "hex_to_rgba",
    "get_chart_layout_config",
]
