"""
Analyst View Page
Sustainable Economic Development Analytics Hub
Ministry of Economy and Planning

This page provides a detailed analytical interface for data analysts:
- Raw data tables with pagination
- Data quality metrics
- Export capabilities
- Detailed filtering and search
"""

import streamlit as st
import pandas as pd

from analytics_hub_platform.ui.layout import (
    render_header,
    render_footer,
    render_section_header,
    inject_custom_css,
    render_alert_box,
)
from analytics_hub_platform.ui.filters import get_filter_state
from analytics_hub_platform.config.theme import get_theme
from analytics_hub_platform.infrastructure.repository import get_repository
from analytics_hub_platform.infrastructure.settings import get_settings
from analytics_hub_platform.infrastructure.security import get_rate_limiter, RateLimitExceeded
from analytics_hub_platform.domain.models import FilterParams
from analytics_hub_platform.domain.services import get_data_quality_metrics
from analytics_hub_platform.utils.export_excel import export_to_excel
from analytics_hub_platform.locale import get_strings


def render_analyst_view() -> None:
    """Render the analyst dashboard view."""
    inject_custom_css()
    theme = get_theme()
    
    # Get filter state
    filters = get_filter_state()
    strings = get_strings(filters.language)
    
    # Header
    render_header(
        title=strings.get("analyst_title", "Data Analysis Console"),
        subtitle=strings.get("analyst_subtitle", "Raw Data Access and Quality Metrics"),
        language=filters.language,
    )
    
    # Load data
    try:
        repo = get_repository()
        settings = get_settings()
        
        df = repo.get_all_indicators(settings.default_tenant_id)
        
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return
    
    # Tabs for different views
    tab1, tab2, tab3 = st.tabs([
        "📋 Data Explorer",
        "✅ Data Quality",
        "📤 Export Center"
    ])
    
    with tab1:
        render_data_explorer_tab(df, theme, filters)
    
    with tab2:
        render_data_quality_tab(df, theme, filters)
    
    with tab3:
        render_export_tab(df, theme, filters)
    
    # Footer
    render_footer(filters.language)


