"""
Tests for Insight Engine and Alert System
Phase 8: Insight Engine

Comprehensive tests covering:
- Insight generation from trends, anomalies, seasonality
- Insight prioritization and ranking
- Alert rules and thresholds
- Alert management and notifications
- Integration with pattern recognition
"""

import numpy as np
import pandas as pd
import pytest

# Import modules under test
from analytics_hub_platform.domain.insight_engine import (
    InsightType,
    InsightPriority,
    InsightCategory,
    Insight,
    InsightReport,
    TrendInsightGenerator,
    AnomalyInsightGenerator,
    SeasonalityInsightGenerator,
    ChangePointInsightGenerator,
    TargetGapInsightGenerator,
    MilestoneInsightGenerator,
    InsightEngine,
    generate_kpi_insights,
    generate_insight_report,
)
from analytics_hub_platform.domain.alert_system import (
    AlertSeverity,
    AlertStatus,
    ThresholdOperator,
    AlertChannel,
    AlertRule,
    Alert,
    ThresholdEvaluator,
    AlertManager,
    create_default_rules,
    add_alert_rule,
    check_alerts,
    get_active_alerts,
)
from analytics_hub_platform.domain.advanced_analytics import (
    TrendDirection,
    SeasonalityType,
    PatternRecognitionResult,
    TrendAnalysisResult,
    SeasonalityResult,
    ChangePoint,
    ChangePointType,
)
from analytics_hub_platform.domain.ml_services import (
    AnomalySeverity,
    AnomalyResult,
)


# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def upward_trend_data():
    """Data with clear upward trend."""
    data = []
    for year in range(2020, 2025):
        for quarter in range(1, 5):
            base_value = (year - 2020) * 40 + quarter * 2 + 100
            noise = np.random.normal(0, 2)
            data.append({
                "year": year,
                "quarter": quarter,
                "value": base_value + noise,
            })
    return pd.DataFrame(data)


@pytest.fixture
def seasonal_data():
    """Data with clear quarterly seasonality."""
    data = []
    seasonal_pattern = {1: 0.8, 2: 1.0, 3: 1.3, 4: 0.9}
    for year in range(2020, 2025):
        for quarter in range(1, 5):
            base_value = 100 * seasonal_pattern[quarter]
            noise = np.random.normal(0, 2)
            data.append({
                "year": year,
                "quarter": quarter,
                "value": base_value + noise,
            })
    return pd.DataFrame(data)


@pytest.fixture
def change_point_data():
    """Data with a clear level shift."""
    data = []
    for year in range(2020, 2025):
        for quarter in range(1, 5):
            if year < 2022 or (year == 2022 and quarter < 3):
                base_value = 100
            else:
                base_value = 150
            noise = np.random.normal(0, 2)
            data.append({
                "year": year,
                "quarter": quarter,
                "value": base_value + noise,
            })
    return pd.DataFrame(data)


@pytest.fixture
def pattern_result_increasing():
    """Mock pattern recognition result with increasing trend."""
    return PatternRecognitionResult(
        trend=TrendAnalysisResult(
            direction=TrendDirection.INCREASING,
            slope=2.5,
            r_squared=0.85,
            p_value=0.001,
            confidence=0.8,
            annual_change_rate=10.0,
            interpretation="Strong upward trend",
            start_value=100.0,
            end_value=150.0,
            total_change_pct=50.0,
        ),
        seasonality=SeasonalityResult(
            type=SeasonalityType.NONE,
            strength=0.0,
            peak_quarter=None,
            trough_quarter=None,
            quarterly_indices={1: 1.0, 2: 1.0, 3: 1.0, 4: 1.0},
            interpretation="No seasonality",
        ),
        change_points=[],
        volatility=0.1,
        autocorrelation_lag1=0.5,
        stationarity_test_p=0.1,
        is_stationary=False,
        summary="Upward trend",
    )


