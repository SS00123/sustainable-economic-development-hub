"""
Help System Utility
Sustainable Economic Development Analytics Hub
Ministry of Economy and Planning

Provides contextual help content, tooltips, and documentation.
"""

from dataclasses import dataclass


@dataclass
class HelpContent:
    """Help content structure."""

    title: str
    description: str
    examples: list | None = None
    related_topics: list | None = None
    video_url: str | None = None


# Help content database
HELP_CONTENT: dict[str, dict[str, HelpContent]] = {
    "en": {
        "sustainability_index": HelpContent(
            title="Sustainability Index",
            description=(
                "The Sustainability Index is a composite score ranging from 0-100 that measures "
                "overall environmental and economic sustainability performance. It combines "
                "multiple indicators including CO2 emissions, renewable energy adoption, "
                "green investment levels, and resource efficiency metrics."
            ),
            examples=[
                "A score of 75+ indicates strong sustainability performance",
                "A score of 50-74 indicates moderate progress",
                "A score below 50 indicates areas needing improvement",
            ],
            related_topics=["co2_per_gdp", "renewable_energy", "green_investment"],
        ),
        "co2_per_gdp": HelpContent(
            title="CO₂ per GDP",
            description=(
                "Measures carbon dioxide emissions per unit of GDP, indicating the carbon "
                "intensity of economic output. Lower values are better, showing more efficient "
                "economic production with less environmental impact."
            ),
            examples=[
                "0.3 kg CO₂/SAR GDP = Efficient, low-carbon economy",
                "0.5 kg CO₂/SAR GDP = Average carbon intensity",
                "0.8+ kg CO₂/SAR GDP = High carbon intensity",
            ],
            related_topics=["co2_per_capita", "sustainability_index"],
        ),
        "renewable_energy": HelpContent(
            title="Renewable Energy Percentage",
            description=(
                "The share of total energy consumption that comes from renewable sources "
                "such as solar, wind, and hydroelectric power. Higher percentages indicate "
                "progress toward clean energy transition goals."
            ),
            examples=[
                "Saudi Arabia's Vision 2030 targets 50% renewable energy",
                "Current progress varies by region",
            ],
            related_topics=["energy_intensity", "sustainability_index"],
        ),
        "green_investment": HelpContent(
            title="Green Investment Percentage",
            description=(
                "The proportion of total investment directed toward environmentally sustainable "
                "projects and initiatives. This includes renewable energy, sustainable infrastructure, "
                "and environmental protection programs."
            ),
            examples=[
                "Green bonds and sustainable finance instruments",
                "Investment in clean technology",
                "Environmental infrastructure projects",
            ],
        ),
        "data_quality": HelpContent(
            title="Data Quality Score",
            description=(
                "A composite measure of data reliability, completeness, and timeliness. "
                "Higher scores indicate more trustworthy data suitable for decision-making."
            ),
            examples=[
                "90+: Excellent quality, suitable for all reporting",
                "70-89: Good quality, minor gaps acceptable",
                "50-69: Moderate quality, use with caution",
                "<50: Poor quality, needs remediation",
            ],
        ),
        "executive_view": HelpContent(
            title="Executive Dashboard",
            description=(
                "High-level strategic view designed for Minister-level decision makers. "
                "Shows key performance indicators at a glance with traffic-light status "
                "indicators and trend arrows. Focuses on the 'what' rather than the 'how'."
            ),
            related_topics=["director_view", "analyst_view"],
        ),
        "director_view": HelpContent(
            title="Director Dashboard",
            description=(
                "Detailed analytics view for department directors and managers. "
                "Includes regional comparisons, quarterly trends, and variance analysis. "
                "Enables drill-down into specific indicators and time periods."
            ),
            related_topics=["executive_view", "analyst_view"],
        ),
        "analyst_view": HelpContent(
            title="Analyst Dashboard",
            description=(
                "Data-rich view for analysts and researchers. Provides full access to "
                "raw data tables, export capabilities, and detailed statistical analysis. "
                "Supports data exploration and custom reporting."
            ),
            related_topics=["executive_view", "director_view", "export"],
        ),
        "export": HelpContent(
            title="Export Features",
            description=(
                "Export dashboard data and visualizations in multiple formats:\n"
                "• PDF: Professional reports with charts and narrative\n"
                "• PowerPoint: Presentation-ready slides\n"
                "• Excel: Full data with formatting and charts"
            ),
        ),
        "filters": HelpContent(
            title="Dashboard Filters",
            description=(
                "Use filters to customize your view:\n"
                "• Year: Select reporting year (2019-2024)\n"
                "• Quarter: Q1-Q4 or all quarters\n"
                "• Region: Filter by specific region or view all\n"
                "• Language: Switch between English and Arabic"
            ),
        ),
    },
    "ar": {
        "sustainability_index": HelpContent(
            title="مؤشر الاستدامة",
            description=(
                "مؤشر الاستدامة هو نتيجة مركبة تتراوح من 0-100 تقيس الأداء العام "
                "للاستدامة البيئية والاقتصادية. يجمع بين مؤشرات متعددة بما في ذلك "
                "انبعاثات ثاني أكسيد الكربون واعتماد الطاقة المتجددة ومستويات الاستثمار الأخضر."
            ),
            examples=[
                "درجة 75+ تشير إلى أداء استدامة قوي",
                "درجة 50-74 تشير إلى تقدم معتدل",
                "درجة أقل من 50 تشير إلى مجالات تحتاج تحسين",
            ],
        ),
        "co2_per_gdp": HelpContent(
            title="ثاني أكسيد الكربون لكل ناتج محلي",
            description=(
                "يقيس انبعاثات ثاني أكسيد الكربون لكل وحدة من الناتج المحلي الإجمالي، "
                "مما يشير إلى كثافة الكربون في الإنتاج الاقتصادي."
            ),
        ),
        "renewable_energy": HelpContent(
            title="نسبة الطاقة المتجددة",
            description=(
                "حصة إجمالي استهلاك الطاقة التي تأتي من مصادر متجددة "
                "مثل الطاقة الشمسية وطاقة الرياح والطاقة الكهرومائية."
            ),
        ),
        "executive_view": HelpContent(
            title="لوحة القيادة التنفيذية",
            description=("عرض استراتيجي عالي المستوى مصمم لصناع القرار على مستوى الوزراء."),
        ),
    },
}


