"""
UI Layout Components
Sustainable Economic Development Analytics Hub
Ministry of Economy and Planning

This module provides reusable layout components for Streamlit pages,
ensuring consistent visual design across the platform.
"""

from typing import Optional, Union, Dict, Any
import streamlit as st

from analytics_hub_platform.config.theme import get_theme
from analytics_hub_platform.config.branding import get_branding


def inject_custom_css() -> None:
    """Inject custom CSS styles into the Streamlit app."""
    theme = get_theme()
    st.markdown(theme.get_streamlit_custom_css(), unsafe_allow_html=True)


def render_header(
    title: str,
    subtitle: Optional[str] = None,
    show_branding: bool = True,
    language: str = "en"
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
    
    st.markdown(header_html, unsafe_allow_html=True)


def render_footer(language: str = "en") -> None:
    """
    Render the page footer with branding.
    
    Args:
        language: Display language
    """
    theme = get_theme()
    branding = get_branding()
    
    footer_text = branding.get_footer(language)
    author_info = branding.get_author_info(language).replace("\n", " | ")
    
    footer_html = f"""
    <div style="
        border-top: 1px solid {theme.colors.divider};
        padding: 24px 0;
        margin-top: 48px;
        text-align: center;
    ">
        <p style="
            color: {theme.colors.text_muted};
            font-size: {theme.typography.size_sm}px;
            margin: 0 0 8px 0;
            font-family: {theme.typography.font_family};
        ">{footer_text}</p>
        <p style="
            color: {theme.colors.text_muted};
            font-size: {theme.typography.size_xs}px;
            margin: 0;
            font-family: {theme.typography.font_family};
        ">Developed by: {author_info}</p>
    </div>
    """
    
    st.markdown(footer_html, unsafe_allow_html=True)


def render_section_header(
    title: str,
    description: Optional[str] = None,
    icon: Optional[str] = None
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
    
    st.markdown(header_html, unsafe_allow_html=True)


def render_kpi_card(
    label: str,
    value: Union[str, float, int],
    delta: Optional[float] = None,
    delta_suffix: str = "%",
    status: str = "neutral",
    unit: str = "",
    higher_is_better: bool = True,
    show_trend: bool = True
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
    
    # Format value
    if isinstance(value, float):
        display_value = f"{value:,.2f}"
    elif isinstance(value, int):
        display_value = f"{value:,}"
    else:
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
        is_good = (delta_positive and higher_is_better) or (not delta_positive and not higher_is_better)
        
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
    
    st.markdown(card_html, unsafe_allow_html=True)


def render_status_badge(status: str, label: Optional[str] = None) -> str:
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
        status.lower(),
        (theme.colors.text_muted, theme.colors.surface_alt, "Unknown")
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
    
    for col, metric in zip(cols, metrics):
        with col:
            render_kpi_card(
                label=metric.get("label", ""),
                value=metric.get("value", 0),
                delta=metric.get("delta"),
                status=metric.get("status", "neutral"),
                unit=metric.get("unit", ""),
                higher_is_better=metric.get("higher_is_better", True),
            )


def render_alert_box(
    message: str,
    alert_type: str = "info",
    icon: Optional[str] = None
) -> None:
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
    
    st.markdown(alert_html, unsafe_allow_html=True)


def render_data_table(
    data: list,
    columns: list,
    title: Optional[str] = None
) -> None:
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
    
    st.markdown(table_html, unsafe_allow_html=True)
