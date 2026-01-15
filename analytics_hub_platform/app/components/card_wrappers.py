"""Card wrapper components: open/close for dark card blocks.

Canonical implementations migrated from ui.dark_components.
"""

from __future__ import annotations

from analytics_hub_platform.ui.html import render_html


def card_open(
    title: str,
    subtitle: str | None = None,
    right_html: str | None = None,
    accent_color: str | None = None,
    glow: bool = False,
) -> None:
    """
    Open a styled dark card wrapper with premium glassmorphism effect.

    Args:
        title: Card title
        subtitle: Optional subtitle text
        right_html: Optional HTML to render on the right side of header
        accent_color: Optional accent color for left border glow
        glow: Whether to add a subtle glow effect
    """
    subtitle_html = f"<div class='card-sub'>{subtitle}</div>" if subtitle else ""
    right = right_html or ""

    # Build accent/glow styles
    accent_style = ""
    if accent_color:
        accent_style = f"border-left: 3px solid {accent_color}; box-shadow: -4px 0 20px {accent_color}25;"
    if glow:
        accent_style += " box-shadow: 0 0 40px rgba(168, 85, 247, 0.15);"

    render_html(
        f"""
        <div class="dark-card" style="{accent_style}">
          <div style="display:flex; align-items:flex-start; justify-content:space-between; gap:16px; margin-bottom: 16px;">
            <div>
              <div class="card-title">{title}</div>
              {subtitle_html}
            </div>
            <div>{right}</div>
          </div>
        """
    )


def card_close() -> None:
    """Close the styled dark card wrapper."""
    render_html("</div>")
