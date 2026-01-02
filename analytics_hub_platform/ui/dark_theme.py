"""
Dark Theme Configuration
Sustainable Economic Development Analytics Hub
Ministry of Economy and Planning

Modern dark 3D dashboard theme matching the provided UI reference.
Purple/cyan/pink accent colors with glassmorphism cards.
"""

from dataclasses import dataclass
from functools import lru_cache


@dataclass(frozen=True)
class DarkColorPalette:
    """Dark theme color palette for the Minister View dashboard."""

    # Background colors
    bg_deep: str = "#0f1122"
    bg_main: str = "#121532"
    bg_card: str = "#1b1f36"
    bg_card_alt: str = "#1e2340"
    bg_hover: str = "#252a48"

    # Accent colors (neon-like)
    purple: str = "#a855f7"
    purple_dark: str = "#7c3aed"
    pink: str = "#ec4899"
    cyan: str = "#22d3ee"
    gradient_start: str = "#a855f7"
    gradient_end: str = "#ec4899"

    # Status colors
    green: str = "#10b981"
    green_bg: str = "rgba(16, 185, 129, 0.15)"
    amber: str = "#f59e0b"
    amber_bg: str = "rgba(245, 158, 11, 0.15)"
    red: str = "#ef4444"
    red_bg: str = "rgba(239, 68, 68, 0.15)"

    # Text colors
    text_primary: str = "rgba(255, 255, 255, 0.95)"
    text_secondary: str = "rgba(255, 255, 255, 0.78)"
    text_muted: str = "rgba(255, 255, 255, 0.55)"
    text_subtle: str = "rgba(255, 255, 255, 0.35)"

    # Borders and strokes
    border: str = "rgba(255, 255, 255, 0.08)"
    border_light: str = "rgba(255, 255, 255, 0.12)"

    # Chart palette
    chart_colors: tuple = (
        "#a855f7",  # Purple
        "#22d3ee",  # Cyan
        "#ec4899",  # Pink
        "#10b981",  # Green
        "#f59e0b",  # Amber
        "#3b82f6",  # Blue
        "#8b5cf6",  # Violet
        "#06b6d4",  # Teal
    )

    def get_status_color(self, status: str) -> str:
        """Return color for a status value."""
        status_map = {
            "green": self.green,
            "amber": self.amber,
            "red": self.red,
            "success": self.green,
            "warning": self.amber,
            "error": self.red,
        }
        return status_map.get(status.lower(), self.text_muted)

    def get_status_bg(self, status: str) -> str:
        """Return background color for a status value."""
        status_map = {
            "green": self.green_bg,
            "amber": self.amber_bg,
            "red": self.red_bg,
        }
        return status_map.get(status.lower(), "rgba(255,255,255,0.05)")


@dataclass(frozen=True)
class DarkShadows:
    """Box shadow definitions for dark theme."""

    card: str = "0 18px 48px rgba(0, 0, 0, 0.55)"
    card_hover: str = "0 22px 55px rgba(0, 0, 0, 0.62)"
    card_sm: str = "0 10px 26px rgba(0, 0, 0, 0.45)"
    glow_purple: str = "0 0 20px rgba(168, 85, 247, 0.35)"
    glow_cyan: str = "0 0 20px rgba(34, 211, 238, 0.35)"
    glow_pink: str = "0 0 20px rgba(236, 72, 153, 0.35)"


@dataclass(frozen=True)
class DarkTheme:
    """Complete dark theme configuration."""

    colors: DarkColorPalette = None
    shadows: DarkShadows = None

    def __post_init__(self):
        object.__setattr__(self, "colors", DarkColorPalette())
        object.__setattr__(self, "shadows", DarkShadows())


@lru_cache(maxsize=1)
def get_dark_theme() -> DarkTheme:
    """Get the singleton dark theme instance."""
    return DarkTheme()


