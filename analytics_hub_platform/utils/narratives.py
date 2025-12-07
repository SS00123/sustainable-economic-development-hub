"""
Narrative Generation Utility
Sustainable Economic Development Analytics Hub
Ministry of Economy and Planning

Generates human-readable narratives and insights from data.
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
import pandas as pd

from analytics_hub_platform.domain.models import KPIStatus, DashboardSummary


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


def _generate_english_narrative(summary: DashboardSummary) -> str:
    """Generate English narrative."""
    lines = []
    
    # Opening statement
    lines.append(f"**Sustainability Performance Overview**")
    lines.append("")
    
    # Core metric
    if summary.sustainability_index is not None:
        index_val = summary.sustainability_index
        if index_val >= 70:
            assessment = "strong performance"
        elif index_val >= 50:
            assessment = "moderate progress"
        else:
            assessment = "areas requiring attention"
        
        lines.append(
            f"The current Sustainability Index stands at **{index_val:.1f}**, "
            f"indicating {assessment} across measured dimensions."
        )
        lines.append("")
    
    # Period context
    if summary.period:
        lines.append(f"*Reporting Period: {summary.period}*")
        lines.append("")
    
    # KPI highlights
    if summary.kpis:
        green_kpis = [k for k in summary.kpis if k.status == KPIStatus.GREEN]
        amber_kpis = [k for k in summary.kpis if k.status == KPIStatus.AMBER]
        red_kpis = [k for k in summary.kpis if k.status == KPIStatus.RED]
        
        if green_kpis:
            lines.append(f"**Strengths:** {len(green_kpis)} indicators are on track, including:")
            for kpi in green_kpis[:3]:
                lines.append(f"  • {kpi.name}: {kpi.value} {kpi.unit}")
            lines.append("")
        
        if amber_kpis:
            lines.append(f"**Watch Areas:** {len(amber_kpis)} indicators require monitoring:")
            for kpi in amber_kpis[:3]:
                lines.append(f"  • {kpi.name}: {kpi.value} {kpi.unit}")
            lines.append("")
        
        if red_kpis:
            lines.append(f"**Action Required:** {len(red_kpis)} indicators need immediate attention:")
            for kpi in red_kpis[:3]:
                lines.append(f"  • {kpi.name}: {kpi.value} {kpi.unit}")
            lines.append("")
    
    # Trend commentary
    if hasattr(summary, "trend") and summary.trend:
        trend = summary.trend
        if trend > 0:
            lines.append(f"Overall trend shows improvement of **{trend:.1f}%** compared to the previous period.")
        elif trend < 0:
            lines.append(f"Overall trend indicates a decline of **{abs(trend):.1f}%** from the previous period.")
        else:
            lines.append("Performance remains stable compared to the previous period.")
        lines.append("")
    
    # Regional insights
    if hasattr(summary, "top_region") and summary.top_region:
        lines.append(f"**Top Performing Region:** {summary.top_region}")
    
    if hasattr(summary, "bottom_region") and summary.bottom_region:
        lines.append(f"**Region Needing Support:** {summary.bottom_region}")
    
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
        
        lines.append(
            f"يبلغ مؤشر الاستدامة الحالي **{index_val:.1f}**، "
            f"مما يشير إلى {assessment}."
        )
        lines.append("")
    
    if summary.period:
        lines.append(f"*فترة التقرير: {summary.period}*")
        lines.append("")
    
    if summary.kpis:
        green_count = sum(1 for k in summary.kpis if k.status == KPIStatus.GREEN)
        amber_count = sum(1 for k in summary.kpis if k.status == KPIStatus.AMBER)
        red_count = sum(1 for k in summary.kpis if k.status == KPIStatus.RED)
        
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
    previous_value: Optional[float] = None,
    target: Optional[float] = None,
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
        return "Insufficient data for trend analysis." if language == "en" else "بيانات غير كافية لتحليل الاتجاه."
    
    first_val = values.iloc[0]
    last_val = values.iloc[-1]
    
    if first_val != 0:
        total_change = ((last_val - first_val) / abs(first_val)) * 100
    else:
        total_change = 0
    
    # Calculate average annual change
    n_periods = len(values)
    avg_change = total_change / n_periods if n_periods > 0 else 0
    
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
