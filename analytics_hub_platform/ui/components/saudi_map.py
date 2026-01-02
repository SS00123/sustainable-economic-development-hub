"""
Saudi Arabia Map Component
Sustainable Economic Development Analytics Hub
Ministry of Economy and Planning

Modern interactive bubble map of Saudi Arabia regions
for visualizing KPI performance geographically.
"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from analytics_hub_platform.config.theme import get_theme

# Region data with accurate coordinates and relative sizes
SAUDI_REGIONS = {
    "riyadh": {
        "name_en": "Riyadh",
        "name_ar": "الرياض",
        "lat": 24.7136,
        "lon": 46.6753,
        "size": 100,  # Capital - largest
        "icon": "🏛️",
    },
    "makkah": {
        "name_en": "Makkah",
        "name_ar": "مكة المكرمة",
        "lat": 21.4225,
        "lon": 39.8262,
        "size": 85,
        "icon": "🕋",
    },
    "eastern": {
        "name_en": "Eastern Province",
        "name_ar": "المنطقة الشرقية",
        "lat": 26.3927,
        "lon": 49.9777,
        "size": 90,
        "icon": "🛢️",
    },
    "madinah": {
        "name_en": "Madinah",
        "name_ar": "المدينة المنورة",
        "lat": 24.5247,
        "lon": 39.5692,
        "size": 75,
        "icon": "🕌",
    },
    "qassim": {
        "name_en": "Qassim",
        "name_ar": "القصيم",
        "lat": 26.3489,
        "lon": 43.7668,
        "size": 55,
        "icon": "🌾",
    },
    "asir": {
        "name_en": "Asir",
        "name_ar": "عسير",
        "lat": 18.2164,
        "lon": 42.5053,
        "size": 60,
        "icon": "⛰️",
    },
    "tabuk": {
        "name_en": "Tabuk",
        "name_ar": "تبوك",
        "lat": 28.3998,
        "lon": 36.5715,
        "size": 55,
        "icon": "🏜️",
    },
    "hail": {
        "name_en": "Hail",
        "name_ar": "حائل",
        "lat": 27.5114,
        "lon": 41.7208,
        "size": 50,
        "icon": "🏔️",
    },
    "northern_borders": {
        "name_en": "Northern Borders",
        "name_ar": "الحدود الشمالية",
        "lat": 30.9943,
        "lon": 41.1239,
        "size": 45,
        "icon": "🧭",
    },
    "jazan": {
        "name_en": "Jazan",
        "name_ar": "جازان",
        "lat": 16.8892,
        "lon": 42.5706,
        "size": 45,
        "icon": "🌴",
    },
    "najran": {
        "name_en": "Najran",
        "name_ar": "نجران",
        "lat": 17.4924,
        "lon": 44.1322,
        "size": 50,
        "icon": "🏰",
    },
    "bahah": {
        "name_en": "Al Bahah",
        "name_ar": "الباحة",
        "lat": 20.0129,
        "lon": 41.4677,
        "size": 40,
        "icon": "🌲",
    },
    "jawf": {
        "name_en": "Al Jawf",
        "name_ar": "الجوف",
        "lat": 29.8144,
        "lon": 40.0998,
        "size": 50,
        "icon": "🌙",
    },
}


# Region center coordinates for labels (legacy compatibility)
REGION_CENTERS = {
    "riyadh": {"lat": 24.7136, "lon": 46.6753},
    "makkah": {"lat": 21.4225, "lon": 39.8262},
    "eastern": {"lat": 26.3927, "lon": 49.9777},
    "madinah": {"lat": 24.5247, "lon": 39.5692},
    "qassim": {"lat": 26.3489, "lon": 43.7668},
    "asir": {"lat": 18.2164, "lon": 42.5053},
    "tabuk": {"lat": 28.3998, "lon": 36.5715},
    "hail": {"lat": 27.5114, "lon": 41.7208},
    "northern_borders": {"lat": 30.9943, "lon": 41.1239},
    "jazan": {"lat": 16.8892, "lon": 42.5706},
    "najran": {"lat": 17.4924, "lon": 44.1322},
    "bahah": {"lat": 20.0129, "lon": 41.4677},
    "jawf": {"lat": 29.8144, "lon": 40.0998},
}


def get_status_color(status: str) -> str:
    """Get color based on KPI status."""
    colors = {
        "green": "#10B981",
        "amber": "#F59E0B",
        "red": "#EF4444",
        "gray": "#6B7280",
    }
    return colors.get(status, colors["gray"])


def get_value_color(value: float, min_val: float, max_val: float) -> str:
    """Get gradient color based on value position in range."""
    if max_val == min_val:
        normalized = 0.5
    else:
        normalized = (value - min_val) / (max_val - min_val)

    # Gradient from red -> yellow -> green
    if normalized < 0.5:
        # Red to Yellow
        r = 239
        g = int(68 + (230 - 68) * (normalized * 2))
        b = 68
    else:
        # Yellow to Green
        r = int(234 - (234 - 16) * ((normalized - 0.5) * 2))
        g = int(179 + (185 - 179) * ((normalized - 0.5) * 2))
        b = int(8 + (129 - 8) * ((normalized - 0.5) * 2))

    return f"rgb({r}, {g}, {b})"


def render_saudi_map(
    region_data: pd.DataFrame,
    value_column: str = "value",
    status_column: str | None = "status",
    title: str = "Saudi Arabia Regional Performance",
    height: int = 550,
    language: str = "en",
    show_labels: bool = True,
    show_status_overlay: bool = True,
) -> go.Figure:
    """
    Render a modern interactive bubble map of Saudi Arabia.

    Args:
        region_data: DataFrame with region_id, value, and optionally status
        value_column: Column name for values to display
        status_column: Column name for status (green/amber/red)
        title: Map title
        height: Map height in pixels
        language: Display language ("en" or "ar")
        show_labels: Whether to show region labels
        show_status_overlay: Whether to show status indicators

    Returns:
        Plotly figure object
    """
    get_theme()
    name_key = "name_ar" if language == "ar" else "name_en"

    # Prepare data lookup
    region_values = {}
    region_status = {}
    for _, row in region_data.iterrows():
        region_id = row.get("region_id", row.get("region", ""))
        if region_id:
            region_values[region_id] = row.get(value_column, 0)
            if status_column and status_column in row:
                region_status[region_id] = row[status_column]

    # Calculate value range for color scaling
    values_list = list(region_values.values()) if region_values else [0]
    min_val = min(values_list) if values_list else 0
    max_val = max(values_list) if values_list else 100

    # Build data arrays
    lats = []
    lons = []
    values = []
    texts = []
    colors = []
    sizes = []
    names = []
    hovers = []

    for region_id, region_info in SAUDI_REGIONS.items():
        lats.append(region_info["lat"])
        lons.append(region_info["lon"])

        value = region_values.get(region_id, 0)
        values.append(value)

        name = region_info[name_key]
        names.append(name)

        status = region_status.get(region_id, "gray")

        # Use status color if available, otherwise gradient
        if status != "gray" and show_status_overlay:
            color = get_status_color(status)
        else:
            color = get_value_color(value, min_val, max_val)
        colors.append(color)

        # Scale bubble size based on value and base size
        base_size = region_info["size"]
        size_scale = 0.8 + 0.4 * (
            (value - min_val) / (max_val - min_val) if max_val != min_val else 0.5
        )
        sizes.append(base_size * size_scale)

        # Text for labels
        texts.append(f"<b>{name}</b>")

        # Build hover text
        status_label = status.upper() if status != "gray" else "N/A"
        status_emoji = {"green": "🟢", "amber": "🟡", "red": "🔴"}.get(status, "⚪")
        icon = region_info["icon"]

        hover = (
            f"<b style='font-size:15px;'>{icon} {name}</b><br>"
            f"<span style='color:#a855f7;'>━━━━━━━━━━━━━</span><br>"
            f"📊 <b>Value:</b> {value:.1f}<br>"
            f"{status_emoji} <b>Status:</b> {status_label}"
        )
        hovers.append(hover)

    # Create figure
    fig = go.Figure()

    # Add outer glow layer for depth effect
    fig.add_trace(
        go.Scattergeo(
            lon=lons,
            lat=lats,
            mode="markers",
            marker={
                "size": [s * 1.4 for s in sizes],
                "color": colors,
                "opacity": 0.15,
                "line": {"width": 0},
            },
            hoverinfo="skip",
            showlegend=False,
        )
    )

    # Add middle glow layer
    fig.add_trace(
        go.Scattergeo(
            lon=lons,
            lat=lats,
            mode="markers",
            marker={
                "size": [s * 1.2 for s in sizes],
                "color": colors,
                "opacity": 0.25,
                "line": {"width": 0},
            },
            hoverinfo="skip",
            showlegend=False,
        )
    )

    # Main bubble markers
    fig.add_trace(
        go.Scattergeo(
            lon=lons,
            lat=lats,
            mode="markers",
            marker={
                "size": sizes,
                "color": colors,
                "opacity": 0.9,
                "line": {"color": "rgba(255,255,255,0.8)", "width": 2},
                "gradient": {
                    "type": "radial",
                    "color": ["rgba(255,255,255,0.3)", "rgba(0,0,0,0.1)"],
                },
            },
            text=hovers,
            hovertemplate="%{text}<extra></extra>",
            hoverlabel={
                "bgcolor": "rgba(27, 31, 54, 0.96)",
                "bordercolor": "rgba(168, 85, 247, 0.6)",
                "font": {"family": "Inter, sans-serif", "size": 12, "color": "white"},
            },
            showlegend=False,
        )
    )

    # Add text labels
    if show_labels:
        fig.add_trace(
            go.Scattergeo(
                lon=lons,
                lat=lats,
                mode="text",
                text=[
                    f"<b>{n}</b><br><span style='font-size:9px'>{v:.1f}</span>"
                    for n, v in zip(names, values, strict=False)
                ],
                textfont={
                    "size": 10,
                    "color": "rgba(255, 255, 255, 0.95)",
                    "family": "Inter, sans-serif",
                },
                textposition="top center",
                hoverinfo="skip",
                showlegend=False,
            )
        )

    # Update layout for modern dark theme
    fig.update_layout(
        title={
            "text": f"<b>{title}</b>",
            "x": 0.5,
            "xanchor": "center",
            "font": {
                "size": 18,
                "color": "rgba(255, 255, 255, 0.95)",
                "family": "Inter, sans-serif",
            },
        },
        geo={
            "scope": "asia",
            "center": {"lat": 24.5, "lon": 44},
            "projection_scale": 4.8,
            "projection_type": "natural earth",
            "showland": True,
            "landcolor": "rgba(30, 35, 60, 0.98)",
            "showocean": True,
            "oceancolor": "rgba(15, 20, 40, 0.98)",
            "showlakes": False,
            "showcountries": True,
            "countrycolor": "rgba(168, 85, 247, 0.4)",
            "countrywidth": 1.5,
            "showcoastlines": True,
            "coastlinecolor": "rgba(168, 85, 247, 0.5)",
            "coastlinewidth": 1,
            "showframe": False,
            "bgcolor": "rgba(0, 0, 0, 0)",
            "fitbounds": "locations",
            "visible": True,
        },
        height=height,
        margin={"l": 10, "r": 10, "t": 60, "b": 10},
        paper_bgcolor="rgba(0, 0, 0, 0)",
        plot_bgcolor="rgba(0, 0, 0, 0)",
        dragmode=False,
    )

    # Add legend for status colors
    if show_status_overlay:
        # Add invisible traces for legend
        for _status, color, label in [
            ("green", "#10B981", "Excellent"),
            ("amber", "#F59E0B", "Warning"),
            ("red", "#EF4444", "Critical"),
        ]:
            fig.add_trace(
                go.Scattergeo(
                    lon=[None],
                    lat=[None],
                    mode="markers",
                    marker={"size": 12, "color": color},
                    name=label,
                    showlegend=True,
                )
            )

        fig.update_layout(
            legend={
                "orientation": "h",
                "yanchor": "bottom",
                "y": -0.05,
                "xanchor": "center",
                "x": 0.5,
                "bgcolor": "rgba(27, 31, 54, 0.85)",
                "bordercolor": "rgba(255, 255, 255, 0.1)",
                "borderwidth": 1,
                "font": {"color": "rgba(255, 255, 255, 0.8)", "size": 11},
            }
        )

    return fig


def render_saudi_map_simple(
    region_data: dict[str, float],
    title: str = "Regional Overview",
    language: str = "en",
) -> None:
    """
    Simple wrapper to render Saudi map in Streamlit.

    Args:
        region_data: Dictionary mapping region_id to value
        title: Map title
        language: Display language
    """
    df = pd.DataFrame([{"region_id": k, "value": v} for k, v in region_data.items()])

    fig = render_saudi_map(
        region_data=df,
        value_column="value",
        title=title,
        language=language,
    )

    st.plotly_chart(fig, use_container_width=True)
