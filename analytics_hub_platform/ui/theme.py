"""
Consolidated Theme Configuration
Sustainable Economic Development Analytics Hub
Ministry of Economy and Planning

Single source of truth for all theme tokens: colors, typography, spacing, shadows.
This replaces fragmented theme definitions across multiple files.

Usage:
    from analytics_hub_platform.ui.theme import theme, colors, spacing, typography
    
    # Or get the full theme object
    from analytics_hub_platform.ui.theme import get_theme
    t = get_theme()
    print(t.colors.primary)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from functools import lru_cache
from typing import Tuple


@dataclass(frozen=True)
class Colors:
    """
    Complete color palette for the dark premium theme.
    
    Organized by category for easy discovery and consistent usage.
    """

    # === Background Colors ===
    bg_deep: str = "#0B1120"        # Deepest background
    bg_main: str = "#111827"        # Main canvas
    bg_card: str = "#1E293B"        # Card background
    bg_card_alt: str = "#1E2340"    # Alternate card background
    bg_hover: str = "#334155"       # Hover state
    bg_glass: str = "linear-gradient(135deg, rgba(255,255,255,0.08) 0%, rgba(255,255,255,0.02) 100%)"

    # === Primary Accent Colors ===
    primary: str = "#06B6D4"        # Cyan - primary accent
    secondary: str = "#3B82F6"      # Blue - secondary accent
    purple: str = "#8B5CF6"         # Violet/Purple
    purple_dark: str = "#7C3AED"    # Darker purple
    pink: str = "#EC4899"           # Pink accent
    cyan: str = "#06B6D4"           # Cyan (alias)
    blue: str = "#3B82F6"           # Blue (alias)

    # === Status Colors ===
    green: str = "#10B981"          # Success/On track
    green_bg: str = "rgba(16, 185, 129, 0.15)"
    amber: str = "#F59E0B"          # Warning/At risk
    amber_bg: str = "rgba(245, 158, 11, 0.15)"
    red: str = "#EF4444"            # Error/Off track
    red_bg: str = "rgba(239, 68, 68, 0.15)"

    # === Domain/Pillar Colors ===
    domain_economic: str = "#3B82F6"       # Blue
    domain_labor: str = "#8B5CF6"          # Violet
    domain_social: str = "#06B6D4"         # Cyan
    domain_environmental: str = "#10B981"  # Green
    domain_data_quality: str = "#64748B"   # Slate

    # === Text Colors ===
    text_primary: str = "rgba(255, 255, 255, 0.95)"
    text_secondary: str = "rgba(255, 255, 255, 0.78)"
    text_muted: str = "rgba(255, 255, 255, 0.55)"
    text_subtle: str = "rgba(255, 255, 255, 0.35)"

    # === Border Colors ===
    border: str = "rgba(255, 255, 255, 0.08)"
    border_light: str = "rgba(255, 255, 255, 0.12)"
    border_glow: str = "rgba(168, 85, 247, 0.3)"

    # === Chart Palette ===
    chart_palette: Tuple[str, ...] = (
        "#06B6D4",  # Cyan
        "#3B82F6",  # Blue
        "#10B981",  # Green
        "#F59E0B",  # Amber
        "#EF4444",  # Red
        "#8B5CF6",  # Violet
        "#EC4899",  # Pink
        "#14B8A6",  # Teal
        "#F472B6",  # Light pink
        "#818CF8",  # Indigo
    )

    def get_status_color(self, status: str) -> str:
        """Get color for a status value."""
        status_map = {
            "green": self.green,
            "amber": self.amber,
            "red": self.red,
            "success": self.green,
            "warning": self.amber,
            "error": self.red,
            "on_track": self.green,
            "at_risk": self.amber,
            "off_track": self.red,
        }
        return status_map.get(status.lower(), self.text_muted)

    def get_status_bg(self, status: str) -> str:
        """Get background color for a status value."""
        status_map = {
            "green": self.green_bg,
            "amber": self.amber_bg,
            "red": self.red_bg,
        }
        return status_map.get(status.lower(), "rgba(255,255,255,0.05)")

    def get_domain_color(self, domain: str) -> str:
        """Get color for a domain/pillar category."""
        domain_map = {
            "economic": self.domain_economic,
            "labor": self.domain_labor,
            "social": self.domain_social,
            "environmental": self.domain_environmental,
            "data_quality": self.domain_data_quality,
            "economy": self.domain_economic,
            "labor_skills": self.domain_labor,
            "social_digital": self.domain_social,
            "environment": self.domain_environmental,
        }
        return domain_map.get(domain.lower(), self.primary)


@dataclass(frozen=True)
class Typography:
    """Typography scale and font settings."""

    # === Font Family ===
    font_family: str = "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"

    # === Size Scale ===
    size_hero: str = "48px"      # Hero numbers
    size_h1: str = "32px"        # Page title
    size_h2: str = "24px"        # Section headers
    size_h3: str = "18px"        # Card titles
    size_h4: str = "16px"        # Sub-section titles
    size_body: str = "14px"      # Body text
    size_caption: str = "12px"   # Captions
    size_small: str = "11px"     # Small text
    size_tiny: str = "10px"      # Tiny labels

    # === Font Weights ===
    weight_regular: int = 400
    weight_medium: int = 500
    weight_semibold: int = 600
    weight_bold: int = 700
    weight_extrabold: int = 800


@dataclass(frozen=True)
class Spacing:
    """Spacing scale for margins and padding."""

    xs: str = "4px"
    sm: str = "8px"
    md: str = "16px"
    lg: str = "24px"
    xl: str = "32px"
    xxl: str = "48px"

    # === Named spacing ===
    page_margin: str = "32px"
    section_gap: str = "32px"
    card_gap: str = "24px"
    row_gap: str = "20px"
    gutter: str = "16px"


@dataclass(frozen=True)
class Radius:
    """Border radius scale."""

    xs: str = "4px"
    sm: str = "6px"
    md: str = "8px"
    lg: str = "12px"
    xl: str = "16px"
    xxl: str = "20px"
    full: str = "9999px"

    # === Named radius ===
    card: str = "16px"
    button: str = "8px"
    input: str = "8px"
    badge: str = "20px"


@dataclass(frozen=True)
class Shadows:
    """Box shadow definitions."""

    # === Card Shadows ===
    card: str = "0 4px 6px rgba(0, 0, 0, 0.1), 0 20px 50px rgba(0, 0, 0, 0.4)"
    card_hover: str = "0 8px 16px rgba(0, 0, 0, 0.15), 0 30px 60px rgba(0, 0, 0, 0.45)"
    card_sm: str = "0 2px 4px rgba(0, 0, 0, 0.1), 0 10px 20px rgba(0, 0, 0, 0.3)"
    card_subtle: str = "0 4px 12px rgba(0, 0, 0, 0.25)"

    # === Glow Effects ===
    glow_purple: str = "0 0 40px rgba(168, 85, 247, 0.15)"
    glow_cyan: str = "0 0 40px rgba(6, 182, 212, 0.15)"
    glow_pink: str = "0 0 40px rgba(236, 72, 153, 0.15)"
    glow_green: str = "0 0 20px rgba(16, 185, 129, 0.3)"
    glow_amber: str = "0 0 20px rgba(245, 158, 11, 0.3)"
    glow_red: str = "0 0 20px rgba(239, 68, 68, 0.3)"

    # === Inset ===
    inset_highlight: str = "inset 0 1px 0 rgba(255, 255, 255, 0.08)"
    inset_shadow: str = "inset 0 -1px 0 rgba(0, 0, 0, 0.1)"


@dataclass(frozen=True)
class Transitions:
    """Transition timing presets."""

    fast: str = "150ms ease"
    normal: str = "200ms ease"
    slow: str = "300ms ease"
    smooth: str = "280ms cubic-bezier(0.4, 0, 0.2, 1)"


@dataclass
class Theme:
    """
    Complete theme configuration combining all token categories.
    
    Usage:
        theme = get_theme()
        bg = theme.colors.bg_main
        font = theme.typography.font_family
    """

    colors: Colors = field(default_factory=Colors)
    typography: Typography = field(default_factory=Typography)
    spacing: Spacing = field(default_factory=Spacing)
    radius: Radius = field(default_factory=Radius)
    shadows: Shadows = field(default_factory=Shadows)
    transitions: Transitions = field(default_factory=Transitions)


@lru_cache(maxsize=1)
def get_theme() -> Theme:
    """
    Get the singleton theme instance.
    
    Returns:
        Theme object with all design tokens
    """
    return Theme()


# === Convenience exports ===
# These provide direct access to token categories without needing to call get_theme()

@lru_cache(maxsize=1)
def _get_colors() -> Colors:
    return get_theme().colors


@lru_cache(maxsize=1)
def _get_typography() -> Typography:
    return get_theme().typography


@lru_cache(maxsize=1)
def _get_spacing() -> Spacing:
    return get_theme().spacing


@lru_cache(maxsize=1)
def _get_radius() -> Radius:
    return get_theme().radius


@lru_cache(maxsize=1)
def _get_shadows() -> Shadows:
    return get_theme().shadows


# Direct access objects
colors = _get_colors()
typography = _get_typography()
spacing = _get_spacing()
radius = _get_radius()
shadows = _get_shadows()


def hex_to_rgba(hex_color: str, alpha: float) -> str:
    """
    Convert hex color to rgba format.
    
    Args:
        hex_color: Hex color string (e.g., '#3B82F6')
        alpha: Alpha value between 0 and 1

    Returns:
        RGBA string (e.g., 'rgba(59, 130, 246, 0.15)')
    """
    hex_color = hex_color.lstrip("#")
    if len(hex_color) == 3:
        hex_color = "".join([c * 2 for c in hex_color])
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return f"rgba({r}, {g}, {b}, {alpha})"


def get_gradient(
    start: str | None = None,
    end: str | None = None,
    direction: str = "135deg",
) -> str:
    """
    Generate a linear gradient string.
    
    Args:
        start: Start color (defaults to purple)
        end: End color (defaults to cyan)
        direction: Gradient direction

    Returns:
        CSS linear-gradient string
    """
    c = get_theme().colors
    start = start or c.purple
    end = end or c.cyan
    return f"linear-gradient({direction}, {start}, {end})"


def get_chart_layout_config() -> dict:
    """
    Get standard Plotly chart layout configuration for dark theme.
    
    Returns:
        Dictionary of Plotly layout settings
    """
    c = get_theme().colors
    t = get_theme().typography

    return {
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(0,0,0,0)",
        "font": {
            "family": t.font_family,
            "color": c.text_secondary,
            "size": 12,
        },
        "margin": {"l": 40, "r": 20, "t": 40, "b": 40},
        "xaxis": {
            "gridcolor": c.border,
            "linecolor": c.border,
            "tickfont": {"color": c.text_muted},
            "showgrid": True,
            "gridwidth": 1,
        },
        "yaxis": {
            "gridcolor": c.border,
            "linecolor": c.border,
            "tickfont": {"color": c.text_muted},
            "showgrid": True,
            "gridwidth": 1,
        },
        "legend": {
            "font": {"color": c.text_secondary},
            "bgcolor": "rgba(0,0,0,0)",
        },
        "hoverlabel": {
            "bgcolor": c.bg_card,
            "bordercolor": c.border_light,
            "font": {"color": c.text_primary, "size": 12},
        },
    }


def get_css() -> str:
    """
    Return the complete CSS for the dark 3D dashboard theme.
    This should be injected via st.markdown at the start of the app.

    Enhanced with premium glassmorphism, animated gradients, and micro-interactions.
    """
    t = get_theme()
    c = t.colors
    s = t.shadows
    ty = t.typography
    sp = t.spacing
    r = t.radius

    return f"""
    <style>
      /* ===== CSS Custom Properties (Premium Design System) ===== */
      :root {{
        --bg0: {c.bg_deep};
        --bg1: {c.bg_main};
        --card: {c.bg_card};
        --card2: {c.bg_card_alt};
        --stroke: {c.border};
        --stroke-glow: rgba(168, 85, 247, 0.3);
        --muted: {c.text_secondary};
        --muted2: {c.text_muted};
        --white: {c.text_primary};
        --primary: {c.primary};
        --secondary: {c.secondary};
        --purple: {c.purple};
        --purple2: {c.purple_dark};
        --pink: {c.pink};
        --cyan: {c.cyan};
        --blue: {c.blue};
        --green: {c.green};
        --amber: {c.amber};
        --red: {c.red};
        --domain-economic: {c.domain_economic};
        --domain-labor: {c.domain_labor};
        --domain-social: {c.domain_social};
        --domain-env: {c.domain_environmental};
        --shadow: {s.card};
        --shadow2: {s.card_hover};
        --radius: {r.card};
        --radius-lg: {r.xxl};
        --gutter: {sp.lg};
        --margin: {sp.page_margin};
        --glass-bg: linear-gradient(135deg, rgba(255,255,255,0.08) 0%, rgba(255,255,255,0.02) 100%);
        --glass-border: rgba(255,255,255,0.12);
        --glow-purple: 0 0 40px rgba(168, 85, 247, 0.15);
        --glow-cyan: 0 0 40px rgba(6, 182, 212, 0.15);
        --glow-pink: 0 0 40px rgba(236, 72, 153, 0.15);
      }}

      /* ===== Google Fonts Import for Premium Typography ===== */
      @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

      /* ===== App Background (Premium Multi-Layer Gradient) ===== */
      html, body, [data-testid="stAppViewContainer"] {{
        background:
          radial-gradient(ellipse 1400px 900px at 5% 5%, rgba(168, 85, 247, 0.08), transparent 50%),
          radial-gradient(ellipse 1200px 800px at 95% 10%, rgba(6, 182, 212, 0.06), transparent 45%),
          radial-gradient(ellipse 1000px 600px at 50% 80%, rgba(236, 72, 153, 0.04), transparent 40%),
          radial-gradient(ellipse 800px 500px at 30% 60%, rgba(59, 130, 246, 0.05), transparent 35%),
          linear-gradient(180deg, {c.bg_deep} 0%, #0F172A 50%, {c.bg_card} 100%);
        color: var(--white);
        min-height: 100vh;
        font-family: 'Inter', {ty.font_family};
        font-size: {ty.size_body};
        line-height: 1.6;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
      }}

      /* ===== Animated Background Mesh ===== */
      [data-testid="stAppViewContainer"]::before {{
        content: "";
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-image:
          linear-gradient(rgba(168, 85, 247, 0.03) 1px, transparent 1px),
          linear-gradient(90deg, rgba(168, 85, 247, 0.03) 1px, transparent 1px);
        background-size: 60px 60px;
        pointer-events: none;
        z-index: 0;
        opacity: 0.5;
      }}

      /* Hide Streamlit chrome */
      #MainMenu, footer, header {{ visibility: hidden; }}
      [data-testid="stSidebar"] {{ display: none !important; }}

      /* ===== Layout Container (Enhanced Spacing) ===== */
      .block-container {{
        padding-top: 20px !important;
        padding-bottom: 40px !important;
        padding-left: 32px !important;
        padding-right: 32px !important;
        max-width: 1440px !important;
        position: relative;
        z-index: 1;
      }}

      /* Remove default white containers */
      [data-testid="stVerticalBlock"], [data-testid="stHorizontalBlock"] {{
        gap: 20px;
      }}

      /* ===== Premium Glassmorphism Card ===== */
      .dark-card {{
        background: var(--glass-bg);
        border: 1px solid var(--glass-border);
        border-radius: 16px;
        box-shadow:
          0 4px 6px rgba(0, 0, 0, 0.1),
          0 20px 50px rgba(0, 0, 0, 0.4),
          inset 0 1px 0 rgba(255, 255, 255, 0.08),
          inset 0 -1px 0 rgba(0, 0, 0, 0.1);
        padding: 24px 26px;
        -webkit-backdrop-filter: blur(20px) saturate(180%);
        backdrop-filter: blur(20px) saturate(180%);
        position: relative;
        overflow: hidden;
        transition: all 280ms cubic-bezier(0.4, 0, 0.2, 1);
      }}

      /* Card Shine Effect */
      .dark-card::before {{
        content: "";
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(
          90deg,
          transparent,
          rgba(255, 255, 255, 0.03),
          transparent
        );
        transition: left 600ms ease;
        pointer-events: none;
      }}

      .dark-card:hover {{
        transform: translateY(-4px) scale(1.005);
        border-color: rgba(168, 85, 247, 0.25);
        box-shadow:
          0 8px 16px rgba(0, 0, 0, 0.15),
          0 30px 60px rgba(0, 0, 0, 0.45),
          var(--glow-purple),
          inset 0 1px 0 rgba(255, 255, 255, 0.12);
      }}

      .dark-card:hover::before {{
        left: 100%;
      }}

      .dark-card .card-title {{
        font-size: 11px;
        font-weight: 600;
        color: var(--muted);
        letter-spacing: 1px;
        text-transform: uppercase;
        margin-bottom: 8px;
      }}

      .dark-card .card-value {{
        font-size: 32px;
        font-weight: 800;
        color: var(--white);
        margin: 8px 0;
        letter-spacing: -0.5px;
        background: linear-gradient(135deg, rgba(255,255,255,0.98), rgba(255,255,255,0.85));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
      }}

      .dark-card .card-sub {{
        font-size: 12px;
        color: var(--muted2);
        margin-top: 4px;
        line-height: 1.5;
      }}

      /* ===== Premium Delta Badges ===== */
      .delta {{
        font-size: 11px;
        font-weight: 600;
        padding: 4px 12px;
        border-radius: 20px;
        border: 1px solid rgba(255,255,255,0.08);
        background: rgba(255,255,255,0.04);
        display: inline-flex;
        gap: 5px;
        align-items: center;
        transition: all 200ms ease;
      }}

      .delta.positive {{
        color: {c.green};
        border-color: rgba(16, 185, 129, 0.35);
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.15), rgba(16, 185, 129, 0.08));
        box-shadow: 0 0 20px rgba(16, 185, 129, 0.1);
      }}

      .delta.negative {{
        color: {c.red};
        border-color: rgba(239, 68, 68, 0.35);
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.15), rgba(239, 68, 68, 0.08));
        box-shadow: 0 0 20px rgba(239, 68, 68, 0.1);
      }}

      /* ===== Premium Sidebar Container ===== */
      .side {{
        background: linear-gradient(180deg, rgba(15, 23, 42, 0.98), rgba(11, 17, 32, 0.98));
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 20px;
        box-shadow:
          0 25px 60px rgba(0, 0, 0, 0.5),
          inset 0 1px 0 rgba(255, 255, 255, 0.05);
        overflow: hidden;
        height: 100%;
        min-height: 88vh;
        -webkit-backdrop-filter: blur(24px);
        backdrop-filter: blur(24px);
      }}

      .side-top {{
        padding: 24px 20px;
        background: linear-gradient(145deg, rgba(168, 85, 247, 0.92), rgba(139, 92, 246, 0.85), rgba(236, 72, 153, 0.7));
        position: relative;
        overflow: hidden;
      }}

      .side-top::before {{
        content: "";
        position: absolute;
        top: -40%;
        right: -25%;
        width: 180px;
        height: 180px;
        background: radial-gradient(circle, rgba(255,255,255,0.25) 0%, transparent 65%);
        border-radius: 50%;
        animation: float-orb 8s ease-in-out infinite;
      }}

      .side-top::after {{
        content: "";
        position: absolute;
        bottom: -30%;
        left: -15%;
        width: 140px;
        height: 140px;
        background: radial-gradient(circle, rgba(34, 211, 238, 0.35) 0%, transparent 60%);
        border-radius: 50%;
        animation: float-orb 6s ease-in-out infinite reverse;
      }}

      @keyframes float-orb {{
        0%, 100% {{ transform: translate(0, 0) scale(1); }}
        50% {{ transform: translate(10px, 15px) scale(1.1); }}
      }}

      .brand {{
        font-weight: 800;
        letter-spacing: 0.3px;
        color: rgba(255,255,255,0.98);
        font-size: 15px;
        position: relative;
        z-index: 2;
        text-shadow: 0 2px 10px rgba(0,0,0,0.3);
      }}

      .nav a {{
        display: flex;
        gap: 12px;
        align-items: center;
        padding: 14px 16px;
        border-radius: 14px;
        text-decoration: none;
        color: rgba(255,255,255,0.65);
        font-size: 13px;
        font-weight: 500;
        border: 1px solid transparent;
        margin-bottom: 6px;
        transition: all 220ms cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
      }}

      .nav a::before {{
        content: "";
        position: absolute;
        left: 0;
        top: 0;
        bottom: 0;
        width: 0;
        background: linear-gradient(90deg, rgba(168, 85, 247, 0.3), transparent);
        transition: width 220ms ease;
        border-radius: 14px;
      }}

      .nav a:hover {{
        background: linear-gradient(135deg, rgba(168, 85, 247, 0.15), rgba(34, 211, 238, 0.08));
        border-color: rgba(168, 85, 247, 0.3);
        color: rgba(255,255,255,0.98);
        transform: translateX(6px);
        box-shadow: 0 4px 20px rgba(168, 85, 247, 0.15);
      }}

      .nav a:hover::before {{
        width: 100%;
      }}

      .nav .dot {{
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: linear-gradient(135deg, {c.purple}, {c.cyan});
        box-shadow: 0 0 16px rgba(168, 85, 247, 0.7);
        flex-shrink: 0;
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
        background: linear-gradient(135deg, rgba(168, 85, 247, 0.2), rgba(34, 211, 238, 0.15));
        border-color: rgba(168, 85, 247, 0.4);
        transform: translateY(-2px);
        box-shadow: 0 4px 16px rgba(168, 85, 247, 0.2);
      }}

      /* ===== Premium Form Inputs ===== */
      .stTextInput input {{
        background: linear-gradient(135deg, rgba(255,255,255,0.06), rgba(255,255,255,0.03)) !important;
        border: 1px solid rgba(255,255,255,0.12) !important;
        border-radius: 14px !important;
        color: var(--white) !important;
        height: 44px;
        padding: 0 20px !important;
        font-size: 13px !important;
        transition: all 200ms ease !important;
        box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.1);
      }}

      .stTextInput input:focus {{
        border-color: rgba(168, 85, 247, 0.5) !important;
        box-shadow:
          0 0 0 3px rgba(168, 85, 247, 0.15),
          inset 0 2px 4px rgba(0, 0, 0, 0.1) !important;
        outline: none !important;
      }}

      .stTextInput input::placeholder {{
        color: rgba(255,255,255,0.35);
      }}

      /* Premium Select Boxes */
      .stSelectbox > div > div {{
        background: linear-gradient(135deg, rgba(255,255,255,0.06), rgba(255,255,255,0.03)) !important;
        border: 1px solid rgba(255,255,255,0.12) !important;
        border-radius: 12px !important;
        color: var(--white) !important;
        min-height: 44px !important;
        transition: all 200ms ease !important;
      }}

      .stSelectbox > div > div:hover {{
        border-color: rgba(168, 85, 247, 0.4) !important;
      }}

      .stSelectbox > div > div:focus-within {{
        border-color: rgba(168, 85, 247, 0.5) !important;
        box-shadow: 0 0 0 3px rgba(168, 85, 247, 0.15) !important;
      }}

      .stSelectbox label {{
        color: var(--muted) !important;
        font-size: 11px !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.8px !important;
        margin-bottom: 6px !important;
      }}

      /* Dropdown menu styling */
      [data-baseweb="popover"] {{
        background: linear-gradient(180deg, rgba(27, 31, 54, 0.98), rgba(15, 17, 34, 0.98)) !important;
        border: 1px solid rgba(168, 85, 247, 0.25) !important;
        border-radius: 14px !important;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5) !important;
        -webkit-backdrop-filter: blur(20px);
        backdrop-filter: blur(20px);
      }}

      [data-baseweb="menu"] {{
        background: transparent !important;
      }}

      [data-baseweb="menu"] li {{
        color: rgba(255, 255, 255, 0.75) !important;
        border-radius: 10px !important;
        margin: 2px 6px !important;
        transition: all 150ms ease !important;
      }}

      [data-baseweb="menu"] li:hover {{
        background: linear-gradient(135deg, rgba(168, 85, 247, 0.2), rgba(34, 211, 238, 0.1)) !important;
        color: rgba(255, 255, 255, 0.98) !important;
      }}

      /* ===== Premium Metric Styling ===== */
      [data-testid="stMetricValue"] {{
        color: var(--white) !important;
        font-size: 28px !important;
        font-weight: 700 !important;
        letter-spacing: -0.3px !important;
      }}
      [data-testid="stMetricLabel"] {{
        color: var(--muted) !important;
        font-size: 12px !important;
        font-weight: 500 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
      }}
      [data-testid="stMetricDelta"] {{
        color: var(--cyan) !important;
        font-weight: 600 !important;
      }}

      /* ===== Plotly Charts Premium ===== */
      .js-plotly-plot .plotly .main-svg {{
        border-radius: 14px;
      }}
      .stPlotlyChart {{
        background: transparent !important;
        border-radius: 14px;
      }}

      /* ===== Premium Section Headers ===== */
      .section-header {{
        font-size: 18px;
        font-weight: 700;
        color: var(--white);
        margin: 28px 0 12px 0;
        display: flex;
        align-items: center;
        gap: 12px;
        letter-spacing: -0.3px;
        position: relative;
      }}

      .section-header::after {{
        content: "";
        flex: 1;
        height: 2px;
        margin-left: 16px;
        background: linear-gradient(90deg,
          rgba(168, 85, 247, 0.6),
          rgba(34, 211, 238, 0.4),
          rgba(236, 72, 153, 0.2),
          transparent 80%);
        border-radius: 2px;
      }}

      .section-sub {{
        font-size: 13px;
        color: var(--muted2);
        margin: -6px 0 20px 0;
        padding-left: 2px;
      }}

      /* ===== Enhanced Status Pills ===== */
      .status-pill {{
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 8px 18px;
        border-radius: 12px;
        font-weight: 600;
        font-size: 13px;
        margin: 4px;
        transition: all 200ms ease;
        position: relative;
        overflow: hidden;
      }}

      .status-pill::before {{
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(180deg, rgba(255,255,255,0.1) 0%, transparent 50%);
      }}
    </style>
    """


# === Backward Compatibility Aliases ===
get_dark_css = get_css
get_dark_theme = get_theme
DarkColorPalette = Colors
DarkTheme = Theme

