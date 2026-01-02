"""
Narrative Generation Utility
Sustainable Economic Development Analytics Hub
Ministry of Economy and Planning

Generates human-readable narratives and insights from data.
"""

from typing import Any

import pandas as pd

from analytics_hub_platform.domain.models import DashboardSummary

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def _plural(n: int, singular: str, plural: str) -> str:
    """Return singular or plural form based on count."""
    return singular if n == 1 else plural


def _get_item_name(item: dict[str, Any]) -> str:
    """
    Get display name from an item dict, supporting multiple key formats.

    Args:
        item: Dictionary that may contain display_name, name, or kpi_name

    Returns:
        The best available name, or 'Unknown' if none found
    """
    return item.get("display_name") or item.get("name") or item.get("kpi_name") or "Unknown"


def _get_item_value(item: dict[str, Any]) -> float:
    """
    Get value from an item dict, supporting multiple key formats.

    Args:
        item: Dictionary that may contain change_percent, value, or achievement

    Returns:
        The best available value, or 0.0 if none found
    """
    value = item.get("change_percent") or item.get("value") or item.get("achievement") or 0.0
    return float(value) if value is not None else 0.0


def _format_signed_percent(value: float) -> str:
    """Format a value as a signed percentage string."""
    if value > 0:
        return f"+{value:.1f}%"
    elif value < 0:
        return f"{value:.1f}%"
    else:
        return "0.0%"


# =============================================================================
# MAIN NARRATIVE GENERATORS
# =============================================================================


def generate_narrative(
    summary: DashboardSummary,
    language: str = "en",
) -> str:
    """
    Generate executive narrative from dashboard summary.

    Args:
        summary: DashboardSummary object with KPI data
        language: Language code (en/ar)

    Returns:
        Narrative text
    """
    if language == "ar":
        return _generate_arabic_narrative(summary)
    return _generate_english_narrative(summary)


def generate_executive_narrative(
    snapshot: Any,
    language: str = "en",
) -> str:
    """
    Generate executive narrative from executive snapshot data.

    This is an alias for generate_narrative that accepts
    the snapshot dictionary from get_executive_snapshot().

    Args:
        snapshot: Dictionary or object with summary data
        language: Language code (en/ar)

    Returns:
        Narrative text
    """
    # Convert snapshot to DashboardSummary if it's a dict
    if isinstance(snapshot, dict):
        # Extract metrics to count statuses
        metrics = snapshot.get("metrics", {})
        total = len(metrics)
        on_target = sum(1 for m in metrics.values() if m.get("status") == "green")
        warning = sum(1 for m in metrics.values() if m.get("status") == "amber")
        critical = sum(1 for m in metrics.values() if m.get("status") == "red")

        # Count improvements and declines
        improvements = snapshot.get("top_improvements", [])
        deteriorations = snapshot.get("top_deteriorations", [])

        # Get sustainability index
        sustainability_index = None
        if "sustainability_index" in metrics:
            sustainability_index = metrics["sustainability_index"].get("value")

        summary = DashboardSummary(
            total_indicators=total,
            on_target_count=on_target,
            warning_count=warning,
            critical_count=critical,
            improving_count=len(improvements),
            declining_count=len(deteriorations),
            average_achievement=0.0,
            sustainability_index=sustainability_index,
            top_performers=improvements,
            attention_needed=deteriorations,
            period=snapshot.get("period", ""),
        )
        summary.calculate_percentages()
    elif isinstance(snapshot, DashboardSummary):
        summary = snapshot
    else:
        # Try to use as-is (duck typing)
        summary = snapshot

    return generate_narrative(summary, language)


