"""
UI Layout Components
Sustainable Economic Development Analytics Hub
Ministry of Economy and Planning

This module provides reusable layout components for Streamlit pages,
ensuring consistent visual design across the platform.
"""

import streamlit as st

from analytics_hub_platform.config.branding import get_branding
from analytics_hub_platform.config.theme import get_theme
from analytics_hub_platform.ui.html import render_html


def inject_custom_css() -> None:
    """Inject custom CSS styles into the Streamlit app."""
    theme = get_theme()
    render_html(theme.get_streamlit_custom_css())
    # Global aesthetic enhancements shared across all pages
    render_html(
        f"""
        <style>
            /* Import modern font */
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

            /* Global Typography */
            html, body, [class*="css"] {{
                font-family: 'Inter', system-ui, -apple-system, sans-serif !important;
            }}

            /* Page canvas - Deep Space Gradient */
            .stApp {{
                background-color: {theme.colors.bg_deep} !important;
                background-image: 
                    radial-gradient(circle at 15% 50%, rgba(139, 92, 246, 0.08), transparent 25%),
                    radial-gradient(circle at 85% 30%, rgba(6, 182, 212, 0.08), transparent 25%),
                    radial-gradient(circle at 50% 0%, rgba(59, 130, 246, 0.05), transparent 50%) !important;
                background-attachment: fixed !important;
            }}
            
            /* Main container background override */
            .main {{
                background: transparent !important;
            }}

            .block-container {{
                padding-top: 2rem !important;
                padding-bottom: 3rem !important;
                max-width: 1280px !important;
            }}

            /* Glass surfaces with premium border */
            .glass-box {{
                background: rgba(30, 41, 59, 0.7) !important;
                border: 1px solid rgba(255, 255, 255, 0.08) !important;
                box-shadow: 0 4px 24px -1px rgba(0, 0, 0, 0.2) !important;
                border-radius: 16px !important;
                padding: 20px !important;
                backdrop-filter: blur(12px) !important;
                -webkit-backdrop-filter: blur(12px) !important;
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
            }}

            .glass-box:hover {{
                border-color: rgba(255, 255, 255, 0.15) !important;
                box-shadow: 0 8px 32px -4px rgba(0, 0, 0, 0.3) !important;
                transform: translateY(-2px) !important;
            }}

            /* Custom Scrollbar */
            ::-webkit-scrollbar {{
                width: 8px;
                height: 8px;
            }}
            ::-webkit-scrollbar-track {{
                background: {theme.colors.bg_deep};
            }}
            ::-webkit-scrollbar-thumb {{
                background: {theme.colors.bg_hover};
                border-radius: 4px;
            }}
            ::-webkit-scrollbar-thumb:hover {{
                background: {theme.colors.text_muted};
            }}

            /* Pills for highlights/filters */
            .pill {{
                display: inline-flex;
                align-items: center;
                gap: 8px;
                padding: 6px 12px;
                border-radius: 8px;
                background: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
                color: {theme.colors.text_secondary};
                font-weight: 500;
                font-size: 0.85rem;
                transition: all 0.2s ease;
            }}
            
            .pill:hover {{
                background: rgba(255, 255, 255, 0.1);
                border-color: rgba(255, 255, 255, 0.2);
                color: {theme.colors.text_primary};
            }}

            /* Inline labels for compact filters */
            .filter-label {{
                font-size: 0.75rem;
                letter-spacing: 0.05em;
                text-transform: uppercase;
                color: {theme.colors.text_muted};
                margin-bottom: 4px;
                font-weight: 600;
            }}

            /* Streamlit Elements Polish */
            
            /* Buttons */
            .stButton > button {{
                border-radius: 8px !important;
                font-weight: 500 !important;
                border: 1px solid rgba(255, 255, 255, 0.1) !important;
                transition: all 0.2s ease !important;
            }}
            
            .stButton > button:hover {{
                transform: translateY(-1px);
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
            }}

            /* Inputs & Selects */
            .stTextInput > div > div, .stSelectbox > div > div {{
                background-color: rgba(30, 41, 59, 0.5) !important;
                border-color: rgba(255, 255, 255, 0.1) !important;
                border-radius: 8px !important;
            }}
            
            .stTextInput > div > div:focus-within, .stSelectbox > div > div:focus-within {{
                border-color: {theme.colors.primary} !important;
                box-shadow: 0 0 0 2px rgba(6, 182, 212, 0.2) !important;
            }}

            /* Metrics */
            div[data-testid="stMetricValue"] {{
                font-family: 'Inter', sans-serif !important;
                font-weight: 600 !important;
            }}

            /* Soft entrance animations */
            @keyframes fadeUp {{
                0% {{ opacity: 0; transform: translateY(10px); }}
                100% {{ opacity: 1; transform: translateY(0); }}
            }}
            
            .glass-box, .stPlotlyChart, .stMetric, .element-container > div {{
                animation: fadeUp 0.4s cubic-bezier(0.4, 0, 0.2, 1) both;
            }}
            
            /* Stagger columns slightly */
            .stColumn:nth-child(1) > div {{ animation-delay: 0ms; }}
            .stColumn:nth-child(2) > div {{ animation-delay: 50ms; }}
            .stColumn:nth-child(3) > div {{ animation-delay: 100ms; }}
            .stColumn:nth-child(4) > div {{ animation-delay: 150ms; }}

            /* Section divider accent */
            hr {{
                border: none;
                height: 1px;
                background: linear-gradient(90deg, transparent, {theme.colors.secondary}, transparent);
            }}

        </style>
        """,
    )


