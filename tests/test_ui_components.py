"""
Tests for UI Components
"""



class TestHTMLRenderer:
    """Tests for safe HTML rendering."""

    def test_render_html_import(self):
        """Test that render_html can be imported."""
        from analytics_hub_platform.ui.html import render_html

        assert callable(render_html)

    def test_is_rtl_language(self):
        """Test RTL language detection."""
        from analytics_hub_platform.ui.html import is_rtl_language

        assert is_rtl_language("ar") is True
        assert is_rtl_language("he") is True
        assert is_rtl_language("en") is False
        assert is_rtl_language("fr") is False

    def test_rtl_container_start(self):
        """Test RTL container generation."""
        from analytics_hub_platform.ui.html import render_rtl_aware_container_start

        # Just verify it doesn't crash
        # Actual rendering requires Streamlit context
        assert callable(render_rtl_aware_container_start)


class TestTheme:
    """Tests for theme configuration."""

    def test_get_theme(self):
        """Test getting theme configuration."""
        from analytics_hub_platform.ui.theme import get_theme, Theme

        theme = get_theme()

        assert isinstance(theme, Theme)

    def test_theme_colors(self):
        """Test theme has required colors."""
        from analytics_hub_platform.ui.theme import get_theme

        theme = get_theme()

        # Check essential colors exist
        assert hasattr(theme.colors, "purple")
        assert hasattr(theme.colors, "cyan")
        assert hasattr(theme.colors, "green")
        assert hasattr(theme.colors, "red")
        assert hasattr(theme.colors, "amber")

    def test_hex_to_rgba(self):
        """Test hex to rgba conversion."""
        from analytics_hub_platform.ui.theme import hex_to_rgba

        result = hex_to_rgba("#ff0000", 0.5)

        assert "rgba" in result
        assert "255" in result  # Red component
        assert "0.5" in result  # Alpha


class TestDarkComponents:
    """Tests for dark theme components."""

    def test_get_dark_css(self):
        """Test getting dark CSS."""
        from analytics_hub_platform.ui.theme import get_dark_css

        css = get_dark_css()

        assert isinstance(css, str)
        assert "<style>" in css
        assert "</style>" in css

    def test_dark_theme_import(self):
        """Test dark theme can be imported."""
        from analytics_hub_platform.ui.theme import get_dark_theme

        theme = get_dark_theme()

        assert theme is not None
        assert hasattr(theme, "colors")


class TestSections:
    """Tests for dashboard sections."""

    def test_sections_import(self):
        """Test all sections can be imported."""
        from analytics_hub_platform.ui.sections import (
            render_page_header,
            render_hero_sustainability_gauge,
            render_hero_kpi_cards,
            render_pillar_section_economic,
            render_pillar_section_labor,
            render_pillar_section_environmental,
            render_key_insights_section,
            render_regional_comparison_section,
            render_yoy_comparison_section,
        )

        # All should be callable
        assert callable(render_page_header)
        assert callable(render_hero_sustainability_gauge)
        assert callable(render_hero_kpi_cards)
        assert callable(render_pillar_section_economic)
        assert callable(render_pillar_section_labor)
        assert callable(render_pillar_section_environmental)
        assert callable(render_key_insights_section)
        assert callable(render_regional_comparison_section)
        assert callable(render_yoy_comparison_section)
