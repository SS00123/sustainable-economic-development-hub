"""
Dark Theme UI Components
Sustainable Economic Development Analytics Hub
Ministry of Economy and Planning

Reusable UI components for the dark 3D dashboard design.
Matches the provided UI reference with purple/cyan/pink accents.
"""

from __future__ import annotations

from datetime import date, datetime

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from analytics_hub_platform.ui.theme import get_dark_css, get_dark_theme
from analytics_hub_platform.ui.html import render_html


def inject_dark_theme() -> None:
    """Inject the dark theme CSS into the Streamlit app."""
    render_html(get_dark_css())


# =============================================================================
# LAYOUT COMPONENTS
# =============================================================================


def render_sidebar(active: str = "Dashboard") -> None:
    """
    Render a premium left sidebar with glassmorphism, gradient header, and page navigation.
    Uses Streamlit's native page_link for working navigation.

    Args:
        active: The currently active page name
    """
    # Navigation items matching the pages in pages/ directory (ASCII filenames)
    items = [
        ("Dashboard", "📊", "pages/01_Dashboard.py"),
        ("KPIs", "📈", "pages/02_KPIs.py"),
        ("Trends", "📊", "pages/03_Trends.py"),
        ("Data", "📋", "pages/04_Data.py"),
        ("Advanced Analytics", "🧠", "pages/05_Advanced_Analytics.py"),
        ("Settings", "⚙️", "pages/06_Settings.py"),
    ]

    # Inject premium sidebar styling
    render_html(
        """
    <style>
      /* Premium Sidebar Container */
      .sidebar-header-card {
        background: linear-gradient(145deg, rgba(168, 85, 247, 0.95), rgba(139, 92, 246, 0.9), rgba(236, 72, 153, 0.75));
        border-radius: 18px;
        padding: 24px 20px;
        margin-bottom: 20px;
        position: relative;
        overflow: hidden;
        box-shadow: 0 8px 32px rgba(168, 85, 247, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.1);
      }

      .sidebar-header-card::before {
        content: "";
        position: absolute;
        top: -40%;
        right: -25%;
        width: 180px;
        height: 180px;
        background: radial-gradient(circle, rgba(255,255,255,0.25) 0%, transparent 65%);
        border-radius: 50%;
        animation: float-orb-sidebar 8s ease-in-out infinite;
      }

      .sidebar-header-card::after {
        content: "";
        position: absolute;
        bottom: -35%;
        left: -15%;
        width: 140px;
        height: 140px;
        background: radial-gradient(circle, rgba(34, 211, 238, 0.35) 0%, transparent 60%);
        border-radius: 50%;
        animation: float-orb-sidebar 6s ease-in-out infinite reverse;
      }

      @keyframes float-orb-sidebar {
        0%, 100% { transform: translate(0, 0) scale(1); }
        50% { transform: translate(8px, 12px) scale(1.08); }
      }

      .logo-icon {
        font-size: 32px;
        filter: drop-shadow(0 0 14px rgba(255,255,255,0.5));
        position: relative;
        z-index: 2;
      }

      .sidebar-brand {
        font-weight: 800;
        font-size: 16px;
        color: white;
        margin-top: 8px;
        position: relative;
        z-index: 2;
        text-shadow: 0 2px 8px rgba(0,0,0,0.2);
        letter-spacing: -0.3px;
      }

      .sidebar-subtitle {
        font-size: 11px;
        color: rgba(255,255,255,0.8);
        margin-top: 3px;
        position: relative;
        z-index: 2;
      }

      /* Premium User Card */
      .user-card {
        background: linear-gradient(135deg, rgba(30, 35, 64, 0.95), rgba(15, 17, 34, 0.95));
        border: 1px solid rgba(168, 85, 247, 0.2);
        border-radius: 14px;
        padding: 16px;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        gap: 14px;
        box-shadow:
          0 8px 24px rgba(0, 0, 0, 0.3),
          inset 0 1px 0 rgba(255, 255, 255, 0.05);
        transition: all 200ms ease;
      }

      .user-card:hover {
        border-color: rgba(168, 85, 247, 0.35);
        transform: translateY(-2px);
      }

      .user-avatar {
        width: 44px;
        height: 44px;
        border-radius: 14px;
        background: linear-gradient(145deg, rgba(168, 85, 247, 0.85), rgba(34, 211, 238, 0.75));
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 14px;
        color: white;
        box-shadow: 0 6px 18px rgba(168, 85, 247, 0.35);
        position: relative;
      }

      .user-avatar::after {
        content: "";
        position: absolute;
        inset: -3px;
        border-radius: 16px;
        border: 2px solid rgba(168, 85, 247, 0.25);
        animation: pulse-ring-sidebar 3s ease-out infinite;
      }

      @keyframes pulse-ring-sidebar {
        0%, 100% { transform: scale(1); opacity: 0.8; }
        50% { transform: scale(1.08); opacity: 0.4; }
      }

      .user-info { flex: 1; }

      .user-title {
        font-size: 14px;
        font-weight: 600;
        color: rgba(255,255,255,0.95);
        letter-spacing: -0.2px;
      }

      .user-role {
        font-size: 11px;
        color: rgba(255,255,255,0.5);
        margin-top: 2px;
      }

      .user-status {
        width: 10px;
        height: 10px;
        border-radius: 50%;
        background: #10b981;
        box-shadow: 0 0 12px #10b981, 0 0 24px rgba(16, 185, 129, 0.4);
        animation: pulse-status 2s ease-in-out infinite;
      }

      @keyframes pulse-status {
        0%, 100% { transform: scale(1); opacity: 1; }
        50% { transform: scale(1.15); opacity: 0.8; }
      }

      /* Navigation Section Label */
      .nav-section-label {
        font-size: 10px;
        font-weight: 700;
        color: rgba(255,255,255,0.4);
        letter-spacing: 1.5px;
        text-transform: uppercase;
        padding: 10px 6px;
        margin-bottom: 10px;
      }

      /* Style Streamlit page links */
      [data-testid="stPageLink"] {
        background: transparent !important;
        border: 1px solid transparent !important;
        border-radius: 12px !important;
        margin-bottom: 6px !important;
        transition: all 220ms cubic-bezier(0.4, 0, 0.2, 1) !important;
        position: relative;
        overflow: hidden;
      }

      [data-testid="stPageLink"]::before {
        content: "";
        position: absolute;
        left: 0;
        top: 0;
        bottom: 0;
        width: 0;
        background: linear-gradient(90deg, rgba(168, 85, 247, 0.25), transparent);
        transition: width 220ms ease;
        border-radius: 12px;
        pointer-events: none;
      }

      [data-testid="stPageLink"]:hover {
        background: linear-gradient(135deg, rgba(168, 85, 247, 0.15), rgba(34, 211, 238, 0.08)) !important;
        border-color: rgba(168, 85, 247, 0.3) !important;
        transform: translateX(4px);
        box-shadow: 0 4px 16px rgba(168, 85, 247, 0.15);
      }

      [data-testid="stPageLink"]:hover::before {
        width: 100%;
      }

      [data-testid="stPageLink"] p {
        color: rgba(255,255,255,0.65) !important;
        font-size: 13px !important;
        font-weight: 500 !important;
        transition: color 180ms ease !important;
      }

      [data-testid="stPageLink"]:hover p {
        color: rgba(255,255,255,0.98) !important;
      }

      /* Active page styling - Premium */
      .nav-active-indicator {
        background: linear-gradient(135deg, rgba(168, 85, 247, 0.3), rgba(34, 211, 238, 0.18)) !important;
        border: 1px solid rgba(168, 85, 247, 0.45) !important;
        border-radius: 12px !important;
        padding: 12px 16px !important;
        margin-bottom: 6px !important;
        box-shadow: 0 4px 20px rgba(168, 85, 247, 0.2);
        position: relative;
      }

      .nav-active-indicator::before {
        content: "";
        position: absolute;
        left: 0;
        top: 0;
        bottom: 0;
        width: 4px;
        background: linear-gradient(180deg, #a855f7, #22d3ee);
        border-radius: 4px 0 0 4px;
      }

      .nav-active-indicator p {
        color: rgba(255,255,255,0.98) !important;
        font-weight: 600 !important;
      }
    </style>
    """
    )

    # Header card
    render_html(
        """
    <div class="sidebar-header-card">
        <div class="logo-icon">🌱</div>
        <div class="sidebar-brand">Sustainable Analytics</div>
        <div class="sidebar-subtitle">Ministry Dashboard</div>
    </div>
    """
    )

    # User card
    render_html(
        """
    <div class="user-card">
        <div class="user-avatar">ME</div>
        <div class="user-info">
            <div class="user-title">H.E. Minister</div>
            <div class="user-role">Executive View</div>
        </div>
        <div class="user-status"></div>
    </div>
    """
    )

    # Navigation section
    render_html('<div class="nav-section-label">MAIN MENU</div>')

    # Render navigation links using Streamlit's page_link
    for name, icon, page_path in items:
        if name == active:
            # Show active page with special styling (non-clickable)
            render_html(
                f"""
            <div class="nav-active-indicator" style="
                background: linear-gradient(90deg, rgba(34, 211, 238, 0.15), transparent);
                border-left: 3px solid #22d3ee;
                padding: 12px 16px;
                border-radius: 0 8px 8px 0;
                margin-bottom: 8px;
            ">
                <p style="margin: 0; display: flex; align-items: center; gap: 12px; color: #22d3ee; font-weight: 600;">
                    <span style="font-size: 1.1em;">{icon}</span>
                    <span style="letter-spacing: 0.5px;">{name}</span>
                </p>
            </div>
            """
            )
        else:
            # Clickable link to other pages
            st.page_link(page_path, label=f"{icon} {name}", width="stretch")


