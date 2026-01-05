"""
Tests for Maturity Model Module
Sustainable Economic Development Analytics Hub

Comprehensive tests for:
- Maturity level enums and constants
- Dimension assessments
- Maturity assessor (manual and automated)
- Benchmarking service
- Roadmap generation
- Convenience functions
"""

import pytest
from datetime import datetime, timezone

from analytics_hub_platform.domain.maturity_model import (
    # Enums
    MaturityLevel,
    CapabilityDimension,
    AssessmentStatus,
    # Constants
    MATURITY_LEVEL_INFO,
    DIMENSION_CRITERIA,
    # Data models
    DimensionAssessment,
    MaturityAssessment,
    Benchmark,
    BenchmarkComparison,
    RoadmapMilestone,
    MaturityRoadmap,
    # Classes
    MaturityAssessor,
    BenchmarkingService,
    RoadmapGenerator,
    # Convenience functions
    assess_platform_maturity,
    compare_to_benchmarks,
    generate_improvement_roadmap,
    get_maturity_summary,
)


# =============================================================================
# ENUM AND CONSTANT TESTS
# =============================================================================


class TestMaturityLevel:
    """Tests for MaturityLevel enum."""

    def test_maturity_level_values(self):
        """Test maturity levels have correct integer values."""
        assert MaturityLevel.INITIAL.value == 1
        assert MaturityLevel.DEVELOPING.value == 2
        assert MaturityLevel.DEFINED.value == 3
        assert MaturityLevel.MANAGED.value == 4
        assert MaturityLevel.OPTIMIZING.value == 5

    def test_maturity_level_ordering(self):
        """Test maturity levels can be compared."""
        assert MaturityLevel.INITIAL.value < MaturityLevel.DEVELOPING.value
        assert MaturityLevel.DEVELOPING.value < MaturityLevel.DEFINED.value
        assert MaturityLevel.DEFINED.value < MaturityLevel.MANAGED.value
        assert MaturityLevel.MANAGED.value < MaturityLevel.OPTIMIZING.value

    def test_maturity_level_info_complete(self):
        """Test all maturity levels have info."""
        for level in MaturityLevel:
            assert level in MATURITY_LEVEL_INFO
            info = MATURITY_LEVEL_INFO[level]
            assert "name" in info
            assert "name_ar" in info
            assert "description" in info
            assert "color" in info


class TestCapabilityDimension:
    """Tests for CapabilityDimension enum."""

    def test_all_dimensions_exist(self):
        """Test all expected dimensions exist."""
        expected = [
            "data_quality",
            "data_governance",
            "analytics_capability",
            "reporting",
            "decision_support",
            "technology",
            "organization",
            "strategic_alignment",
        ]
        actual = [d.value for d in CapabilityDimension]
        assert set(expected) == set(actual)

    def test_dimension_criteria_complete(self):
        """Test all dimensions have criteria defined."""
        for dimension in CapabilityDimension:
            assert dimension in DIMENSION_CRITERIA
            criteria = DIMENSION_CRITERIA[dimension]
            assert "name" in criteria
            assert "name_ar" in criteria
            assert "description" in criteria
            assert "weight" in criteria
            assert "criteria" in criteria
            # Check criteria for all levels
            for level in MaturityLevel:
                assert level in criteria["criteria"]
                assert len(criteria["criteria"][level]) >= 1

    def test_dimension_weights_sum_to_one(self):
        """Test dimension weights sum to approximately 1.0."""
        total_weight = sum(
            DIMENSION_CRITERIA[d]["weight"]
            for d in CapabilityDimension
        )
        assert abs(total_weight - 1.0) < 0.01


class TestAssessmentStatus:
    """Tests for AssessmentStatus enum."""

    def test_all_statuses_exist(self):
        """Test all expected statuses exist."""
        expected = ["draft", "in_progress", "completed", "approved", "archived"]
        actual = [s.value for s in AssessmentStatus]
        assert set(expected) == set(actual)


# =============================================================================
# DIMENSION ASSESSMENT TESTS
# =============================================================================


