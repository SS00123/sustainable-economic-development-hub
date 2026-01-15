"""Help & documentation renderers.

Moved from the legacy Streamlit documentation page to keep `pages/` thin.
"""

from __future__ import annotations

import streamlit as st


def render_about_section() -> None:
    st.header("ℹ️ About This Dashboard")

    st.markdown(
        """
    ### Sustainable Economic Development Analytics Hub

    This dashboard provides comprehensive analytics and visualization of Saudi Arabia's
    progress toward sustainable economic development goals under **Vision 2030**.

    #### Purpose
    - Monitor key performance indicators (KPIs) across economic, social, and environmental pillars
    - Track regional progress and identify areas requiring attention
    - Provide data-driven insights for policy decision-making
    - Enable transparent reporting to stakeholders

    #### Key Features
    - **Real-time KPI tracking** with trend analysis
    - **Regional breakdowns** for all 13 Saudi regions
    - **Multi-language support** (English and Arabic with RTL)
    - **Data quality monitoring** and validation
    - **Export capabilities** (CSV, PNG, PDF)
    - **Shareable views** with URL-based state preservation

    #### Audience
    - Executive leadership for strategic oversight
    - Analysts for detailed data exploration
    - Directors for regional performance monitoring
    - External stakeholders for transparency reporting
    """
    )

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            """
        #### Version Information
        - **Version:** 1.0.0
        - **Last Updated:** January 2026
        - **Data Refresh:** Quarterly
        """
        )

    with col2:
        st.markdown(
            """
        #### Contact
        - **Owner:** Ministry of Economy and Planning
        - **Support:** analytics-support@mep.gov.sa
        - **Documentation:** Internal wiki
        """
        )


def render_methodology_section() -> None:
    st.header("📐 Methodology")

    st.markdown(
        """
    ### Data Collection & Processing

    #### Collection Frequency
    - **Quarterly updates** for most indicators
    - **Monthly updates** for real-time economic indicators
    - **Annual updates** for structural metrics

    #### Data Processing Pipeline
    1. **Ingestion**: Data received from source systems (GASTAT, MISA, SEC, etc.)
    2. **Validation**: Automated checks against DATA_CONTRACT specifications
    3. **Transformation**: Standardization, normalization, and derived calculations
    4. **Quality Scoring**: Each record receives a data quality score (0-100)
    5. **Storage**: Validated data stored in analytical database
    6. **Visualization**: Real-time dashboard rendering

    ---

    ### Calculation Methodologies

    #### Sustainability Index
    The composite Sustainability Index is calculated as a weighted average:

    ```
    Sustainability Index =
        35% × Economic Score +
        35% × Social Score +
        30% × Environmental Score
    ```

    ---

    ### Data Quality Dimensions

    | Dimension | Check | Threshold |
    |-----------|-------|-----------|
    | Completeness | Required fields filled | ≥ 95% |
    | Timeliness | Data freshness | ≤ 45 days old |
    | Validity | Values within defined ranges | ≥ 99% |
    | Consistency | No duplicate records | 100% |
    | Outliers | Z-score within bounds | < 5% flagged |
    """
    )


def render_sources_section() -> None:
    st.header("📚 Data Sources")

    st.markdown(
        """
    ### Primary Data Sources

    The dashboard integrates data from the following authoritative sources:

    | Source | Acronym | Data Provided | Update Frequency |
    |--------|---------|---------------|------------------|
    | General Authority for Statistics | GASTAT | GDP, unemployment, population, surveys | Quarterly |
    | Ministry of Investment Saudi Arabia | MISA | Foreign direct investment, business licensing | Monthly |
    | Saudi Electricity Company | SEC | Energy production, renewable capacity | Monthly |
    | Ministry of Commerce | MOC | Trade, export diversification | Quarterly |
    | Presidency of Meteorology and Environment | PME | Emissions, air quality, environmental indices | Monthly |
    | Ministry of Environment, Water and Agriculture | MEWA | Water resources, agriculture, sustainability | Quarterly |
    | Human Resources Development Fund | HRDF | Skills gap, training, employment programs | Quarterly |
    | Ministry of Labor and Social Development | MLSD | Green jobs, labor market statistics | Quarterly |
    | King Abdulaziz City for Science and Technology | KACST | Innovation indices, R&D metrics | Annual |
    | Ministry of Communications and IT | MCIT | Digital readiness, ICT adoption | Quarterly |
    """
    )


