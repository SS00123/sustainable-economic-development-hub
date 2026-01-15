"""
Insights Section Components
Key insights, YoY comparison, and regional analysis.
"""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from analytics_hub_platform.domain.models import FilterParams
from analytics_hub_platform.domain.services import get_regional_comparison
from analytics_hub_platform.ui.ui_components import apply_dark_chart_layout
from analytics_hub_platform.app.components import card_close, card_open
from analytics_hub_platform.ui.html import render_html


def render_yoy_comparison_section(
    df: pd.DataFrame, year: int, quarter: int, region: str, dark_theme
) -> None:
    """Render Year-over-Year comparison cards for key KPIs."""
    # Filter by region if specified
    filtered_df = df.copy()
    if region and region != "all":
        filtered_df = filtered_df[filtered_df["region"] == region]

    # Get current and previous year data
    current_data = filtered_df[(filtered_df["year"] == year) & (filtered_df["quarter"] == quarter)]
    prev_year_data = filtered_df[(filtered_df["year"] == year - 1) & (filtered_df["quarter"] == quarter)]

    # KPIs to compare
    yoy_kpis = [
        ("gdp_growth", "GDP Growth", "%", "📈"),
        ("unemployment_rate", "Unemployment Rate", "%", "👥"),
        ("sustainability_index", "Sustainability Index", "", "🌱"),
        ("digital_readiness", "Digital Readiness", "", "💻"),
    ]

    card_open("Year-over-Year Performance", f"Q{quarter} {year} vs Q{quarter} {year-1}")

    # Create 2x2 grid for YoY comparisons
    row1 = st.columns(2, gap="medium")
    row2 = st.columns(2, gap="medium")
    cols = [row1[0], row1[1], row2[0], row2[1]]

    for i, (kpi_id, kpi_name, unit, icon) in enumerate(yoy_kpis):
        with cols[i]:
            if kpi_id not in current_data.columns:
                continue

            current_val = current_data[kpi_id].mean() if not current_data.empty else 0
            prev_val = prev_year_data[kpi_id].mean() if not prev_year_data.empty else 0

            # Handle NaN
            current_val = 0 if pd.isna(current_val) else current_val
            prev_val = 0 if pd.isna(prev_val) else prev_val

            # Calculate change
            change = current_val - prev_val
            pct_change = ((current_val - prev_val) / prev_val * 100) if prev_val != 0 else 0

            # Invert logic for unemployment (lower is better)
            is_positive = change >= 0
            if kpi_id == "unemployment_rate":
                is_positive = change <= 0

            change_class = "positive" if is_positive else "negative"
            arrow = "→"

            render_html(f'''
            <div style="margin-bottom:8px; color:rgba(255,255,255,0.7); font-size:13px">{icon} {kpi_name}</div>
            <div class="yoy-comparison animate-fade-in">
                <div class="yoy-year">
                    <div class="year-label">{year - 1}</div>
                    <div class="year-value">{prev_val:.1f}{unit}</div>
                </div>
                <div class="yoy-divider">
                    <span class="yoy-arrow">{arrow}</span>
                    <span class="yoy-change {change_class}">
                        {"+" if pct_change >= 0 else ""}{pct_change:.1f}%
                    </span>
                </div>
                <div class="yoy-year">
                    <div class="year-label">{year}</div>
                    <div class="year-value">{current_val:.1f}{unit}</div>
                </div>
            </div>
            ''')

    card_close()


def render_regional_comparison_section(
    df: pd.DataFrame, filter_params: FilterParams, selected_region: str, dark_theme
) -> None:
    """Horizontal bar chart + stats panel using real regional comparison data."""
    comparison = get_regional_comparison(df, "sustainability_index", filter_params)

    if not comparison.regions:
        st.info("No regional data available for this period.")
        return

    data = pd.DataFrame(
        {
            "region": comparison.regions,
            "value": comparison.values,
            "status": [s.value if hasattr(s, "value") else str(s) for s in comparison.statuses],
        }
    ).sort_values("value", ascending=False)

    national_avg = comparison.national_average or 0
    highlight_region = selected_region if selected_region != "all" else None

    colors = [
        dark_theme.colors.cyan if (highlight_region and r == highlight_region) else "#334155"
        for r in data["region"]
    ]

    fig = go.Figure(
        go.Bar(
            y=data["region"],
            x=data["value"],
            orientation="h",
            marker={"color": colors, "line": {"width": 0}},
            text=[f"{v:.1f}" for v in data["value"]],
            textposition="outside",
            textfont={"color": "#F8FAFC", "size": 12},
            hovertemplate="<b>%{y}</b><br>Index: %{x:.1f}<extra></extra>",
        )
    )

    fig.add_vline(
        x=national_avg,
        line_dash="dash",
        line_color="#64748B",
        annotation_text=f"National Avg: {national_avg:.1f}",
        annotation_font={"color": "#94A3B8", "size": 11},
    )

    apply_dark_chart_layout(fig, height=420)
    fig.update_layout(
        xaxis={
            "showgrid": True,
            "gridcolor": "rgba(148,163,184,0.2)",
            "range": [0, max(100, max(data["value"]) + 5)],
            "title": "Sustainability Index",
        },
        yaxis={"showgrid": False, "autorange": "reversed"},
        bargap=0.35,
    )
    st.plotly_chart(fig, width="stretch")

    # Stats panel (Highest, Lowest, National Avg)
    highest_row = data.loc[data["value"].idxmax()]
    lowest_row = data.loc[data["value"].idxmin()]

    stats = [
        ("Highest Region", highest_row["region"], highest_row["value"], dark_theme.colors.green),
        ("Lowest Region", lowest_row["region"], lowest_row["value"], dark_theme.colors.red),
        ("National Avg", "Saudi Arabia", national_avg, dark_theme.colors.cyan),
    ]

    stat_cols = st.columns(len(stats), gap="medium")
    for col, (label, region_name, value, color) in zip(stat_cols, stats, strict=False):
        with col:
            render_html(
                f"""
                <div style="
                    background: linear-gradient(145deg, #0B1120 0%, #1E293B 100%);
                    border: 1px solid {color}40;
                    border-radius: 14px;
                    padding: 18px;
                    text-align: center;
                    box-shadow: {dark_theme.shadows.card_sm};
                ">
                    <div style="font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; color: {dark_theme.colors.text_muted};">{label}</div>
                    <div style="font-size: 18px; font-weight: 700; color: {dark_theme.colors.text_primary}; margin-top: 6px;">{region_name}</div>
                    <div style="font-size: 26px; font-weight: 800; color: {color};">{value:.1f}</div>
                </div>
            """
            )


