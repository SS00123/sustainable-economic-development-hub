"""
Saudi Arabia Map Component
Sustainable Economic Development Analytics Hub
Eng. Sultan Albuqami

Modern interactive bubble map of Saudi Arabia regions
for visualizing KPI performance geographically.
Matches PDF design spec with dark theme and neon accents.
"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from analytics_hub_platform.ui.theme import get_dark_theme

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
    """Get color based on KPI status using dark theme palette."""
    dark_theme = get_dark_theme()
    colors = {
        "green": dark_theme.colors.green,
        "amber": dark_theme.colors.amber,
        "red": dark_theme.colors.red,
        "gray": dark_theme.colors.text_muted,
        "high": dark_theme.colors.green,
        "medium": dark_theme.colors.amber,
        "low": dark_theme.colors.red,
    }
    return colors.get(status.lower() if status else "gray", colors["gray"])


def get_three_tier_color(value: float, min_val: float, max_val: float) -> tuple[str, str]:
    """
    Get three-tier choropleth color matching PDF design spec.

    Returns tuple of (fill_color, tier_name) based on value position.
    - Low (0-33%): Red
    - Medium (33-66%): Amber
    - High (66-100%): Green
    """
    dark_theme = get_dark_theme()

    if max_val == min_val:
        normalized = 0.5
    else:
        normalized = (value - min_val) / (max_val - min_val)

    if normalized < 0.33:
        return dark_theme.colors.red, "Low"
    elif normalized < 0.66:
        return dark_theme.colors.amber, "Medium"
    else:
        return dark_theme.colors.green, "High"


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
    use_three_tier: bool = True,
) -> go.Figure:
    """
    Render a modern interactive bubble map of Saudi Arabia.
    Matches PDF design spec with dark theme, three-tier choropleth,
    and neon-stroke city bubbles.

    Args:
        region_data: DataFrame with region_id, value, and optionally status
        value_column: Column name for values to display
        status_column: Column name for status (green/amber/red)
        title: Map title
        height: Map height in pixels
        language: Display language ("en" or "ar")
        show_labels: Whether to show region labels
        show_status_overlay: Whether to show status indicators
        use_three_tier: Whether to use three-tier (low/medium/high) color scheme

    Returns:
        Plotly figure object
    """
    dark_theme = get_dark_theme()
    name_key = "name_ar" if language == "ar" else "name_en"

    # Prepare data lookup
    region_values = {}
    region_status = {}
    _region_tiers = {}  # noqa: F841 Reserved for tier-based coloring
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
    tiers = []

    for region_id, region_info in SAUDI_REGIONS.items():
        lats.append(region_info["lat"])
        lons.append(region_info["lon"])

        value = region_values.get(region_id, 0)
        values.append(value)

        name = region_info[name_key]
        names.append(name)

        status = region_status.get(region_id, "gray")

        # Use three-tier color scheme matching PDF design
        if use_three_tier:
            color, tier = get_three_tier_color(value, min_val, max_val)
            tiers.append(tier)
        elif status != "gray" and show_status_overlay:
            color = get_status_color(status)
            tiers.append(status.title())
        else:
            color = get_value_color(value, min_val, max_val)
            tiers.append("N/A")
        colors.append(color)

        # Scale bubble size based on value and base size
        base_size = region_info["size"]
        size_scale = 0.8 + 0.4 * (
            (value - min_val) / (max_val - min_val) if max_val != min_val else 0.5
        )
        sizes.append(base_size * size_scale)

        # Text for labels
        texts.append(f"<b>{name}</b>")

        # Build hover text with tier information
        tier_label = tiers[-1] if tiers else "N/A"
        tier_emoji = {"High": "🟢", "Medium": "🟡", "Low": "🔴"}.get(tier_label, "⚪")
        icon = region_info["icon"]

        hover = (
            f"<b style='font-size:15px;'>{icon} {name}</b><br>"
            f"<span style='color:{dark_theme.colors.primary};'>━━━━━━━━━━━━━</span><br>"
            f"📊 <b>Index:</b> {value:.1f}<br>"
            f"{tier_emoji} <b>Performance:</b> {tier_label}"
        )
        hovers.append(hover)

    # Create figure
    fig = go.Figure()

    # Add outer neon glow layer for depth effect (PDF design spec)
    fig.add_trace(
        go.Scattergeo(
            lon=lons,
            lat=lats,
            mode="markers",
            marker={
                "size": [s * 1.5 for s in sizes],
                "color": colors,
                "opacity": 0.12,
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
                "size": [s * 1.25 for s in sizes],
                "color": colors,
                "opacity": 0.2,
                "line": {"width": 0},
            },
            hoverinfo="skip",
            showlegend=False,
        )
    )

    # Main bubble markers with neon stroke (PDF design spec)
    fig.add_trace(
        go.Scattergeo(
            lon=lons,
            lat=lats,
            mode="markers",
            marker={
                "size": sizes,
                "color": colors,
                "opacity": 0.85,
                "line": {"color": dark_theme.colors.primary, "width": 2},
            },
            text=hovers,
            hovertemplate="%{text}<extra></extra>",
            hoverlabel={
                "bgcolor": dark_theme.colors.bg_card,
                "bordercolor": dark_theme.colors.primary,
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
                    "color": dark_theme.colors.text_primary,
                    "family": "Inter, sans-serif",
                },
                textposition="top center",
                hoverinfo="skip",
                showlegend=False,
            )
        )

    # Update layout for dark theme matching PDF design spec
    fig.update_layout(
        title={
            "text": f"<b>{title}</b>",
            "x": 0.5,
            "xanchor": "center",
            "font": {
                "size": 18,
                "color": dark_theme.colors.text_primary,
                "family": "Inter, sans-serif",
            },
        },
        geo={
            "scope": "asia",
            "center": {"lat": 24.5, "lon": 44},
            "projection_scale": 4.8,
            "projection_type": "natural earth",
            "showland": True,
            "landcolor": dark_theme.colors.bg_card,  # Dark background for land
            "showocean": True,
            "oceancolor": dark_theme.colors.bg_deep,  # Darker ocean
            "showlakes": False,
            "showcountries": True,
            "countrycolor": "rgba(6, 182, 212, 0.37)",  # Faded neighboring countries
            "countrywidth": 1,
            "showcoastlines": True,
            "coastlinecolor": "rgba(6, 182, 212, 0.5)",
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

    # Add three-tier legend (PDF design spec: Low/Medium/High)
    if show_status_overlay or use_three_tier:
        # Add invisible traces for legend with three-tier color scheme
        legend_items = [
            ("high", dark_theme.colors.green, "High (70-100)"),
            ("medium", dark_theme.colors.amber, "Medium (40-70)"),
            ("low", dark_theme.colors.red, "Low (0-40)"),
        ]

        for _status, color, label in legend_items:
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
                "bgcolor": dark_theme.colors.bg_card,
                "bordercolor": dark_theme.colors.border,
                "borderwidth": 1,
                "font": {"color": dark_theme.colors.text_secondary, "size": 11},
            }
        )

    return fig


def render_saudi_map_with_overlay(
    region_data: pd.DataFrame,
    value_column: str = "value",
    title: str = "Saudi Arabia Sustainability Index",
    height: int = 500,
    language: str = "en",
) -> tuple[go.Figure, dict]:
    """
    Render Saudi map with an overlay KPI panel.

    Returns both the figure and KPI data for the overlay panel.

    Args:
        region_data: DataFrame with region_id, value, and optionally status
        value_column: Column name for values to display
        title: Map title
        height: Map height in pixels
        language: Display language

    Returns:
        Tuple of (Plotly figure, dict with national stats)
    """
    _dark_theme = get_dark_theme()  # noqa: F841 Reserved for themed map

    # Calculate national statistics
    values = region_data[value_column].dropna().tolist() if value_column in region_data else []
    national_avg = sum(values) / len(values) if values else 0
    regions_above_target = sum(1 for v in values if v >= 70)
    highest_region = region_data.loc[region_data[value_column].idxmax()] if values else None
    lowest_region = region_data.loc[region_data[value_column].idxmin()] if values else None

    stats = {
        "national_index": national_avg,
        "regions_above_target": regions_above_target,
        "total_regions": len(values),
        "highest_region": highest_region["region_id"] if highest_region is not None else "N/A",
        "highest_value": highest_region[value_column] if highest_region is not None else 0,
        "lowest_region": lowest_region["region_id"] if lowest_region is not None else "N/A",
        "lowest_value": lowest_region[value_column] if lowest_region is not None else 0,
    }

    # Render the map
    fig = render_saudi_map(
        region_data=region_data,
        value_column=value_column,
        title=title,
        height=height,
        language=language,
        use_three_tier=True,
    )

    return fig, stats


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

    st.plotly_chart(fig, width="stretch")
