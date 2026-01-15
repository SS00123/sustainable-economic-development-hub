"""Anomaly and alert display components.

Provides consistent rendering for:
- Anomaly cards with severity indicators
- Alert summaries
- All-clear notifications

Usage:
    from analytics_hub_platform.app.components.anomaly_display import (
        render_anomaly_card,
        render_anomaly_list,
        render_all_clear,
    )
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from analytics_hub_platform.app.styles.tokens import (
    colors,
    spacing,
    radius,
    typography,
)
from analytics_hub_platform.ui.html import render_html


class Severity(str, Enum):
    """Anomaly severity levels."""
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"


@dataclass
class AnomalyInfo:
    """Data class for anomaly display."""
    kpi_id: str
    year: int
    quarter: int
    description: str
    severity: Severity | str
    value: float | None = None
    expected: float | None = None


def render_anomaly_card(
    kpi_id: str,
    year: int,
    quarter: int,
    description: str,
    severity: Severity | str,
    value: float | None = None,
    expected: float | None = None,
) -> None:
    """Render a single anomaly card with severity indicator.

    Args:
        kpi_id: The KPI identifier
        year: Year of the anomaly
        quarter: Quarter of the anomaly
        description: Description of the anomaly
        severity: Severity level (critical, warning, info)
        value: Optional actual value
        expected: Optional expected value
    """
    # Normalize severity
    severity_str = severity.value if isinstance(severity, Enum) else str(severity).lower()

    # Map severity to colors and icons
    severity_config = {
        "critical": {
            "color": colors.status_red,
            "icon": "🔴",
            "label": "CRITICAL",
        },
        "warning": {
            "color": colors.status_amber,
            "icon": "🟡",
            "label": "WARNING",
        },
        "info": {
            "color": colors.accent_primary,
            "icon": "🔵",
            "label": "INFO",
        },
    }

    config = severity_config.get(severity_str, severity_config["info"])
    severity_color = config["color"]
    severity_icon = config["icon"]
    severity_label = config["label"]

    display_name = kpi_id.replace("_", " ").title()

    render_html(f"""
        <div style="
            background: {colors.bg_card};
            border-left: 4px solid {severity_color};
            padding: {spacing.card_padding};
            margin: {spacing.sm} 0;
            border-radius: 0 {radius.lg} {radius.lg} 0;
        ">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: {spacing.sm};">
                <div style="display: flex; align-items: center; gap: {spacing.sm};">
                    <span style="font-size: {typography.h4};">{severity_icon}</span>
                    <span style="font-weight: {typography.weight_bold}; font-size: {typography.body}; color: {colors.text_primary};">{display_name}</span>
                    <span style="
                        background: {severity_color};
                        color: white;
                        padding: 2px {spacing.sm};
                        border-radius: {radius.xs};
                        font-size: {typography.small};
                        font-weight: {typography.weight_semibold};
                    ">{severity_label}</span>
                </div>
                <span style="color: {colors.text_muted}; font-size: {typography.caption}; font-weight: {typography.weight_medium};">Q{quarter} {year}</span>
            </div>
            <p style="margin: {spacing.sm} 0 {spacing.md} 0; color: {colors.text_secondary}; font-size: {typography.body}; line-height: 1.5;">{description}</p>
        </div>
    """)


def render_anomaly_list(
    anomalies: list,
    max_display: int = 5,
    sort_by_severity: bool = True,
) -> None:
    """Render a list of anomaly cards.

    Args:
        anomalies: List of anomaly objects (must have kpi_id, year, quarter, description, severity)
        max_display: Maximum number of anomalies to display
        sort_by_severity: Whether to sort by severity (critical first)
    """
    if not anomalies:
        render_all_clear()
        return

    # Sort by severity and recency
    if sort_by_severity:
        def severity_key(a):
            sev = a.severity.value if hasattr(a.severity, 'value') else str(a.severity)
            sev_order = {"critical": 0, "warning": 1, "info": 2}.get(sev.lower(), 3)
            return (sev_order, -a.year, -a.quarter)

        sorted_anomalies = sorted(anomalies, key=severity_key)
    else:
        sorted_anomalies = anomalies

    for anomaly in sorted_anomalies[:max_display]:
        severity = anomaly.severity.value if hasattr(anomaly.severity, 'value') else anomaly.severity
        render_anomaly_card(
            kpi_id=anomaly.kpi_id,
            year=anomaly.year,
            quarter=anomaly.quarter,
            description=anomaly.description,
            severity=severity,
        )


def render_all_clear(
    message: str = "All Systems Normal - No significant anomalies detected.",
) -> None:
    """Render an all-clear notification.

    Args:
        message: Custom message to display
    """
    render_html(f"""
        <div style="
            background: linear-gradient(135deg, {colors.status_green}15 0%, {colors.status_green}05 100%);
            border: 1px solid {colors.status_green}30;
            border-radius: {radius.lg};
            padding: {spacing.card_padding};
            margin: {spacing.md} 0;
        ">
            <p style="margin: 0; color: {colors.text_primary}; font-size: {typography.body};">
                ✅ {message}
            </p>
        </div>
    """)


__all__ = [
    "AnomalyInfo",
    "Severity",
    "render_anomaly_card",
    "render_anomaly_list",
    "render_all_clear",
]