def render_sticky_header(
    year: int,
    quarter: int,
    region: str,
    language: str,
) -> None:
    """
    Render a sticky header with current filter context.
    """
    render_html(
        f"""
        <style>
            .sticky-header {{
                position: sticky;
                top: 0;
                z-index: 999;
                background: rgba(15, 23, 42, 0.85);
                backdrop-filter: blur(12px);
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
                padding: 12px 24px;
                margin: -16px -24px 24px -24px;
                display: flex;
                align-items: center;
                justify-content: space-between;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
            }}
            .filter-chip {{
                background: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 20px;
                padding: 4px 12px;
                font-size: 12px;
                color: rgba(255, 255, 255, 0.8);
                display: flex;
                align-items: center;
                gap: 6px;
            }}
            .filter-chip strong {{
                color: #fff;
                font-weight: 600;
            }}
            .reset-btn {{
                background: transparent;
                border: 1px solid rgba(239, 68, 68, 0.3);
                color: #fca5a5;
                border-radius: 6px;
                padding: 4px 12px;
                font-size: 12px;
                cursor: pointer;
                transition: all 0.2s;
            }}
            .reset-btn:hover {{
                background: rgba(239, 68, 68, 0.1);
                border-color: rgba(239, 68, 68, 0.5);
            }}
        </style>
        <div class="sticky-header">
            <div style="display: flex; gap: 12px; align-items: center;">
                <span style="font-size: 13px; font-weight: 600; color: rgba(255,255,255,0.5); text-transform: uppercase; letter-spacing: 1px;">Active Context</span>
                <div class="filter-chip">📅 Year: <strong>{year}</strong></div>
                <div class="filter-chip">📊 Quarter: <strong>Q{quarter}</strong></div>
                <div class="filter-chip">🌍 Region: <strong>{region.title()}</strong></div>
                <div class="filter-chip">🗣️ Lang: <strong>{language.upper()}</strong></div>
            </div>
            <!-- Reset button logic would go here if using callbacks, for now just visual -->
        </div>
        """
    )