@pytest.fixture
def pattern_result_seasonal():
    """Mock pattern recognition result with seasonality."""
    return PatternRecognitionResult(
        trend=TrendAnalysisResult(
            direction=TrendDirection.STABLE,
            slope=0.1,
            r_squared=0.1,
            p_value=0.5,
            confidence=0.1,
            annual_change_rate=0.4,
            interpretation="Stable",
            start_value=100.0,
            end_value=100.0,
            total_change_pct=0.0,
        ),
        seasonality=SeasonalityResult(
            type=SeasonalityType.QUARTERLY,
            strength=0.35,
            peak_quarter=3,
            trough_quarter=1,
            quarterly_indices={1: 0.8, 2: 1.0, 3: 1.3, 4: 0.9},
            interpretation="Strong quarterly pattern",
        ),
        change_points=[],
        volatility=0.15,
        autocorrelation_lag1=0.3,
        stationarity_test_p=0.6,
        is_stationary=True,
        summary="Seasonal pattern",
    )


@pytest.fixture
def pattern_result_with_change_point():
    """Mock pattern recognition result with change point."""
    return PatternRecognitionResult(
        trend=TrendAnalysisResult(
            direction=TrendDirection.INCREASING,
            slope=1.5,
            r_squared=0.7,
            p_value=0.01,
            confidence=0.6,
            annual_change_rate=6.0,
            interpretation="Upward trend with change point",
            start_value=100.0,
            end_value=150.0,
            total_change_pct=50.0,
        ),
        seasonality=SeasonalityResult(
            type=SeasonalityType.NONE,
            strength=0.0,
            peak_quarter=None,
            trough_quarter=None,
            quarterly_indices={1: 1.0, 2: 1.0, 3: 1.0, 4: 1.0},
            interpretation="No seasonality",
        ),
        change_points=[
            ChangePoint(
                year=2022,
                quarter=3,
                index=10,
                type=ChangePointType.LEVEL_SHIFT,
                magnitude=50.0,
                before_mean=100.0,
                after_mean=150.0,
                confidence=0.85,
                description="Level shift in 2022 Q3: 50% increase",
            )
        ],
        volatility=0.2,
        autocorrelation_lag1=0.4,
        stationarity_test_p=0.2,
        is_stationary=False,
        summary="Change point detected",
    )


@pytest.fixture
def sample_anomalies():
    """Sample anomaly results."""
    return [
        AnomalyResult(
            kpi_id="test_kpi",
            region_id="region_1",
            year=2024,
            quarter=2,
            actual_value=200.0,
            expected_value=100.0,
            deviation=100.0,
            z_score=4.5,
            severity=AnomalySeverity.CRITICAL,
            direction="high",
            description="Critical anomaly detected",
        ),
        AnomalyResult(
            kpi_id="test_kpi",
            region_id="region_1",
            year=2024,
            quarter=3,
            actual_value=80.0,
            expected_value=100.0,
            deviation=-20.0,
            z_score=-2.5,
            severity=AnomalySeverity.WARNING,
            direction="low",
            description="Warning anomaly detected",
        ),
    ]


# =============================================================================
# TREND INSIGHT GENERATOR TESTS
# =============================================================================


