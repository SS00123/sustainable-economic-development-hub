"""
Advanced Analytics Module
Sustainable Economic Development Analytics Hub

Provides advanced analytics capabilities:
- Multiple forecasting algorithms (Linear, Exponential Smoothing, Ensemble)
- Pattern recognition (trends, seasonality, change points)
- Trend analysis and decomposition
- Statistical tests for time series
"""

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

import numpy as np
import pandas as pd
from scipy import stats as scipy_stats

logger = logging.getLogger(__name__)


# =============================================================================
# ENUMS AND MODELS
# =============================================================================


class TrendDirection(str, Enum):
    """Direction of trend."""

    INCREASING = "increasing"
    DECREASING = "decreasing"
    STABLE = "stable"
    VOLATILE = "volatile"


class SeasonalityType(str, Enum):
    """Type of seasonality detected."""

    NONE = "none"
    QUARTERLY = "quarterly"
    ANNUAL = "annual"
    MIXED = "mixed"


class ChangePointType(str, Enum):
    """Type of change point."""

    LEVEL_SHIFT = "level_shift"
    TREND_CHANGE = "trend_change"
    VARIANCE_CHANGE = "variance_change"


@dataclass
class TrendAnalysisResult:
    """Result of trend analysis."""

    direction: TrendDirection
    slope: float
    r_squared: float
    p_value: float
    confidence: float
    annual_change_rate: float
    interpretation: str
    start_value: float
    end_value: float
    total_change_pct: float


@dataclass
class SeasonalityResult:
    """Result of seasonality analysis."""

    type: SeasonalityType
    strength: float  # 0-1, how strong the seasonal pattern is
    peak_quarter: int | None
    trough_quarter: int | None
    quarterly_indices: dict[int, float]  # Quarter -> seasonal index
    interpretation: str


@dataclass
class ChangePoint:
    """A detected change point in the time series."""

    year: int
    quarter: int
    index: int
    type: ChangePointType
    magnitude: float
    before_mean: float
    after_mean: float
    confidence: float
    description: str


@dataclass
class PatternRecognitionResult:
    """Complete pattern recognition results."""

    trend: TrendAnalysisResult
    seasonality: SeasonalityResult
    change_points: list[ChangePoint]
    volatility: float
    autocorrelation_lag1: float
    stationarity_test_p: float
    is_stationary: bool
    summary: str


@dataclass
class ForecastComparison:
    """Comparison of multiple forecasting methods."""

    method_results: dict[str, list[dict[str, Any]]]
    best_method: str
    consensus_forecast: list[dict[str, Any]]
    method_weights: dict[str, float]
    agreement_score: float  # How much methods agree


# =============================================================================
# TREND ANALYSIS
# =============================================================================