def render_header(
    title: str, subtitle: str | None = None, show_branding: bool = True, language: str = "en"
) -> None:
    """
    Render the page header with title and optional subtitle.

    Args:
        title: Page title
        subtitle: Optional subtitle or description
        show_branding: Whether to show platform branding
        language: Display language
    """
    theme = get_theme()
    branding = get_branding()

    # Header container
    header_html = f"""
        <div style="
            background: linear-gradient(135deg, {theme.colors.primary} 0%, {theme.colors.secondary} 100%);
            padding: 24px 32px;
            border-radius: 12px;
            margin-bottom: 24px;
            box-shadow: {theme.shadows.md};
        ">
            <h1 style="
                color: {theme.colors.text_inverse};
                margin: 0;
                font-size: {theme.typography.page_title_size}px;
                font-weight: {theme.typography.weight_bold};
                font-family: {theme.typography.font_family};
            ">{title}</h1>
        """

    if subtitle:
        header_html += f"""
        <p style="
            color: rgba(255, 255, 255, 0.85);
            margin: 8px 0 0 0;
            font-size: {theme.typography.size_base}px;
            font-family: {theme.typography.font_family};
        ">{subtitle}</p>
        """

    if show_branding:
        platform_name = branding.get_platform_title(language)
        header_html += f"""
        <p style="
            color: rgba(255, 255, 255, 0.7);
            margin: 12px 0 0 0;
            font-size: {theme.typography.size_sm}px;
            font-family: {theme.typography.font_family};
        ">{platform_name}</p>
        """

    header_html += "</div>"

    # Use components.html to ensure HTML is rendered without escaping
    st.components.v1.html(header_html, height=160)


def render_footer(language: str = "en") -> None:
    """
    Render the page footer with branding.

    Args:
        language: Display language
    """
    footer_html = """
    <div style="position: relative; z-index: 2; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 24px; margin-top: 48px;">
        <!-- Left: Branding -->
        <div style="display: flex; align-items: center; gap: 16px;">
            <div style="
                width: 48px;
                height: 48px;
                background: linear-gradient(145deg, rgba(168, 85, 247, 0.8), rgba(34, 211, 238, 0.6));
                border-radius: 14px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 24px;
                box-shadow: 0 8px 24px rgba(168, 85, 247, 0.3);
            ">📊</div>
            <div>
                <div style="font-size: 14px; font-weight: 700; color: rgba(255,255,255,0.92);">
                    Sustainable Economic Development
                </div>
                <div style="font-size: 12px; color: rgba(255,255,255,0.5);">
                    Ministry of Economy and Planning
                </div>
            </div>
        </div>

        <!-- Center: Links (hidden on mobile) -->
        <div style="display: flex; gap: 24px; align-items: center;">
            <span style="font-size: 12px; color: rgba(255,255,255,0.4); cursor: pointer; transition: color 200ms;">Documentation</span>
            <span style="font-size: 12px; color: rgba(255,255,255,0.4); cursor: pointer;">API</span>
            <span style="font-size: 12px; color: rgba(255,255,255,0.4); cursor: pointer;">Support</span>
        </div>

        <!-- Right: Developer info -->
        <div style="text-align: right;">
            <div style="font-size: 11px; color: rgba(255,255,255,0.4); margin-bottom: 4px;">
                Developed by
            </div>
            <div style="font-size: 13px; font-weight: 600; color: rgba(255,255,255,0.75);">
                Eng. Sultan Albuqami
            </div>
            <div style="font-size: 11px; color: rgba(168, 85, 247, 0.8);">
                sultan_mutep@hotmail.com
            </div>
        </div>
    </div>

    <!-- Bottom copyright -->
    <div style="
        position: relative;
        z-index: 2;
        margin-top: 24px;
        padding-top: 20px;
        border-top: 1px solid rgba(255,255,255,0.06);
        display: flex;
        align-items: center;
        justify-content: space-between;
        flex-wrap: wrap;
        gap: 12px;
    ">
        <span style="font-size: 11px; color: rgba(255,255,255,0.35);">
            © 2024-2026 Ministry of Economy and Planning. All rights reserved.
        </span>
        <span style="font-size: 11px; color: rgba(255,255,255,0.35);">
            Version 2.0.0 • Built with Streamlit
        </span>
    </div>
    """

    render_html(footer_html)


