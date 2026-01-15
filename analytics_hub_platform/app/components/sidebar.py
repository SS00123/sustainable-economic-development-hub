"""Sidebar navigation.

This replaces direct usage of the legacy `ui.dark_components.render_sidebar`.
"""

from __future__ import annotations

import streamlit as st

from analytics_hub_platform.ui.html import render_html


def render_sidebar(active: str = "Dashboard") -> None:
    """Render a left navigation sidebar using Streamlit's `page_link`.

    Args:
        active: Human-readable page name used to highlight the current page.
    """

    items = [
        ("Dashboard", "📊", "pages/01_Dashboard.py"),
        ("KPIs", "📈", "pages/02_KPIs.py"),
        ("Trends", "📊", "pages/03_Trends.py"),
        ("Data", "📋", "pages/04_Data.py"),
        ("Settings", "⚙️", "pages/05_Settings.py"),
        ("Help", "❓", "pages/06_Help.py"),
        ("Diagnostics", "🩺", "pages/07_Diagnostics.py"),
    ]

    render_html(
        """
        <style>
          .ahp-sidebar-title {
            font-weight: 800;
            font-size: 14px;
            margin: 6px 0 0 0;
          }
          .ahp-sidebar-subtitle {
            font-size: 11px;
            opacity: 0.75;
            margin: 2px 0 12px 0;
          }
          .ahp-active-pill {
            display: inline-block;
            padding: 2px 8px;
            border-radius: 999px;
            font-size: 10px;
            margin-top: 10px;
            background: rgba(168, 85, 247, 0.18);
            border: 1px solid rgba(168, 85, 247, 0.28);
          }
        </style>
        """
    )

    st.markdown("### Sustainable Economic Development")
    st.caption("Analytics Hub")

    # Active indicator (simple, audit-friendly)
    st.markdown(f"<span class='ahp-active-pill'>Active: {active}</span>", unsafe_allow_html=True)

    st.divider()

    for name, icon, path in items:
        label = f"{icon} {name}"
        st.page_link(path, label=label)
