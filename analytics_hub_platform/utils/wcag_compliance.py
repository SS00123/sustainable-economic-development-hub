"""
WCAG 2.1 AA Compliance Module
Sustainable Economic Development Analytics Hub
Ministry of Economy and Planning

This module provides WCAG 2.1 Level AA compliant utilities for the Analytics Hub.
Includes: accessible components, keyboard navigation, ARIA support, RTL handling.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any

import streamlit as st

from analytics_hub_platform.ui.html import render_html


class WCAGLevel(str, Enum):
    """WCAG conformance levels."""

    A = "A"
    AA = "AA"
    AAA = "AAA"


@dataclass
class AccessibleComponentConfig:
    """Configuration for accessible components."""

    # WCAG 2.1 AA Requirements
    min_contrast_ratio: float = 4.5  # For normal text
    min_contrast_ratio_large: float = 3.0  # For large text (18pt+)
    min_touch_target: int = 44  # Minimum touch target size in pixels
    min_focus_indicator: int = 2  # Minimum focus indicator width in pixels

    # Timing
    min_focus_visible_time: int = 2000  # Minimum time focus must be visible (ms)
    animation_duration_limit: int = 5000  # Max animation duration before pause (ms)

    # Text
    min_line_height: float = 1.5  # Minimum line height for readability
    max_line_length: int = 80  # Maximum characters per line

    # Language
    lang: str = "en"
    dir: str = "ltr"


# =============================================================================
# ACCESSIBLE CSS GENERATION
# =============================================================================


def get_wcag_compliant_css(
    rtl: bool = False,
    high_contrast: bool = False,
    large_text: bool = False,
) -> str:
    """
    Generate WCAG 2.1 AA compliant CSS.

    Args:
        rtl: Enable right-to-left layout
        high_contrast: Enable high contrast mode
        large_text: Enable larger text sizes

    Returns:
        CSS string with accessibility features
    """
    direction = "rtl" if rtl else "ltr"
    text_align = "right" if rtl else "left"
    base_font_size = "18px" if large_text else "16px"

    # High contrast color overrides
    if high_contrast:
        text_color = "#FFFFFF"
        bg_color = "#000000"
        border_color = "#FFFFFF"
        link_color = "#FFFF00"
        focus_color = "#00FFFF"
    else:
        text_color = "rgba(255, 255, 255, 0.95)"
        bg_color = "inherit"
        border_color = "rgba(255, 255, 255, 0.12)"
        link_color = "#22d3ee"
        focus_color = "#2563eb"

    return f"""
    <style>
    /* =================================================================
       WCAG 2.1 AA Compliant Styles
       ================================================================= */

    /* ---- Global Accessibility Settings ---- */
    :root {{
        --a11y-text-color: {text_color};
        --a11y-bg-color: {bg_color};
        --a11y-border-color: {border_color};
        --a11y-link-color: {link_color};
        --a11y-focus-color: {focus_color};
        --a11y-focus-width: 3px;
        --a11y-min-target: 44px;
        --a11y-font-size: {base_font_size};
        --a11y-line-height: 1.5;
    }}

    /* ---- Document Direction (RTL/LTR) ---- */
    html, body, [data-testid="stAppViewContainer"] {{
        direction: {direction};
        text-align: {text_align};
    }}

    /* ---- Base Typography for Readability ---- */
    body {{
        font-size: var(--a11y-font-size);
        line-height: var(--a11y-line-height);
        letter-spacing: 0.01em;
    }}

    /* Ensure text is readable - WCAG 1.4.12 */
    p, li, td, th, label {{
        line-height: var(--a11y-line-height);
        max-width: 80ch; /* Limit line length */
    }}

    /* ---- Focus Indicators (WCAG 2.4.7, 2.4.11) ---- */
    *:focus {{
        outline: var(--a11y-focus-width) solid var(--a11y-focus-color) !important;
        outline-offset: 2px !important;
    }}

    *:focus:not(:focus-visible) {{
        outline: none !important;
    }}

    *:focus-visible {{
        outline: var(--a11y-focus-width) solid var(--a11y-focus-color) !important;
        outline-offset: 2px !important;
        box-shadow: 0 0 0 6px rgba(37, 99, 235, 0.25) !important;
    }}

    /* ---- Touch Targets (WCAG 2.5.5) ---- */
    button,
    [role="button"],
    input[type="checkbox"],
    input[type="radio"],
    select,
    .stButton > button,
    .stSelectbox > div,
    [data-testid="stBaseButton-secondary"] {{
        min-height: var(--a11y-min-target) !important;
        min-width: var(--a11y-min-target) !important;
        padding: 8px 16px !important;
    }}

    /* ---- Skip Links (WCAG 2.4.1) ---- */
    .skip-link {{
        position: absolute;
        top: -100px;
        left: 0;
        background: var(--a11y-focus-color);
        color: #FFFFFF;
        padding: 12px 24px;
        z-index: 10000;
        font-weight: bold;
        text-decoration: none;
        border-radius: 0 0 8px 0;
        transition: top 0.15s ease;
    }}

    .skip-link:focus {{
        top: 0;
        outline: none !important;
    }}

    /* ---- Screen Reader Only Content ---- */
    .sr-only,
    .visually-hidden {{
        position: absolute !important;
        width: 1px !important;
        height: 1px !important;
        padding: 0 !important;
        margin: -1px !important;
        overflow: hidden !important;
        clip: rect(0, 0, 0, 0) !important;
        white-space: nowrap !important;
        border: 0 !important;
    }}

    /* ---- Reduced Motion (WCAG 2.3.3) ---- */
    @media (prefers-reduced-motion: reduce) {{
        *,
        *::before,
        *::after {{
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: 0.01ms !important;
            scroll-behavior: auto !important;
        }}

        .dark-card:hover {{
            transform: none !important;
        }}
    }}

    /* ---- High Contrast Mode (WCAG 1.4.11) ---- */
    @media (prefers-contrast: high) {{
        * {{
            border-color: var(--a11y-border-color) !important;
        }}

        .dark-card,
        .kpi-card,
        .stMetric {{
            border: 2px solid var(--a11y-border-color) !important;
            background: var(--a11y-bg-color) !important;
        }}

        button,
        [role="button"] {{
            border: 2px solid currentColor !important;
        }}
    }}

    /* ---- Error States (WCAG 1.4.1) ---- */
    .error-message,
    [role="alert"] {{
        color: #ff6b6b;
        border-left: 4px solid #ff6b6b;
        padding-left: 12px;
        font-weight: 500;
    }}

    /* Error icon for non-color indication */
    .error-message::before {{
        content: "⚠️ ";
    }}

    /* ---- Success States ---- */
    .success-message {{
        color: #51cf66;
        border-left: 4px solid #51cf66;
        padding-left: 12px;
    }}

    .success-message::before {{
        content: "✓ ";
    }}

    /* ---- Link Styling (WCAG 1.4.1) ---- */
    a {{
        color: var(--a11y-link-color);
        text-decoration: underline;
        text-underline-offset: 3px;
    }}

    a:hover {{
        text-decoration-thickness: 2px;
    }}

    /* ---- Form Labels (WCAG 1.3.1, 3.3.2) ---- */
    label {{
        display: block;
        margin-bottom: 4px;
        font-weight: 500;
    }}

    /* Required field indicator */
    .required::after {{
        content: " *";
        color: #ff6b6b;
    }}

    /* ---- Data Tables (WCAG 1.3.1) ---- */
    table {{
        border-collapse: collapse;
        width: 100%;
    }}

    th, td {{
        padding: 12px;
        text-align: {text_align};
        border-bottom: 1px solid var(--a11y-border-color);
    }}

    th {{
        font-weight: bold;
        background: rgba(255, 255, 255, 0.05);
    }}

    /* ---- Chart Accessibility ---- */
    .chart-description {{
        position: absolute;
        left: -9999px;
    }}

    /* ---- RTL Specific Styles ---- */
    {
        ""
        if not rtl
        else '''
    .nav a .dot {
        margin-left: 10px;
        margin-right: 0;
    }

    .delta {
        margin-right: 10px;
        margin-left: 0;
    }

    .card-sub {
        text-align: right;
    }

    [dir="rtl"] .stSelectbox > div {
        text-align: right;
    }
    '''
    }

    /* ---- Print Styles (WCAG) ---- */
    @media print {{
        * {{
            background: white !important;
            color: black !important;
        }}

        a {{
            text-decoration: underline;
        }}

        a[href]::after {{
            content: " (" attr(href) ")";
        }}
    }}
    </style>
    """


# =============================================================================
# ACCESSIBLE COMPONENT HELPERS
# =============================================================================


def accessible_card(
    title: str,
    content: str,
    *,
    aria_label: str | None = None,
    role: str = "region",
    level: int = 2,
    landmark: bool = True,
) -> str:
    """
    Generate accessible card HTML with proper ARIA attributes.

    Args:
        title: Card title
        content: Card content HTML
        aria_label: Custom ARIA label
        role: ARIA role (region, article, etc.)
        level: Heading level (1-6)
        landmark: Whether this is a landmark region

    Returns:
        Accessible HTML string
    """
    aria_labelledby = f"card-title-{hash(title) % 10000}"
    aria_attrs = (
        f'aria-labelledby="{aria_labelledby}"' if not aria_label else f'aria-label="{aria_label}"'
    )
    role_attr = f'role="{role}"' if landmark else ""

    return f"""
    <div class="dark-card" {role_attr} {aria_attrs} tabindex="0">
        <h{level} id="{aria_labelledby}" class="card-title">{title}</h{level}>
        <div class="card-content">
            {content}
        </div>
    </div>
    """


def accessible_metric(
    label: str,
    value: str,
    delta: str | None = None,
    delta_description: str | None = None,
    unit: str = "",
) -> str:
    """
    Generate accessible metric display with screen reader support.

    Args:
        label: Metric label
        value: Current value
        delta: Change value (e.g., "+5.2%")
        delta_description: Description of change for screen readers
        unit: Unit of measurement

    Returns:
        Accessible HTML string
    """
    # Screen reader description
    sr_description = f"{label}: {value}"
    if unit:
        sr_description += f" {unit}"
    if delta and delta_description:
        sr_description += f", {delta_description}"

    delta_html = ""
    if delta:
        is_positive = delta.startswith("+") or (delta[0].isdigit() and float(delta.rstrip("%")) > 0)
        delta_class = "positive" if is_positive else "negative"
        arrow = "▲" if is_positive else "▼"
        delta_html = f"""
        <span class="delta {delta_class}" aria-hidden="true">
            {arrow} {delta}
        </span>
        """

    return f"""
    <div class="metric-container" role="status" aria-live="polite">
        <span class="sr-only">{sr_description}</span>
        <div class="card-title" aria-hidden="true">{label}</div>
        <div class="card-value" aria-hidden="true">
            {value}
            <span class="unit">{unit}</span>
            {delta_html}
        </div>
    </div>
    """


def accessible_chart_wrapper(
    chart_element: Any,
    title: str,
    description: str,
    data_summary: str | None = None,
) -> None:
    """
    Wrap a chart with accessible description for screen readers.

    Args:
        chart_element: Streamlit chart element
        title: Chart title
        description: Description of what the chart shows
        data_summary: Summary of key data points
    """
    # Generate unique ID
    chart_id = f"chart-{hash(title) % 10000}"

    # Screen reader description
    sr_text = f"Chart: {title}. {description}"
    if data_summary:
        sr_text += f" Key data: {data_summary}"

    render_html(
        f"""
        <figure role="img" aria-labelledby="{chart_id}-desc" tabindex="0">
            <figcaption id="{chart_id}-desc" class="sr-only">
                {sr_text}
            </figcaption>
        """
    )

    # Render the chart
    if callable(chart_element):
        chart_element()

    render_html("</figure>")


def accessible_data_table(
    headers: list[str],
    rows: list[list[str]],
    caption: str,
    sortable: bool = False,
) -> str:
    """
    Generate accessible data table HTML.

    Args:
        headers: Column headers
        rows: Table data rows
        caption: Table caption for screen readers
        sortable: Whether columns are sortable

    Returns:
        Accessible table HTML
    """
    # Generate header cells
    header_cells = ""
    for header in headers:
        scope = 'scope="col"'
        sort_attr = 'aria-sort="none"' if sortable else ""
        header_cells += f"<th {scope} {sort_attr}>{header}</th>"

    # Generate data rows
    body_rows = ""
    for row in rows:
        cells = ""
        for i, cell in enumerate(row):
            if i == 0:
                # First column as row header
                cells += f'<th scope="row">{cell}</th>'
            else:
                cells += f"<td>{cell}</td>"
        body_rows += f"<tr>{cells}</tr>"

    return f"""
    <table role="table" aria-label="{caption}">
        <caption class="sr-only">{caption}</caption>
        <thead>
            <tr>{header_cells}</tr>
        </thead>
        <tbody>
            {body_rows}
        </tbody>
    </table>
    """


def inject_skip_link(main_content_id: str = "main-content") -> None:
    """
    Inject skip link for keyboard navigation (WCAG 2.4.1).

    Args:
        main_content_id: ID of main content area
    """
    render_html(
        f"""
        <a href="#{main_content_id}" class="skip-link">
            Skip to main content
        </a>
        """
    )


def inject_live_region() -> None:
    """
    Inject ARIA live region for dynamic content announcements.
    """
    render_html(
        """
        <div id="live-region"
             role="status"
             aria-live="polite"
             aria-atomic="true"
             class="sr-only">
        </div>
        """
    )


# =============================================================================
# RTL (RIGHT-TO-LEFT) SUPPORT
# =============================================================================


def get_rtl_css() -> str:
    """
    Get CSS for right-to-left (RTL) layout support.

    Returns:
        RTL-specific CSS
    """
    return """
    <style>
    /* RTL Layout Support */
    [dir="rtl"] {
        direction: rtl;
        text-align: right;
    }

    [dir="rtl"] .dark-card {
        direction: rtl;
    }

    [dir="rtl"] .nav a {
        flex-direction: row-reverse;
    }

    [dir="rtl"] .delta {
        margin-right: 10px;
        margin-left: 0;
    }

    [dir="rtl"] .stSelectbox {
        direction: rtl;
    }

    [dir="rtl"] .card-value {
        direction: ltr; /* Keep numbers LTR */
        unicode-bidi: embed;
    }

    [dir="rtl"] .topbar {
        flex-direction: row-reverse;
    }

    /* Arabic font stack */
    [lang="ar"] {
        font-family: 'Noto Sans Arabic', 'Segoe UI', 'Arial', sans-serif;
    }
    </style>
    """


def set_document_direction(lang: str = "en") -> None:
    """
    Set document direction based on language.

    Args:
        lang: Language code (en, ar, etc.)
    """
    direction = "rtl" if lang in ["ar", "he", "fa", "ur"] else "ltr"

    render_html(
        f"""
        <script>
            document.documentElement.setAttribute('dir', '{direction}');
            document.documentElement.setAttribute('lang', '{lang}');
        </script>
        """
    )


# =============================================================================
# KEYBOARD NAVIGATION
# =============================================================================


def get_keyboard_navigation_js() -> str:
    """
    Get JavaScript for enhanced keyboard navigation.

    Returns:
        JavaScript for keyboard navigation
    """
    return """
    <script>
    (function() {
        // Enhanced keyboard navigation
        document.addEventListener('keydown', function(e) {
            // Skip link activation with Tab
            if (e.key === 'Tab') {
                document.body.classList.add('keyboard-navigation');
            }

            // Escape to close modals/dropdowns
            if (e.key === 'Escape') {
                const activeElement = document.activeElement;
                if (activeElement && activeElement.blur) {
                    activeElement.blur();
                }
            }

            // Arrow key navigation for card grids
            if (['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight'].includes(e.key)) {
                const cards = Array.from(document.querySelectorAll('.dark-card[tabindex="0"]'));
                const currentIndex = cards.indexOf(document.activeElement);

                if (currentIndex !== -1) {
                    let nextIndex = currentIndex;

                    switch(e.key) {
                        case 'ArrowRight':
                        case 'ArrowDown':
                            nextIndex = (currentIndex + 1) % cards.length;
                            break;
                        case 'ArrowLeft':
                        case 'ArrowUp':
                            nextIndex = (currentIndex - 1 + cards.length) % cards.length;
                            break;
                    }

                    if (nextIndex !== currentIndex) {
                        e.preventDefault();
                        cards[nextIndex].focus();
                    }
                }
            }
        });

        // Remove keyboard navigation class on mouse use
        document.addEventListener('mousedown', function() {
            document.body.classList.remove('keyboard-navigation');
        });
    })();
    </script>
    """


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================


def announce(message: str, priority: str = "polite") -> None:
    """
    Announce a message to screen readers via live region.

    Args:
        message: Message to announce
        priority: 'polite' or 'assertive'
    """
    render_html(
        f"""
        <script>
            const liveRegion = document.getElementById('live-region');
            if (liveRegion) {{
                liveRegion.setAttribute('aria-live', '{priority}');
                liveRegion.textContent = '{message}';
            }}
        </script>
        """
    )


def format_number_accessible(
    value: float,
    lang: str = "en",
    precision: int = 1,
) -> str:
    """
    Format number for accessibility with proper localization.

    Args:
        value: Number to format
        lang: Language code
        precision: Decimal precision

    Returns:
        Formatted number string
    """
    if lang == "ar":
        # Arabic-Indic numerals
        arabic_numerals = "٠١٢٣٤٥٦٧٨٩"
        formatted = f"{value:,.{precision}f}"
        return formatted.translate(str.maketrans("0123456789", arabic_numerals))
    else:
        return f"{value:,.{precision}f}"


def get_accessibility_statement() -> str:
    """
    Get accessibility statement for the application.

    Returns:
        HTML accessibility statement
    """
    return """
    <div role="region" aria-label="Accessibility Statement">
        <h2>Accessibility Statement</h2>
        <p>
            The Sustainable Economic Development Analytics Hub is committed to ensuring
            digital accessibility for people with disabilities. We are continually
            improving the user experience for everyone and applying the relevant
            accessibility standards.
        </p>

        <h3>Conformance Status</h3>
        <p>
            This application aims to conform to WCAG 2.1 Level AA. We have implemented:
        </p>
        <ul>
            <li>Keyboard navigation support</li>
            <li>Screen reader compatibility</li>
            <li>Sufficient color contrast (4.5:1 minimum)</li>
            <li>Focus indicators on interactive elements</li>
            <li>Alternative text for charts and images</li>
            <li>Proper heading hierarchy</li>
            <li>Skip navigation links</li>
            <li>ARIA landmarks and labels</li>
            <li>Right-to-left (RTL) language support</li>
        </ul>

        <h3>Feedback</h3>
        <p>
            We welcome your feedback on the accessibility of this application.
            Please contact us if you encounter accessibility barriers.
        </p>
    </div>
    """