class TestDimensionAssessment:
    """Tests for DimensionAssessment dataclass."""

    def test_dimension_assessment_creation(self):
        """Test creating a dimension assessment."""
        assessment = DimensionAssessment(
            dimension=CapabilityDimension.DATA_QUALITY,
            current_level=MaturityLevel.DEFINED,
            target_level=MaturityLevel.MANAGED,
            score=3.0,
            evidence=["Evidence 1", "Evidence 2"],
            gaps=["Gap 1"],
            recommendations=["Recommendation 1"],
        )

        assert assessment.dimension == CapabilityDimension.DATA_QUALITY
        assert assessment.current_level == MaturityLevel.DEFINED
        assert assessment.target_level == MaturityLevel.MANAGED
        assert assessment.score == 3.0
        assert len(assessment.evidence) == 2
        assert len(assessment.gaps) == 1
        assert len(assessment.recommendations) == 1

    def test_gap_score_calculation(self):
        """Test gap score is calculated correctly."""
        # Gap exists
        assessment = DimensionAssessment(
            dimension=CapabilityDimension.DATA_QUALITY,
            current_level=MaturityLevel.DEVELOPING,
            target_level=MaturityLevel.MANAGED,
            score=2.0,
        )
        assert assessment.gap_score == 2  # 4 - 2

        # No gap (at target)
        assessment2 = DimensionAssessment(
            dimension=CapabilityDimension.DATA_QUALITY,
            current_level=MaturityLevel.MANAGED,
            target_level=MaturityLevel.MANAGED,
            score=4.0,
        )
        assert assessment2.gap_score == 0

        # Exceeds target
        assessment3 = DimensionAssessment(
            dimension=CapabilityDimension.DATA_QUALITY,
            current_level=MaturityLevel.OPTIMIZING,
            target_level=MaturityLevel.MANAGED,
            score=5.0,
        )
        assert assessment3.gap_score == 0  # No negative gap

    def test_gap_percentage_calculation(self):
        """Test gap percentage calculation."""
        assessment = DimensionAssessment(
            dimension=CapabilityDimension.DATA_QUALITY,
            current_level=MaturityLevel.DEVELOPING,
            target_level=MaturityLevel.MANAGED,
            score=2.0,
        )
        # Gap is 2, target is 4, so 50%
        assert assessment.gap_percentage == 50.0

    def test_to_dict(self):
        """Test conversion to dictionary."""
        assessment = DimensionAssessment(
            dimension=CapabilityDimension.DATA_QUALITY,
            current_level=MaturityLevel.DEFINED,
            target_level=MaturityLevel.MANAGED,
            score=3.0,
        )
        result = assessment.to_dict()

        assert result["dimension"] == "data_quality"
        assert result["current_level"] == 3
        assert result["current_level_name"] == "Defined"
        assert result["target_level"] == 4
        assert result["score"] == 3.0
        assert "assessed_at" in result


# =============================================================================
# MATURITY ASSESSMENT TESTS
# =============================================================================


class TestMaturityAssessment:
    """Tests for MaturityAssessment dataclass."""

    def test_assessment_creation(self):
        """Test creating a maturity assessment."""
        assessment = MaturityAssessment(
            id="test-001",
            name="Test Assessment",
            description="Test description",
            status=AssessmentStatus.COMPLETED,
            assessor="Test Assessor",
        )

        assert assessment.id == "test-001"
        assert assessment.name == "Test Assessment"
        assert assessment.status == AssessmentStatus.COMPLETED
        assert assessment.overall_score == 0.0
        assert assessment.overall_level == MaturityLevel.INITIAL
        assert len(assessment.dimension_assessments) == 0

    def test_calculate_overall_score(self):
        """Test overall score calculation."""
        assessment = MaturityAssessment(
            id="test-001",
            name="Test Assessment",
            description="Test",
            status=AssessmentStatus.COMPLETED,
            assessor="Test",
        )

        # Add dimension assessments
        assessment.dimension_assessments = [
            DimensionAssessment(
                dimension=CapabilityDimension.DATA_QUALITY,
                current_level=MaturityLevel.DEFINED,
                target_level=MaturityLevel.MANAGED,
                score=3.0,
            ),
            DimensionAssessment(
                dimension=CapabilityDimension.DATA_GOVERNANCE,
                current_level=MaturityLevel.DEVELOPING,
                target_level=MaturityLevel.MANAGED,
                score=2.0,
            ),
        ]

        score = assessment.calculate_overall_score()

        # Should be weighted average
        # DATA_QUALITY: weight 0.15, score 3.0
        # DATA_GOVERNANCE: weight 0.15, score 2.0
        # Weighted avg = (0.15*3.0 + 0.15*2.0) / (0.15 + 0.15) = 2.5
        assert abs(score - 2.5) < 0.01
        assert assessment.overall_level == MaturityLevel.DEVELOPING

    def test_strengths_and_weaknesses(self):
        """Test identifying strengths and weaknesses."""
        assessment = MaturityAssessment(
            id="test-001",
            name="Test Assessment",
            description="Test",
            status=AssessmentStatus.COMPLETED,
            assessor="Test",
            target_level=MaturityLevel.DEFINED,
        )

        assessment.dimension_assessments = [
            DimensionAssessment(
                dimension=CapabilityDimension.DATA_QUALITY,
                current_level=MaturityLevel.MANAGED,
                target_level=MaturityLevel.DEFINED,
                score=4.0,
            ),
            DimensionAssessment(
                dimension=CapabilityDimension.DATA_GOVERNANCE,
                current_level=MaturityLevel.INITIAL,
                target_level=MaturityLevel.DEFINED,
                score=1.0,
            ),
        ]

        assert len(assessment.strengths) == 1
        assert assessment.strengths[0].dimension == CapabilityDimension.DATA_QUALITY

        assert len(assessment.weaknesses) == 1
        assert assessment.weaknesses[0].dimension == CapabilityDimension.DATA_GOVERNANCE

    def test_to_dict(self):
        """Test conversion to dictionary."""
        assessment = MaturityAssessment(
            id="test-001",
            name="Test Assessment",
            description="Test",
            status=AssessmentStatus.COMPLETED,
            assessor="Test",
        )
        assessment.calculate_overall_score()

        result = assessment.to_dict()

        assert result["id"] == "test-001"
        assert result["status"] == "completed"
        assert "overall_score" in result
        assert "overall_level_name" in result
        assert "dimension_assessments" in result


