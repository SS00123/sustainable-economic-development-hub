"""Information panel components.

Provides reusable styled information displays:
- Theme info boxes
- Read-only configuration displays
- Gradient accent boxes

Usage:
    from analytics_hub_platform.app.components.info_panels import (
        render_theme_info_box,
        render_config_display,
        render_gradient_info_box,
    )
"""

from __future__ import annotations

from analytics_hub_platform.app.styles.tokens import (
    colors,
    spacing,
    radius,
    typography,
)
from analytics_hub_platform.ui.html import render_html


def render_theme_info_box(
    theme_name: str = "Dark Theme",
    theme_icon: str = "🌙",
    description: str = "Professional dark theme optimized for executive dashboards",
) -> None:
    """Render a themed info box showing current theme.

    Args:
        theme_name: Name of the current theme
        theme_icon: Icon to display
        description: Theme description
    """
    render_html(f"""
        <div style="
            background: linear-gradient(135deg, {colors.accent_purple}25, {colors.accent_primary}15);
            border: 1px solid {colors.accent_purple}50;
            border-radius: {radius.md};
            padding: {spacing.md};
            margin-top: {spacing.sm};
        ">
            <div style="font-size: {typography.small}; color: {colors.text_muted}; margin-bottom: {spacing.xs};">Theme</div>
            <div style="font-size: {typography.h4}; font-weight: {typography.weight_semibold}; color: {colors.text_primary};">
                {theme_icon} {theme_name}
            </div>
            <div style="font-size: {typography.small}; color: {colors.text_subtle}; margin-top: {spacing.xs};">
                {description}
            </div>
        </div>
    """)


def render_config_display(
    label: str,
    value: str,
    description: str | None = None,
    icon: str | None = None,
) -> None:
    """Render a read-only configuration value display.

    Args:
        label: Label for the config item
        value: Current value
        description: Optional description text
        icon: Optional icon to display
    """
    icon_html = f'<span style="margin-right: {spacing.sm};">{icon}</span>' if icon else ""
    description_html = f'<div style="font-size: {typography.small}; color: {colors.text_subtle}; margin-top: {spacing.xs};">{description}</div>' if description else ""

    render_html(f"""
        <div style="
            background: {colors.bg_card};
            border: 1px solid {colors.border};
            border-radius: {radius.md};
            padding: {spacing.md};
            margin-bottom: {spacing.sm};
        ">
            <div style="font-size: {typography.small}; color: {colors.text_muted}; margin-bottom: {spacing.xs};">{label}</div>
            <div style="font-size: {typography.h4}; font-weight: {typography.weight_semibold}; color: {colors.text_primary};">
                {icon_html}{value}
            </div>
            {description_html}
        </div>
    """)


def render_gradient_info_box(
    title: str,
    content: str,
    gradient_from: str | None = None,
    gradient_to: str | None = None,
    icon: str | None = None,
) -> None:
    """Render an info box with gradient background.

    Args:
        title: Box title
        content: Main content text
        gradient_from: Start color of gradient (default: purple)
        gradient_to: End color of gradient (default: cyan)
        icon: Optional icon to display
    """
    gradient_from = gradient_from or colors.accent_purple
    gradient_to = gradient_to or colors.accent_primary
    icon_html = f'<span style="font-size: {typography.h3}; margin-right: {spacing.sm};">{icon}</span>' if icon else ""

    render_html(f"""
        <div style="
            background: linear-gradient(135deg, {gradient_from}20 0%, {gradient_to}10 100%);
            border: 1px solid {gradient_from}30;
            border-radius: {radius.lg};
            padding: {spacing.card_padding};
            margin: {spacing.md} 0;
        ">
            <div style="display: flex; align-items: center; margin-bottom: {spacing.sm};">
                {icon_html}
                <span style="font-size: {typography.h4}; font-weight: {typography.weight_semibold}; color: {colors.text_primary};">{title}</span>
            </div>
            <p style="margin: 0; color: {colors.text_secondary}; font-size: {typography.body}; line-height: 1.5;">
                {content}
            </p>
        </div>
    """)


def render_stat_card(
    label: str,
    value: str,
    sublabel: str | None = None,
) -> None:
    """Render a simple statistics card.

    Args:
        label: Metric label
        value: Metric value
        sublabel: Optional sub-label
    """
    sublabel_html = f'<div style="font-size: {typography.small}; color: {colors.text_subtle}; margin-top: {spacing.xs};">{sublabel}</div>' if sublabel else ""

    render_html(f"""
        <div style="
            background: {colors.bg_card};
            padding: {spacing.md};
            border-radius: {radius.md};
            margin-bottom: {spacing.sm};
        ">
            <div style="font-size: {typography.small}; color: {colors.text_muted};">{label}</div>
            <div style="font-size: {typography.h4}; font-weight: {typography.weight_bold}; color: {colors.text_primary};">{value}</div>
            {sublabel_html}
        </div>
    """)


__all__ = [
    "render_theme_info_box",
    "render_config_display",
    "render_gradient_info_box",
    "render_stat_card",
]
