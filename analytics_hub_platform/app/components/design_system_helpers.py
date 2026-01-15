"""Helper components for the Design System documentation page."""

import streamlit as st

def hex_to_rgb(hex_color: str) -> str:
    """Convert hex to rgb string for display."""
    hex_color = hex_color.lstrip('#')
    try:
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        return f"rgb{rgb}"
    except (ValueError, IndexError):
        return hex_color

def render_color_swatch(name: str, value: str, description: str = ""):
    """Render a visual color swatch with details."""
    # Check if value is a gradient or simple color for the background
    bg_style = f"background: {value};" if "gradient" in value or value.startswith("#") or value.startswith("rgba") else f"background-color: {value};"

    # Determine text color based on brightness (very rough approximation)
    text_color = "#000000"
    if value.startswith("#"):
        # simple brightness check
        try:
            r = int(value[1:3], 16)
            g = int(value[3:5], 16)
            b = int(value[5:7], 16)
            brightness = (r * 299 + g * 587 + b * 114) / 1000
            if brightness < 128:
                text_color = "#ffffff"
        except:
            pass
    elif "rgba" in value:
        # Default to white for rgba as they are often dark/transparent in this system
        text_color = "#ffffff"

    st.markdown(
        f"""
        <div style="
            display: flex;
            align_items: center;
            margin-bottom: 8px;
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 8px;
            overflow: hidden;
        ">
            <div style="
                width: 80px;
                height: 80px;
                {bg_style}
                display: flex;
                align_items: center;
                justify_content: center;
                color: {text_color};
                font-size: 10px;
                flex-shrink: 0;
            ">
            </div>
            <div style="padding: 0 16px; flex-grow: 1;">
                <div style="font-family: monospace; font-weight: 600; color: #fff;">{name}</div>
                <div style="font-family: monospace; font-size: 12px; color: rgba(255,255,255,0.6);">{value}</div>
                <div style="font-size: 12px; color: rgba(255,255,255,0.4); margin-top: 4px;">{description}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

def render_spacing_bar(name: str, value: str):
    """Render a visual bar representing spacing."""
    # Extract numeric pixels for width if possible
    pixel_val = value.replace("px", "")
    try:
        width_px = int(pixel_val)
        # Cap width for display
        display_width = min(width_px * 2, 300)
    except ValueError:
        display_width = 20

    st.markdown(
        f"""
        <div style="display: flex; align_items: center; margin-bottom: 8px;">
            <div style="width: 100px; font-family: monospace; font-size: 12px; color: rgba(255,255,255,0.8);">{name}</div>
            <div style="
                height: 16px;
                width: {display_width}px;
                background-color: #3B82F6;
                opacity: 0.8;
                border-radius: 2px;
                margin-right: 12px;
            "></div>
            <div style="font-family: monospace; font-size: 12px; color: rgba(255,255,255,0.5);">{value}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

def render_radius_box(name: str, value: str):
    """Render a box with specific border radius."""
    st.markdown(
        f"""
        <div style="display: inline-block; margin: 8px; text-align: center;">
            <div style="
                width: 80px;
                height: 80px;
                border: 2px solid #3B82F6;
                border-radius: {value};
                background: rgba(59, 130, 246, 0.1);
                margin-bottom: 8px;
            "></div>
            <div style="font-family: monospace; font-size: 11px; color: rgba(255,255,255,0.8);">{name}</div>
            <div style="font-family: monospace; font-size: 10px; color: rgba(255,255,255,0.5);">{value}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

def render_shadow_card(name: str, value: str):
    """Render a card with specific shadow."""
    st.markdown(
        f"""
        <div style="display: inline-block; margin: 16px;">
            <div style="
                width: 160px;
                height: 100px;
                background-color: #1E293B;
                border-radius: 8px;
                box-shadow: {value};
                display: flex;
                align_items: center;
                justify_content: center;
                flex-direction: column;
                margin-bottom: 8px;
            ">
                <span style="font-size: 12px; color: #fff;">{name}</span>
            </div>
            <div style="font-family: monospace; font-size: 10px; color: rgba(255,255,255,0.4); max-width: 160px; word-wrap: break-word;">{value}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

def render_typography_sample(name: str, size: str, weight: str = "normal", line_height: str = "normal", family: str = "sans-serif"):
    """Render a typography sample."""
    st.markdown(
        f"""
        <div style="margin-bottom: 24px; padding-bottom: 16px; border-bottom: 1px solid rgba(255,255,255,0.05);">
            <div style="
                font-family: {family};
                font-size: {size};
                font-weight: {weight};
                line-height: {line_height};
                color: rgba(255,255,255,0.9);
                margin-bottom: 8px;
            ">
                The quick brown fox jumps over the lazy dog.
            </div>
            <div style="display: flex; gap: 16px; font-family: monospace; font-size: 11px; color: rgba(255,255,255,0.5);">
                <span>Token: {name}</span>
                <span>Size: {size}</span>
                <span>Weight: {weight}</span>
                <span>Line-Height: {line_height}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
