"""
Trends Page
Time-series Analysis and Historical Performance

Displays:
- Selectable indicator trends over time
- Regional comparison charts
- Environmental multi-indicator trends
- Volatility and variance analysis
"""

import streamlit as st

# Page configuration
st.set_page_config(
    page_title="Trend Analysis",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Import application modules
from analytics_hub_platform.ui.page_init import initialize_page
from analytics_hub_platform.infrastructure.repository import get_repository
from analytics_hub_platform.infrastructure.settings import get_settings
from analytics_hub_platform.app.components import (
    card_container,
    render_sidebar,
    render_page_header,
    section_header,
    spacer,
)
from analytics_hub_platform.app.components.trend_charts import (
    render_trend_line_chart,
    render_multi_series_chart,
)
from analytics_hub_platform.app.components.anomaly_display import (
    render_anomaly_list,
)
from analytics_hub_platform.app.components.regional_charts import (
    render_regional_comparison,
)
from analytics_hub_platform.app.styles.tokens import colors
from analytics_hub_platform.ui.theme import get_dark_theme
from analytics_hub_platform.utils.dataframe_adapter import add_period_column
from analytics_hub_platform.domain.ml_services import AnomalyDetector, AnomalySeverity


# Initialize page (session state, database, theme)
initialize_page()
dark_theme = get_dark_theme()

# Layout
side_col, main_col = st.columns([0.2, 0.8], gap="large")

with side_col:
    render_sidebar(active="Trends")

with main_col:
    # Header
    render_page_header("Trend Analysis", "Historical performance and time-series analysis", "📊")

    # Filters
    col_f1, col_f2 = st.columns([1, 3])
    with col_f1:
        region = st.selectbox(
            "Region",
            [
                "all",
                "Riyadh",
                "Makkah",
                "Eastern Province",
                "Madinah",
                "Qassim",
                "Asir",
                "Tabuk",
                "Hail",
                "Northern Borders",
                "Jazan",
                "Najran",
                "Al Bahah",
                "Al Jawf",
            ],
            index=0,
            key="trend_filter_region",
        )
    with col_f2:
        st.info("💡 Analyze historical trends to identify patterns and forecast future performance")

    spacer("md")

    # Load data
    try:
        settings = get_settings()
        repo = get_repository()
        df = repo.get_all_indicators(settings.default_tenant_id)

        # Section 1: Single Indicator Trend
        section_header(
            "Indicator Trends", "Select an indicator to view historical performance", "📈"
        )

        with st.container():
            col1, col2 = st.columns([3, 1])

            with col2:
                kpi_options = {
                    "sustainability_index": "Sustainability Index",
                    "gdp_growth": "GDP Growth",
                    "renewable_share": "Renewable Energy",
                    "co2_index": "CO2 Intensity",
                    "unemployment_rate": "Unemployment",
                    "green_jobs": "Green Jobs",
                    "digital_readiness": "Digital Readiness",
                    "innovation_index": "Innovation Index",
                }
                selected_kpi = st.selectbox(
                    "Select Indicator",
                    list(kpi_options.keys()),
                    format_func=lambda x: kpi_options[x],
                    key="trend_kpi",
                )

            with col1:
                trend_df = df.copy()
                if region != "all":
                    trend_df = trend_df[trend_df["region"] == region]

                trend_agg = (
                    trend_df.groupby(["year", "quarter"]).agg({selected_kpi: "mean"}).reset_index()
                )
                trend_agg = add_period_column(trend_agg)
                trend_agg = trend_agg.sort_values(["year", "quarter"])

                # Use extracted component
                render_trend_line_chart(
                    df=trend_agg,
                    x_column="period",
                    y_column=selected_kpi,
                    title=kpi_options[selected_kpi],
                    show_trend_line=True,
                    primary_color=colors.accent_purple,
                    trend_color=colors.accent_primary,
                )

        spacer("lg")

        # Section 1.5: Early Warning System
        section_header("Early Warning System", "Anomaly detection for critical KPI deviations", "⚠️")

        try:
            detector = AnomalyDetector(zscore_threshold=2.5, critical_threshold=3.5)

            anomaly_kpis = [
                "sustainability_index",
                "gdp_growth",
                "unemployment_rate",
                "co2_index",
            ]
            available_anomaly_kpis = [k for k in anomaly_kpis if k in df.columns]

            all_anomalies = []
            for kpi in available_anomaly_kpis:
                kpi_df = df.groupby(["year", "quarter"]).agg({kpi: "mean"}).reset_index()
                kpi_df = kpi_df.rename(columns={kpi: "value"}).dropna()
                kpi_df = kpi_df.sort_values(["year", "quarter"])

                if len(kpi_df) >= 4:
                    higher_is_better = kpi not in ["unemployment_rate", "co2_index"]
                    anomalies = detector.detect_anomalies(kpi_df, kpi, "national", higher_is_better)
                    all_anomalies.extend(anomalies)

            critical = [a for a in all_anomalies if a.severity == AnomalySeverity.CRITICAL]
            warnings = [a for a in all_anomalies if a.severity == AnomalySeverity.WARNING]

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("🔴 Critical Alerts", len(critical))
            with col2:
                st.metric("🟡 Warnings", len(warnings))
            with col3:
                st.metric("📊 KPIs Monitored", len(available_anomaly_kpis))

            spacer("md")

            # Use extracted component for anomaly display
            render_anomaly_list(all_anomalies, max_display=5, sort_by_severity=True)

        except Exception as e:
            st.warning(f"⚠️ Anomaly detection unavailable: {str(e)}")

        spacer("lg")

        # Section 2: Regional Comparison
        section_header("Regional Comparison", "Performance across regions for current period", "🗺️")

        year = st.session_state.year
        quarter = st.session_state.quarter

        with card_container(
            "Regional Performance", f"Sustainability Index by Region - Q{quarter} {year}"
        ):
            regional_df = df[(df["year"] == year) & (df["quarter"] == quarter)].copy()

            # Use extracted component for regional comparison
            render_regional_comparison(
                regional_df,
                region_column="region",
                value_column="sustainability_index",
                title="Sustainability Index",
            )

        spacer("md")

        try:
            from analytics_hub_platform.ui.components.saudi_map import render_saudi_map

            with card_container(
                "Geographic Visualization",
                f"Interactive Regional KPI Map - Q{quarter} {year}",
            ):
                if len(regional_df) > 0:
                    map_kpis = [
                        "sustainability_index",
                        "gdp_growth",
                        "unemployment_rate",
                        "co2_index",
                    ]
                    available_map_kpis = [k for k in map_kpis if k in regional_df.columns]

                    if available_map_kpis:
                        selected_map_kpi = st.selectbox(
                            "Select KPI for Map",
                            available_map_kpis,
                            format_func=lambda x: x.replace("_", " ").title(),
                            key="map_kpi",
                        )

                        region_mapping = {
                            "Riyadh": "riyadh",
                            "Makkah": "makkah",
                            "Eastern Province": "eastern",
                            "Madinah": "madinah",
                            "Qassim": "qassim",
                            "Asir": "asir",
                            "Tabuk": "tabuk",
                            "Hail": "hail",
                            "Northern Borders": "northern_borders",
                            "Jazan": "jazan",
                            "Najran": "najran",
                            "Al Bahah": "bahah",
                            "Al Jawf": "jawf",
                        }

                        if "region" in regional_df.columns:
                            regional_map_agg = (
                                regional_df.groupby("region")
                                .agg({selected_map_kpi: "mean"})
                                .reset_index()
                            )
                            regional_map_agg["region_id"] = regional_map_agg["region"].map(
                                region_mapping
                            )
                            regional_map_agg = regional_map_agg.rename(
                                columns={selected_map_kpi: "value"}
                            )
                            regional_map_agg = regional_map_agg.dropna(
                                subset=["region_id", "value"]
                            )

                            if len(regional_map_agg) > 0:
                                fig = render_saudi_map(
                                    region_data=regional_map_agg,
                                    value_column="value",
                                    title=f"{selected_map_kpi.replace('_', ' ').title()} - Q{quarter} {year}",
                                    language=st.session_state.get("language", "en"),
                                )
                                st.plotly_chart(fig, use_container_width=True)
                            else:
                                st.info("No regional data available for map")
                    else:
                        st.info("No KPI data available for map")
                else:
                    st.info("No data for selected period")

        except ImportError:
            pass
        except Exception as e:
            st.warning(f"⚠️ Map unavailable: {str(e)}")

        spacer("lg")

        # Section 3: Environmental Multi-Indicator Trends
        section_header(
            "Environmental Trends", "Multi-indicator sustainability performance over time", "🌿"
        )

        with card_container("Environmental KPIs", "Tracking sustainability metrics"):
            env_kpis = [
                "co2_index",
                "renewable_share",
                "energy_intensity",
                "water_efficiency",
                "waste_recycling_rate",
                "air_quality_index",
                "forest_coverage",
                "green_jobs",
            ]

            trend_env = (
                df.groupby(["year", "quarter"])
                .agg({k: "mean" for k in env_kpis if k in df.columns})
                .reset_index()
            )
            trend_env = add_period_column(trend_env)
            trend_env = trend_env.sort_values(["year", "quarter"])

            label_map = {
                "co2_index": "CO2 Intensity",
                "renewable_share": "Renewables %",
                "energy_intensity": "Energy Intensity",
                "water_efficiency": "Water Efficiency",
                "waste_recycling_rate": "Recycling Rate",
                "air_quality_index": "Air Quality",
                "forest_coverage": "Forest Coverage",
                "green_jobs": "Green Jobs",
            }

            # Use extracted component for multi-series chart
            available_env_kpis = [k for k in env_kpis if k in trend_env.columns]
            render_multi_series_chart(
                df=trend_env,
                x_column="period",
                y_columns=available_env_kpis,
                labels=label_map,
                height=420,
            )

    except Exception as e:
        st.error(f"Error loading trend data: {str(e)}")
        import traceback

        st.code(traceback.format_exc())