def render_glossary_section() -> None:
    st.header("📖 Glossary")

    glossary = {
        "CAGR": "Compound Annual Growth Rate - The mean annual growth rate over a specified period longer than one year.",
        "CO2 Index": "A normalized score (0-100) representing carbon emissions efficiency relative to economic output.",
        "Economic Complexity Index": "A measure of the productive capabilities of a country based on the diversity and sophistication of its exports.",
        "Export Diversity Index": "A score (0-100) measuring the diversification of exports across product categories and trading partners.",
        "FDI": "Foreign Direct Investment - Investment from foreign entities into domestic businesses and assets.",
        "GDP": "Gross Domestic Product - The total monetary value of all goods and services produced within a country's borders.",
        "GDP Growth": "The year-over-year percentage change in Gross Domestic Product, adjusted for inflation.",
        "Green Jobs": "Employment in economic sectors and activities that contribute to preserving or restoring environmental quality.",
        "KPI": "Key Performance Indicator - A measurable value that demonstrates how effectively an objective is being achieved.",
        "QoQ": "Quarter-over-Quarter - A comparison metric between the current quarter and the immediately preceding quarter.",
        "Renewable Share": "The percentage of total energy consumption or production derived from renewable sources (solar, wind, etc.).",
        "Skills Gap Index": "A measure (0-100) of the mismatch between available workforce skills and employer requirements.",
        "Sustainability Index": "A composite score (0-100) combining economic, social, and environmental performance indicators.",
        "Vision 2030": "Saudi Arabia's strategic framework for reducing dependence on oil, diversifying the economy, and developing public sectors.",
        "YoY": "Year-over-Year - A comparison metric between the current period and the same period in the previous year.",
    }

    search = st.text_input("🔍 Search terms", "")
    st.markdown("---")

    for term, definition in sorted(glossary.items()):
        if search.lower() in term.lower() or search.lower() in definition.lower():
            st.markdown(f"**{term}**")
            st.markdown(f"> {definition}")
            st.markdown("")


def render_faq_section() -> None:
    st.header("❓ Frequently Asked Questions")

    with st.expander("How often is the dashboard updated?"):
        st.markdown(
            """
        The dashboard refreshes data quarterly for most indicators.
        Some real-time indicators (energy, economic) update monthly.
        The refresh timestamp is shown on the Diagnostics page.
        """
        )

    with st.expander("What does the Sustainability Index represent?"):
        st.markdown(
            """
        The Sustainability Index is a composite score (0-100) combining economic, social,
        and environmental performance indicators.
        """
        )

    with st.expander("How can I export data from the dashboard?"):
        st.markdown(
            """
        Several export options are available:
        - **CSV**: Download raw data tables for analysis
        - **PNG**: Save chart visualizations as images
        - **PDF**: Generate Executive Brief reports
        """
        )

    with st.expander("How do I share a specific view with colleagues?"):
        st.markdown(
            """
        1. Configure your desired filters and settings
        2. Use the Share panel to copy a URL that restores the view
        """
        )

    with st.expander("Who should I contact for data issues?"):
        st.markdown(
            """
        - **Technical Support**: analytics-support@mep.gov.sa
        - **Feature Requests**: Submit via internal ticketing system
        """
        )


def render_help_page() -> None:
    """Main help page renderer."""
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        [
            "ℹ️ About",
            "📐 Methodology",
            "📚 Sources",
            "📖 Glossary",
            "❓ FAQ",
        ]
    )

    with tab1:
        render_about_section()

    with tab2:
        render_methodology_section()

    with tab3:
        render_sources_section()

    with tab4:
        render_glossary_section()

    with tab5:
        render_faq_section()
