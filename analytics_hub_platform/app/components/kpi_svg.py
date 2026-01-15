"""Legacy SVG helpers reimplemented in the canonical component layer.

These functions previously lived in `analytics_hub_platform.ui.dark_components`.
They are re-homed here to reduce dependency on the legacy monolith while
preserving exact behavior and markup.
"""

from __future__ import annotations


def create_sparkline_svg(
    values: list[float],
    width: int = 100,
    height: int = 30,
    color: str = "#a855f7",
    fill_color: str | None = None,
) -> str:
    """Create an SVG sparkline from a list of values."""
    if not values or len(values) < 2:
        return ""

    min_val = min(values)
    max_val = max(values)
    value_range = max_val - min_val if max_val != min_val else 1

    points: list[str] = []
    for i, val in enumerate(values):
        x = (i / (len(values) - 1)) * width
        y = height - ((val - min_val) / value_range) * (height - 4) - 2
        points.append(f"{x:.1f},{y:.1f}")

    path_d = f"M {' L '.join(points)}"

    fill_path = ""
    if fill_color:
        area_points = [f"0,{height}"] + points + [f"{width},{height}"]
        fill_path = f"""
        <defs>
            <linearGradient id="sparkGrad" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" style="stop-color:{fill_color};stop-opacity:0.4"/>
                <stop offset="100%" style="stop-color:{fill_color};stop-opacity:0"/>
            </linearGradient>
        </defs>
        <path d="M {' L '.join(area_points)} Z" fill="url(#sparkGrad)"/>"""

    return f"""
    <svg width="{width}" height="{height}" viewBox="0 0 {width} {height}"
         style="overflow:visible" xmlns="http://www.w3.org/2000/svg">
        {fill_path}
        <path d="{path_d}" fill="none" stroke="{color}" stroke-width="2"
              stroke-linecap="round" stroke-linejoin="round"/>
        <circle cx="{points[-1].split(',')[0]}" cy="{points[-1].split(',')[1]}"
                r="3" fill="{color}" stroke="white" stroke-width="1"/>
    </svg>"""


def create_progress_ring(
    value: float,
    max_value: float = 100,
    size: int = 80,
    stroke_width: int = 8,
    color: str = "#a855f7",
    bg_color: str = "rgba(255,255,255,0.08)",
    label: str = "",
) -> str:
    """Create an SVG circular progress ring."""
    radius = (size - stroke_width) / 2
    circumference = 2 * 3.14159 * radius
    percentage = min(value / max_value, 1.0) if max_value > 0 else 0
    dash_offset = circumference * (1 - percentage)

    if percentage >= 0.8:
        color = "#10b981"  # Green for good
    elif percentage >= 0.5:
        color = "#f59e0b"  # Yellow for medium
    else:
        color = "#ef4444"  # Red for low

    display_value = f"{int(value)}%" if max_value == 100 else f"{value:.1f}"

    return f"""
    <div class="progress-ring-container" style="text-align:center">
        <svg class="progress-ring" width="{size}" height="{size}">
            <circle class="progress-bg"
                    cx="{size/2}" cy="{size/2}" r="{radius}"
                    stroke="{bg_color}" stroke-width="{stroke_width}"/>
            <circle class="progress-bar"
                    cx="{size/2}" cy="{size/2}" r="{radius}"
                    stroke="{color}" stroke-width="{stroke_width}"
                    stroke-dasharray="{circumference}"
                    stroke-dashoffset="{dash_offset}"
                    style="--target-offset: {dash_offset}"/>
        </svg>
        <span class="progress-ring-value" style="color:{color}">{display_value}</span>
        {f'<div class="progress-ring-label">{label}</div>' if label else ''}
    </div>"""


def create_alert_badge(
    alert_type: str = "info",
    count: int | None = None,
) -> str:
    """Create an alert badge for KPI cards."""
    icons = {
        "critical": "!",
        "warning": "⚠",
        "info": "i",
    }
    icon = icons.get(alert_type, "i")
    display = str(count) if count is not None else icon

    return f'<div class="alert-badge {alert_type}">{display}</div>'