class TestTrendInsightGenerator:
    """Tests for TrendInsightGenerator."""

    def test_generate_upward_trend_insight(self, pattern_result_increasing):
        """Test insight generation for upward trend."""
        generator = TrendInsightGenerator()
        insights = generator.generate(
            kpi_id="test_kpi",
            kpi_name="Test KPI",
            category=InsightCategory.ECONOMIC,
            pattern_result=pattern_result_increasing,
        )

        assert len(insights) == 1
        insight = insights[0]
        assert insight.type == InsightType.TREND
        assert "upward" in insight.title.lower() or "Strong" in insight.title
        assert insight.metric_change == 50.0
        assert insight.confidence > 0

    def test_no_insight_for_stable_trend(self, pattern_result_seasonal):
        """Test no insight for stable trend."""
        generator = TrendInsightGenerator()
        insights = generator.generate(
            kpi_id="test_kpi",
            kpi_name="Test KPI",
            category=InsightCategory.ECONOMIC,
            pattern_result=pattern_result_seasonal,
        )

        assert len(insights) == 0

    def test_priority_based_on_magnitude(self, pattern_result_increasing):
        """Test priority is based on change magnitude."""
        generator = TrendInsightGenerator()
        insights = generator.generate(
            kpi_id="test_kpi",
            kpi_name="Test KPI",
            category=InsightCategory.ECONOMIC,
            pattern_result=pattern_result_increasing,
        )

        assert len(insights) == 1
        # 50% change with high confidence should be high priority
        assert insights[0].priority == InsightPriority.HIGH


# =============================================================================
# ANOMALY INSIGHT GENERATOR TESTS
# =============================================================================


class TestAnomalyInsightGenerator:
    """Tests for AnomalyInsightGenerator."""

    def test_generate_anomaly_insights(self, sample_anomalies):
        """Test insight generation from anomalies."""
        generator = AnomalyInsightGenerator()
        insights = generator.generate(
            kpi_id="test_kpi",
            kpi_name="Test KPI",
            category=InsightCategory.ECONOMIC,
            anomalies=sample_anomalies,
        )

        assert len(insights) == 2

    def test_critical_anomaly_priority(self, sample_anomalies):
        """Test critical anomaly gets critical priority."""
        generator = AnomalyInsightGenerator()
        insights = generator.generate(
            kpi_id="test_kpi",
            kpi_name="Test KPI",
            category=InsightCategory.ECONOMIC,
            anomalies=sample_anomalies,
        )

        critical_insights = [i for i in insights if i.priority == InsightPriority.CRITICAL]
        assert len(critical_insights) == 1
        assert "2024 Q2" in critical_insights[0].title

    def test_anomaly_insight_contains_details(self, sample_anomalies):
        """Test anomaly insight contains value details."""
        generator = AnomalyInsightGenerator()
        insights = generator.generate(
            kpi_id="test_kpi",
            kpi_name="Test KPI",
            category=InsightCategory.ECONOMIC,
            anomalies=sample_anomalies,
        )

        insight = insights[0]
        assert insight.metric_value == 200.0
        assert "200" in insight.description
        assert "100" in insight.description


# =============================================================================
# SEASONALITY INSIGHT GENERATOR TESTS
# =============================================================================


class TestSeasonalityInsightGenerator:
    """Tests for SeasonalityInsightGenerator."""

    def test_generate_seasonality_insight(self, pattern_result_seasonal):
        """Test insight generation for seasonal pattern."""
        generator = SeasonalityInsightGenerator()
        insights = generator.generate(
            kpi_id="test_kpi",
            kpi_name="Test KPI",
            category=InsightCategory.ECONOMIC,
            pattern_result=pattern_result_seasonal,
        )

        assert len(insights) == 1
        insight = insights[0]
        assert insight.type == InsightType.SEASONALITY
        assert "Q3" in insight.description  # Peak quarter
        assert "Q1" in insight.description  # Trough quarter

    def test_no_insight_without_seasonality(self, pattern_result_increasing):
        """Test no insight when no seasonality."""
        generator = SeasonalityInsightGenerator()
        insights = generator.generate(
            kpi_id="test_kpi",
            kpi_name="Test KPI",
            category=InsightCategory.ECONOMIC,
            pattern_result=pattern_result_increasing,
        )

        assert len(insights) == 0


# =============================================================================
# CHANGE POINT INSIGHT GENERATOR TESTS
# =============================================================================


