"""
Dashboard Quick Actions Component
Sustainable Economic Development Analytics Hub

Provides:
- Export buttons (PDF, Excel, CSV)
- Comparison mode toggle
- Data freshness indicator with animation
- Smart alerts panel
- Quick action toolbar
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from typing import Any, Callable

from analytics_hub_platform.ui.html import render_html


def render_quick_actions_bar(
    df: pd.DataFrame,
    year: int,
    quarter: int,
    region: str,
    on_export_csv: Callable[[], None] | None = None,
    on_export_excel: Callable[[], None] | None = None,
    on_refresh: Callable[[], None] | None = None,
    key_prefix: str = "qa",
) -> dict[str, Any]:
    """
    Render a quick actions toolbar with export and utility buttons.

    Args:
        df: Current dashboard data
        year: Selected year
        quarter: Selected quarter
        region: Selected region
        on_export_csv: Callback for CSV export
        on_export_excel: Callback for Excel export
        on_refresh: Callback for data refresh
        key_prefix: Unique key prefix for widgets

    Returns:
        Dict with action results (e.g., comparison_enabled, etc.)
    """
    results: dict[str, Any] = {}

    # Quick actions container
    render_html("""
        <style>
            .quick-actions-bar {
                display: flex;
                gap: 8px;
                padding: 12px 16px;
                background: rgba(30, 41, 59, 0.8);
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 12px;
                margin-bottom: 16px;
                backdrop-filter: blur(8px);
            }
            .qa-btn {
                display: inline-flex;
                align-items: center;
                gap: 6px;
                padding: 8px 16px;
                background: rgba(59, 130, 246, 0.15);
                border: 1px solid rgba(59, 130, 246, 0.3);
                border-radius: 8px;
                color: rgba(255, 255, 255, 0.9);
                font-size: 13px;
                cursor: pointer;
                transition: all 0.2s ease;
            }
            .qa-btn:hover {
                background: rgba(59, 130, 246, 0.25);
                border-color: rgba(59, 130, 246, 0.5);
            }
        </style>
    """)

    col1, col2, col3, col4, col5 = st.columns([1.2, 1.2, 1.2, 1.5, 1])

    with col1:
        # CSV Export
        csv_data = _export_to_csv(df)
        st.download_button(
            label="📥 CSV",
            data=csv_data,
            file_name=f"dashboard_Q{quarter}_{year}.csv",
            mime="text/csv",
            key=f"{key_prefix}_csv",
            use_container_width=True,
        )

    with col2:
        # Excel Export
        try:
            from analytics_hub_platform.utils.export_excel import generate_excel_workbook
            excel_data = generate_excel_workbook(
                data=df,
                title=f"Dashboard Report Q{quarter} {year}",
                summary_metrics=_get_summary_metrics(df),
            )
            st.download_button(
                label="📊 Excel",
                data=excel_data.getvalue(),
                file_name=f"dashboard_Q{quarter}_{year}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key=f"{key_prefix}_excel",
                use_container_width=True,
            )
        except ImportError:
            st.button("📊 Excel", disabled=True, key=f"{key_prefix}_excel_disabled",
                     help="Excel export requires openpyxl", use_container_width=True)

    with col3:
        # Refresh button
        if st.button("🔄 Refresh", key=f"{key_prefix}_refresh", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    with col4:
        # Comparison mode toggle
        results["comparison_enabled"] = st.checkbox(
            "📊 Compare Periods",
            value=st.session_state.get("comparison_mode", False),
            key=f"{key_prefix}_compare",
        )
        if results["comparison_enabled"] != st.session_state.get("comparison_mode", False):
            st.session_state["comparison_mode"] = results["comparison_enabled"]

    with col5:
        # Print / Screenshot hint
        st.button("🖨️ Print", key=f"{key_prefix}_print", use_container_width=True,
                 help="Use Ctrl+P to print this page")

    return results


def render_smart_alerts(
    metrics: dict[str, dict],
    thresholds: dict[str, dict] | None = None,
    max_alerts: int = 5,
) -> list[dict]:
    """
    Render smart alerts based on KPI status and thresholds.

    Args:
        metrics: Dict of KPI metrics with status
        thresholds: Optional custom thresholds
        max_alerts: Maximum number of alerts to show

    Returns:
        List of alert dictionaries
    """
    alerts = []

    # Analyze metrics for alerts
    for kpi_name, kpi_data in metrics.items():
        status = kpi_data.get("status", "gray")
        value = kpi_data.get("value", 0)
        delta = kpi_data.get("delta", 0)

        # Critical: Red status or large negative delta
        if status == "red":
            alerts.append({
                "type": "critical",
                "icon": "🔴",
                "title": f"{_format_kpi_name(kpi_name)} Critical",
                "message": f"Current value: {value:.1f} (below threshold)",
                "kpi": kpi_name,
            })
        elif status == "amber":
            alerts.append({
                "type": "warning",
                "icon": "🟡",
                "title": f"{_format_kpi_name(kpi_name)} Warning",
                "message": f"Approaching threshold. Delta: {delta:+.1f}%",
                "kpi": kpi_name,
            })
        elif delta and delta < -5:
            alerts.append({
                "type": "info",
                "icon": "📉",
                "title": f"{_format_kpi_name(kpi_name)} Declining",
                "message": f"Significant decrease: {delta:.1f}%",
                "kpi": kpi_name,
            })

    # Sort by severity
    severity_order = {"critical": 0, "warning": 1, "info": 2}
    alerts.sort(key=lambda x: severity_order.get(x["type"], 3))

    # Limit alerts
    alerts = alerts[:max_alerts]

    if not alerts:
        render_html("""
            <div style="
                display: flex;
                align-items: center;
                gap: 12px;
                padding: 16px 20px;
                background: rgba(16, 185, 129, 0.1);
                border: 1px solid rgba(16, 185, 129, 0.3);
                border-radius: 12px;
                margin-bottom: 16px;
            ">
                <span style="font-size: 24px;">✅</span>
                <div>
                    <div style="font-weight: 600; color: #10B981;">All Systems Nominal</div>
                    <div style="font-size: 13px; color: rgba(255,255,255,0.6);">
                        No critical alerts at this time
                    </div>
                </div>
            </div>
        """)
    else:
        for alert in alerts:
            bg_color = {
                "critical": "rgba(239, 68, 68, 0.1)",
                "warning": "rgba(245, 158, 11, 0.1)",
                "info": "rgba(59, 130, 246, 0.1)",
            }.get(alert["type"], "rgba(100, 116, 139, 0.1)")

            border_color = {
                "critical": "rgba(239, 68, 68, 0.3)",
                "warning": "rgba(245, 158, 11, 0.3)",
                "info": "rgba(59, 130, 246, 0.3)",
            }.get(alert["type"], "rgba(100, 116, 139, 0.3)")

            render_html(f"""
                <div style="
                    display: flex;
                    align-items: center;
                    gap: 12px;
                    padding: 14px 18px;
                    background: {bg_color};
                    border: 1px solid {border_color};
                    border-radius: 10px;
                    margin-bottom: 10px;
                ">
                    <span style="font-size: 20px;">{alert["icon"]}</span>
                    <div style="flex: 1;">
                        <div style="font-weight: 600; color: rgba(255,255,255,0.95); font-size: 14px;">
                            {alert["title"]}
                        </div>
                        <div style="font-size: 12px; color: rgba(255,255,255,0.6);">
                            {alert["message"]}
                        </div>
                    </div>
                </div>
            """)

    return alerts


def render_comparison_panel(
    current_metrics: dict[str, dict],
    previous_metrics: dict[str, dict],
    current_label: str = "Current Period",
    previous_label: str = "Previous Period",
) -> None:
    """
    Render a side-by-side comparison panel for two periods.

    Args:
        current_metrics: Metrics for current period
        previous_metrics: Metrics for previous period
        current_label: Label for current period
        previous_label: Label for previous period
    """
    render_html(f"""
        <div style="
            background: rgba(30, 41, 59, 0.6);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 16px;
            padding: 20px 24px;
            margin-bottom: 20px;
        ">
            <div style="
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 16px;
                padding-bottom: 12px;
                border-bottom: 1px solid rgba(255, 255, 255, 0.08);
            ">
                <span style="font-weight: 600; color: rgba(255,255,255,0.9);">
                    📊 Period Comparison
                </span>
                <div style="display: flex; gap: 20px; font-size: 13px;">
                    <span style="color: #06B6D4;">● {current_label}</span>
                    <span style="color: #8B5CF6;">● {previous_label}</span>
                </div>
            </div>
    """)

    # Create comparison rows
    cols = st.columns(4)
    kpi_list = list(set(list(current_metrics.keys())[:8]))

    for i, kpi in enumerate(kpi_list):
        with cols[i % 4]:
            curr = current_metrics.get(kpi, {})
            prev = previous_metrics.get(kpi, {})

            curr_val = curr.get("value", 0)
            prev_val = prev.get("value", 0)

            if prev_val != 0:
                change = ((curr_val - prev_val) / prev_val) * 100
            else:
                change = 0

            change_color = "#10B981" if change >= 0 else "#EF4444"
            change_icon = "↑" if change >= 0 else "↓"

            render_html(f"""
                <div style="
                    background: rgba(15, 23, 42, 0.5);
                    border-radius: 10px;
                    padding: 14px;
                    margin-bottom: 12px;
                ">
                    <div style="font-size: 11px; color: rgba(255,255,255,0.5); margin-bottom: 6px;">
                        {_format_kpi_name(kpi)}
                    </div>
                    <div style="display: flex; justify-content: space-between; align-items: baseline;">
                        <span style="font-size: 18px; font-weight: 700; color: #06B6D4;">
                            {curr_val:.1f}
                        </span>
                        <span style="font-size: 13px; color: {change_color};">
                            {change_icon} {abs(change):.1f}%
                        </span>
                    </div>
                    <div style="font-size: 11px; color: rgba(255,255,255,0.4); margin-top: 4px;">
                        vs {prev_val:.1f}
                    </div>
                </div>
            """)

    render_html("</div>")


def render_data_freshness_badge(
    last_updated: datetime | str | None = None,
    is_live: bool = False,
) -> None:
    """
    Render an animated data freshness indicator.

    Args:
        last_updated: Timestamp of last data update
        is_live: Whether data is being updated in real-time
    """
    if last_updated is None:
        last_updated = datetime.now()
    elif isinstance(last_updated, str):
        try:
            last_updated = datetime.fromisoformat(last_updated)
        except ValueError:
            last_updated = datetime.now()

    time_str = last_updated.strftime("%H:%M")
    date_str = last_updated.strftime("%b %d, %Y")

    pulse_animation = """
        @keyframes pulse-dot {
            0%, 100% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.5; transform: scale(1.2); }
        }
    """ if is_live else ""

    pulse_style = "animation: pulse-dot 2s ease-in-out infinite;" if is_live else ""

    render_html(f"""
        <style>{pulse_animation}</style>
        <div style="
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 6px 14px;
            background: rgba(16, 185, 129, 0.1);
            border: 1px solid rgba(16, 185, 129, 0.25);
            border-radius: 20px;
            font-size: 12px;
        ">
            <span style="
                width: 8px;
                height: 8px;
                background: #10B981;
                border-radius: 50%;
                {pulse_style}
            "></span>
            <span style="color: rgba(255,255,255,0.8);">
                Updated {time_str}
            </span>
            <span style="color: rgba(255,255,255,0.4);">
                {date_str}
            </span>
        </div>
    """)


def render_kpi_drill_down(
    kpi_name: str,
    kpi_data: dict,
    historical_data: pd.DataFrame | None = None,
) -> None:
    """
    Render a detailed drill-down view for a KPI.

    Args:
        kpi_name: Name of the KPI
        kpi_data: Current KPI data dictionary
        historical_data: Optional historical data for trend
    """
    value = kpi_data.get("value", 0)
    delta = kpi_data.get("delta", 0)
    status = kpi_data.get("status", "gray")
    target = kpi_data.get("target")
    unit = kpi_data.get("unit", "")

    status_colors = {
        "green": ("#10B981", "On Track"),
        "amber": ("#F59E0B", "Monitor"),
        "red": ("#EF4444", "At Risk"),
        "gray": ("#64748B", "No Data"),
    }
    color, label = status_colors.get(status, ("#64748B", "Unknown"))

    with st.expander(f"📊 {_format_kpi_name(kpi_name)} Details", expanded=False):
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                label="Current Value",
                value=f"{value:.1f}{unit}",
                delta=f"{delta:+.1f}%" if delta else None,
            )

        with col2:
            if target:
                progress = (value / target) * 100 if target else 0
                st.metric(
                    label="Target",
                    value=f"{target:.1f}{unit}",
                    delta=f"{progress:.0f}% achieved",
                )
            else:
                st.metric(label="Target", value="Not Set")

        with col3:
            render_html(f"""
                <div style="text-align: center; padding: 10px;">
                    <div style="
                        display: inline-block;
                        padding: 6px 16px;
                        background: {color}20;
                        border: 1px solid {color}40;
                        border-radius: 20px;
                        color: {color};
                        font-weight: 600;
                        font-size: 13px;
                    ">
                        {label}
                    </div>
                </div>
            """)

        # Historical trend if available
        if historical_data is not None and len(historical_data) > 0:
            st.line_chart(historical_data, height=150)


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def _export_to_csv(df: pd.DataFrame) -> bytes:
    """Export DataFrame to CSV bytes."""
    return df.to_csv(index=False).encode("utf-8-sig")


def _get_summary_metrics(df: pd.DataFrame) -> dict:
    """Extract summary metrics from DataFrame."""
    numeric_cols = df.select_dtypes(include=["number"]).columns
    metrics = {}
    for col in numeric_cols[:10]:  # Limit to first 10
        metrics[col] = df[col].mean()
    return metrics


def _format_kpi_name(kpi_name: str) -> str:
    """Format KPI name for display."""
    return kpi_name.replace("_", " ").title()


def render_theme_toggle(key_prefix: str = "theme") -> bool:
    """
    Render a dark/light theme toggle button.

    Args:
        key_prefix: Unique key prefix for the toggle

    Returns:
        True if dark mode is enabled, False for light mode
    """
    # Initialize theme in session state
    if "dark_mode" not in st.session_state:
        st.session_state["dark_mode"] = True  # Default to dark mode

    is_dark = st.session_state["dark_mode"]

    # Theme toggle button
    col1, col2 = st.columns([0.15, 0.85])
    with col1:
        icon = "🌙" if is_dark else "☀️"
        # Label for tooltip/help text
        mode_label = "Light" if is_dark else "Dark"
        if st.button(
            f"{icon}",
            key=f"{key_prefix}_toggle",
            help=f"Switch to {mode_label} mode",
        ):
            st.session_state["dark_mode"] = not is_dark
            st.rerun()

    return st.session_state["dark_mode"]


def render_bookmark_share_button(
    year: int,
    quarter: int,
    region: str,
    key_prefix: str = "share",
) -> None:
    """
    Render a button that copies the current dashboard state as a shareable URL.

    Args:
        year: Current year filter
        quarter: Current quarter filter
        region: Current region filter
        key_prefix: Unique key prefix
    """
    import urllib.parse

    # Build query parameters
    params = {
        "year": str(year),
        "quarter": str(quarter),
        "region": region,
    }
    query_string = urllib.parse.urlencode(params)

    # Get base URL (simplified for Streamlit)
    base_url = "?tab=Dashboard"

    share_url = f"{base_url}&{query_string}"

    render_html(f"""
        <div style="margin: 8px 0;">
            <div style="
                display: flex;
                align-items: center;
                gap: 10px;
                padding: 12px 16px;
                background: rgba(30, 41, 59, 0.6);
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 10px;
            ">
                <span style="font-size: 16px;">🔗</span>
                <input type="text" value="{share_url}" readonly
                    onclick="this.select(); document.execCommand('copy');"
                    style="
                        flex: 1;
                        background: transparent;
                        border: none;
                        color: rgba(255,255,255,0.7);
                        font-size: 12px;
                        outline: none;
                        cursor: pointer;
                    "
                    title="Click to copy"
                />
                <span style="font-size: 11px; color: rgba(255,255,255,0.4);">
                    Click to copy
                </span>
            </div>
        </div>
    """)


def render_mobile_view_toggle(key_prefix: str = "mobile") -> bool:
    """
    Render a toggle for mobile-optimized view.

    Args:
        key_prefix: Unique key prefix

    Returns:
        True if mobile view is enabled
    """
    if "mobile_view" not in st.session_state:
        st.session_state["mobile_view"] = False

    is_mobile = st.checkbox(
        "📱 Mobile View",
        value=st.session_state["mobile_view"],
        key=f"{key_prefix}_toggle",
        help="Enable compact mobile-optimized layout",
    )

    if is_mobile != st.session_state["mobile_view"]:
        st.session_state["mobile_view"] = is_mobile
        st.rerun()

    return is_mobile
