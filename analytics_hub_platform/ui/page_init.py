"""
Page Initialization Utilities
Sustainable Economic Development Analytics Hub
Ministry of Economy and Planning

Provides centralized initialization for all Streamlit pages.
This eliminates repeated boilerplate across page files.

Usage:
    from analytics_hub_platform.ui.page_init import initialize_page

    # Call after st.set_page_config()
    initialize_page()

    # Or with custom options
    initialize_page(apply_theme=True, init_db=True)
"""

import streamlit as st

from analytics_hub_platform.infrastructure.db_init import initialize_database
from analytics_hub_platform.ui.theme import get_dark_css
from analytics_hub_platform.ui.html import render_html
from analytics_hub_platform.ui.ui_components import initialize_page_session_state


def initialize_page(
    apply_theme: bool = True,
    init_db: bool = True,
    init_session: bool = True,
) -> None:
    """
    Initialize a Streamlit page with common setup.

    This function consolidates the repeated initialization boilerplate
    found across all pages:
    - Session state initialization
    - Database initialization (first run only)
    - Dark theme CSS application

    Args:
        apply_theme: Whether to apply the dark theme CSS. Default True.
        init_db: Whether to initialize the database. Default True.
        init_session: Whether to initialize page session state. Default True.

    Example:
        ```python
        import streamlit as st
        from analytics_hub_platform.ui.page_init import initialize_page

        st.set_page_config(page_title="My Page", layout="wide")
        initialize_page()

        # Now render your page content...
        st.title("My Page")
        ```
    """
    # Initialize session state
    if init_session:
        initialize_page_session_state()

    # Initialize database on first run
    if init_db and not st.session_state.get("initialized"):
        initialize_database()
        st.session_state["initialized"] = True

    # Apply dark theme CSS
    if apply_theme:
        render_html(get_dark_css())


def with_page_init(
    apply_theme: bool = True,
    init_db: bool = True,
    init_session: bool = True,
):
    """
    Decorator for page main functions that handles initialization.

    Usage:
        ```python
        @with_page_init()
        def main():
            st.title("My Page")
            # ... rest of page content

        if __name__ == "__main__":
            main()
        ```
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            initialize_page(
                apply_theme=apply_theme,
                init_db=init_db,
                init_session=init_session,
            )
            return func(*args, **kwargs)
        return wrapper
    return decorator


__all__ = ["initialize_page", "with_page_init"]