class TestChangePointInsightGenerator:
    """Tests for ChangePointInsightGenerator."""

    def test_generate_change_point_insight(self, pattern_result_with_change_point):
        """Test insight generation for change point."""
        generator = ChangePointInsightGenerator()
        insights = generator.generate(
            kpi_id="test_kpi",
            kpi_name="Test KPI",
            category=InsightCategory.ECONOMIC,
            pattern_result=pattern_result_with_change_point,
        )

        assert len(insights) == 1
        insight = insights[0]
        assert insight.type == InsightType.CHANGE_POINT
        assert "2022" in insight.title
        assert insight.confidence == 0.85


# =============================================================================
# TARGET GAP INSIGHT GENERATOR TESTS
# =============================================================================


class TestTargetGapInsightGenerator:
    """Tests for TargetGapInsightGenerator."""

    def test_below_target_insight(self):
        """Test insight when below target."""
        generator = TargetGapInsightGenerator()
        insights = generator.generate(
            kpi_id="test_kpi",
            kpi_name="Test KPI",
            category=InsightCategory.ECONOMIC,
            current_value=80.0,
            target_value=100.0,
            higher_is_better=True,
        )

        assert len(insights) == 1
        insight = insights[0]
        assert insight.type == InsightType.TARGET_GAP
        assert "below" in insight.title.lower()
        assert insight.priority == InsightPriority.HIGH

    def test_exceeding_target_insight(self):
        """Test insight when exceeding target."""
        generator = TargetGapInsightGenerator()
        insights = generator.generate(
            kpi_id="test_kpi",
            kpi_name="Test KPI",
            category=InsightCategory.ECONOMIC,
            current_value=120.0,
            target_value=100.0,
            higher_is_better=True,
        )

        assert len(insights) == 1
        insight = insights[0]
        assert "exceeding" in insight.title.lower()
        assert insight.priority == InsightPriority.LOW

    def test_critical_priority_for_large_gap(self):
        """Test critical priority for large gap."""
        generator = TargetGapInsightGenerator()
        insights = generator.generate(
            kpi_id="test_kpi",
            kpi_name="Test KPI",
            category=InsightCategory.ECONOMIC,
            current_value=70.0,
            target_value=100.0,
            higher_is_better=True,
        )

        assert len(insights) == 1
        assert insights[0].priority == InsightPriority.CRITICAL


# =============================================================================
# MILESTONE INSIGHT GENERATOR TESTS
# =============================================================================


class TestMilestoneInsightGenerator:
    """Tests for MilestoneInsightGenerator."""

    def test_milestone_crossed(self):
        """Test insight when milestone is crossed."""
        generator = MilestoneInsightGenerator(milestones=[100, 500, 1000])
        insights = generator.generate(
            kpi_id="test_kpi",
            kpi_name="Test KPI",
            category=InsightCategory.ECONOMIC,
            current_value=105.0,
            previous_value=95.0,
        )

        assert len(insights) == 1
        assert "100" in insights[0].title
        assert insights[0].type == InsightType.MILESTONE

    def test_no_milestone_insight(self):
        """Test no insight when no milestone crossed."""
        generator = MilestoneInsightGenerator(milestones=[100, 500, 1000])
        insights = generator.generate(
            kpi_id="test_kpi",
            kpi_name="Test KPI",
            category=InsightCategory.ECONOMIC,
            current_value=150.0,
            previous_value=140.0,
        )

        assert len(insights) == 0


# =============================================================================
# INSIGHT ENGINE TESTS
# =============================================================================


