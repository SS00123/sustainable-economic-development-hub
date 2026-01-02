"""
Export Utility Tests
Sustainable Economic Development Analytics Hub

Tests for PDF, PPT, and Excel export functions.
"""

from io import BytesIO

import pandas as pd
import pytest


class TestPDFExport:
    """Tests for PDF export functionality."""

    def test_generate_pdf_report(self, sample_indicator_data):
        """Test PDF report generation."""
        try:
            from analytics_hub_platform.utils.export_pdf import generate_pdf_report

            buffer = generate_pdf_report(
                data=sample_indicator_data,
                title="Test Report",
                subtitle="Test Subtitle",
                summary_metrics={"Metric 1": "100", "Metric 2": "200"},
            )

            assert isinstance(buffer, BytesIO)
            assert buffer.getvalue()[:4] == b"%PDF"  # PDF magic bytes

        except ImportError:
            pytest.skip("reportlab not installed")

    def test_generate_pdf_empty_data(self):
        """Test PDF with empty data."""
        try:
            from analytics_hub_platform.utils.export_pdf import generate_pdf_report

            buffer = generate_pdf_report(
                data=pd.DataFrame(),
                title="Empty Report",
            )

            assert isinstance(buffer, BytesIO)

        except ImportError:
            pytest.skip("reportlab not installed")


class TestPPTExport:
    """Tests for PowerPoint export functionality."""

    def test_generate_ppt_presentation(self, sample_indicator_data):
        """Test PPT presentation generation."""
        try:
            from analytics_hub_platform.utils.export_ppt import generate_ppt_presentation

            buffer = generate_ppt_presentation(
                data=sample_indicator_data,
                title="Test Presentation",
                summary_metrics={"KPI 1": "75%", "KPI 2": "82%"},
            )

            assert isinstance(buffer, BytesIO)
            # PPTX files are ZIP archives
            assert buffer.getvalue()[:2] == b"PK"

        except ImportError:
            pytest.skip("python-pptx not installed")

    def test_generate_kpi_slide(self):
        """Test single KPI slide generation."""
        try:
            from analytics_hub_platform.utils.export_ppt import generate_kpi_slide

            buffer = generate_kpi_slide(
                kpi_name="Sustainability Index",
                kpi_value="72.5",
                trend="+5.2% vs last quarter",
                status="green",
            )

            assert isinstance(buffer, BytesIO)

        except ImportError:
            pytest.skip("python-pptx not installed")


class TestExcelExport:
    """Tests for Excel export functionality."""

    def test_generate_excel_workbook(self, sample_indicator_data):
        """Test Excel workbook generation."""
        try:
            from analytics_hub_platform.utils.export_excel import generate_excel_workbook

            buffer = generate_excel_workbook(
                data=sample_indicator_data,
                title="Test Workbook",
                summary_metrics={"Total": 100, "Average": 50},
            )

            assert isinstance(buffer, BytesIO)
            # XLSX files are ZIP archives
            assert buffer.getvalue()[:2] == b"PK"

        except ImportError:
            pytest.skip("openpyxl not installed")

    def test_generate_simple_excel(self, sample_indicator_data):
        """Test simple Excel export."""
        try:
            from analytics_hub_platform.utils.export_excel import generate_simple_excel

            buffer = generate_simple_excel(
                data=sample_indicator_data,
                sheet_name="Data",
            )

            assert isinstance(buffer, BytesIO)

        except ImportError:
            pytest.skip("openpyxl not installed")

    def test_generate_multi_sheet_excel(self, sample_indicator_data):
        """Test multi-sheet Excel export."""
        try:
            from analytics_hub_platform.utils.export_excel import generate_multi_sheet_excel

            sheets = {
                "Summary": sample_indicator_data.head(10),
                "Full Data": sample_indicator_data,
            }

            buffer = generate_multi_sheet_excel(
                sheets=sheets,
                title="Multi-Sheet Report",
            )

            assert isinstance(buffer, BytesIO)

        except ImportError:
            pytest.skip("openpyxl not installed")
