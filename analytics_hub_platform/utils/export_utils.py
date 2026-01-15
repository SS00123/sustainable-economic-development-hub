"""
Export Module
Sustainable Economic Development Analytics Hub

Provides export functionality:
- CSV export for data tables
- PNG export for charts (with fallback)
- Executive Brief PDF generation
"""

import base64
import io
from datetime import datetime, timezone
from typing import Any

import pandas as pd

# Optional imports with fallbacks
try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, letter
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import inch
    from reportlab.platypus import (
        Image,
        PageBreak,
        Paragraph,
        SimpleDocTemplate,
        Spacer,
        Table,
        TableStyle,
    )

    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

try:
    import plotly.graph_objects as go
    import plotly.io as pio

    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False


# =============================================================================
# CSV EXPORT
# =============================================================================


def export_dataframe_to_csv(
    df: pd.DataFrame,
    filename: str = "export.csv",
    include_index: bool = False,
) -> bytes:
    """
    Export a DataFrame to CSV bytes.

    Args:
        df: DataFrame to export
        filename: Suggested filename (not used for bytes output)
        include_index: Whether to include the index column

    Returns:
        CSV file as bytes
    """
    buffer = io.StringIO()
    df.to_csv(buffer, index=include_index, encoding="utf-8-sig")  # BOM for Excel
    return buffer.getvalue().encode("utf-8-sig")


def get_csv_download_link(
    df: pd.DataFrame,
    filename: str = "data_export.csv",
    link_text: str = "📥 Download CSV",
) -> str:
    """
    Generate an HTML download link for CSV data.

    Args:
        df: DataFrame to export
        filename: Download filename
        link_text: Text to display on link

    Returns:
        HTML anchor tag for download
    """
    csv_bytes = export_dataframe_to_csv(df)
    b64 = base64.b64encode(csv_bytes).decode()

    return f'<a href="data:file/csv;base64,{b64}" download="{filename}">{link_text}</a>'


# =============================================================================
# PNG EXPORT
# =============================================================================


def export_plotly_to_png(
    fig: Any,
    width: int = 1200,
    height: int = 800,
    scale: int = 2,
) -> bytes | None:
    """
    Export a Plotly figure to PNG bytes.

    Args:
        fig: Plotly figure object
        width: Image width in pixels
        height: Image height in pixels
        scale: Resolution scale factor

    Returns:
        PNG bytes or None if export fails
    """
    if not PLOTLY_AVAILABLE:
        return None

    try:
        img_bytes = pio.to_image(
            fig,
            format="png",
            width=width,
            height=height,
            scale=scale,
        )
        return img_bytes
    except Exception as e:
        # Fallback: Try without kaleido (requires different setup)
        print(f"PNG export failed: {e}")
        return None


def export_chart_to_svg(fig: Any) -> str | None:
    """
    Export a Plotly figure to SVG string (fallback for PNG).

    Args:
        fig: Plotly figure object

    Returns:
        SVG string or None
    """
    if not PLOTLY_AVAILABLE:
        return None

    try:
        return pio.to_image(fig, format="svg").decode("utf-8")
    except Exception:
        # Pure HTML fallback
        return fig.to_html(include_plotlyjs=False, full_html=False)


def get_png_download_button_html(
    fig: Any,
    filename: str = "chart.png",
    button_text: str = "📊 Download Chart",
) -> str:
    """
    Generate HTML for a PNG download button.

    Args:
        fig: Plotly figure
        filename: Download filename
        button_text: Button text

    Returns:
        HTML for download button or fallback message
    """
    png_bytes = export_plotly_to_png(fig)

    if png_bytes:
        b64 = base64.b64encode(png_bytes).decode()
        return f'''
        <a href="data:image/png;base64,{b64}"
           download="{filename}"
           style="
               display: inline-block;
               padding: 0.5rem 1rem;
               background-color: #059669;
               color: white;
               border-radius: 0.25rem;
               text-decoration: none;
               font-size: 0.875rem;
           ">
            {button_text}
        </a>
        '''
    else:
        # Fallback: Provide instructions
        return '''
        <div style="
            padding: 0.5rem 1rem;
            background-color: #FEF3C7;
            border-radius: 0.25rem;
            color: #92400E;
            font-size: 0.875rem;
        ">
            📊 Use browser's screenshot (Ctrl+Shift+S) or install kaleido for PNG export
        </div>
        '''


# =============================================================================
# PDF EXPORT - EXECUTIVE BRIEF
# =============================================================================