class TestInsightEngine:
    """Tests for InsightEngine."""

    def test_generate_insights_from_data(self, upward_trend_data):
        """Test insight generation from raw data."""
        engine = InsightEngine()
        insights = engine.generate_insights(
            kpi_id="test_kpi",
            kpi_name="Test KPI",
            category="economic",
            data=upward_trend_data,
            target_value=150.0,
        )

        assert len(insights) > 0
        assert all(isinstance(i, Insight) for i in insights)

    def test_empty_data_returns_no_insights(self):
        """Test empty data returns no insights."""
        engine = InsightEngine()
        insights = engine.generate_insights(
            kpi_id="test_kpi",
            kpi_name="Test KPI",
            category="economic",
            data=pd.DataFrame(),
        )

        assert len(insights) == 0

    def test_generate_report(self, upward_trend_data, seasonal_data):
        """Test full report generation."""
        engine = InsightEngine()
        kpis = [
            {
                "id": "kpi_1",
                "name": "Economic Growth",
                "category": "economic",
                "data": upward_trend_data,
                "target": 150.0,
            },
            {
                "id": "kpi_2",
                "name": "Seasonal Metric",
                "category": "environmental",
                "data": seasonal_data,
            },
        ]

        report = engine.generate_report(kpis, period="Q4 2024")

        assert isinstance(report, InsightReport)
        assert report.period == "Q4 2024"
        assert report.total_count > 0
        assert len(report.insights) == report.total_count
        assert sum(report.by_priority.values()) == report.total_count

    def test_insights_sorted_by_priority(self, upward_trend_data):
        """Test insights are sorted by priority."""
        engine = InsightEngine()
        kpis = [
            {
                "id": "kpi_1",
                "name": "Test KPI",
                "category": "economic",
                "data": upward_trend_data,
                "target": 50.0,  # Far below current to trigger critical
            },
        ]

        report = engine.generate_report(kpis)

        # Check priority order
        priorities = [i.priority for i in report.insights]
        priority_order = {
            InsightPriority.CRITICAL: 0,
            InsightPriority.HIGH: 1,
            InsightPriority.MEDIUM: 2,
            InsightPriority.LOW: 3,
            InsightPriority.INFO: 4,
        }
        priority_values = [priority_order[p] for p in priorities]
        assert priority_values == sorted(priority_values)


class TestInsightConvenienceFunctions:
    """Tests for convenience functions."""

    def test_generate_kpi_insights(self, upward_trend_data):
        """Test generate_kpi_insights function."""
        insights = generate_kpi_insights(
            kpi_id="test_kpi",
            kpi_name="Test KPI",
            category="economic",
            data=upward_trend_data,
        )

        assert isinstance(insights, list)
        assert all(isinstance(i, dict) for i in insights)
        if insights:
            assert "id" in insights[0]
            assert "type" in insights[0]
            assert "priority" in insights[0]

    def test_generate_insight_report(self, upward_trend_data):
        """Test generate_insight_report function."""
        kpis = [
            {
                "id": "kpi_1",
                "name": "Test KPI",
                "category": "economic",
                "data": upward_trend_data,
            },
        ]

        report = generate_insight_report(kpis, period="Q4 2024")

        assert isinstance(report, dict)
        assert "insights" in report
        assert "summary" in report
        assert report["period"] == "Q4 2024"


# =============================================================================
# THRESHOLD EVALUATOR TESTS
# =============================================================================


