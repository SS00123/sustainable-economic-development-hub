"""Theme helpers for Streamlit pages."""

from __future__ import annotations

from analytics_hub_platform.ui.html import render_html
from analytics_hub_platform.ui.theme import get_dark_css


def inject_dark_theme() -> None:
    """Inject the app's dark theme CSS into the current Streamlit page."""
    render_html(get_dark_css())


__all__ = ["inject_dark_theme"]
