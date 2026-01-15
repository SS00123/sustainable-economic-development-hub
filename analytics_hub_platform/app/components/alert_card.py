"""Alert and anomaly card components."""

from __future__ import annotations

from analytics_hub_platform.app.styles.compat import (
    COLORS,
    RADIUS,
    SHADOWS,
    SPACING,
    TYPOGRAPHY,
)
from analytics_hub_platform.ui.html import render_html


def render_alert_card(
    title: str,
    description: str,
    severity: str = "warning",
    kpi_name: str = "",
    period: str = "",
    z_score: float | None = None,
    recommended_action: str = "",
) -> None:
    """Render an alert/anomaly card.

    Args:
        title: Alert title
        description: Alert description
        severity: 'critical', 'warning', or 'info'
        kpi_name: Optional KPI name
        period: Optional period (e.g., "2025 Q4")
        z_score: Optional Z-score value
        recommended_action: Optional action text
    """
    severity_colors = {
        "critical": COLORS.status_red,
        "warning": COLORS.status_amber,
        "info": COLORS.primary,
    }
    severity_icons = {
        "critical": "🔴",
        "warning": "🟡",
        "info": "🔵",
    }

    color = severity_colors.get(severity.lower(), COLORS.status_amber)
    icon = severity_icons.get(severity.lower(), "🟡")

    meta_parts = []
    if kpi_name:
        meta_parts.append(kpi_name)
    if period:
        meta_parts.append(period)
    if z_score is not None:
        meta_parts.append(f"Z-score: {z_score:.2f}")

    meta_html = (
        f'<div style="font-size: {TYPOGRAPHY.small}; color: {COLORS.text_muted}; margin-top: {SPACING.xs};">'
        f'{" • ".join(meta_parts)}</div>'
        if meta_parts
        else ""
    )

    action_html = (
        f'<div style="font-size: {TYPOGRAPHY.caption}; color: {COLORS.primary}; margin-top: {SPACING.sm}; '
        f'padding: {SPACING.xs} {SPACING.sm}; background: rgba(6, 182, 212, 0.1); border-radius: {RADIUS.sm};">'
        f"→ {recommended_action}</div>"
        if recommended_action
        else ""
    )

    render_html(
        f"""
        <div style="
            background: linear-gradient(135deg, {COLORS.bg_card}, {color}08);
            border: 1px solid {color}50;
            border-left: 5px solid {color};
            border-radius: {RADIUS.lg};
            padding: {SPACING.lg};
            margin-bottom: {SPACING.md};
            box-shadow: {SHADOWS.sm}, 0 0 20px {color}15;
            transition: all 200ms ease;
        ">
            <div style="display: flex; align-items: flex-start; gap: {SPACING.md};">
                <span style="font-size: 22px; filter: drop-shadow(0 0 8px {color});">{icon}</span>
                <div style="flex: 1;">
                    <div style="font-size: 15px; font-weight: 600; color: {COLORS.text_primary};">
                        {title}
                    </div>
                    <div style="font-size: 14px; color: {COLORS.text_secondary}; margin-top: {SPACING.sm}; line-height: 1.5;">
                        {description}
                    </div>
                    {meta_html}
                    {action_html}
                </div>
            </div>
        </div>
    """
    )


def render_alert_summary(
    critical: int = 0,
    warning: int = 0,
    normal: int = 0,
) -> None:
    """Render an alert summary strip.

    Args:
        critical: Number of critical alerts
        warning: Number of warning alerts
        normal: Number of normal/info items
    """
    items = []
    if critical > 0:
        items.append(
            f'<span style="color: {COLORS.status_red}; font-weight: 600; padding: 6px 14px; background: {COLORS.status_red}20; border-radius: 20px; border: 1px solid {COLORS.status_red}40;">🔴 {critical} Critical</span>'
        )
    if warning > 0:
        items.append(
            f'<span style="color: {COLORS.status_amber}; font-weight: 600; padding: 6px 14px; background: {COLORS.status_amber}20; border-radius: 20px; border: 1px solid {COLORS.status_amber}40;">🟡 {warning} Warning</span>'
        )
    if normal > 0:
        items.append(
            f'<span style="color: {COLORS.status_green}; font-weight: 600; padding: 6px 14px; background: {COLORS.status_green}20; border-radius: 20px; border: 1px solid {COLORS.status_green}40;">🟢 {normal} Normal</span>'
        )

    if not items:
        items.append(
            f'<span style="color: {COLORS.text_muted};">No alerts</span>'
        )

    render_html(
        f"""
        <div style="
            display: flex;
            gap: {SPACING.lg};
            padding: {SPACING.sm} {SPACING.md};
            background: {COLORS.bg_card};
            border-radius: {RADIUS.md};
            margin-bottom: {SPACING.md};
            font-size: {TYPOGRAPHY.body};
        ">
            {' '.join(items)}
        </div>
    """
    )


__all__ = [
    "render_alert_card",
    "render_alert_summary",
]
