"""
Tests for WCAG 2.1 AA Compliance
Sustainable Economic Development Analytics Hub
Ministry of Economy and Planning
"""

import pytest
from analytics_hub_platform.utils.wcag_compliance import (
    get_wcag_compliant_css,
    accessible_card,
    accessible_metric,
    accessible_data_table,
    get_rtl_css,
    get_keyboard_navigation_js,
    format_number_accessible,
    get_accessibility_statement,
    WCAGLevel,
    AccessibleComponentConfig,
)
from analytics_hub_platform.utils.accessibility import (
    check_contrast_ratio,
    meets_wcag_contrast,
    get_accessible_text_color,
    generate_alt_text,
    generate_aria_label,
    get_font_size_multiplier,
    get_accessible_css,
    ContrastLevel,
    FontSize,
    AccessibilityConfig,
    COLOR_BLIND_PALETTES,
)


class TestContrastRatio:
    """Test contrast ratio calculations for WCAG compliance."""
    
    def test_white_on_black_contrast(self):
        """White on black should have maximum contrast."""
        ratio = check_contrast_ratio("#FFFFFF", "#000000")
        assert ratio >= 21.0  # Maximum contrast is 21:1
    
    def test_same_color_contrast(self):
        """Same colors should have minimum contrast."""
        ratio = check_contrast_ratio("#333333", "#333333")
        assert ratio == 1.0  # Minimum contrast is 1:1
    
    def test_wcag_aa_normal_text(self):
        """Test WCAG AA compliance for normal text (4.5:1)."""
        # Good contrast
        assert meets_wcag_contrast("#FFFFFF", "#2E7D32", ContrastLevel.AA, False)
        # Poor contrast
        assert not meets_wcag_contrast("#888888", "#999999", ContrastLevel.AA, False)
    
    def test_wcag_aa_large_text(self):
        """Test WCAG AA compliance for large text (3:1)."""
        assert meets_wcag_contrast("#FFFFFF", "#666666", ContrastLevel.AA, True)
    
    def test_wcag_aaa_normal_text(self):
        """Test WCAG AAA compliance for normal text (7:1)."""
        assert meets_wcag_contrast("#FFFFFF", "#000000", ContrastLevel.AAA, False)


class TestAccessibleTextColor:
    """Test automatic text color selection for accessibility."""
    
    def test_light_background_gets_dark_text(self):
        """Light backgrounds should get dark text."""
        color = get_accessible_text_color("#FFFFFF")
        assert color == "#111827"  # Dark text
    
    def test_dark_background_gets_light_text(self):
        """Dark backgrounds should get light text."""
        color = get_accessible_text_color("#000000")
        assert color == "#FFFFFF"  # Light text
    
    def test_medium_background(self):
        """Medium backgrounds should pick the better option."""
        # This is a middle gray - should pick based on contrast
        color = get_accessible_text_color("#808080")
        assert color in ["#FFFFFF", "#111827"]


class TestAltTextGeneration:
    """Test alt text generation for charts."""
    
    def test_basic_alt_text(self):
        """Test basic alt text generation."""
        alt = generate_alt_text("line", "GDP Growth")
        assert "Line chart" in alt
        assert "GDP Growth" in alt
    
    def test_alt_text_with_stats(self):
        """Test alt text with summary statistics."""
        stats = {"min": 10, "max": 100, "trend": "increasing", "count": 24}
        alt = generate_alt_text("bar", "Employment", stats)
        assert "10" in alt
        assert "100" in alt
        assert "increasing" in alt


class TestAriaLabels:
    """Test ARIA label generation."""
    
    def test_button_label(self):
        """Test button ARIA label."""
        label = generate_aria_label("button", "Submit")
        assert "Submit" in label
        assert "button" in label
    
    def test_input_label(self):
        """Test input field ARIA label."""
        label = generate_aria_label("input", "Search")
        assert "Search" in label
        assert "input field" in label
    
    def test_label_with_context(self):
        """Test label with additional context."""
        label = generate_aria_label("select", "Region", "Choose a region")
        assert "Region" in label
        assert "Choose a region" in label


