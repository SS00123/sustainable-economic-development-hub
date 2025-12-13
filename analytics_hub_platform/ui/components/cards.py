"""
Reusable Card Components
Sustainable Economic Development Analytics Hub
Ministry of Economy and Planning

This module provides reusable card components that use the theme
as the single source of truth for styling.
"""

from typing import Optional, Union
import streamlit as st
from analytics_hub_platform.config.theme import get_theme
from analytics_hub_platform.utils.accessibility import calculate_contrast_ratio


def render_kpi_card(
    label: str,
    value: Union[str, float, int, None],
    delta: Optional[float] = None,
    delta_suffix: str = "%",
    status: str = "neutral",
    unit: str = "",
    higher_is_better: bool = True,
    show_trend: bool = True,
    height: int = 110
) -> None:
    """
    Render a compact, modern KPI card with accessibility support.
    
    Args:
        label: KPI label/name
        value: Current value (None displays as "N/A")
        delta: Change from previous period
        delta_suffix: Suffix for delta (e.g., "%", "pts")
        status: Status color ("green", "amber", "red", "neutral")
        unit: Unit suffix for the value
        higher_is_better: Whether higher values are better
        show_trend: Whether to show trend arrow
        height: Card height in pixels
    """
    theme = get_theme()
    
    # Format value - handle None safely
    if value is None:
        display_value = "N/A"
    elif isinstance(value, (int, float)):
        if isinstance(value, float):
            if abs(value) >= 1000:
                display_value = f"{value:,.0f}"
            else:
                display_value = f"{value:,.1f}"
        else:
            display_value = f"{value:,}"
    else:
        try:
            float_val = float(value)
            display_value = f"{float_val:,.1f}"
        except (ValueError, TypeError):
            display_value = str(value)
    
    # Get status colors
    status_colors = {
        "green": ("#059669", "#ecfdf5", "#d1fae5"),
        "amber": ("#d97706", "#fffbeb", "#fef3c7"),
        "red": ("#dc2626", "#fef2f2", "#fee2e2"),
        "neutral": ("#64748b", "#f8fafc", "#f1f5f9"),
    }
    text_color, bg_color, border_color = status_colors.get(status, status_colors["neutral"])
    
    # Delta formatting
    delta_html = ""
    if delta is not None and show_trend:
        delta_positive = delta > 0
        is_good = (delta_positive and higher_is_better) or (not delta_positive and not higher_is_better)
        
        arrow = "↑" if delta_positive else "↓"
        delta_color = "#059669" if is_good else "#dc2626"
        delta_value = f"+{delta:.1f}" if delta > 0 else f"{delta:.1f}"
        
        delta_html = f"""
        <div style="
            display: inline-flex;
            align-items: center;
            gap: 3px;
            background: {'#ecfdf5' if is_good else '#fef2f2'};
            color: {delta_color};
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 600;
            margin-top: 6px;
        ">{arrow} {delta_value}{delta_suffix}</div>
        """
    
    card_html = f"""
    <div style="
        background: white;
        border: 1px solid #e2e8f0;
        border-left: 3px solid {text_color};
        border-radius: 8px;
        padding: 14px 16px;
        min-height: {height - 10}px;
    ">
        <div style="
            font-size: 11px;
            color: #64748b;
            text-transform: uppercase;
            letter-spacing: 0.3px;
            margin-bottom: 6px;
            font-weight: 500;
        ">{label}</div>
        <div style="
            font-size: 22px;
            font-weight: 700;
            color: #0f172a;
            line-height: 1.1;
        ">{display_value}<span style="font-size: 13px; color: #94a3b8; font-weight: 500; margin-left: 3px;">{unit}</span></div>
        {delta_html}
    </div>
    """
    
    st.components.v1.html(card_html, height=height)


def render_status_pill(
    status: str,
    label: Optional[str] = None,
    size: str = "medium"
) -> None:
    """
    Render a status pill/badge using theme colors.
    
    Args:
        status: Status value ("green", "amber", "red", "success", "warning", "error")
        label: Optional custom label (defaults to status name)
        size: Pill size ("small", "medium", "large")
    """
    theme = get_theme()
    
    # Status configuration
    status_config = {
        "green": {"label": "On Track", "icon": "✓", "color": theme.colors.status_green, "bg": theme.colors.status_green_bg},
        "amber": {"label": "At Risk", "icon": "⚠", "color": theme.colors.status_amber, "bg": theme.colors.status_amber_bg},
        "red": {"label": "Critical", "icon": "✕", "color": theme.colors.status_red, "bg": theme.colors.status_red_bg},
        "success": {"label": "Success", "icon": "✓", "color": theme.colors.success, "bg": theme.colors.status_green_bg},
        "warning": {"label": "Warning", "icon": "⚠", "color": theme.colors.warning, "bg": theme.colors.status_amber_bg},
        "error": {"label": "Error", "icon": "✕", "color": theme.colors.error, "bg": theme.colors.status_red_bg},
    }
    
    config = status_config.get(status.lower(), {
        "label": status.title(),
        "icon": "●",
        "color": theme.colors.text_muted,
        "bg": theme.colors.surface_alt
    })
    
    # Use custom label if provided
    display_label = label or config["label"]
    
    # Size configuration
    size_config = {
        "small": {"padding": "4px 10px", "font_size": "12px"},
        "medium": {"padding": "6px 12px", "font_size": "13px"},
        "large": {"padding": "8px 16px", "font_size": "14px"},
    }
    
    size_style = size_config.get(size, size_config["medium"])
    
    pill_html = f"""
    <span style="
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: {size_style['padding']};
        border-radius: 999px;
        background-color: {config['bg']};
        color: {config['color']};
        font-weight: {theme.typography.weight_semibold};
        font-size: {size_style['font_size']};
        font-family: {theme.typography.font_family};
        border: 1px solid {config['color']};
    ">
        <span>{config['icon']}</span>
        <span>{display_label}</span>
    </span>
    """
    
    st.markdown(pill_html, unsafe_allow_html=True)