def render_header(
    title: str = "Overview",
    period_text: str | None = None,
    show_search: bool = True,
    show_icons: bool = True,
) -> None:
    """
    Render the premium top header bar with title, date range, search, and icons.

    Args:
        title: Page title
        period_text: Optional custom period text
        show_search: Whether to show search box
        show_icons: Whether to show icon pills
    """
    if period_text is None:
        now = datetime.now().date()
        start = date(now.year - 6, 1, 1)
        period_text = f"{start.strftime('%b %Y')} – {now.strftime('%b %Y')}"

    c1, c2, c3 = st.columns([0.32, 0.44, 0.24], gap="small")

    with c1:
        render_html(
            f"""
            <div class="topbar" style="
                background: linear-gradient(135deg, rgba(255,255,255,0.05), rgba(255,255,255,0.02));
                border: 1px solid rgba(255,255,255,0.08);
                border-radius: 16px;
                padding: 18px 22px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            ">
              <div class="title" style="
                font-weight: 800;
                font-size: 18px;
                color: rgba(255,255,255,0.95);
                letter-spacing: -0.3px;
              ">{title}</div>
              <div class="daterange" style="
                font-size: 12px;
                color: rgba(255,255,255,0.5);
                margin-top: 4px;
              ">📅 Reporting period: {period_text}</div>
            </div>
            """
        )

    with c2:
        if show_search:
            render_html(
                """
                <div class='topbar' style='
                    padding: 12px 16px;
                    background: linear-gradient(135deg, rgba(255,255,255,0.05), rgba(255,255,255,0.02));
                    border: 1px solid rgba(255,255,255,0.08);
                    border-radius: 16px;
                '>
                """
            )
            st.text_input(
                "Search",
                placeholder="🔍 Search KPIs, regions, policies…",
                label_visibility="collapsed",
                key="header_search",
            )
            render_html("</div>")
        else:
            render_html("<div class='topbar' style='height: 68px;'></div>")

    with c3:
        if show_icons:
            render_html(
                """
                <div class="topbar" style="
                    display: flex;
                    align-items: center;
                    justify-content: flex-end;
                    gap: 12px;
                    height: 68px;
                    background: linear-gradient(135deg, rgba(255,255,255,0.05), rgba(255,255,255,0.02));
                    border: 1px solid rgba(255,255,255,0.08);
                    border-radius: 16px;
                    padding: 0 18px;
                ">
                  <div class="icon-pill" style="
                    width: 40px;
                    height: 40px;
                    border-radius: 12px;
                    background: linear-gradient(135deg, rgba(168, 85, 247, 0.15), rgba(34, 211, 238, 0.1));
                    border: 1px solid rgba(168, 85, 247, 0.25);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 16px;
                    cursor: pointer;
                    transition: all 200ms ease;
                  ">🔔</div>
                  <div class="icon-pill" style="
                    width: 40px;
                    height: 40px;
                    border-radius: 12px;
                    background: linear-gradient(135deg, rgba(168, 85, 247, 0.15), rgba(34, 211, 238, 0.1));
                    border: 1px solid rgba(168, 85, 247, 0.25);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 16px;
                    cursor: pointer;
                    transition: all 200ms ease;
                  ">📧</div>
                  <div class="icon-pill" style="
                    width: 40px;
                    height: 40px;
                    border-radius: 12px;
                    background: linear-gradient(145deg, rgba(168, 85, 247, 0.8), rgba(34, 211, 238, 0.6));
                    border: 1px solid rgba(168, 85, 247, 0.4);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 16px;
                    cursor: pointer;
                    transition: all 200ms ease;
                    box-shadow: 0 4px 16px rgba(168, 85, 247, 0.3);
                  ">👤</div>
                </div>
                """
            )
        else:
            render_html("<div class='topbar' style='height: 68px;'></div>")


# =============================================================================
# CARD COMPONENTS
# =============================================================================


def card_open(
    title: str,
    subtitle: str | None = None,
    right_html: str | None = None,
    accent_color: str | None = None,
    glow: bool = False,
) -> None:
    """
    Open a styled dark card wrapper with premium glassmorphism effect.

    Args:
        title: Card title
        subtitle: Optional subtitle text
        right_html: Optional HTML to render on the right side of header
        accent_color: Optional accent color for left border glow
        glow: Whether to add a subtle glow effect
    """
    subtitle_html = f"<div class='card-sub'>{subtitle}</div>" if subtitle else ""
    right = right_html or ""

    # Build accent/glow styles
    accent_style = ""
    if accent_color:
        accent_style = f"border-left: 3px solid {accent_color}; box-shadow: -4px 0 20px {accent_color}25;"
    if glow:
        accent_style += " box-shadow: 0 0 40px rgba(168, 85, 247, 0.15);"

    render_html(
        f"""
        <div class="dark-card" style="{accent_style}">
          <div style="display:flex; align-items:flex-start; justify-content:space-between; gap:16px; margin-bottom: 16px;">
            <div>
              <div class="card-title">{title}</div>
              {subtitle_html}
            </div>
            <div>{right}</div>
          </div>
        """
    )


def card_close() -> None:
    """Close the styled dark card wrapper."""
    render_html("</div>")


def render_kpi_card(
    title: str,
    value: str | float | int,
    delta: float | None = None,
    unit: str = "",
    subtitle: str = "",
    height: int = 140,
    accent_color: str | None = None,
    icon: str = "",
) -> None:
    """
    Render a premium KPI metric card with glassmorphism dark theme.

    Args:
        title: KPI label/name
        value: Current value
        delta: Change percentage from previous period
        unit: Unit suffix for the value
        subtitle: Additional context text
        height: Card height in pixels
        accent_color: Optional accent color for glow effect
        icon: Optional emoji/icon to display
    """
    theme = get_dark_theme()

    # Format value
    if isinstance(value, float):
        display_value = f"{value:,.1f}" if value < 1000 else f"{value:,.0f}"
    elif isinstance(value, int):
        display_value = f"{value:,}"
    else:
        display_value = str(value)

    # Delta HTML with enhanced styling
    delta_html = ""
    if delta is not None:
        if delta >= 0:
            delta_class = "positive"
            arrow = "↑"
            glow_color = theme.colors.green
        else:
            delta_class = "negative"
            arrow = "↓"
            glow_color = theme.colors.red
        delta_html = f"""
        <div class='delta {delta_class}' style='
            display: inline-flex;
            align-items: center;
            gap: 4px;
            margin-top: 12px;
            box-shadow: 0 0 20px {glow_color}20;
        '>
            <span style="font-size: 14px;">{arrow}</span>
            <span>{abs(delta):.1f}%</span>
        </div>
        """

    # Accent glow effect
    accent_style = ""
    if accent_color:
        accent_style = f"""
            border-left: 3px solid {accent_color};
            box-shadow:
                0 4px 6px rgba(0, 0, 0, 0.1),
                0 20px 50px rgba(0, 0, 0, 0.4),
                -6px 0 30px {accent_color}20,
                inset 0 1px 0 rgba(255, 255, 255, 0.08);
        """

    # Icon display
    icon_html = ""
    if icon:
        icon_html = f"""
        <div style="
            position: absolute;
            top: 16px;
            right: 16px;
            font-size: 28px;
            opacity: 0.4;
            filter: grayscale(20%);
        ">{icon}</div>
        """

    card_html = f"""
    <div class="dark-card" style="min-height: {height - 20}px; position: relative; {accent_style}">
        {icon_html}
        <div class="card-title" style="margin-bottom: 8px;">{title}</div>
        <div style="display: flex; align-items: baseline; flex-wrap: wrap; margin-top: 8px;">
            <span class="card-value" style="
                font-size: 36px;
                font-weight: 800;
                background: linear-gradient(135deg, rgba(255,255,255,0.98), rgba(255,255,255,0.82));
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                letter-spacing: -0.5px;
            ">{display_value}</span>
            <span style="font-size: 14px; color: rgba(255,255,255,0.5); margin-left: 6px; font-weight: 500;">{unit}</span>
        </div>
        {delta_html}
        <div class="card-sub" style="margin-top: 10px; font-size: 12px; line-height: 1.4;">{subtitle}</div>
    </div>
    """
    render_html(card_html)


