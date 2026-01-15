"""
Header Section Component
Page header with gradient background, live indicator, and period info.
"""

from datetime import datetime

from analytics_hub_platform.ui.html import render_html


def render_page_header(
    dark_theme, year: int, quarter: int, last_updated: str | None = None
) -> None:
    """
    Render the premium page header matching modern dashboard design.

    Features:
    - Animated gradient background with mesh overlay
    - Main title with gradient text
    - Live data indicator
    - Period badge and last updated timestamp

    Args:
        dark_theme: Theme configuration object
        year: Current year
        quarter: Current quarter (1-4)
        last_updated: Optional timestamp string
    """
    if last_updated is None:
        last_updated = datetime.now().strftime("%B %d, %Y %H:%M")

    header_html = f"""
        <div style="
            position: relative;
            background: linear-gradient(135deg,
                rgba(27, 31, 54, 0.95) 0%,
                rgba(15, 17, 34, 0.98) 50%,
                rgba(30, 35, 64, 0.95) 100%);
            border: 1px solid rgba(168, 85, 247, 0.2);
            border-radius: 20px;
            padding: 32px 36px;
            margin-bottom: 28px;
            overflow: hidden;
            box-shadow:
                0 20px 60px rgba(0, 0, 0, 0.4),
                inset 0 1px 0 rgba(255, 255, 255, 0.06);
        ">
            <!-- Animated orbs -->
            <div style="
                position: absolute;
                top: -80px;
                right: -60px;
                width: 250px;
                height: 250px;
                background: radial-gradient(circle, rgba(168, 85, 247, 0.25) 0%, transparent 60%);
                border-radius: 50%;
                filter: blur(40px);
                animation: float-orb 8s ease-in-out infinite;
            "></div>
            <div style="
                position: absolute;
                bottom: -60px;
                left: 20%;
                width: 200px;
                height: 200px;
                background: radial-gradient(circle, rgba(34, 211, 238, 0.2) 0%, transparent 60%);
                border-radius: 50%;
                filter: blur(35px);
                animation: float-orb 10s ease-in-out infinite reverse;
            "></div>
            <div style="
                position: absolute;
                top: 30%;
                left: 60%;
                width: 150px;
                height: 150px;
                background: radial-gradient(circle, rgba(236, 72, 153, 0.15) 0%, transparent 60%);
                border-radius: 50%;
                filter: blur(30px);
                animation: float-orb 6s ease-in-out infinite;
            "></div>

            <div style="position: relative; z-index: 2;">
                <!-- Live badge -->
                <div style="
                    display: inline-flex;
                    align-items: center;
                    gap: 8px;
                    background: rgba(16, 185, 129, 0.15);
                    border: 1px solid rgba(16, 185, 129, 0.3);
                    padding: 6px 14px;
                    border-radius: 20px;
                    margin-bottom: 16px;
                    font-size: 11px;
                    color: #10b981;
                    font-weight: 600;
                    letter-spacing: 0.5px;
                ">
                    <span style="
                        width: 8px;
                        height: 8px;
                        background: #10b981;
                        border-radius: 50%;
                        display: inline-block;
                        box-shadow: 0 0 12px #10b981;
                        animation: pulse-glow 2s ease-in-out infinite;
                    "></span>
                    LIVE DATA
                </div>

                <!-- Title -->
                <h1 style="
                    font-size: 34px;
                    font-weight: 800;
                    color: rgba(255,255,255,0.98);
                    margin: 0 0 10px 0;
                    font-family: 'Inter', -apple-system, sans-serif;
                    letter-spacing: -0.5px;
                    background: linear-gradient(135deg, #fff 0%, rgba(255,255,255,0.85) 100%);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    background-clip: text;
                ">
                    📊 Sustainable Economic Development
                </h1>
                <p style="
                    font-size: 16px;
                    color: rgba(255,255,255,0.65);
                    margin: 0 0 20px 0;
                    font-weight: 500;
                ">
                    Eng. Sultan Albuqami • Executive Analytics Hub
                </p>

                <!-- Period and timestamp -->
                <div style="
                    display: flex;
                    align-items: center;
                    gap: 20px;
                    flex-wrap: wrap;
                ">
                    <span style="
                        display: inline-flex;
                        align-items: center;
                        gap: 10px;
                        background: linear-gradient(135deg, rgba(168, 85, 247, 0.2), rgba(34, 211, 238, 0.15));
                        padding: 10px 20px;
                        border-radius: 24px;
                        border: 1px solid rgba(168, 85, 247, 0.3);
                        font-size: 14px;
                        color: rgba(255,255,255,0.95);
                        font-weight: 600;
                        box-shadow: 0 4px 20px rgba(168, 85, 247, 0.2);
                    ">
                        <span style="font-size: 16px;">📅</span>
                        Q{quarter} {year}
                    </span>
                    <span style="
                        font-size: 13px;
                        color: rgba(255,255,255,0.5);
                        display: flex;
                        align-items: center;
                        gap: 8px;
                    ">
                        <span style="font-size: 14px;">🕐</span>
                        Last updated: {last_updated}
                    </span>
                </div>
            </div>
        </div>

        <style>
            @keyframes float-orb {{
                0%, 100% {{ transform: translate(0, 0) scale(1); opacity: 0.8; }}
                50% {{ transform: translate(20px, 25px) scale(1.15); opacity: 1; }}
            }}
            @keyframes pulse-glow {{
                0%, 100% {{ opacity: 1; transform: scale(1); }}
                50% {{ opacity: 0.6; transform: scale(1.2); }}
            }}
        </style>
    """
    render_html(header_html)