# Tooltips database (shorter, inline help)
TOOLTIPS: dict[str, dict[str, str]] = {
    "en": {
        "sustainability_index": "Composite score (0-100) measuring overall sustainability",
        "co2_per_gdp": "Carbon emissions per unit of economic output (kg CO₂/SAR)",
        "co2_per_capita": "Carbon emissions per person (tonnes CO₂/person)",
        "renewable_energy_pct": "Share of energy from renewable sources (%)",
        "green_investment_pct": "Investment in sustainable projects (%)",
        "energy_intensity": "Energy consumption per unit of GDP",
        "recycling_rate": "Waste recycled vs total waste (%)",
        "water_efficiency": "Water use efficiency index",
        "green_jobs_pct": "Employment in green sectors (%)",
        "data_quality_score": "Data reliability score (0-100)",
        "year": "Select reporting year",
        "quarter": "Select quarter (Q1-Q4)",
        "region": "Filter by region",
        "language": "Switch display language",
        "export_pdf": "Download as PDF report",
        "export_ppt": "Download as PowerPoint",
        "export_excel": "Download as Excel workbook",
        "refresh": "Refresh dashboard data",
        "help": "Open help documentation",
    },
    "ar": {
        "sustainability_index": "نتيجة مركبة (0-100) تقيس الاستدامة الشاملة",
        "co2_per_gdp": "انبعاثات الكربون لكل وحدة إنتاج اقتصادي",
        "renewable_energy_pct": "حصة الطاقة من مصادر متجددة (%)",
        "green_investment_pct": "الاستثمار في المشاريع المستدامة (%)",
        "year": "اختر سنة التقرير",
        "quarter": "اختر الربع (ر1-ر4)",
        "region": "تصفية حسب المنطقة",
        "language": "تبديل لغة العرض",
    },
}


def get_help_content(topic: str, language: str = "en") -> HelpContent | None:
    """
    Get help content for a topic.

    Args:
        topic: Help topic key
        language: Language code (en/ar)

    Returns:
        HelpContent object or None if not found
    """
    lang_content = HELP_CONTENT.get(language, HELP_CONTENT.get("en", {}))
    return lang_content.get(topic)


def get_tooltip(key: str, language: str = "en") -> str:
    """
    Get tooltip text for a UI element.

    Args:
        key: Tooltip key
        language: Language code (en/ar)

    Returns:
        Tooltip text or empty string if not found
    """
    lang_tooltips = TOOLTIPS.get(language, TOOLTIPS.get("en", {}))
    return lang_tooltips.get(key, "")


def get_all_help_topics(language: str = "en") -> dict[str, str]:
    """
    Get all available help topics.

    Args:
        language: Language code

    Returns:
        Dictionary of topic keys to titles
    """
    lang_content = HELP_CONTENT.get(language, HELP_CONTENT.get("en", {}))
    return {key: content.title for key, content in lang_content.items()}


def format_help_markdown(content: HelpContent) -> str:
    """
    Format HelpContent as markdown.

    Args:
        content: HelpContent object

    Returns:
        Formatted markdown string
    """
    lines = [f"## {content.title}", "", content.description, ""]

    if content.examples:
        lines.append("### Examples")
        for example in content.examples:
            lines.append(f"- {example}")
        lines.append("")

    if content.related_topics:
        lines.append("### Related Topics")
        lines.append(", ".join(content.related_topics))
        lines.append("")

    return "\n".join(lines)


def search_help(query: str, language: str = "en") -> list:
    """
    Search help content by query.

    Args:
        query: Search query
        language: Language code

    Returns:
        List of matching topic keys
    """
    query_lower = query.lower()
    lang_content = HELP_CONTENT.get(language, HELP_CONTENT.get("en", {}))

    matches = []
    for key, content in lang_content.items():
        if (
            query_lower in key.lower()
            or query_lower in content.title.lower()
            or query_lower in content.description.lower()
        ):
            matches.append(key)

    return matches
