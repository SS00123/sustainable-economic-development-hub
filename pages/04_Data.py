"""
Data Page
Data Quality and Raw Data View

Displays:
- Data quality metrics
- Completeness statistics
- Record counts
- Update timestamps
- Data freshness indicators
"""

import pandas as pd
import streamlit as st

# Page configuration
st.set_page_config(
    page_title="Data Quality",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Import application modules
from analytics_hub_platform.ui.page_init import initialize_page
from analytics_hub_platform.domain.models import FilterParams
from analytics_hub_platform.domain.services import get_data_quality_metrics
from analytics_hub_platform.infrastructure.repository import get_repository
from analytics_hub_platform.infrastructure.settings import get_settings
from analytics_hub_platform.app.components import (
    chart_card_close,
    chart_card_open,
    mini_stat,
    render_page_header,
    render_sidebar,
    section_header,
    spacer,
)
from analytics_hub_platform.app.pages.data_management import render_data_management
from analytics_hub_platform.ui.theme import get_dark_theme


# Initialize page (session state, database, theme)
initialize_page()
dark_theme = get_dark_theme()

# Layout
side_col, main_col = st.columns([0.2, 0.8], gap="large")

with side_col:
    render_sidebar(active="Data")

with main_col:
    # Header
    render_page_header(
        "Data Quality",
        "Data health, completeness, and quality metrics",
        "📋"
    )

    spacer("md")

    try:
        tab_quality, tab_management = st.tabs(["✅ Quality", "📤 Management"])

        with tab_management:
            section_header("Data Management", "Upload, validate, and explore data", "📤")
            render_data_management()

        with tab_quality:
            settings = get_settings()
            repo = get_repository()
            df = repo.get_all_indicators(settings.default_tenant_id)

            year = st.session_state.year
            quarter = st.session_state.quarter
            region = st.session_state.region

            region_param = region if region != "all" else None
            filter_params = FilterParams(
                tenant_id=settings.default_tenant_id,
                year=year,
                quarter=quarter,
                region=region_param,
            )

            quality_metrics = get_data_quality_metrics(df, filter_params)

            section_header(
                "Data Health Overview", "Real-time quality and completeness indicators", "✅"
            )

            col1, col2, col3, col4 = st.columns(4)

            completeness = quality_metrics.get("completeness", 0)
            avg_quality = quality_metrics.get("avg_quality_score") or 0
            records = quality_metrics.get("records_count", 0)
            last_update = quality_metrics.get("last_update")
            update_str = last_update.strftime("%Y-%m-%d") if last_update else "N/A"

            with col1:
                mini_stat("Completeness", f"{completeness:.1f}%", "📊")
            with col2:
                mini_stat("Quality Score", f"{avg_quality:.1f}", "⭐")
            with col3:
                mini_stat("Records", f"{records:,}", "📝")
            with col4:
                mini_stat("Last Updated", update_str, "🕒")

            spacer("lg")

            section_header(
                "Quality Breakdown by Indicator", "Individual KPI data quality metrics", "🔍"
            )

            chart_card_open(
                "KPI Quality Analysis", "Completeness and quality scores per indicator"
            )

            current_df = df[(df["year"] == year) & (df["quarter"] == quarter)]
            if region != "all":
                current_df = current_df[current_df["region"] == region]

            kpi_columns = [
                col
                for col in df.columns
                if col
                not in [
                    "year",
                    "quarter",
                    "region",
                    "tenant_id",
                    "id",
                    "created_at",
                    "updated_at",
                ]
            ]

            quality_data = []
            for kpi in kpi_columns:
                if kpi in current_df.columns:
                    total = len(current_df)
                    non_null = current_df[kpi].notna().sum()
                    completeness_pct = (non_null / total * 100) if total > 0 else 0

                    quality_data.append(
                        {
                            "KPI": kpi.replace("_", " ").title(),
                            "Completeness (%)": f"{completeness_pct:.1f}",
                            "Records": non_null,
                            "Total": total,
                        }
                    )

            if quality_data:
                quality_df = pd.DataFrame(quality_data)
                st.dataframe(quality_df, width="stretch", hide_index=True)
            else:
                st.info("No data quality metrics available for this period")

            chart_card_close()

            spacer("lg")

            section_header("Raw Data Preview", "Sample of indicator data", "📄")

            chart_card_open("Data Sample", f"Showing data for Q{quarter} {year}")

            sample_df = current_df.head(100)
            if len(sample_df) > 0:
                st.dataframe(sample_df, width="stretch", height=400)

                csv = current_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Full Dataset (CSV)",
                    data=csv,
                    file_name=f"indicators_q{quarter}_{year}.csv",
                    mime="text/csv",
                )
            else:
                st.info("No data available for the selected period")

            chart_card_close()

            spacer("lg")

            section_header("Summary Statistics", "Statistical overview of the dataset", "📐")

            chart_card_open(
                "Descriptive Statistics", "Statistical summary of key indicators"
            )

            numeric_cols = current_df.select_dtypes(include=["float64", "int64"]).columns.tolist()
            numeric_cols = [col for col in numeric_cols if col not in ["year", "quarter"]]

            if numeric_cols:
                stats_df = current_df[numeric_cols].describe().round(2)
                st.dataframe(stats_df, width="stretch")
            else:
                st.info("No numeric data available for statistics")

            chart_card_close()

    except Exception as e:
        st.error(f"Error loading data quality metrics: {str(e)}")
        import traceback
        st.code(traceback.format_exc())
