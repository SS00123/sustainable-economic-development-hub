"""
ML Services Module
Sustainable Economic Development Analytics Hub
Ministry of Economy and Planning

This module provides ML-based forecasting and anomaly detection
services for KPI time-series analysis.
"""

import logging
import warnings
from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor, IsolationForest, RandomForestRegressor
from sklearn.preprocessing import StandardScaler

from analytics_hub_platform.config.constants import (
    ANOMALY_ZSCORE_CRITICAL,
    ANOMALY_ZSCORE_WARNING,
    DEFAULT_ROLLING_WINDOW,
    ML_MIN_FORECAST_POINTS,
)
from analytics_hub_platform.infrastructure.exceptions import (
    ConstantSeriesError,
    DataError,
    InsufficientDataError,
    ModelNotFittedError,
)
from analytics_hub_platform.infrastructure.settings import get_settings

warnings.filterwarnings("ignore")
logger = logging.getLogger(__name__)


class AnomalySeverity(str, Enum):
    """Anomaly severity classification."""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class ForecastResult:
    """Container for forecast results."""

    kpi_id: str
    region_id: str
    year: int
    quarter: int
    predicted_value: float
    confidence_lower: float
    confidence_upper: float
    model_type: str


@dataclass
class AnomalyResult:
    """Container for anomaly detection results."""

    kpi_id: str
    region_id: str
    year: int
    quarter: int
    actual_value: float
    expected_value: float
    deviation: float
    z_score: float
    severity: AnomalySeverity
    direction: str
    description: str