def render_section_header(
    title: str, description: str | None = None, icon: str | None = None
) -> None:
    """
    Render a section header with optional description and icon.

    Args:
        title: Section title
        description: Optional description text
        icon: Optional emoji or icon
    """
    theme = get_theme()

    icon_html = f'<span style="margin-right: 8px;">{icon}</span>' if icon else ""

    header_html = f"""
    <div style="margin-bottom: 16px;">
        <h2 style="
            color: {theme.colors.text_primary};
            font-size: {theme.typography.section_title_size}px;
            font-weight: {theme.typography.weight_semibold};
            margin: 0;
            padding-bottom: 8px;
            border-bottom: 2px solid {theme.colors.primary};
            font-family: {theme.typography.font_family};
        ">{icon_html}{title}</h2>
    """

    if description:
        header_html += f"""
        <p style="
            color: {theme.colors.text_muted};
            font-size: {theme.typography.size_base}px;
            margin: 8px 0 0 0;
            font-family: {theme.typography.font_family};
        ">{description}</p>
        """

    header_html += "</div>"

    # Use components.html to avoid HTML escaping
    st.components.v1.html(header_html, height=80)


def render_kpi_card(
    label: str,
    value: str | float | int,
    delta: float | None = None,
    delta_suffix: str = "%",
    status: str = "neutral",
    unit: str = "",
    higher_is_better: bool = True,
    show_trend: bool = True,
) -> None:
    """
    Render a styled KPI card.

    Args:
        label: KPI label/name
        value: Current value
        delta: Change from previous period
        delta_suffix: Suffix for delta (e.g., "%", "pts")
        status: Status color ("green", "amber", "red", "neutral")
        unit: Unit suffix for the value
        higher_is_better: Whether higher values are better
        show_trend: Whether to show trend arrow
    """
    theme = get_theme()

    # Format value - handle None and convert to proper type
    if value is None:
        display_value = "0"
    elif isinstance(value, (int, float)):
        if isinstance(value, float):
            display_value = f"{value:,.2f}"
        else:
            display_value = f"{value:,}"
    else:
        # Try to convert to float, fallback to string
        try:
            float_val = float(value)
            display_value = f"{float_val:,.2f}"
        except (ValueError, TypeError):
            display_value = str(value)

    # Determine status colors
    status_colors = {
        "green": (theme.colors.status_green, theme.colors.status_green_bg),
        "amber": (theme.colors.status_amber, theme.colors.status_amber_bg),
        "red": (theme.colors.status_red, theme.colors.status_red_bg),
        "neutral": (theme.colors.text_muted, theme.colors.surface_alt),
    }
    status_color, status_bg = status_colors.get(status.lower(), status_colors["neutral"])

    # Delta formatting
    delta_html = ""
    if delta is not None and show_trend:
        delta_positive = delta > 0
        is_good = (delta_positive and higher_is_better) or (
            not delta_positive and not higher_is_better
        )

        arrow = "↑" if delta_positive else "↓"
        delta_color = theme.colors.status_green if is_good else theme.colors.status_red
        delta_value = f"+{delta:.1f}" if delta > 0 else f"{delta:.1f}"

        delta_html = f"""
        <span style="
            color: {delta_color};
            font-size: {theme.typography.size_sm}px;
            font-weight: {theme.typography.weight_semibold};
            margin-left: 8px;
        ">{arrow} {delta_value}{delta_suffix}</span>
        """

    # Status indicator
    status_indicator = f"""
    <span style="
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        background-color: {status_color};
        margin-right: 8px;
    "></span>
    """

    card_html = f"""
    <div style="
        background: {theme.colors.surface};
        border: 1px solid {theme.colors.border};
        border-radius: {theme.border_radius.card}px;
        padding: {theme.spacing.card_padding}px;
        box-shadow: {theme.shadows.card};
        min-height: 120px;
    ">
        <div style="
            display: flex;
            align-items: center;
            margin-bottom: 8px;
        ">
            {status_indicator}
            <span style="
                color: {theme.colors.text_muted};
                font-size: {theme.typography.kpi_label_size}px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                font-family: {theme.typography.font_family};
            ">{label}</span>
        </div>
        <div style="
            display: flex;
            align-items: baseline;
        ">
            <span style="
                color: {theme.colors.text_primary};
                font-size: {theme.typography.kpi_value_size}px;
                font-weight: {theme.typography.weight_bold};
                font-family: {theme.typography.font_family};
            ">{display_value}</span>
            <span style="
                color: {theme.colors.text_muted};
                font-size: {theme.typography.size_base}px;
                margin-left: 4px;
                font-family: {theme.typography.font_family};
            ">{unit}</span>
            {delta_html}
        </div>
    </div>
    """

    # Use components.html to avoid any escaping issues when rendering HTML
    st.components.v1.html(card_html, height=140)


