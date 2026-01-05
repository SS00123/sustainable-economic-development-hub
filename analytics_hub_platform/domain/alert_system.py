"""
Alert System Module
Sustainable Economic Development Analytics Hub

Provides threshold-based alerting and notification system:
- Configurable alert rules
- Multi-level severity
- Alert history tracking
- Notification templates
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable

import pandas as pd

logger = logging.getLogger(__name__)


# =============================================================================
# ENUMS AND MODELS
# =============================================================================


class AlertSeverity(str, Enum):
    """Severity level for alerts."""

    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"


class AlertStatus(str, Enum):
    """Status of an alert."""

    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    EXPIRED = "expired"


class ThresholdOperator(str, Enum):
    """Comparison operator for thresholds."""

    GREATER_THAN = "gt"
    GREATER_THAN_OR_EQUAL = "gte"
    LESS_THAN = "lt"
    LESS_THAN_OR_EQUAL = "lte"
    EQUAL = "eq"
    NOT_EQUAL = "neq"
    BETWEEN = "between"
    OUTSIDE = "outside"


class AlertChannel(str, Enum):
    """Notification channel for alerts."""

    EMAIL = "email"
    SMS = "sms"
    WEBHOOK = "webhook"
    IN_APP = "in_app"
    LOG = "log"


@dataclass
class AlertRule:
    """Configuration for an alert rule."""

    id: str
    name: str
    kpi_id: str
    operator: ThresholdOperator
    threshold: float
    threshold_upper: float | None = None  # For BETWEEN/OUTSIDE
    severity: AlertSeverity = AlertSeverity.WARNING
    enabled: bool = True
    cooldown_minutes: int = 60  # Minimum time between repeated alerts
    channels: list[AlertChannel] = field(default_factory=lambda: [AlertChannel.IN_APP])
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "kpi_id": self.kpi_id,
            "operator": self.operator.value,
            "threshold": self.threshold,
            "threshold_upper": self.threshold_upper,
            "severity": self.severity.value,
            "enabled": self.enabled,
            "cooldown_minutes": self.cooldown_minutes,
            "channels": [c.value for c in self.channels],
            "metadata": self.metadata,
        }


@dataclass
class Alert:
    """An alert instance triggered by a rule."""

    id: str
    rule_id: str
    rule_name: str
    kpi_id: str
    severity: AlertSeverity
    status: AlertStatus
    title: str
    message: str
    current_value: float
    threshold_value: float
    triggered_at: datetime
    acknowledged_at: datetime | None = None
    resolved_at: datetime | None = None
    acknowledged_by: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "rule_id": self.rule_id,
            "rule_name": self.rule_name,
            "kpi_id": self.kpi_id,
            "severity": self.severity.value,
            "status": self.status.value,
            "title": self.title,
            "message": self.message,
            "current_value": self.current_value,
            "threshold_value": self.threshold_value,
            "triggered_at": self.triggered_at.isoformat(),
            "acknowledged_at": self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "acknowledged_by": self.acknowledged_by,
            "metadata": self.metadata,
        }


# =============================================================================
# THRESHOLD EVALUATOR
# =============================================================================


class ThresholdEvaluator:
    """Evaluates values against threshold rules."""

    @staticmethod
    def evaluate(
        value: float,
        operator: ThresholdOperator,
        threshold: float,
        threshold_upper: float | None = None,
    ) -> bool:
        """
        Evaluate if a value triggers the threshold.

        Returns True if threshold is breached.
        """
        if operator == ThresholdOperator.GREATER_THAN:
            return value > threshold
        elif operator == ThresholdOperator.GREATER_THAN_OR_EQUAL:
            return value >= threshold
        elif operator == ThresholdOperator.LESS_THAN:
            return value < threshold
        elif operator == ThresholdOperator.LESS_THAN_OR_EQUAL:
            return value <= threshold
        elif operator == ThresholdOperator.EQUAL:
            return value == threshold
        elif operator == ThresholdOperator.NOT_EQUAL:
            return value != threshold
        elif operator == ThresholdOperator.BETWEEN:
            if threshold_upper is None:
                return False
            return threshold <= value <= threshold_upper
        elif operator == ThresholdOperator.OUTSIDE:
            if threshold_upper is None:
                return False
            return value < threshold or value > threshold_upper
        else:
            return False


# =============================================================================
# ALERT MANAGER
# =============================================================================


class AlertManager:
    """
    Manages alert rules, evaluation, and history.

    Provides:
    - Rule management (add, update, delete)
    - Alert evaluation against rules
    - Alert history tracking
    - Notification dispatch
    """

    def __init__(self):
        self.rules: dict[str, AlertRule] = {}
        self.alerts: list[Alert] = []
        self.last_triggered: dict[str, datetime] = {}
        self.notification_handlers: dict[AlertChannel, Callable] = {}

    def add_rule(self, rule: AlertRule) -> None:
        """Add or update an alert rule."""
        self.rules[rule.id] = rule
        logger.info(f"Alert rule added: {rule.id} - {rule.name}")

    def remove_rule(self, rule_id: str) -> bool:
        """Remove an alert rule."""
        if rule_id in self.rules:
            del self.rules[rule_id]
            logger.info(f"Alert rule removed: {rule_id}")
            return True
        return False

    def get_rule(self, rule_id: str) -> AlertRule | None:
        """Get an alert rule by ID."""
        return self.rules.get(rule_id)

    def list_rules(self, kpi_id: str | None = None) -> list[AlertRule]:
        """List all rules, optionally filtered by KPI."""
        rules = list(self.rules.values())
        if kpi_id:
            rules = [r for r in rules if r.kpi_id == kpi_id]
        return rules

    def register_handler(
        self,
        channel: AlertChannel,
        handler: Callable[[Alert], None],
    ) -> None:
        """Register a notification handler for a channel."""
        self.notification_handlers[channel] = handler
        logger.info(f"Registered handler for channel: {channel.value}")

    def evaluate(
        self,
        kpi_id: str,
        value: float,
        metadata: dict[str, Any] | None = None,
    ) -> list[Alert]:
        """
        Evaluate a value against all applicable rules.

        Args:
            kpi_id: KPI identifier
            value: Current value to evaluate
            metadata: Additional context

        Returns:
            List of triggered alerts
        """
        triggered_alerts: list[Alert] = []
        now = datetime.now(timezone.utc)

        for rule in self.rules.values():
            if not rule.enabled or rule.kpi_id != kpi_id:
                continue

            # Check cooldown
            last_trigger = self.last_triggered.get(rule.id)
            if last_trigger:
                elapsed = (now - last_trigger).total_seconds() / 60
                if elapsed < rule.cooldown_minutes:
                    continue

            # Evaluate threshold
            breached = ThresholdEvaluator.evaluate(
                value=value,
                operator=rule.operator,
                threshold=rule.threshold,
                threshold_upper=rule.threshold_upper,
            )

            if breached:
                alert = self._create_alert(rule, value, metadata or {})
                triggered_alerts.append(alert)
                self.alerts.append(alert)
                self.last_triggered[rule.id] = now

                # Dispatch notifications
                self._dispatch_notifications(alert, rule.channels)

        return triggered_alerts

    def evaluate_dataframe(
        self,
        kpi_id: str,
        df: pd.DataFrame,
        value_column: str = "value",
    ) -> list[Alert]:
        """
        Evaluate the latest value from a DataFrame.

        Args:
            kpi_id: KPI identifier
            df: DataFrame with time series data
            value_column: Column containing values

        Returns:
            List of triggered alerts
        """
        if df.empty:
            return []

        # Get latest value
        df_sorted = df.sort_values(["year", "quarter"])
        latest_value = float(df_sorted.iloc[-1][value_column])

        return self.evaluate(kpi_id, latest_value)

    def _create_alert(
        self,
        rule: AlertRule,
        value: float,
        metadata: dict[str, Any],
    ) -> Alert:
        """Create an alert from a triggered rule."""
        now = datetime.now(timezone.utc)
        alert_id = f"alert_{rule.id}_{now.strftime('%Y%m%d%H%M%S')}"

        # Generate message based on operator
        operator_text = {
            ThresholdOperator.GREATER_THAN: "exceeded",
            ThresholdOperator.GREATER_THAN_OR_EQUAL: "reached or exceeded",
            ThresholdOperator.LESS_THAN: "dropped below",
            ThresholdOperator.LESS_THAN_OR_EQUAL: "at or below",
            ThresholdOperator.EQUAL: "exactly at",
            ThresholdOperator.NOT_EQUAL: "changed from",
            ThresholdOperator.BETWEEN: "within range",
            ThresholdOperator.OUTSIDE: "outside range",
        }

        op_text = operator_text.get(rule.operator, "triggered")

        title = f"{rule.severity.value.upper()}: {rule.name}"
        message = (
            f"KPI '{rule.kpi_id}' has {op_text} threshold. "
            f"Current value: {value:.2f}, Threshold: {rule.threshold:.2f}"
        )

        if rule.threshold_upper:
            message += f" - {rule.threshold_upper:.2f}"

        return Alert(
            id=alert_id,
            rule_id=rule.id,
            rule_name=rule.name,
            kpi_id=rule.kpi_id,
            severity=rule.severity,
            status=AlertStatus.ACTIVE,
            title=title,
            message=message,
            current_value=value,
            threshold_value=rule.threshold,
            triggered_at=now,
            metadata={**rule.metadata, **metadata},
        )

    def _dispatch_notifications(
        self,
        alert: Alert,
        channels: list[AlertChannel],
    ) -> None:
        """Dispatch alert to notification channels."""
        for channel in channels:
            handler = self.notification_handlers.get(channel)
            if handler:
                try:
                    handler(alert)
                    logger.info(f"Alert {alert.id} dispatched to {channel.value}")
                except Exception as e:
                    logger.error(f"Failed to dispatch alert to {channel.value}: {e}")
            else:
                # Default: log the alert
                logger.info(f"Alert triggered: {alert.title} - {alert.message}")

    def acknowledge(self, alert_id: str, user: str) -> bool:
        """Acknowledge an alert."""
        for alert in self.alerts:
            if alert.id == alert_id and alert.status == AlertStatus.ACTIVE:
                alert.status = AlertStatus.ACKNOWLEDGED
                alert.acknowledged_at = datetime.now(timezone.utc)
                alert.acknowledged_by = user
                logger.info(f"Alert {alert_id} acknowledged by {user}")
                return True
        return False

    def resolve(self, alert_id: str) -> bool:
        """Resolve an alert."""
        for alert in self.alerts:
            if alert.id == alert_id and alert.status in [
                AlertStatus.ACTIVE,
                AlertStatus.ACKNOWLEDGED,
            ]:
                alert.status = AlertStatus.RESOLVED
                alert.resolved_at = datetime.now(timezone.utc)
                logger.info(f"Alert {alert_id} resolved")
                return True
        return False

    def get_active_alerts(self, kpi_id: str | None = None) -> list[Alert]:
        """Get all active alerts, optionally filtered by KPI."""
        active = [a for a in self.alerts if a.status == AlertStatus.ACTIVE]
        if kpi_id:
            active = [a for a in active if a.kpi_id == kpi_id]
        return active

    def get_alert_history(
        self,
        kpi_id: str | None = None,
        limit: int = 100,
    ) -> list[Alert]:
        """Get alert history, optionally filtered by KPI."""
        alerts = self.alerts
        if kpi_id:
            alerts = [a for a in alerts if a.kpi_id == kpi_id]
        return sorted(alerts, key=lambda a: a.triggered_at, reverse=True)[:limit]


# =============================================================================
# DEFAULT ALERT RULES
# =============================================================================


def create_default_rules() -> list[AlertRule]:
    """Create default alert rules for common KPIs."""
    return [
        AlertRule(
            id="gdp_growth_low",
            name="GDP Growth Below Target",
            kpi_id="gdp_growth",
            operator=ThresholdOperator.LESS_THAN,
            threshold=2.0,
            severity=AlertSeverity.WARNING,
        ),
        AlertRule(
            id="gdp_growth_critical",
            name="GDP Growth Critical",
            kpi_id="gdp_growth",
            operator=ThresholdOperator.LESS_THAN,
            threshold=0.0,
            severity=AlertSeverity.CRITICAL,
        ),
        AlertRule(
            id="unemployment_high",
            name="Unemployment Above Target",
            kpi_id="unemployment_rate",
            operator=ThresholdOperator.GREATER_THAN,
            threshold=7.0,
            severity=AlertSeverity.WARNING,
        ),
        AlertRule(
            id="co2_emissions_high",
            name="CO2 Emissions Exceeding Limit",
            kpi_id="co2_emissions",
            operator=ThresholdOperator.GREATER_THAN,
            threshold=500.0,
            severity=AlertSeverity.WARNING,
        ),
        AlertRule(
            id="renewable_energy_low",
            name="Renewable Energy Below Target",
            kpi_id="renewable_energy_share",
            operator=ThresholdOperator.LESS_THAN,
            threshold=10.0,
            severity=AlertSeverity.INFO,
        ),
    ]


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================


# Global alert manager instance
_alert_manager: AlertManager | None = None


def get_alert_manager() -> AlertManager:
    """Get the global alert manager instance."""
    global _alert_manager
    if _alert_manager is None:
        _alert_manager = AlertManager()
        # Load default rules
        for rule in create_default_rules():
            _alert_manager.add_rule(rule)
    return _alert_manager


def add_alert_rule(
    rule_id: str,
    name: str,
    kpi_id: str,
    operator: str,
    threshold: float,
    severity: str = "warning",
    threshold_upper: float | None = None,
) -> dict[str, Any]:
    """
    Add a new alert rule.

    Args:
        rule_id: Unique rule identifier
        name: Human-readable rule name
        kpi_id: KPI to monitor
        operator: Comparison operator (gt, gte, lt, lte, eq, neq, between, outside)
        threshold: Threshold value
        severity: Alert severity (critical, warning, info)
        threshold_upper: Upper threshold for range operators

    Returns:
        Rule dictionary
    """
    manager = get_alert_manager()

    rule = AlertRule(
        id=rule_id,
        name=name,
        kpi_id=kpi_id,
        operator=ThresholdOperator(operator),
        threshold=threshold,
        threshold_upper=threshold_upper,
        severity=AlertSeverity(severity),
    )

    manager.add_rule(rule)
    return rule.to_dict()


def check_alerts(
    kpi_id: str,
    value: float,
) -> list[dict[str, Any]]:
    """
    Check if a value triggers any alerts.

    Returns list of triggered alert dictionaries.
    """
    manager = get_alert_manager()
    alerts = manager.evaluate(kpi_id, value)
    return [a.to_dict() for a in alerts]


def get_active_alerts(kpi_id: str | None = None) -> list[dict[str, Any]]:
    """
    Get all active alerts.

    Returns list of alert dictionaries.
    """
    manager = get_alert_manager()
    alerts = manager.get_active_alerts(kpi_id)
    return [a.to_dict() for a in alerts]


def acknowledge_alert(alert_id: str, user: str) -> bool:
    """Acknowledge an alert."""
    manager = get_alert_manager()
    return manager.acknowledge(alert_id, user)


def resolve_alert(alert_id: str) -> bool:
    """Resolve an alert."""
    manager = get_alert_manager()
    return manager.resolve(alert_id)