def render_mini_metric(
    title: str,
    value: str,
    delta: float,
    ring_percent: float,
    subtitle: str = "vs previous period",
    ring_color: str = "#a855f7",
) -> None:
    """
    Render a premium mini metric card with animated ring indicator.

    Args:
        title: Metric title
        value: Display value (e.g., "62.5K")
        delta: Change percentage
        ring_percent: Progress ring percentage (0-100)
        subtitle: Subtitle text
        ring_color: Color for the ring indicator
    """
    theme = get_dark_theme()
    delta_class = "positive" if delta >= 0 else "negative"
    arrow = "↑" if delta >= 0 else "↓"

    right_html = f"""
    <span class='delta {delta_class}' style='font-size: 11px; padding: 3px 10px;'>
        <span style="font-size: 12px;">{arrow}</span> {abs(delta):.1f}%
    </span>
    """
    card_open(title=title, subtitle=subtitle, right_html=right_html, glow=True)

    c1, c2 = st.columns([0.55, 0.45], gap="small")
    with c1:
        render_html(
            f"""
            <div style='margin-top: 4px;'>
                <div class='card-value' style='
                    font-size: 28px;
                    font-weight: 800;
                    background: linear-gradient(135deg, rgba(255,255,255,0.98), rgba(255,255,255,0.8));
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    background-clip: text;
                '>{value}</div>
                <div style='margin-top: 10px; color: rgba(255,255,255,0.4); font-size: 11px; font-weight: 500;'>
                    Updated monthly
                </div>
            </div>
            """
        )
    with c2:
        ring = float(np.clip(ring_percent, 0, 100))
        # Create gradient colors for the ring
        fig = go.Figure(
            data=[
                go.Pie(
                    values=[ring, 100 - ring],
                    hole=0.76,
                    sort=False,
                    direction="clockwise",
                    marker={
                        "colors": [ring_color, "rgba(255,255,255,0.06)"],
                        "line": {"width": 0},
                    },
                    textinfo="none",
                    hoverinfo="skip",
                )
            ]
        )
        fig.update_layout(
            height=110,
            margin={"l": 0, "r": 0, "t": 0, "b": 0},
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            showlegend=False,
            annotations=[
                {
                    "text": f"<b>{ring:.0f}%</b>",
                    "x": 0.5,
                    "y": 0.5,
                    "showarrow": False,
                    "font": {"color": "rgba(255,255,255,0.88)", "size": 14},
                }
            ],
        )
        st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})

    card_close()


# =============================================================================
# CHART COMPONENTS
# =============================================================================


def apply_dark_chart_layout(fig: go.Figure, height: int = 300, show_grid: bool = True) -> go.Figure:
    """
    Apply premium dark theme styling to a Plotly figure.

    Args:
        fig: Plotly figure to style
        height: Chart height in pixels
        show_grid: Whether to show grid lines

    Returns:
        Styled Plotly figure
    """
    theme = get_dark_theme()

    grid_color = "rgba(255,255,255,0.06)" if show_grid else "rgba(0,0,0,0)"

    fig.update_layout(
        height=height,
        margin={"l": 20, "r": 20, "t": 30, "b": 24},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={
            "color": "rgba(255,255,255,0.85)",
            "size": 12,
            "family": "'Inter', -apple-system, BlinkMacSystemFont, sans-serif",
        },
        legend={
            "orientation": "h",
            "yanchor": "top",
            "y": 1.14,
            "xanchor": "center",
            "x": 0.5,
            "bgcolor": "rgba(15, 23, 42, 0.9)",
            "bordercolor": "rgba(168, 85, 247, 0.2)",
            "borderwidth": 1,
            "font": {"color": "rgba(255,255,255,0.82)", "size": 11},
            "itemsizing": "constant",
        },
        xaxis={
            "showgrid": show_grid,
            "gridcolor": grid_color,
            "gridwidth": 1,
            "zeroline": False,
            "tickfont": {"color": "rgba(255,255,255,0.55)", "size": 11},
            "title": {"font": {"color": "rgba(255,255,255,0.65)", "size": 12}},
            "linecolor": "rgba(255,255,255,0.1)",
            "linewidth": 1,
            "mirror": False,
            "tickcolor": "rgba(255,255,255,0.1)",
        },
        yaxis={
            "showgrid": show_grid,
            "gridcolor": grid_color,
            "gridwidth": 1,
            "zeroline": False,
            "tickfont": {"color": "rgba(255,255,255,0.55)", "size": 11},
            "title": {"font": {"color": "rgba(255,255,255,0.65)", "size": 12}},
            "linecolor": "rgba(255,255,255,0.1)",
            "linewidth": 1,
            "mirror": False,
            "tickcolor": "rgba(255,255,255,0.1)",
        },
        hoverlabel={
            "bgcolor": "rgba(15, 23, 42, 0.95)",
            "bordercolor": "rgba(168, 85, 247, 0.4)",
            "font": {"color": "white", "size": 12},
        },
    )
    return fig