class TestThresholdEvaluator:
    """Tests for ThresholdEvaluator."""

    def test_greater_than(self):
        """Test greater than operator."""
        assert ThresholdEvaluator.evaluate(10, ThresholdOperator.GREATER_THAN, 5) is True
        assert ThresholdEvaluator.evaluate(5, ThresholdOperator.GREATER_THAN, 5) is False
        assert ThresholdEvaluator.evaluate(3, ThresholdOperator.GREATER_THAN, 5) is False

    def test_greater_than_or_equal(self):
        """Test greater than or equal operator."""
        assert ThresholdEvaluator.evaluate(10, ThresholdOperator.GREATER_THAN_OR_EQUAL, 5) is True
        assert ThresholdEvaluator.evaluate(5, ThresholdOperator.GREATER_THAN_OR_EQUAL, 5) is True
        assert ThresholdEvaluator.evaluate(3, ThresholdOperator.GREATER_THAN_OR_EQUAL, 5) is False

    def test_less_than(self):
        """Test less than operator."""
        assert ThresholdEvaluator.evaluate(3, ThresholdOperator.LESS_THAN, 5) is True
        assert ThresholdEvaluator.evaluate(5, ThresholdOperator.LESS_THAN, 5) is False
        assert ThresholdEvaluator.evaluate(10, ThresholdOperator.LESS_THAN, 5) is False

    def test_between(self):
        """Test between operator."""
        assert ThresholdEvaluator.evaluate(7, ThresholdOperator.BETWEEN, 5, 10) is True
        assert ThresholdEvaluator.evaluate(5, ThresholdOperator.BETWEEN, 5, 10) is True
        assert ThresholdEvaluator.evaluate(3, ThresholdOperator.BETWEEN, 5, 10) is False

    def test_outside(self):
        """Test outside operator."""
        assert ThresholdEvaluator.evaluate(3, ThresholdOperator.OUTSIDE, 5, 10) is True
        assert ThresholdEvaluator.evaluate(12, ThresholdOperator.OUTSIDE, 5, 10) is True
        assert ThresholdEvaluator.evaluate(7, ThresholdOperator.OUTSIDE, 5, 10) is False


# =============================================================================
# ALERT RULE TESTS
# =============================================================================


class TestAlertRule:
    """Tests for AlertRule."""

    def test_rule_creation(self):
        """Test alert rule creation."""
        rule = AlertRule(
            id="test_rule",
            name="Test Rule",
            kpi_id="test_kpi",
            operator=ThresholdOperator.GREATER_THAN,
            threshold=100.0,
            severity=AlertSeverity.WARNING,
        )

        assert rule.id == "test_rule"
        assert rule.enabled is True
        assert rule.cooldown_minutes == 60

    def test_rule_to_dict(self):
        """Test rule serialization."""
        rule = AlertRule(
            id="test_rule",
            name="Test Rule",
            kpi_id="test_kpi",
            operator=ThresholdOperator.GREATER_THAN,
            threshold=100.0,
        )

        result = rule.to_dict()
        assert result["id"] == "test_rule"
        assert result["operator"] == "gt"


# =============================================================================
# ALERT MANAGER TESTS
# =============================================================================