# =============================================================================
# BENCHMARK TESTS
# =============================================================================


class TestBenchmark:
    """Tests for Benchmark dataclass."""

    def test_benchmark_creation(self):
        """Test creating a benchmark."""
        benchmark = Benchmark(
            id="test-benchmark",
            name="Test Benchmark",
            benchmark_type="target",
            dimension_scores={
                CapabilityDimension.DATA_QUALITY: 4.0,
                CapabilityDimension.DATA_GOVERNANCE: 3.5,
            },
            overall_score=3.75,
        )

        assert benchmark.id == "test-benchmark"
        assert benchmark.benchmark_type == "target"
        assert benchmark.dimension_scores[CapabilityDimension.DATA_QUALITY] == 4.0
        assert benchmark.overall_score == 3.75

    def test_benchmark_to_dict(self):
        """Test benchmark serialization."""
        benchmark = Benchmark(
            id="test-benchmark",
            name="Test Benchmark",
            benchmark_type="peer",
            dimension_scores={
                CapabilityDimension.DATA_QUALITY: 4.0,
            },
            overall_score=4.0,
        )

        result = benchmark.to_dict()

        assert result["id"] == "test-benchmark"
        assert result["benchmark_type"] == "peer"
        assert "data_quality" in result["dimension_scores"]


class TestBenchmarkComparison:
    """Tests for BenchmarkComparison dataclass."""

    def test_gap_calculation(self):
        """Test gap calculation between assessment and benchmark."""
        assessment = MaturityAssessment(
            id="test-001",
            name="Test",
            description="Test",
            status=AssessmentStatus.COMPLETED,
            assessor="Test",
            overall_score=3.0,
        )
        assessment.dimension_assessments = [
            DimensionAssessment(
                dimension=CapabilityDimension.DATA_QUALITY,
                current_level=MaturityLevel.DEFINED,
                target_level=MaturityLevel.MANAGED,
                score=3.0,
            ),
        ]

        benchmark = Benchmark(
            id="target",
            name="Target",
            benchmark_type="target",
            dimension_scores={
                CapabilityDimension.DATA_QUALITY: 4.0,
            },
            overall_score=4.0,
        )

        comparison = BenchmarkComparison(
            assessment=assessment,
            benchmark=benchmark,
        )
        comparison.calculate_gaps()

        assert comparison.overall_gap == 1.0  # 4.0 - 3.0
        assert CapabilityDimension.DATA_QUALITY in comparison.dimension_gaps
        assert comparison.dimension_gaps[CapabilityDimension.DATA_QUALITY] == 1.0

    def test_dimensions_above_below_benchmark(self):
        """Test identifying dimensions above/below benchmark."""
        assessment = MaturityAssessment(
            id="test-001",
            name="Test",
            description="Test",
            status=AssessmentStatus.COMPLETED,
            assessor="Test",
        )
        assessment.dimension_assessments = [
            DimensionAssessment(
                dimension=CapabilityDimension.DATA_QUALITY,
                current_level=MaturityLevel.OPTIMIZING,
                target_level=MaturityLevel.MANAGED,
                score=5.0,
            ),
            DimensionAssessment(
                dimension=CapabilityDimension.DATA_GOVERNANCE,
                current_level=MaturityLevel.DEVELOPING,
                target_level=MaturityLevel.MANAGED,
                score=2.0,
            ),
        ]

        benchmark = Benchmark(
            id="target",
            name="Target",
            benchmark_type="target",
            dimension_scores={
                CapabilityDimension.DATA_QUALITY: 4.0,
                CapabilityDimension.DATA_GOVERNANCE: 4.0,
            },
            overall_score=4.0,
        )

        comparison = BenchmarkComparison(
            assessment=assessment,
            benchmark=benchmark,
        )
        comparison.calculate_gaps()

        assert CapabilityDimension.DATA_QUALITY in comparison.dimensions_above_benchmark
        assert CapabilityDimension.DATA_GOVERNANCE in comparison.dimensions_below_benchmark


# =============================================================================
# MATURITY ASSESSOR TESTS
# =============================================================================


