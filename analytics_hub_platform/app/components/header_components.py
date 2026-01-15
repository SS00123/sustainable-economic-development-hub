"""Header UI components: top bar and sticky context headers.

Canonical implementations migrated from ui.dark_components.
"""

from __future__ import annotations

from datetime import date, datetime

import streamlit as st

from analytics_hub_platform.ui.html import render_html


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


def render_sticky_header(
    year: int,
    quarter: int,
    region: str,
    language: str,
) -> None:
    """
    Render a sticky header with current filter context.

    Args:
        year: Selected year
        quarter: Selected quarter (1-4)
        region: Selected region name
        language: Selected language code
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
