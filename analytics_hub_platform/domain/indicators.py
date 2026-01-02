"""
Indicator Calculations
Sustainable Economic Development Analytics Hub
Ministry of Economy and Planning

This module contains functions for calculating:
- Derived indicators (CO2 per GDP, CO2 per capita, etc.)
- Normalized values (0-100 scale)
- Composite sustainability index
- KPI status determination (green/amber/red)

All calculations use configuration from kpi_catalog.yaml for
thresholds and weights, ensuring consistency and maintainability.
"""

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from analytics_hub_platform.domain.models import KPIStatus, KPIThresholds

# ============================================
# DERIVED INDICATOR CALCULATIONS
# ============================================


def co2_per_gdp(co2_total: float | None, gdp_total: float | None) -> float | None:
    """
    Calculate CO2 emissions per unit of GDP.

    Args:
        co2_total: Total CO2 emissions in million tons
        gdp_total: Total GDP in million SAR

    Returns:
        CO2 per million SAR of GDP (tons/M SAR), or None if inputs invalid
    """
    if co2_total is None or gdp_total is None:
        return None
    if gdp_total <= 0:
        return None

    # Convert: MT CO2 / M SAR = tons per million SAR
    return (co2_total * 1_000_000) / gdp_total


def co2_per_capita(co2_total: float | None, population: float | None) -> float | None:
    """
    Calculate CO2 emissions per capita.

    Args:
        co2_total: Total CO2 emissions in million tons
        population: Population in millions

    Returns:
        CO2 per capita (tons per person), or None if inputs invalid
    """
    if co2_total is None or population is None:
        return None
    if population <= 0:
        return None

    # MT CO2 / M people = tons per person
    return co2_total / population


def energy_intensity(energy_consumption: float | None, gdp_total: float | None) -> float | None:
    """
    Calculate energy intensity (energy per unit of GDP).

    Args:
        energy_consumption: Total energy consumption (e.g., in PJ)
        gdp_total: Total GDP in million SAR

    Returns:
        Energy intensity (MJ per SAR), or None if inputs invalid
    """
    if energy_consumption is None or gdp_total is None:
        return None
    if gdp_total <= 0:
        return None

    # Convert PJ to MJ and divide by GDP
    return (energy_consumption * 1_000_000) / gdp_total


# ============================================
# NORMALIZATION
# ============================================


def normalize_to_100(
    value: float | None, min_val: float, max_val: float, inverse: bool = False
) -> float | None:
    """
    Normalize a value to a 0-100 scale.

    Args:
        value: The value to normalize
        min_val: Minimum value in the expected range
        max_val: Maximum value in the expected range
        inverse: If True, lower values map to higher scores
                 (for "lower is better" indicators like CO2)

    Returns:
        Normalized value between 0 and 100, clamped at boundaries
        Returns None if value is None
    """
    if value is None:
        return None

    if max_val == min_val:
        return 50.0  # Cannot normalize with zero range

    # Calculate normalized value
    normalized = (value - min_val) / (max_val - min_val) * 100

    # Clamp to 0-100
    normalized = max(0.0, min(100.0, normalized))

    # Inverse for "lower is better" indicators
    if inverse:
        normalized = 100.0 - normalized

    return round(normalized, 2)


# ============================================
# KPI STATUS DETERMINATION
# ============================================


def get_kpi_status(
    value: float | None, thresholds: KPIThresholds | None, higher_is_better: bool | None = True
) -> KPIStatus:
    """
    Determine the status (green/amber/red) for a KPI value.

    Args:
        value: The KPI value to evaluate
        thresholds: Threshold configuration for this KPI
        higher_is_better: Whether higher values are desirable

    Returns:
        KPIStatus enum value
    """
    if value is None or thresholds is None:
        return KPIStatus.UNKNOWN

    # Check against thresholds
    if thresholds.green_min <= value <= thresholds.green_max:
        return KPIStatus.GREEN
    elif thresholds.amber_min <= value <= thresholds.amber_max:
        return KPIStatus.AMBER
    elif thresholds.red_min <= value <= thresholds.red_max:
        return KPIStatus.RED
    else:
        # Value outside all defined ranges
        return KPIStatus.UNKNOWN