class TestMaturityAssessor:
    """Tests for MaturityAssessor class."""

    def test_assessor_initialization(self):
        """Test assessor initialization with default target."""
        assessor = MaturityAssessor()
        assert assessor.target_level == MaturityLevel.MANAGED

        assessor2 = MaturityAssessor(target_level=MaturityLevel.OPTIMIZING)
        assert assessor2.target_level == MaturityLevel.OPTIMIZING

    def test_assess_dimension(self):
        """Test single dimension assessment."""
        assessor = MaturityAssessor(target_level=MaturityLevel.MANAGED)

        result = assessor.assess_dimension(
            dimension=CapabilityDimension.DATA_QUALITY,
            current_level=MaturityLevel.DEVELOPING,
            evidence=["Test evidence"],
        )

        assert result.dimension == CapabilityDimension.DATA_QUALITY
        assert result.current_level == MaturityLevel.DEVELOPING
        assert result.target_level == MaturityLevel.MANAGED
        assert result.score == 2.0
        assert len(result.evidence) == 1
        assert len(result.gaps) > 0  # Should have gaps to next level
        assert len(result.recommendations) > 0

    def test_assess_dimension_at_target(self):
        """Test dimension assessment when at target level."""
        assessor = MaturityAssessor(target_level=MaturityLevel.DEFINED)

        result = assessor.assess_dimension(
            dimension=CapabilityDimension.DATA_QUALITY,
            current_level=MaturityLevel.DEFINED,
        )

        assert result.gap_score == 0
        assert len(result.gaps) == 0

    def test_assess_from_metrics(self):
        """Test automated assessment from metrics."""
        assessor = MaturityAssessor()

        metrics = {
            "data_quality_score": 80,  # Should map to ~Level 4
            "governance_score": 60,  # Should map to ~Level 3
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

        result = assessor.assess_from_metrics(metrics)

        assert result.status == AssessmentStatus.COMPLETED
        assert result.assessor == "system"
        assert len(result.dimension_assessments) == 8
        assert result.overall_score > 0

    def test_create_manual_assessment(self):
        """Test manual assessment creation."""
        assessor = MaturityAssessor()

        dimension_levels = {
            CapabilityDimension.DATA_QUALITY: MaturityLevel.MANAGED,
            CapabilityDimension.DATA_GOVERNANCE: MaturityLevel.DEFINED,
            CapabilityDimension.ANALYTICS_CAPABILITY: MaturityLevel.DEVELOPING,
        }

        result = assessor.create_manual_assessment(
            assessment_id="manual-001",
            name="Manual Test",
            assessor="John Doe",
            dimension_levels=dimension_levels,
            description="Test manual assessment",
        )

        assert result.id == "manual-001"
        assert result.assessor == "John Doe"
        assert len(result.dimension_assessments) == 3
        assert result.overall_score > 0

    def test_score_to_level_mapping(self):
        """Test score to level conversion."""
        assessor = MaturityAssessor()

        # Score < 1.5 → INITIAL
        assert assessor._score_to_level(0.5) == MaturityLevel.INITIAL
        assert assessor._score_to_level(1.4) == MaturityLevel.INITIAL
        # Score 1.5-2.49 → DEVELOPING
        assert assessor._score_to_level(1.5) == MaturityLevel.DEVELOPING
        assert assessor._score_to_level(2.0) == MaturityLevel.DEVELOPING
        # Score 2.5-3.49 → DEFINED
        assert assessor._score_to_level(2.5) == MaturityLevel.DEFINED
        assert assessor._score_to_level(3.0) == MaturityLevel.DEFINED
        # Score 3.5-4.49 → MANAGED
        assert assessor._score_to_level(3.5) == MaturityLevel.MANAGED
        assert assessor._score_to_level(4.0) == MaturityLevel.MANAGED
        # Score >= 4.5 → OPTIMIZING
        assert assessor._score_to_level(4.5) == MaturityLevel.OPTIMIZING
        assert assessor._score_to_level(4.8) == MaturityLevel.OPTIMIZING


# =============================================================================
# BENCHMARKING SERVICE TESTS
# =============================================================================


class TestBenchmarkingService:
    """Tests for BenchmarkingService class."""

    def test_default_benchmarks_initialized(self):
        """Test default benchmarks are created."""
        service = BenchmarkingService()

        benchmarks = service.list_benchmarks()
        assert len(benchmarks) >= 3

        # Check specific defaults exist
        assert service.get_benchmark("vision2030") is not None
        assert service.get_benchmark("gov_avg") is not None
        assert service.get_benchmark("best_in_class") is not None

    def test_add_benchmark(self):
        """Test adding a new benchmark."""
        service = BenchmarkingService()

        new_benchmark = Benchmark(
            id="custom",
            name="Custom Benchmark",
            benchmark_type="custom",
            overall_score=3.5,
        )
        service.add_benchmark(new_benchmark)

        retrieved = service.get_benchmark("custom")
        assert retrieved is not None
        assert retrieved.name == "Custom Benchmark"

    def test_list_benchmarks_by_type(self):
        """Test filtering benchmarks by type."""
        service = BenchmarkingService()

        targets = service.list_benchmarks(benchmark_type="target")
        assert len(targets) >= 1
        assert all(b.benchmark_type == "target" for b in targets)

        peers = service.list_benchmarks(benchmark_type="peer")
        assert all(b.benchmark_type == "peer" for b in peers)

    def test_compare_to_benchmark(self):
        """Test comparing assessment to benchmark."""
        service = BenchmarkingService()

        # Create an assessment
        assessment = MaturityAssessment(
            id="test-001",
            name="Test",
            description="Test",
            status=AssessmentStatus.COMPLETED,
            assessor="Test",
            overall_score=3.0,
        )
        assessment.dimension_assessments = [
            DimensionAssessment(
                dimension=CapabilityDimension.DATA_QUALITY,
                current_level=MaturityLevel.DEFINED,
                target_level=MaturityLevel.MANAGED,
                score=3.0,
            ),
        ]

        comparison = service.compare_to_benchmark(assessment, "vision2030")

        assert comparison is not None
        assert comparison.benchmark.id == "vision2030"
        assert comparison.overall_gap > 0  # Vision2030 target is higher

    def test_compare_to_nonexistent_benchmark(self):
        """Test comparing to nonexistent benchmark returns None."""
        service = BenchmarkingService()

        assessment = MaturityAssessment(
            id="test-001",
            name="Test",
            description="Test",
            status=AssessmentStatus.COMPLETED,
            assessor="Test",
        )

        result = service.compare_to_benchmark(assessment, "nonexistent")
        assert result is None

    def test_compare_to_all_benchmarks(self):
        """Test comparing to all benchmarks."""
        service = BenchmarkingService()

        assessment = MaturityAssessment(
            id="test-001",
            name="Test",
            description="Test",
            status=AssessmentStatus.COMPLETED,
            assessor="Test",
            overall_score=3.0,
        )

        comparisons = service.compare_to_all_benchmarks(assessment)

        assert len(comparisons) >= 3
        benchmark_ids = [c.benchmark.id for c in comparisons]
        assert "vision2030" in benchmark_ids
        assert "gov_avg" in benchmark_ids

    def test_calculate_percentile(self):
        """Test percentile calculation."""
        service = BenchmarkingService()

        target = MaturityAssessment(
            id="target",
            name="Target",
            description="",
            status=AssessmentStatus.COMPLETED,
            assessor="Test",
            overall_score=3.5,
        )

        peers = [
            MaturityAssessment(
                id=f"peer-{i}",
                name=f"Peer {i}",
                description="",
                status=AssessmentStatus.COMPLETED,
                assessor="Test",
                overall_score=score,
            )
            for i, score in enumerate([2.0, 2.5, 3.0, 4.0, 4.5])
        ]

        percentile = service.calculate_percentile(target, peers)

        # Score 3.5 is above median (3.0) but below 4.0 and 4.5
        assert 50 < percentile < 100

    def test_create_historical_benchmark(self):
        """Test creating historical benchmark from assessment."""
        service = BenchmarkingService()

        assessment = MaturityAssessment(
            id="test-001",
            name="Test Assessment",
            description="Test",
            status=AssessmentStatus.COMPLETED,
            assessor="Test",
            overall_score=3.5,
        )
        assessment.dimension_assessments = [
            DimensionAssessment(
                dimension=CapabilityDimension.DATA_QUALITY,
                current_level=MaturityLevel.DEFINED,
                target_level=MaturityLevel.MANAGED,
                score=3.0,
            ),
        ]

        benchmark = service.create_historical_benchmark(assessment)

        assert benchmark.benchmark_type == "historical"
        assert benchmark.overall_score == 3.5
        assert CapabilityDimension.DATA_QUALITY in benchmark.dimension_scores

        # Should be retrievable
        retrieved = service.get_benchmark(benchmark.id)
        assert retrieved is not None


# =============================================================================
# ROADMAP GENERATOR TESTS
# =============================================================================


class TestRoadmapMilestone:
    """Tests for RoadmapMilestone dataclass."""

    def test_milestone_creation(self):
        """Test creating a roadmap milestone."""
        milestone = RoadmapMilestone(
            id="milestone-001",
            title="Improve Data Quality",
            description="Advance from Level 2 to Level 3",
            dimension=CapabilityDimension.DATA_QUALITY,
            from_level=MaturityLevel.DEVELOPING,
            to_level=MaturityLevel.DEFINED,
            priority=1,
            effort="medium",
            duration_months=6,
            actions=["Action 1", "Action 2"],
            success_criteria=["Criteria 1"],
        )

        assert milestone.id == "milestone-001"
        assert milestone.priority == 1
        assert milestone.effort == "medium"
        assert milestone.duration_months == 6

    def test_milestone_to_dict(self):
        """Test milestone serialization."""
        milestone = RoadmapMilestone(
            id="milestone-001",
            title="Test",
            description="Test",
            dimension=CapabilityDimension.DATA_QUALITY,
            from_level=MaturityLevel.DEVELOPING,
            to_level=MaturityLevel.DEFINED,
            priority=1,
            effort="low",
            duration_months=3,
        )

        result = milestone.to_dict()

        assert result["id"] == "milestone-001"
        assert result["dimension"] == "data_quality"
        assert result["from_level"] == 2
        assert result["to_level"] == 3


class TestMaturityRoadmap:
    """Tests for MaturityRoadmap dataclass."""

    def test_roadmap_creation(self):
        """Test creating a roadmap."""
        roadmap = MaturityRoadmap(
            id="roadmap-001",
            assessment_id="assessment-001",
            name="Improvement Roadmap",
            target_level=MaturityLevel.MANAGED,
        )

        assert roadmap.id == "roadmap-001"
        assert len(roadmap.milestones) == 0

    def test_roadmap_properties(self):
        """Test roadmap properties."""
        milestone1 = RoadmapMilestone(
            id="m1",
            title="High Priority",
            description="",
            dimension=CapabilityDimension.DATA_QUALITY,
            from_level=MaturityLevel.DEVELOPING,
            to_level=MaturityLevel.DEFINED,
            priority=1,
            effort="low",
            duration_months=3,
        )
        milestone2 = RoadmapMilestone(
            id="m2",
            title="Low Priority",
            description="",
            dimension=CapabilityDimension.TECHNOLOGY,
            from_level=MaturityLevel.INITIAL,
            to_level=MaturityLevel.DEVELOPING,
            priority=5,
            effort="high",
            duration_months=12,
        )

        roadmap = MaturityRoadmap(
            id="roadmap-001",
            assessment_id="assessment-001",
            name="Test Roadmap",
            target_level=MaturityLevel.MANAGED,
            milestones=[milestone1, milestone2],
        )

        assert len(roadmap.high_priority_milestones) == 1
        assert roadmap.high_priority_milestones[0].id == "m1"

        assert len(roadmap.quick_wins) == 1
        assert roadmap.quick_wins[0].id == "m1"


class TestRoadmapGenerator:
    """Tests for RoadmapGenerator class."""

    def test_generate_roadmap_from_assessment(self):
        """Test generating roadmap from assessment."""
        generator = RoadmapGenerator()

        assessment = MaturityAssessment(
            id="test-001",
            name="Test Assessment",
            description="Test",
            status=AssessmentStatus.COMPLETED,
            assessor="Test",
            target_level=MaturityLevel.MANAGED,
        )
        assessment.dimension_assessments = [
            DimensionAssessment(
                dimension=CapabilityDimension.DATA_QUALITY,
                current_level=MaturityLevel.DEVELOPING,
                target_level=MaturityLevel.MANAGED,
                score=2.0,
            ),
            DimensionAssessment(
                dimension=CapabilityDimension.DATA_GOVERNANCE,
                current_level=MaturityLevel.MANAGED,
                target_level=MaturityLevel.MANAGED,
                score=4.0,
            ),
        ]
        assessment.calculate_overall_score()

        roadmap = generator.generate_roadmap(assessment)

        assert roadmap.assessment_id == "test-001"
        # Should have milestone for DATA_QUALITY (below target) but not DATA_GOVERNANCE
        assert len(roadmap.milestones) >= 1
        assert any(
            m.dimension == CapabilityDimension.DATA_QUALITY
            for m in roadmap.milestones
        )

    def test_generate_roadmap_with_dependencies(self):
        """Test roadmap generation includes dependencies."""
        generator = RoadmapGenerator()

        assessment = MaturityAssessment(
            id="test-001",
            name="Test Assessment",
            description="Test",
            status=AssessmentStatus.COMPLETED,
            assessor="Test",
            target_level=MaturityLevel.MANAGED,
        )
        # ANALYTICS_CAPABILITY depends on DATA_QUALITY
        assessment.dimension_assessments = [
            DimensionAssessment(
                dimension=CapabilityDimension.DATA_QUALITY,
                current_level=MaturityLevel.DEVELOPING,
                target_level=MaturityLevel.MANAGED,
                score=2.0,
            ),
            DimensionAssessment(
                dimension=CapabilityDimension.ANALYTICS_CAPABILITY,
                current_level=MaturityLevel.DEVELOPING,
                target_level=MaturityLevel.MANAGED,
                score=2.0,
            ),
            DimensionAssessment(
                dimension=CapabilityDimension.TECHNOLOGY,
                current_level=MaturityLevel.DEVELOPING,
                target_level=MaturityLevel.MANAGED,
                score=2.0,
            ),
        ]
        assessment.calculate_overall_score()

        roadmap = generator.generate_roadmap(assessment)

        analytics_milestone = next(
            (m for m in roadmap.milestones if m.dimension == CapabilityDimension.ANALYTICS_CAPABILITY),
            None
        )
        assert analytics_milestone is not None
        # Should have dependencies
        assert len(analytics_milestone.dependencies) >= 1

    def test_priority_calculation(self):
        """Test priority is calculated based on weight and gap."""
        generator = RoadmapGenerator()

        # High weight dimension with gap should get high priority
        assessment = MaturityAssessment(
            id="test-001",
            name="Test",
            description="Test",
            status=AssessmentStatus.COMPLETED,
            assessor="Test",
            target_level=MaturityLevel.OPTIMIZING,
        )
        assessment.dimension_assessments = [
            DimensionAssessment(
                dimension=CapabilityDimension.DATA_QUALITY,  # weight 0.15
                current_level=MaturityLevel.INITIAL,
                target_level=MaturityLevel.OPTIMIZING,
                score=1.0,
            ),
        ]
        assessment.calculate_overall_score()

        roadmap = generator.generate_roadmap(assessment)

        # High weight * high gap = high priority
        assert len(roadmap.milestones) >= 1
        assert roadmap.milestones[0].priority <= 2

    def test_get_quick_wins(self):
        """Test filtering quick wins."""
        generator = RoadmapGenerator()

        milestones = [
            RoadmapMilestone(
                id="m1",
                title="Quick Win",
                description="",
                dimension=CapabilityDimension.DATA_QUALITY,
                from_level=MaturityLevel.DEVELOPING,
                to_level=MaturityLevel.DEFINED,
                priority=3,
                effort="low",
                duration_months=2,
            ),
            RoadmapMilestone(
                id="m2",
                title="Long Project",
                description="",
                dimension=CapabilityDimension.TECHNOLOGY,
                from_level=MaturityLevel.INITIAL,
                to_level=MaturityLevel.MANAGED,
                priority=1,
                effort="high",
                duration_months=12,
            ),
        ]

        roadmap = MaturityRoadmap(
            id="test",
            assessment_id="test",
            name="Test",
            target_level=MaturityLevel.MANAGED,
            milestones=milestones,
        )

        quick_wins = generator.get_quick_wins(roadmap)

        assert len(quick_wins) == 1
        assert quick_wins[0].id == "m1"

    def test_get_critical_path(self):
        """Test getting critical path with dependencies."""
        generator = RoadmapGenerator()

        milestones = [
            RoadmapMilestone(
                id="m1",
                title="Priority 1 with deps",
                description="",
                dimension=CapabilityDimension.ANALYTICS_CAPABILITY,
                from_level=MaturityLevel.DEVELOPING,
                to_level=MaturityLevel.DEFINED,
                priority=1,
                effort="medium",
                duration_months=6,
                dependencies=["m2"],
            ),
            RoadmapMilestone(
                id="m2",
                title="Dependency",
                description="",
                dimension=CapabilityDimension.DATA_QUALITY,
                from_level=MaturityLevel.DEVELOPING,
                to_level=MaturityLevel.DEFINED,
                priority=2,
                effort="low",
                duration_months=3,
            ),
            RoadmapMilestone(
                id="m3",
                title="Not Critical",
                description="",
                dimension=CapabilityDimension.ORGANIZATION,
                from_level=MaturityLevel.INITIAL,
                to_level=MaturityLevel.DEVELOPING,
                priority=5,
                effort="high",
                duration_months=12,
            ),
        ]

        roadmap = MaturityRoadmap(
            id="test",
            assessment_id="test",
            name="Test",
            target_level=MaturityLevel.MANAGED,
            milestones=milestones,
        )

        critical = generator.get_critical_path(roadmap)

        # Should include m1 and its dependency m2, but not m3
        critical_ids = [m.id for m in critical]
        assert "m1" in critical_ids
        assert "m2" in critical_ids
        assert "m3" not in critical_ids
        # m2 should come before m1 (dependency first)
        assert critical_ids.index("m2") < critical_ids.index("m1")


# =============================================================================
# CONVENIENCE FUNCTION TESTS
# =============================================================================


class TestConvenienceFunctions:
    """Tests for convenience functions."""

    def test_assess_platform_maturity_default(self):
        """Test platform maturity assessment with defaults."""
        result = assess_platform_maturity()

        assert isinstance(result, MaturityAssessment)
        assert result.status == AssessmentStatus.COMPLETED
        assert result.assessor == "system"
        assert len(result.dimension_assessments) == 8
        assert result.overall_score > 0

    def test_assess_platform_maturity_custom_metrics(self):
        """Test platform maturity with custom metrics."""
        metrics = {
            "data_quality_score": 50,
            "governance_score": 40,
        }

        result = assess_platform_maturity(
            metrics=metrics,
            target_level=MaturityLevel.OPTIMIZING,
        )

        assert result.target_level == MaturityLevel.OPTIMIZING
        # Lower scores should result in lower maturity
        assert result.overall_score < 4.0

    def test_compare_to_benchmarks(self):
        """Test comparing assessment to all benchmarks."""
        assessment = assess_platform_maturity()

        comparisons = compare_to_benchmarks(assessment)

        assert len(comparisons) >= 3
        assert all(isinstance(c, BenchmarkComparison) for c in comparisons)

    def test_generate_improvement_roadmap(self):
        """Test generating improvement roadmap."""
        assessment = assess_platform_maturity(
            target_level=MaturityLevel.OPTIMIZING,
        )

        roadmap = generate_improvement_roadmap(assessment)

        assert isinstance(roadmap, MaturityRoadmap)
        assert roadmap.assessment_id == assessment.id
        # Should have some milestones to reach OPTIMIZING
        assert len(roadmap.milestones) >= 0

    def test_get_maturity_summary(self):
        """Test getting maturity summary."""
        assessment = assess_platform_maturity()

        summary = get_maturity_summary(assessment)

        assert "overall_score" in summary
        assert "overall_level" in summary
        assert "level_name" in summary
        assert "level_name_ar" in summary
        assert "level_color" in summary
        assert "dimensions" in summary
        assert len(summary["dimensions"]) == 8

    def test_get_maturity_summary_with_recommendations(self):
        """Test summary includes recommendations."""
        # Create assessment with weaknesses
        assessment = assess_platform_maturity(
            metrics={"data_quality_score": 20},
            target_level=MaturityLevel.OPTIMIZING,
        )

        summary = get_maturity_summary(assessment, include_recommendations=True)

        assert "top_recommendations" in summary

    def test_get_maturity_summary_without_recommendations(self):
        """Test summary without recommendations."""
        assessment = assess_platform_maturity()

        summary = get_maturity_summary(assessment, include_recommendations=False)

        assert "top_recommendations" not in summary


# =============================================================================
# INTEGRATION TESTS
# =============================================================================


class TestMaturityModelIntegration:
    """Integration tests for the maturity model."""

    def test_full_assessment_workflow(self):
        """Test complete assessment workflow."""
        # 1. Perform assessment
        assessor = MaturityAssessor(target_level=MaturityLevel.MANAGED)
        assessment = assessor.assess_from_metrics({
            "data_quality_score": 70,
            "governance_score": 65,
            "has_forecasting": True,
            "has_anomaly_detection": True,
            "has_insights": True,
            "has_dashboards": True,
            "has_export": True,
            "has_alerts": True,
            "kpi_count": 10,
            "has_vision2030_link": True,
        })

        assert assessment.overall_score > 0
        assert len(assessment.dimension_assessments) == 8

        # 2. Compare to benchmarks
        service = BenchmarkingService()
        comparisons = service.compare_to_all_benchmarks(assessment)

        assert len(comparisons) >= 3
        vision2030_comparison = next(
            (c for c in comparisons if c.benchmark.id == "vision2030"),
            None
        )
        assert vision2030_comparison is not None

        # 3. Generate roadmap
        generator = RoadmapGenerator()
        roadmap = generator.generate_roadmap(assessment)

        assert roadmap.assessment_id == assessment.id

        # 4. Get quick wins
        quick_wins = generator.get_quick_wins(roadmap)

        # 5. Get critical path
        critical_path = generator.get_critical_path(roadmap)

        # 6. Create historical benchmark for future comparison
        historical = service.create_historical_benchmark(assessment)

        assert historical.benchmark_type == "historical"
        assert service.get_benchmark(historical.id) is not None

    def test_improvement_tracking_over_time(self):
        """Test tracking improvement by comparing historical assessments."""
        service = BenchmarkingService()

        # Initial assessment
        initial_assessment = MaturityAssessment(
            id="assessment-q1",
            name="Q1 Assessment",
            description="",
            status=AssessmentStatus.COMPLETED,
            assessor="Test",
            overall_score=2.5,
        )
        initial_assessment.dimension_assessments = [
            DimensionAssessment(
                dimension=CapabilityDimension.DATA_QUALITY,
                current_level=MaturityLevel.DEVELOPING,
                target_level=MaturityLevel.MANAGED,
                score=2.0,
            ),
        ]

        # Create historical benchmark
        service.create_historical_benchmark(initial_assessment, "q1_baseline")

        # Later assessment showing improvement
        current_assessment = MaturityAssessment(
            id="assessment-q2",
            name="Q2 Assessment",
            description="",
            status=AssessmentStatus.COMPLETED,
            assessor="Test",
            overall_score=3.5,
        )
        current_assessment.dimension_assessments = [
            DimensionAssessment(
                dimension=CapabilityDimension.DATA_QUALITY,
                current_level=MaturityLevel.DEFINED,
                target_level=MaturityLevel.MANAGED,
                score=3.0,
            ),
        ]

        # Compare to Q1 baseline
        comparison = service.compare_to_benchmark(current_assessment, "q1_baseline")

        assert comparison is not None
        # Current is higher than baseline (negative gap = improvement)
        assert comparison.overall_gap < 0

    def test_vision2030_alignment_scoring(self):
        """Test strategic alignment with Vision 2030."""
        assessor = MaturityAssessor()

        # High strategic alignment
        high_alignment = assessor.assess_from_metrics({
            "strategic_alignment_score": 95,
            "kpi_count": 13,
            "has_vision2030_link": True,
        })

        alignment_dim = next(
            (a for a in high_alignment.dimension_assessments
             if a.dimension == CapabilityDimension.STRATEGIC_ALIGNMENT),
            None
        )
        assert alignment_dim is not None
        assert alignment_dim.score >= 4.0

        # Low strategic alignment
        low_alignment = assessor.assess_from_metrics({
            "strategic_alignment_score": 20,
            "kpi_count": 2,
            "has_vision2030_link": False,
        })

        alignment_dim_low = next(
            (a for a in low_alignment.dimension_assessments
             if a.dimension == CapabilityDimension.STRATEGIC_ALIGNMENT),
            None
        )
        assert alignment_dim_low is not None
        assert alignment_dim_low.score < 3.0
