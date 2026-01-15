"""
Tests for Export Utilities Module
Sustainable Economic Development Analytics Hub

Tests:
- CSV export
- PNG export (fallback handling)
- PDF generation
"""

import pytest
import pandas as pd

from analytics_hub_platform.utils.export_utils import (
    export_dataframe_to_csv,
    get_csv_download_link,
    generate_executive_brief_pdf,
    generate_simple_text_report,
    REPORTLAB_AVAILABLE,
    PLOTLY_AVAILABLE,
)


# =============================================================================
# CSV EXPORT TESTS
# =============================================================================


class TestCSVExport:
    """Tests for CSV export functionality."""

    @pytest.fixture
    def sample_dataframe(self) -> pd.DataFrame:
        """Create a sample DataFrame for testing."""
        return pd.DataFrame({
            "region": ["Riyadh", "Makkah", "Eastern"],
            "gdp_growth": [3.5, 2.8, 4.2],
            "unemployment": [11.2, 12.5, 10.0],
            "renewable_share": [12.5, 10.0, 15.0],
        })

    def test_export_csv_returns_bytes(self, sample_dataframe):
        """Test that CSV export returns bytes."""
        result = export_dataframe_to_csv(sample_dataframe)

        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_export_csv_contains_headers(self, sample_dataframe):
        """Test that CSV contains column headers."""
        result = export_dataframe_to_csv(sample_dataframe)
        content = result.decode("utf-8-sig")

        assert "region" in content
        assert "gdp_growth" in content
        assert "unemployment" in content

    def test_export_csv_contains_data(self, sample_dataframe):
        """Test that CSV contains data values."""
        result = export_dataframe_to_csv(sample_dataframe)
        content = result.decode("utf-8-sig")

        assert "Riyadh" in content
        assert "3.5" in content
        assert "12.5" in content

    def test_export_csv_with_index(self, sample_dataframe):
        """Test CSV export with index column."""
        result = export_dataframe_to_csv(sample_dataframe, include_index=True)
        content = result.decode("utf-8-sig")

        # Should have index column (first column will be empty header for index)
        lines = content.strip().split("\n")
        assert len(lines) == 4  # Header + 3 data rows

    def test_export_csv_without_index(self, sample_dataframe):
        """Test CSV export without index column."""
        result = export_dataframe_to_csv(sample_dataframe, include_index=False)
        content = result.decode("utf-8-sig")

        lines = content.strip().split("\n")
        first_line = lines[0]
        # First column should be 'region', not an index number
        assert first_line.startswith("region") or first_line.startswith("\ufeffregion")

    def test_export_empty_dataframe(self):
        """Test exporting empty DataFrame."""
        df = pd.DataFrame()
        result = export_dataframe_to_csv(df)

        assert isinstance(result, bytes)

    def test_csv_download_link_format(self, sample_dataframe):
        """Test that download link has correct HTML format."""
        link = get_csv_download_link(sample_dataframe, "test.csv", "Download")

        assert "<a href=" in link
        assert "data:file/csv;base64," in link
        assert 'download="test.csv"' in link
        assert "Download" in link


# =============================================================================
# PDF EXPORT TESTS
# =============================================================================


class TestPDFExport:
    """Tests for PDF export functionality."""

    def test_generate_pdf_returns_bytes(self):
        """Test that PDF generation returns bytes."""
        result = generate_executive_brief_pdf(
            title="Test Report",
            summary_metrics={"GDP Growth": "3.5%", "Unemployment": "11.2%"},
        )

        assert result is not None
        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_generate_pdf_with_all_sections(self):
        """Test PDF generation with all sections populated."""
        result = generate_executive_brief_pdf(
            title="Complete Test Report",
            date="2024-01-01",
            summary_metrics={
                "GDP Growth": "3.5%",
                "FDI": "45.2B SAR",
                "Renewable Share": "12.5%",
            },
            key_insights=[
                "Economic growth remains strong",
                "Unemployment trending downward",
                "Renewable energy adoption increasing",
            ],
            data_tables={
                "Regional Summary": pd.DataFrame({
                    "Region": ["Riyadh", "Makkah"],
                    "Score": [85, 78],
                })
            },
            recommendations=[
                "Continue investment in renewable energy",
                "Expand green jobs training programs",
            ],
        )

        assert result is not None
        assert len(result) > 0

    def test_generate_pdf_with_minimal_content(self):
        """Test PDF generation with minimal content."""
        result = generate_executive_brief_pdf(title="Minimal Report")

        assert result is not None
        assert len(result) > 0

    def test_generate_pdf_uses_current_date_if_none(self):
        """Test that PDF uses current date if none provided."""
        result = generate_executive_brief_pdf(
            title="Test Report",
            date=None,
        )

        assert result is not None

    @pytest.mark.skipif(REPORTLAB_AVAILABLE, reason="Test for fallback when reportlab not available")
    def test_fallback_text_report(self):
        """Test fallback to text report when reportlab unavailable."""
        result = generate_simple_text_report(
            title="Fallback Report",
            date="2024-01-01",
            summary_metrics={"Metric1": "Value1"},
            key_insights=["Insight 1"],
            data_tables=None,
            recommendations=["Recommendation 1"],
        )

        content = result.decode("utf-8")
        assert "FALLBACK REPORT" in content
        assert "Metric1" in content