def generate_executive_brief_pdf(
    title: str = "Sustainability Dashboard Executive Brief",
    date: str | None = None,
    summary_metrics: dict[str, Any] | None = None,
    key_insights: list[str] | None = None,
    data_tables: dict[str, pd.DataFrame] | None = None,
    recommendations: list[str] | None = None,
) -> bytes | None:
    """
    Generate an Executive Brief PDF report.

    Args:
        title: Report title
        date: Report date (defaults to now)
        summary_metrics: Dict of metric name -> value
        key_insights: List of key insight strings
        data_tables: Dict of table name -> DataFrame
        recommendations: List of recommendation strings

    Returns:
        PDF bytes or None if generation fails
    """
    if not REPORTLAB_AVAILABLE:
        return generate_simple_text_report(
            title, date, summary_metrics, key_insights, data_tables, recommendations
        )

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.75 * inch, bottomMargin=0.75 * inch)

    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Heading1"],
        fontSize=24,
        spaceAfter=30,
        textColor=colors.HexColor("#1E3A5F"),
    )
    heading_style = ParagraphStyle(
        "CustomHeading",
        parent=styles["Heading2"],
        fontSize=14,
        spaceBefore=20,
        spaceAfter=10,
        textColor=colors.HexColor("#1E40AF"),
    )
    normal_style = styles["Normal"]

    # Content elements
    elements = []

    # Title
    elements.append(Paragraph(title, title_style))

    # Date
    if date is None:
        date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    elements.append(Paragraph(f"<i>Generated: {date}</i>", normal_style))
    elements.append(Spacer(1, 20))

    # Summary Metrics Section
    if summary_metrics:
        elements.append(Paragraph("Key Performance Indicators", heading_style))

        metric_data = [["Indicator", "Value", "Status"]]
        for name, value in summary_metrics.items():
            status = "🟢" if isinstance(value, (int, float)) and value > 0 else "🟡"
            metric_data.append([name, str(value), status])

        metric_table = Table(metric_data, colWidths=[3 * inch, 2 * inch, 1 * inch])
        metric_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E3A5F")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("FONTSIZE", (0, 0), (-1, 0), 11),
                    ("FONTSIZE", (0, 1), (-1, -1), 10),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F3F4F6")]),
                ]
            )
        )
        elements.append(metric_table)
        elements.append(Spacer(1, 20))

    # Key Insights Section
    if key_insights:
        elements.append(Paragraph("Key Insights", heading_style))
        for insight in key_insights:
            elements.append(Paragraph(f"• {insight}", normal_style))
        elements.append(Spacer(1, 20))

    # Data Tables Section
    if data_tables:
        for table_name, df in data_tables.items():
            elements.append(Paragraph(table_name, heading_style))

            # Convert DataFrame to table data
            table_data = [df.columns.tolist()] + df.head(10).values.tolist()

            # Calculate column widths
            num_cols = len(df.columns)
            col_width = (6.5 * inch) / num_cols

            data_table = Table(table_data, colWidths=[col_width] * num_cols)
            data_table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#374151")),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                        ("FONTSIZE", (0, 0), (-1, 0), 9),
                        ("FONTSIZE", (0, 1), (-1, -1), 8),
                        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F9FAFB")]),
                    ]
                )
            )
            elements.append(data_table)
            elements.append(Spacer(1, 15))

    # Recommendations Section
    if recommendations:
        elements.append(PageBreak())
        elements.append(Paragraph("Recommendations", heading_style))
        for i, rec in enumerate(recommendations, 1):
            elements.append(Paragraph(f"{i}. {rec}", normal_style))
        elements.append(Spacer(1, 20))

    # Footer
    elements.append(Spacer(1, 30))
    elements.append(
        Paragraph(
            "<i>Ministry of Economy and Planning - Confidential</i>",
            ParagraphStyle("Footer", parent=normal_style, fontSize=8, textColor=colors.grey),
        )
    )

    # Build PDF
    try:
        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue()
    except Exception as e:
        print(f"PDF generation failed: {e}")
        return None


