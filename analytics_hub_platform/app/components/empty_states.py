"""Empty state components for loading, error, and no-data scenarios."""

from __future__ import annotations

import streamlit as st

from analytics_hub_platform.app.styles.compat import (
    COLORS,
    RADIUS,
    SPACING,
    TYPOGRAPHY,
)
from analytics_hub_platform.ui.html import render_html


def render_empty_state(
    title: str = "No data available",
    message: str = "",
    icon: str = "📭",
    action_label: str = "",
    action_key: str = "",
) -> bool:
    """Render an empty state placeholder.

    Args:
        title: Main title text
        message: Optional description message
        icon: Emoji or icon character
        action_label: Optional button label
        action_key: Key for action button

    Returns:
        True if action button was clicked, False otherwise
    """
    message_html = (
        f'<div style="font-size: {TYPOGRAPHY.body}; color: {COLORS.text_muted}; margin-top: {SPACING.sm};">'
        f"{message}</div>"
        if message
        else ""
    )

    render_html(
        f"""
        <div style="
            text-align: center;
            padding: {SPACING.xxl} {SPACING.xl};
            background: {COLORS.bg_card};
            border-radius: {RADIUS.lg};
            border: 1px dashed {COLORS.border};
            margin: {SPACING.lg} 0;
        ">
            <div style="font-size: 48px; margin-bottom: {SPACING.md}; opacity: 0.6;">{icon}</div>
            <div style="font-size: {TYPOGRAPHY.heading3}; font-weight: 600; color: {COLORS.text_secondary};">
                {title}
            </div>
            {message_html}
        </div>
    """
    )

    if action_label and action_key:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            return st.button(action_label, key=action_key, use_container_width=True)
    return False


def render_loading_state(
    message: str = "Loading...",
    show_spinner: bool = True,
) -> None:
    """Render a loading state placeholder.

    Args:
        message: Loading message text
        show_spinner: Whether to show a spinner animation
    """
    spinner_html = (
        '<div class="loading-spinner" style="'
        "width: 40px; height: 40px; border: 3px solid rgba(255,255,255,0.1); "
        f"border-top-color: {COLORS.primary}; border-radius: 50%; "
        'animation: spin 1s linear infinite; margin: 0 auto 16px auto;"></div>'
        if show_spinner
        else ""
    )

    render_html(
        f"""
        <style>
            @keyframes spin {{
                to {{ transform: rotate(360deg); }}
            }}
        </style>
        <div style="
            text-align: center;
            padding: {SPACING.xxl} {SPACING.xl};
            background: {COLORS.bg_card};
            border-radius: {RADIUS.lg};
            margin: {SPACING.lg} 0;
        ">
            {spinner_html}
            <div style="font-size: {TYPOGRAPHY.body}; color: {COLORS.text_muted};">
                {message}
            </div>
        </div>
    """
    )


def render_error_state(
    title: str = "Something went wrong",
    message: str = "",
    error_code: str = "",
    retry_label: str = "Retry",
    retry_key: str = "",
) -> bool:
    """Render an error state placeholder.

    Args:
        title: Error title
        message: Error description
        error_code: Optional error code
        retry_label: Retry button label
        retry_key: Key for retry button

    Returns:
        True if retry button was clicked, False otherwise
    """
    message_html = (
        f'<div style="font-size: {TYPOGRAPHY.body}; color: {COLORS.text_muted}; margin-top: {SPACING.sm};">'
        f"{message}</div>"
        if message
        else ""
    )

    code_html = (
        f'<div style="font-size: {TYPOGRAPHY.small}; color: {COLORS.text_muted}; '
        f'margin-top: {SPACING.md}; font-family: monospace; opacity: 0.6;">'
        f"Error code: {error_code}</div>"
        if error_code
        else ""
    )

    render_html(
        f"""
        <div style="
            text-align: center;
            padding: {SPACING.xxl} {SPACING.xl};
            background: {COLORS.bg_card};
            border-radius: {RADIUS.lg};
            border: 1px solid {COLORS.status_red}40;
            margin: {SPACING.lg} 0;
        ">
            <div style="font-size: 48px; margin-bottom: {SPACING.md};">⚠️</div>
            <div style="font-size: {TYPOGRAPHY.heading3}; font-weight: 600; color: {COLORS.status_red};">
                {title}
            </div>
            {message_html}
            {code_html}
        </div>
    """
    )

    if retry_key:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            return st.button(retry_label, key=retry_key, use_container_width=True)
    return False


__all__ = [
    "render_empty_state",
    "render_loading_state",
    "render_error_state",
]