def render_line_chart_card(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    title: str,
    subtitle: str = "",
    show_glow: bool = True,
    color: str = "#a855f7",
    fill_gradient: bool = True,
) -> None:
    """
    Render a premium line chart inside a dark card with glowing effect.

    Args:
        df: DataFrame with data
        x_col: Column name for x-axis
        y_col: Column name for y-axis
        title: Card title
        subtitle: Card subtitle
        show_glow: Whether to show glow effect on line
        color: Line color
        fill_gradient: Whether to show gradient fill under the line
    """
    theme = get_dark_theme()
    latest = float(df[y_col].iloc[-1]) if len(df) > 0 else 0
    prev = (
        float(df[y_col].iloc[-8]) if len(df) > 8 else float(df[y_col].iloc[0]) if len(df) > 0 else 0
    )
    delta = ((latest - prev) / max(prev, 1e-9)) * 100 if prev != 0 else 0

    delta_class = "positive" if delta >= 0 else "negative"
    arrow = "↑" if delta >= 0 else "↓"
    right_html = f"""
    <span class='delta {delta_class}' style='font-size: 12px; padding: 4px 12px;'>
        <span style="font-size: 13px;">{arrow}</span> {abs(delta):.1f}%
    </span>
    """

    card_open(title=title, subtitle=subtitle, right_html=right_html, glow=True)

    fig = go.Figure()

    # Gradient fill under the line
    if fill_gradient:
        fig.add_trace(
            go.Scatter(
                x=df[x_col],
                y=df[y_col],
                mode="lines",
                fill="tozeroy",
                fillcolor=f"rgba({int(color[1:3], 16)}, {int(color[3:5], 16)}, {int(color[5:7], 16)}, 0.12)",
                line={"color": "rgba(0,0,0,0)", "width": 0},
                hoverinfo="skip",
                showlegend=False,
            )
        )

    # Glow layer for premium effect
    if show_glow:
        fig.add_trace(
            go.Scatter(
                x=df[x_col],
                y=df[y_col],
                mode="lines",
                line={
                    "color": f"rgba({int(color[1:3], 16)}, {int(color[3:5], 16)}, {int(color[5:7], 16)}, 0.25)",
                    "width": 14,
                    "shape": "spline",
                },
                hoverinfo="skip",
                showlegend=False,
            )
        )

    # Main line with gradient effect
    fig.add_trace(
        go.Scatter(
            x=df[x_col],
            y=df[y_col],
            mode="lines+markers",
            line={"color": color, "width": 3, "shape": "spline"},
            marker={
                "size": 8,
                "color": color,
                "line": {"width": 2, "color": "rgba(255,255,255,0.3)"},
            },
            hovertemplate="<b>%{x}</b><br>Value: %{y:.1f}<extra></extra>",
        )
    )

    # Premium annotation for latest value
    if len(df) > 0:
        fig.add_annotation(
            x=df[x_col].iloc[-1],
            y=latest,
            text=f"<b>{latest:.1f}</b>",
            showarrow=True,
            arrowwidth=2,
            arrowcolor="rgba(168, 85, 247, 0.6)",
            arrowhead=2,
            bgcolor="rgba(139, 92, 246, 0.95)",
            bordercolor="rgba(255,255,255,0.25)",
            font={"color": "white", "size": 12, "family": "'Inter', sans-serif"},
            borderpad=8,
            borderwidth=1,
            ax=-35,
            ay=-40,
        )

    apply_dark_chart_layout(fig, height=240)
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})

    card_close()


def render_horizontal_bar_card(
    df: pd.DataFrame,
    y_col: str,
    value_cols: list[str],
    title: str,
    subtitle: str = "",
    colors: list[str] | None = None,
) -> None:
    """
    Render horizontal stacked bars inside a dark card.

    Args:
        df: DataFrame with data
        y_col: Column name for y-axis labels
        value_cols: List of column names for bar values
        title: Card title
        subtitle: Card subtitle
        colors: List of colors for each value column
    """
    theme = get_dark_theme()
    if colors is None:
        colors = [theme.colors.purple, theme.colors.cyan]

    card_open(title=title, subtitle=subtitle)

    fig = go.Figure()
    for i, col in enumerate(value_cols):
        fig.add_trace(
            go.Bar(
                y=df[y_col],
                x=df[col],
                orientation="h",
                marker={
                    "color": colors[i % len(colors)],
                    "line": {"color": "rgba(255,255,255,0.10)", "width": 1},
                },
                name=col.replace("_", " ").title(),
                hovertemplate="%{y}<br><b>%{x:.0f}</b><extra></extra>",
            )
        )

    fig.update_layout(barmode="overlay")
    fig.update_xaxes(showgrid=False, zeroline=False, range=[0, 100], showticklabels=False)
    fig.update_yaxes(
        showgrid=False, zeroline=False, tickfont={"color": "rgba(255,255,255,0.78)", "size": 12}
    )

    apply_dark_chart_layout(fig, height=200)
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})

    card_close()


def render_donut_chart_card(
    df: pd.DataFrame,
    labels_col: str,
    values_col: str,
    title: str,
    subtitle: str = "",
    colors: list[str] | None = None,
    center_text: str = "",
) -> None:
    """
    Render a donut chart inside a dark card with legend below.

    Args:
        df: DataFrame with data
        labels_col: Column name for labels
        values_col: Column name for values
        title: Card title
        subtitle: Card subtitle
        colors: List of colors for segments
        center_text: Text to show in center of donut
    """
    theme = get_dark_theme()
    if colors is None:
        colors = [theme.colors.purple, theme.colors.cyan, theme.colors.pink]

    card_open(title=title, subtitle=subtitle)

    fig = go.Figure(
        data=[
            go.Pie(
                labels=df[labels_col],
                values=df[values_col],
                hole=0.72,
                sort=False,
                marker={"colors": colors, "line": {"color": "rgba(0,0,0,0)", "width": 0}},
                textinfo="none",
                hovertemplate="%{label}<br><b>%{value}%</b><extra></extra>",
            )
        ]
    )

    annotations = []
    if center_text:
        annotations.append(
            {
                "text": center_text,
                "x": 0.5,
                "y": 0.5,
                "font": {"size": 12, "color": "rgba(255,255,255,0.78)"},
                "showarrow": False,
            }
        )

    fig.update_layout(annotations=annotations)
    apply_dark_chart_layout(fig, height=220)
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})

    # Legend below chart
    total = df[values_col].sum()
    for i, (_, row) in enumerate(df.iterrows()):
        pct = (row[values_col] / total) * 100 if total else 0
        color = colors[i % len(colors)]
        render_html(
            f"""
            <div style='display:flex; align-items:center; justify-content:space-between; color:rgba(255,255,255,0.70); font-size:12px; padding:4px 2px;'>
                <span style='display:flex; align-items:center; gap:8px;'>
                    <span style='width:10px; height:10px; border-radius:3px; background:{color};'></span>
                    {row[labels_col]}
                </span>
                <span style='font-weight:600;'>{pct:.0f}%</span>
            </div>
            """
        )

    card_close()