def generate_director_narrative(
    snapshot: Any,
    language: str = "en",
) -> str:
    """
    Generate director-level narrative with more operational detail.

    Args:
        snapshot: Dictionary or DashboardSummary with summary data
        language: Language code (en/ar)

    Returns:
        Narrative text for director view
    """
    # Convert snapshot to DashboardSummary if needed
    if isinstance(snapshot, dict):
        # Extract metrics to count statuses
        metrics = snapshot.get("metrics", {})
        total = len(metrics)
        on_target = sum(1 for m in metrics.values() if m.get("status") == "green")
        warning = sum(1 for m in metrics.values() if m.get("status") == "amber")
        critical = sum(1 for m in metrics.values() if m.get("status") == "red")

        # Count improvements and declines
        improvements = snapshot.get("top_improvements", [])
        deteriorations = snapshot.get("top_deteriorations", [])

        # Get sustainability index
        sustainability_index = None
        if "sustainability_index" in metrics:
            sustainability_index = metrics["sustainability_index"].get("value")

        summary = DashboardSummary(
            total_indicators=total,
            on_target_count=on_target,
            warning_count=warning,
            critical_count=critical,
            improving_count=len(improvements),
            declining_count=len(deteriorations),
            average_achievement=0.0,
            sustainability_index=sustainability_index,
            top_performers=improvements,
            attention_needed=deteriorations,
            period=snapshot.get("period", ""),
        )
        summary.calculate_percentages()
    elif isinstance(snapshot, DashboardSummary):
        summary = snapshot
    else:
        summary = snapshot

    if language == "ar":
        return _generate_arabic_director_narrative(summary)
    return _generate_english_director_narrative(summary)


def _generate_english_director_narrative(summary: DashboardSummary) -> str:
    """Generate English director-level narrative with clear structure."""
    lines = []

    # Header
    lines.append("**Operational Performance Summary**")
    lines.append("")

    total = summary.total_indicators
    if total > 0:
        on_target_pct = (summary.on_target_count / total) * 100
        warning_pct = (summary.warning_count / total) * 100
        critical_pct = (summary.critical_count / total) * 100

        # Use proper pluralization
        ind_word = _plural(total, "indicator", "indicators")
        lines.append(
            f"Of **{total}** monitored {ind_word}: "
            f"**{summary.on_target_count}** ({on_target_pct:.0f}%) on target, "
            f"**{summary.warning_count}** ({warning_pct:.0f}%) {_plural(summary.warning_count, 'requires', 'require')} attention, "
            f"**{summary.critical_count}** ({critical_pct:.0f}%) {_plural(summary.critical_count, 'is', 'are')} critical."
        )
        lines.append("")

    # Improvement/decline summary with pluralization
    if summary.improving_count > 0 or summary.declining_count > 0:
        imp_word = _plural(summary.improving_count, "indicator", "indicators")
        dec_word = _plural(summary.declining_count, "indicator", "indicators")
        lines.append(
            f"**{summary.improving_count}** {imp_word} improving, "
            f"**{summary.declining_count}** {dec_word} declining."
        )
        lines.append("")

    # Top performers with proper name and value resolution
    if summary.top_performers:
        lines.append("**Top Performers:**")
        for perf in summary.top_performers[:3]:
            name = _get_item_name(perf)
            value = _get_item_value(perf)
            lines.append(f"- {name}: {_format_signed_percent(value)}")
        lines.append("")

    # Needs attention with proper name and value resolution
    if summary.attention_needed:
        lines.append("**Needs Attention:**")
        for item in summary.attention_needed[:3]:
            name = _get_item_name(item)
            value = _get_item_value(item)
            lines.append(f"- {name}: {_format_signed_percent(value)}")

    return "\n".join(lines)


def _generate_arabic_director_narrative(summary: DashboardSummary) -> str:
    """Generate Arabic director-level narrative."""
    lines = []

    lines.append("**ملخص الأداء التشغيلي**")
    lines.append("")

    total = summary.total_indicators
    if total > 0:
        on_pct = (summary.on_target_count / total) * 100
        warn_pct = (summary.warning_count / total) * 100
        crit_pct = (summary.critical_count / total) * 100
        lines.append(
            f"من **{total}** مؤشر: "
            f"**{summary.on_target_count}** ({on_pct:.0f}%) على المسار، "
            f"**{summary.warning_count}** ({warn_pct:.0f}%) تتطلب اهتماماً، "
            f"**{summary.critical_count}** ({crit_pct:.0f}%) حرجة."
        )
        lines.append("")

    if summary.improving_count > 0 or summary.declining_count > 0:
        lines.append(
            f"**{summary.improving_count}** مؤشر في تحسن، **{summary.declining_count}** في تراجع."
        )

    return "\n".join(lines)


# =============================================================================
# NARRATIVE SECTION BUILDERS
# =============================================================================


