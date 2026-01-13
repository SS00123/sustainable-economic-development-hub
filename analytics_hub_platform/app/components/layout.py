"""Layout utilities and shared page scaffolding."""

from __future__ import annotations

import streamlit as st

from analytics_hub_platform.ui.html import render_html


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


def page_container(content_func):
    """Wrapper to create consistent page layout with max-width and alignment."""
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


def spacer(size: str = "md") -> None:
    """Add vertical spacing."""
    size_map = {
        "xs": "4px",
        "sm": "8px",
        "md": "16px",
        "lg": "24px",
        "xl": "32px",
    }
    height = size_map.get(size, "16px")
    render_html(f'<div style="height: {height};"></div>')
