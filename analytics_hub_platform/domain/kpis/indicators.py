"""Indicator calculations.

This is the canonical module for KPI indicator calculations.
The legacy `analytics_hub_platform.domain.indicators` module re-exports these
symbols for backward compatibility.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from analytics_hub_platform.domain.models import KPIStatus, KPIThresholds

# ============================================
# DERIVED INDICATOR CALCULATIONS
# ============================================


def co2_per_gdp(co2_total: float | None, gdp_total: float | None) -> float | None:
    """Calculate CO2 emissions per unit of GDP."""
    if co2_total is None or gdp_total is None:
        return None
    if gdp_total <= 0:
        return None
    return (co2_total * 1_000_000) / gdp_total


def co2_per_capita(co2_total: float | None, population: float | None) -> float | None:
    """Calculate CO2 emissions per capita."""
    if co2_total is None or population is None:
        return None
    if population <= 0:
        return None
    return co2_total / population


def energy_intensity(energy_consumption: float | None, gdp_total: float | None) -> float | None:
    """Calculate energy intensity (energy per unit of GDP)."""
    if energy_consumption is None or gdp_total is None:
        return None
    if gdp_total <= 0:
        return None
    return (energy_consumption * 1_000_000) / gdp_total


# ============================================
# NORMALIZATION
# ============================================


def normalize_to_100(
    value: float | None, min_val: float, max_val: float, inverse: bool = False
) -> float | None:
    """Normalize a value to a 0-100 scale."""
    if value is None:
        return None
    if max_val == min_val:
        return 50.0

    normalized = (value - min_val) / (max_val - min_val) * 100
    normalized = max(0.0, min(100.0, normalized))
    if inverse:
        normalized = 100.0 - normalized
    return round(normalized, 2)


# ============================================
# KPI STATUS DETERMINATION
# ============================================


def get_kpi_status(
    value: float | None, thresholds: KPIThresholds | None, higher_is_better: bool | None = True
) -> KPIStatus:
    """Determine the status (green/amber/red) for a KPI value."""
    if value is None or thresholds is None:
        return KPIStatus.UNKNOWN

    if thresholds.green_min <= value <= thresholds.green_max:
        return KPIStatus.GREEN
    if thresholds.amber_min <= value <= thresholds.amber_max:
        return KPIStatus.AMBER
    if thresholds.red_min <= value <= thresholds.red_max:
        return KPIStatus.RED
    return KPIStatus.UNKNOWN


def get_status_from_catalog(kpi_id: str, value: float | None, catalog: dict[str, Any]) -> KPIStatus:
    """Get KPI status using the catalog configuration."""
    if value is None:
        return KPIStatus.UNKNOWN

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
    catalog_path = Path(__file__).parents[2] / "config" / "kpi_catalog.yaml"
    if catalog_path.exists():
        with open(catalog_path, encoding="utf-8") as f:
            return yaml.safe_load(f)
    return {"kpis": []}


def get_sustainability_weights(catalog: dict[str, Any] | None = None) -> dict[str, float]:
    """Get the weights for sustainability index calculation from catalog."""
    if catalog is None:
        _load_kpi_catalog()
        return _get_weights_cached()
    return _extract_weights(catalog)


@lru_cache(maxsize=1)
def _get_weights_cached() -> dict[str, float]:
    return _extract_weights(_load_kpi_catalog())


def _extract_weights(catalog: dict[str, Any]) -> dict[str, float]:
    weights: dict[str, float] = {}
    for kpi in catalog.get("kpis", []):
        weight = kpi.get("default_weight_in_sustainability_index", 0.0)
        if weight > 0:
            weights[kpi["id"]] = weight
    return weights


def get_kpi_ranges(catalog: dict[str, Any] | None = None) -> dict[str, tuple[float, float, bool]]:
    """Get min/max ranges and inverse flag for KPIs from catalog."""
    if catalog is None:
        _load_kpi_catalog()
        return _get_ranges_cached()
    return _extract_ranges(catalog)


@lru_cache(maxsize=1)
def _get_ranges_cached() -> dict[str, tuple[float, float, bool]]:
    return _extract_ranges(_load_kpi_catalog())


def _extract_ranges(catalog: dict[str, Any]) -> dict[str, tuple[float, float, bool]]:
    ranges: dict[str, tuple[float, float, bool]] = {}
    for kpi in catalog.get("kpis", []):
        if kpi.get("min_value") is not None and kpi.get("max_value") is not None:
            higher_is_better = kpi.get("higher_is_better", True)
            inverse = higher_is_better is False
            ranges[kpi["id"]] = (kpi["min_value"], kpi["max_value"], inverse)
    return ranges


def calculate_sustainability_index(
    indicators: dict[str, float | None],
    catalog: dict[str, Any] | None = None,
    weights: dict[str, float] | None = None,
    ranges: dict[str, tuple[float, float, bool]] | None = None,
) -> float | None:
    """Calculate the composite sustainability index (0-100)."""
    if catalog is None:
        catalog = _load_kpi_catalog()
    if weights is None:
        weights = get_sustainability_weights(catalog)
    if ranges is None:
        ranges = get_kpi_ranges(catalog)
    if not weights:
        return None

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
        if normalized is None:
            continue

        weighted_sum += normalized * weight
        total_weight += weight
        components_used += 1

    if components_used < 3 or total_weight == 0:
        return None

    sustainability_index = weighted_sum / total_weight
    return round(sustainability_index, 2)


def get_sustainability_breakdown(
    indicators: dict[str, float | None], catalog: dict[str, Any] | None = None
) -> list[dict[str, Any]]:
    """Get detailed breakdown of sustainability index components."""
    if catalog is None:
        catalog = _load_kpi_catalog()

    weights = get_sustainability_weights(catalog)
    ranges = get_kpi_ranges(catalog)

    breakdown: list[dict[str, Any]] = []
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

        thresholds = KPIThresholds(**kpi["thresholds"]) if kpi.get("thresholds") else None
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

    breakdown.sort(key=lambda x: x["weight"], reverse=True)
    return breakdown


# ============================================
# CHANGE CALCULATIONS
# ============================================


def calculate_change(
    current: float | None, previous: float | None
) -> tuple[float | None, float | None]:
    """Calculate absolute and percentage change between two values."""
    if current is None or previous is None:
        return None, None

    absolute_change = current - previous
    if previous == 0:
        percent_change = None
    else:
        percent_change = (absolute_change / abs(previous)) * 100

    return round(absolute_change, 2), round(percent_change, 2) if percent_change else None


def get_change_direction(change: float | None, higher_is_better: bool = True) -> str:
    """Determine if a change is positive or negative."""
    if change is None or change == 0:
        return "neutral"
    if higher_is_better:
        return "positive" if change > 0 else "negative"
    return "positive" if change < 0 else "negative"


__all__ = [
    "KPIStatus",
    "KPIThresholds",
    "co2_per_gdp",
    "co2_per_capita",
    "energy_intensity",
    "normalize_to_100",
    "get_kpi_status",
    "get_status_from_catalog",
    "get_sustainability_weights",
    "get_kpi_ranges",
    "calculate_sustainability_index",
    "get_sustainability_breakdown",
    "calculate_change",
    "get_change_direction",
]