def _build_executive_summary_section(summary: DashboardSummary) -> list[str]:
    """Build the executive summary section of the narrative."""
    lines = []
    lines.append("### 📊 Executive Summary")
    lines.append("")

    if summary.sustainability_index is not None:
        index_val = summary.sustainability_index
        if index_val >= 70:
            status_emoji = "🟢"
            assessment = "**strong performance**"
        elif index_val >= 50:
            status_emoji = "🟡"
            assessment = "**moderate progress**"
        else:
            status_emoji = "🔴"
            assessment = "**significant challenges**"

        lines.append(
            f"{status_emoji} The **Sustainability Index** stands at **{index_val:.1f} points**, "
            f"reflecting {assessment} across economic, environmental, and social dimensions."
        )
        lines.append("")

    if summary.period:
        lines.append(f"📅 *Reporting Period: {summary.period}*")
        lines.append("")
        lines.append("---")
        lines.append("")

    return lines


def _build_performance_distribution_section(summary: DashboardSummary) -> list[str]:
    """Build the performance distribution section of the narrative."""
    lines = []

    if summary.total_indicators <= 0:
        return lines

    lines.append("### 🎯 Performance Distribution")
    lines.append("")

    total = summary.total_indicators
    on_target_pct = (summary.on_target_count / total) * 100
    warning_pct = (summary.warning_count / total) * 100
    critical_pct = (summary.critical_count / total) * 100

    if summary.on_target_count > 0:
        ind_word = _plural(summary.on_target_count, "indicator", "indicators")
        lines.append(
            f"🟢 **On Track** — **{summary.on_target_count}** {ind_word} ({on_target_pct:.0f}%) "
            f"meeting or exceeding targets"
        )
        lines.append("")

    if summary.warning_count > 0:
        ind_word = _plural(summary.warning_count, "indicator", "indicators")
        lines.append(
            f"🟡 **Monitoring Required** — **{summary.warning_count}** {ind_word} ({warning_pct:.0f}%) "
            f"within acceptable range but below optimal"
        )
        lines.append("")

    if summary.critical_count > 0:
        ind_word = _plural(summary.critical_count, "indicator", "indicators")
        lines.append(
            f"🔴 **Action Needed** — **{summary.critical_count}** {ind_word} ({critical_pct:.0f}%) "
            f"require immediate corrective measures"
        )
        lines.append("")

    lines.append("---")
    lines.append("")

    return lines


def _build_trend_analysis_section(summary: DashboardSummary) -> list[str]:
    """Build the trend analysis section of the narrative."""
    lines = []

    if summary.improving_count <= 0 and summary.declining_count <= 0:
        return lines

    lines.append("### 📈 Trend Analysis")
    lines.append("")

    imp_word = _plural(summary.improving_count, "indicator", "indicators")
    dec_word = _plural(summary.declining_count, "indicator", "indicators")

    if summary.improving_count > summary.declining_count:
        trend_emoji = "📈"
        trend_assessment = "**Positive trajectory**"
    elif summary.declining_count > summary.improving_count:
        trend_emoji = "📉"
        trend_assessment = "**Concerning trends**"
    else:
        trend_emoji = "↔️"
        trend_assessment = "**Mixed dynamics**"

    lines.append(
        f"{trend_emoji} {trend_assessment}: **{summary.improving_count}** {imp_word} showing improvement, "
        f"while **{summary.declining_count}** {dec_word} experiencing decline."
    )
    lines.append("")
    lines.append("---")
    lines.append("")

    return lines


def _build_key_highlights_section(summary: DashboardSummary) -> list[str]:
    """Build the key highlights section of the narrative."""
    lines = []

    has_highlights = summary.top_performers or summary.attention_needed
    if not has_highlights:
        return lines

    lines.append("### 💡 Key Highlights")
    lines.append("")

    # Top performers with context
    if summary.top_performers:
        lines.append("**🏆 Outstanding Performers**")
        lines.append("")
        for idx, item in enumerate(summary.top_performers[:3], 1):
            name = _get_item_name(item)
            value = _get_item_value(item)

            if value > 20:
                context = " (exceptional growth)"
            elif value > 10:
                context = " (strong improvement)"
            else:
                context = ""

            lines.append(f"{idx}. **{name}**: {_format_signed_percent(value)}{context}")
        lines.append("")

    # Areas needing attention with urgency
    if summary.attention_needed:
        lines.append("**⚠️ Priority Areas for Action**")
        lines.append("")
        for idx, item in enumerate(summary.attention_needed[:3], 1):
            name = _get_item_name(item)
            value = _get_item_value(item)

            abs_value = abs(value)
            if abs_value > 15:
                urgency = " — *High priority*"
            elif abs_value > 8:
                urgency = " — *Moderate priority*"
            else:
                urgency = ""

            lines.append(f"{idx}. **{name}**: {_format_signed_percent(value)}{urgency}")
        lines.append("")

    return lines