def render_grouped_bar_card(
    df: pd.DataFrame,
    x_col: str,
    y_cols: list[str],
    title: str,
    subtitle: str = "",
    colors: list[str] | None = None,
    labels: dict[str, str] | None = None,
) -> None:
    """
    Render a grouped bar chart inside a dark card.

    Args:
        df: DataFrame with data
        x_col: Column name for x-axis
        y_cols: List of column names for y-axis values
        title: Card title
        subtitle: Card subtitle
        colors: List of colors for each series
        labels: Dictionary mapping column names to display labels
    """
    theme = get_dark_theme()
    if colors is None:
        colors = [theme.colors.purple, theme.colors.cyan, theme.colors.pink]
    if labels is None:
        labels = {col: col.replace("_", " ").title() for col in y_cols}

    card_open(title=title, subtitle=subtitle)

    fig = go.Figure()
    for i, col in enumerate(y_cols):
        fig.add_trace(
            go.Bar(
                x=df[x_col],
                y=df[col],
                name=labels.get(col, col),
                marker_color=colors[i % len(colors)],
                hovertemplate="%{x}<br><b>%{y:.1f}</b><extra></extra>",
            )
        )

    fig.update_layout(
        barmode="group",
        legend={
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.02,
            "xanchor": "center",
            "x": 0.5,
            "font": {"color": "rgba(255,255,255,0.70)", "size": 11},
        },
        showlegend=True,
    )
    fig.update_xaxes(tickfont={"color": "rgba(255,255,255,0.55)", "size": 10})

    apply_dark_chart_layout(fig, height=280)
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})

    card_close()


# =============================================================================
# UTILITY COMPONENTS
# =============================================================================


def render_section_title(title: str, subtitle: str = "", icon: str = "") -> None:
    """
    Render a premium section title with gradient line and optional icon.

    Args:
        title: Section title
        subtitle: Optional subtitle
        icon: Optional emoji icon
    """
    icon_html = f"<span style='margin-right: 8px;'>{icon}</span>" if icon else ""
    render_html(
        f"""
        <div class='section-header' style='
            font-size: 20px;
            font-weight: 700;
            margin: 32px 0 14px 0;
        '>
            {icon_html}{title}
        </div>
        """
    )
    if subtitle:
        render_html(
            f"""
            <div class='section-sub' style='
                font-size: 13px;
                color: rgba(255, 255, 255, 0.5);
                margin: -8px 0 20px 2px;
            '>
                {subtitle}
            </div>
            """
        )


def render_status_overview(green: int, amber: int, red: int, total: int | None = None) -> None:
    """
    Render a premium compact status overview with animated pills.

    Args:
        green: Count of green status items
        amber: Count of amber status items
        red: Count of red status items
        total: Optional total count to display
    """
    total_count = total if total is not None else (green + amber + red)
    render_html(
        f"""
        <div style="display: flex; gap: 12px; align-items: center; flex-wrap: wrap;">
            <div class="status-pill status-green" style="cursor: pointer;">
                <span style="font-size: 14px;">✓</span>
                <span style="font-weight: 700;">{green}</span>
                <span style="opacity: 0.7; font-weight: 500;">On Track</span>
            </div>
            <div class="status-pill status-amber" style="cursor: pointer;">
                <span style="font-size: 14px;">⚠</span>
                <span style="font-weight: 700;">{amber}</span>
                <span style="opacity: 0.7; font-weight: 500;">At Risk</span>
            </div>
            <div class="status-pill status-red" style="cursor: pointer;">
                <span style="font-size: 14px;">✕</span>
                <span style="font-weight: 700;">{red}</span>
                <span style="opacity: 0.7; font-weight: 500;">Critical</span>
            </div>
            <div style="
                margin-left: auto;
                padding: 8px 16px;
                background: rgba(255,255,255,0.04);
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 10px;
                font-size: 12px;
                color: rgba(255,255,255,0.6);
            ">
                <span style="font-weight: 600; color: rgba(255,255,255,0.9);">{total_count}</span> KPIs tracked
            </div>
        </div>
        """
    )


