"""Compatibility tokens.

Provides the legacy token names (`COLORS`, `SPACING`, ...) historically exported
by `analytics_hub_platform.ui.ui_theme`.

New code should prefer `analytics_hub_platform.ui.theme` directly.
"""

from __future__ import annotations

from dataclasses import dataclass

from analytics_hub_platform.ui.theme import (
    colors as _colors,
    get_gradient as _get_gradient,
    radius as _radius,
    shadows as _shadows,
    spacing as _spacing,
    typography as _typography,
)


@dataclass(frozen=True)
class ColorPalette:
    """Legacy-friendly color palette backed by `ui.theme`."""

    purple: str = _colors.purple
    cyan: str = _colors.cyan
    pink: str = _colors.pink
    primary: str = _colors.cyan  # Alias for accent color

    bg_primary: str = _colors.bg_main
    bg_secondary: str = _colors.bg_card_alt
    bg_card: str = _colors.bg_card
    bg_card_hover: str = _colors.bg_hover

    text_primary: str = _colors.text_primary
    text_secondary: str = _colors.text_secondary
    text_muted: str = _colors.text_muted
    text_disabled: str = _colors.text_subtle

    status_green: str = _colors.green
    status_amber: str = _colors.amber
    status_red: str = _colors.red

    border: str = _colors.border
    border_light: str = _colors.border_light
    divider: str = "rgba(255,255,255,0.06)"

    gradient_start: str = _colors.purple
    gradient_end: str = _colors.cyan

    chart_purple: str = _colors.chart_palette[5]
    chart_cyan: str = _colors.chart_palette[0]
    chart_pink: str = _colors.chart_palette[6]
    chart_green: str = _colors.chart_palette[2]
    chart_orange: str = _colors.chart_palette[3]
    chart_blue: str = _colors.chart_palette[1]
    chart_yellow: str = _colors.chart_palette[3]
    chart_indigo: str = _colors.chart_palette[9]


@dataclass(frozen=True)
class Spacing:
    xs: str = _spacing.xs
    sm: str = _spacing.sm
    md: str = _spacing.md
    lg: str = _spacing.lg
    xl: str = _spacing.xl
    xxl: str = _spacing.xxl


@dataclass(frozen=True)
class Typography:
    heading1: str = _typography.size_h1
    heading2: str = _typography.size_h2
    heading3: str = _typography.size_h3
    heading4: str = _typography.size_h4
    body: str = _typography.size_body
    caption: str = _typography.size_caption
    small: str = _typography.size_caption  # Alias for smaller text
    tiny: str = _typography.size_tiny


@dataclass(frozen=True)
class BorderRadius:
    sm: str = _radius.sm
    md: str = _radius.md
    lg: str = _radius.lg
    xl: str = _radius.xl
    full: str = _radius.full


@dataclass(frozen=True)
class Shadows:
    sm: str = _shadows.card_sm
    md: str = _shadows.card
    lg: str = _shadows.card_hover
    xl: str = _shadows.card_hover
    glow_purple: str = _shadows.glow_purple
    glow_cyan: str = _shadows.glow_cyan


COLORS = ColorPalette()
SPACING = Spacing()
TYPOGRAPHY = Typography()
RADIUS = BorderRadius()
SHADOWS = Shadows()


def get_status_color(status: str) -> str:
    return _colors.get_status_color(status)


def get_gradient(
    start_color: str | None = None, end_color: str | None = None, angle: int = 135
) -> str:
    return _get_gradient(start=start_color, end=end_color, direction=f"{angle}deg")