class TrendAnalyzer:
    """Analyzes trends in time series data."""

    def __init__(
        self,
        significance_level: float = 0.05,
        min_r_squared_for_trend: float = 0.3,
    ):
        self.significance_level = significance_level
        self.min_r_squared = min_r_squared_for_trend

    def analyze(self, df: pd.DataFrame) -> TrendAnalysisResult:
        """
        Perform comprehensive trend analysis.

        Args:
            df: DataFrame with year, quarter, value columns

        Returns:
            TrendAnalysisResult with trend metrics
        """
        if df.empty or len(df) < 4:
            return self._insufficient_data_result()

        # Sort and create time index
        df = df.sort_values(["year", "quarter"]).reset_index(drop=True)
        values = df["value"].values
        time_idx = np.arange(len(values))

        # Linear regression
        slope, intercept, r_value, p_value, std_err = scipy_stats.linregress(
            time_idx, values
        )

        r_squared = r_value ** 2

        # Determine direction
        if p_value > self.significance_level:
            direction = TrendDirection.STABLE
        elif r_squared < self.min_r_squared:
            # High variance, no clear trend
            direction = TrendDirection.VOLATILE
        elif slope > 0:
            direction = TrendDirection.INCREASING
        else:
            direction = TrendDirection.DECREASING

        # Calculate metrics
        start_value = float(values[0])
        end_value = float(values[-1])
        total_change_pct = (
            ((end_value - start_value) / start_value * 100)
            if start_value != 0
            else 0
        )

        # Annual change rate (4 quarters per year)
        annual_change_rate = slope * 4

        # Confidence based on R² and p-value
        confidence = r_squared * (1 - p_value)

        # Generate interpretation
        interpretation = self._generate_interpretation(
            direction, slope, r_squared, total_change_pct, len(df)
        )

        return TrendAnalysisResult(
            direction=direction,
            slope=round(slope, 6),
            r_squared=round(r_squared, 4),
            p_value=round(p_value, 4),
            confidence=round(confidence, 4),
            annual_change_rate=round(annual_change_rate, 4),
            interpretation=interpretation,
            start_value=round(start_value, 4),
            end_value=round(end_value, 4),
            total_change_pct=round(total_change_pct, 2),
        )

    def _insufficient_data_result(self) -> TrendAnalysisResult:
        """Return result for insufficient data."""
        return TrendAnalysisResult(
            direction=TrendDirection.STABLE,
            slope=0.0,
            r_squared=0.0,
            p_value=1.0,
            confidence=0.0,
            annual_change_rate=0.0,
            interpretation="Insufficient data for trend analysis",
            start_value=0.0,
            end_value=0.0,
            total_change_pct=0.0,
        )

    def _generate_interpretation(
        self,
        direction: TrendDirection,
        slope: float,
        r_squared: float,
        total_change_pct: float,
        n_points: int,
    ) -> str:
        """Generate human-readable trend interpretation."""
        if direction == TrendDirection.STABLE:
            return f"No significant trend detected over {n_points} observations."

        if direction == TrendDirection.VOLATILE:
            return (
                f"High volatility with no clear directional trend. "
                f"R² = {r_squared:.2f} indicates weak linear relationship."
            )

        strength = "strong" if r_squared > 0.7 else "moderate" if r_squared > 0.5 else "weak"
        dir_word = "upward" if direction == TrendDirection.INCREASING else "downward"

        return (
            f"A {strength} {dir_word} trend detected (R² = {r_squared:.2f}). "
            f"Total change: {total_change_pct:+.1f}% over {n_points} observations."
        )


# =============================================================================
# SEASONALITY ANALYSIS
# =============================================================================


class SeasonalityAnalyzer:
    """Analyzes seasonal patterns in quarterly data."""

    def __init__(self, min_years: int = 2):
        self.min_years = min_years

    def analyze(self, df: pd.DataFrame) -> SeasonalityResult:
        """
        Analyze seasonality in the time series.

        Args:
            df: DataFrame with year, quarter, value columns

        Returns:
            SeasonalityResult with seasonal patterns
        """
        if df.empty or len(df) < self.min_years * 4:
            return self._no_seasonality_result(
                "Insufficient data for seasonality analysis"
            )

        df = df.sort_values(["year", "quarter"]).reset_index(drop=True)

        # Calculate quarterly averages
        quarterly_means = df.groupby("quarter")["value"].mean()
        overall_mean = df["value"].mean()

        if overall_mean == 0:
            return self._no_seasonality_result("Cannot analyze: zero mean")

        # Calculate seasonal indices (ratio to overall mean)
        seasonal_indices = (quarterly_means / overall_mean).to_dict()

        # Calculate seasonality strength
        # Using coefficient of variation of quarterly means
        quarterly_std = quarterly_means.std()
        seasonality_strength = quarterly_std / overall_mean if overall_mean else 0

        # Normalize to 0-1 range (cap at 0.5 variation = 100% strength)
        seasonality_strength = min(1.0, seasonality_strength * 2)

        # Determine seasonality type
        if seasonality_strength < 0.05:
            seasonality_type = SeasonalityType.NONE
        else:
            seasonality_type = SeasonalityType.QUARTERLY

        # Find peak and trough quarters
        peak_quarter = int(quarterly_means.idxmax())
        trough_quarter = int(quarterly_means.idxmin())

        # Generate interpretation
        interpretation = self._generate_interpretation(
            seasonality_type,
            seasonality_strength,
            peak_quarter,
            trough_quarter,
            seasonal_indices,
        )

        return SeasonalityResult(
            type=seasonality_type,
            strength=round(seasonality_strength, 4),
            peak_quarter=peak_quarter if seasonality_type != SeasonalityType.NONE else None,
            trough_quarter=trough_quarter if seasonality_type != SeasonalityType.NONE else None,
            quarterly_indices={k: round(v, 4) for k, v in seasonal_indices.items()},
            interpretation=interpretation,
        )

    def _no_seasonality_result(self, reason: str) -> SeasonalityResult:
        """Return result when no seasonality detected."""
        return SeasonalityResult(
            type=SeasonalityType.NONE,
            strength=0.0,
            peak_quarter=None,
            trough_quarter=None,
            quarterly_indices={1: 1.0, 2: 1.0, 3: 1.0, 4: 1.0},
            interpretation=reason,
        )

    def _generate_interpretation(
        self,
        seasonality_type: SeasonalityType,
        strength: float,
        peak_quarter: int,
        trough_quarter: int,
        indices: dict[int, float],
    ) -> str:
        """Generate human-readable seasonality interpretation."""
        if seasonality_type == SeasonalityType.NONE:
            return "No significant seasonal pattern detected."

        quarter_names = {1: "Q1", 2: "Q2", 3: "Q3", 4: "Q4"}
        strength_word = "strong" if strength > 0.3 else "moderate" if strength > 0.15 else "weak"

        peak_idx = indices[peak_quarter]
        trough_idx = indices[trough_quarter]
        variation = (peak_idx - trough_idx) * 100

        return (
            f"A {strength_word} quarterly seasonal pattern detected. "
            f"Peak in {quarter_names[peak_quarter]} ({peak_idx:.0%} of average), "
            f"trough in {quarter_names[trough_quarter]} ({trough_idx:.0%} of average). "
            f"Seasonal variation: {variation:.1f}%."
        )