def render_status_badge(status: str, label: str | None = None) -> str:
    """
    Render a status badge/pill.

    Args:
        status: Status value ("green", "amber", "red")
        label: Optional custom label (defaults to status name)

    Returns:
        HTML string for the badge
    """
    theme = get_theme()

    status_config = {
        "green": (theme.colors.status_green, theme.colors.status_green_bg, "On Track"),
        "amber": (theme.colors.status_amber, theme.colors.status_amber_bg, "At Risk"),
        "red": (theme.colors.status_red, theme.colors.status_red_bg, "Critical"),
    }

    color, bg_color, default_label = status_config.get(
        status.lower(), (theme.colors.text_muted, theme.colors.surface_alt, "Unknown")
    )

    display_label = label or default_label

    return f"""
    <span style="
        background-color: {bg_color};
        color: {color};
        padding: 4px 12px;
        border-radius: 16px;
        font-size: {theme.typography.size_xs}px;
        font-weight: {theme.typography.weight_semibold};
        text-transform: uppercase;
        font-family: {theme.typography.font_family};
    ">{display_label}</span>
    """


def render_metric_row(metrics: list) -> None:
    """
    Render a row of metrics using Streamlit columns.

    Args:
        metrics: List of metric dictionaries with keys:
                 - label, value, delta, status, unit, higher_is_better
    """
    cols = st.columns(len(metrics))

    for col, metric in zip(cols, metrics, strict=False):
        with col:
            render_kpi_card(
                label=metric.get("label", ""),
                value=metric.get("value", 0),
                delta=metric.get("delta"),
                status=metric.get("status", "neutral"),
                unit=metric.get("unit", ""),
                higher_is_better=metric.get("higher_is_better", True),
            )


def render_alert_box(message: str, alert_type: str = "info", icon: str | None = None) -> None:
    """
    Render an alert/notification box.

    Args:
        message: Alert message
        alert_type: Type of alert ("info", "success", "warning", "error")
        icon: Optional icon/emoji
    """
    theme = get_theme()

    type_config = {
        "info": (theme.colors.primary, "#EBF5FF"),
        "success": (theme.colors.status_green, theme.colors.status_green_bg),
        "warning": (theme.colors.status_amber, theme.colors.status_amber_bg),
        "error": (theme.colors.status_red, theme.colors.status_red_bg),
    }

    border_color, bg_color = type_config.get(alert_type, type_config["info"])

    default_icons = {
        "info": "ℹ️",
        "success": "✅",
        "warning": "⚠️",
        "error": "❌",
    }

    display_icon = icon or default_icons.get(alert_type, "")

    alert_html = f"""
    <div style="
        background-color: {bg_color};
        border-left: 4px solid {border_color};
        padding: 16px;
        border-radius: 0 8px 8px 0;
        margin: 16px 0;
    ">
        <span style="margin-right: 8px;">{display_icon}</span>
        <span style="
            color: {theme.colors.text_primary};
            font-size: {theme.typography.size_base}px;
            font-family: {theme.typography.font_family};
        ">{message}</span>
    </div>
    """

    render_html(alert_html)


def render_data_table(data: list, columns: list, title: str | None = None) -> None:
    """
    Render a styled data table.

    Args:
        data: List of dictionaries with row data
        columns: List of column definitions with 'key' and 'label'
        title: Optional table title
    """
    theme = get_theme()

    if title:
        st.markdown(f"**{title}**")

    # Build table HTML
    header_cells = "".join(
        f'<th style="background: {theme.colors.surface_alt}; padding: 12px 16px; text-align: left; font-weight: {theme.typography.weight_semibold}; border-bottom: 2px solid {theme.colors.border};">{col["label"]}</th>'
        for col in columns
    )

    rows_html = ""
    for row in data:
        cells = "".join(
            f'<td style="padding: 12px 16px; border-bottom: 1px solid {theme.colors.border};">{row.get(col["key"], "")}</td>'
            for col in columns
        )
        rows_html += f"<tr>{cells}</tr>"

    table_html = f"""
    <table style="
        width: 100%;
        border-collapse: collapse;
        border: 1px solid {theme.colors.border};
        border-radius: {theme.border_radius.md}px;
        overflow: hidden;
        font-family: {theme.typography.font_family};
        font-size: {theme.typography.size_base}px;
    ">
        <thead>
            <tr>{header_cells}</tr>
        </thead>
        <tbody>
            {rows_html}
        </tbody>
    </table>
    """

    render_html(table_html)