def _build_strategic_recommendation_section(summary: DashboardSummary) -> list[str]:
    """Build the strategic recommendation section of the narrative."""
    lines = []

    if summary.sustainability_index is None:
        return lines

    lines.append("---")
    lines.append("")
    lines.append("### 🎯 Strategic Recommendation")
    lines.append("")

    index_val = summary.sustainability_index
    if index_val >= 70:
        lines.append(
            "✅ **Maintain and Optimize**: Current performance is strong. "
            "Focus on sustaining gains, sharing best practices across lagging indicators, "
            "and preparing for next-phase targets."
        )
    elif index_val >= 50:
        lines.append(
            "⚡ **Accelerate Progress**: Performance is on track but requires focused intervention. "
            "Prioritize resources toward critical/warning indicators, establish quarterly review checkpoints, "
            "and strengthen cross-ministerial coordination."
        )
    else:
        lines.append(
            "🚨 **Urgent Action Required**: Current trajectory requires immediate course correction. "
            "Recommend establishing a task force to address critical indicators, "
            "conducting root-cause analysis for declining metrics, and reallocating resources to high-impact interventions."
        )

    return lines


def _generate_english_narrative(summary: DashboardSummary) -> str:
    """Generate English executive narrative with clear paragraph structure."""
    lines: list[str] = []

    lines.extend(_build_executive_summary_section(summary))
    lines.extend(_build_performance_distribution_section(summary))
    lines.extend(_build_trend_analysis_section(summary))
    lines.extend(_build_key_highlights_section(summary))
    lines.extend(_build_strategic_recommendation_section(summary))

    return "\n".join(lines)


def _generate_arabic_narrative(summary: DashboardSummary) -> str:
    """Generate Arabic narrative."""
    lines = []

    lines.append("**نظرة عامة على الأداء المستدام**")
    lines.append("")

    if summary.sustainability_index is not None:
        index_val = summary.sustainability_index
        if index_val >= 70:
            assessment = "أداء قوي"
        elif index_val >= 50:
            assessment = "تقدم معتدل"
        else:
            assessment = "مجالات تحتاج إلى اهتمام"

        lines.append(f"يبلغ مؤشر الاستدامة الحالي **{index_val:.1f}**، مما يشير إلى {assessment}.")
        lines.append("")

    if summary.period:
        lines.append(f"*فترة التقرير: {summary.period}*")
        lines.append("")

    # Use count fields instead of kpis list
    if summary.total_indicators > 0:
        green_count = summary.on_target_count
        amber_count = summary.warning_count
        red_count = summary.critical_count

        if green_count:
            lines.append(f"**نقاط القوة:** {green_count} مؤشرات على المسار الصحيح")
        if amber_count:
            lines.append(f"**تحتاج متابعة:** {amber_count} مؤشرات تتطلب المراقبة")
        if red_count:
            lines.append(f"**تتطلب إجراء:** {red_count} مؤشرات تحتاج اهتمام فوري")

    return "\n".join(lines)


def generate_kpi_insight(
    kpi_name: str,
    current_value: float,
    previous_value: float | None = None,
    target: float | None = None,
    unit: str = "",
    higher_is_better: bool = True,
    language: str = "en",
) -> str:
    """
    Generate insight text for a single KPI.

    Args:
        kpi_name: Name of the KPI
        current_value: Current value
        previous_value: Previous period value for comparison
        target: Target value
        unit: Unit of measurement
        higher_is_better: Whether higher values are better
        language: Language code

    Returns:
        Insight text
    """
    parts = []

    # Current state
    parts.append(f"{kpi_name}: **{current_value:.2f}{unit}**")

    # Change from previous
    if previous_value is not None and previous_value != 0:
        change = ((current_value - previous_value) / abs(previous_value)) * 100
        direction = "up" if change > 0 else "down"

        if language == "ar":
            direction = "ارتفاع" if change > 0 else "انخفاض"
            parts.append(f"({direction} {abs(change):.1f}%)")
        else:
            parts.append(f"({direction} {abs(change):.1f}% vs prior period)")

        # Assessment
        is_positive = (change > 0 and higher_is_better) or (change < 0 and not higher_is_better)
        if is_positive:
            parts.append("✓" if language == "en" else "✓")
        else:
            parts.append("⚠")

    # Target comparison
    if target is not None:
        gap = current_value - target
        gap_pct = (gap / target) * 100 if target != 0 else 0

        if language == "ar":
            if gap >= 0 and higher_is_better:
                parts.append(f"(تجاوز الهدف بنسبة {abs(gap_pct):.1f}%)")
            elif gap < 0 and higher_is_better:
                parts.append(f"(أقل من الهدف بنسبة {abs(gap_pct):.1f}%)")
        else:
            if gap >= 0 and higher_is_better:
                parts.append(f"(above target by {abs(gap_pct):.1f}%)")
            elif gap < 0 and higher_is_better:
                parts.append(f"(below target by {abs(gap_pct):.1f}%)")

    return " ".join(parts)


