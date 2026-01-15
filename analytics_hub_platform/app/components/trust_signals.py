"""Trust signal components for data credibility indicators.

Provides consistent rendering of:
- Data freshness indicators
- Data source attribution
- Confidence/quality badges
- Timestamp displays

Usage:
    from analytics_hub_platform.app.components.trust_signals import (
        render_data_freshness,
        render_data_source,
        render_confidence_badge,
        render_trust_bar,
    )
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from analytics_hub_platform.app.styles.tokens import (
    colors,
    typography,
    spacing,
    radius,
)
from analytics_hub_platform.ui.html import render_html


# =============================================================================
# DATA FRESHNESS INDICATOR
# =============================================================================

def render_data_freshness(
    last_updated: str | datetime | None = None,
    max_age_hours: int = 24,
    show_live_dot: bool = True,
    compact: bool = False,
) -> None:
    """Render a data freshness indicator.

    Shows when data was last updated with visual status:
    - Green: Fresh (within max_age_hours)
    - Amber: Stale (1-3x max_age_hours)
    - Red: Outdated (>3x max_age_hours)

    Args:
        last_updated: Timestamp of last data update
        max_age_hours: Hours before data is considered stale
        show_live_dot: Whether to show animated "live" dot
        compact: Use compact layout for inline display
    """
    if last_updated is None:
        last_updated = datetime.now()
    elif isinstance(last_updated, str):
        try:
            last_updated = datetime.fromisoformat(last_updated)
        except ValueError:
            last_updated = datetime.now()

    # Calculate age and status
    age_hours = (datetime.now() - last_updated).total_seconds() / 3600

    if age_hours <= max_age_hours:
        status_color = colors.status_green
        status_bg = colors.status_green_bg
        status_text = "Live"
    elif age_hours <= max_age_hours * 3:
        status_color = colors.status_amber
        status_bg = colors.status_amber_bg
        status_text = "Recent"
    else:
        status_color = colors.status_red
        status_bg = colors.status_red_bg
        status_text = "Stale"

    formatted_time = last_updated.strftime("%b %d, %Y %H:%M")

    live_dot = ""
    if show_live_dot and age_hours <= max_age_hours:
        live_dot = f"""
            <span style="
                display: inline-block;
                width: 8px;
                height: 8px;
                border-radius: 50%;
                background: {status_color};
                box-shadow: 0 0 8px {status_color};
                animation: pulse-live 2s ease-in-out infinite;
                margin-right: 6px;
            "></span>
        """

    if compact:
        render_html(f"""
            <style>
                @keyframes pulse-live {{
                    0%, 100% {{ opacity: 1; transform: scale(1); }}
                    50% {{ opacity: 0.6; transform: scale(0.9); }}
                }}
            </style>
            <span style="
                display: inline-flex;
                align-items: center;
                gap: 4px;
                font-size: {typography.small};
                color: {colors.text_muted};
            ">
                {live_dot}
                <span style="color: {status_color}; font-weight: 600;">{status_text}</span>
                <span>• {formatted_time}</span>
            </span>
        """)
    else:
        render_html(f"""
            <style>
                @keyframes pulse-live {{
                    0%, 100% {{ opacity: 1; transform: scale(1); }}
                    50% {{ opacity: 0.6; transform: scale(0.9); }}
                }}
            </style>
            <div style="
                display: inline-flex;
                align-items: center;
                gap: 8px;
                background: {status_bg};
                border: 1px solid {status_color}30;
                padding: 6px 14px;
                border-radius: {radius.badge};
                font-size: {typography.caption};
            ">
                {live_dot}
                <span style="color: {status_color}; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">
                    {status_text}
                </span>
                <span style="color: {colors.text_muted};">|</span>
                <span style="color: {colors.text_secondary};">
                    🕐 {formatted_time}
                </span>
            </div>
        """)


# =============================================================================
# DATA SOURCE ATTRIBUTION
# =============================================================================

def render_data_source(
    source: str,
    url: str | None = None,
    compact: bool = False,
) -> None:
    """Render a data source attribution.

    Args:
        source: Name of data source (e.g., "GASTAT", "Ministry of Economy")
        url: Optional URL link to source
        compact: Use compact inline layout
    """
    source_content = source
    if url:
        source_content = f'<a href="{url}" target="_blank" style="color: {colors.accent_primary}; text-decoration: none;">{source}</a>'

    if compact:
        render_html(f"""
            <span style="font-size: {typography.small}; color: {colors.text_muted};">
                📊 Source: {source_content}
            </span>
        """)
    else:
        render_html(f"""
            <div style="
                display: inline-flex;
                align-items: center;
                gap: 8px;
                font-size: {typography.caption};
                color: {colors.text_secondary};
            ">
                <span>📊</span>
                <span>Source:</span>
                <span style="font-weight: 500;">{source_content}</span>
            </div>
        """)


# =============================================================================
# CONFIDENCE / QUALITY BADGE
# =============================================================================

def render_confidence_badge(
    confidence: float,
    label: str = "Confidence",
    show_percentage: bool = True,
) -> None:
    """Render a confidence/quality score badge.

    Args:
        confidence: Confidence score 0-1 (or 0-100)
        label: Label text
        show_percentage: Show as percentage (vs decimal)
    """
    # Normalize to 0-1
    if confidence > 1:
        confidence = confidence / 100

    # Determine color based on confidence level
    if confidence >= 0.8:
        badge_color = colors.status_green
        badge_bg = colors.status_green_bg
    elif confidence >= 0.6:
        badge_color = colors.status_amber
        badge_bg = colors.status_amber_bg
    else:
        badge_color = colors.status_red
        badge_bg = colors.status_red_bg

    display_value = f"{confidence * 100:.0f}%" if show_percentage else f"{confidence:.2f}"

    render_html(f"""
        <div style="
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: {badge_bg};
            border: 1px solid {badge_color}30;
            padding: 4px 12px;
            border-radius: {radius.badge};
            font-size: {typography.caption};
        ">
            <span style="color: {colors.text_muted};">{label}:</span>
            <span style="color: {badge_color}; font-weight: 700;">{display_value}</span>
        </div>
    """)


# =============================================================================
# QUALITY TIER BADGE
# =============================================================================

QualityTier = Literal["high", "medium", "low", "unknown"]

def render_quality_tier(
    tier: QualityTier,
    label: str = "Data Quality",
) -> None:
    """Render a data quality tier badge.

    Args:
        tier: Quality tier (high/medium/low/unknown)
        label: Label text
    """
    tier_config = {
        "high": (colors.status_green, colors.status_green_bg, "✓ High"),
        "medium": (colors.status_amber, colors.status_amber_bg, "◐ Medium"),
        "low": (colors.status_red, colors.status_red_bg, "⚠ Low"),
        "unknown": (colors.text_muted, "rgba(255,255,255,0.05)", "? Unknown"),
    }

    color, bg, text = tier_config.get(tier, tier_config["unknown"])

    render_html(f"""
        <div style="
            display: inline-flex;
            align-items: center;
            gap: 8px;
            font-size: {typography.caption};
        ">
            <span style="color: {colors.text_muted};">{label}:</span>
            <span style="
                background: {bg};
                color: {color};
                padding: 3px 10px;
                border-radius: {radius.sm};
                font-weight: 600;
                font-size: {typography.small};
            ">{text}</span>
        </div>
    """)


# =============================================================================
# COMBINED TRUST BAR
# =============================================================================

def render_trust_bar(
    last_updated: str | datetime | None = None,
    source: str | None = None,
    confidence: float | None = None,
    quality_tier: QualityTier | None = None,
) -> None:
    """Render a complete trust signal bar with all indicators.

    This is the canonical component for showing data credibility.
    Use this on major dashboard sections and data views.

    Args:
        last_updated: Timestamp of last data update
        source: Data source name
        confidence: Confidence score 0-1
        quality_tier: Quality tier (high/medium/low)
    """
    signals = []

    if last_updated:
        if isinstance(last_updated, datetime):
            formatted = last_updated.strftime("%b %d, %Y %H:%M")
        else:
            formatted = str(last_updated)
        signals.append(f'<span style="color: {colors.text_muted};">🕐 Updated: {formatted}</span>')

    if source:
        signals.append(f'<span style="color: {colors.text_muted};">📊 Source: <span style="color: {colors.text_secondary};">{source}</span></span>')

    if confidence is not None:
        if confidence > 1:
            confidence = confidence / 100
        conf_color = colors.status_green if confidence >= 0.8 else (colors.status_amber if confidence >= 0.6 else colors.status_red)
        signals.append(f'<span style="color: {colors.text_muted};">📈 Confidence: <span style="color: {conf_color}; font-weight: 600;">{confidence * 100:.0f}%</span></span>')

    if quality_tier:
        tier_colors = {
            "high": colors.status_green,
            "medium": colors.status_amber,
            "low": colors.status_red,
            "unknown": colors.text_muted,
        }
        tier_labels = {"high": "High", "medium": "Medium", "low": "Low", "unknown": "Unknown"}
        q_color = tier_colors.get(quality_tier, colors.text_muted)
        q_label = tier_labels.get(quality_tier, "Unknown")
        signals.append(f'<span style="color: {colors.text_muted};">✓ Quality: <span style="color: {q_color}; font-weight: 600;">{q_label}</span></span>')

    if not signals:
        return

    separator = f'<span style="color: {colors.border_light}; margin: 0 12px;">|</span>'

    render_html(f"""
        <div style="
            display: flex;
            align-items: center;
            flex-wrap: wrap;
            gap: 8px;
            padding: 10px 16px;
            background: {colors.bg_card};
            border: 1px solid {colors.border};
            border-radius: {radius.md};
            font-size: {typography.caption};
            margin-bottom: {spacing.md};
        ">
            {separator.join(signals)}
        </div>
    """)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "render_data_freshness",
    "render_data_source",
    "render_confidence_badge",
    "render_quality_tier",
    "render_trust_bar",
]
