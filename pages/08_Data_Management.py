"""
Data Management Page
Sustainable Economic Development Analytics Hub

Provides:
- File upload (Excel/CSV)
- Data validation
- Data quality reports
- Upload history
"""

import streamlit as st
from datetime import datetime, timezone

# Page config
st.set_page_config(
    page_title="Data Management | Analytics Hub",
    page_icon="📤",
    layout="wide",
)


def render_upload_section():
    """Render the data upload section."""
    st.subheader("📤 Upload Data")

    # Instructions
    with st.expander("📋 Upload Instructions", expanded=False):
        st.markdown("""
        ### Supported Formats
        - **Excel (.xlsx, .xls)** - Recommended
        - **CSV (.csv)**

        ### Required Columns
        - `tenant_id` - Tenant identifier
        - `year` - Calendar year (2020-2030)
        - `quarter` - Quarter (1-4)
        - `region` - Administrative region

        ### Optional Indicator Columns
        Economic, Social, and Environmental indicators as documented in DATA_CONTRACT.md

        ### Tips
        1. Download the template first to see the expected format
        2. Use "Validate Only" to check data before importing
        3. Review warnings even if validation passes
        """)

    # Template download
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("📥 Download Template"):
            try:
                from analytics_hub_platform.infrastructure.data_ingestion import export_template_excel

                template_bytes = export_template_excel()
                st.download_button(
                    label="💾 Save Template",
                    data=template_bytes,
                    file_name="data_upload_template.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
            except Exception as e:
                st.error(f"Failed to generate template: {e}")

    st.divider()

    # File upload
    uploaded_file = st.file_uploader(
        "Choose a file to upload",
        type=["xlsx", "xls", "csv"],
        help="Select an Excel or CSV file with sustainability indicator data",
    )

    if uploaded_file is not None:
        st.info(f"📁 File: **{uploaded_file.name}** ({uploaded_file.size:,} bytes)")

        # Configuration
        col1, col2, col3 = st.columns(3)

        with col1:
            tenant_id = st.text_input(
                "Tenant ID",
                value="ministry_economy",
                help="Identifier for the tenant/organization",
            )

        with col2:
            source_system = st.text_input(
                "Source System",
                value="manual_upload",
                help="Origin system of the data",
            )

        with col3:
            replace_existing = st.checkbox(
                "Replace Existing Records",
                value=False,
                help="If checked, existing records will be updated",
            )

        # Action buttons
        col1, col2, col3 = st.columns([1, 1, 2])

        with col1:
            validate_only = st.button("🔍 Validate Only", type="secondary")

        with col2:
            do_import = st.button("📥 Import Data", type="primary")

        if validate_only or do_import:
            with st.spinner("Processing..."):
                try:
                    from analytics_hub_platform.infrastructure.data_ingestion import ingest_file

                    result = ingest_file(
                        file_content=uploaded_file.getvalue(),
                        filename=uploaded_file.name,
                        tenant_id=tenant_id,
                        source_system=source_system,
                        replace_existing=replace_existing,
                        validate_only=validate_only,
                    )

                    # Display results
                    if result.success:
                        st.success(f"✅ {result.message}")

                        if not validate_only:
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Inserted", result.rows_inserted)
                            with col2:
                                st.metric("Updated", result.rows_updated)
                            with col3:
                                st.metric("Skipped", result.rows_skipped)

                            st.caption(f"Batch ID: `{result.batch_id}`")
                    else:
                        st.error(f"❌ {result.message}")

                    # Show validation details
                    if result.validation.errors:
                        st.error("**Errors:**")
                        for error in result.validation.errors:
                            st.write(f"  ❌ {error}")

                    if result.validation.warnings:
                        st.warning("**Warnings:**")
                        for warning in result.validation.warnings:
                            st.write(f"  ⚠️ {warning}")

                    # Show stats
                    with st.expander("Validation Details"):
                        st.write(f"**Total Rows:** {result.validation.row_count}")
                        st.write(f"**Valid Rows:** {result.validation.valid_row_count}")
                        st.write(f"**Invalid Rows:** {len(result.validation.invalid_row_indices)}")

                except Exception as e:
                    st.error(f"Processing failed: {e}")


def render_dq_report_section():
    """Render the data quality report section."""
    st.subheader("📊 Data Quality Report")

    tenant_id = st.selectbox(
        "Select Tenant",
        options=["ministry_economy"],
        index=0,
    )

    if st.button("🔄 Generate Report", type="primary"):
        with st.spinner("Analyzing data quality..."):
            try:
                from analytics_hub_platform.infrastructure.data_quality import generate_dq_report

                report = generate_dq_report(tenant_id)

                # Overall score card
                status_colors = {
                    "excellent": "🟢",
                    "good": "🟡",
                    "fair": "🟠",
                    "poor": "🔴",
                }

                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric(
                        "Overall Score",
                        f"{report.overall_score:.1f}%",
                        help="Weighted average of all quality dimensions",
                    )

                with col2:
                    st.metric(
                        "Status",
                        f"{status_colors.get(report.status, '⚪')} {report.status.title()}",
                    )

                with col3:
                    st.metric("Checks Passed", report.passed_checks)

                with col4:
                    st.metric("Checks Failed", report.failed_checks)

                st.divider()

                # Category scores
                if report.summary.get("category_scores"):
                    st.write("**Scores by Category:**")
                    cols = st.columns(len(report.summary["category_scores"]))
                    for i, (category, score) in enumerate(report.summary["category_scores"].items()):
                        with cols[i]:
                            progress_color = "normal" if score >= 70 else "off"
                            st.progress(score / 100, f"{category.title()}: {score:.0f}%")

                st.divider()

                # Individual checks
                st.write("**Individual Checks:**")

                for check in report.checks:
                    icon = "✅" if check.passed else "❌"
                    with st.expander(f"{icon} {check.name} ({check.score:.0f}%)"):
                        st.write(f"**Category:** {check.category.title()}")
                        st.write(f"**Message:** {check.message}")
                        if check.details:
                            st.json(check.details)

                # Summary stats
                st.divider()
                st.write("**Data Summary:**")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Rows", report.summary.get("total_rows", 0))
                with col2:
                    st.metric("Unique Periods", report.summary.get("unique_periods", 0))
                with col3:
                    st.metric("Unique Regions", report.summary.get("unique_regions", 0))

            except Exception as e:
                st.error(f"Failed to generate report: {e}")
                import traceback

                st.code(traceback.format_exc())


def render_data_explorer():
    """Render a simple data explorer."""
    st.subheader("🔍 Data Explorer")

    try:
        from analytics_hub_platform.infrastructure.repository import get_repository

        repo = get_repository()
        df = repo.get_all_indicators("ministry_economy")

        if len(df) == 0:
            st.warning("No data available. Upload data using the section above.")
            return

        # Filters
        col1, col2, col3 = st.columns(3)

        with col1:
            years = sorted(df["year"].unique())
            selected_year = st.selectbox("Year", options=["All"] + list(years))

        with col2:
            quarters = sorted(df["quarter"].unique())
            selected_quarter = st.selectbox("Quarter", options=["All"] + list(quarters))

        with col3:
            regions = sorted(df["region"].unique())
            selected_region = st.selectbox("Region", options=["All"] + list(regions))

        # Apply filters
        filtered_df = df.copy()
        if selected_year != "All":
            filtered_df = filtered_df[filtered_df["year"] == selected_year]
        if selected_quarter != "All":
            filtered_df = filtered_df[filtered_df["quarter"] == selected_quarter]
        if selected_region != "All":
            filtered_df = filtered_df[filtered_df["region"] == selected_region]

        st.write(f"Showing {len(filtered_df)} of {len(df)} records")

        # Display options
        columns_to_show = st.multiselect(
            "Select columns to display",
            options=list(df.columns),
            default=["year", "quarter", "region", "gdp_growth", "unemployment_rate", "renewable_share", "sustainability_index"],
        )

        if columns_to_show:
            st.dataframe(
                filtered_df[columns_to_show],
                use_container_width=True,
                hide_index=True,
            )

            # Download filtered data
            csv = filtered_df[columns_to_show].to_csv(index=False)
            st.download_button(
                label="📥 Download Filtered Data (CSV)",
                data=csv,
                file_name=f"analytics_data_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
            )

    except Exception as e:
        st.error(f"Failed to load data: {e}")


def main():
    """Main page function."""
    st.title("📤 Data Management")
    st.caption("Upload, validate, and manage sustainability indicator data")

    # Tabs for different sections
    tab1, tab2, tab3 = st.tabs(["📤 Upload", "📊 Quality Report", "🔍 Explorer"])

    with tab1:
        render_upload_section()

    with tab2:
        render_dq_report_section()

    with tab3:
        render_data_explorer()


if __name__ == "__main__":
    main()
else:
    main()