def generate_trend_commentary(
    data: pd.DataFrame,
    metric_column: str,
    time_column: str = "year",
    language: str = "en",
) -> str:
    """
    Generate commentary on a metric's trend.

    Args:
        data: DataFrame with time series data
        metric_column: Column to analyze
        time_column: Column containing time periods
        language: Language code

    Returns:
        Trend commentary text
    """
    if data.empty or metric_column not in data.columns:
        return ""

    sorted_data = data.sort_values(time_column)
    values = sorted_data[metric_column].dropna()

    if len(values) < 2:
        return (
            "Insufficient data for trend analysis."
            if language == "en"
            else "بيانات غير كافية لتحليل الاتجاه."
        )

    first_val = values.iloc[0]
    last_val = values.iloc[-1]

    if first_val != 0:
        total_change = ((last_val - first_val) / abs(first_val)) * 100
    else:
        total_change = 0

    # Calculate average annual change
    n_periods = len(values)
    total_change / n_periods if n_periods > 0 else 0

    # Volatility (standard deviation of period-over-period changes)
    pct_changes = values.pct_change().dropna() * 100
    volatility = pct_changes.std() if len(pct_changes) > 0 else 0

    if language == "ar":
        if total_change > 5:
            direction = "اتجاه تصاعدي"
        elif total_change < -5:
            direction = "اتجاه تنازلي"
        else:
            direction = "مستقر نسبياً"

        commentary = f"يظهر {metric_column} {direction} بتغير إجمالي قدره {total_change:.1f}%."

        if volatility > 10:
            commentary += " لوحظ تقلب ملحوظ خلال الفترة."

        return commentary

    # English
    if total_change > 5:
        direction = "upward trend"
    elif total_change < -5:
        direction = "downward trend"
    else:
        direction = "relative stability"

    commentary = f"{metric_column} shows {direction} with a total change of {total_change:.1f}%."

    if volatility > 10:
        commentary += " Notable volatility observed during the period."
    elif volatility < 3:
        commentary += " The metric has been consistently stable."

    # Recent momentum
    if len(values) >= 3:
        recent = values.iloc[-3:]
        recent_trend = recent.iloc[-1] - recent.iloc[0]
        if recent_trend > 0:
            commentary += " Recent momentum is positive."
        elif recent_trend < 0:
            commentary += " Recent momentum shows deceleration."

    return commentary


def generate_comparison_summary(
    data: pd.DataFrame,
    group_column: str,
    metric_column: str,
    language: str = "en",
) -> str:
    """
    Generate summary comparing groups (e.g., regions).

    Args:
        data: DataFrame with grouped data
        group_column: Column containing group names
        metric_column: Column to compare
        language: Language code

    Returns:
        Comparison summary text
    """
    if data.empty or group_column not in data.columns or metric_column not in data.columns:
        return ""

    grouped = data.groupby(group_column)[metric_column].mean()

    if grouped.empty:
        return ""

    best = grouped.idxmax()
    best_val = grouped.max()
    worst = grouped.idxmin()
    worst_val = grouped.min()
    avg = grouped.mean()

    gap = best_val - worst_val

    if language == "ar":
        lines = [
            f"**الأفضل أداءً:** {best} ({best_val:.2f})",
            f"**الأدنى أداءً:** {worst} ({worst_val:.2f})",
            f"**المتوسط:** {avg:.2f}",
            f"**الفجوة:** {gap:.2f}",
        ]
    else:
        lines = [
            f"**Top Performer:** {best} ({best_val:.2f})",
            f"**Lowest Performer:** {worst} ({worst_val:.2f})",
            f"**Average:** {avg:.2f}",
            f"**Performance Gap:** {gap:.2f}",
        ]

    return "\n".join(lines)