def get_status_from_catalog(kpi_id: str, value: float | None, catalog: dict[str, Any]) -> KPIStatus:
    """
    Get KPI status using the catalog configuration.

    Args:
        kpi_id: The KPI identifier
        value: The KPI value
        catalog: The loaded KPI catalog dictionary

    Returns:
        KPIStatus enum value
    """
    if value is None:
        return KPIStatus.UNKNOWN

    # Find KPI in catalog
    kpi_def = None
    for kpi in catalog.get("kpis", []):
        if kpi.get("id") == kpi_id:
            kpi_def = kpi
            break

    if kpi_def is None or kpi_def.get("thresholds") is None:
        return KPIStatus.UNKNOWN

    thresholds = KPIThresholds(**kpi_def["thresholds"])
    higher_is_better = kpi_def.get("higher_is_better", True)

    return get_kpi_status(value, thresholds, higher_is_better)


# ============================================
# SUSTAINABILITY INDEX CALCULATION
# ============================================


@lru_cache(maxsize=1)
def _load_kpi_catalog() -> dict[str, Any]:
    """Load KPI catalog from YAML file. Cached for performance."""
    catalog_path = Path(__file__).parent.parent / "config" / "kpi_catalog.yaml"
    if catalog_path.exists():
        with open(catalog_path, encoding="utf-8") as f:
            return yaml.safe_load(f)
    return {"kpis": []}


def get_sustainability_weights(catalog: dict[str, Any] | None = None) -> dict[str, float]:
    """
    Get the weights for sustainability index calculation from catalog.

    Returns:
        Dictionary mapping KPI IDs to their weights
    """
    if catalog is None:
        catalog = _load_kpi_catalog()
        # Use cached version when using default catalog
        return _get_weights_cached()

    # Non-cached path for custom catalog
    return _extract_weights(catalog)


@lru_cache(maxsize=1)
def _get_weights_cached() -> dict[str, float]:
    """Cached version using default catalog."""
    return _extract_weights(_load_kpi_catalog())


def _extract_weights(catalog: dict[str, Any]) -> dict[str, float]:
    """Extract weights from catalog dictionary."""
    weights = {}
    for kpi in catalog.get("kpis", []):
        weight = kpi.get("default_weight_in_sustainability_index", 0.0)
        if weight > 0:
            weights[kpi["id"]] = weight
    return weights


def get_kpi_ranges(catalog: dict[str, Any] | None = None) -> dict[str, tuple[float, float, bool]]:
    """
    Get min/max ranges and inverse flag for KPIs from catalog.

    Returns:
        Dictionary mapping KPI IDs to (min_value, max_value, inverse)
    """
    if catalog is None:
        catalog = _load_kpi_catalog()
        # Use cached version when using default catalog
        return _get_ranges_cached()

    # Non-cached path for custom catalog
    return _extract_ranges(catalog)


@lru_cache(maxsize=1)
def _get_ranges_cached() -> dict[str, tuple[float, float, bool]]:
    """Cached version using default catalog."""
    return _extract_ranges(_load_kpi_catalog())


def _extract_ranges(catalog: dict[str, Any]) -> dict[str, tuple[float, float, bool]]:
    """Extract ranges from catalog dictionary."""
    ranges = {}
    for kpi in catalog.get("kpis", []):
        if kpi.get("min_value") is not None and kpi.get("max_value") is not None:
            higher_is_better = kpi.get("higher_is_better", True)
            # Inverse normalization for "lower is better" indicators
            inverse = higher_is_better is False
            ranges[kpi["id"]] = (kpi["min_value"], kpi["max_value"], inverse)
    return ranges


