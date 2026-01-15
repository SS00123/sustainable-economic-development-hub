"""
HTML Rendering Utilities
Sustainable Economic Development Analytics Hub
Eng. Sultan Albuqami

Safe HTML rendering with fallback for Streamlit version compatibility.
Works with Streamlit 1.28+ (uses st.markdown fallback) and 1.33+ (uses st.html).
"""

from __future__ import annotations

from functools import lru_cache
from typing import TYPE_CHECKING

import streamlit as st

if TYPE_CHECKING:
    pass


@lru_cache(maxsize=1)
def _has_st_html() -> bool:
    """Check if st.html is available (Streamlit 1.33+)."""
    return hasattr(st, "html") and callable(getattr(st, "html", None))


def render_html(html_content: str, *, height: int | None = None) -> None:
    """
    Render HTML content safely with version fallback.

    Uses st.html() if available (Streamlit 1.33+), otherwise falls back to
    st.markdown() with unsafe_allow_html=True.

    Args:
        html_content: The HTML string to render
        height: Optional height for components.html fallback (ignored for st.html/st.markdown)

    Note:
        For isolated HTML that needs iframe sandboxing, use render_html_isolated() instead.
    """
    if _has_st_html():
        st.html(html_content)
    else:
        # Fallback for older Streamlit versions
        st.markdown(html_content, unsafe_allow_html=True)


def render_html_isolated(html_content: str, height: int = 400, scrolling: bool = False) -> None:
    """
    Render HTML in an isolated iframe using streamlit.components.v1.html.

    Use this for:
    - Complex JavaScript that shouldn't affect main page
    - Third-party widgets
    - Content that needs sandboxing

    Args:
        html_content: The HTML string to render
        height: Height of the iframe in pixels
        scrolling: Whether to allow scrolling in the iframe
    """
    import streamlit.components.v1 as components

    components.html(html_content, height=height, scrolling=scrolling)


def render_css(css_content: str) -> None:
    """
    Inject CSS styles into the page.

    Wraps the CSS in <style> tags and renders using the safe render_html function.

    Args:
        css_content: Raw CSS string (without <style> tags)
    """
    # Ensure we don't double-wrap
    if not css_content.strip().startswith("<style"):
        css_content = f"<style>{css_content}</style>"
    render_html(css_content)


def render_spacer(height: int = 24) -> None:
    """
    Render a vertical spacer.

    Args:
        height: Height in pixels
    """
    render_html(f"<div style='height: {height}px;'></div>")


def render_anchor(anchor_id: str, height: int = 8) -> None:
    """
    Render an anchor point for navigation.

    Args:
        anchor_id: The ID for the anchor element
        height: Height in pixels
    """
    render_html(f"<div id='{anchor_id}' style='height: {height}px;'></div>")


def get_rtl_wrapper_start(language: str = "en") -> str:
    """
    Get the opening RTL wrapper div if language is RTL.

    Args:
        language: Language code (e.g., 'en', 'ar')

    Returns:
        Opening div tag with dir attribute, or empty string for LTR
    """
    if language in ("ar", "he", "fa", "ur"):
        return '<div dir="rtl" style="text-align: right;">'
    return '<div dir="ltr">'


def get_rtl_wrapper_end() -> str:
    """Get the closing RTL wrapper div."""
    return "</div>"


def is_rtl_language(language: str) -> bool:
    """
    Check if a language is right-to-left.

    Args:
        language: Language code

    Returns:
        True if the language is RTL
    """
    return language in ("ar", "he", "fa", "ur")


def get_text_direction(language: str) -> str:
    """
    Get the text direction for a language.

    Args:
        language: Language code

    Returns:
        'rtl' or 'ltr'
    """
    return "rtl" if is_rtl_language(language) else "ltr"


def get_text_align(language: str) -> str:
    """
    Get the text alignment for a language.

    Args:
        language: Language code

    Returns:
        'right' or 'left'
    """
    return "right" if is_rtl_language(language) else "left"


def render_rtl_aware_container_start(language: str = "en") -> None:
    """
    Render the start of an RTL-aware container.

    This should be called once at the top of the main content area.

    Args:
        language: Language code
    """
    direction = get_text_direction(language)
    align = get_text_align(language)

    # RTL-specific bullet and list fixes
    rtl_css = ""
    if is_rtl_language(language):
        rtl_css = """
        <style>
            /* RTL Bullet List Fixes */
            [dir="rtl"] ul, [dir="rtl"] ol {
                padding-right: 1.5em;
                padding-left: 0;
                margin-right: 0;
                margin-left: 0;
            }
            [dir="rtl"] li {
                text-align: right;
            }
            [dir="rtl"] li::marker {
                unicode-bidi: isolate;
            }
            /* RTL Card and Component Alignment */
            [dir="rtl"] .dark-card {
                text-align: right;
            }
            [dir="rtl"] .card-title,
            [dir="rtl"] .card-value,
            [dir="rtl"] .card-sub {
                text-align: right;
            }
            /* RTL Delta badges */
            [dir="rtl"] .delta {
                flex-direction: row-reverse;
            }
            /* RTL Navigation */
            [dir="rtl"] .nav a {
                flex-direction: row-reverse;
            }
            /* RTL Form elements */
            [dir="rtl"] .stSelectbox label,
            [dir="rtl"] .stTextInput label {
                text-align: right;
            }
        </style>
        """

    render_html(f'{rtl_css}<div dir="{direction}" style="text-align: {align};">')


def render_rtl_aware_container_end() -> None:
    """Render the end of an RTL-aware container."""
    render_html("</div>")


# Convenience aliases
html = render_html
css = render_css
spacer = render_spacer
anchor = render_anchor