class TestSimpleTextReport:
    """Tests for simple text report fallback."""

    def test_text_report_structure(self):
        """Test that text report has expected structure."""
        result = generate_simple_text_report(
            title="Test Report",
            date="2024-01-15",
            summary_metrics={"GDP": "3.5%", "Jobs": "1000"},
            key_insights=["Insight A", "Insight B"],
            data_tables={"Table1": pd.DataFrame({"Col": [1, 2, 3]})},
            recommendations=["Do X", "Do Y"],
        )

        content = result.decode("utf-8")

        # Check structure elements
        assert "TEST REPORT" in content
        assert "2024-01-15" in content
        assert "KEY PERFORMANCE INDICATORS" in content
        assert "GDP" in content
        assert "KEY INSIGHTS" in content
        assert "Insight A" in content
        assert "RECOMMENDATIONS" in content
        assert "Do X" in content
        assert "Eng. Sultan Albuqami" in content

    def test_text_report_with_minimal_content(self):
        """Test text report with minimal content."""
        result = generate_simple_text_report(
            title="Minimal",
            date=None,
            summary_metrics=None,
            key_insights=None,
            data_tables=None,
            recommendations=None,
        )

        content = result.decode("utf-8")
        assert "MINIMAL" in content


# =============================================================================
# PNG EXPORT TESTS
# =============================================================================


class TestPNGExport:
    """Tests for PNG export functionality."""

    @pytest.mark.skipif(not PLOTLY_AVAILABLE, reason="Plotly not available")
    def test_plotly_available_flag(self):
        """Test that Plotly availability is correctly detected."""
        # If we're here, PLOTLY_AVAILABLE should be True
        assert PLOTLY_AVAILABLE is True

    def test_png_export_handles_none_chart(self):
        """Test that PNG export handles None gracefully."""
        from analytics_hub_platform.utils.export_utils import export_plotly_to_png

        result = export_plotly_to_png(None)
        # Should return None without crashing
        assert result is None


# =============================================================================
# INTEGRATION TESTS
# =============================================================================


class TestExportIntegration:
    """Integration tests for export functionality."""

    def test_csv_roundtrip(self):
        """Test that exported CSV can be re-parsed."""
        original = pd.DataFrame({
            "region": ["Riyadh", "Makkah"],
            "value": [100.5, 200.3],
        })

        # Export
        csv_bytes = export_dataframe_to_csv(original)

        # Re-parse
        import io
        restored = pd.read_csv(io.BytesIO(csv_bytes))

        assert len(restored) == len(original)
        assert list(restored.columns) == list(original.columns)
        assert restored["region"].tolist() == original["region"].tolist()

    def test_export_with_unicode(self):
        """Test export with Unicode/Arabic content."""
        df = pd.DataFrame({
            "region": ["الرياض", "مكة المكرمة"],
            "value": [100, 200],
        })

        csv_bytes = export_dataframe_to_csv(df)
        content = csv_bytes.decode("utf-8-sig")

        assert "الرياض" in content
        assert "مكة المكرمة" in content

    def test_export_with_special_characters(self):
        """Test export with special characters."""
        df = pd.DataFrame({
            "description": ["GDP Growth (%):", "Rate < 5%", "Value > 100"],
            "value": [3.5, 4.2, 150],
        })

        csv_bytes = export_dataframe_to_csv(df)
        content = csv_bytes.decode("utf-8-sig")

        assert "GDP Growth" in content
        assert "<" in content or "&lt;" in content
