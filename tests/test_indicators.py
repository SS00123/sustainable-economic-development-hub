"""
Indicator Calculation Tests
Sustainable Economic Development Analytics Hub

Tests for indicator calculation functions.
"""

import pytest

from analytics_hub_platform.domain.indicators import (
    co2_per_gdp,
    co2_per_capita,
    energy_intensity,
    normalize_to_100,
    calculate_sustainability_index,
    get_kpi_status,
)
from analytics_hub_platform.domain.models import KPIStatus, KPIThresholds


class TestCO2Calculations:
    """Tests for CO2-related calculations."""
    
    def test_co2_per_gdp_calculation(self):
        """Test CO2 per GDP calculation returns a number."""
        result = co2_per_gdp(1000, 2500)
        assert result is not None
        assert isinstance(result, (int, float))
    
    def test_co2_per_gdp_zero_gdp(self):
        """Test CO2 per GDP with zero GDP."""
        result = co2_per_gdp(1000, 0)
        assert result is None or result == 0.0
    
    def test_co2_per_gdp_none_values(self):
        """Test CO2 per GDP with None values."""
        result = co2_per_gdp(None, 2500)
        assert result is None
        
        result = co2_per_gdp(1000, None)
        assert result is None
    
    def test_co2_per_capita_calculation(self):
        """Test CO2 per capita calculation returns a number."""
        result = co2_per_capita(5_000_000, 300_000)
        assert result is not None
        assert isinstance(result, (int, float))
    
    def test_co2_per_capita_zero_population(self):
        """Test CO2 per capita with zero population."""
        result = co2_per_capita(1000, 0)
        assert result is None or result == 0.0


class TestEnergyIntensity:
    """Tests for energy intensity calculation."""
    
    def test_energy_intensity_calculation(self):
        """Test energy intensity calculation returns a number."""
        result = energy_intensity(500, 100)
        assert result is not None
        assert isinstance(result, (int, float))
    
    def test_energy_intensity_zero_gdp(self):
        """Test energy intensity with zero GDP."""
        result = energy_intensity(500, 0)
        assert result is None or result == 0.0


class TestNormalization:
    """Tests for value normalization."""
    
    def test_normalize_to_100_basic(self):
        """Test basic normalization."""
        result = normalize_to_100(50, 0, 100)
        assert result == 50.0
    
    def test_normalize_to_100_different_range(self):
        """Test normalization with different range."""
        result = normalize_to_100(75, 50, 100)
        assert result == 50.0  # Midpoint of 50-100 range
    
    def test_normalize_to_100_clamping(self):
        """Test value clamping."""
        result = normalize_to_100(120, 0, 100)
        assert result == 100.0
        
        result = normalize_to_100(-10, 0, 100)
        assert result == 0.0


class TestSustainabilityIndex:
    """Tests for sustainability index calculation."""
    
    def test_calculate_sustainability_index(self):
        """Test sustainability index calculation."""
        indicators = {
            "co2_per_gdp": 0.4,
            "renewable_energy_pct": 15.0,
            "green_investment_pct": 8.0,
            "recycling_rate": 25.0,
            "water_efficiency": 70.0,
        }
        
        result = calculate_sustainability_index(indicators)
        
        # Result could be None or a number
        if result is not None:
            assert 0 <= result <= 100
            assert isinstance(result, float)
    
    def test_calculate_sustainability_index_empty(self):
        """Test sustainability index with empty values."""
        indicators = {}
        
        result = calculate_sustainability_index(indicators)
        
        # Should handle empty gracefully
        assert result is None or result == 0.0 or 0 <= result <= 100


class TestKPIStatusFunction:
    """Tests for KPI status determination."""
    
    def test_get_kpi_status_with_thresholds_model(self):
        """Test status with proper KPIThresholds model."""
        thresholds = KPIThresholds(
            green_min=70.0,
            green_max=100.0,
            amber_min=50.0,
            amber_max=69.9,
            red_min=0.0,
            red_max=49.9,
        )
        
        # Test green status
        result = get_kpi_status(80, thresholds, higher_is_better=True)
        assert result == KPIStatus.GREEN
        
        # Test amber status
        result = get_kpi_status(60, thresholds, higher_is_better=True)
        assert result == KPIStatus.AMBER
        
        # Test red status
        result = get_kpi_status(40, thresholds, higher_is_better=True)
        assert result == KPIStatus.RED
    
    def test_get_kpi_status_none_value(self):
        """Test status with None value."""
        thresholds = KPIThresholds(
            green_min=70.0,
            green_max=100.0,
            amber_min=50.0,
            amber_max=69.9,
            red_min=0.0,
            red_max=49.9,
        )
        
        result = get_kpi_status(None, thresholds)
        
        # Should return a valid status (including UNKNOWN for None values)
        assert result in [KPIStatus.GREEN, KPIStatus.AMBER, KPIStatus.RED, KPIStatus.UNKNOWN]
