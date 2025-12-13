"""Anomaly detection wrapper providing the interface expected by tests."""

from dataclasses import asdict
from typing import List, Optional
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

from analytics_hub_platform.domain.ml_services import (
    AnomalyDetector as CoreAnomalyDetector,
    AnomalyResult,
    AnomalySeverity,
)


class AnomalyDetector:
    """Facade matching legacy test API while delegating to core detector."""

    def __init__(
        self,
        zscore_threshold: float = 2.5,
        critical_threshold: float = 3.5,
        use_rolling_stats: bool = True,
        rolling_window: int = 8,
    ) -> None:
        self._core = CoreAnomalyDetector(
            zscore_threshold=zscore_threshold,
            critical_threshold=critical_threshold,
            use_rolling_stats=use_rolling_stats,
            rolling_window=rolling_window,
        )
        self.zscore_threshold = zscore_threshold

    # Legacy API expected by tests
    def detect_zscore_anomalies(
        self,
        df: pd.DataFrame,
        kpi_id: str,
        region_id: str,
        higher_is_better: bool = True,
    ) -> List[AnomalyResult]:
        return self._core.detect_anomalies(df, kpi_id, region_id, higher_is_better)

    def detect_isolation_forest_anomalies(
        self,
        df: pd.DataFrame,
        kpi_id: str,
        region_id: str,
        contamination: float = 0.1,
    ) -> List[AnomalyResult]:
        """Lightweight IsolationForest-based detector for tests."""
        if df.empty:
            return []

        # Prepare features
        data = df.copy().reset_index(drop=True)
        features = data[["year", "quarter", "value"]].astype(float)
        scaler = StandardScaler()
        X = scaler.fit_transform(features)

        iso = IsolationForest(
            contamination=contamination,
            random_state=42,
            n_estimators=200,
        )
        preds = iso.fit_predict(X)

        anomalies: List[AnomalyResult] = []
        mean_val = float(data["value"].mean())
        std_val = float(data["value"].std() or 1.0)

        for idx, pred in enumerate(preds):
            if pred != -1:
                continue

            row = data.iloc[idx]
            actual = float(row["value"])
            z_score = (actual - mean_val) / std_val if std_val else 0.0
            direction = "high" if actual >= mean_val else "low"
            severity = (
                AnomalySeverity.CRITICAL
                if abs(z_score) >= 3.5
                else AnomalySeverity.WARNING
            )

            anomalies.append(
                AnomalyResult(
                    kpi_id=kpi_id,
                    region_id=region_id,
                    year=int(row["year"]),
                    quarter=int(row["quarter"]),
                    actual_value=round(actual, 4),
                    expected_value=round(mean_val, 4),
                    deviation=round(actual - mean_val, 4),
                    z_score=round(z_score, 4),
                    severity=severity,
                    direction=direction,
                    description=(
                        f"IsolationForest anomaly: {direction} deviation (z={z_score:.2f})"
                    ),
                )
            )

        return anomalies


__all__ = ["AnomalyDetector", "AnomalyResult", "AnomalySeverity"]