def calculate_sustainability_index(
    indicators: dict[str, float | None],
    catalog: dict[str, Any] | None = None,
    weights: dict[str, float] | None = None,
    ranges: dict[str, tuple[float, float, bool]] | None = None,
) -> float | None:
    """
    Calculate the composite sustainability index (0-100).

    The index is a weighted average of normalized environmental
    and green economy indicators. Weights and ranges are loaded
    from the KPI catalog configuration.

    Args:
        indicators: Dictionary of KPI values keyed by KPI ID
        catalog: Optional pre-loaded KPI catalog
        weights: Optional pre-loaded weights (for testing)
        ranges: Optional pre-loaded ranges (for testing)

    Returns:
        Composite sustainability index (0-100), or None if insufficient data

    Example:
        >>> indicators = {
        ...     "co2_index": 85.0,
        ...     "renewable_share": 25.0,
        ...     "energy_intensity": 6.0,
        ...     "water_efficiency": 65.0,
        ...     "waste_recycling_rate": 35.0,
        ...     "air_quality_index": 75.0,
        ...     "forest_coverage": 3.0,
        ...     "green_jobs": 150.0,
        ... }
        >>> index = calculate_sustainability_index(indicators)
    """
    if catalog is None:
        catalog = _load_kpi_catalog()

    if weights is None:
        weights = get_sustainability_weights(catalog)

    if ranges is None:
        ranges = get_kpi_ranges(catalog)

    if not weights:
        return None

    # Normalize each indicator and calculate weighted sum
    weighted_sum = 0.0
    total_weight = 0.0
    components_used = 0

    for kpi_id, weight in weights.items():
        value = indicators.get(kpi_id)
        if value is None:
            continue

        if kpi_id not in ranges:
            continue

        min_val, max_val, inverse = ranges[kpi_id]
        normalized = normalize_to_100(value, min_val, max_val, inverse)

        if normalized is not None:
            weighted_sum += normalized * weight
            total_weight += weight
            components_used += 1

    # Require at least 3 components for a meaningful index
    if components_used < 3 or total_weight == 0:
        return None

    # Normalize by actual weight used (in case some indicators are missing)
    sustainability_index = weighted_sum / total_weight

    return round(sustainability_index, 2)


def get_sustainability_breakdown(
    indicators: dict[str, float | None], catalog: dict[str, Any] | None = None
) -> list[dict[str, Any]]:
    """
    Get detailed breakdown of sustainability index components.

    Returns a list of component contributions for transparency
    and explanation of the composite index.

    Args:
        indicators: Dictionary of KPI values
        catalog: Optional pre-loaded KPI catalog

    Returns:
        List of dictionaries with component details
    """
    if catalog is None:
        catalog = _load_kpi_catalog()

    weights = get_sustainability_weights(catalog)
    ranges = get_kpi_ranges(catalog)

    breakdown = []

    for kpi in catalog.get("kpis", []):
        kpi_id = kpi["id"]
        weight = weights.get(kpi_id, 0.0)

        if weight == 0:
            continue

        value = indicators.get(kpi_id)

        if value is None or kpi_id not in ranges:
            breakdown.append(
                {
                    "kpi_id": kpi_id,
                    "name_en": kpi["display_name_en"],
                    "name_ar": kpi["display_name_ar"],
                    "raw_value": None,
                    "normalized_value": None,
                    "weight": weight,
                    "contribution": None,
                    "status": "missing",
                }
            )
            continue

        min_val, max_val, inverse = ranges[kpi_id]
        normalized = normalize_to_100(value, min_val, max_val, inverse)
        contribution = normalized * weight if normalized else None

        # Get status
        thresholds = None
        if kpi.get("thresholds"):
            thresholds = KPIThresholds(**kpi["thresholds"])
        status = get_kpi_status(value, thresholds, kpi.get("higher_is_better", True))

        breakdown.append(
            {
                "kpi_id": kpi_id,
                "name_en": kpi["display_name_en"],
                "name_ar": kpi["display_name_ar"],
                "raw_value": value,
                "normalized_value": normalized,
                "weight": weight,
                "contribution": contribution,
                "status": status.value,
                "unit": kpi["unit"],
            }
        )

    # Sort by weight (highest first)
    breakdown.sort(key=lambda x: x["weight"], reverse=True)

    return breakdown


# ============================================
# CHANGE CALCULATIONS
# ============================================


def calculate_change(
    current: float | None, previous: float | None
) -> tuple[float | None, float | None]:
    """
    Calculate absolute and percentage change between two values.

    Args:
        current: Current period value
        previous: Previous period value

    Returns:
        Tuple of (absolute_change, percent_change)
    """
    if current is None or previous is None:
        return None, None

    absolute_change = current - previous

    if previous == 0:
        percent_change = None
    else:
        percent_change = (absolute_change / abs(previous)) * 100

    return round(absolute_change, 2), round(percent_change, 2) if percent_change else None


def get_change_direction(change: float | None, higher_is_better: bool = True) -> str:
    """
    Determine if a change is positive or negative based on whether higher is better.

    Args:
        change: The change value
        higher_is_better: Whether higher values are desirable

    Returns:
        "positive", "negative", or "neutral"
    """
    if change is None or change == 0:
        return "neutral"

    if higher_is_better:
        return "positive" if change > 0 else "negative"
    else:
        return "positive" if change < 0 else "negative"
