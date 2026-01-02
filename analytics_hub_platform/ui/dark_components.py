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

from analytics_hub_platform.ui.dark_theme import get_dark_css, get_dark_theme


def inject_dark_theme() -> None:
    """Inject the dark theme CSS into the Streamlit app."""
    st.markdown(get_dark_css(), unsafe_allow_html=True)


# =============================================================================
# LAYOUT COMPONENTS
# =============================================================================


def render_sidebar(active: str = "Dashboard") -> None:
    """
    Render the left sidebar with gradient header, avatar, and page navigation.
    Uses Streamlit's native page_link for working navigation.

    Args:
        active: The currently active page name
    """
    # Navigation items matching the pages in pages/ directory
    items = [
        ("Dashboard", "📊", "pages/1_📊_Dashboard.py"),
        ("KPIs", "📈", "pages/2_📈_KPIs.py"),
        ("Trends", "📊", "pages/3_📊_Trends.py"),
        ("Data", "📋", "pages/4_📋_Data.py"),
        ("Advanced Analytics", "🧠", "pages/5_🧠_Advanced_Analytics.py"),
        ("Settings", "⚙️", "pages/6_⚙️_Settings.py"),
    ]

    # Inject sidebar styling
    st.markdown(
        """
    <style>
      /* Sidebar container styling */
      .sidebar-header-card {
        background: linear-gradient(145deg, rgba(168, 85, 247, 0.95), rgba(236, 72, 153, 0.8));
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 16px;
        position: relative;
        overflow: hidden;
      }
      .sidebar-header-card::before {
        content: "";
        position: absolute;
        top: -50%;
        right: -30%;
        width: 150px;
        height: 150px;
        background: radial-gradient(circle, rgba(255,255,255,0.2) 0%, transparent 70%);
        border-radius: 50%;
      }
      .logo-icon {
        font-size: 28px;
        filter: drop-shadow(0 0 10px rgba(255,255,255,0.4));
      }
      .sidebar-brand {
        font-weight: 700;
        font-size: 15px;
        color: white;
        margin-top: 6px;
      }
      .sidebar-subtitle {
        font-size: 11px;
        color: rgba(255,255,255,0.75);
        margin-top: 2px;
      }

      /* User card */
      .user-card {
        background: rgba(30, 35, 64, 0.9);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 12px;
        padding: 14px;
        margin-bottom: 16px;
        display: flex;
        align-items: center;
        gap: 12px;
      }
      .user-avatar {
        width: 40px;
        height: 40px;
        border-radius: 12px;
        background: linear-gradient(145deg, rgba(168, 85, 247, 0.8), rgba(34, 211, 238, 0.8));
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 13px;
        color: white;
        box-shadow: 0 4px 12px rgba(168, 85, 247, 0.3);
      }
      .user-info { flex: 1; }
      .user-title {
        font-size: 13px;
        font-weight: 600;
        color: rgba(255,255,255,0.95);
      }
      .user-role {
        font-size: 10px;
        color: rgba(255,255,255,0.5);
        margin-top: 2px;
      }
      .user-status {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #10b981;
        box-shadow: 0 0 8px #10b981;
      }

      /* Navigation styling */
      .nav-section-label {
        font-size: 10px;
        font-weight: 700;
        color: rgba(255,255,255,0.35);
        letter-spacing: 1.2px;
        padding: 8px 4px;
        margin-bottom: 8px;
      }

      /* Style Streamlit page links */
      [data-testid="stPageLink"] {
        background: transparent !important;
        border: 1px solid transparent !important;
        border-radius: 10px !important;
        margin-bottom: 4px !important;
        transition: all 180ms ease !important;
      }
      [data-testid="stPageLink"]:hover {
        background: rgba(168, 85, 247, 0.15) !important;
        border-color: rgba(168, 85, 247, 0.3) !important;
      }
      [data-testid="stPageLink"] p {
        color: rgba(255,255,255,0.7) !important;
        font-size: 13px !important;
        font-weight: 500 !important;
      }
      [data-testid="stPageLink"]:hover p {
        color: rgba(255,255,255,0.95) !important;
      }

      /* Active page styling */
      .nav-active-indicator {
        background: linear-gradient(135deg, rgba(168, 85, 247, 0.25), rgba(34, 211, 238, 0.15)) !important;
        border: 1px solid rgba(168, 85, 247, 0.4) !important;
        border-radius: 10px !important;
        padding: 10px 14px !important;
        margin-bottom: 4px !important;
      }
      .nav-active-indicator p {
        color: rgba(255,255,255,0.98) !important;
        font-weight: 600 !important;
      }
    </style>
    """,
        unsafe_allow_html=True,
    )

    # Header card
    st.markdown(
        """
    <div class="sidebar-header-card">
        <div class="logo-icon">🌱</div>
        <div class="sidebar-brand">Sustainable Analytics</div>
        <div class="sidebar-subtitle">Ministry Dashboard</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # User card
    st.markdown(
        """
    <div class="user-card">
        <div class="user-avatar">ME</div>
        <div class="user-info">
            <div class="user-title">H.E. Minister</div>
            <div class="user-role">Executive View</div>
        </div>
        <div class="user-status"></div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Navigation section
    st.markdown('<div class="nav-section-label">MAIN MENU</div>', unsafe_allow_html=True)

    # Render navigation links using Streamlit's page_link
    for name, icon, page_path in items:
        if name == active:
            # Show active page with special styling (non-clickable)
            st.markdown(
                f"""
            <div class="nav-active-indicator">
                <p style="margin: 0; display: flex; align-items: center; gap: 10px;">
                    <span style="width: 8px; height: 8px; border-radius: 50%; background: #22d3ee; box-shadow: 0 0 12px #22d3ee;"></span>
                    <span>{icon}</span>
                    <span>{name}</span>
                </p>
            </div>
            """,
                unsafe_allow_html=True,
            )
        else:
            # Clickable link to other pages
            st.page_link(page_path, label=f"● {icon} {name}", use_container_width=True)


def render_header(
    title: str = "Overview",
    period_text: str | None = None,
    show_search: bool = True,
    show_icons: bool = True,
) -> None:
    """
    Render the top header bar with title, date range, search, and icons.

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
        st.markdown(
            f"""
            <div class="topbar">
              <div class="title">{title}</div>
              <div class="daterange">Reporting period: {period_text}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c2:
        if show_search:
            st.markdown("<div class='topbar' style='padding:10px 14px;'>", unsafe_allow_html=True)
            st.text_input(
                "Search",
                placeholder="Search KPIs, regions, policies…",
                label_visibility="collapsed",
                key="header_search",
            )
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='topbar' style='height: 60px;'></div>", unsafe_allow_html=True)

    with c3:
        if show_icons:
            st.markdown(
                """
                <div class="topbar" style="display:flex; align-items:center; justify-content:flex-end; gap:10px; height: 60px;">
                  <div class="icon-pill">🔔</div>
                  <div class="icon-pill">📧</div>
                  <div class="icon-pill">👤</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown("<div class='topbar' style='height: 60px;'></div>", unsafe_allow_html=True)


# =============================================================================
# CARD COMPONENTS
# =============================================================================


def card_open(
    title: str,
    subtitle: str | None = None,
    right_html: str | None = None,
) -> None:
    """
    Open a styled dark card wrapper.

    Args:
        title: Card title
        subtitle: Optional subtitle text
        right_html: Optional HTML to render on the right side of header
    """
    subtitle_html = f"<div class='card-sub'>{subtitle}</div>" if subtitle else ""
    right = right_html or ""
    st.markdown(
        f"""
        <div class="dark-card">
          <div style="display:flex; align-items:flex-start; justify-content:space-between; gap:12px; margin-bottom: 12px;">
            <div>
              <div class="card-title">{title}</div>
              {subtitle_html}
            </div>
            <div>{right}</div>
          </div>
        """,
        unsafe_allow_html=True,
    )


def card_close() -> None:
    """Close the styled dark card wrapper."""
    st.markdown("</div>", unsafe_allow_html=True)


def render_kpi_card(
    title: str,
    value: str | float | int,
    delta: float | None = None,
    unit: str = "",
    subtitle: str = "",
    height: int = 130,
) -> None:
    """
    Render a compact KPI metric card in dark theme.

    Args:
        title: KPI label/name
        value: Current value
        delta: Change percentage from previous period
        unit: Unit suffix for the value
        subtitle: Additional context text
        height: Card height in pixels
    """
    get_dark_theme()

    # Format value
    if isinstance(value, float):
        display_value = f"{value:,.1f}" if value < 1000 else f"{value:,.0f}"
    elif isinstance(value, int):
        display_value = f"{value:,}"
    else:
        display_value = str(value)

    # Delta HTML
    delta_html = ""
    if delta is not None:
        delta_class = "positive" if delta >= 0 else "negative"
        arrow = "▲" if delta >= 0 else "▼"
        delta_html = f"""
        <span class='delta {delta_class}' style='margin-left: 10px;'>
            {arrow} {abs(delta):.1f}%
        </span>
        """

    card_html = f"""
    <div class="dark-card" style="min-height: {height - 20}px;">
        <div class="card-title">{title}</div>
        <div style="display: flex; align-items: baseline; margin-top: 8px;">
            <span class="card-value">{display_value}</span>
            <span style="font-size: 14px; color: rgba(255,255,255,0.55); margin-left: 4px;">{unit}</span>
            {delta_html}
        </div>
        <div class="card-sub" style="margin-top: 8px;">{subtitle}</div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)


def render_mini_metric(
    title: str,
    value: str,
    delta: float,
    ring_percent: float,
    subtitle: str = "vs previous period",
) -> None:
    """
    Render a mini metric card with a ring indicator (like New Green Jobs, FDI).

    Args:
        title: Metric title
        value: Display value (e.g., "62.5K")
        delta: Change percentage
        ring_percent: Progress ring percentage (0-100)
        subtitle: Subtitle text
    """
    get_dark_theme()
    delta_class = "positive" if delta >= 0 else "negative"
    arrow = "▲" if delta >= 0 else "▼"

    right_html = f"<span class='delta {delta_class}'>{arrow} {abs(delta):.1f}%</span>"
    card_open(title=title, subtitle=subtitle, right_html=right_html)

    c1, c2 = st.columns([0.58, 0.42], gap="small")
    with c1:
        st.markdown(
            f"""
            <div class='card-value' style='font-size: 26px;'>{value}</div>
            <div style='margin-top: 8px; color: rgba(255,255,255,0.45); font-size: 11px;'>Updated monthly</div>
            """,
            unsafe_allow_html=True,
        )
    with c2:
        ring = float(np.clip(ring_percent, 0, 100))
        fig = go.Figure(
            data=[
                go.Pie(
                    values=[ring, 100 - ring],
                    hole=0.78,
                    sort=False,
                    marker={"colors": ["rgba(168, 85, 247, 0.95)", "rgba(255,255,255,0.08)"]},
                    textinfo="none",
                    hoverinfo="skip",
                )
            ]
        )
        fig.update_layout(
            height=100,
            margin={"l": 0, "r": 0, "t": 0, "b": 0},
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            showlegend=False,
            annotations=[
                {
                    "text": f"{ring:.0f}%",
                    "x": 0.5,
                    "y": 0.5,
                    "showarrow": False,
                    "font": {"color": "rgba(255,255,255,0.82)", "size": 12},
                }
            ],
        )
        st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})

    card_close()


