"""
Tests for KPI Calculations and Indicators
"""

import pytest
import pandas as pd
import numpy as np


class TestIndicatorCalculations:
    """Tests for indicator calculation functions."""
    
    def test_calculate_change_positive(self):
        """Test positive change calculation."""
        from analytics_hub_platform.domain.indicators import calculate_change
        
        current = 100
        previous = 80
        abs_change, pct_change = calculate_change(current, previous)
        
        assert abs_change == pytest.approx(20.0, rel=0.01)  # 100 - 80 = 20
        assert pct_change == pytest.approx(25.0, rel=0.01)  # 20/80 * 100 = 25%
    
    def test_calculate_change_negative(self):
        """Test negative change calculation."""
        from analytics_hub_platform.domain.indicators import calculate_change
        
        current = 80
        previous = 100
        abs_change, pct_change = calculate_change(current, previous)
        
        assert abs_change == pytest.approx(-20.0, rel=0.01)  # 80 - 100 = -20
        assert pct_change == pytest.approx(-20.0, rel=0.01)  # -20/100 * 100 = -20%
    
    def test_calculate_change_zero_previous(self):
        """Test change calculation with zero previous value."""
        from analytics_hub_platform.domain.indicators import calculate_change
        
        current = 100
        previous = 0
        abs_change, pct_change = calculate_change(current, previous)
        
        # Should handle division by zero gracefully
        assert abs_change == pytest.approx(100.0, rel=0.01)
        assert pct_change is None
    
    def test_calculate_change_none_values(self):
        """Test change calculation with None values."""
        from analytics_hub_platform.domain.indicators import calculate_change
        
        # Should handle None gracefully
        assert calculate_change(None, 100) == (None, None)
        assert calculate_change(100, None) == (None, None)


class TestSustainabilityIndex:
    """Tests for sustainability index calculations."""
    
    def test_sustainability_index_range(self, sample_dataframe):
        """Test that sustainability index is within valid range."""
        # Sustainability index should be 0-100
        assert sample_dataframe["sustainability_index"].min() >= 0
        assert sample_dataframe["sustainability_index"].max() <= 100
    
    def test_sustainability_status_green(self):
        """Test green status for high sustainability."""
        from analytics_hub_platform.domain.models import KPIStatus
        
        # Index >= 70 should be green
        def get_status(value):
            if value >= 70:
                return KPIStatus.GREEN
            elif value >= 40:
                return KPIStatus.AMBER
            else:
                return KPIStatus.RED
        
        assert get_status(75) == KPIStatus.GREEN
        assert get_status(70) == KPIStatus.GREEN
    
    def test_sustainability_status_amber(self):
        """Test amber status for medium sustainability."""
        from analytics_hub_platform.domain.models import KPIStatus
        
        def get_status(value):
            if value >= 70:
                return KPIStatus.GREEN
            elif value >= 40:
                return KPIStatus.AMBER
            else:
                return KPIStatus.RED
        
        assert get_status(50) == KPIStatus.AMBER
        assert get_status(40) == KPIStatus.AMBER
    
    def test_sustainability_status_red(self):
        """Test red status for low sustainability."""
        from analytics_hub_platform.domain.models import KPIStatus
        
        def get_status(value):
            if value >= 70:
                return KPIStatus.GREEN
            elif value >= 40:
                return KPIStatus.AMBER
            else:
                return KPIStatus.RED
        
        assert get_status(30) == KPIStatus.RED
        assert get_status(0) == KPIStatus.RED


class TestKPIFormatting:
    """Tests for KPI value formatting."""
    
    def test_format_large_numbers(self):
        """Test formatting of large numbers."""
        def format_value(value):
            if abs(value) >= 1_000_000_000:
                return f"{value / 1_000_000_000:.1f}B"
            elif abs(value) >= 1_000_000:
                return f"{value / 1_000_000:.1f}M"
            elif abs(value) >= 1_000:
                return f"{value / 1_000:.1f}K"
            else:
                return f"{value:.1f}"
        
        assert format_value(1_500_000_000) == "1.5B"
        assert format_value(2_500_000) == "2.5M"
        assert format_value(3_500) == "3.5K"
        assert format_value(150) == "150.0"
    
    def test_format_percentage(self):
        """Test percentage formatting."""
        def format_percent(value):
            return f"{value:.1f}%"
        
        assert format_percent(12.345) == "12.3%"
        assert format_percent(-5.67) == "-5.7%"
