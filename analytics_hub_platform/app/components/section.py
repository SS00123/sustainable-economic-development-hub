"""Section UI components: titles and status overviews.

Canonical implementations migrated from ui.dark_components.
"""

from __future__ import annotations

from analytics_hub_platform.ui.html import render_html


def render_section_title(title: str, subtitle: str = "", icon: str = "") -> None:
    """
    Render a premium section title with gradient line and optional icon.

    Args:
        title: Section title
        subtitle: Optional subtitle
        icon: Optional emoji icon
    """
    icon_html = f"<span style='margin-right: 8px;'>{icon}</span>" if icon else ""
    render_html(
        f"""
        <div class='section-header' style='
            font-size: 20px;
            font-weight: 700;
            margin: 32px 0 14px 0;
        '>
            {icon_html}{title}
        </div>
        """
    )
    if subtitle:
        render_html(
            f"""
            <div class='section-sub' style='
                font-size: 13px;
                color: rgba(255, 255, 255, 0.5);
                margin: -8px 0 20px 2px;
            '>
                {subtitle}
            </div>
            """
        )


def render_status_overview(green: int, amber: int, red: int, total: int | None = None) -> None:
    """
    Render a premium compact status overview with animated pills.

    Args:
        green: Count of green status items
        amber: Count of amber status items
        red: Count of red status items
        total: Optional total count to display
    """
    total_count = total if total is not None else (green + amber + red)
    render_html(
        f"""
        <div style="display: flex; gap: 12px; align-items: center; flex-wrap: wrap;">
            <div class="status-pill status-green" style="cursor: pointer;">
                <span style="font-size: 14px;">✓</span>
                <span style="font-weight: 700;">{green}</span>
                <span style="opacity: 0.7; font-weight: 500;">On Track</span>
            </div>
            <div class="status-pill status-amber" style="cursor: pointer;">
                <span style="font-size: 14px;">⚠</span>
                <span style="font-weight: 700;">{amber}</span>
                <span style="opacity: 0.7; font-weight: 500;">At Risk</span>
            </div>
            <div class="status-pill status-red" style="cursor: pointer;">
                <span style="font-size: 14px;">✕</span>
                <span style="font-weight: 700;">{red}</span>
                <span style="opacity: 0.7; font-weight: 500;">Critical</span>
            </div>
            <div style="
                margin-left: auto;
                padding: 8px 16px;
                background: rgba(255,255,255,0.04);
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 10px;
                font-size: 12px;
                color: rgba(255,255,255,0.6);
            ">
                <span style="font-weight: 600; color: rgba(255,255,255,0.9);">{total_count}</span> KPIs tracked
            </div>
        </div>
        """
    )