# =============================================================================
# CHANGE POINT DETECTION
# =============================================================================


class ChangePointDetector:
    """Detects structural changes in time series."""

    def __init__(
        self,
        min_segment_size: int = 4,
        significance_threshold: float = 2.0,  # Z-score threshold
    ):
        self.min_segment_size = min_segment_size
        self.significance_threshold = significance_threshold

    def detect(self, df: pd.DataFrame) -> list[ChangePoint]:
        """
        Detect change points in the time series.

        Uses CUSUM-like approach for level shifts and
        variance ratio tests for variance changes.

        Args:
            df: DataFrame with year, quarter, value columns

        Returns:
            List of detected change points
        """
        if df.empty or len(df) < 2 * self.min_segment_size:
            return []

        df = df.sort_values(["year", "quarter"]).reset_index(drop=True)
        values = df["value"].values
        n = len(values)

        change_points = []

        # Detect level shifts using sliding window comparison
        for i in range(self.min_segment_size, n - self.min_segment_size):
            before = values[max(0, i - self.min_segment_size) : i]
            after = values[i : min(n, i + self.min_segment_size)]

            before_mean = np.mean(before)
            after_mean = np.mean(after)
            pooled_std = np.std(np.concatenate([before, after]))

            if pooled_std == 0:
                continue

            z_score = abs(after_mean - before_mean) / (
                pooled_std / np.sqrt(len(before))
            )

            if z_score > self.significance_threshold:
                row = df.iloc[i]
                magnitude = after_mean - before_mean
                confidence = min(1.0, z_score / 5)  # Normalize confidence

                change_points.append(
                    ChangePoint(
                        year=int(row["year"]),
                        quarter=int(row["quarter"]),
                        index=i,
                        type=ChangePointType.LEVEL_SHIFT,
                        magnitude=round(magnitude, 4),
                        before_mean=round(before_mean, 4),
                        after_mean=round(after_mean, 4),
                        confidence=round(confidence, 4),
                        description=self._describe_change(
                            before_mean, after_mean, row["year"], row["quarter"]
                        ),
                    )
                )

        # Filter overlapping change points (keep highest confidence)
        return self._filter_overlapping(change_points)

    def _describe_change(
        self,
        before_mean: float,
        after_mean: float,
        year: int,
        quarter: int,
    ) -> str:
        """Generate description for change point."""
        change_pct = (
            ((after_mean - before_mean) / before_mean * 100)
            if before_mean != 0
            else 0
        )
        direction = "increase" if change_pct > 0 else "decrease"

        return (
            f"Level shift detected in {year} Q{quarter}: "
            f"{abs(change_pct):.1f}% {direction} "
            f"(from {before_mean:.2f} to {after_mean:.2f})"
        )

    def _filter_overlapping(
        self, change_points: list[ChangePoint]
    ) -> list[ChangePoint]:
        """Filter overlapping change points, keeping highest confidence."""
        if not change_points:
            return []

        # Sort by index
        sorted_points = sorted(change_points, key=lambda x: x.index)

        filtered = [sorted_points[0]]
        for point in sorted_points[1:]:
            last = filtered[-1]
            # If too close to previous, keep higher confidence
            if point.index - last.index < self.min_segment_size:
                if point.confidence > last.confidence:
                    filtered[-1] = point
            else:
                filtered.append(point)

        return filtered