def generate_simple_text_report(
    title: str,
    date: str | None,
    summary_metrics: dict[str, Any] | None,
    key_insights: list[str] | None,
    data_tables: dict[str, pd.DataFrame] | None,
    recommendations: list[str] | None,
) -> bytes:
    """
    Generate a simple text report as fallback when reportlab is not available.

    Returns:
        Text report as bytes
    """
    lines = []

    # Header
    lines.append("=" * 60)
    lines.append(title.upper())
    lines.append("=" * 60)
    lines.append(f"Generated: {date or datetime.now(timezone.utc).strftime('%Y-%m-%d')}")
    lines.append("")

    # Metrics
    if summary_metrics:
        lines.append("-" * 40)
        lines.append("KEY PERFORMANCE INDICATORS")
        lines.append("-" * 40)
        for name, value in summary_metrics.items():
            lines.append(f"  {name}: {value}")
        lines.append("")

    # Insights
    if key_insights:
        lines.append("-" * 40)
        lines.append("KEY INSIGHTS")
        lines.append("-" * 40)
        for insight in key_insights:
            lines.append(f"  • {insight}")
        lines.append("")

    # Tables
    if data_tables:
        for table_name, df in data_tables.items():
            lines.append("-" * 40)
            lines.append(table_name.upper())
            lines.append("-" * 40)
            lines.append(df.head(10).to_string())
            lines.append("")

    # Recommendations
    if recommendations:
        lines.append("-" * 40)
        lines.append("RECOMMENDATIONS")
        lines.append("-" * 40)
        for i, rec in enumerate(recommendations, 1):
            lines.append(f"  {i}. {rec}")
        lines.append("")

    lines.append("=" * 60)
    lines.append("Ministry of Economy and Planning - Confidential")

    return "\n".join(lines).encode("utf-8")


def get_pdf_download_link(
    pdf_bytes: bytes,
    filename: str = "executive_brief.pdf",
    link_text: str = "📄 Download Executive Brief",
) -> str:
    """
    Generate an HTML download link for a PDF.

    Args:
        pdf_bytes: PDF file bytes
        filename: Download filename
        link_text: Link text

    Returns:
        HTML anchor tag
    """
    b64 = base64.b64encode(pdf_bytes).decode()
    mime = "application/pdf" if pdf_bytes[:4] == b"%PDF" else "text/plain"

    return f'''
    <a href="data:{mime};base64,{b64}"
       download="{filename}"
       style="
           display: inline-block;
           padding: 0.75rem 1.5rem;
           background-color: #DC2626;
           color: white;
           border-radius: 0.375rem;
           text-decoration: none;
           font-weight: 500;
       ">
        {link_text}
    </a>
    '''


# =============================================================================
# STREAMLIT EXPORT COMPONENTS
# =============================================================================


def render_export_panel(
    df: pd.DataFrame | None = None,
    chart: Any | None = None,
    metrics: dict[str, Any] | None = None,
    insights: list[str] | None = None,
):
    """
    Render a complete export panel with all export options.

    Args:
        df: Optional DataFrame for CSV export
        chart: Optional Plotly chart for PNG export
        metrics: Optional metrics dict for PDF
        insights: Optional insights list for PDF
    """
    import streamlit as st

    st.subheader("📤 Export Options")

    col1, col2, col3 = st.columns(3)

    # CSV Export
    with col1:
        st.markdown("##### 📊 Data Export")
        if df is not None and len(df) > 0:
            csv_bytes = export_dataframe_to_csv(df)
            st.download_button(
                label="📥 Download CSV",
                data=csv_bytes,
                file_name=f"data_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
            )
        else:
            st.info("No data available for export")

    # PNG Export
    with col2:
        st.markdown("##### 📈 Chart Export")
        if chart is not None:
            png_bytes = export_plotly_to_png(chart)
            if png_bytes:
                st.download_button(
                    label="📊 Download PNG",
                    data=png_bytes,
                    file_name=f"chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
                    mime="image/png",
                )
            else:
                st.warning("Install kaleido for PNG export:\n`pip install -U kaleido`")
        else:
            st.info("No chart available for export")

    # PDF Export
    with col3:
        st.markdown("##### 📄 Executive Brief")
        if st.button("Generate PDF", key="gen_pdf_btn"):
            with st.spinner("Generating report..."):
                pdf_bytes = generate_executive_brief_pdf(
                    title="Sustainability Dashboard - Executive Brief",
                    summary_metrics=metrics,
                    key_insights=insights,
                    data_tables={"Summary Data": df} if df is not None else None,
                )

                if pdf_bytes:
                    ext = "pdf" if REPORTLAB_AVAILABLE else "txt"
                    mime = "application/pdf" if REPORTLAB_AVAILABLE else "text/plain"
                    st.download_button(
                        label="📄 Download Brief",
                        data=pdf_bytes,
                        file_name=f"executive_brief_{datetime.now().strftime('%Y%m%d')}.{ext}",
                        mime=mime,
                    )
                else:
                    st.error("Failed to generate report")
