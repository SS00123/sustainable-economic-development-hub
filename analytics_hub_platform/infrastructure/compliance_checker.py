"""
Compliance Checker Module
Sustainable Economic Development Analytics Hub

Provides automated compliance verification for:
- KPI Register completeness and validity
- Data quality rule enforcement
- Governance policy compliance
- Regulatory requirement checks
"""

import logging
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)


# =============================================================================
# COMPLIANCE ENUMS AND MODELS
# =============================================================================


class ComplianceSeverity(Enum):
    """Severity levels for compliance issues."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ComplianceCategory(Enum):
    """Categories of compliance checks."""

    KPI_METADATA = "kpi_metadata"
    DATA_QUALITY = "data_quality"
    GOVERNANCE = "governance"
    REGULATORY = "regulatory"
    SECURITY = "security"


@dataclass
class ComplianceIssue:
    """Represents a single compliance issue."""

    code: str
    category: ComplianceCategory
    severity: ComplianceSeverity
    message: str
    kpi_id: str | None = None
    details: dict[str, Any] = field(default_factory=dict)
    recommendation: str = ""

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "code": self.code,
            "category": self.category.value,
            "severity": self.severity.value,
            "message": self.message,
            "kpi_id": self.kpi_id,
            "details": self.details,
            "recommendation": self.recommendation,
        }


@dataclass
class ComplianceReport:
    """Full compliance audit report."""

    timestamp: datetime
    total_checks: int
    passed_checks: int
    failed_checks: int
    issues: list[ComplianceIssue]
    score: float  # Percentage 0-100
    summary: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "total_checks": self.total_checks,
            "passed_checks": self.passed_checks,
            "failed_checks": self.failed_checks,
            "score": round(self.score, 2),
            "issues": [issue.to_dict() for issue in self.issues],
            "summary": self.summary,
        }

    @property
    def critical_issues(self) -> list[ComplianceIssue]:
        """Get critical issues only."""
        return [i for i in self.issues if i.severity == ComplianceSeverity.CRITICAL]

    @property
    def error_issues(self) -> list[ComplianceIssue]:
        """Get error issues only."""
        return [i for i in self.issues if i.severity == ComplianceSeverity.ERROR]

    @property
    def is_compliant(self) -> bool:
        """Check if fully compliant (no critical/error issues)."""
        return len(self.critical_issues) == 0 and len(self.error_issues) == 0


# =============================================================================
# COMPLIANCE CHECKER
# =============================================================================


class ComplianceChecker:
    """
    Automated compliance checker for the Analytics Hub.

    Validates:
    - KPI Register structure and completeness
    - Data quality rules
    - Governance policies
    - Regulatory requirements
    """

    # Required fields for each KPI
    REQUIRED_KPI_FIELDS = [
        "id",
        "name",
        "name_ar",
        "definition",
        "unit",
        "frequency",
        "source",
    ]

    # Required governance fields
    REQUIRED_GOVERNANCE_FIELDS = [
        "owner",
        "steward",
    ]

    # Valid ID patterns per pillar
    ID_PATTERNS = {
        "economic": r"^ECON-\d{3}$",
        "environmental": r"^ENV-\d{3}$",
        "social": r"^SOC-\d{3}$",
        "governance": r"^GOV-\d{3}$",
    }

    # Valid frequencies
    VALID_FREQUENCIES = [
        "daily",
        "weekly",
        "monthly",
        "quarterly",
        "annual",
        "biennial",
    ]

    # Valid units
    VALID_UNITS = [
        "percentage",
        "index",
        "billion_sar",
        "million_sar",
        "metric_tons_per_capita",
        "sar_per_cubic_meter",
        "count",
        "ratio",
    ]

    def __init__(self, kpi_register_path: Path | str | None = None):
        """
        Initialize compliance checker.

        Args:
            kpi_register_path: Path to KPI register YAML file
        """
        if kpi_register_path is None:
            # Default path
            kpi_register_path = (
                Path(__file__).parent.parent / "config" / "kpi_register.yaml"
            )
        self.kpi_register_path = Path(kpi_register_path)
        self._kpi_data: dict | None = None
        self._issues: list[ComplianceIssue] = []
        self._checks_run = 0
        self._checks_passed = 0

    def _load_kpi_register(self) -> dict:
        """Load KPI register from YAML file."""
        if self._kpi_data is not None:
            return self._kpi_data

        if not self.kpi_register_path.exists():
            raise FileNotFoundError(
                f"KPI Register not found: {self.kpi_register_path}"
            )

        with open(self.kpi_register_path, encoding="utf-8") as f:
            self._kpi_data = yaml.safe_load(f)

        return self._kpi_data

    def _add_issue(
        self,
        code: str,
        category: ComplianceCategory,
        severity: ComplianceSeverity,
        message: str,
        kpi_id: str | None = None,
        details: dict | None = None,
        recommendation: str = "",
    ):
        """Add a compliance issue."""
        self._issues.append(
            ComplianceIssue(
                code=code,
                category=category,
                severity=severity,
                message=message,
                kpi_id=kpi_id,
                details=details or {},
                recommendation=recommendation,
            )
        )

    def _check_passed(self):
        """Record a passed check."""
        self._checks_run += 1
        self._checks_passed += 1

    def _check_failed(self):
        """Record a failed check."""
        self._checks_run += 1

    # =========================================================================
    # KPI METADATA CHECKS
    # =========================================================================

    def check_kpi_register_exists(self) -> bool:
        """Check that KPI register file exists."""
        if self.kpi_register_path.exists():
            self._check_passed()
            return True
        else:
            self._check_failed()
            self._add_issue(
                code="KPI-001",
                category=ComplianceCategory.KPI_METADATA,
                severity=ComplianceSeverity.CRITICAL,
                message="KPI Register file not found",
                details={"path": str(self.kpi_register_path)},
                recommendation="Create kpi_register.yaml in config directory",
            )
            return False

    def check_kpi_required_fields(self) -> bool:
        """Check all KPIs have required fields."""
        try:
            data = self._load_kpi_register()
        except FileNotFoundError:
            return False

        all_valid = True
        pillars = data.get("pillars", {})

        for pillar_name, pillar_data in pillars.items():
            kpis = pillar_data.get("kpis", {})
            for kpi_name, kpi_data in kpis.items():
                for field in self.REQUIRED_KPI_FIELDS:
                    if field not in kpi_data or kpi_data[field] is None:
                        self._check_failed()
                        self._add_issue(
                            code="KPI-002",
                            category=ComplianceCategory.KPI_METADATA,
                            severity=ComplianceSeverity.ERROR,
                            message=f"Missing required field: {field}",
                            kpi_id=kpi_data.get("id", kpi_name),
                            details={"field": field, "pillar": pillar_name},
                            recommendation=f"Add '{field}' field to KPI definition",
                        )
                        all_valid = False
                    else:
                        self._check_passed()

        return all_valid

    def check_kpi_id_format(self) -> bool:
        """Check KPI IDs follow naming convention."""
        try:
            data = self._load_kpi_register()
        except FileNotFoundError:
            return False

        all_valid = True
        pillars = data.get("pillars", {})

        for pillar_name, pillar_data in pillars.items():
            pattern = self.ID_PATTERNS.get(pillar_name)
            if not pattern:
                continue

            kpis = pillar_data.get("kpis", {})
            for kpi_name, kpi_data in kpis.items():
                kpi_id = kpi_data.get("id", "")
                if re.match(pattern, kpi_id):
                    self._check_passed()
                else:
                    self._check_failed()
                    self._add_issue(
                        code="KPI-003",
                        category=ComplianceCategory.KPI_METADATA,
                        severity=ComplianceSeverity.WARNING,
                        message=f"KPI ID does not match expected pattern",
                        kpi_id=kpi_id,
                        details={
                            "expected_pattern": pattern,
                            "actual_id": kpi_id,
                            "pillar": pillar_name,
                        },
                        recommendation=f"Use format {pattern} for {pillar_name} KPIs",
                    )
                    all_valid = False

        return all_valid

    def check_kpi_valid_frequency(self) -> bool:
        """Check KPI frequencies are valid."""
        try:
            data = self._load_kpi_register()
        except FileNotFoundError:
            return False

        all_valid = True
        pillars = data.get("pillars", {})

        for pillar_name, pillar_data in pillars.items():
            kpis = pillar_data.get("kpis", {})
            for kpi_name, kpi_data in kpis.items():
                frequency = kpi_data.get("frequency", "")
                if frequency in self.VALID_FREQUENCIES:
                    self._check_passed()
                else:
                    self._check_failed()
                    self._add_issue(
                        code="KPI-004",
                        category=ComplianceCategory.KPI_METADATA,
                        severity=ComplianceSeverity.WARNING,
                        message=f"Invalid frequency: {frequency}",
                        kpi_id=kpi_data.get("id"),
                        details={
                            "valid_frequencies": self.VALID_FREQUENCIES,
                            "actual": frequency,
                        },
                        recommendation=f"Use one of: {', '.join(self.VALID_FREQUENCIES)}",
                    )
                    all_valid = False

        return all_valid

    def check_kpi_valid_unit(self) -> bool:
        """Check KPI units are valid."""
        try:
            data = self._load_kpi_register()
        except FileNotFoundError:
            return False

        all_valid = True
        pillars = data.get("pillars", {})

        for pillar_name, pillar_data in pillars.items():
            kpis = pillar_data.get("kpis", {})
            for kpi_name, kpi_data in kpis.items():
                unit = kpi_data.get("unit", "")
                if unit in self.VALID_UNITS:
                    self._check_passed()
                else:
                    self._check_failed()
                    self._add_issue(
                        code="KPI-005",
                        category=ComplianceCategory.KPI_METADATA,
                        severity=ComplianceSeverity.WARNING,
                        message=f"Invalid unit: {unit}",
                        kpi_id=kpi_data.get("id"),
                        details={"valid_units": self.VALID_UNITS, "actual": unit},
                        recommendation=f"Use one of: {', '.join(self.VALID_UNITS)}",
                    )
                    all_valid = False

        return all_valid

    # =========================================================================
    # GOVERNANCE CHECKS
    # =========================================================================

    def check_kpi_governance_fields(self) -> bool:
        """Check KPIs have governance information."""
        try:
            data = self._load_kpi_register()
        except FileNotFoundError:
            return False

        all_valid = True
        pillars = data.get("pillars", {})

        for pillar_name, pillar_data in pillars.items():
            kpis = pillar_data.get("kpis", {})
            for kpi_name, kpi_data in kpis.items():
                governance = kpi_data.get("governance", {})
                for field in self.REQUIRED_GOVERNANCE_FIELDS:
                    if field not in governance or not governance[field]:
                        self._check_failed()
                        self._add_issue(
                            code="GOV-001",
                            category=ComplianceCategory.GOVERNANCE,
                            severity=ComplianceSeverity.ERROR,
                            message=f"Missing governance field: {field}",
                            kpi_id=kpi_data.get("id"),
                            details={"field": field, "pillar": pillar_name},
                            recommendation=f"Assign a {field} to this KPI",
                        )
                        all_valid = False
                    else:
                        self._check_passed()

        return all_valid

    def check_kpi_has_thresholds(self) -> bool:
        """Check KPIs have defined thresholds."""
        try:
            data = self._load_kpi_register()
        except FileNotFoundError:
            return False

        all_valid = True
        pillars = data.get("pillars", {})

        for pillar_name, pillar_data in pillars.items():
            kpis = pillar_data.get("kpis", {})
            for kpi_name, kpi_data in kpis.items():
                thresholds = kpi_data.get("thresholds", {})
                if thresholds and thresholds.get("target") is not None:
                    self._check_passed()
                else:
                    self._check_failed()
                    self._add_issue(
                        code="GOV-002",
                        category=ComplianceCategory.GOVERNANCE,
                        severity=ComplianceSeverity.WARNING,
                        message="KPI missing target threshold",
                        kpi_id=kpi_data.get("id"),
                        details={"pillar": pillar_name},
                        recommendation="Define target threshold for monitoring",
                    )
                    all_valid = False

        return all_valid

    def check_kpi_has_compliance_info(self) -> bool:
        """Check KPIs have compliance information."""
        try:
            data = self._load_kpi_register()
        except FileNotFoundError:
            return False

        all_valid = True
        pillars = data.get("pillars", {})

        for pillar_name, pillar_data in pillars.items():
            kpis = pillar_data.get("kpis", {})
            for kpi_name, kpi_data in kpis.items():
                compliance = kpi_data.get("compliance", {})
                if compliance and compliance.get("regulations"):
                    self._check_passed()
                else:
                    self._check_failed()
                    self._add_issue(
                        code="REG-001",
                        category=ComplianceCategory.REGULATORY,
                        severity=ComplianceSeverity.INFO,
                        message="KPI missing regulatory compliance info",
                        kpi_id=kpi_data.get("id"),
                        details={"pillar": pillar_name},
                        recommendation="Document applicable regulations",
                    )
                    all_valid = False

        return all_valid

    def check_arabic_names_present(self) -> bool:
        """Check all KPIs have Arabic translations."""
        try:
            data = self._load_kpi_register()
        except FileNotFoundError:
            return False

        all_valid = True
        pillars = data.get("pillars", {})

        for pillar_name, pillar_data in pillars.items():
            kpis = pillar_data.get("kpis", {})
            for kpi_name, kpi_data in kpis.items():
                name_ar = kpi_data.get("name_ar", "")
                if name_ar and len(name_ar) > 0:
                    self._check_passed()
                else:
                    self._check_failed()
                    self._add_issue(
                        code="GOV-003",
                        category=ComplianceCategory.GOVERNANCE,
                        severity=ComplianceSeverity.WARNING,
                        message="Missing Arabic name (name_ar)",
                        kpi_id=kpi_data.get("id"),
                        details={"pillar": pillar_name},
                        recommendation="Add Arabic translation for bilingual support",
                    )
                    all_valid = False

        return all_valid

    # =========================================================================
    # RUN ALL CHECKS
    # =========================================================================

    def run_all_checks(self) -> ComplianceReport:
        """Run all compliance checks and return report."""
        self._issues = []
        self._checks_run = 0
        self._checks_passed = 0

        # Run all checks
        self.check_kpi_register_exists()
        self.check_kpi_required_fields()
        self.check_kpi_id_format()
        self.check_kpi_valid_frequency()
        self.check_kpi_valid_unit()
        self.check_kpi_governance_fields()
        self.check_kpi_has_thresholds()
        self.check_kpi_has_compliance_info()
        self.check_arabic_names_present()

        # Calculate score
        score = (
            (self._checks_passed / self._checks_run * 100)
            if self._checks_run > 0
            else 0
        )

        # Build summary
        summary = {
            "by_category": {},
            "by_severity": {},
        }

        for issue in self._issues:
            cat = issue.category.value
            sev = issue.severity.value
            summary["by_category"][cat] = summary["by_category"].get(cat, 0) + 1
            summary["by_severity"][sev] = summary["by_severity"].get(sev, 0) + 1

        return ComplianceReport(
            timestamp=datetime.now(timezone.utc),
            total_checks=self._checks_run,
            passed_checks=self._checks_passed,
            failed_checks=self._checks_run - self._checks_passed,
            issues=self._issues,
            score=score,
            summary=summary,
        )


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================


def run_compliance_audit(
    kpi_register_path: Path | str | None = None,
) -> ComplianceReport:
    """
    Run a full compliance audit.

    Args:
        kpi_register_path: Optional path to KPI register

    Returns:
        ComplianceReport with all findings
    """
    checker = ComplianceChecker(kpi_register_path)
    return checker.run_all_checks()


def check_kpi_compliance(kpi_id: str) -> list[ComplianceIssue]:
    """
    Check compliance for a specific KPI.

    Args:
        kpi_id: The KPI ID to check

    Returns:
        List of compliance issues for this KPI
    """
    checker = ComplianceChecker()
    report = checker.run_all_checks()
    return [issue for issue in report.issues if issue.kpi_id == kpi_id]


def get_compliance_score() -> float:
    """Get overall compliance score (0-100)."""
    checker = ComplianceChecker()
    report = checker.run_all_checks()
    return report.score


def is_fully_compliant() -> bool:
    """Check if system is fully compliant (no critical/error issues)."""
    checker = ComplianceChecker()
    report = checker.run_all_checks()
    return report.is_compliant