class KPIForecaster:
    """
    KPI Forecasting Engine using ensemble methods.

    Supports:
    - Gradient Boosting Regressor
    - Random Forest Regressor
    - Feature engineering with time-based features
    - Confidence intervals via quantile regression
    """

    def __init__(
        self,
        model_type: str = "gradient_boosting",
        n_estimators: int = 100,
        confidence_level: float = 0.95,
    ):
        self.model_type = model_type
        self.n_estimators = n_estimators
        self.confidence_level = confidence_level
        self.scaler = StandardScaler()
        self.model = None
        self.model_lower = None
        self.model_upper = None
        self._is_fitted = False
        self._history: list[float] = []

    def _create_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create time-based features for forecasting."""
        features = df.copy()

        features["time_idx"] = (features["year"] - features["year"].min()) * 4 + features["quarter"]
        features["quarter_sin"] = np.sin(2 * np.pi * features["quarter"] / 4)
        features["quarter_cos"] = np.cos(2 * np.pi * features["quarter"] / 4)
        features["year_norm"] = (features["year"] - features["year"].min()) / max(
            1, features["year"].max() - features["year"].min()
        )

        for lag in [1, 2, 4]:
            features[f"lag_{lag}"] = features["value"].shift(lag)

        features["rolling_mean_4"] = features["value"].rolling(window=4, min_periods=1).mean()
        features["rolling_std_4"] = (
            features["value"].rolling(window=4, min_periods=1).std().fillna(0)
        )
        features["diff_1"] = features["value"].diff(1)
        features["diff_4"] = features["value"].diff(4)

        features = features.ffill().bfill().fillna(0)

        return features

    def _get_feature_columns(self) -> list[str]:
        return [
            "time_idx",
            "quarter_sin",
            "quarter_cos",
            "year_norm",
            "lag_1",
            "lag_2",
            "lag_4",
            "rolling_mean_4",
            "rolling_std_4",
            "diff_1",
            "diff_4",
        ]

    def fit(self, df: pd.DataFrame) -> "KPIForecaster":
        """
        Fit the forecasting model with edge case handling.

        Args:
            df: DataFrame with year, quarter, value columns

        Returns:
            Self for method chaining

        Raises:
            InsufficientDataError: If not enough data points
            ConstantSeriesError: If data has zero variance
            DataError: If data contains invalid values
        """
        if df.empty or len(df) < ML_MIN_FORECAST_POINTS:
            raise InsufficientDataError(
                message=f"Need at least {ML_MIN_FORECAST_POINTS} data points for forecasting, got {len(df)}. "
                "Cannot build reliable forecast with fewer observations.",
                required_points=ML_MIN_FORECAST_POINTS,
                actual_points=len(df),
            )

        # Check for constant series (zero variance)
        if df["value"].std() == 0:
            raise ConstantSeriesError(
                message="Cannot forecast constant series (zero variance). "
                "All values are identical, no pattern to learn."
            )

        # Check for NaN/infinite values
        if df["value"].isna().any():
            raise DataError(
                message="Data contains NaN values. Please clean data before forecasting.",
                code="INVALID_DATA",
            )

        if np.isinf(df["value"]).any():
            raise DataError(
                message="Data contains infinite values. Please clean data before forecasting.",
                code="INVALID_DATA",
            )

        features_df = self._create_features(df)
        feature_cols = self._get_feature_columns()

        X = features_df[feature_cols].values
        y = features_df["value"].values

        # Additional validation after feature creation
        if np.isnan(X).any() or np.isinf(X).any():
            # Fill any remaining NaN/inf after feature engineering
            X = np.nan_to_num(X, nan=0.0, posinf=0.0, neginf=0.0)

        X_scaled = self.scaler.fit_transform(X)

        if self.model_type == "gradient_boosting":
            self.model = GradientBoostingRegressor(
                n_estimators=self.n_estimators,
                max_depth=4,
                learning_rate=0.1,
                random_state=42,
            )
            alpha = (1 - self.confidence_level) / 2
            self.model_lower = GradientBoostingRegressor(
                n_estimators=self.n_estimators,
                max_depth=4,
                learning_rate=0.1,
                loss="quantile",
                alpha=alpha,
                random_state=42,
            )
            self.model_upper = GradientBoostingRegressor(
                n_estimators=self.n_estimators,
                max_depth=4,
                learning_rate=0.1,
                loss="quantile",
                alpha=1 - alpha,
                random_state=42,
            )
        else:
            self.model = RandomForestRegressor(
                n_estimators=self.n_estimators,
                max_depth=6,
                random_state=42,
            )
            self.model_lower = None
            self.model_upper = None

        self.model.fit(X_scaled, y)
        if self.model_lower is not None:
            self.model_lower.fit(X_scaled, y)
            self.model_upper.fit(X_scaled, y)

        self._is_fitted = True
        self._last_df = features_df
        self._last_value = y[-1]
        self._history = df["value"].tolist()

        return self

    def predict(
        self,
        quarters_ahead: int = 4,
        start_year: int | None = None,
        start_quarter: int | None = None,
    ) -> list[dict[str, Any]]:
        """Generate predictions for future quarters.

        Raises:
            ModelNotFittedError: If model has not been fitted
        """
        if not self._is_fitted:
            raise ModelNotFittedError(
                message="Model must be fitted before prediction. Call fit() first."
            )

        last_row = self._last_df.iloc[-1]
        min_year = int(self._last_df["year"].min())
        max_year = int(self._last_df["year"].max())
        if start_year is None:
            start_year = int(last_row["year"])
        if start_quarter is None:
            start_quarter = int(last_row["quarter"])

        predictions = []
        current_year = start_year
        current_quarter = start_quarter
        history = list(self._history)

        for _ in range(quarters_ahead):
            current_quarter += 1
            if current_quarter > 4:
                current_quarter = 1
                current_year += 1

            # Build dynamic lag/rolling features from the latest history
            lag_1 = history[-1] if len(history) >= 1 else 0.0
            lag_2 = history[-2] if len(history) >= 2 else lag_1
            lag_4 = history[-4] if len(history) >= 4 else lag_1
            recent_window = history[-4:] if history else [0.0]
            rolling_mean_4 = float(pd.Series(recent_window).mean())
            rolling_std_4 = float(pd.Series(recent_window).std(ddof=0) or 0.0)
            diff_1 = lag_1 - lag_2 if len(history) >= 2 else 0.0
            diff_4 = lag_1 - lag_4 if len(history) >= 4 else 0.0

            time_idx = (current_year - min_year) * 4 + current_quarter
            year_norm = (current_year - min_year) / max(1, max_year - min_year)

            features = np.array(
                [
                    [
                        time_idx,
                        np.sin(2 * np.pi * current_quarter / 4),
                        np.cos(2 * np.pi * current_quarter / 4),
                        year_norm,
                        lag_1,
                        lag_2,
                        lag_4,
                        rolling_mean_4,
                        rolling_std_4,
                        diff_1,
                        diff_4,
                    ]
                ]
            )

            features_scaled = self.scaler.transform(features)
            pred = self.model.predict(features_scaled)[0]

            if self.model_lower is not None:
                lower = self.model_lower.predict(features_scaled)[0]
                upper = self.model_upper.predict(features_scaled)[0]
            else:
                std = self._last_df["value"].std() * 0.5
                lower = pred - 1.96 * std
                upper = pred + 1.96 * std

            predictions.append(
                {
                    "year": current_year,
                    "quarter": current_quarter,
                    "predicted_value": round(pred, 4),
                    "confidence_lower": round(lower, 4),
                    "confidence_upper": round(upper, 4),
                }
            )

            history.append(float(pred))
            self._last_value = pred

        return predictions


class AnomalyDetector:
    """
    Anomaly Detection Engine for KPI time series.

    Supports:
    - Z-score based detection (univariate)
    - Isolation Forest (multivariate)
    """

    def __init__(
        self,
        zscore_threshold: float = ANOMALY_ZSCORE_WARNING,
        critical_threshold: float = ANOMALY_ZSCORE_CRITICAL,
        use_rolling_stats: bool = True,
        rolling_window: int = DEFAULT_ROLLING_WINDOW,
        random_state: int | None = None,
    ):
        self.zscore_threshold = zscore_threshold
        self.critical_threshold = critical_threshold
        self.use_rolling_stats = use_rolling_stats
        self.rolling_window = rolling_window
        self.scaler = StandardScaler()
        settings = get_settings()
        self.random_state = random_state if random_state is not None else settings.ml_random_state

    def detect_anomalies(
        self,
        df: pd.DataFrame,
        kpi_id: str,
        region_id: str,
        higher_is_better: bool = True,
    ) -> list[AnomalyResult]:
        """
        Detect anomalies using Z-score method with edge case handling.

        Args:
            df: DataFrame with year, quarter, value columns
            kpi_id: KPI identifier
            region_id: Region identifier
            higher_is_better: Whether higher values indicate better performance

        Returns:
            List of detected anomalies (empty if insufficient data or constant series)
        """
        # Edge case: insufficient data
        if df.empty or len(df) < 4:
            return []

        # Edge case: check for constant series (no variation to detect anomalies)
        if df["value"].std() == 0:
            # All values are identical - no anomalies to detect
            return []

        # Edge case: filter out NaN/infinite values
        df = df[df["value"].notna() & np.isfinite(df["value"])].copy()

        if df.empty or len(df) < 4:
            return []

        df = df.sort_values(["year", "quarter"]).reset_index(drop=True)
        anomalies = []

        for i in range(len(df)):
            row = df.iloc[i]
            value = row["value"]

            if self.use_rolling_stats and i >= self.rolling_window:
                window_data = df.iloc[max(0, i - self.rolling_window) : i]["value"]
                mean = window_data.mean()
                std = window_data.std()
            else:
                if i < 2:
                    continue
                prior_data = df.iloc[:i]["value"]
                mean = prior_data.mean()
                std = prior_data.std()

            if std == 0 or np.isnan(std):
                continue

            z_score = (value - mean) / std
            abs_z = abs(z_score)

            if abs_z >= self.zscore_threshold:
                direction = "high" if z_score > 0 else "low"

                if abs_z >= self.critical_threshold:
                    severity = AnomalySeverity.CRITICAL
                else:
                    severity = AnomalySeverity.WARNING

                deviation_pct = ((value - mean) / mean * 100) if mean != 0 else 0

                is_good = (direction == "high") if higher_is_better else (direction == "low")
                desc_prefix = "Positive anomaly" if is_good else "Concerning anomaly"

                description = (
                    f"{desc_prefix}: Value is {abs(deviation_pct):.1f}% "
                    f"{'above' if direction == 'high' else 'below'} expected "
                    f"(Z-score: {z_score:.2f})"
                )

                anomalies.append(
                    AnomalyResult(
                        kpi_id=kpi_id,
                        region_id=region_id,
                        year=int(row["year"]),
                        quarter=int(row["quarter"]),
                        actual_value=round(value, 4),
                        expected_value=round(mean, 4),
                        deviation=round(value - mean, 4),
                        z_score=round(z_score, 4),
                        severity=severity,
                        direction=direction,
                        description=description,
                    )
                )

        return anomalies

    # Backward-compatible alias for tests
    def detect_zscore_anomalies(
        self,
        df: pd.DataFrame,
        kpi_id: str,
        region_id: str,
        higher_is_better: bool = True,
    ) -> list[AnomalyResult]:
        return self.detect_anomalies(df, kpi_id, region_id, higher_is_better)

    def detect_isolation_forest_anomalies(
        self,
        df: pd.DataFrame,
        kpi_id: str,
        region_id: str,
        contamination: float | None = None,
    ) -> list[AnomalyResult]:
        """Detect anomalies using Isolation Forest for multivariate patterns."""
        if df.empty:
            return []

        settings = get_settings()
        contamination_val = (
            contamination if contamination is not None else settings.anomaly_if_contamination
        )

        data = df.copy().reset_index(drop=True)
        features = data[["year", "quarter", "value"]].astype(float)
        X = self.scaler.fit_transform(features)

        iso = IsolationForest(
            contamination=contamination_val,
            random_state=self.random_state,
            n_estimators=200,
        )
        preds = iso.fit_predict(X)

        anomalies: list[AnomalyResult] = []
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
                if abs(z_score) >= self.critical_threshold
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


# Service functions for easy access
def forecast_kpi(
    df: pd.DataFrame,
    kpi_id: str,
    region_id: str,
    quarters_ahead: int = 8,
    model_type: str = "gradient_boosting",
) -> dict[str, Any]:
    """
    High-level function to forecast a KPI.

    Args:
        df: DataFrame with year, quarter, value columns
        kpi_id: KPI identifier
        region_id: Region identifier
        quarters_ahead: Number of quarters to forecast
        model_type: Model type to use

    Returns:
        Dictionary with forecast results
    """
    forecaster = KPIForecaster(model_type=model_type)
    forecaster.fit(df)
    predictions = forecaster.predict(quarters_ahead=quarters_ahead)

    return {
        "kpi_id": kpi_id,
        "region_id": region_id,
        "model_type": model_type,
        "predictions": predictions,
    }


def detect_kpi_anomalies(
    df: pd.DataFrame,
    kpi_id: str,
    region_id: str,
    higher_is_better: bool = True,
    zscore_threshold: float = 2.5,
) -> list[dict[str, Any]]:
    """
    High-level function to detect anomalies in a KPI.

    Args:
        df: DataFrame with year, quarter, value columns
        kpi_id: KPI identifier
        region_id: Region identifier
        higher_is_better: Whether higher values are better
        zscore_threshold: Z-score threshold for detection

    Returns:
        List of anomaly dictionaries
    """
    detector = AnomalyDetector(zscore_threshold=zscore_threshold)
    anomalies = detector.detect_anomalies(df, kpi_id, region_id, higher_is_better)

    return [asdict(a) for a in anomalies]
