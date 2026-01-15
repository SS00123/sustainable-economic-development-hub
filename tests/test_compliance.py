"""
Tests for compliance checker module.

Tests KPI register validation, governance checks, and compliance auditing.
"""

from datetime import datetime, timezone
from pathlib import Path

import pytest

from analytics_hub_platform.infrastructure.compliance_checker import (
    ComplianceCategory,
    ComplianceChecker,
    ComplianceIssue,
    ComplianceReport,
    ComplianceSeverity,
    check_kpi_compliance,
    get_compliance_score,
    is_fully_compliant,
    run_compliance_audit,
)


class TestComplianceSeverity:
    """Test ComplianceSeverity enum."""

    def test_severity_values(self):
        """Test all severity levels exist."""
        assert ComplianceSeverity.INFO.value == "info"
        assert ComplianceSeverity.WARNING.value == "warning"
        assert ComplianceSeverity.ERROR.value == "error"
        assert ComplianceSeverity.CRITICAL.value == "critical"


class TestComplianceCategory:
    """Test ComplianceCategory enum."""

    def test_category_values(self):
        """Test all categories exist."""
        assert ComplianceCategory.KPI_METADATA.value == "kpi_metadata"
        assert ComplianceCategory.DATA_QUALITY.value == "data_quality"
        assert ComplianceCategory.GOVERNANCE.value == "governance"
        assert ComplianceCategory.REGULATORY.value == "regulatory"
        assert ComplianceCategory.SECURITY.value == "security"


class TestComplianceIssue:
    """Test ComplianceIssue dataclass."""

    def test_issue_creation(self):
        """Test creating a compliance issue."""
        issue = ComplianceIssue(
            code="KPI-001",
            category=ComplianceCategory.KPI_METADATA,
            severity=ComplianceSeverity.ERROR,
            message="Missing required field",
        )

        assert issue.code == "KPI-001"
        assert issue.category == ComplianceCategory.KPI_METADATA
        assert issue.severity == ComplianceSeverity.ERROR
        assert issue.kpi_id is None
        assert issue.details == {}

    def test_issue_with_kpi_id(self):
        """Test issue with KPI reference."""
        issue = ComplianceIssue(
            code="GOV-001",
            category=ComplianceCategory.GOVERNANCE,
            severity=ComplianceSeverity.WARNING,
            message="Missing owner",
            kpi_id="ECON-001",
            details={"field": "owner"},
            recommendation="Assign an owner",
        )

        assert issue.kpi_id == "ECON-001"
        assert issue.details["field"] == "owner"
        assert issue.recommendation == "Assign an owner"

    def test_to_dict(self):
        """Test converting issue to dictionary."""
        issue = ComplianceIssue(
            code="KPI-002",
            category=ComplianceCategory.KPI_METADATA,
            severity=ComplianceSeverity.ERROR,
            message="Invalid format",
            kpi_id="ENV-001",
        )

        d = issue.to_dict()

        assert d["code"] == "KPI-002"
        assert d["category"] == "kpi_metadata"
        assert d["severity"] == "error"
        assert d["kpi_id"] == "ENV-001"


class TestComplianceReport:
    """Test ComplianceReport dataclass."""

    def test_report_creation(self):
        """Test creating a compliance report."""
        report = ComplianceReport(
            timestamp=datetime.now(timezone.utc),
            total_checks=100,
            passed_checks=90,
            failed_checks=10,
            issues=[],
            score=90.0,
        )

        assert report.total_checks == 100
        assert report.passed_checks == 90
        assert report.score == 90.0

    def test_report_is_compliant_no_issues(self):
        """Test compliant when no critical/error issues."""
        report = ComplianceReport(
            timestamp=datetime.now(timezone.utc),
            total_checks=50,
            passed_checks=48,
            failed_checks=2,
            issues=[
                ComplianceIssue(
                    code="INFO-001",
                    category=ComplianceCategory.GOVERNANCE,
                    severity=ComplianceSeverity.INFO,
                    message="Info message",
                ),
                ComplianceIssue(
                    code="WARN-001",
                    category=ComplianceCategory.GOVERNANCE,
                    severity=ComplianceSeverity.WARNING,
                    message="Warning message",
                ),
            ],
            score=96.0,
        )

        assert report.is_compliant is True

    def test_report_not_compliant_with_error(self):
        """Test not compliant with error issues."""
        report = ComplianceReport(
            timestamp=datetime.now(timezone.utc),
            total_checks=50,
            passed_checks=45,
            failed_checks=5,
            issues=[
                ComplianceIssue(
                    code="ERR-001",
                    category=ComplianceCategory.KPI_METADATA,
                    severity=ComplianceSeverity.ERROR,
                    message="Error message",
                ),
            ],
            score=90.0,
        )

        assert report.is_compliant is False

    def test_report_not_compliant_with_critical(self):
        """Test not compliant with critical issues."""
        report = ComplianceReport(
            timestamp=datetime.now(timezone.utc),
            total_checks=50,
            passed_checks=49,
            failed_checks=1,
            issues=[
                ComplianceIssue(
                    code="CRIT-001",
                    category=ComplianceCategory.SECURITY,
                    severity=ComplianceSeverity.CRITICAL,
                    message="Critical issue",
                ),
            ],
            score=98.0,
        )

        assert report.is_compliant is False
        assert len(report.critical_issues) == 1

    def test_report_to_dict(self):
        """Test report serialization."""
        ts = datetime.now(timezone.utc)
        report = ComplianceReport(
            timestamp=ts,
            total_checks=10,
            passed_checks=9,
            failed_checks=1,
            issues=[],
            score=90.0,
            summary={"by_category": {"kpi_metadata": 1}},
        )

        d = report.to_dict()

        assert d["total_checks"] == 10
        assert d["score"] == 90.0
        assert "timestamp" in d