def render_advanced_analytics_sidebar(active: str = "forecast") -> str:
    """
    Render a modern vertical sidebar for advanced analytics navigation.
    Returns the selected section key.

    Args:
        active: Currently active section key (forecast, warning, recommendations, map)

    Returns:
        Selected section key
    """
    # Sections configuration
    sections = [
        ("forecast", "🔮", "KPI Forecasting", "ML-powered predictions"),
        ("warning", "⚠️", "Early Warning", "Anomaly detection"),
        ("recommendations", "🤖", "AI Recommendations", "Smart insights"),
        ("map", "🗺️", "Regional Map", "Geographic view"),
    ]

    options = [s[0] for s in sections]
    desc_map = {s[0]: s[3] for s in sections}

    if "analytics_section" not in st.session_state:
        st.session_state.analytics_section = active if active in options else options[0]

    # Sidebar container styling
    render_html(
        """
        <style>
          /* Sidebar navigation container */
          .analytics-sidebar-nav {
            background: linear-gradient(145deg, rgba(27, 31, 54, 0.98), rgba(15, 17, 34, 0.98));
            border: 1px solid rgba(168, 85, 247, 0.25);
            border-radius: 16px;
            padding: 16px 12px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.40), inset 0 1px 0 rgba(255, 255, 255, 0.05);
            position: sticky;
            top: 60px;
          }

          .analytics-sidebar-title {
            font-size: 11px;
            font-weight: 700;
            color: rgba(255, 255, 255, 0.45);
            letter-spacing: 1.5px;
            text-transform: uppercase;
            padding: 0 8px 12px 8px;
            margin-bottom: 8px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.08);
          }

          .nav-item {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 14px 16px;
            margin: 6px 0;
            border-radius: 12px;
            border: 1px solid transparent;
            background: transparent;
            cursor: pointer;
            transition: all 220ms cubic-bezier(0.4, 0, 0.2, 1);
          }

          .nav-item:hover {
            background: rgba(168, 85, 247, 0.12);
            border-color: rgba(168, 85, 247, 0.25);
            transform: translateX(4px);
          }

          .nav-item.active {
            background: linear-gradient(135deg, rgba(168, 85, 247, 0.35), rgba(34, 211, 238, 0.20));
            border-color: rgba(168, 85, 247, 0.55);
            box-shadow: 0 4px 24px rgba(168, 85, 247, 0.25), inset 0 1px 0 rgba(255, 255, 255, 0.10);
          }

          .nav-item .nav-icon {
            font-size: 18px;
            width: 28px;
            text-align: center;
          }

          .nav-item .nav-content {
            flex: 1;
          }

          .nav-item .nav-label {
            font-size: 13px;
            font-weight: 500;
            color: rgba(255, 255, 255, 0.78);
            letter-spacing: 0.2px;
          }

          .nav-item.active .nav-label {
            color: rgba(255, 255, 255, 0.98);
            font-weight: 700;
          }

          .nav-item .nav-desc {
            font-size: 11px;
            color: rgba(255, 255, 255, 0.45);
            margin-top: 2px;
          }

          .nav-item.active .nav-desc {
            color: rgba(255, 255, 255, 0.65);
          }

          .nav-indicator {
            width: 6px;
            height: 6px;
            border-radius: 50%;
            background: transparent;
          }

          .nav-item.active .nav-indicator {
            background: #22d3ee;
            box-shadow: 0 0 12px #22d3ee;
          }

          /* Style the sidebar navigation buttons */
          .analytics-sidebar-nav button[kind="secondary"] {
            background: transparent !important;
            border: 1px solid transparent !important;
            color: rgba(255, 255, 255, 0.78) !important;
            text-align: left !important;
            padding: 14px 16px !important;
            margin: 4px 0 !important;
            border-radius: 12px !important;
            font-size: 13px !important;
            font-weight: 500 !important;
            transition: all 220ms cubic-bezier(0.4, 0, 0.2, 1) !important;
          }

          .analytics-sidebar-nav button[kind="secondary"]:hover {
            background: rgba(168, 85, 247, 0.12) !important;
            border-color: rgba(168, 85, 247, 0.25) !important;
            transform: translateX(4px);
          }

          .analytics-sidebar-nav button[kind="primary"] {
            background: linear-gradient(135deg, rgba(168, 85, 247, 0.35), rgba(34, 211, 238, 0.20)) !important;
            border: 1px solid rgba(168, 85, 247, 0.55) !important;
            color: rgba(255, 255, 255, 0.98) !important;
            text-align: left !important;
            padding: 14px 16px !important;
            margin: 4px 0 !important;
            border-radius: 12px !important;
            font-size: 13px !important;
            font-weight: 700 !important;
            box-shadow: 0 4px 24px rgba(168, 85, 247, 0.25), inset 0 1px 0 rgba(255, 255, 255, 0.10) !important;
          }

          /* Alternative: target by data-testid for Streamlit buttons */
          .analytics-sidebar-nav [data-testid="stButton"] button {
            background: transparent !important;
            border: 1px solid transparent !important;
            color: rgba(255, 255, 255, 0.78) !important;
            text-align: left !important;
            justify-content: flex-start !important;
            padding: 14px 16px !important;
            margin: 4px 0 !important;
            border-radius: 12px !important;
            font-size: 13px !important;
            font-weight: 500 !important;
            transition: all 220ms cubic-bezier(0.4, 0, 0.2, 1) !important;
          }

          .analytics-sidebar-nav [data-testid="stButton"] button:hover {
            background: rgba(168, 85, 247, 0.12) !important;
            border-color: rgba(168, 85, 247, 0.25) !important;
          }

          .analytics-sidebar-nav [data-testid="stButton"] button[kind="primary"],
          .analytics-sidebar-nav [data-testid="stButton"]:has(button[data-active="true"]) button {
            background: linear-gradient(135deg, rgba(168, 85, 247, 0.35), rgba(34, 211, 238, 0.20)) !important;
            border: 1px solid rgba(168, 85, 247, 0.55) !important;
            color: rgba(255, 255, 255, 0.98) !important;
            font-weight: 700 !important;
            box-shadow: 0 4px 24px rgba(168, 85, 247, 0.25) !important;
          }
        </style>
        """
    )

    # Render sidebar with buttons for navigation
    render_html('<div class="analytics-sidebar-nav">')
    render_html(
        '<div class="analytics-sidebar-title">Analytics Modules</div>'
    )

    selected = st.session_state.analytics_section

    for key, icon, label, _desc in sections:
        is_active = key == selected
        if st.button(
            f"{icon}  {label}",
            key=f"nav_{key}",
            width="stretch",
            type="primary" if is_active else "secondary",
        ):
            st.session_state.analytics_section = key
            selected = key
            st.rerun()

    render_html("</div>")

    # Show description for selected section
    st.caption(f"📍 {desc_map.get(selected, '')}")

    return selected


# =============================================================================
# ENHANCED KPI COMPONENTS WITH SPARKLINES
# =============================================================================


def create_sparkline_svg(
    values: list[float],
    width: int = 100,
    height: int = 30,
    color: str = "#a855f7",
    fill_color: str | None = None,
) -> str:
    """
    Create an SVG sparkline from a list of values.

    Args:
        values: List of numeric values for the sparkline
        width: Width of the SVG
        height: Height of the SVG
        color: Stroke color for the line
        fill_color: Optional gradient fill below line

    Returns:
        SVG markup string
    """
    if not values or len(values) < 2:
        return ""

    # Normalize values to fit in SVG
    min_val = min(values)
    max_val = max(values)
    value_range = max_val - min_val if max_val != min_val else 1

    # Create points
    points = []
    for i, val in enumerate(values):
        x = (i / (len(values) - 1)) * width
        y = height - ((val - min_val) / value_range) * (height - 4) - 2
        points.append(f"{x:.1f},{y:.1f}")

    path_d = f"M {' L '.join(points)}"

    # Create gradient fill area
    fill_path = ""
    if fill_color:
        area_points = [f"0,{height}"] + points + [f"{width},{height}"]
        fill_path = f"""
        <defs>
            <linearGradient id="sparkGrad" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" style="stop-color:{fill_color};stop-opacity:0.4"/>
                <stop offset="100%" style="stop-color:{fill_color};stop-opacity:0"/>
            </linearGradient>
        </defs>
        <path d="M {' L '.join(area_points)} Z" fill="url(#sparkGrad)"/>"""

    return f"""
    <svg width="{width}" height="{height}" viewBox="0 0 {width} {height}"
         style="overflow:visible" xmlns="http://www.w3.org/2000/svg">
        {fill_path}
        <path d="{path_d}" fill="none" stroke="{color}" stroke-width="2"
              stroke-linecap="round" stroke-linejoin="round"/>
        <circle cx="{points[-1].split(',')[0]}" cy="{points[-1].split(',')[1]}"
                r="3" fill="{color}" stroke="white" stroke-width="1"/>
    </svg>"""