def render_narrative_block(
    title: str,
    content: str,
    icon: str = "💡",
    theme_color: str = "primary"
) -> None:
    """
    Render a narrative/insight block with consistent styling.
    
    Args:
        title: Block title
        content: Narrative content
        icon: Optional emoji icon
        theme_color: Theme color to use ("primary", "secondary", "success", "warning")
    """
    theme = get_theme()
    
    # Color mapping
    color_map = {
        "primary": theme.colors.primary,
        "secondary": theme.colors.secondary,
        "success": theme.colors.success,
        "warning": theme.colors.warning,
        "error": theme.colors.error,
    }
    
    accent_color = color_map.get(theme_color, theme.colors.primary)
    
    narrative_html = f"""
    <div style="
        background: {theme.colors.surface};
        border-left: 4px solid {accent_color};
        border-radius: {theme.border_radius.card}px;
        padding: 16px 20px;
        margin: 16px 0;
        box-shadow: {theme.shadows.sm};
    ">
        <div style="
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 10px;
        ">
            <span style="font-size: 24px;">{icon}</span>
            <h3 style="
                color: {theme.colors.text_primary};
                font-size: {theme.typography.size_lg}px;
                font-weight: {theme.typography.weight_semibold};
                margin: 0;
                font-family: {theme.typography.font_family};
            ">{title}</h3>
        </div>
        <p style="
            color: {theme.colors.text_secondary};
            font-size: {theme.typography.size_base}px;
            line-height: 1.6;
            margin: 0;
            font-family: {theme.typography.font_family};
        ">{content}</p>
    </div>
    """
    
    st.markdown(narrative_html, unsafe_allow_html=True)


def render_metric_comparison_card(
    title: str,
    current_value: Union[float, int],
    previous_value: Union[float, int],
    unit: str = "",
    higher_is_better: bool = True
) -> None:
    """
    Render a card showing metric comparison between two periods.
    
    Args:
        title: Metric title
        current_value: Current period value
        previous_value: Previous period value
        unit: Unit of measurement
        higher_is_better: Whether higher values are better
    """
    theme = get_theme()
    
    # Calculate change
    if previous_value != 0:
        change_pct = ((current_value - previous_value) / abs(previous_value)) * 100
    else:
        change_pct = 0
    
    change_abs = current_value - previous_value
    is_positive = change_abs > 0
    is_good = (is_positive and higher_is_better) or (not is_positive and not higher_is_better)
    
    # Colors
    change_color = theme.colors.status_green if is_good else theme.colors.status_red
    arrow = "↑" if is_positive else "↓"
    
    card_html = f"""
    <div style="
        background: {theme.colors.surface};
        border: 1px solid {theme.colors.border};
        border-radius: {theme.border_radius.card}px;
        padding: {theme.spacing.card_padding}px;
        box-shadow: {theme.shadows.card};
    ">
        <h4 style="
            color: {theme.colors.text_muted};
            font-size: {theme.typography.size_sm}px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin: 0 0 12px 0;
            font-family: {theme.typography.font_family};
        ">{title}</h4>
        
        <div style="
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
        ">
            <div>
                <div style="
                    color: {theme.colors.text_primary};
                    font-size: {theme.typography.kpi_value_size}px;
                    font-weight: {theme.typography.weight_bold};
                    font-family: {theme.typography.font_family};
                ">{current_value:,.2f} {unit}</div>
                <div style="
                    color: {theme.colors.text_muted};
                    font-size: {theme.typography.size_sm}px;
                    font-family: {theme.typography.font_family};
                ">Current</div>
            </div>
            
            <div style="
                text-align: center;
                color: {change_color};
            ">
                <div style="
                    font-size: 28px;
                    line-height: 1;
                ">{arrow}</div>
                <div style="
                    font-size: {theme.typography.size_base}px;
                    font-weight: {theme.typography.weight_semibold};
                    font-family: {theme.typography.font_family};
                ">{change_pct:+.1f}%</div>
            </div>
            
            <div style="text-align: right;">
                <div style="
                    color: {theme.colors.text_secondary};
                    font-size: {theme.typography.size_lg}px;
                    font-weight: {theme.typography.weight_semibold};
                    font-family: {theme.typography.font_family};
                ">{previous_value:,.2f} {unit}</div>
                <div style="
                    color: {theme.colors.text_muted};
                    font-size: {theme.typography.size_sm}px;
                    font-family: {theme.typography.font_family};
                ">Previous</div>
            </div>
        </div>
    </div>
    """
    
    st.markdown(card_html, unsafe_allow_html=True)
