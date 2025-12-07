"""
PDF Export Utility
Sustainable Economic Development Analytics Hub
Ministry of Economy and Planning

Generates professional PDF reports with KPI summaries and charts.
"""

from io import BytesIO
from datetime import datetime
from typing import Optional
import pandas as pd

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch, cm
    from reportlab.platypus import (
        SimpleDocTemplate,
        Paragraph,
        Spacer,
        Table,
        TableStyle,
        PageBreak,
        Image,
    )
    from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

from analytics_hub_platform.config.branding import BRANDING
from analytics_hub_platform.config.theme import get_theme


def generate_pdf_report(
    data: pd.DataFrame,
    title: str = "Sustainability Analytics Report",
    subtitle: Optional[str] = None,
    summary_metrics: Optional[dict] = None,
    language: str = "en",
) -> BytesIO:
    """
    Generate a PDF report from indicator data.
    
    Args:
        data: DataFrame containing indicator data
        title: Report title
        subtitle: Optional subtitle
        summary_metrics: Optional dict of key metrics to highlight
        language: Language code (en/ar)
    
    Returns:
        BytesIO buffer containing the PDF
    """
    if not REPORTLAB_AVAILABLE:
        raise ImportError(
            "reportlab is required for PDF export. "
            "Install with: pip install reportlab"
        )
    
    buffer = BytesIO()
    theme = get_theme()
    
    # Create document
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=1.5*cm,
        leftMargin=1.5*cm,
        topMargin=2*cm,
        bottomMargin=2*cm,
    )
    
    # Styles
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Title"],
        fontSize=24,
        textColor=colors.HexColor(theme.colors.primary),
        spaceAfter=12,
        alignment=TA_CENTER,
    )
    
    subtitle_style = ParagraphStyle(
        "CustomSubtitle",
        parent=styles["Normal"],
        fontSize=14,
        textColor=colors.HexColor(theme.colors.secondary),
        spaceAfter=24,
        alignment=TA_CENTER,
    )
    
    heading_style = ParagraphStyle(
        "CustomHeading",
        parent=styles["Heading2"],
        fontSize=14,
        textColor=colors.HexColor(theme.colors.primary),
        spaceBefore=12,
        spaceAfter=8,
    )
    
    normal_style = ParagraphStyle(
        "CustomNormal",
        parent=styles["Normal"],
        fontSize=10,
        textColor=colors.HexColor(theme.colors.text_primary),
    )
    
    footer_style = ParagraphStyle(
        "CustomFooter",
        parent=styles["Normal"],
        fontSize=8,
        textColor=colors.HexColor(theme.colors.text_muted),
        alignment=TA_CENTER,
    )
    
    # Build content
    elements = []
    
    # Header
    elements.append(Paragraph(title, title_style))
    
    if subtitle:
        elements.append(Paragraph(subtitle, subtitle_style))
    
    # Generation timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    elements.append(Paragraph(f"Generated: {timestamp}", normal_style))
    elements.append(Spacer(1, 0.5*inch))
    
    # Summary Metrics Section
    if summary_metrics:
        elements.append(Paragraph("Executive Summary", heading_style))
        
        metric_data = [[k, str(v)] for k, v in summary_metrics.items()]
        metric_table = Table(metric_data, colWidths=[3*inch, 2*inch])
        metric_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f0f4f8")),
            ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor(theme.colors.text_primary)),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor(theme.colors.border)),
        ]))
        elements.append(metric_table)
        elements.append(Spacer(1, 0.3*inch))
    
    # Data Table Section
    elements.append(Paragraph("Detailed Data", heading_style))
    
    # Prepare table data
    if not data.empty:
        # Select key columns for display
        display_cols = [
            col for col in [
                "year", "quarter", "region", "sustainability_index",
                "co2_per_gdp", "renewable_energy_pct", "green_investment_pct",
            ]
            if col in data.columns
        ][:7]  # Limit columns for PDF
        
        if display_cols:
            table_data = [display_cols]  # Header row
            
            # Limit to 50 rows for PDF
            sample_data = data.head(50)
            
            for _, row in sample_data.iterrows():
                table_data.append([
                    str(row.get(col, ""))[:20]  # Truncate long values
                    for col in display_cols
                ])
            
            # Calculate column widths
            col_width = (doc.width - 0.5*inch) / len(display_cols)
            
            data_table = Table(table_data, colWidths=[col_width] * len(display_cols))
            data_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(theme.colors.primary)),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor(theme.colors.border)),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
            ]))
            elements.append(data_table)
            
            if len(data) > 50:
                elements.append(Spacer(1, 0.2*inch))
                elements.append(Paragraph(
                    f"Showing 50 of {len(data)} records. Export to Excel for complete data.",
                    normal_style
                ))
    
    elements.append(Spacer(1, 0.5*inch))
    
    # Footer with branding
    elements.append(Paragraph("—" * 60, footer_style))
    elements.append(Paragraph(
        f"Sustainable Economic Development Analytics Hub | Ministry of Economy and Planning",
        footer_style
    ))
    elements.append(Paragraph(
        f"Prepared by: {BRANDING['author_name']} | {BRANDING['author_email']}",
        footer_style
    ))
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    
    return buffer


def generate_kpi_summary_pdf(
    kpi_data: dict,
    language: str = "en",
) -> BytesIO:
    """
    Generate a one-page KPI summary PDF.
    
    Args:
        kpi_data: Dictionary of KPI names to values
        language: Language code
    
    Returns:
        BytesIO buffer containing the PDF
    """
    if not REPORTLAB_AVAILABLE:
        raise ImportError("reportlab required for PDF export")
    
    buffer = BytesIO()
    theme = get_theme()
    
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm,
    )
    
    styles = getSampleStyleSheet()
    
    elements = []
    
    # Title
    title_style = ParagraphStyle(
        "Title",
        parent=styles["Title"],
        fontSize=20,
        textColor=colors.HexColor(theme.colors.primary),
        alignment=TA_CENTER,
        spaceAfter=20,
    )
    
    elements.append(Paragraph("Key Performance Indicators Summary", title_style))
    elements.append(Paragraph(
        datetime.now().strftime("%B %Y"),
        ParagraphStyle(
            "Date",
            parent=styles["Normal"],
            fontSize=12,
            alignment=TA_CENTER,
            spaceAfter=30,
        )
    ))
    
    # KPI Grid
    if kpi_data:
        kpi_rows = []
        items = list(kpi_data.items())
        
        # Create 2-column layout
        for i in range(0, len(items), 2):
            row = []
            for j in range(2):
                if i + j < len(items):
                    name, value = items[i + j]
                    row.append(f"{name}\n{value}")
                else:
                    row.append("")
            kpi_rows.append(row)
        
        kpi_table = Table(kpi_rows, colWidths=[3.5*inch, 3.5*inch])
        kpi_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 11),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 20),
            ("TOPPADDING", (0, 0), (-1, -1), 20),
            ("BOX", (0, 0), (-1, -1), 1, colors.HexColor(theme.colors.border)),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor(theme.colors.border)),
        ]))
        elements.append(kpi_table)
    
    doc.build(elements)
    buffer.seek(0)
    
    return buffer