def render_key_insights_section(
    snapshot: dict, metrics: dict, dark_theme, language: str
) -> None:
    """Render Key Insights section with two columns matching PDF design."""
    # Prefer domain-generated insights; fallback to metric deltas
    improvements = snapshot.get("top_improvements") or []
    attention_needed = snapshot.get("top_deteriorations") or []

    if not improvements and not attention_needed:
        for kpi_id, kpi in metrics.items():
            change = kpi.get("change_percent", 0) or 0
            status = kpi.get("status", "neutral")
            label = kpi.get("name", kpi.get("display_name", kpi_id.replace("_", " ").title()))

            if change > 0 and status == "green":
                improvements.append({"label": label, "change": change, "kpi_id": kpi_id})
            elif change < 0 or status == "red":
                attention_needed.append({"label": label, "change": change, "kpi_id": kpi_id})

        improvements = sorted(improvements, key=lambda x: -x["change"])[:5]
        attention_needed = sorted(attention_needed, key=lambda x: x["change"])[:5]

    def _normalize_items(items, positive: bool) -> list[dict]:
        normalized = []
        for item in items:
            label = item.get("label") or item.get("display_name") or item.get("kpi_id", "").replace("_", " ").title()
            change_val = item.get("change") or item.get("change_percent") or 0
            normalized.append({"label": label, "change": float(change_val), "positive": positive})
        return normalized

    improvements = _normalize_items(improvements, True)
    attention_needed = _normalize_items(attention_needed, False)

    # Two-column layout
    improve_col, attention_col = st.columns(2, gap="large")

    with improve_col:
        card_open("🚀 Top Improvements This Quarter", "KPIs showing strong positive momentum")
        if improvements:
            for item in improvements:
                render_html(
                    f"""
                    <div style="
                        display: flex;
                        align-items: center;
                        padding: 12px 16px;
                        background: {dark_theme.colors.green}10;
                        border-left: 3px solid {dark_theme.colors.green};
                        border-radius: 0 8px 8px 0;
                        margin-bottom: 8px;
                    ">
                        <span style="color: {dark_theme.colors.green}; font-size: 16px; margin-right: 12px;">▲</span>
                        <div style="flex: 1;">
                            <div style="color: {dark_theme.colors.text_primary}; font-weight: 500;">
                                {item['label']}
                            </div>
                            <div style="color: {dark_theme.colors.green}; font-size: 12px;">
                                +{item['change']:.1f}% improvement
                            </div>
                        </div>
                    </div>
                """
                )
        else:
            render_html(
                f"<p style='color: {dark_theme.colors.text_muted};'>No significant improvements to highlight.</p>"
            )
        card_close()

    with attention_col:
        card_open("⚠️ Areas Needing Attention", "KPIs requiring focus and intervention")
        if attention_needed:
            for item in attention_needed:
                change_display = f"{item['change']:.1f}%" if item['change'] < 0 else "At Risk"
                render_html(
                    f"""
                    <div style="
                        display: flex;
                        align-items: center;
                        padding: 12px 16px;
                        background: {dark_theme.colors.red}10;
                        border-left: 3px solid {dark_theme.colors.red};
                        border-radius: 0 8px 8px 0;
                        margin-bottom: 8px;
                    ">
                        <span style="color: {dark_theme.colors.red}; font-size: 16px; margin-right: 12px;">▼</span>
                        <div style="flex: 1;">
                            <div style="color: {dark_theme.colors.text_primary}; font-weight: 500;">
                                {item['label']}
                            </div>
                            <div style="color: {dark_theme.colors.red}; font-size: 12px;">
                                {change_display}
                            </div>
                        </div>
                    </div>
                """
                )
        else:
            render_html(
                f"<p style='color: {dark_theme.colors.text_muted};'>All KPIs are performing within acceptable ranges.</p>"
            )
        card_close()
