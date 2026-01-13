"""Card components: KPI cards, info banners, and containers."""

from __future__ import annotations

from analytics_hub_platform.app.styles.compat import (
    COLORS,
    RADIUS,
    SHADOWS,
    SPACING,
    TYPOGRAPHY,
    get_gradient,
    get_status_color,
)
from analytics_hub_platform.ui.html import render_html


def card_container(title: str = "", subtitle: str = ""):
    """Context manager for card containers."""

    class CardContext:
        def __enter__(self):
            title_html = (
                f'<div style="font-size: {TYPOGRAPHY.heading4}; font-weight: 600; color: {COLORS.text_primary}; margin-bottom: {SPACING.xs};">{title}</div>'
                if title
                else ""
            )
            subtitle_html = (
                f'<div style="font-size: {TYPOGRAPHY.caption}; color: {COLORS.text_muted}; margin-bottom: {SPACING.md};">{subtitle}</div>'
                if subtitle
                else ""
            )

            render_html(
                f"""
                <div style="
                    background: {COLORS.bg_card};
                    border: 1px solid {COLORS.border};
                    border-radius: {RADIUS.lg};
                    padding: 20px 22px;
                    box-shadow: {SHADOWS.md};
                    margin-bottom: {SPACING.md};
                    backdrop-filter: blur(10px);
                ">
                {title_html}
                {subtitle_html}
            """
            )
            return self

        def __exit__(self, *args):
            render_html("</div>")

    return CardContext()


def metric_card(
    label: str,
    value: str | float,
    delta: float | None = None,
    delta_label: str = "vs prev",
    status: str | None = None,
    icon: str = "",
    unit: str = "",
) -> None:
    """Render a metric card with value, delta, and status."""
    if isinstance(value, float):
        if abs(value) >= 1000000:
            value_str = f"{value / 1000000:.1f}M"
        elif abs(value) >= 1000:
            value_str = f"{value / 1000:.1f}K"
        else:
            value_str = f"{value:.1f}"
    else:
        value_str = str(value)

    if unit:
        value_str = f"{value_str}{unit}"

    delta_html = ""
    if delta is not None:
        delta_color = COLORS.status_green if delta >= 0 else COLORS.status_red
        delta_icon = "▲" if delta >= 0 else "▼"
        delta_html = (
            f'<div style="font-size: {TYPOGRAPHY.caption}; color: {delta_color}; margin-top: {SPACING.xs};">'
            f"{delta_icon} {abs(delta):.1f}% {delta_label}"
            "</div>"
        )

    status_html = ""
    if status and status.lower() in ("green", "amber", "red", "on_track", "at_risk", "off_track"):
        status_color = get_status_color(status)
        status_html = (
            f'<div style="position: absolute; top: 12px; right: 12px; width: 8px; height: 8px; '
            f'border-radius: 50%; background: {status_color}; box-shadow: 0 0 10px {status_color};"></div>'
        )

    icon_html = (
        f'<span style="font-size: 20px; opacity: 0.8;">{icon}</span>' if icon else ""
    )

    html = f"""<div style="background: {COLORS.bg_card}; border: 1px solid {COLORS.border}; border-radius: {RADIUS.md}; padding: 18px 16px; position: relative; transition: all 0.2s ease;">
{status_html}
{icon_html}
<div style="font-size: {TYPOGRAPHY.caption}; color: {COLORS.text_muted}; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: {SPACING.xs};">{label}</div>
<div style="font-size: 26px; font-weight: 700; color: {COLORS.text_primary}; line-height: 1.2;">{value_str}</div>
{delta_html}
</div>"""

    render_html(html)


def status_pills(green: int = 0, amber: int = 0, red: int = 0) -> None:
    """Render status pill indicators."""
    render_html(
        f"""
        <div style="display: flex; gap: {SPACING.md}; flex-wrap: wrap;">
            <div style="
                background: {COLORS.bg_card};
                border: 1px solid {COLORS.status_green}40;
                border-radius: {RADIUS.md};
                padding: 10px 16px;
                display: flex;
                align-items: center;
                gap: 8px;
            ">
                <div style="
                    width: 8px;
                    height: 8px;
                    border-radius: 50%;
                    background: {COLORS.status_green};
                    box-shadow: 0 0 10px {COLORS.status_green};
                "></div>
                <span style="color: {COLORS.text_secondary}; font-size: {TYPOGRAPHY.body};">
                    <strong>{green}</strong> On Track
                </span>
            </div>
            <div style="
                background: {COLORS.bg_card};
                border: 1px solid {COLORS.status_amber}40;
                border-radius: {RADIUS.md};
                padding: 10px 16px;
                display: flex;
                align-items: center;
                gap: 8px;
            ">
                <div style="
                    width: 8px;
                    height: 8px;
                    border-radius: 50%;
                    background: {COLORS.status_amber};
                    box-shadow: 0 0 10px {COLORS.status_amber};
                "></div>
                <span style="color: {COLORS.text_secondary}; font-size: {TYPOGRAPHY.body};">
                    <strong>{amber}</strong> At Risk
                </span>
            </div>
            <div style="
                background: {COLORS.bg_card};
                border: 1px solid {COLORS.status_red}40;
                border-radius: {RADIUS.md};
                padding: 10px 16px;
                display: flex;
                align-items: center;
                gap: 8px;
            ">
                <div style="
                    width: 8px;
                    height: 8px;
                    border-radius: 50%;
                    background: {COLORS.status_red};
                    box-shadow: 0 0 10px {COLORS.status_red};
                "></div>
                <span style="color: {COLORS.text_secondary}; font-size: {TYPOGRAPHY.body};">
                    <strong>{red}</strong> Off Track
                </span>
            </div>
        </div>
    """
    )


def mini_stat(label: str, value: str, icon: str = "") -> None:
    """Render a compact inline stat."""
    icon_html = f"{icon} " if icon else ""
    render_html(
        f"""
        <div style="
            background: {COLORS.bg_card};
            border-radius: {RADIUS.md};
            padding: 12px 16px;
            text-align: center;
        ">
            <div style="font-size: {TYPOGRAPHY.tiny}; color: {COLORS.text_muted}; text-transform: uppercase; margin-bottom: 4px;">
                {icon_html}{label}
            </div>
            <div style="font-size: 20px; font-weight: 700; color: {COLORS.text_primary};">
                {value}
            </div>
        </div>
    """
    )


def info_banner(message: str, type: str = "info") -> None:
    """Render an informational banner."""
    colors_map = {
        "info": (COLORS.cyan, "ℹ️"),
        "success": (COLORS.status_green, "✓"),
        "warning": (COLORS.status_amber, "⚠️"),
        "error": (COLORS.status_red, "✕"),
    }

    color, icon = colors_map.get(type, colors_map["info"])

    render_html(
        f"""
        <div style="
            background: {get_gradient(color, color, 135)}15;
            border-left: 4px solid {color};
            border-radius: {RADIUS.md};
            padding: 16px 20px;
            margin: {SPACING.md} 0;
            color: {COLORS.text_secondary};
            font-size: {TYPOGRAPHY.body};
        ">
            <strong>{icon}</strong> {message}
        </div>
    """
    )