# =============================================================================
# CHART COMPONENTS
# =============================================================================


def apply_dark_chart_layout(fig: go.Figure, height: int = 300) -> go.Figure:
    """
    Apply dark theme styling to a Plotly figure.

    Args:
        fig: Plotly figure to style
        height: Chart height in pixels

    Returns:
        Styled Plotly figure
    """
    get_dark_theme()
    fig.update_layout(
        height=height,
        margin={"l": 18, "r": 16, "t": 22, "b": 18},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "rgba(255,255,255,0.82)", "size": 12},
        legend={
            "orientation": "h",
            "yanchor": "top",
            "y": 1.12,
            "xanchor": "center",
            "x": 0.5,
            "bgcolor": "rgba(17,22,40,0.85)",
            "bordercolor": "rgba(255,255,255,0.08)",
            "borderwidth": 1,
            "font": {"color": "rgba(255,255,255,0.78)", "size": 11},
        },
        xaxis={
            "showgrid": True,
            "gridcolor": "rgba(255,255,255,0.05)",
            "zeroline": False,
            "tickfont": {"color": "rgba(255,255,255,0.60)", "size": 11},
            "title": {"font": {"color": "rgba(255,255,255,0.70)", "size": 12}},
            "linecolor": "rgba(255,255,255,0.10)",
            "mirror": False,
        },
        yaxis={
            "showgrid": True,
            "gridcolor": "rgba(255,255,255,0.07)",
            "zeroline": False,
            "tickfont": {"color": "rgba(255,255,255,0.60)", "size": 11},
            "title": {"font": {"color": "rgba(255,255,255,0.70)", "size": 12}},
            "linecolor": "rgba(255,255,255,0.10)",
            "mirror": False,
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
) -> None:
    """
    Render a line chart inside a dark card with glowing effect.

    Args:
        df: DataFrame with data
        x_col: Column name for x-axis
        y_col: Column name for y-axis
        title: Card title
        subtitle: Card subtitle
        show_glow: Whether to show glow effect on line
        color: Line color
    """
    latest = float(df[y_col].iloc[-1]) if len(df) > 0 else 0
    prev = (
        float(df[y_col].iloc[-8]) if len(df) > 8 else float(df[y_col].iloc[0]) if len(df) > 0 else 0
    )
    delta = ((latest - prev) / max(prev, 1e-9)) * 100 if prev != 0 else 0

    delta_class = "positive" if delta >= 0 else "negative"
    arrow = "▲" if delta >= 0 else "▼"
    right_html = f"<span class='delta {delta_class}'>{arrow} {abs(delta):.1f}%</span>"

    card_open(title=title, subtitle=subtitle, right_html=right_html)

    fig = go.Figure()

    # Glow layer
    if show_glow:
        fig.add_trace(
            go.Scatter(
                x=df[x_col],
                y=df[y_col],
                mode="lines",
                line={
                    "color": color.replace(")", ", 0.22)")
                    .replace("rgb", "rgba")
                    .replace("#a855f7", "rgba(168,85,247,0.22)"),
                    "width": 12,
                    "shape": "spline",
                },
                hoverinfo="skip",
            )
        )

    # Main line
    fig.add_trace(
        go.Scatter(
            x=df[x_col],
            y=df[y_col],
            mode="lines+markers",
            line={"color": color, "width": 3, "shape": "spline"},
            marker={"size": 6, "color": color},
            hovertemplate="<b>%{x}</b><br>%{y:.1f}<extra></extra>",
        )
    )

    # Annotation for latest value
    if len(df) > 0:
        fig.add_annotation(
            x=df[x_col].iloc[-1],
            y=latest,
            text=f"{latest:.1f}",
            showarrow=True,
            arrowwidth=1,
            arrowcolor="rgba(255,255,255,0.35)",
            bgcolor="#7c3aed",
            bordercolor="rgba(255,255,255,0.20)",
            font={"color": "white", "size": 11},
            borderpad=6,
            ax=-30,
            ay=-35,
        )

    apply_dark_chart_layout(fig, height=220)
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
        st.markdown(
            f"""
            <div style='display:flex; align-items:center; justify-content:space-between; color:rgba(255,255,255,0.70); font-size:12px; padding:4px 2px;'>
                <span style='display:flex; align-items:center; gap:8px;'>
                    <span style='width:10px; height:10px; border-radius:3px; background:{color};'></span>
                    {row[labels_col]}
                </span>
                <span style='font-weight:600;'>{pct:.0f}%</span>
            </div>
            """,
            unsafe_allow_html=True,
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


def render_section_title(title: str, subtitle: str = "") -> None:
    """
    Render a section title with optional subtitle.

    Args:
        title: Section title
        subtitle: Optional subtitle
    """
    st.markdown(f"<div class='section-header'>{title}</div>", unsafe_allow_html=True)
    if subtitle:
        st.markdown(f"<div class='section-sub'>{subtitle}</div>", unsafe_allow_html=True)


def render_status_overview(green: int, amber: int, red: int) -> None:
    """
    Render a compact status overview with pills.

    Args:
        green: Count of green status items
        amber: Count of amber status items
        red: Count of red status items
    """
    st.markdown(
        f"""
        <div style="display: flex; gap: 8px;">
            <div class="status-pill status-green">✓ {green}</div>
            <div class="status-pill status-amber">⚠ {amber}</div>
            <div class="status-pill status-red">✕ {red}</div>
        </div>
        """,
        unsafe_allow_html=True,
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
    st.markdown(
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
        """,
        unsafe_allow_html=True,
    )

    # Render sidebar with buttons for navigation
    st.markdown('<div class="analytics-sidebar-nav">', unsafe_allow_html=True)
    st.markdown(
        '<div class="analytics-sidebar-title">Analytics Modules</div>', unsafe_allow_html=True
    )

    selected = st.session_state.analytics_section

    for key, icon, label, _desc in sections:
        is_active = key == selected
        if st.button(
            f"{icon}  {label}",
            key=f"nav_{key}",
            use_container_width=True,
            type="primary" if is_active else "secondary",
        ):
            st.session_state.analytics_section = key
            selected = key
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    # Show description for selected section
    st.caption(f"📍 {desc_map.get(selected, '')}")

    return selected
