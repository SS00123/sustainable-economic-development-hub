"""
Reusable UI Components
Production-grade card, metric, and chart components for consistent styling
"""

import plotly.graph_objects as go
import streamlit as st

from analytics_hub_platform.ui.html import render_html
from analytics_hub_platform.ui.ui_theme import (
    COLORS,
    RADIUS,
    SHADOWS,
    SPACING,
    TYPOGRAPHY,
    get_gradient,
    get_status_color,
)


def initialize_page_session_state() -> None:
    """Initialize common session state variables across all pages."""
    defaults = {
        "year": 2026,
        "quarter": 4,
        "region": "all",
        "language": "en",
        "user_role": "EXECUTIVE",
        "theme": "dark",
        "initialized": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def render_page_header(title: str, subtitle: str, icon: str = "") -> None:
    """
    Render consistent page header with gradient background.
    
    Args:
        title: Page title
        subtitle: Page subtitle/description
        icon: Optional emoji icon
    """
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


def page_container(content_func):
    """
    Wrapper to create consistent page layout with max-width and proper alignment.
    
    Args:
        content_func: Function that renders page content
    """
    render_html(
        """
        <style>
        .main .block-container {
            max-width: 1440px;
            padding-left: 2rem;
            padding-right: 2rem;
        }
        </style>
        """
    )
    content_func()


def section_header(title: str, subtitle: str = "", icon: str = "") -> None:
    """
    Render a section header with title and optional subtitle

    Args:
        title: Section title
        subtitle: Optional subtitle/description
        icon: Optional emoji/icon
    """
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


def card_container(title: str = "", subtitle: str = ""):
    """
    Context manager for card containers

    Args:
        title: Card title
        subtitle: Card subtitle
    """

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
    """
    Render a metric card with value, delta, and status

    Args:
        label: Metric label
        value: Main metric value
        delta: Change percentage
        delta_label: Label for delta
        status: Status indicator (green/amber/red)
        icon: Optional icon
        unit: Unit suffix for value
    """
    # Format value
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

    # Delta HTML
    delta_html = ""
    if delta is not None:
        delta_color = COLORS.status_green if delta >= 0 else COLORS.status_red
        delta_icon = "▲" if delta >= 0 else "▼"
        delta_html = f'<div style="font-size: {TYPOGRAPHY.caption}; color: {delta_color}; margin-top: {SPACING.xs};">{delta_icon} {abs(delta):.1f}% {delta_label}</div>'

    # Status pill - only show for actual status values (green/amber/red), not neutral
    status_html = ""
    if status and status.lower() in ("green", "amber", "red", "on_track", "at_risk", "off_track"):
        status_color = get_status_color(status)
        status_html = f'<div style="position: absolute; top: 12px; right: 12px; width: 8px; height: 8px; border-radius: 50%; background: {status_color}; box-shadow: 0 0 10px {status_color};"></div>'

    icon_html = f'<span style="font-size: 20px; opacity: 0.8;">{icon}</span>' if icon else ""

    # Build compact HTML
    html = f"""<div style="background: {COLORS.bg_card}; border: 1px solid {COLORS.border}; border-radius: {RADIUS.md}; padding: 18px 16px; position: relative; transition: all 0.2s ease;">
{status_html}
{icon_html}
<div style="font-size: {TYPOGRAPHY.caption}; color: {COLORS.text_muted}; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: {SPACING.xs};">{label}</div>
<div style="font-size: 26px; font-weight: 700; color: {COLORS.text_primary}; line-height: 1.2;">{value_str}</div>
{delta_html}
</div>"""

    render_html(html)


def status_pills(green: int = 0, amber: int = 0, red: int = 0) -> None:
    """
    Render status pill indicators

    Args:
        green: Count of green status items
        amber: Count of amber status items
        red: Count of red status items
    """
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


def apply_chart_theme(fig: go.Figure, height: int = 400) -> go.Figure:
    """
    Apply consistent dark theme styling to Plotly charts

    Args:
        fig: Plotly figure
        height: Chart height in pixels

    Returns:
        Styled figure
    """
    fig.update_layout(
        height=height,
        margin={"l": 18, "r": 16, "t": 22, "b": 18},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": COLORS.text_muted, "size": 12},
        legend={
            "orientation": "h",
            "yanchor": "top",
            "y": 1.12,
            "xanchor": "center",
            "x": 0.5,
            "bgcolor": COLORS.bg_card,
            "bordercolor": COLORS.border_light,
            "borderwidth": 1,
            "font": {"color": COLORS.text_muted, "size": 11},
        },
        xaxis={
            "showgrid": True,
            "gridcolor": "rgba(255,255,255,0.05)",
            "zeroline": False,
            "tickfont": {"color": COLORS.text_muted, "size": 11},
            "title": {"font": {"color": COLORS.text_muted, "size": 12}},
            "linecolor": "rgba(255,255,255,0.10)",
            "mirror": False,
        },
        yaxis={
            "showgrid": True,
            "gridcolor": "rgba(255,255,255,0.07)",
            "zeroline": False,
            "tickfont": {"color": COLORS.text_muted, "size": 11},
            "title": {"font": {"color": COLORS.text_muted, "size": 12}},
            "linecolor": "rgba(255,255,255,0.10)",
            "mirror": False,
        },
    )
    return fig


def mini_stat(label: str, value: str, icon: str = "") -> None:
    """
    Render a compact inline stat

    Args:
        label: Stat label
        value: Stat value
        icon: Optional icon
    """
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
    """
    Render an informational banner

    Args:
        message: Banner message
        type: Banner type (info/success/warning/error)
    """
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


def spacer(size: str = "md") -> None:
    """Add vertical spacing"""
    size_map = {
        "xs": "4px",
        "sm": "8px",
        "md": "16px",
        "lg": "24px",
        "xl": "32px",
    }
    height = size_map.get(size, "16px")
    render_html(f'<div style="height: {height};"></div>')