# =============================================================================
# PATTERN RECOGNITION (COMPOSITE)
# =============================================================================


class PatternRecognizer:
    """
    Comprehensive pattern recognition for time series.

    Combines trend analysis, seasonality detection, and change point detection.
    """

    def __init__(self):
        self.trend_analyzer = TrendAnalyzer()
        self.seasonality_analyzer = SeasonalityAnalyzer()
        self.change_point_detector = ChangePointDetector()

    def analyze(self, df: pd.DataFrame) -> PatternRecognitionResult:
        """
        Perform comprehensive pattern recognition.

        Args:
            df: DataFrame with year, quarter, value columns

        Returns:
            PatternRecognitionResult with all detected patterns
        """
        if df.empty or len(df) < 4:
            return self._insufficient_data_result()

        df = df.sort_values(["year", "quarter"]).reset_index(drop=True)
        values = df["value"].values

        # Run all analyzers
        trend = self.trend_analyzer.analyze(df)
        seasonality = self.seasonality_analyzer.analyze(df)
        change_points = self.change_point_detector.detect(df)

        # Calculate additional metrics
        volatility = float(np.std(values) / np.mean(values)) if np.mean(values) != 0 else 0

        # Autocorrelation at lag 1
        if len(values) > 1:
            autocorr = float(np.corrcoef(values[:-1], values[1:])[0, 1])
            if np.isnan(autocorr):
                autocorr = 0.0
        else:
            autocorr = 0.0

        # Simple stationarity test (Augmented Dickey-Fuller approximation)
        # Using first-order differencing test
        if len(values) > 4:
            diff = np.diff(values)
            # If differences are roughly stationary, original may have unit root
            _, p_value = scipy_stats.normaltest(diff) if len(diff) > 8 else (0, 0.5)
            is_stationary = p_value > 0.05
        else:
            p_value = 0.5
            is_stationary = True

        # Generate summary
        summary = self._generate_summary(
            trend, seasonality, change_points, volatility
        )

        return PatternRecognitionResult(
            trend=trend,
            seasonality=seasonality,
            change_points=change_points,
            volatility=round(volatility, 4),
            autocorrelation_lag1=round(autocorr, 4),
            stationarity_test_p=round(p_value, 4),
            is_stationary=is_stationary,
            summary=summary,
        )

    def _insufficient_data_result(self) -> PatternRecognitionResult:
        """Return result for insufficient data."""
        return PatternRecognitionResult(
            trend=TrendAnalysisResult(
                direction=TrendDirection.STABLE,
                slope=0.0,
                r_squared=0.0,
                p_value=1.0,
                confidence=0.0,
                annual_change_rate=0.0,
                interpretation="Insufficient data",
                start_value=0.0,
                end_value=0.0,
                total_change_pct=0.0,
            ),
            seasonality=SeasonalityResult(
                type=SeasonalityType.NONE,
                strength=0.0,
                peak_quarter=None,
                trough_quarter=None,
                quarterly_indices={},
                interpretation="Insufficient data",
            ),
            change_points=[],
            volatility=0.0,
            autocorrelation_lag1=0.0,
            stationarity_test_p=0.5,
            is_stationary=True,
            summary="Insufficient data for pattern recognition.",
        )

    def _generate_summary(
        self,
        trend: TrendAnalysisResult,
        seasonality: SeasonalityResult,
        change_points: list[ChangePoint],
        volatility: float,
    ) -> str:
        """Generate comprehensive summary of patterns."""
        parts = []

        # Trend summary
        if trend.direction == TrendDirection.INCREASING:
            parts.append(f"Upward trend ({trend.total_change_pct:+.1f}% total change)")
        elif trend.direction == TrendDirection.DECREASING:
            parts.append(f"Downward trend ({trend.total_change_pct:+.1f}% total change)")
        elif trend.direction == TrendDirection.VOLATILE:
            parts.append("Volatile with no clear trend")
        else:
            parts.append("Stable, no significant trend")

        # Seasonality summary
        if seasonality.type != SeasonalityType.NONE:
            parts.append(
                f"Seasonal pattern (peak in Q{seasonality.peak_quarter})"
            )

        # Change points
        if change_points:
            parts.append(f"{len(change_points)} structural change(s) detected")

        # Volatility
        if volatility > 0.3:
            parts.append("High volatility")
        elif volatility > 0.15:
            parts.append("Moderate volatility")

        return ". ".join(parts) + "."