class TestAlertManager:
    """Tests for AlertManager."""

    def test_add_and_get_rule(self):
        """Test adding and retrieving rules."""
        manager = AlertManager()
        rule = AlertRule(
            id="test_rule",
            name="Test Rule",
            kpi_id="test_kpi",
            operator=ThresholdOperator.GREATER_THAN,
            threshold=100.0,
        )

        manager.add_rule(rule)
        retrieved = manager.get_rule("test_rule")

        assert retrieved is not None
        assert retrieved.id == "test_rule"

    def test_remove_rule(self):
        """Test removing a rule."""
        manager = AlertManager()
        rule = AlertRule(
            id="test_rule",
            name="Test Rule",
            kpi_id="test_kpi",
            operator=ThresholdOperator.GREATER_THAN,
            threshold=100.0,
        )

        manager.add_rule(rule)
        assert manager.remove_rule("test_rule") is True
        assert manager.get_rule("test_rule") is None

    def test_evaluate_triggers_alert(self):
        """Test evaluation triggers alert."""
        manager = AlertManager()
        rule = AlertRule(
            id="test_rule",
            name="Test Rule",
            kpi_id="test_kpi",
            operator=ThresholdOperator.GREATER_THAN,
            threshold=100.0,
            severity=AlertSeverity.WARNING,
        )

        manager.add_rule(rule)
        alerts = manager.evaluate("test_kpi", 150.0)

        assert len(alerts) == 1
        assert alerts[0].severity == AlertSeverity.WARNING
        assert alerts[0].current_value == 150.0

    def test_evaluate_no_alert_below_threshold(self):
        """Test no alert when below threshold."""
        manager = AlertManager()
        rule = AlertRule(
            id="test_rule",
            name="Test Rule",
            kpi_id="test_kpi",
            operator=ThresholdOperator.GREATER_THAN,
            threshold=100.0,
        )

        manager.add_rule(rule)
        alerts = manager.evaluate("test_kpi", 50.0)

        assert len(alerts) == 0

    def test_cooldown_prevents_repeated_alerts(self):
        """Test cooldown prevents repeated alerts."""
        manager = AlertManager()
        rule = AlertRule(
            id="test_rule",
            name="Test Rule",
            kpi_id="test_kpi",
            operator=ThresholdOperator.GREATER_THAN,
            threshold=100.0,
            cooldown_minutes=60,
        )

        manager.add_rule(rule)

        # First evaluation triggers
        alerts1 = manager.evaluate("test_kpi", 150.0)
        assert len(alerts1) == 1

        # Second evaluation within cooldown doesn't trigger
        alerts2 = manager.evaluate("test_kpi", 160.0)
        assert len(alerts2) == 0

    def test_acknowledge_alert(self):
        """Test acknowledging an alert."""
        manager = AlertManager()
        rule = AlertRule(
            id="test_rule",
            name="Test Rule",
            kpi_id="test_kpi",
            operator=ThresholdOperator.GREATER_THAN,
            threshold=100.0,
        )

        manager.add_rule(rule)
        alerts = manager.evaluate("test_kpi", 150.0)

        assert manager.acknowledge(alerts[0].id, "test_user") is True
        assert alerts[0].status == AlertStatus.ACKNOWLEDGED
        assert alerts[0].acknowledged_by == "test_user"

    def test_resolve_alert(self):
        """Test resolving an alert."""
        manager = AlertManager()
        rule = AlertRule(
            id="test_rule",
            name="Test Rule",
            kpi_id="test_kpi",
            operator=ThresholdOperator.GREATER_THAN,
            threshold=100.0,
        )

        manager.add_rule(rule)
        alerts = manager.evaluate("test_kpi", 150.0)

        assert manager.resolve(alerts[0].id) is True
        assert alerts[0].status == AlertStatus.RESOLVED

    def test_get_active_alerts(self):
        """Test getting active alerts."""
        manager = AlertManager()
        rule = AlertRule(
            id="test_rule",
            name="Test Rule",
            kpi_id="test_kpi",
            operator=ThresholdOperator.GREATER_THAN,
            threshold=100.0,
        )

        manager.add_rule(rule)
        manager.evaluate("test_kpi", 150.0)

        active = manager.get_active_alerts()
        assert len(active) == 1

        # Resolve and check again
        manager.resolve(active[0].id)
        active = manager.get_active_alerts()
        assert len(active) == 0

    def test_evaluate_dataframe(self, upward_trend_data):
        """Test evaluation from DataFrame."""
        manager = AlertManager()
        rule = AlertRule(
            id="test_rule",
            name="High Value Alert",
            kpi_id="test_kpi",
            operator=ThresholdOperator.GREATER_THAN,
            threshold=200.0,
        )

        manager.add_rule(rule)
        alerts = manager.evaluate_dataframe("test_kpi", upward_trend_data)

        # Latest value should exceed 200
        assert len(alerts) == 1

    def test_notification_handler(self):
        """Test custom notification handler."""
        manager = AlertManager()
        notifications = []

        def handler(alert: Alert):
            notifications.append(alert)

        manager.register_handler(AlertChannel.IN_APP, handler)

        rule = AlertRule(
            id="test_rule",
            name="Test Rule",
            kpi_id="test_kpi",
            operator=ThresholdOperator.GREATER_THAN,
            threshold=100.0,
            channels=[AlertChannel.IN_APP],
        )

        manager.add_rule(rule)
        manager.evaluate("test_kpi", 150.0)

        assert len(notifications) == 1


# =============================================================================
# DEFAULT RULES TESTS
# =============================================================================


