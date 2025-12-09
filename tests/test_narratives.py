"""
Narrative Generation Tests
Sustainable Economic Development Analytics Hub

Tests for narrative generation utilities.
"""

import pytest

from analytics_hub_platform.utils.narratives import (
    generate_executive_narrative,
    generate_director_narrative,
    generate_narrative,
    _plural,
    _get_item_name,
    _get_item_value,
    _format_signed_percent,
)
from analytics_hub_platform.domain.models import DashboardSummary


class TestHelperFunctions:
    """Tests for helper functions."""
    
    def test_plural_singular(self):
        """Test plural function with singular value."""
        assert _plural(1, "indicator", "indicators") == "indicator"
    
    def test_plural_plural(self):
        """Test plural function with plural value."""
        assert _plural(0, "indicator", "indicators") == "indicators"
        assert _plural(2, "indicator", "indicators") == "indicators"
        assert _plural(100, "indicator", "indicators") == "indicators"
    
    def test_get_item_name_display_name(self):
        """Test _get_item_name with display_name."""
        item = {"display_name": "GDP Growth", "name": "gdp", "kpi_name": "gdp_growth"}
        assert _get_item_name(item) == "GDP Growth"
    
    def test_get_item_name_fallback_name(self):
        """Test _get_item_name fallback to name."""
        item = {"name": "GDP Growth", "kpi_name": "gdp_growth"}
        assert _get_item_name(item) == "GDP Growth"
    
    def test_get_item_name_fallback_kpi_name(self):
        """Test _get_item_name fallback to kpi_name."""
        item = {"kpi_name": "gdp_growth"}
        assert _get_item_name(item) == "gdp_growth"
    
    def test_get_item_name_unknown(self):
        """Test _get_item_name returns Unknown for empty dict."""
        item = {}
        assert _get_item_name(item) == "Unknown"
    
    def test_get_item_value_change_percent(self):
        """Test _get_item_value with change_percent."""
        item = {"change_percent": 5.5, "value": 10.0}
        assert _get_item_value(item) == 5.5
    
    def test_get_item_value_fallback_value(self):
        """Test _get_item_value fallback to value."""
        item = {"value": 10.0}
        assert _get_item_value(item) == 10.0
    
    def test_get_item_value_default(self):
        """Test _get_item_value returns 0 for empty dict."""
        item = {}
        assert _get_item_value(item) == 0.0
    
    def test_format_signed_percent_positive(self):
        """Test positive percentage formatting."""
        assert _format_signed_percent(5.5) == "+5.5%"
    
    def test_format_signed_percent_negative(self):
        """Test negative percentage formatting."""
        assert _format_signed_percent(-3.2) == "-3.2%"
    
    def test_format_signed_percent_zero(self):
        """Test zero percentage formatting."""
        assert _format_signed_percent(0) == "0.0%"


class TestExecutiveNarrative:
    """Tests for executive narrative generation."""
    
    def test_generate_executive_narrative_dict(self):
        """Test narrative generation from dict snapshot."""
        snapshot = {
            "period": "Q4 2024",
            "metrics": {
                "sustainability_index": {"value": 72.5, "status": "green"},
                "gdp_growth": {"value": 3.2, "status": "green"},
                "unemployment_rate": {"value": 5.5, "status": "amber"},
            },
            "top_improvements": [
                {"display_name": "GDP Growth", "change_percent": 1.5},
            ],
            "top_deteriorations": [
                {"display_name": "Unemployment", "change_percent": -0.5},
            ],
        }
        
        narrative = generate_executive_narrative(snapshot, "en")
        
        assert narrative is not None
        assert len(narrative) > 0
        assert "Sustainability" in narrative or "indicator" in narrative
    
    def test_generate_executive_narrative_empty(self):
        """Test narrative with empty snapshot."""
        snapshot = {
            "period": "Q4 2024",
            "metrics": {},
            "top_improvements": [],
            "top_deteriorations": [],
        }
        
        narrative = generate_executive_narrative(snapshot, "en")
        
        assert narrative is not None
    
    def test_generate_executive_narrative_arabic(self):
        """Test Arabic narrative generation."""
        snapshot = {
            "period": "Q4 2024",
            "metrics": {
                "sustainability_index": {"value": 72.5, "status": "green"},
            },
            "top_improvements": [],
            "top_deteriorations": [],
        }
        
        narrative = generate_executive_narrative(snapshot, "ar")
        
        assert narrative is not None


class TestDirectorNarrative:
    """Tests for director narrative generation."""
    
    def test_generate_director_narrative(self):
        """Test director narrative generation."""
        snapshot = {
            "period": "Q4 2024",
            "metrics": {
                "sustainability_index": {"value": 72.5, "status": "green"},
                "gdp_growth": {"value": 3.2, "status": "green"},
            },
            "top_improvements": [
                {"display_name": "Renewable Share", "change_percent": 2.5},
            ],
            "top_deteriorations": [],
        }
        
        narrative = generate_director_narrative(snapshot, "en")
        
        assert narrative is not None
        assert "Performance" in narrative or "indicator" in narrative


class TestDashboardSummaryNarrative:
    """Tests for narrative from DashboardSummary."""
    
    def test_generate_narrative_from_summary(self):
        """Test narrative from DashboardSummary object."""
        summary = DashboardSummary(
            total_indicators=10,
            on_target_count=6,
            warning_count=3,
            critical_count=1,
            improving_count=4,
            declining_count=2,
            average_achievement=75.0,
            sustainability_index=72.5,
            top_performers=[],
            attention_needed=[],
            period="Q4 2024",
        )
        
        narrative = generate_narrative(summary, "en")
        
        assert narrative is not None
        assert "72.5" in narrative or "Sustainability" in narrative