def render_data_explorer_tab(df: pd.DataFrame, theme, filters) -> None:
    """Render the data explorer tab."""
    
    render_section_header(title="Data Explorer", icon="📋")
    
    # Filters
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        years = sorted(df["year"].unique(), reverse=True)
        selected_years = st.multiselect(
            "Filter by Year",
            options=years,
            default=[filters.year] if filters.year in years else years[:1],
        )
    
    with col2:
        quarters = [1, 2, 3, 4]
        selected_quarters = st.multiselect(
            "Filter by Quarter",
            options=quarters,
            default=[filters.quarter],
            format_func=lambda x: f"Q{x}",
        )
    
    with col3:
        regions = sorted(df["region"].unique())
        selected_regions = st.multiselect(
            "Filter by Region",
            options=regions,
            default=None,
        )
    
    with col4:
        # Column selector
        all_columns = list(df.columns)
        display_columns = [c for c in all_columns if c not in ["id", "tenant_id", "source_system", "load_batch_id"]]
        
        selected_columns = st.multiselect(
            "Select Columns",
            options=display_columns,
            default=["year", "quarter", "region", "sustainability_index", "gdp_growth", "renewable_share"],
        )
    
    # Apply filters
    filtered_df = df.copy()
    
    if selected_years:
        filtered_df = filtered_df[filtered_df["year"].isin(selected_years)]
    
    if selected_quarters:
        filtered_df = filtered_df[filtered_df["quarter"].isin(selected_quarters)]
    
    if selected_regions:
        filtered_df = filtered_df[filtered_df["region"].isin(selected_regions)]
    
    if selected_columns:
        filtered_df = filtered_df[selected_columns]
    
    # Display stats
    st.markdown(f"**Showing {len(filtered_df):,} records**")
    
    # Search
    search_term = st.text_input("🔍 Search", placeholder="Search in data...")
    
    if search_term:
        mask = filtered_df.astype(str).apply(
            lambda x: x.str.contains(search_term, case=False)
        ).any(axis=1)
        filtered_df = filtered_df[mask]
        st.markdown(f"**Found {len(filtered_df):,} matching records**")
    
    # Pagination
    page_size = st.selectbox("Rows per page", options=[25, 50, 100, 250], index=1)
    total_pages = max(1, (len(filtered_df) - 1) // page_size + 1)
    
    page = st.number_input(
        f"Page (1-{total_pages})",
        min_value=1,
        max_value=total_pages,
        value=1,
    )
    
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    
    # Display data
    st.dataframe(
        filtered_df.iloc[start_idx:end_idx],
        use_container_width=True,
        height=400,
    )
    
    # Summary statistics
    st.markdown("---")
    render_section_header(title="Summary Statistics", icon="📊")
    
    numeric_cols = filtered_df.select_dtypes(include=['float64', 'int64']).columns
    if len(numeric_cols) > 0:
        st.dataframe(
            filtered_df[numeric_cols].describe().round(2),
            use_container_width=True,
        )


def render_data_quality_tab(df: pd.DataFrame, theme, filters) -> None:
    """Render the data quality metrics tab."""
    
    render_section_header(title="Data Quality Metrics", icon="✅")
    
    settings = get_settings()
    filter_params = FilterParams(
        tenant_id=settings.default_tenant_id,
        year=filters.year,
        quarter=filters.quarter,
        region=filters.region if filters.region != "all" else None,
    )
    
    quality_metrics = get_data_quality_metrics(df, filter_params)
    
    # Overview metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        completeness = quality_metrics.get("completeness", 0)
        st.metric(
            "Data Completeness",
            f"{completeness:.1f}%",
            delta=None,
        )
    
    with col2:
        records = quality_metrics.get("records_count", 0)
        st.metric(
            "Total Records",
            f"{records:,}",
        )
    
    with col3:
        avg_quality = quality_metrics.get("avg_quality_score") or 0
        st.metric(
            "Avg Quality Score",
            f"{avg_quality:.1f}",
        )
    
    with col4:
        last_update = quality_metrics.get("last_update")
        update_str = last_update.strftime("%Y-%m-%d") if last_update else "N/A"
        st.metric(
            "Last Updated",
            update_str,
        )
    
    st.markdown("---")
    
    # Missing data by KPI
    render_section_header(title="Data Completeness by Indicator", icon="📉")
    
    missing_by_kpi = quality_metrics.get("missing_by_kpi", {})
    
    if missing_by_kpi:
        # Create DataFrame for display
        missing_data = []
        for kpi, info in missing_by_kpi.items():
            missing_data.append({
                "Indicator": kpi,
                "Total Records": info["total"],
                "Missing": info["missing"],
                "Missing %": info["percent"],
                "Complete %": 100 - info["percent"],
            })
        
        missing_df = pd.DataFrame(missing_data)
        missing_df = missing_df.sort_values("Missing %", ascending=False)
        
        # Color code based on completeness
        def color_completeness(val):
            if val >= 95:
                return f'background-color: {theme.colors.status_green_bg}'
            elif val >= 80:
                return f'background-color: {theme.colors.status_amber_bg}'
            else:
                return f'background-color: {theme.colors.status_red_bg}'
        
        st.dataframe(
            missing_df.style.map(
                color_completeness,
                subset=["Complete %"]
            ),
            use_container_width=True,
            height=400,
        )
    
    st.markdown("---")
    
    # Data freshness by region
    render_section_header(title="Data Freshness by Region", icon="🕐")
    
    # Group by region and find latest timestamp
    if "load_timestamp" in df.columns and "region" in df.columns:
        freshness = df.groupby("region").agg({
            "load_timestamp": "max",
            "data_quality_score": "mean",
        }).reset_index()
        
        freshness.columns = ["Region", "Last Update", "Avg Quality"]
        freshness = freshness.sort_values("Last Update", ascending=False)
        
        st.dataframe(freshness, use_container_width=True)
    else:
        st.info("Timestamp data not available for freshness analysis.")


def render_export_tab(df: pd.DataFrame, theme, filters) -> None:
    """Render the export center tab."""
    
    render_section_header(title="Export Center", icon="📤")
    
    st.markdown("""
    Export data in various formats for further analysis or reporting.
    Rate limits apply to prevent system overload.
    """)
    
    # Export options
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Excel Export")
        st.markdown("Export raw data and summary statistics to Excel.")
        
        export_years = st.multiselect(
            "Years to export",
            options=sorted(df["year"].unique(), reverse=True),
            default=[filters.year],
            key="export_years",
        )
        
        export_regions = st.multiselect(
            "Regions to export",
            options=["All"] + sorted(df["region"].unique().tolist()),
            default=["All"],
            key="export_regions",
        )
        
        include_summary = st.checkbox("Include summary sheet", value=True)
        include_quality = st.checkbox("Include data quality sheet", value=True)
        
        if st.button("📥 Generate Excel Export", type="primary"):
            try:
                # Check rate limit
                limiter = get_rate_limiter("export")
                limiter.acquire_or_raise(f"user_{filters.tenant_id}")
                
                # Filter data
                export_df = df.copy()
                if export_years:
                    export_df = export_df[export_df["year"].isin(export_years)]
                if "All" not in export_regions:
                    export_df = export_df[export_df["region"].isin(export_regions)]
                
                # Generate export
                excel_bytes = export_to_excel(
                    export_df,
                    include_summary=include_summary,
                    include_quality=include_quality,
                )
                
                st.download_button(
                    "⬇️ Download Excel File",
                    data=excel_bytes,
                    file_name=f"analytics_export_{filters.year}_Q{filters.quarter}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
                
                render_alert_box("Excel file generated successfully!", "success")
                
            except RateLimitExceeded as e:
                render_alert_box(
                    f"Rate limit exceeded. Please try again in {e.retry_after} seconds.",
                    "warning"
                )
            except Exception as e:
                render_alert_box(f"Error generating export: {str(e)}", "error")
    
    with col2:
        st.markdown("### CSV Export")
        st.markdown("Export raw data to CSV format.")
        
        csv_filter_year = st.selectbox(
            "Year",
            options=sorted(df["year"].unique(), reverse=True),
            key="csv_year",
        )
        
        csv_filter_quarter = st.selectbox(
            "Quarter",
            options=[1, 2, 3, 4],
            format_func=lambda x: f"Q{x}",
            key="csv_quarter",
        )
        
        if st.button("📥 Generate CSV Export"):
            try:
                limiter = get_rate_limiter("export")
                limiter.acquire_or_raise(f"user_{filters.tenant_id}")
                
                csv_df = df[
                    (df["year"] == csv_filter_year) &
                    (df["quarter"] == csv_filter_quarter)
                ]
                
                csv_data = csv_df.to_csv(index=False)
                
                st.download_button(
                    "⬇️ Download CSV File",
                    data=csv_data,
                    file_name=f"analytics_data_{csv_filter_year}_Q{csv_filter_quarter}.csv",
                    mime="text/csv",
                )
                
                render_alert_box("CSV file generated successfully!", "success")
                
            except RateLimitExceeded as e:
                render_alert_box(
                    f"Rate limit exceeded. Please try again in {e.retry_after} seconds.",
                    "warning"
                )
            except Exception as e:
                render_alert_box(f"Error generating export: {str(e)}", "error")
    
    st.markdown("---")
    
    # Export rate limit info
    limiter = get_rate_limiter("export")
    remaining = limiter.get_remaining(f"user_{filters.tenant_id}")
    
    st.info(f"📊 Export quota remaining: {remaining} exports per minute")
