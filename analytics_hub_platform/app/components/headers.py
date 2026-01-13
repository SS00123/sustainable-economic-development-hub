"""Header components."""

from __future__ import annotations

from analytics_hub_platform.app.styles.compat import COLORS, SPACING, TYPOGRAPHY, get_gradient
from analytics_hub_platform.ui.html import render_html


def render_page_header(title: str, subtitle: str, icon: str = "") -> None:
    """Render consistent page header with gradient background."""
    icon_prefix = f"{icon} " if icon else ""
    render_html(
        f"""
        <div style="
            background: linear-gradient(135deg, {COLORS.purple} 0%, {COLORS.cyan} 100%);
            padding: 24px 28px;
            border-radius: 12px;
            margin-bottom: 20px;
        ">
            <h1 style="color: white; margin: 0; font-size: 28px; font-weight: 700;">
                {icon_prefix}{title}
            </h1>
            <p style="color: rgba(255,255,255,0.9); margin: 8px 0 0 0; font-size: 14px;">
                {subtitle}
            </p>
        </div>
    """
    )


def section_header(title: str, subtitle: str = "", icon: str = "") -> None:
    """Render a section header with title and optional subtitle."""
    icon_html = f"{icon} " if icon else ""
    subtitle_html = (
        f'<p style="color: {COLORS.text_muted}; margin: 8px 0 0 0; font-size: {TYPOGRAPHY.body};">{subtitle}</p>'
        if subtitle
        else ""
    )

    render_html(
        f"""
        <div style="
            margin: {SPACING.lg} 0;
            padding-bottom: {SPACING.md};
            border-bottom: 2px solid transparent;
            border-image: {get_gradient()};
            border-image-slice: 1;
        ">
            <h2 style="
                color: {COLORS.text_primary};
                font-size: {TYPOGRAPHY.heading2};
                font-weight: 700;
                margin: 0;
            ">
                {icon_html}{title}
            </h2>
            {subtitle_html}
        </div>
    """
    )
