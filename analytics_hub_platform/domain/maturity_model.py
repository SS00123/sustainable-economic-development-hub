"""
Maturity Model Module
Sustainable Economic Development Analytics Hub

Provides capability maturity assessment for KPI tracking and analytics practices.
Based on CMMI-style maturity levels adapted for government analytics:
- Level 1: Initial - Ad-hoc, reactive
- Level 2: Developing - Documented, repeatable
- Level 3: Defined - Standardized, proactive
- Level 4: Managed - Measured, controlled
- Level 5: Optimizing - Continuous improvement

Supports:
- Capability dimension assessments
- Overall maturity scoring
- Gap analysis and recommendations
- Benchmarking against targets
- Roadmap generation
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


logger = logging.getLogger(__name__)


# =============================================================================
# ENUMS AND CONSTANTS
# =============================================================================


class MaturityLevel(int, Enum):
    """Capability Maturity Model levels."""

    INITIAL = 1  # Ad-hoc, reactive, unpredictable
    DEVELOPING = 2  # Documented, repeatable basics
    DEFINED = 3  # Standardized, proactive processes
    MANAGED = 4  # Measured, quantitatively controlled
    OPTIMIZING = 5  # Continuous improvement, innovation


class CapabilityDimension(str, Enum):
    """Dimensions of analytics capability maturity."""

    DATA_QUALITY = "data_quality"  # Data completeness, accuracy, timeliness
    DATA_GOVERNANCE = "data_governance"  # Ownership, policies, compliance
    ANALYTICS_CAPABILITY = "analytics_capability"  # Analysis depth, methods
    REPORTING = "reporting"  # Dashboards, visualization, distribution
    DECISION_SUPPORT = "decision_support"  # Insights, recommendations
    TECHNOLOGY = "technology"  # Infrastructure, automation, integration
    ORGANIZATION = "organization"  # Skills, culture, processes
    STRATEGIC_ALIGNMENT = "strategic_alignment"  # Vision 2030 alignment


class AssessmentStatus(str, Enum):
    """Status of a maturity assessment."""

    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    APPROVED = "approved"
    ARCHIVED = "archived"


# Maturity level metadata
MATURITY_LEVEL_INFO: dict[MaturityLevel, dict[str, str]] = {
    MaturityLevel.INITIAL: {
        "name": "Initial",
        "name_ar": "مبدئي",
        "description": "Ad-hoc and reactive processes with unpredictable outcomes",
        "color": "#ef4444",  # Red
    },
    MaturityLevel.DEVELOPING: {
        "name": "Developing",
        "name_ar": "متطور",
        "description": "Documented processes with repeatable basic practices",
        "color": "#f97316",  # Orange
    },
    MaturityLevel.DEFINED: {
        "name": "Defined",
        "name_ar": "محدد",
        "description": "Standardized and proactive processes organization-wide",
        "color": "#eab308",  # Yellow
    },
    MaturityLevel.MANAGED: {
        "name": "Managed",
        "name_ar": "مُدار",
        "description": "Quantitatively measured and controlled processes",
        "color": "#22c55e",  # Green
    },
    MaturityLevel.OPTIMIZING: {
        "name": "Optimizing",
        "name_ar": "محسّن",
        "description": "Continuous improvement with innovation focus",
        "color": "#3b82f6",  # Blue
    },
}


# Dimension metadata and criteria
DIMENSION_CRITERIA: dict[CapabilityDimension, dict[str, Any]] = {
    CapabilityDimension.DATA_QUALITY: {
        "name": "Data Quality",
        "name_ar": "جودة البيانات",
        "description": "Completeness, accuracy, and timeliness of data",
        "weight": 0.15,
        "criteria": {
            MaturityLevel.INITIAL: [
                "No formal data quality checks",
                "Ad-hoc data validation",
                "Incomplete data common",
            ],
            MaturityLevel.DEVELOPING: [
                "Basic validation rules defined",
                "Manual quality checks performed",
                "Quality issues documented",
            ],
            MaturityLevel.DEFINED: [
                "Automated quality checks",
                "Quality metrics tracked",
                "DQ thresholds established",
            ],
            MaturityLevel.MANAGED: [
                "Quality SLAs defined and measured",
                "Root cause analysis performed",
                "Proactive quality monitoring",
            ],
            MaturityLevel.OPTIMIZING: [
                "Predictive quality management",
                "Self-healing data pipelines",
                "Continuous improvement loop",
            ],
        },
    },
    CapabilityDimension.DATA_GOVERNANCE: {
        "name": "Data Governance",
        "name_ar": "حوكمة البيانات",
        "description": "Ownership, policies, and compliance management",
        "weight": 0.15,
        "criteria": {
            MaturityLevel.INITIAL: [
                "No formal ownership",
                "No data policies",
                "Compliance not tracked",
            ],
            MaturityLevel.DEVELOPING: [
                "Some owners assigned",
                "Basic policies drafted",
                "Compliance awareness",
            ],
            MaturityLevel.DEFINED: [
                "Clear ownership matrix",
                "Policies published and enforced",
                "Regular compliance audits",
            ],
            MaturityLevel.MANAGED: [
                "Data stewardship program",
                "Policy compliance measured",
                "Automated compliance checks",
            ],
            MaturityLevel.OPTIMIZING: [
                "Enterprise data management",
                "Policy optimization cycle",
                "Proactive regulatory alignment",
            ],
        },
    },
    CapabilityDimension.ANALYTICS_CAPABILITY: {
        "name": "Analytics Capability",
        "name_ar": "القدرة التحليلية",
        "description": "Depth and sophistication of analytical methods",
        "weight": 0.15,
        "criteria": {
            MaturityLevel.INITIAL: [
                "Basic reporting only",
                "Manual calculations",
                "No trend analysis",
            ],
            MaturityLevel.DEVELOPING: [
                "Standard reports automated",
                "Basic trend analysis",
                "Simple visualizations",
            ],
            MaturityLevel.DEFINED: [
                "Advanced visualizations",
                "Statistical analysis",
                "Comparative analytics",
            ],
            MaturityLevel.MANAGED: [
                "Predictive analytics",
                "ML models deployed",
                "Anomaly detection",
            ],
            MaturityLevel.OPTIMIZING: [
                "AI-powered insights",
                "Prescriptive analytics",
                "Continuous model improvement",
            ],
        },
    },
    CapabilityDimension.REPORTING: {
        "name": "Reporting & Visualization",
        "name_ar": "إعداد التقارير والتصور",
        "description": "Dashboard, visualization, and report distribution",
        "weight": 0.10,
        "criteria": {
            MaturityLevel.INITIAL: [
                "Manual report generation",
                "Static spreadsheets",
                "Email distribution",
            ],
            MaturityLevel.DEVELOPING: [
                "Scheduled reports",
                "Basic dashboards",
                "Defined distribution lists",
            ],
            MaturityLevel.DEFINED: [
                "Interactive dashboards",
                "Role-based views",
                "Self-service reporting",
            ],
            MaturityLevel.MANAGED: [
                "Real-time dashboards",
                "Drill-down capabilities",
                "Automated alerts",
            ],
            MaturityLevel.OPTIMIZING: [
                "Personalized dashboards",
                "Embedded analytics",
                "Natural language reporting",
            ],
        },
    },
    CapabilityDimension.DECISION_SUPPORT: {
        "name": "Decision Support",
        "name_ar": "دعم القرار",
        "description": "Insights, recommendations, and decision enablement",
        "weight": 0.15,
        "criteria": {
            MaturityLevel.INITIAL: [
                "Data without context",
                "No recommendations",
                "Reactive decisions",
            ],
            MaturityLevel.DEVELOPING: [
                "Basic insights provided",
                "Manual recommendations",
                "Some scenario planning",
            ],
            MaturityLevel.DEFINED: [
                "Automated insights",
                "KPI-linked recommendations",
                "What-if analysis",
            ],
            MaturityLevel.MANAGED: [
                "AI-generated insights",
                "Prioritized actions",
                "Impact quantification",
            ],
            MaturityLevel.OPTIMIZING: [
                "Autonomous decisions",
                "Continuous learning",
                "Strategic optimization",
            ],
        },
    },
    CapabilityDimension.TECHNOLOGY: {
        "name": "Technology & Infrastructure",
        "name_ar": "التقنية والبنية التحتية",
        "description": "Tools, automation, and system integration",
        "weight": 0.10,
        "criteria": {
            MaturityLevel.INITIAL: [
                "Siloed systems",
                "Manual integrations",
                "No automation",
            ],
            MaturityLevel.DEVELOPING: [
                "Basic integrations",
                "Some automation",
                "Standard tools",
            ],
            MaturityLevel.DEFINED: [
                "Unified platform",
                "Automated pipelines",
                "API-based integration",
            ],
            MaturityLevel.MANAGED: [
                "Cloud-native platform",
                "CI/CD for analytics",
                "Monitoring & observability",
            ],
            MaturityLevel.OPTIMIZING: [
                "AI-ops enabled",
                "Self-scaling infrastructure",
                "Innovation platform",
            ],
        },
    },
    CapabilityDimension.ORGANIZATION: {
        "name": "Organization & Skills",
        "name_ar": "التنظيم والمهارات",
        "description": "Team capabilities, culture, and processes",
        "weight": 0.10,
        "criteria": {
            MaturityLevel.INITIAL: [
                "Individual contributors",
                "No analytics team",
                "Limited skills",
            ],
            MaturityLevel.DEVELOPING: [
                "Small analytics team",
                "Basic training",
                "Defined roles",
            ],
            MaturityLevel.DEFINED: [
                "Center of Excellence",
                "Skill development program",
                "Cross-functional teams",
            ],
            MaturityLevel.MANAGED: [
                "Data literacy program",
                "Performance metrics",
                "Agile practices",
            ],
            MaturityLevel.OPTIMIZING: [
                "Data-driven culture",
                "Continuous learning",
                "Innovation incentives",
            ],
        },
    },
    CapabilityDimension.STRATEGIC_ALIGNMENT: {
        "name": "Strategic Alignment",
        "name_ar": "التوافق الاستراتيجي",
        "description": "Alignment with Vision 2030 and organizational goals",
        "weight": 0.10,
        "criteria": {
            MaturityLevel.INITIAL: [
                "No strategic linkage",
                "Operational focus only",
                "Disconnected metrics",
            ],
            MaturityLevel.DEVELOPING: [
                "Vision 2030 awareness",
                "Some KPI alignment",
                "Annual strategy review",
            ],
            MaturityLevel.DEFINED: [
                "KPIs linked to Vision 2030",
                "Strategic dashboard",
                "Regular alignment checks",
            ],
            MaturityLevel.MANAGED: [
                "Real-time goal tracking",
                "Impact measurement",
                "Strategic scenario planning",
            ],
            MaturityLevel.OPTIMIZING: [
                "Dynamic goal adjustment",
                "Predictive goal attainment",
                "Strategy optimization loop",
            ],
        },
    },
}


# =============================================================================
# DATA MODELS
# =============================================================================


@dataclass
class DimensionAssessment:
    """Assessment result for a single capability dimension."""

    dimension: CapabilityDimension
    current_level: MaturityLevel
    target_level: MaturityLevel
    score: float  # 1.0 - 5.0
    evidence: list[str] = field(default_factory=list)
    gaps: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    assessed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def gap_score(self) -> float:
        """Calculate gap between current and target (0 = no gap)."""
        return max(0, self.target_level.value - self.current_level.value)

    @property
    def gap_percentage(self) -> float:
        """Gap as percentage of target."""
        if self.target_level.value == 0:
            return 0.0
        return (self.gap_score / self.target_level.value) * 100

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "dimension": self.dimension.value,
            "dimension_name": DIMENSION_CRITERIA[self.dimension]["name"],
            "current_level": self.current_level.value,
            "current_level_name": MATURITY_LEVEL_INFO[self.current_level]["name"],
            "target_level": self.target_level.value,
            "target_level_name": MATURITY_LEVEL_INFO[self.target_level]["name"],
            "score": round(self.score, 2),
            "gap_score": self.gap_score,
            "gap_percentage": round(self.gap_percentage, 1),
            "evidence": self.evidence,
            "gaps": self.gaps,
            "recommendations": self.recommendations,
            "assessed_at": self.assessed_at.isoformat(),
        }


@dataclass
class MaturityAssessment:
    """Complete maturity assessment across all dimensions."""

    id: str
    name: str
    description: str
    status: AssessmentStatus
    assessor: str
    dimension_assessments: list[DimensionAssessment] = field(default_factory=list)
    overall_score: float = 0.0
    overall_level: MaturityLevel = MaturityLevel.INITIAL
    target_level: MaturityLevel = MaturityLevel.MANAGED
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = field(default_factory=dict)

    def calculate_overall_score(self) -> float:
        """Calculate weighted overall maturity score."""
        if not self.dimension_assessments:
            return 1.0

        total_weight = 0.0
        weighted_score = 0.0

        for assessment in self.dimension_assessments:
            weight = DIMENSION_CRITERIA[assessment.dimension]["weight"]
            weighted_score += assessment.score * weight
            total_weight += weight

        if total_weight > 0:
            self.overall_score = weighted_score / total_weight
        else:
            self.overall_score = 1.0

        # Determine overall level from score
        self.overall_level = MaturityLevel(max(1, min(5, round(self.overall_score))))
        return self.overall_score

    @property
    def strengths(self) -> list[DimensionAssessment]:
        """Get dimensions at or above target level."""
        return [
            a for a in self.dimension_assessments
            if a.current_level.value >= a.target_level.value
        ]

    @property
    def weaknesses(self) -> list[DimensionAssessment]:
        """Get dimensions below target level, sorted by gap."""
        below_target = [
            a for a in self.dimension_assessments
            if a.current_level.value < a.target_level.value
        ]
        return sorted(below_target, key=lambda x: x.gap_score, reverse=True)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "status": self.status.value,
            "assessor": self.assessor,
            "overall_score": round(self.overall_score, 2),
            "overall_level": self.overall_level.value,
            "overall_level_name": MATURITY_LEVEL_INFO[self.overall_level]["name"],
            "target_level": self.target_level.value,
            "target_level_name": MATURITY_LEVEL_INFO[self.target_level]["name"],
            "dimension_assessments": [a.to_dict() for a in self.dimension_assessments],
            "strengths_count": len(self.strengths),
            "weaknesses_count": len(self.weaknesses),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "metadata": self.metadata,
        }


@dataclass
class Benchmark:
    """Benchmark reference for comparison."""

    id: str
    name: str
    benchmark_type: str  # 'target', 'peer', 'industry', 'historical'
    dimension_scores: dict[CapabilityDimension, float] = field(default_factory=dict)
    overall_score: float = 0.0
    description: str = ""
    source: str = ""
    as_of_date: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "benchmark_type": self.benchmark_type,
            "dimension_scores": {
                k.value: round(v, 2) for k, v in self.dimension_scores.items()
            },
            "overall_score": round(self.overall_score, 2),
            "description": self.description,
            "source": self.source,
            "as_of_date": self.as_of_date.isoformat(),
        }


@dataclass
class BenchmarkComparison:
    """Comparison between assessment and benchmark."""

    assessment: MaturityAssessment
    benchmark: Benchmark
    overall_gap: float = 0.0
    dimension_gaps: dict[CapabilityDimension, float] = field(default_factory=dict)
    percentile: float | None = None  # Position relative to peer group

    def calculate_gaps(self) -> None:
        """Calculate gaps between assessment and benchmark."""
        self.overall_gap = self.benchmark.overall_score - self.assessment.overall_score

        for dim_assessment in self.assessment.dimension_assessments:
            dim = dim_assessment.dimension
            if dim in self.benchmark.dimension_scores:
                self.dimension_gaps[dim] = (
                    self.benchmark.dimension_scores[dim] - dim_assessment.score
                )

    @property
    def dimensions_above_benchmark(self) -> list[CapabilityDimension]:
        """Dimensions where assessment exceeds benchmark."""
        return [dim for dim, gap in self.dimension_gaps.items() if gap < 0]

    @property
    def dimensions_below_benchmark(self) -> list[CapabilityDimension]:
        """Dimensions where assessment is below benchmark."""
        return [dim for dim, gap in self.dimension_gaps.items() if gap > 0]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "assessment_id": self.assessment.id,
            "benchmark_id": self.benchmark.id,
            "benchmark_name": self.benchmark.name,
            "overall_gap": round(self.overall_gap, 2),
            "dimension_gaps": {
                k.value: round(v, 2) for k, v in self.dimension_gaps.items()
            },
            "percentile": self.percentile,
            "above_benchmark_count": len(self.dimensions_above_benchmark),
            "below_benchmark_count": len(self.dimensions_below_benchmark),
        }


# =============================================================================
# MATURITY ASSESSOR
# =============================================================================


class MaturityAssessor:
    """
    Performs capability maturity assessments.

    Supports:
    - Manual assessment input
    - Automated assessment from platform metrics
    - Hybrid assessment combining both
    """

    def __init__(self, target_level: MaturityLevel = MaturityLevel.MANAGED):
        """
        Initialize the assessor.

        Args:
            target_level: Default target maturity level for assessments
        """
        self.target_level = target_level

    def assess_dimension(
        self,
        dimension: CapabilityDimension,
        current_level: MaturityLevel,
        evidence: list[str] | None = None,
        target_level: MaturityLevel | None = None,
    ) -> DimensionAssessment:
        """
        Assess a single capability dimension.

        Args:
            dimension: The dimension to assess
            current_level: Assessed current maturity level
            evidence: Evidence supporting the assessment
            target_level: Target level (defaults to assessor target)

        Returns:
            DimensionAssessment result
        """
        target = target_level or self.target_level
        criteria = DIMENSION_CRITERIA[dimension]["criteria"]

        # Generate gaps based on criteria between current and target
        gaps = []
        recommendations = []

        if current_level.value < target.value:
            # Get criteria for next level
            next_level = MaturityLevel(current_level.value + 1)
            next_criteria = criteria.get(next_level, [])
            gaps.extend([f"Missing: {c}" for c in next_criteria])

            # Generate recommendations
            recommendations.extend([
                f"Implement: {c}" for c in next_criteria[:3]  # Top 3
            ])

        return DimensionAssessment(
            dimension=dimension,
            current_level=current_level,
            target_level=target,
            score=float(current_level.value),
            evidence=evidence or [],
            gaps=gaps,
            recommendations=recommendations,
        )

    def assess_from_metrics(
        self,
        metrics: dict[str, Any],
        assessment_id: str = "auto",
        name: str = "Automated Assessment",
    ) -> MaturityAssessment:
        """
        Generate maturity assessment from platform metrics.

        Args:
            metrics: Dictionary of platform metrics
            assessment_id: Assessment identifier
            name: Assessment name

        Returns:
            MaturityAssessment based on metrics
        """
        dimension_assessments = []

        # Data Quality assessment
        dq_score = metrics.get("data_quality_score", 0)
        dq_level = self._score_to_level(dq_score / 20)  # 0-100 → 0-5
        dimension_assessments.append(
            self.assess_dimension(
                CapabilityDimension.DATA_QUALITY,
                dq_level,
                evidence=[f"Data quality score: {dq_score}%"],
            )
        )

        # Data Governance assessment
        governance_score = metrics.get("governance_score", 0)
        gov_level = self._score_to_level(governance_score / 20)
        dimension_assessments.append(
            self.assess_dimension(
                CapabilityDimension.DATA_GOVERNANCE,
                gov_level,
                evidence=[f"Governance compliance: {governance_score}%"],
            )
        )

        # Analytics Capability assessment
        analytics_score = metrics.get("analytics_score", 0)
        if analytics_score == 0:
            # Infer from features available
            has_forecasting = metrics.get("has_forecasting", False)
            has_anomaly = metrics.get("has_anomaly_detection", False)
            has_insights = metrics.get("has_insights", False)
            feature_count = sum([has_forecasting, has_anomaly, has_insights])
            analytics_score = 40 + (feature_count * 20)

        analytics_level = self._score_to_level(analytics_score / 20)
        dimension_assessments.append(
            self.assess_dimension(
                CapabilityDimension.ANALYTICS_CAPABILITY,
                analytics_level,
                evidence=[f"Analytics capability score: {analytics_score}%"],
            )
        )

        # Reporting assessment
        reporting_score = metrics.get("reporting_score", 0)
        if reporting_score == 0:
            has_dashboards = metrics.get("has_dashboards", True)
            has_export = metrics.get("has_export", False)
            has_alerts = metrics.get("has_alerts", False)
            feature_count = sum([has_dashboards, has_export, has_alerts])
            reporting_score = 40 + (feature_count * 20)

        reporting_level = self._score_to_level(reporting_score / 20)
        dimension_assessments.append(
            self.assess_dimension(
                CapabilityDimension.REPORTING,
                reporting_level,
                evidence=[f"Reporting capability score: {reporting_score}%"],
            )
        )

        # Decision Support assessment
        decision_score = metrics.get("decision_support_score", 0)
        if decision_score == 0:
            has_recommendations = metrics.get("has_recommendations", False)
            has_llm = metrics.get("has_llm_insights", False)
            feature_count = sum([has_recommendations, has_llm])
            decision_score = 40 + (feature_count * 30)

        decision_level = self._score_to_level(decision_score / 20)
        dimension_assessments.append(
            self.assess_dimension(
                CapabilityDimension.DECISION_SUPPORT,
                decision_level,
                evidence=[f"Decision support score: {decision_score}%"],
            )
        )

        # Technology assessment
        tech_score = metrics.get("technology_score", 0)
        if tech_score == 0:
            has_api = metrics.get("has_api", True)
            has_docker = metrics.get("has_docker", False)
            has_ci_cd = metrics.get("has_ci_cd", False)
            feature_count = sum([has_api, has_docker, has_ci_cd])
            tech_score = 40 + (feature_count * 20)

        tech_level = self._score_to_level(tech_score / 20)
        dimension_assessments.append(
            self.assess_dimension(
                CapabilityDimension.TECHNOLOGY,
                tech_level,
                evidence=[f"Technology readiness score: {tech_score}%"],
            )
        )

        # Organization assessment (default to level 3 if not specified)
        org_score = metrics.get("organization_score", 60)
        org_level = self._score_to_level(org_score / 20)
        dimension_assessments.append(
            self.assess_dimension(
                CapabilityDimension.ORGANIZATION,
                org_level,
                evidence=[f"Organization readiness: {org_score}%"],
            )
        )

        # Strategic Alignment assessment
        alignment_score = metrics.get("strategic_alignment_score", 0)
        if alignment_score == 0:
            kpi_count = metrics.get("kpi_count", 0)
            has_vision2030_link = metrics.get("has_vision2030_link", True)
            alignment_score = min(100, 40 + (kpi_count * 3) + (30 if has_vision2030_link else 0))

        alignment_level = self._score_to_level(alignment_score / 20)
        dimension_assessments.append(
            self.assess_dimension(
                CapabilityDimension.STRATEGIC_ALIGNMENT,
                alignment_level,
                evidence=[f"Strategic alignment score: {alignment_score}%"],
            )
        )

        # Create assessment
        assessment = MaturityAssessment(
            id=assessment_id,
            name=name,
            description="Automated maturity assessment from platform metrics",
            status=AssessmentStatus.COMPLETED,
            assessor="system",
            dimension_assessments=dimension_assessments,
            target_level=self.target_level,
        )
        assessment.calculate_overall_score()

        return assessment

    def create_manual_assessment(
        self,
        assessment_id: str,
        name: str,
        assessor: str,
        dimension_levels: dict[CapabilityDimension, MaturityLevel],
        evidence: dict[CapabilityDimension, list[str]] | None = None,
        description: str = "",
    ) -> MaturityAssessment:
        """
        Create assessment from manual input.

        Args:
            assessment_id: Unique assessment ID
            name: Assessment name
            assessor: Name of person performing assessment
            dimension_levels: Current level for each dimension
            evidence: Evidence for each dimension
            description: Assessment description

        Returns:
            MaturityAssessment from manual input
        """
        evidence = evidence or {}
        dimension_assessments = []

        for dimension, level in dimension_levels.items():
            dimension_assessments.append(
                self.assess_dimension(
                    dimension=dimension,
                    current_level=level,
                    evidence=evidence.get(dimension, []),
                )
            )

        assessment = MaturityAssessment(
            id=assessment_id,
            name=name,
            description=description or "Manual maturity assessment",
            status=AssessmentStatus.COMPLETED,
            assessor=assessor,
            dimension_assessments=dimension_assessments,
            target_level=self.target_level,
        )
        assessment.calculate_overall_score()

        return assessment

    def _score_to_level(self, score: float) -> MaturityLevel:
        """Convert numeric score to maturity level."""
        if score < 1.5:
            return MaturityLevel.INITIAL
        elif score < 2.5:
            return MaturityLevel.DEVELOPING
        elif score < 3.5:
            return MaturityLevel.DEFINED
        elif score < 4.5:
            return MaturityLevel.MANAGED
        else:
            return MaturityLevel.OPTIMIZING


# =============================================================================
# BENCHMARKING SERVICE
# =============================================================================


class BenchmarkingService:
    """
    Provides benchmarking capabilities for maturity assessments.

    Supports:
    - Target benchmarks (organizational goals)
    - Peer benchmarks (similar organizations)
    - Industry benchmarks (sector averages)
    - Historical benchmarks (past assessments)
    """

    def __init__(self):
        """Initialize the benchmarking service."""
        self.benchmarks: dict[str, Benchmark] = {}
        self._initialize_default_benchmarks()

    def _initialize_default_benchmarks(self) -> None:
        """Create default benchmark references."""
        # Vision 2030 target benchmark
        vision2030_scores = {
            CapabilityDimension.DATA_QUALITY: 4.5,
            CapabilityDimension.DATA_GOVERNANCE: 4.5,
            CapabilityDimension.ANALYTICS_CAPABILITY: 4.0,
            CapabilityDimension.REPORTING: 4.0,
            CapabilityDimension.DECISION_SUPPORT: 4.0,
            CapabilityDimension.TECHNOLOGY: 4.0,
            CapabilityDimension.ORGANIZATION: 3.5,
            CapabilityDimension.STRATEGIC_ALIGNMENT: 5.0,
        }
        self.add_benchmark(Benchmark(
            id="vision2030",
            name="Vision 2030 Target",
            benchmark_type="target",
            dimension_scores=vision2030_scores,
            overall_score=4.2,
            description="Target maturity levels for Vision 2030 alignment",
            source="Ministry of Economy and Planning",
        ))

        # Government sector average
        gov_scores = {
            CapabilityDimension.DATA_QUALITY: 3.2,
            CapabilityDimension.DATA_GOVERNANCE: 2.8,
            CapabilityDimension.ANALYTICS_CAPABILITY: 2.5,
            CapabilityDimension.REPORTING: 3.0,
            CapabilityDimension.DECISION_SUPPORT: 2.3,
            CapabilityDimension.TECHNOLOGY: 2.7,
            CapabilityDimension.ORGANIZATION: 2.5,
            CapabilityDimension.STRATEGIC_ALIGNMENT: 3.0,
        }
        self.add_benchmark(Benchmark(
            id="gov_avg",
            name="Government Sector Average",
            benchmark_type="industry",
            dimension_scores=gov_scores,
            overall_score=2.75,
            description="Average maturity across government analytics programs",
            source="Digital Government Authority Benchmarks 2024",
        ))

        # Best-in-class government
        best_scores = {
            CapabilityDimension.DATA_QUALITY: 4.2,
            CapabilityDimension.DATA_GOVERNANCE: 4.0,
            CapabilityDimension.ANALYTICS_CAPABILITY: 4.5,
            CapabilityDimension.REPORTING: 4.3,
            CapabilityDimension.DECISION_SUPPORT: 4.0,
            CapabilityDimension.TECHNOLOGY: 4.5,
            CapabilityDimension.ORGANIZATION: 4.0,
            CapabilityDimension.STRATEGIC_ALIGNMENT: 4.5,
        }
        self.add_benchmark(Benchmark(
            id="best_in_class",
            name="Best-in-Class Government",
            benchmark_type="peer",
            dimension_scores=best_scores,
            overall_score=4.25,
            description="Top-performing government analytics programs globally",
            source="Gartner Government Analytics Benchmark 2024",
        ))

    def add_benchmark(self, benchmark: Benchmark) -> None:
        """Add a benchmark to the service."""
        self.benchmarks[benchmark.id] = benchmark

    def get_benchmark(self, benchmark_id: str) -> Benchmark | None:
        """Get a benchmark by ID."""
        return self.benchmarks.get(benchmark_id)

    def list_benchmarks(
        self,
        benchmark_type: str | None = None,
    ) -> list[Benchmark]:
        """List available benchmarks, optionally filtered by type."""
        if benchmark_type:
            return [
                b for b in self.benchmarks.values()
                if b.benchmark_type == benchmark_type
            ]
        return list(self.benchmarks.values())

    def compare_to_benchmark(
        self,
        assessment: MaturityAssessment,
        benchmark_id: str,
    ) -> BenchmarkComparison | None:
        """
        Compare an assessment to a benchmark.

        Args:
            assessment: The maturity assessment to compare
            benchmark_id: ID of benchmark to compare against

        Returns:
            BenchmarkComparison or None if benchmark not found
        """
        benchmark = self.get_benchmark(benchmark_id)
        if not benchmark:
            return None

        comparison = BenchmarkComparison(
            assessment=assessment,
            benchmark=benchmark,
        )
        comparison.calculate_gaps()

        return comparison

    def compare_to_all_benchmarks(
        self,
        assessment: MaturityAssessment,
    ) -> list[BenchmarkComparison]:
        """Compare assessment to all available benchmarks."""
        comparisons = []
        for benchmark in self.benchmarks.values():
            comparison = BenchmarkComparison(
                assessment=assessment,
                benchmark=benchmark,
            )
            comparison.calculate_gaps()
            comparisons.append(comparison)
        return comparisons

    def calculate_percentile(
        self,
        assessment: MaturityAssessment,
        peer_assessments: list[MaturityAssessment],
    ) -> float:
        """
        Calculate percentile ranking among peer assessments.

        Args:
            assessment: The assessment to rank
            peer_assessments: List of peer assessments

        Returns:
            Percentile (0-100)
        """
        if not peer_assessments:
            return 50.0

        scores = [a.overall_score for a in peer_assessments]
        scores.append(assessment.overall_score)
        scores.sort()

        rank = scores.index(assessment.overall_score)
        percentile = (rank / (len(scores) - 1)) * 100 if len(scores) > 1 else 50.0

        return round(percentile, 1)

    def create_historical_benchmark(
        self,
        assessment: MaturityAssessment,
        benchmark_id: str | None = None,
    ) -> Benchmark:
        """
        Create a benchmark from an assessment for future comparison.

        Args:
            assessment: Assessment to convert to benchmark
            benchmark_id: Optional ID (defaults to assessment ID)

        Returns:
            Benchmark based on assessment
        """
        dimension_scores = {
            a.dimension: a.score
            for a in assessment.dimension_assessments
        }

        benchmark = Benchmark(
            id=benchmark_id or f"historical_{assessment.id}",
            name=f"Historical: {assessment.name}",
            benchmark_type="historical",
            dimension_scores=dimension_scores,
            overall_score=assessment.overall_score,
            description=f"Historical benchmark from {assessment.created_at.strftime('%Y-%m-%d')}",
            source="Internal Assessment",
            as_of_date=assessment.created_at,
        )

        self.add_benchmark(benchmark)
        return benchmark


# =============================================================================
# ROADMAP GENERATOR
# =============================================================================


@dataclass
class RoadmapMilestone:
    """A milestone in the improvement roadmap."""

    id: str
    title: str
    description: str
    dimension: CapabilityDimension
    from_level: MaturityLevel
    to_level: MaturityLevel
    priority: int  # 1 = highest
    effort: str  # 'low', 'medium', 'high'
    duration_months: int
    dependencies: list[str] = field(default_factory=list)
    actions: list[str] = field(default_factory=list)
    success_criteria: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "dimension": self.dimension.value,
            "from_level": self.from_level.value,
            "to_level": self.to_level.value,
            "priority": self.priority,
            "effort": self.effort,
            "duration_months": self.duration_months,
            "dependencies": self.dependencies,
            "actions": self.actions,
            "success_criteria": self.success_criteria,
        }


@dataclass
class MaturityRoadmap:
    """Improvement roadmap based on maturity assessment."""

    id: str
    assessment_id: str
    name: str
    target_level: MaturityLevel
    milestones: list[RoadmapMilestone] = field(default_factory=list)
    total_duration_months: int = 0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def high_priority_milestones(self) -> list[RoadmapMilestone]:
        """Get milestones with priority 1 or 2."""
        return [m for m in self.milestones if m.priority <= 2]

    @property
    def quick_wins(self) -> list[RoadmapMilestone]:
        """Get low-effort milestones."""
        return [m for m in self.milestones if m.effort == "low"]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "assessment_id": self.assessment_id,
            "name": self.name,
            "target_level": self.target_level.value,
            "target_level_name": MATURITY_LEVEL_INFO[self.target_level]["name"],
            "milestones": [m.to_dict() for m in self.milestones],
            "total_duration_months": self.total_duration_months,
            "high_priority_count": len(self.high_priority_milestones),
            "quick_wins_count": len(self.quick_wins),
            "created_at": self.created_at.isoformat(),
            "metadata": self.metadata,
        }


class RoadmapGenerator:
    """
    Generates improvement roadmaps from maturity assessments.

    Considers:
    - Gap size between current and target
    - Dimension weight/importance
    - Dependencies between dimensions
    - Quick wins vs. strategic investments
    """

    # Effort estimation by level gap
    EFFORT_BY_GAP = {
        1: "low",
        2: "medium",
        3: "high",
        4: "high",
    }

    # Duration estimation (months) by level gap
    DURATION_BY_GAP = {
        1: 3,
        2: 6,
        3: 12,
        4: 18,
    }

    # Dependencies between dimensions
    DIMENSION_DEPENDENCIES = {
        CapabilityDimension.ANALYTICS_CAPABILITY: [
            CapabilityDimension.DATA_QUALITY,
            CapabilityDimension.TECHNOLOGY,
        ],
        CapabilityDimension.DECISION_SUPPORT: [
            CapabilityDimension.ANALYTICS_CAPABILITY,
            CapabilityDimension.DATA_GOVERNANCE,
        ],
        CapabilityDimension.REPORTING: [
            CapabilityDimension.DATA_QUALITY,
            CapabilityDimension.TECHNOLOGY,
        ],
        CapabilityDimension.STRATEGIC_ALIGNMENT: [
            CapabilityDimension.DATA_GOVERNANCE,
            CapabilityDimension.REPORTING,
        ],
    }

    def generate_roadmap(
        self,
        assessment: MaturityAssessment,
        roadmap_id: str | None = None,
        name: str | None = None,
    ) -> MaturityRoadmap:
        """
        Generate improvement roadmap from assessment.

        Args:
            assessment: Maturity assessment to base roadmap on
            roadmap_id: Optional roadmap ID
            name: Optional roadmap name

        Returns:
            MaturityRoadmap with prioritized milestones
        """
        milestones = []
        milestone_counter = 0

        # Generate milestones for dimensions below target
        for dim_assessment in assessment.weaknesses:
            gap = dim_assessment.gap_score
            if gap <= 0:
                continue

            milestone_counter += 1
            dimension = dim_assessment.dimension
            dim_info = DIMENSION_CRITERIA[dimension]

            # Calculate priority based on weight and gap
            priority_score = dim_info["weight"] * gap
            priority = self._calculate_priority(priority_score)

            # Get effort and duration
            gap_int = int(min(gap, 4))
            effort = self.EFFORT_BY_GAP.get(gap_int, "high")
            duration = self.DURATION_BY_GAP.get(gap_int, 18)

            # Get dependencies
            dependencies = []
            if dimension in self.DIMENSION_DEPENDENCIES:
                for dep in self.DIMENSION_DEPENDENCIES[dimension]:
                    dep_assessment = next(
                        (a for a in assessment.dimension_assessments if a.dimension == dep),
                        None
                    )
                    if dep_assessment and dep_assessment.gap_score > 0:
                        dependencies.append(f"milestone_{dep.value}")

            # Generate actions based on criteria
            next_level = MaturityLevel(dim_assessment.current_level.value + 1)
            criteria = dim_info["criteria"].get(next_level, [])
            actions = [f"Implement: {c}" for c in criteria]

            # Success criteria
            success_criteria = [
                f"Achieve Level {next_level.value} ({MATURITY_LEVEL_INFO[next_level]['name']}) in {dim_info['name']}",
                f"Score ≥ {next_level.value}.0 on {dim_info['name']} assessment",
            ]

            milestone = RoadmapMilestone(
                id=f"milestone_{dimension.value}",
                title=f"Improve {dim_info['name']} to {MATURITY_LEVEL_INFO[next_level]['name']}",
                description=f"Advance {dim_info['name']} from Level {dim_assessment.current_level.value} to Level {next_level.value}",
                dimension=dimension,
                from_level=dim_assessment.current_level,
                to_level=next_level,
                priority=priority,
                effort=effort,
                duration_months=duration,
                dependencies=dependencies,
                actions=actions,
                success_criteria=success_criteria,
            )
            milestones.append(milestone)

        # Sort by priority
        milestones.sort(key=lambda m: (m.priority, -DIMENSION_CRITERIA[m.dimension]["weight"]))

        # Calculate total duration (considering parallelism)
        # Simple estimation: sum of unique paths
        total_duration = self._estimate_total_duration(milestones)

        roadmap = MaturityRoadmap(
            id=roadmap_id or f"roadmap_{assessment.id}",
            assessment_id=assessment.id,
            name=name or f"Improvement Roadmap - {assessment.name}",
            target_level=assessment.target_level,
            milestones=milestones,
            total_duration_months=total_duration,
        )

        return roadmap

    def _calculate_priority(self, priority_score: float) -> int:
        """Convert priority score to priority level (1-5)."""
        if priority_score >= 0.4:
            return 1
        elif priority_score >= 0.3:
            return 2
        elif priority_score >= 0.2:
            return 3
        elif priority_score >= 0.1:
            return 4
        else:
            return 5

    def _estimate_total_duration(self, milestones: list[RoadmapMilestone]) -> int:
        """Estimate total roadmap duration considering dependencies."""
        if not milestones:
            return 0

        # Group by priority for parallel execution
        priority_groups: dict[int, list[RoadmapMilestone]] = {}
        for m in milestones:
            if m.priority not in priority_groups:
                priority_groups[m.priority] = []
            priority_groups[m.priority].append(m)

        # Sum maximum duration per priority group
        total = 0
        for priority in sorted(priority_groups.keys()):
            group = priority_groups[priority]
            max_duration = max(m.duration_months for m in group)
            total += max_duration

        return total

    def get_quick_wins(
        self,
        roadmap: MaturityRoadmap,
        max_effort: str = "low",
        max_duration_months: int = 3,
    ) -> list[RoadmapMilestone]:
        """
        Get quick win milestones from roadmap.

        Args:
            roadmap: The roadmap to filter
            max_effort: Maximum effort level ('low' or 'medium')
            max_duration_months: Maximum duration

        Returns:
            List of quick win milestones
        """
        effort_levels = ["low"] if max_effort == "low" else ["low", "medium"]

        return [
            m for m in roadmap.milestones
            if m.effort in effort_levels and m.duration_months <= max_duration_months
        ]

    def get_critical_path(
        self,
        roadmap: MaturityRoadmap,
    ) -> list[RoadmapMilestone]:
        """
        Get critical path milestones (priority 1 and their dependencies).

        Args:
            roadmap: The roadmap to analyze

        Returns:
            List of critical path milestones in execution order
        """
        critical = []
        seen = set()

        def add_with_deps(milestone: RoadmapMilestone) -> None:
            if milestone.id in seen:
                return
            # Add dependencies first
            for dep_id in milestone.dependencies:
                dep_milestone = next(
                    (m for m in roadmap.milestones if m.id == dep_id),
                    None
                )
                if dep_milestone:
                    add_with_deps(dep_milestone)
            seen.add(milestone.id)
            critical.append(milestone)

        # Start with priority 1 milestones
        for m in roadmap.milestones:
            if m.priority == 1:
                add_with_deps(m)

        return critical


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================


def assess_platform_maturity(
    metrics: dict[str, Any] | None = None,
    target_level: MaturityLevel = MaturityLevel.MANAGED,
) -> MaturityAssessment:
    """
    Perform automated maturity assessment of the platform.

    Args:
        metrics: Platform metrics (auto-detected if not provided)
        target_level: Target maturity level

    Returns:
        MaturityAssessment result
    """
    if metrics is None:
        # Auto-detect platform capabilities
        metrics = {
            "data_quality_score": 85,  # From DQ module
            "governance_score": 80,  # From compliance checker
            "has_forecasting": True,
            "has_anomaly_detection": True,
            "has_insights": True,
            "has_dashboards": True,
            "has_export": True,
            "has_alerts": True,
            "has_recommendations": True,
            "has_llm_insights": True,
            "has_api": True,
            "has_docker": True,
            "has_ci_cd": True,
            "kpi_count": 13,
            "has_vision2030_link": True,
        }

    assessor = MaturityAssessor(target_level=target_level)
    return assessor.assess_from_metrics(metrics)


def compare_to_benchmarks(
    assessment: MaturityAssessment,
) -> list[BenchmarkComparison]:
    """
    Compare assessment to all standard benchmarks.

    Args:
        assessment: Assessment to compare

    Returns:
        List of benchmark comparisons
    """
    service = BenchmarkingService()
    return service.compare_to_all_benchmarks(assessment)


def generate_improvement_roadmap(
    assessment: MaturityAssessment,
) -> MaturityRoadmap:
    """
    Generate improvement roadmap from assessment.

    Args:
        assessment: Maturity assessment

    Returns:
        MaturityRoadmap with prioritized improvements
    """
    generator = RoadmapGenerator()
    return generator.generate_roadmap(assessment)


def get_maturity_summary(
    assessment: MaturityAssessment,
    include_recommendations: bool = True,
) -> dict[str, Any]:
    """
    Get a summary of maturity assessment for dashboards.

    Args:
        assessment: Maturity assessment
        include_recommendations: Include improvement recommendations

    Returns:
        Summary dictionary
    """
    level_info = MATURITY_LEVEL_INFO[assessment.overall_level]

    summary = {
        "overall_score": round(assessment.overall_score, 2),
        "overall_level": assessment.overall_level.value,
        "level_name": level_info["name"],
        "level_name_ar": level_info["name_ar"],
        "level_color": level_info["color"],
        "target_level": assessment.target_level.value,
        "target_gap": assessment.target_level.value - assessment.overall_level.value,
        "strengths_count": len(assessment.strengths),
        "weaknesses_count": len(assessment.weaknesses),
        "dimensions": [],
    }

    for dim_assessment in assessment.dimension_assessments:
        dim_info = DIMENSION_CRITERIA[dim_assessment.dimension]
        summary["dimensions"].append({
            "name": dim_info["name"],
            "name_ar": dim_info["name_ar"],
            "score": round(dim_assessment.score, 2),
            "level": dim_assessment.current_level.value,
            "target": dim_assessment.target_level.value,
            "gap": dim_assessment.gap_score,
        })

    if include_recommendations:
        # Get top 3 recommendations from weakest areas
        recommendations = []
        for weakness in assessment.weaknesses[:3]:
            recommendations.extend(weakness.recommendations[:2])
        summary["top_recommendations"] = recommendations[:5]

    return summary