class TestComplianceChecker:
    """Test ComplianceChecker class."""

    @pytest.fixture
    def checker(self):
        """Create checker with real KPI register."""
        kpi_path = (
            Path(__file__).parent.parent
            / "analytics_hub_platform"
            / "config"
            / "kpi_register.yaml"
        )
        return ComplianceChecker(kpi_path)

    def test_checker_init(self, checker):
        """Test checker initialization."""
        assert checker.kpi_register_path is not None

    def test_required_fields_constant(self):
        """Test required fields are defined."""
        assert "id" in ComplianceChecker.REQUIRED_KPI_FIELDS
        assert "name" in ComplianceChecker.REQUIRED_KPI_FIELDS
        assert "name_ar" in ComplianceChecker.REQUIRED_KPI_FIELDS
        assert "definition" in ComplianceChecker.REQUIRED_KPI_FIELDS

    def test_id_patterns_defined(self):
        """Test ID patterns for all pillars."""
        assert "economic" in ComplianceChecker.ID_PATTERNS
        assert "environmental" in ComplianceChecker.ID_PATTERNS
        assert "social" in ComplianceChecker.ID_PATTERNS
        assert "governance" in ComplianceChecker.ID_PATTERNS

    def test_valid_frequencies_defined(self):
        """Test valid frequencies list."""
        assert "annual" in ComplianceChecker.VALID_FREQUENCIES
        assert "quarterly" in ComplianceChecker.VALID_FREQUENCIES
        assert "monthly" in ComplianceChecker.VALID_FREQUENCIES


class TestComplianceCheckerWithRealData:
    """Test compliance checker with actual KPI register."""

    @pytest.fixture
    def checker(self):
        """Create checker pointing to real register."""
        kpi_path = (
            Path(__file__).parent.parent
            / "analytics_hub_platform"
            / "config"
            / "kpi_register.yaml"
        )
        if not kpi_path.exists():
            pytest.skip("KPI register not found")
        return ComplianceChecker(kpi_path)

    def test_kpi_register_exists(self, checker):
        """Test register file exists check."""
        result = checker.check_kpi_register_exists()
        assert result is True

    def test_run_all_checks(self, checker):
        """Test running all checks returns report."""
        report = checker.run_all_checks()

        assert isinstance(report, ComplianceReport)
        assert report.total_checks > 0
        assert 0 <= report.score <= 100

    def test_report_has_timestamp(self, checker):
        """Test report has valid timestamp."""
        report = checker.run_all_checks()

        assert report.timestamp is not None
        assert isinstance(report.timestamp, datetime)

    def test_report_summary_structure(self, checker):
        """Test report summary has expected structure."""
        report = checker.run_all_checks()

        assert "by_category" in report.summary
        assert "by_severity" in report.summary


class TestComplianceCheckerMissingFile:
    """Test compliance checker with missing file."""

    def test_missing_file_critical_issue(self, tmp_path):
        """Test missing KPI register generates critical issue."""
        fake_path = tmp_path / "nonexistent.yaml"
        checker = ComplianceChecker(fake_path)

        result = checker.check_kpi_register_exists()

        assert result is False

    def test_missing_file_in_full_report(self, tmp_path):
        """Test full report with missing file."""
        fake_path = tmp_path / "nonexistent.yaml"
        checker = ComplianceChecker(fake_path)

        report = checker.run_all_checks()

        # Should have critical issue
        assert len(report.critical_issues) > 0
        assert report.is_compliant is False