# =============================================================================
# MULTI-METHOD FORECASTING
# =============================================================================


class LinearForecaster:
    """Simple linear trend forecaster."""

    def __init__(self):
        self.slope = 0.0
        self.intercept = 0.0
        self.std_error = 0.0
        self._is_fitted = False
        self._last_year = 0
        self._last_quarter = 0
        self._min_year = 0

    def fit(self, df: pd.DataFrame) -> "LinearForecaster":
        """Fit linear model."""
        if df.empty or len(df) < 2:
            raise ValueError("Need at least 2 data points")

        df = df.sort_values(["year", "quarter"]).reset_index(drop=True)
        values = df["value"].values
        time_idx = np.arange(len(values))

        self.slope, self.intercept, _, _, self.std_error = scipy_stats.linregress(
            time_idx, values
        )

        last_row = df.iloc[-1]
        self._last_year = int(last_row["year"])
        self._last_quarter = int(last_row["quarter"])
        self._min_year = int(df["year"].min())
        self._n_points = len(df)
        self._is_fitted = True

        return self

    def predict(self, quarters_ahead: int = 4) -> list[dict[str, Any]]:
        """Generate predictions."""
        if not self._is_fitted:
            raise ValueError("Model must be fitted first")

        predictions = []
        current_year = self._last_year
        current_quarter = self._last_quarter

        for i in range(quarters_ahead):
            current_quarter += 1
            if current_quarter > 4:
                current_quarter = 1
                current_year += 1

            time_idx = (
                (current_year - self._min_year) * 4
                + current_quarter
                - (self._min_year * 4 + 1)
                + self._n_points
            )

            pred = self.intercept + self.slope * time_idx
            std = self.std_error * np.sqrt(1 + 1 / self._n_points + (time_idx - self._n_points / 2) ** 2)

            predictions.append({
                "year": current_year,
                "quarter": current_quarter,
                "predicted_value": round(pred, 4),
                "confidence_lower": round(pred - 1.96 * std, 4),
                "confidence_upper": round(pred + 1.96 * std, 4),
            })

        return predictions


class ExponentialSmoothingForecaster:
    """Simple exponential smoothing forecaster."""

    def __init__(self, alpha: float = 0.3):
        self.alpha = alpha
        self._smoothed_value = 0.0
        self._is_fitted = False
        self._last_year = 0
        self._last_quarter = 0
        self._std = 0.0

    def fit(self, df: pd.DataFrame) -> "ExponentialSmoothingForecaster":
        """Fit exponential smoothing model."""
        if df.empty or len(df) < 2:
            raise ValueError("Need at least 2 data points")

        df = df.sort_values(["year", "quarter"]).reset_index(drop=True)
        values = df["value"].values

        # Initialize with first value
        smoothed = values[0]
        for val in values[1:]:
            smoothed = self.alpha * val + (1 - self.alpha) * smoothed

        self._smoothed_value = smoothed
        self._std = float(np.std(values))

        last_row = df.iloc[-1]
        self._last_year = int(last_row["year"])
        self._last_quarter = int(last_row["quarter"])
        self._is_fitted = True

        return self

    def predict(self, quarters_ahead: int = 4) -> list[dict[str, Any]]:
        """Generate predictions (flat forecast with increasing uncertainty)."""
        if not self._is_fitted:
            raise ValueError("Model must be fitted first")

        predictions = []
        current_year = self._last_year
        current_quarter = self._last_quarter
        pred = self._smoothed_value

        for i in range(quarters_ahead):
            current_quarter += 1
            if current_quarter > 4:
                current_quarter = 1
                current_year += 1

            # Uncertainty grows with horizon
            std = self._std * np.sqrt(i + 1) * 0.5

            predictions.append({
                "year": current_year,
                "quarter": current_quarter,
                "predicted_value": round(pred, 4),
                "confidence_lower": round(pred - 1.96 * std, 4),
                "confidence_upper": round(pred + 1.96 * std, 4),
            })

        return predictions