class TestColorBlindPalettes:
    """Test color blind friendly palettes."""
    
    def test_default_palette_exists(self):
        """Default palette should exist."""
        assert "default" in COLOR_BLIND_PALETTES
    
    def test_deuteranopia_palette_exists(self):
        """Deuteranopia palette should exist."""
        assert "deuteranopia" in COLOR_BLIND_PALETTES
    
    def test_all_palettes_have_required_colors(self):
        """All palettes should have required semantic colors."""
        required = {"positive", "warning", "negative", "neutral"}
        for name, palette in COLOR_BLIND_PALETTES.items():
            assert required.issubset(palette.keys()), f"{name} missing colors"


class TestFontSizeMultiplier:
    """Test font size multiplier calculations."""
    
    def test_normal_size(self):
        """Normal size should have 1.0 multiplier."""
        assert get_font_size_multiplier(FontSize.NORMAL) == 1.0
    
    def test_large_size(self):
        """Large size should have larger multiplier."""
        assert get_font_size_multiplier(FontSize.LARGE) > 1.0
    
    def test_small_size(self):
        """Small size should have smaller multiplier."""
        assert get_font_size_multiplier(FontSize.SMALL) < 1.0


class TestAccessibilityConfig:
    """Test accessibility configuration."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = AccessibilityConfig()
        assert config.keyboard_navigation is True
        assert config.focus_indicators is True
        assert config.aria_labels is True
        assert config.contrast_level == ContrastLevel.AA
    
    def test_css_vars_generation(self):
        """Test CSS variable generation from config."""
        config = AccessibilityConfig(font_size=FontSize.LARGE)
        css_vars = config.to_css_vars()
        assert "--a11y-font-size-base" in css_vars
        assert css_vars["--a11y-font-size-base"] == "18px"


class TestAccessibleCSS:
    """Test accessible CSS generation."""
    
    def test_css_contains_focus_styles(self):
        """CSS should contain focus indicator styles."""
        css = get_accessible_css()
        assert ":focus" in css
        assert "outline" in css
    
    def test_css_contains_reduced_motion(self):
        """CSS should respect reduced motion preference."""
        css = get_accessible_css()
        assert "prefers-reduced-motion" in css
    
    def test_css_contains_skip_link(self):
        """CSS should contain skip link styles."""
        css = get_accessible_css()
        assert "skip-link" in css
    
    def test_css_contains_sr_only(self):
        """CSS should contain screen reader only styles."""
        css = get_accessible_css()
        assert "sr-only" in css


class TestWCAGCompliantCSS:
    """Test WCAG compliant CSS generation."""
    
    def test_basic_css_generation(self):
        """Test basic CSS generation."""
        css = get_wcag_compliant_css()
        assert "<style>" in css
        assert "--a11y-focus-color" in css
    
    def test_rtl_css_generation(self):
        """Test RTL CSS generation."""
        css = get_wcag_compliant_css(rtl=True)
        assert "direction: rtl" in css
        assert "text-align: right" in css
    
    def test_high_contrast_css(self):
        """Test high contrast mode CSS."""
        css = get_wcag_compliant_css(high_contrast=True)
        assert "#FFFFFF" in css  # White text
        assert "#000000" in css  # Black background
    
    def test_large_text_css(self):
        """Test large text mode CSS."""
        css = get_wcag_compliant_css(large_text=True)
        assert "18px" in css


class TestAccessibleCard:
    """Test accessible card HTML generation."""
    
    def test_card_has_role(self):
        """Card should have ARIA role."""
        html = accessible_card("Test Title", "Test content")
        assert 'role="region"' in html
    
    def test_card_has_aria_labelledby(self):
        """Card should have aria-labelledby."""
        html = accessible_card("Test Title", "Test content")
        assert "aria-labelledby" in html
    
    def test_card_has_heading(self):
        """Card should have heading element."""
        html = accessible_card("Test Title", "Test content", level=2)
        assert "<h2" in html
    
    def test_card_is_focusable(self):
        """Card should be keyboard focusable."""
        html = accessible_card("Test Title", "Test content")
        assert 'tabindex="0"' in html


class TestAccessibleMetric:
    """Test accessible metric HTML generation."""
    
    def test_metric_has_status_role(self):
        """Metric should have status role for updates."""
        html = accessible_metric("GDP", "2.5T")
        assert 'role="status"' in html
    
    def test_metric_has_sr_description(self):
        """Metric should have screen reader description."""
        html = accessible_metric("GDP", "2.5T", unit="SAR")
        assert "sr-only" in html
        assert "GDP: 2.5T SAR" in html
    
    def test_metric_with_delta(self):
        """Metric with delta should be accessible."""
        html = accessible_metric("GDP", "2.5T", delta="+5.2%", delta_description="increased 5.2% from last year")
        assert "increased 5.2% from last year" in html


class TestAccessibleDataTable:
    """Test accessible data table HTML generation."""
    
    def test_table_has_role(self):
        """Table should have table role."""
        html = accessible_data_table(
            headers=["Name", "Value"],
            rows=[["GDP", "2.5T"]],
            caption="Economic indicators"
        )
        assert 'role="table"' in html
    
    def test_table_has_caption(self):
        """Table should have accessible caption."""
        html = accessible_data_table(
            headers=["Name", "Value"],
            rows=[["GDP", "2.5T"]],
            caption="Economic indicators"
        )
        assert "<caption" in html
        assert "Economic indicators" in html
    
    def test_table_has_scope(self):
        """Table headers should have scope attributes."""
        html = accessible_data_table(
            headers=["Name", "Value"],
            rows=[["GDP", "2.5T"]],
            caption="Test"
        )
        assert 'scope="col"' in html
        assert 'scope="row"' in html


class TestRTLSupport:
    """Test RTL language support."""
    
    def test_rtl_css_generation(self):
        """RTL CSS should be generated."""
        css = get_rtl_css()
        assert "[dir=\"rtl\"]" in css
        assert "direction: rtl" in css
    
    def test_rtl_numbers_preserved(self):
        """Numbers should remain LTR in RTL context."""
        css = get_rtl_css()
        assert "direction: ltr" in css  # Numbers stay LTR


class TestKeyboardNavigation:
    """Test keyboard navigation JavaScript."""
    
    def test_js_contains_keydown_handler(self):
        """JS should handle keydown events."""
        js = get_keyboard_navigation_js()
        assert "keydown" in js
    
    def test_js_handles_escape(self):
        """JS should handle Escape key."""
        js = get_keyboard_navigation_js()
        assert "Escape" in js
    
    def test_js_handles_arrow_keys(self):
        """JS should handle arrow key navigation."""
        js = get_keyboard_navigation_js()
        assert "ArrowUp" in js
        assert "ArrowDown" in js
        assert "ArrowLeft" in js
        assert "ArrowRight" in js


class TestNumberFormatting:
    """Test accessible number formatting."""
    
    def test_english_number_format(self):
        """English numbers should use standard format."""
        formatted = format_number_accessible(1234.5, lang="en")
        assert "1,234.5" in formatted
    
    def test_arabic_number_format(self):
        """Arabic numbers should use Arabic-Indic numerals."""
        formatted = format_number_accessible(123, lang="ar")
        # Should contain Arabic-Indic numerals
        assert any(char in formatted for char in "٠١٢٣٤٥٦٧٨٩")


class TestAccessibilityStatement:
    """Test accessibility statement generation."""
    
    def test_statement_contains_required_sections(self):
        """Statement should contain required sections."""
        statement = get_accessibility_statement()
        assert "Accessibility Statement" in statement
        assert "Conformance Status" in statement
        assert "WCAG 2.1" in statement
    
    def test_statement_is_proper_html(self):
        """Statement should be valid HTML."""
        statement = get_accessibility_statement()
        assert "<div" in statement
        assert "</div>" in statement
        assert 'role="region"' in statement


class TestWCAGLevelEnum:
    """Test WCAG level enumeration."""
    
    def test_level_a(self):
        """Level A should be defined."""
        assert WCAGLevel.A == "A"
    
    def test_level_aa(self):
        """Level AA should be defined."""
        assert WCAGLevel.AA == "AA"
    
    def test_level_aaa(self):
        """Level AAA should be defined."""
        assert WCAGLevel.AAA == "AAA"


class TestAccessibleComponentConfig:
    """Test accessible component configuration."""
    
    def test_default_contrast_ratio(self):
        """Default contrast ratio should meet WCAG AA."""
        config = AccessibleComponentConfig()
        assert config.min_contrast_ratio >= 4.5
    
    def test_default_touch_target(self):
        """Default touch target should be at least 44px."""
        config = AccessibleComponentConfig()
        assert config.min_touch_target >= 44
    
    def test_default_line_height(self):
        """Default line height should be at least 1.5."""
        config = AccessibleComponentConfig()
        assert config.min_line_height >= 1.5