class TestConvenienceFunctions:
    """Test convenience functions."""

    @pytest.fixture
    def ensure_register_exists(self):
        """Skip if register doesn't exist."""
        kpi_path = (
            Path(__file__).parent.parent
            / "analytics_hub_platform"
            / "config"
            / "kpi_register.yaml"
        )
        if not kpi_path.exists():
            pytest.skip("KPI register not found")

    def test_run_compliance_audit(self, ensure_register_exists):
        """Test run_compliance_audit function."""
        report = run_compliance_audit()

        assert isinstance(report, ComplianceReport)
        assert report.total_checks > 0

    def test_get_compliance_score(self, ensure_register_exists):
        """Test get_compliance_score function."""
        score = get_compliance_score()

        assert isinstance(score, float)
        assert 0 <= score <= 100

    def test_is_fully_compliant_returns_bool(self, ensure_register_exists):
        """Test is_fully_compliant returns boolean."""
        result = is_fully_compliant()

        assert isinstance(result, bool)

    def test_check_kpi_compliance(self, ensure_register_exists):
        """Test check_kpi_compliance function."""
        issues = check_kpi_compliance("ECON-001")

        assert isinstance(issues, list)
        # May or may not have issues


class TestComplianceCheckerValidation:
    """Test specific validation logic."""

    @pytest.fixture
    def sample_register(self, tmp_path):
        """Create a minimal valid KPI register."""
        content = """
metadata:
  version: "1.0.0"

pillars:
  economic:
    name: "Economic"
    kpis:
      test_kpi:
        id: "ECON-001"
        name: "Test KPI"
        name_ar: "مؤشر اختبار"
        definition: "A test KPI"
        unit: "percentage"
        frequency: "annual"
        source: "Test Source"
        governance:
          owner: "Test Owner"
          steward: "Test Steward"
        thresholds:
          target: 50.0
        compliance:
          regulations: ["Test Reg"]
"""
        path = tmp_path / "test_register.yaml"
        path.write_text(content, encoding="utf-8")
        return path

    def test_valid_register_passes(self, sample_register):
        """Test valid register passes all checks."""
        checker = ComplianceChecker(sample_register)
        report = checker.run_all_checks()

        # Should have high score
        assert report.score >= 80

    def test_detects_missing_arabic(self, tmp_path):
        """Test detection of missing Arabic name."""
        content = """
pillars:
  economic:
    name: "Economic"
    kpis:
      test_kpi:
        id: "ECON-001"
        name: "Test KPI"
        name_ar: ""
        definition: "A test"
        unit: "percentage"
        frequency: "annual"
        source: "Test"
"""
        path = tmp_path / "test_register.yaml"
        path.write_text(content, encoding="utf-8")

        checker = ComplianceChecker(path)
        report = checker.run_all_checks()

        # Should have issue for missing Arabic
        arabic_issues = [i for i in report.issues if "Arabic" in i.message]
        assert len(arabic_issues) > 0

    def test_detects_invalid_frequency(self, tmp_path):
        """Test detection of invalid frequency."""
        content = """
pillars:
  economic:
    name: "Economic"
    kpis:
      test_kpi:
        id: "ECON-001"
        name: "Test KPI"
        name_ar: "اختبار"
        definition: "A test"
        unit: "percentage"
        frequency: "whenever"
        source: "Test"
"""
        path = tmp_path / "test_register.yaml"
        path.write_text(content, encoding="utf-8")

        checker = ComplianceChecker(path)
        report = checker.run_all_checks()

        # Should have issue for invalid frequency
        freq_issues = [i for i in report.issues if "frequency" in i.message.lower()]
        assert len(freq_issues) > 0

    def test_detects_invalid_unit(self, tmp_path):
        """Test detection of invalid unit."""
        content = """
pillars:
  economic:
    name: "Economic"
    kpis:
      test_kpi:
        id: "ECON-001"
        name: "Test KPI"
        name_ar: "اختبار"
        definition: "A test"
        unit: "widgets"
        frequency: "annual"
        source: "Test"
"""
        path = tmp_path / "test_register.yaml"
        path.write_text(content, encoding="utf-8")

        checker = ComplianceChecker(path)
        report = checker.run_all_checks()

        # Should have issue for invalid unit
        unit_issues = [i for i in report.issues if "unit" in i.message.lower()]
        assert len(unit_issues) > 0

    def test_detects_bad_id_format(self, tmp_path):
        """Test detection of non-conforming KPI ID."""
        content = """
pillars:
  economic:
    name: "Economic"
    kpis:
      test_kpi:
        id: "BAD-ID-123"
        name: "Test KPI"
        name_ar: "اختبار"
        definition: "A test"
        unit: "percentage"
        frequency: "annual"
        source: "Test"
"""
        path = tmp_path / "test_register.yaml"
        path.write_text(content, encoding="utf-8")

        checker = ComplianceChecker(path)
        report = checker.run_all_checks()

        # Should have issue for bad ID format
        id_issues = [i for i in report.issues if "pattern" in i.message.lower()]
        assert len(id_issues) > 0