class TestDefaultRules:
    """Tests for default alert rules."""

    def test_default_rules_created(self):
        """Test default rules are created."""
        rules = create_default_rules()
        assert len(rules) >= 4

        rule_ids = [r.id for r in rules]
        assert "gdp_growth_low" in rule_ids
        assert "unemployment_high" in rule_ids


# =============================================================================
# CONVENIENCE FUNCTION TESTS
# =============================================================================


class TestAlertConvenienceFunctions:
    """Tests for alert convenience functions."""

    def test_add_alert_rule(self):
        """Test add_alert_rule function."""
        # Reset manager
        import analytics_hub_platform.domain.alert_system as alert_module
        alert_module._alert_manager = None

        result = add_alert_rule(
            rule_id="custom_rule",
            name="Custom Rule",
            kpi_id="custom_kpi",
            operator="gt",
            threshold=50.0,
        )

        assert result["id"] == "custom_rule"
        assert result["threshold"] == 50.0

    def test_check_alerts(self):
        """Test check_alerts function."""
        # Reset manager
        import analytics_hub_platform.domain.alert_system as alert_module
        alert_module._alert_manager = None

        add_alert_rule(
            rule_id="test_check",
            name="Test Check",
            kpi_id="check_kpi",
            operator="gt",
            threshold=100.0,
        )

        alerts = check_alerts("check_kpi", 150.0)
        assert len(alerts) == 1

    def test_get_active_alerts_function(self):
        """Test get_active_alerts function."""
        # Reset manager
        import analytics_hub_platform.domain.alert_system as alert_module
        alert_module._alert_manager = None

        add_alert_rule(
            rule_id="test_active",
            name="Test Active",
            kpi_id="active_kpi",
            operator="gt",
            threshold=100.0,
        )

        check_alerts("active_kpi", 150.0)
        active = get_active_alerts("active_kpi")

        assert len(active) == 1


# =============================================================================
# INTEGRATION TESTS
# =============================================================================


class TestInsightAlertIntegration:
    """Integration tests for insight engine and alert system."""

    def test_insights_can_trigger_alerts(self, upward_trend_data):
        """Test insights can be used to trigger alerts."""
        # Generate insights
        engine = InsightEngine()
        insights = engine.generate_insights(
            kpi_id="test_kpi",
            kpi_name="Test KPI",
            category="economic",
            data=upward_trend_data,
        )

        # Set up alert manager
        manager = AlertManager()
        rule = AlertRule(
            id="insight_based",
            name="Insight-based Alert",
            kpi_id="test_kpi",
            operator=ThresholdOperator.GREATER_THAN,
            threshold=200.0,
        )
        manager.add_rule(rule)

        # Use latest value from data
        latest_value = float(upward_trend_data.iloc[-1]["value"])
        alerts = manager.evaluate("test_kpi", latest_value)

        # Both insights and alerts should work together
        assert len(insights) > 0
        assert isinstance(alerts, list)

    def test_full_monitoring_pipeline(self, upward_trend_data):
        """Test complete monitoring pipeline."""
        # 1. Generate insights
        report = generate_insight_report(
            kpis=[
                {
                    "id": "monitored_kpi",
                    "name": "Monitored KPI",
                    "category": "economic",
                    "data": upward_trend_data,
                    "target": 150.0,
                }
            ],
            period="Q4 2024",
        )

        assert report["total_count"] > 0

        # 2. Set up alerts
        import analytics_hub_platform.domain.alert_system as alert_module
        alert_module._alert_manager = None  # Reset

        add_alert_rule(
            rule_id="monitor_rule",
            name="Monitor Rule",
            kpi_id="monitored_kpi",
            operator="gt",
            threshold=200.0,
        )

        # 3. Check current value against alerts
        latest = float(upward_trend_data.iloc[-1]["value"])
        alerts = check_alerts("monitored_kpi", latest)

        # 4. Verify integration works
        assert isinstance(report, dict)
        assert isinstance(alerts, list)
