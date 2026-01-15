"""Help & Documentation.

Thin Streamlit wrapper around `analytics_hub_platform.app.pages.help`.
"""

import streamlit as st

st.set_page_config(
    page_title="Help | Analytics Hub",
    page_icon="❓",
    layout="wide",
    initial_sidebar_state="collapsed",
)

from analytics_hub_platform.ui.page_init import initialize_page
from analytics_hub_platform.app.components import (
    render_page_header,
    render_sidebar,
    spacer,
)
from analytics_hub_platform.app.pages.help import render_help_page

# Initialize page (session state, database, theme)
initialize_page()

side_col, main_col = st.columns([0.2, 0.8], gap="large")

with side_col:
    render_sidebar(active="Help")

with main_col:
    render_page_header("Help & Documentation", "About, methodology, and FAQs", "❓")
    spacer("md")
    render_help_page()
