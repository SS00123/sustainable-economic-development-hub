"""
Indicator Calculation Tests
Sustainable Economic Development Analytics Hub

Tests for indicator calculation functions.
"""

import pytest
import numpy as np

from analytics_hub_platform.domain.indicators import (
    co2_per_gdp,
    co2_per_capita,
    energy_intensity_calc,
    normalize_to_100,
    calculate_sustainability_index,
    get_kpi_status,
)
from analytics_hub_platform.domain.models import KPIStatus


class TestCO2Calculations:
    """Tests for CO2-related calculations."""
    
    def test_co2_per_gdp_calculation(self):
        """Test CO2 per GDP calculation."""
        # 1000 tonnes CO2, 2500 million SAR GDP
        result = co2_per_gdp(1000, 2500)
        assert result == pytest.approx(0.4, rel=0.01)
    
    def test_co2_per_gdp_zero_gdp(self):
        """Test CO2 per GDP with zero GDP."""
        result = co2_per_gdp(1000, 0)
        assert result == 0.0
    
    def test_co2_per_gdp_none_values(self):
        """Test CO2 per GDP with None values."""
        result = co2_per_gdp(None, 2500)
        assert result == 0.0
        
        result = co2_per_gdp(1000, None)
        assert result == 0.0
    
    def test_co2_per_capita_calculation(self):
        """Test CO2 per capita calculation."""
        # 5 million tonnes CO2, 300000 population
        result = co2_per_capita(5_000_000, 300_000)
        assert result == pytest.approx(16.67, rel=0.01)
    
    def test_co2_per_capita_zero_population(self):
        """Test CO2 per capita with zero population."""
        result = co2_per_capita(1000, 0)
        assert result == 0.0


class TestEnergyIntensity:
    """Tests for energy intensity calculation."""
    
    def test_energy_intensity_calculation(self):
        """Test energy intensity calculation."""
        # 500 TJ energy, 100 million SAR GDP
        result = energy_intensity_calc(500, 100)
        assert result == pytest.approx(5.0, rel=0.01)
    
    def test_energy_intensity_zero_gdp(self):
        """Test energy intensity with zero GDP."""
        result = energy_intensity_calc(500, 0)
        assert result == 0.0


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
    
    def test_normalize_to_100_inverse(self):
        """Test inverse normalization (lower is better)."""
        # For CO2 where lower is better
        result = normalize_to_100(0.3, 0, 1, inverse=True)
        assert result == 70.0  # 1 - 0.3 = 0.7 normalized
    
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
        
        assert 0 <= result <= 100
        assert isinstance(result, float)
    
    def test_calculate_sustainability_index_perfect(self):
        """Test sustainability index with perfect values."""
        indicators = {
            "co2_per_gdp": 0.0,  # Perfect - no emissions
            "renewable_energy_pct": 100.0,  # Perfect - all renewable
            "green_investment_pct": 50.0,  # High investment
            "recycling_rate": 100.0,  # Perfect recycling
            "water_efficiency": 100.0,  # Perfect efficiency
        }
        
        result = calculate_sustainability_index(indicators)
        
        assert result > 80  # Should be high
    
    def test_calculate_sustainability_index_poor(self):
        """Test sustainability index with poor values."""
        indicators = {
            "co2_per_gdp": 1.0,  # High emissions
            "renewable_energy_pct": 0.0,  # No renewable
            "green_investment_pct": 0.0,  # No investment
            "recycling_rate": 0.0,  # No recycling
            "water_efficiency": 0.0,  # Poor efficiency
        }
        
        result = calculate_sustainability_index(indicators)
        
        assert result < 30  # Should be low
    
    def test_calculate_sustainability_index_missing_data(self):
        """Test sustainability index with missing data."""
        indicators = {
            "co2_per_gdp": 0.4,
            "renewable_energy_pct": None,
            "green_investment_pct": 8.0,
        }
        
        result = calculate_sustainability_index(indicators)
        
        # Should handle missing values gracefully
        assert 0 <= result <= 100


class TestKPIStatus:
    """Tests for KPI status determination."""
    
    def test_get_kpi_status_green(self):
        """Test green status for high value (higher is better)."""
        thresholds = {"green": 70, "amber": 50}
        
        result = get_kpi_status(80, thresholds, higher_is_better=True)
        
        assert result == KPIStatus.GREEN
    
    def test_get_kpi_status_amber(self):
        """Test amber status for medium value."""
        thresholds = {"green": 70, "amber": 50}
        
        result = get_kpi_status(60, thresholds, higher_is_better=True)
        
        assert result == KPIStatus.AMBER
    
    def test_get_kpi_status_red(self):
        """Test red status for low value."""
        thresholds = {"green": 70, "amber": 50}
        
        result = get_kpi_status(40, thresholds, higher_is_better=True)
        
        assert result == KPIStatus.RED
    
    def test_get_kpi_status_inverse(self):
        """Test status for lower is better (e.g., CO2)."""
        thresholds = {"green": 0.35, "amber": 0.50}
        
        # Low value should be green
        result = get_kpi_status(0.30, thresholds, higher_is_better=False)
        assert result == KPIStatus.GREEN
        
        # High value should be red
        result = get_kpi_status(0.60, thresholds, higher_is_better=False)
        assert result == KPIStatus.RED
    
    def test_get_kpi_status_none_value(self):
        """Test status with None value."""
        thresholds = {"green": 70, "amber": 50}
        
        result = get_kpi_status(None, thresholds)
        
        assert result == KPIStatus.NEUTRAL