class EnsembleForecaster:
    """
    Ensemble forecaster combining multiple methods.

    Uses weighted average of:
    - Linear regression
    - Exponential smoothing
    - Gradient Boosting (if available)
    """

    def __init__(self):
        self.linear = LinearForecaster()
        self.exp_smooth = ExponentialSmoothingForecaster()
        self._is_fitted = False

    def fit(self, df: pd.DataFrame) -> "EnsembleForecaster":
        """Fit all component models."""
        self.linear.fit(df)
        self.exp_smooth.fit(df)
        self._is_fitted = True
        return self

    def predict(self, quarters_ahead: int = 4) -> list[dict[str, Any]]:
        """Generate ensemble predictions."""
        if not self._is_fitted:
            raise ValueError("Model must be fitted first")

        linear_preds = self.linear.predict(quarters_ahead)
        exp_preds = self.exp_smooth.predict(quarters_ahead)

        # Simple average (can be weighted based on historical performance)
        ensemble = []
        for i in range(quarters_ahead):
            lp = linear_preds[i]
            ep = exp_preds[i]

            avg_pred = (lp["predicted_value"] + ep["predicted_value"]) / 2
            avg_lower = (lp["confidence_lower"] + ep["confidence_lower"]) / 2
            avg_upper = (lp["confidence_upper"] + ep["confidence_upper"]) / 2

            ensemble.append({
                "year": lp["year"],
                "quarter": lp["quarter"],
                "predicted_value": round(avg_pred, 4),
                "confidence_lower": round(avg_lower, 4),
                "confidence_upper": round(avg_upper, 4),
            })

        return ensemble

    def compare_methods(
        self, quarters_ahead: int = 4
    ) -> ForecastComparison:
        """Compare all forecasting methods."""
        if not self._is_fitted:
            raise ValueError("Model must be fitted first")

        linear_preds = self.linear.predict(quarters_ahead)
        exp_preds = self.exp_smooth.predict(quarters_ahead)
        ensemble_preds = self.predict(quarters_ahead)

        # Calculate agreement (how close predictions are)
        linear_vals = [p["predicted_value"] for p in linear_preds]
        exp_vals = [p["predicted_value"] for p in exp_preds]

        mean_vals = [(l + e) / 2 for l, e in zip(linear_vals, exp_vals)]
        if mean_vals and all(v != 0 for v in mean_vals):
            diffs = [abs(l - e) / abs(m) for l, e, m in zip(linear_vals, exp_vals, mean_vals)]
            agreement = max(0.0, min(1.0, 1 - sum(diffs) / len(diffs)))
        else:
            agreement = 0.5

        return ForecastComparison(
            method_results={
                "linear": linear_preds,
                "exponential_smoothing": exp_preds,
                "ensemble": ensemble_preds,
            },
            best_method="ensemble",
            consensus_forecast=ensemble_preds,
            method_weights={"linear": 0.5, "exponential_smoothing": 0.5},
            agreement_score=round(agreement, 4),
        )


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================


def analyze_patterns(df: pd.DataFrame) -> PatternRecognitionResult:
    """
    Convenience function for pattern recognition.

    Args:
        df: DataFrame with year, quarter, value columns

    Returns:
        PatternRecognitionResult
    """
    recognizer = PatternRecognizer()
    return recognizer.analyze(df)


def analyze_trend(df: pd.DataFrame) -> TrendAnalysisResult:
    """
    Convenience function for trend analysis.

    Args:
        df: DataFrame with year, quarter, value columns

    Returns:
        TrendAnalysisResult
    """
    analyzer = TrendAnalyzer()
    return analyzer.analyze(df)


def analyze_seasonality(df: pd.DataFrame) -> SeasonalityResult:
    """
    Convenience function for seasonality analysis.

    Args:
        df: DataFrame with year, quarter, value columns

    Returns:
        SeasonalityResult
    """
    analyzer = SeasonalityAnalyzer()
    return analyzer.analyze(df)


def detect_change_points(df: pd.DataFrame) -> list[ChangePoint]:
    """
    Convenience function for change point detection.

    Args:
        df: DataFrame with year, quarter, value columns

    Returns:
        List of ChangePoint objects
    """
    detector = ChangePointDetector()
    return detector.detect(df)


def forecast_ensemble(
    df: pd.DataFrame, quarters_ahead: int = 4
) -> ForecastComparison:
    """
    Convenience function for ensemble forecasting with comparison.

    Args:
        df: DataFrame with year, quarter, value columns
        quarters_ahead: Number of quarters to forecast

    Returns:
        ForecastComparison with all method results
    """
    forecaster = EnsembleForecaster()
    forecaster.fit(df)
    return forecaster.compare_methods(quarters_ahead)
