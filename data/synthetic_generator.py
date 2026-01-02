"""Synthetic data generator for tests and demos."""

import numpy as np
import pandas as pd

REGIONS: list[str] = [
    "Riyadh",
    "Makkah",
    "Madinah",
    "Eastern Province",
    "Qassim",
    "Asir",
    "Tabuk",
    "Hail",
    "Northern Borders",
    "Jazan",
    "Najran",
    "Al Bahah",
    "Al Jawf",
]


class SyntheticDataGenerator:
    """Generate simple synthetic KPI data with seasonality and trend."""

    def __init__(self, start_year: int = 2018, end_year: int = 2024) -> None:
        self.start_year = start_year
        self.end_year = end_year
        self.regions = REGIONS
        np.random.seed(42)

    def _build_base_series(self, n_points: int) -> pd.Series:
        trend = np.linspace(0, 2, n_points)
        seasonal = 0.3 * np.sin(2 * np.pi * np.arange(n_points) / 4)
        noise = np.random.normal(0, 0.1, n_points)
        return 5 + trend + seasonal + noise

    def generate_kpi_values(self) -> pd.DataFrame:
        years = []
        quarters = []
        for y in range(self.start_year, self.end_year + 1):
            for q in range(1, 5):
                years.append(y)
                quarters.append(q)
        values = self._build_base_series(len(years))
        return pd.DataFrame({"year": years, "quarter": quarters, "value": values})

    def generate_regions_data(self) -> pd.DataFrame:
        return pd.DataFrame({"region_id": self.regions, "region_name": self.regions})


__all__ = ["SyntheticDataGenerator", "REGIONS"]