def create_progress_ring(
    value: float,
    max_value: float = 100,
    size: int = 80,
    stroke_width: int = 8,
    color: str = "#a855f7",
    bg_color: str = "rgba(255,255,255,0.08)",
    label: str = "",
) -> str:
    """
    Create an SVG circular progress ring.

    Args:
        value: Current value
        max_value: Maximum value (default 100 for percentage)
        size: Diameter of the ring
        stroke_width: Width of the ring stroke
        color: Progress bar color
        bg_color: Background ring color
        label: Optional label below the ring

    Returns:
        HTML markup for progress ring
    """
    radius = (size - stroke_width) / 2
    circumference = 2 * 3.14159 * radius
    percentage = min(value / max_value, 1.0) if max_value > 0 else 0
    dash_offset = circumference * (1 - percentage)

    # Choose color based on percentage
    if percentage >= 0.8:
        color = "#10b981"  # Green for good
    elif percentage >= 0.5:
        color = "#f59e0b"  # Yellow for medium
    else:
        color = "#ef4444"  # Red for low

    display_value = f"{int(value)}%" if max_value == 100 else f"{value:.1f}"

    return f"""
    <div class="progress-ring-container" style="text-align:center">
        <svg class="progress-ring" width="{size}" height="{size}">
            <circle class="progress-bg"
                    cx="{size/2}" cy="{size/2}" r="{radius}"
                    stroke="{bg_color}" stroke-width="{stroke_width}"/>
            <circle class="progress-bar"
                    cx="{size/2}" cy="{size/2}" r="{radius}"
                    stroke="{color}" stroke-width="{stroke_width}"
                    stroke-dasharray="{circumference}"
                    stroke-dashoffset="{dash_offset}"
                    style="--target-offset: {dash_offset}"/>
        </svg>
        <span class="progress-ring-value" style="color:{color}">{display_value}</span>
        {f'<div class="progress-ring-label">{label}</div>' if label else ''}
    </div>"""


def create_alert_badge(
    alert_type: str = "info",
    count: int | None = None,
) -> str:
    """
    Create an alert badge for KPI cards.

    Args:
        alert_type: Type of alert ('critical', 'warning', 'info')
        count: Optional count to display

    Returns:
        HTML markup for alert badge
    """
    icons = {
        "critical": "!",
        "warning": "⚠",
        "info": "i",
    }
    icon = icons.get(alert_type, "i")
    display = str(count) if count is not None else icon

    return f'<div class="alert-badge {alert_type}">{display}</div>'


def render_enhanced_kpi_card(
    title: str,
    value: str | float,
    delta: float | None = None,
    delta_suffix: str = "%",
    sparkline_data: list[float] | None = None,
    alert_type: str | None = None,
    icon: str = "📊",
    color: str = "#a855f7",
    target: float | None = None,
    status: str | None = None,
) -> None:
    """
    Render an enhanced KPI card with sparkline and optional alert badge.

    Args:
        title: KPI title
        value: Main value to display
        delta: Change value (positive/negative)
        delta_suffix: Suffix for delta value
        sparkline_data: List of values for sparkline
        alert_type: Alert badge type ('critical', 'warning', 'info', None)
        icon: Icon emoji
        color: Accent color for the card
        target: Target value for comparison
        status: Status label ('On Track', 'Watch', 'Off Track')
    """
    delta_class = "positive" if delta and delta >= 0 else "negative"
    delta_icon = "↑" if delta and delta >= 0 else "↓"
    delta_html = ""
    if delta is not None:
        delta_html = f"""
        <span class="kpi-delta {delta_class}">
            {delta_icon} {abs(delta):.1f}{delta_suffix}
        </span>"""

    alert_html = create_alert_badge(alert_type) if alert_type else ""

    sparkline_html = ""
    if sparkline_data and len(sparkline_data) >= 2:
        spark_color = "#10b981" if delta and delta >= 0 else "#ef4444"
        sparkline_html = f"""
        <div class="sparkline-container">
            {create_sparkline_svg(sparkline_data, width=120, height=35, color=spark_color, fill_color=spark_color)}
        </div>"""

    # Target and Status HTML
    target_html = ""
    if target is not None:
        target_html = f"""
        <div style="font-size: 11px; color: rgba(255,255,255,0.5); margin-top: 4px;">
            Target: <span style="color: rgba(255,255,255,0.8);">{target}</span>
        </div>
        """

    status_html = ""
    if status:
        status_colors = {
            "On Track": "#10b981",
            "Watch": "#f59e0b",
            "Off Track": "#ef4444",
        }
        s_color = status_colors.get(status, "#a855f7")
        status_html = f"""
        <div style="
            display: inline-block;
            padding: 2px 8px;
            border-radius: 12px;
            background: {s_color}20;
            border: 1px solid {s_color}40;
            color: {s_color};
            font-size: 10px;
            font-weight: 600;
            text-transform: uppercase;
            margin-top: 6px;
        ">
            {status}
        </div>
        """

    html = f"""
    <div class="kpi-card-enhanced" style="--accent-color: {color}">
        {alert_html}
        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
            <div class="kpi-label">{icon} {title}</div>
            {status_html}
        </div>
        <div class="kpi-value">{value}</div>
        {delta_html}
        {target_html}
        {sparkline_html}
    </div>
    """
    render_html(html)


def render_yoy_comparison(
    kpi_name: str,
    current_year: int,
    current_value: float,
    previous_year: int,
    previous_value: float,
    unit: str = "",
    icon: str = "📈",
) -> None:
    """
    Render a Year-over-Year comparison card.

    Args:
        kpi_name: Name of the KPI
        current_year: Current year
        current_value: Value for current year
        previous_year: Previous year
        previous_value: Value for previous year
        unit: Unit suffix (e.g., '%', ' SAR')
        icon: Icon emoji
    """
    change = current_value - previous_value
    pct_change = ((current_value - previous_value) / previous_value * 100) if previous_value != 0 else 0
    change_class = "positive" if change >= 0 else "negative"
    arrow = "→" if change >= 0 else "→"

    html = f"""
    <div class="yoy-comparison">
        <div class="yoy-year">
            <div class="year-label">{previous_year}</div>
            <div class="year-value">{previous_value:.1f}{unit}</div>
        </div>
        <div class="yoy-divider">
            <span class="yoy-arrow">{arrow}</span>
            <span class="yoy-change {change_class}">
                {"+" if change >= 0 else ""}{pct_change:.1f}%
            </span>
        </div>
        <div class="yoy-year">
            <div class="year-label">{current_year}</div>
            <div class="year-value">{current_value:.1f}{unit}</div>
        </div>
    </div>
    """

    render_html(f'<div style="margin-bottom:8px; color:rgba(255,255,255,0.7); font-size:13px">{icon} {kpi_name}</div>')
    render_html(html)


def add_target_line_to_chart(
    fig: go.Figure,
    target_value: float,
    target_label: str = "Target",
    line_color: str = "#10b981",
) -> go.Figure:
    """
    Add a horizontal target line to a Plotly figure.

    Args:
        fig: Plotly figure to modify
        target_value: Y-axis value for target line
        target_label: Label for the target line
        line_color: Color of the target line

    Returns:
        Modified Plotly figure
    """
    fig.add_hline(
        y=target_value,
        line_dash="dash",
        line_color=line_color,
        line_width=2,
        annotation_text=f"🎯 {target_label}: {target_value:.1f}",
        annotation_position="top right",
        annotation_font_size=11,
        annotation_font_color=line_color,
    )
    return fig