def get_dark_css() -> str:
    """
    Return the complete CSS for the dark 3D dashboard theme.
    This should be injected via st.markdown at the start of the app.
    """
    t = get_dark_theme()
    c = t.colors
    s = t.shadows

    return f"""
    <style>
      :root {{
        --bg0: {c.bg_deep};
        --bg1: {c.bg_main};
        --card: {c.bg_card};
        --card2: {c.bg_card_alt};
        --stroke: {c.border};
        --muted: {c.text_secondary};
        --muted2: {c.text_muted};
        --white: {c.text_primary};
        --purple: {c.purple};
        --purple2: {c.purple_dark};
        --pink: {c.pink};
        --cyan: {c.cyan};
        --shadow: {s.card};
        --shadow2: {s.card_sm};
        --radius: 16px;
      }}

      /* ===== App background ===== */
      html, body, [data-testid="stAppViewContainer"] {{
        background:
          radial-gradient(1200px 700px at 10% 10%, rgba(124, 58, 237, 0.35), rgba(0,0,0,0) 60%),
          radial-gradient(1200px 700px at 90% 25%, rgba(34, 211, 238, 0.18), rgba(0,0,0,0) 60%),
          linear-gradient(180deg, var(--bg1), var(--bg0) 60%);
        color: var(--white);
        min-height: 100vh;
        font-size: 13px;
        line-height: 1.55;
      }}

      /* Hide Streamlit chrome */
      #MainMenu, footer, header {{ visibility: hidden; }}
      [data-testid="stSidebar"] {{ display: none !important; }}

      /* Layout container */
      .block-container {{
        padding-top: 16px !important;
        padding-bottom: 32px !important;
        padding-left: 28px !important;
        padding-right: 28px !important;
        max-width: 1280px !important;
      }}

      /* Remove default white containers */
      [data-testid="stVerticalBlock"], [data-testid="stHorizontalBlock"] {{
        gap: 16px;
      }}

      /* ===== Dark Card Base ===== */
      .dark-card {{
        background: linear-gradient(180deg, rgba(255,255,255,0.06), rgba(255,255,255,0.03));
        border: 1px solid var(--stroke);
        border-radius: var(--radius);
        box-shadow: var(--shadow);
        padding: 20px 22px;
        -webkit-backdrop-filter: blur(10px);
        backdrop-filter: blur(10px);
        position: relative;
        overflow: hidden;
        transition: transform 140ms ease, box-shadow 140ms ease;
      }}
      .dark-card:hover {{
        transform: translateY(-2px);
        box-shadow: {s.card_hover};
      }}
      .dark-card .card-title {{
        font-size: 13px;
        color: var(--muted);
        letter-spacing: 0.2px;
        text-transform: uppercase;
        margin-bottom: 4px;
      }}
      .dark-card .card-value {{
        font-size: 26px;
        font-weight: 700;
        color: var(--white);
        margin: 4px 0;
      }}
      .dark-card .card-sub {{
        font-size: 12px;
        color: var(--muted2);
        margin-top: 2px;
      }}

      /* Delta badges */
      .delta {{
        font-size: 12px;
        padding: 3px 10px;
        border-radius: 999px;
        border: 1px solid rgba(255,255,255,0.10);
        background: rgba(255,255,255,0.05);
        display: inline-flex;
        gap: 5px;
        align-items: center;
      }}
      .delta.positive {{ color: {c.cyan}; border-color: rgba(34, 211, 238, 0.25); background: rgba(34, 211, 238, 0.10); }}
      .delta.negative {{ color: {c.pink}; border-color: rgba(236, 72, 153, 0.25); background: rgba(236, 72, 153, 0.10); }}

      /* ===== Legacy Sidebar (kept for compatibility) ===== */
      .side {{
        background: rgba(255,255,255,0.04);
        border: 1px solid var(--stroke);
        border-radius: var(--radius);
        box-shadow: var(--shadow2);
        overflow: hidden;
        height: 100%;
        min-height: 85vh;
      }}
      .side-top {{
        padding: 20px 18px;
        background: linear-gradient(135deg, rgba(168, 85, 247, 0.95), rgba(236, 72, 153, 0.75));
        position: relative;
      }}
      .brand {{
        font-weight: 800;
        letter-spacing: 0.2px;
        color: rgba(255,255,255,0.95);
        font-size: 14px;
        position: relative;
        z-index: 1;
      }}
      .nav a {{
        display: flex;
        gap: 10px;
        align-items: center;
        padding: 12px 12px;
        border-radius: 12px;
        text-decoration: none;
        color: rgba(255,255,255,0.70);
        font-size: 13px;
        border: 1px solid rgba(255,255,255,0);
        margin-bottom: 4px;
        transition: all 140ms ease;
      }}
      .nav a:hover {{
        background: rgba(168, 85, 247, 0.12);
        border: 1px solid rgba(168, 85, 247, 0.20);
        color: rgba(255,255,255,0.95);
      }}
      .nav .dot {{
        width: 7px;
        height: 7px;
        border-radius: 99px;
        background: {c.purple};
        box-shadow: 0 0 14px rgba(168, 85, 247, 0.65);
      }}

      /* ===== Enhanced Sidebar ===== */
      .sidebar-container {{
        background: linear-gradient(180deg, rgba(27, 31, 54, 0.98), rgba(15, 17, 34, 0.98));
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 20px;
        box-shadow: 0 25px 60px rgba(0, 0, 0, 0.6), inset 0 1px 0 rgba(255,255,255,0.05);
        overflow: hidden;
        height: 100%;
        min-height: 88vh;
        display: flex;
        flex-direction: column;
        backdrop-filter: blur(20px);
      }}

      .sidebar-header {{
        padding: 24px 20px 20px;
        background: linear-gradient(145deg, rgba(168, 85, 247, 0.95), rgba(236, 72, 153, 0.8));
        position: relative;
        overflow: hidden;
      }}

      .sidebar-header::before {{
        content: "";
        position: absolute;
        top: -50%;
        right: -30%;
        width: 200px;
        height: 200px;
        background: radial-gradient(circle, rgba(255,255,255,0.2) 0%, transparent 70%);
        border-radius: 50%;
      }}

      .sidebar-header::after {{
        content: "";
        position: absolute;
        bottom: -30%;
        left: -20%;
        width: 150px;
        height: 150px;
        background: radial-gradient(circle, rgba(34, 211, 238, 0.3) 0%, transparent 70%);
        border-radius: 50%;
      }}

      .sidebar-logo {{
        position: relative;
        z-index: 2;
        margin-bottom: 8px;
      }}

      .logo-icon {{
        font-size: 32px;
        filter: drop-shadow(0 0 12px rgba(255,255,255,0.4));
      }}

      .sidebar-brand {{
        font-weight: 800;
        font-size: 16px;
        color: rgba(255,255,255,0.98);
        letter-spacing: 0.3px;
        position: relative;
        z-index: 2;
      }}

      .sidebar-subtitle {{
        font-size: 11px;
        color: rgba(255,255,255,0.75);
        margin-top: 2px;
        position: relative;
        z-index: 2;
      }}

      .sidebar-user {{
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 18px 16px;
        background: rgba(255,255,255,0.03);
        border-bottom: 1px solid rgba(255,255,255,0.06);
      }}

      .user-avatar {{
        width: 44px;
        height: 44px;
        border-radius: 14px;
        background: linear-gradient(145deg, rgba(168, 85, 247, 0.8), rgba(34, 211, 238, 0.8));
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 14px;
        color: white;
        position: relative;
        box-shadow: 0 4px 15px rgba(168, 85, 247, 0.4);
      }}

      .avatar-ring {{
        position: absolute;
        inset: -3px;
        border-radius: 16px;
        border: 2px solid rgba(168, 85, 247, 0.3);
        animation: pulse-ring 2s ease-out infinite;
      }}

      @keyframes pulse-ring {{
        0% {{ transform: scale(1); opacity: 1; }}
        100% {{ transform: scale(1.15); opacity: 0; }}
      }}

      .user-info {{
        flex: 1;
      }}

      .user-title {{
        font-size: 13px;
        font-weight: 600;
        color: rgba(255,255,255,0.95);
      }}

      .user-role {{
        font-size: 11px;
        color: rgba(255,255,255,0.5);
        margin-top: 2px;
      }}

      .user-status {{
        width: 10px;
        height: 10px;
        border-radius: 50%;
        background: {c.green};
        box-shadow: 0 0 10px {c.green};
      }}

      .sidebar-nav {{
        flex: 1;
        padding: 16px 12px;
      }}

      .nav-label {{
        font-size: 10px;
        font-weight: 700;
        color: rgba(255,255,255,0.35);
        letter-spacing: 1.2px;
        padding: 0 12px;
        margin-bottom: 12px;
      }}

      .nav-link {{
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 12px 14px;
        border-radius: 12px;
        text-decoration: none !important;
        color: rgba(255,255,255,0.65);
        font-size: 13px;
        font-weight: 500;
        margin-bottom: 4px;
        transition: all 180ms ease;
        border: 1px solid transparent;
        position: relative;
        overflow: hidden;
      }}

      .nav-link::before {{
        content: "";
        position: absolute;
        left: 0;
        top: 0;
        bottom: 0;
        width: 0;
        background: linear-gradient(90deg, rgba(168, 85, 247, 0.3), transparent);
        transition: width 180ms ease;
      }}

      .nav-link:hover {{
        background: rgba(168, 85, 247, 0.12);
        border-color: rgba(168, 85, 247, 0.25);
        color: rgba(255,255,255,0.95);
        transform: translateX(4px);
      }}

      .nav-link:hover::before {{
        width: 100%;
      }}

      .nav-link.active {{
        background: linear-gradient(135deg, rgba(168, 85, 247, 0.2), rgba(34, 211, 238, 0.1));
        border-color: rgba(168, 85, 247, 0.35);
        color: rgba(255,255,255,0.98);
        box-shadow: 0 4px 20px rgba(168, 85, 247, 0.2);
      }}

      .nav-link.active .nav-dot {{
        background: {c.cyan};
        box-shadow: 0 0 15px {c.cyan};
      }}

      .nav-dot {{
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: {c.purple};
        box-shadow: 0 0 12px rgba(168, 85, 247, 0.6);
        flex-shrink: 0;
      }}

      .nav-icon {{
        font-size: 16px;
        width: 20px;
        text-align: center;
      }}

      .nav-text {{
        flex: 1;
        position: relative;
        z-index: 1;
      }}

      .sidebar-footer {{
        padding: 12px;
        border-top: 1px solid rgba(255,255,255,0.06);
        display: flex;
        gap: 8px;
      }}

      .footer-item {{
        flex: 1;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 6px;
        padding: 10px;
        border-radius: 10px;
        background: rgba(255,255,255,0.03);
        color: rgba(255,255,255,0.5);
        font-size: 11px;
        cursor: pointer;
        transition: all 150ms ease;
      }}

      .footer-item:hover {{
        background: rgba(255,255,255,0.08);
        color: rgba(255,255,255,0.85);
      }}

      /* Section anchors for navigation */
      [id^="section-"] {{
        scroll-margin-top: 20px;
      }}

      /* ===== Top Header Bar ===== */
      .topbar {{
        background: rgba(255,255,255,0.04);
        border: 1px solid var(--stroke);
        border-radius: var(--radius);
        box-shadow: var(--shadow2);
        padding: 14px 18px;
      }}
      .topbar .title {{
        font-weight: 800;
        font-size: 16px;
        color: var(--white);
      }}
      .topbar .daterange {{
        font-size: 11px;
        color: var(--muted2);
        margin-top: 2px;
      }}
      .icon-pill {{
        width: 36px;
        height: 36px;
        border-radius: 999px;
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.10);
        display: flex;
        align-items: center;
        justify-content: center;
        color: rgba(255,255,255,0.75);
        font-size: 14px;
        transition: all 140ms ease;
      }}
      .icon-pill:hover {{
        background: rgba(168, 85, 247, 0.15);
        border-color: rgba(168, 85, 247, 0.30);
      }}

      /* ===== Inputs ===== */
      .stTextInput input {{
        background: rgba(255,255,255,0.06) !important;
        border: 1px solid rgba(255,255,255,0.10) !important;
        border-radius: 999px !important;
        color: var(--white) !important;
        height: 38px;
        padding: 0 16px !important;
      }}
      .stTextInput input::placeholder {{
        color: rgba(255,255,255,0.40);
      }}
      .stSelectbox > div > div {{
        background: rgba(255,255,255,0.06) !important;
        border: 1px solid rgba(255,255,255,0.10) !important;
        border-radius: 10px !important;
        color: var(--white) !important;
      }}
      .stSelectbox label {{
        color: var(--muted) !important;
        font-size: 11px !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
      }}

      /* ===== Metric Styling ===== */
      [data-testid="stMetricValue"] {{
        color: var(--white) !important;
        font-size: 24px !important;
      }}
      [data-testid="stMetricLabel"] {{
        color: var(--muted) !important;
        font-size: 12px !important;
      }}
      [data-testid="stMetricDelta"] {{
        color: var(--cyan) !important;
      }}

      /* ===== Plotly Charts inside cards ===== */
      .js-plotly-plot .plotly .main-svg {{
        border-radius: 12px;
      }}
      .stPlotlyChart {{
        background: transparent !important;
      }}

      /* ===== Section Headers ===== */
      .section-header {{
        font-size: 16px;
        font-weight: 700;
        color: var(--white);
        margin: 22px 0 10px 0;
        display: flex;
        align-items: center;
        gap: 10px;
        letter-spacing: 0.2px;
      }}
      .section-header::after {{
        content: "";
        flex: 1;
        height: 1px;
        margin-left: 10px;
        background: linear-gradient(90deg, rgba(168, 85, 247, 0.55), rgba(34, 211, 238, 0.18), rgba(255,255,255,0.00));
      }}
      .section-sub {{
        font-size: 12px;
        color: var(--muted2);
        margin: -6px 0 16px 0;
      }}

      /* ===== Status Pills ===== */
      .status-pill {{
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 6px 14px;
        border-radius: 8px;
        font-weight: 600;
        font-size: 12px;
        margin: 3px;
      }}
      .status-green {{
        background: {c.green_bg};
        color: {c.green};
        border: 1px solid rgba(16, 185, 129, 0.30);
      }}
      .status-amber {{
        background: {c.amber_bg};
        color: {c.amber};
        border: 1px solid rgba(245, 158, 11, 0.30);
      }}
      .status-red {{
        background: {c.red_bg};
        color: {c.red};
        border: 1px solid rgba(239, 68, 68, 0.30);
      }}

      /* ===== Animations ===== */
      @keyframes fadeUp {{
        0% {{ opacity: 0; transform: translateY(12px); }}
        100% {{ opacity: 1; transform: translateY(0); }}
      }}
      .dark-card, .stPlotlyChart, .side, .topbar {{
        animation: fadeUp 320ms ease both;
      }}
      .stColumn:nth-child(1) > div {{ animation-delay: 40ms; }}
      .stColumn:nth-child(2) > div {{ animation-delay: 80ms; }}
      .stColumn:nth-child(3) > div {{ animation-delay: 120ms; }}
      .stColumn:nth-child(4) > div {{ animation-delay: 160ms; }}

      /* ===== Scrollbar ===== */
      ::-webkit-scrollbar {{
        width: 8px;
        height: 8px;
      }}
      ::-webkit-scrollbar-track {{
        background: rgba(255,255,255,0.03);
        border-radius: 4px;
      }}
      ::-webkit-scrollbar-thumb {{
        background: rgba(255,255,255,0.12);
        border-radius: 4px;
      }}
      ::-webkit-scrollbar-thumb:hover {{
        background: rgba(255,255,255,0.20);
      }}

      /* ===== Enhanced Modern Tabs ===== */
      .stTabs {{
        background: transparent;
      }}

      .stTabs [data-baseweb="tab-list"] {{
        background: linear-gradient(135deg, rgba(27, 31, 54, 0.95), rgba(15, 17, 34, 0.95));
        border: 1px solid rgba(168, 85, 247, 0.2);
        border-radius: 16px;
        padding: 6px 8px;
        gap: 6px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3),
                    inset 0 1px 0 rgba(255, 255, 255, 0.05);
        justify-content: flex-start;
      }}

      .stTabs [data-baseweb="tab"] {{
        background: transparent;
        color: rgba(255, 255, 255, 0.6);
        border-radius: 12px;
        padding: 12px 20px;
        font-weight: 600;
        font-size: 13px;
        letter-spacing: 0.3px;
        transition: all 200ms ease;
        border: 1px solid transparent;
        position: relative;
        min-height: 44px;
      }}

      .stTabs [data-baseweb="tab"]:hover {{
        background: rgba(168, 85, 247, 0.12);
        color: rgba(255, 255, 255, 0.9);
        border-color: rgba(168, 85, 247, 0.2);
      }}

      .stTabs [aria-selected="true"] {{
        background: linear-gradient(135deg, rgba(168, 85, 247, 0.35), rgba(34, 211, 238, 0.2)) !important;
        color: rgba(255, 255, 255, 0.98) !important;
        border-color: rgba(168, 85, 247, 0.5) !important;
        box-shadow: 0 4px 20px rgba(168, 85, 247, 0.25),
                    inset 0 1px 0 rgba(255, 255, 255, 0.1);
      }}

      .stTabs [aria-selected="true"]::before {{
        content: "";
        position: absolute;
        bottom: -7px;
        left: 50%;
        transform: translateX(-50%);
        width: 30px;
        height: 3px;
        background: linear-gradient(90deg, #a855f7, #22d3ee);
        border-radius: 2px;
      }}

      .stTabs [data-baseweb="tab-highlight"] {{
        display: none !important;
      }}

      .stTabs [data-baseweb="tab-border"] {{
        display: none !important;
      }}

      /* ===== Expanders ===== */
      .streamlit-expanderHeader {{
        background: rgba(255,255,255,0.04) !important;
        border: 1px solid var(--stroke) !important;
        border-radius: 12px !important;
        color: var(--white) !important;
      }}

      /* ===== Buttons ===== */
      .stButton > button {{
        background: linear-gradient(135deg, {c.purple}, {c.purple_dark}) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 8px 20px !important;
        font-weight: 600 !important;
        box-shadow: {s.glow_purple};
        transition: all 140ms ease;
        min-height: 44px !important;
        min-width: 44px !important;
      }}
      .stButton > button:hover {{
        transform: translateY(-1px);
        box-shadow: 0 0 30px rgba(168, 85, 247, 0.50);
      }}

      /* ===== ACCESSIBILITY ENHANCEMENTS (WCAG 2.1 AA) ===== */

      /* Focus Indicators */
      *:focus {{
        outline: 3px solid #2563eb !important;
        outline-offset: 2px !important;
      }}

      *:focus:not(:focus-visible) {{
        outline: none !important;
      }}

      *:focus-visible {{
        outline: 3px solid #2563eb !important;
        outline-offset: 2px !important;
        box-shadow: 0 0 0 6px rgba(37, 99, 235, 0.25) !important;
      }}

      /* Minimum touch/click target size */
      button,
      [role="button"],
      input[type="checkbox"],
      input[type="radio"],
      select,
      .stSelectbox > div {{
        min-height: 44px !important;
        min-width: 44px !important;
      }}

      /* Skip to main content link */
      .skip-link {{
        position: absolute;
        top: -100px;
        left: 0;
        background: #2563eb;
        color: #FFFFFF;
        padding: 12px 24px;
        z-index: 10000;
        font-weight: bold;
        text-decoration: none;
        border-radius: 0 0 8px 0;
      }}

      .skip-link:focus {{
        top: 0;
      }}

      /* Screen reader only content */
      .sr-only {{
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

      /* Reduced motion support */
      @media (prefers-reduced-motion: reduce) {{
        *, *::before, *::after {{
          animation-duration: 0.01ms !important;
          animation-iteration-count: 1 !important;
          transition-duration: 0.01ms !important;
        }}

        .dark-card:hover {{
          transform: none !important;
        }}
      }}

      /* High contrast mode support */
      @media (prefers-contrast: high) {{
        .dark-card {{
          border-width: 2px !important;
          border-color: rgba(255, 255, 255, 0.5) !important;
        }}

        .stButton > button {{
          border: 2px solid white !important;
        }}
      }}

      /* Ensure links have underline (not just color) */
      a {{
        text-decoration: underline;
        text-underline-offset: 3px;
      }}

      /* Error states with non-color indicators */
      .error-message::before {{
        content: "⚠️ ";
      }}

      .success-message::before {{
        content: "✓ ";
      }}
    </style>
    """
