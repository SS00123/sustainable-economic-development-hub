"""app.py
Sustainable Economic Development Dashboard – Minister View

Single-file Streamlit dashboard inspired by the provided UI reference.
Run:
    streamlit run app.py
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Optional

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st


# -----------------------------
# Session State Initialization
# -----------------------------

def init_session_state() -> None:
    """Initialize session state for navigation and search."""
    if "current_page" not in st.session_state:
        st.session_state.current_page = "Dashboard"
    if "search_query" not in st.session_state:
        st.session_state.search_query = ""


def set_page(page: str) -> None:
    """Set the current page in session state."""
    st.session_state.current_page = page


# -----------------------------
# Theme & CSS
# -----------------------------


def inject_theme_css() -> None:
    """Inject custom CSS to mimic the dark layered purple UI."""

    st.markdown(
        """
        <style>
          :root{
            --bg0:#0f1122;
            --bg1:#121532;
            --card:#1b1f36;
            --card2:#1e2340;
            --stroke:rgba(255,255,255,0.08);
            --muted:rgba(255,255,255,0.65);
            --muted2:rgba(255,255,255,0.45);
            --white:rgba(255,255,255,0.95);
            --purple:#a855f7;
            --purple2:#7c3aed;
            --pink:#ec4899;
            --cyan:#22d3ee;
            --shadow:0 18px 48px rgba(0,0,0,.55);
            --shadow2:0 10px 26px rgba(0,0,0,.45);
            --radius:16px;
          }

          /* App background */
          html, body, [data-testid="stAppViewContainer"] {
            background:
              radial-gradient(1200px 700px at 10% 10%, rgba(124,58,237,.35), rgba(0,0,0,0) 60%),
              radial-gradient(1200px 700px at 90% 25%, rgba(34,211,238,.18), rgba(0,0,0,0) 60%),
              linear-gradient(180deg, var(--bg1), var(--bg0) 60%);
            color: var(--white);
          }

          /* Hide Streamlit chrome */
          #MainMenu, footer, header { visibility: hidden; }
          [data-testid="stSidebar"] { display: none; }

          /* Layout container */
          .block-container {
            padding-top: 18px;
            padding-bottom: 24px;
            max-width: 1280px;
          }

          /* Remove default white containers */
          [data-testid="stVerticalBlock"], [data-testid="stHorizontalBlock"] {
            gap: 16px;
          }

          /* Inputs styling */
          .stTextInput input {
            background: rgba(255,255,255,0.06) !important;
            border: 1px solid rgba(255,255,255,0.10) !important;
            border-radius: 999px !important;
            color: var(--white) !important;
            height: 36px;
          }
          .stTextInput input::placeholder { color: rgba(255,255,255,0.45); }

          /* Card */
          .card {
            background: linear-gradient(180deg, rgba(255,255,255,0.06), rgba(255,255,255,0.03));
            border: 1px solid var(--stroke);
            border-radius: var(--radius);
            box-shadow: var(--shadow);
            padding: 16px 16px 14px 16px;
            position: relative;
            overflow: hidden;
          }
          .card:hover {
            transform: translateY(-1px);
            box-shadow: 0 22px 55px rgba(0,0,0,.62);
            transition: 140ms ease;
          }
          .card .card-title {
            font-size: 13px;
            color: var(--muted);
            letter-spacing: .2px;
          }
          .card .card-value {
            font-size: 26px;
            font-weight: 700;
            margin-top: 4px;
          }
          .card .card-sub {
            font-size: 12px;
            color: var(--muted2);
            margin-top: 2px;
          }
          .delta {
            font-size: 12px;
            padding: 2px 8px;
            border-radius: 999px;
            border: 1px solid rgba(255,255,255,0.10);
            background: rgba(255,255,255,0.05);
            display: inline-flex;
            gap: 6px;
            align-items: center;
          }
          .delta.positive { color: rgba(34,211,238,0.95); }
          .delta.negative { color: rgba(236,72,153,0.95); }

          /* Sidebar */
          .side {
            background: rgba(255,255,255,0.04);
            border: 1px solid var(--stroke);
            border-radius: var(--radius);
            box-shadow: var(--shadow2);
            overflow: hidden;
          }
          .side-top {
            padding: 18px 16px;
            background: linear-gradient(135deg, rgba(168,85,247,.95), rgba(236,72,153,.75));
            position: relative;
          }
          .side-top:after{
            content:"";
            position:absolute;
            left:-40px;
            bottom:-40px;
            width:140px;
            height:140px;
            background: radial-gradient(circle at 30% 30%, rgba(255,255,255,.35), rgba(255,255,255,0) 60%);
            border-radius: 999px;
            transform: rotate(12deg);
          }
          .brand {
            font-weight: 800;
            letter-spacing: .2px;
            color: rgba(255,255,255,0.95);
            font-size: 14px;
          }
          .brand-sub { font-size: 11px; color: rgba(255,255,255,0.8); margin-top: 2px; }
          .avatar {
            width: 44px;
            height: 44px;
            border-radius: 999px;
            background: linear-gradient(135deg, rgba(34,211,238,.65), rgba(168,85,247,.85));
            border: 2px solid rgba(255,255,255,0.22);
            display:flex;
            align-items:center;
            justify-content:center;
            font-weight: 800;
            margin-top: 14px;
          }
          .user-name { margin-top: 10px; font-size: 12px; color: rgba(255,255,255,0.9); }
          .nav {
            padding: 10px 10px 14px 10px;
          }
          .nav a {
            display:flex;
            gap: 10px;
            align-items:center;
            padding: 10px 10px;
            border-radius: 12px;
            text-decoration: none;
            color: rgba(255,255,255,0.78);
            font-size: 12px;
            border: 1px solid rgba(255,255,255,0);
          }
          .nav a:hover {
            background: rgba(168,85,247,0.10);
            border: 1px solid rgba(168,85,247,0.18);
            color: rgba(255,255,255,0.92);
            transition: 140ms ease;
          }
          .nav a.active {
            background: rgba(255,255,255,0.06);
            border: 1px solid rgba(255,255,255,0.12);
            color: rgba(255,255,255,0.95);
          }
          .nav .dot {
            width: 7px; height: 7px; border-radius: 99px;
            background: rgba(168,85,247,0.95);
            box-shadow: 0 0 14px rgba(168,85,247,0.65);
          }

          /* Header */
          .topbar {
            background: rgba(255,255,255,0.04);
            border: 1px solid var(--stroke);
            border-radius: var(--radius);
            box-shadow: var(--shadow2);
            padding: 14px 16px;
          }
          .title { font-weight: 800; font-size: 15px; }
          .daterange { font-size: 11px; color: var(--muted2); margin-top: 2px; }
          .icon-pill{
            width: 34px; height: 34px; border-radius: 999px;
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.10);
            display:flex; align-items:center; justify-content:center;
            color: rgba(255,255,255,0.80);
          }

          /* Plotly inside cards */
          .js-plotly-plot .plotly .main-svg { border-radius: 12px; }
        </style>
        """,
        unsafe_allow_html=True,
    )


# -----------------------------
# Data generation
# -----------------------------


@dataclass(frozen=True)
class DemoData:
    years: list[int]
    regions: list[str]
    yearly: pd.DataFrame
    economic_indicators: pd.DataFrame
    labor_indicators: pd.DataFrame
    social_indicators: pd.DataFrame
    environmental_indicators: pd.DataFrame
    composite_indicators: pd.DataFrame
    region_snapshot: pd.DataFrame
    activity_daily: pd.DataFrame
    energy_mix: pd.DataFrame


def generate_demo_data(seed: int = 7) -> DemoData:
    """Synthetic (but realistic-looking) data for all dashboard indicators."""

    rng = np.random.default_rng(seed)

    years = list(range(2019, 2026))
    regions = ["Riyadh", "Western Region", "Eastern Region"]

    # === ECONOMIC INDICATORS ===
    gdp_growth = np.clip(rng.normal(3.8, 1.0, len(years)), 0.5, 7.0)
    gdp_total = np.clip(rng.normal(2500000, 200000, len(years)), 2000000, 3000000)  # Million SAR
    foreign_investment = np.clip(rng.normal(15000, 3000, len(years)), 5000, 25000)  # Million SAR
    export_diversity = np.clip(np.linspace(45, 65, len(years)) + rng.normal(0, 3, len(years)), 30, 80)
    economic_complexity = np.clip(rng.normal(0.2, 0.3, len(years)), -1.0, 1.5)
    population = np.linspace(34.0, 36.5, len(years))  # Millions
    
    economic_indicators = pd.DataFrame({
        "Year": years,
        "GDP Growth (%)": gdp_growth,
        "GDP Total (M SAR)": gdp_total,
        "Foreign Investment (M SAR)": foreign_investment,
        "Export Diversity Index": export_diversity,
        "Economic Complexity Index": economic_complexity,
        "Population (M)": population,
    })

    # === LABOR & SKILLS INDICATORS ===
    unemployment_rate = np.clip(np.linspace(12.5, 8.2, len(years)) + rng.normal(0, 0.8, len(years)), 5, 15)
    green_jobs = np.clip(np.linspace(45, 85, len(years)) + rng.normal(0, 5, len(years)), 20, 120)  # Thousands
    skills_gap = np.clip(np.linspace(55, 35, len(years)) + rng.normal(0, 3, len(years)), 20, 70)
    
    labor_indicators = pd.DataFrame({
        "Year": years,
        "Unemployment Rate (%)": unemployment_rate,
        "Green Jobs (K)": green_jobs,
        "Skills Gap Index": skills_gap,
    })

    # === SOCIAL & DIGITAL INDICATORS ===
    social_progress = np.clip(np.linspace(62, 75, len(years)) + rng.normal(0, 2, len(years)), 50, 85)
    digital_readiness = np.clip(np.linspace(58, 78, len(years)) + rng.normal(0, 3, len(years)), 45, 85)
    innovation_index = np.clip(np.linspace(35, 52, len(years)) + rng.normal(0, 2.5, len(years)), 25, 65)
    
    social_indicators = pd.DataFrame({
        "Year": years,
        "Social Progress Score": social_progress,
        "Digital Readiness Index": digital_readiness,
        "Innovation Index": innovation_index,
    })

    # === ENVIRONMENTAL INDICATORS ===
    renew_share = np.clip(np.linspace(12, 34, len(years)) + rng.normal(0, 1.3, len(years)), 8, 40)
    co2_index = np.clip(np.linspace(100, 74, len(years)) + rng.normal(0, 2.0, len(years)), 65, 110)
    co2_total = np.clip(np.linspace(420, 380, len(years)) + rng.normal(0, 15, len(years)), 350, 450)  # Million tons
    energy_intensity = np.clip(np.linspace(8.5, 6.2, len(years)) + rng.normal(0, 0.4, len(years)), 4, 12)  # MJ/SAR
    water_efficiency = np.clip(np.linspace(45, 68, len(years)) + rng.normal(0, 3, len(years)), 35, 80)
    recycling_rate = np.clip(np.linspace(15, 35, len(years)) + rng.normal(0, 2, len(years)), 10, 45)
    forest_coverage = np.clip(np.linspace(0.8, 2.1, len(years)) + rng.normal(0, 0.1, len(years)), 0.5, 3.0)
    air_quality = np.clip(np.linspace(85, 65, len(years)) + rng.normal(0, 4, len(years)), 40, 120)  # Lower is better
    
    environmental_indicators = pd.DataFrame({
        "Year": years,
        "Renewable Share (%)": renew_share,
        "CO₂ Intensity Index": co2_index,
        "CO₂ Total (MT)": co2_total,
        "Energy Intensity (MJ/SAR)": energy_intensity,
        "Water Efficiency Index": water_efficiency,
        "Waste Recycling Rate (%)": recycling_rate,
        "Forest Coverage (%)": forest_coverage,
        "Air Quality Index": air_quality,
    })

    # === COMPOSITE INDICATORS ===
    # Calculate derived indicators
    co2_per_gdp = co2_total / (gdp_total / 1000)  # tons per million SAR
    co2_per_capita = co2_total / population  # tons per capita
    data_quality = np.clip(rng.normal(82, 5, len(years)), 70, 95)
    
    # Calculate sustainability index (weighted average of key environmental indicators)
    sustainability_index = (
        (100 - co2_index) * 0.15 +  # Inverted CO2 index
        renew_share * 0.15 +
        (100 - energy_intensity * 10) * 0.10 +  # Normalized energy intensity
        water_efficiency * 0.10 +
        recycling_rate * 0.10 +
        (100 - air_quality) * 0.10 +  # Inverted air quality
        forest_coverage * 5 * 0.05 +  # Normalized forest coverage
        green_jobs / 2 * 0.10 +  # Normalized green jobs
        export_diversity * 0.05 +
        (economic_complexity + 2) * 25 * 0.05  # Normalized complexity
    )
    sustainability_index = np.clip(sustainability_index, 0, 100)
    
    composite_indicators = pd.DataFrame({
        "Year": years,
        "CO₂ per GDP (tons/M SAR)": co2_per_gdp,
        "CO₂ per Capita (tons/capita)": co2_per_capita,
        "Data Quality Score": data_quality,
        "Sustainability Index": sustainability_index,
    })

    # Maintain existing structures for backward compatibility
    yearly = pd.DataFrame({
        "Year": years,
        "GDP Growth (%)": gdp_growth,
        "Renewable Share (%)": renew_share,
        "CO₂ Intensity Index": co2_index,
    })

    # Regional snapshot for 2025
    base_activity = rng.normal(72, 6, len(regions))
    renewable_momentum = rng.normal(28, 4, len(regions))
    region_snapshot = pd.DataFrame({
        "Region": regions,
        "Economic Activity": np.clip(base_activity, 55, 90),
        "Renewable Momentum": np.clip(renewable_momentum, 15, 40),
    }).sort_values("Economic Activity", ascending=True)

    # Daily Economic Activity Index (last 30 days)
    end = date.today()
    days = pd.date_range(end=end, periods=30, freq="D")
    steps = rng.normal(0, 1.15, len(days)).cumsum()
    curve = 66 + steps + np.sin(np.linspace(0, 4.6, len(days))) * 2.2
    curve = np.clip(curve, 54, 86)
    activity_daily = pd.DataFrame({"Date": days, "Index": curve})

    # Energy mix (donut)
    energy_mix = pd.DataFrame({
        "Source": ["Renewables", "Natural Gas", "Oil"],
        "Share": [int(rng.integers(24, 33)), int(rng.integers(34, 48)), int(rng.integers(18, 32))],
    })
    energy_mix.loc[2, "Share"] = max(0, 100 - int(energy_mix.loc[0, "Share"]) - int(energy_mix.loc[1, "Share"]))

    return DemoData(
        years=years,
        regions=regions,
        yearly=yearly,
        economic_indicators=economic_indicators,
        labor_indicators=labor_indicators,
        social_indicators=social_indicators,
        environmental_indicators=environmental_indicators,
        composite_indicators=composite_indicators,
        region_snapshot=region_snapshot,
        activity_daily=activity_daily,
        energy_mix=energy_mix,
    )


# -----------------------------
# Helper functions (cards/charts)
# -----------------------------


def _delta_class(delta: float) -> str:
    return "positive" if delta >= 0 else "negative"


def _fmt_delta(delta: float) -> str:
    arrow = "▲" if delta >= 0 else "▼"
    return f"{arrow} {abs(delta):.1f}%"


def card_open(title: str, subtitle: str | None = None, right_html: str | None = None) -> None:
    """Open a styled HTML card wrapper."""

    subtitle_html = f"<div class='card-sub'>{subtitle}</div>" if subtitle else ""
    right = right_html or ""
    st.markdown(
        f"""
        <div class="card">
          <div style="display:flex; align-items:flex-start; justify-content:space-between; gap:12px;">
            <div>
              <div class="card-title">{title}</div>
              {subtitle_html}
            </div>
            <div>{right}</div>
          </div>
        """,
        unsafe_allow_html=True,
    )


def card_close() -> None:
    """Close the styled HTML card wrapper."""

    st.markdown("</div>", unsafe_allow_html=True)


def plotly_base_layout(fig: go.Figure) -> go.Figure:
    fig.update_layout(
        margin=dict(l=8, r=8, t=8, b=8),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="rgba(255,255,255,0.86)", size=12),
        showlegend=False,
    )
    return fig


def line_chart_card(df: pd.DataFrame, title: str) -> None:
    latest = float(df.iloc[-1]["Index"])
    prev = float(df.iloc[-8]["Index"]) if len(df) > 8 else float(df.iloc[0]["Index"])
    delta = (latest - prev) / max(prev, 1e-9) * 100

    right = f"<span class='delta {_delta_class(delta)}'>{_fmt_delta(delta)}</span>"
    card_open(title=title, subtitle="Last 30 days", right_html=right)

    x = df["Date"]
    y = df["Index"]

    fig = go.Figure()
    # Glow layer
    fig.add_trace(
        go.Scatter(
            x=x,
            y=y,
            mode="lines",
            line=dict(color="rgba(168,85,247,0.22)", width=10, shape="spline"),
            hoverinfo="skip",
        )
    )
    # Main line
    fig.add_trace(
        go.Scatter(
            x=x,
            y=y,
            mode="lines+markers",
            line=dict(color="#a855f7", width=3, shape="spline"),
            marker=dict(size=5, color="#a855f7"),
            hovertemplate="%{x|%b %d}<br><b>%{y:.1f}</b><extra></extra>",
        )
    )

    fig.update_xaxes(
        showgrid=False,
        zeroline=False,
        showticklabels=True,
        tickfont=dict(color="rgba(255,255,255,0.45)", size=10),
    )
    fig.update_yaxes(
        showgrid=True,
        gridcolor="rgba(255,255,255,0.07)",
        zeroline=False,
        tickfont=dict(color="rgba(255,255,255,0.45)", size=10),
    )

    fig.add_annotation(
        x=df.iloc[-1]["Date"],
        y=latest,
        text=f"{latest:.1f}",
        showarrow=True,
        arrowwidth=1,
        arrowcolor="rgba(255,255,255,0.35)",
        bgcolor="#7c3aed",
        bordercolor="rgba(255,255,255,0.20)",
        font=dict(color="white", size=11),
        borderpad=6,
        ax=-30,
        ay=-35,
    )

    plotly_base_layout(fig)
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})

    card_close()


def region_bar_card(df: pd.DataFrame, title: str) -> None:
    card_open(title=title, subtitle="Economic activity & renewable momentum")

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            y=df["Region"],
            x=df["Economic Activity"],
            orientation="h",
            marker=dict(color="rgba(168,85,247,0.85)", line=dict(color="rgba(255,255,255,0.10)", width=1)),
            name="Economic Activity",
            hovertemplate="%{y}<br><b>%{x:.0f}</b><extra></extra>",
        )
    )
    fig.add_trace(
        go.Bar(
            y=df["Region"],
            x=df["Renewable Momentum"],
            orientation="h",
            marker=dict(color="rgba(34,211,238,0.78)", line=dict(color="rgba(255,255,255,0.10)", width=1)),
            name="Renewable Momentum",
            hovertemplate="%{y}<br><b>%{x:.0f}</b><extra></extra>",
        )
    )

    fig.update_layout(barmode="overlay")
    fig.update_xaxes(
        showgrid=False,
        zeroline=False,
        range=[0, 100],
        showticklabels=False,
    )
    fig.update_yaxes(
        showgrid=False,
        zeroline=False,
        tickfont=dict(color="rgba(255,255,255,0.78)", size=12),
    )

    plotly_base_layout(fig)
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})

    card_close()


def donut_chart_card(df: pd.DataFrame, title: str) -> None:
    card_open(title=title, subtitle="Share of primary energy")

    fig = go.Figure(
        data=[
            go.Pie(
                labels=df["Source"],
                values=df["Share"],
                hole=0.72,
                sort=False,
                marker=dict(colors=["#a855f7", "#22d3ee", "#ec4899"], line=dict(color="rgba(0,0,0,0)", width=0)),
                textinfo="none",
                hovertemplate="%{label}<br><b>%{value}%</b><extra></extra>",
            )
        ]
    )
    fig.update_layout(
        annotations=[
            dict(
                text="Energy<br>Mix",
                x=0.5,
                y=0.5,
                font=dict(size=12, color="rgba(255,255,255,0.78)", family="sans-serif"),
                showarrow=False,
            )
        ]
    )

    plotly_base_layout(fig)
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})

    # Compact legend-like labels
    total = df["Share"].sum()
    for _, row in df.iterrows():
        pct = (row["Share"] / total) * 100 if total else 0
        st.markdown(
            f"<div style='display:flex; justify-content:space-between; color:rgba(255,255,255,0.70); font-size:12px; padding:3px 2px;'>"
            f"<span>{row['Source']}</span><span>{pct:.0f}%</span></div>",
            unsafe_allow_html=True,
        )

    card_close()


def mini_metric_card(title: str, value: str, delta: float, ring: float) -> None:
    right = f"<span class='delta {_delta_class(delta)}'>{_fmt_delta(delta)}</span>"
    card_open(title=title, subtitle="vs previous period", right_html=right)

    c1, c2 = st.columns([0.62, 0.38], gap="small")
    with c1:
        st.markdown(f"<div class='card-value'>{value}</div>", unsafe_allow_html=True)
        st.markdown(
            "<div style='margin-top:6px; color:rgba(255,255,255,0.45); font-size:11px;'>Updated monthly</div>",
            unsafe_allow_html=True,
        )
    with c2:
        ring = float(np.clip(ring, 0, 100))
        fig = go.Figure(
            data=[
                go.Pie(
                    values=[ring, 100 - ring],
                    hole=0.78,
                    sort=False,
                    marker=dict(colors=["rgba(168,85,247,0.95)", "rgba(255,255,255,0.08)"]),
                    textinfo="none",
                    hoverinfo="skip",
                )
            ]
        )
        fig.update_layout(
            height=140,
            annotations=[
                dict(
                    text=f"{ring:.0f}%",
                    x=0.5,
                    y=0.5,
                    showarrow=False,
                    font=dict(color="rgba(255,255,255,0.82)", size=12),
                )
            ],
        )
        plotly_base_layout(fig)
        st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})

    card_close()


def yearly_bar_card(df: pd.DataFrame, title: str) -> None:
    card_open(title=title, subtitle="2019–2025")

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=df["Year"],
            y=df["GDP Growth (%)"],
            name="GDP Growth",
            marker_color="rgba(168,85,247,0.82)",
            hovertemplate="%{x}<br><b>%{y:.1f}%</b><extra></extra>",
        )
    )
    fig.add_trace(
        go.Bar(
            x=df["Year"],
            y=df["Renewable Share (%)"],
            name="Renewable Share",
            marker_color="rgba(34,211,238,0.72)",
            hovertemplate="%{x}<br><b>%{y:.0f}%</b><extra></extra>",
        )
    )
    fig.add_trace(
        go.Bar(
            x=df["Year"],
            y=df["CO₂ Intensity Index"],
            name="CO₂ Intensity Index",
            marker_color="rgba(236,72,153,0.62)",
            hovertemplate="%{x}<br><b>%{y:.0f}</b><extra></extra>",
        )
    )

    fig.update_layout(barmode="group")
    fig.update_xaxes(
        tickfont=dict(color="rgba(255,255,255,0.55)", size=10),
        showgrid=False,
        zeroline=False,
    )
    fig.update_yaxes(
        showgrid=True,
        gridcolor="rgba(255,255,255,0.07)",
        zeroline=False,
        tickfont=dict(color="rgba(255,255,255,0.45)", size=10),
    )

    plotly_base_layout(fig)
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})

    card_close()


def sustainability_gauge_card(score: float, title: str) -> None:
    """Display sustainability index as a gauge chart."""
    card_open(title=title, subtitle=f"Composite Score: {score:.1f}/100")

    # Color based on score
    if score >= 70:
        color = "#22d3ee"  # Green/Cyan for good
    elif score >= 50:
        color = "#a855f7"  # Purple for fair
    else:
        color = "#ec4899"  # Pink for needs improvement

    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': ""},
        gauge = {
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "rgba(255,255,255,0.3)"},
            'bar': {'color': color},
            'bgcolor': "rgba(0,0,0,0.1)",
            'borderwidth': 2,
            'bordercolor': "rgba(255,255,255,0.1)",
            'steps': [
                {'range': [0, 50], 'color': "rgba(236,72,153,0.2)"},
                {'range': [50, 70], 'color': "rgba(168,85,247,0.2)"},
                {'range': [70, 100], 'color': "rgba(34,211,238,0.2)"}
            ],
        }
    ))

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={'color': "white"},
        height=200,
        margin=dict(l=20, r=20, t=20, b=20)
    )
    
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
    card_close()


def indicators_summary_card(df: pd.DataFrame, title: str, indicators: list) -> None:
    """Display a summary of multiple indicators in a compact card."""
    card_open(title=title, subtitle=f"{len(indicators)} indicators")

    # Get latest year data
    latest = df.iloc[-1]
    
    for i, indicator in enumerate(indicators):
        if indicator in df.columns:
            value = latest[indicator]
            
            # Determine trend (simple comparison with previous year)
            if len(df) > 1:
                prev_value = df.iloc[-2][indicator]
                delta = value - prev_value
                trend = "↗" if delta > 0 else "↘" if delta < 0 else "→"
                trend_color = "#22d3ee" if delta > 0 else "#ec4899" if delta < 0 else "#a855f7"
            else:
                trend = "→"
                trend_color = "#a855f7"
            
            # Format value based on indicator type
            if "%" in indicator:
                formatted_value = f"{value:.1f}%"
            elif "Index" in indicator:
                formatted_value = f"{value:.1f}"
            elif "(K)" in indicator:
                formatted_value = f"{value:.0f}K"
            elif "(M" in indicator:
                formatted_value = f"{value/1000000:.1f}M" if value > 1000000 else f"{value/1000:.0f}K"
            else:
                formatted_value = f"{value:.1f}"
            
            st.markdown(
                f"<div style='display: flex; justify-content: space-between; align-items: center; padding: 8px 0; border-bottom: 1px solid rgba(255,255,255,0.05);'>"
                f"<div style='color: rgba(255,255,255,0.7); font-size: 11px;'>{indicator.replace(' (%)', '').replace(' (M SAR)', '').replace(' (K)', '')}</div>"
                f"<div style='display: flex; align-items: center; gap: 6px;'>"
                f"<span style='color: white; font-weight: 600; font-size: 12px;'>{formatted_value}</span>"
                f"<span style='color: {trend_color}; font-size: 10px;'>{trend}</span>"
                f"</div></div>",
                unsafe_allow_html=True,
            )

    card_close()


def environmental_trends_card(df: pd.DataFrame, title: str) -> None:
    """Display environmental trends in a multi-line chart."""
    card_open(title=title, subtitle="Key environmental indicators")

    fig = go.Figure()
    
    # Add renewable share
    fig.add_trace(go.Scatter(
        x=df["Year"],
        y=df["Renewable Share (%)"],
        mode="lines+markers",
        name="Renewable Share (%)",
        line=dict(color="#22d3ee", width=2),
        marker=dict(size=4),
    ))
    
    # Add water efficiency (normalize to similar scale)
    fig.add_trace(go.Scatter(
        x=df["Year"],
        y=df["Water Efficiency Index"],
        mode="lines+markers", 
        name="Water Efficiency",
        line=dict(color="#a855f7", width=2),
        marker=dict(size=4),
    ))
    
    # Add recycling rate
    fig.add_trace(go.Scatter(
        x=df["Year"],
        y=df["Waste Recycling Rate (%)"],
        mode="lines+markers",
        name="Recycling Rate (%)",
        line=dict(color="#ec4899", width=2),
        marker=dict(size=4),
    ))

    fig.update_xaxes(
        showgrid=False,
        zeroline=False,
        tickfont=dict(color="rgba(255,255,255,0.45)", size=10),
    )
    fig.update_yaxes(
        showgrid=True,
        gridcolor="rgba(255,255,255,0.07)",
        zeroline=False,
        tickfont=dict(color="rgba(255,255,255,0.45)", size=10),
    )

    plotly_base_layout(fig)
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
    card_close()


# -----------------------------
# Layout (sidebar + header + main grid)
# -----------------------------


def render_sidebar(active: str = "Dashboard") -> None:
    """Interactive sidebar with navigation buttons."""

    # Sidebar header with branding
    st.markdown(
        """
        <div class="side">
          <div class="side-top">
            <div class="brand">Sustainable Analytics</div>
            <div class="brand-sub">Minister View</div>
            <div class="avatar">SA</div>
            <div class="user-name">H.E. Minister</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    # Navigation structure
    nav_sections = [
        {
            "label": "MAIN",
            "items": [
                ("Dashboard", "📊"),
                ("KPIs", "📈"),
                ("Trends", "📉"),
            ]
        },
        {
            "label": "🧠 ANALYTICS",
            "items": [
                ("KPI Forecasting", "🔮"),
                ("Early Warning", "⚠️"),
                ("AI Recommendations", "🤖"),
                ("Regional Map", "🗺️"),
            ]
        },
        {
            "label": "SYSTEM",
            "items": [
                ("Data", "📁"),
                ("Settings", "⚙️"),
            ]
        },
    ]
    
    # Render navigation sections
    for section in nav_sections:
        # Section header
        st.markdown(f"""
            <div style="
                margin-top: 16px;
                padding: 6px 12px;
                font-size: 10px;
                font-weight: 700;
                color: rgba(255,255,255,0.4);
                letter-spacing: 1.2px;
                text-transform: uppercase;
                border-top: 1px solid rgba(255,255,255,0.08);
            ">
                {section['label']}
            </div>
        """, unsafe_allow_html=True)
        
        # Section items
        for name, icon in section["items"]:
            is_active = st.session_state.current_page == name
            button_type = "primary" if is_active else "secondary"
            if st.button(
                f"{icon} {name}",
                key=f"nav_{name.replace(' ', '_')}",
                width="stretch",
                type=button_type,
            ):
                st.session_state.current_page = name
                st.rerun()


def render_header() -> None:
    """Top header with title, date range, functional search, icons."""

    now = datetime.now().date()
    start = date(now.year - 6, 1, 1)
    date_range = f"{start.strftime('%b %Y')} – {now.strftime('%b %Y')}"
    
    # Get current page title
    page_title = st.session_state.get("current_page", "Dashboard")
    page_titles = {
        "Dashboard": "Overview",
        "KPIs": "Key Performance Indicators",
        "Trends": "Trend Analysis",
        "Data": "Data Management",
        "Settings": "Settings & Preferences",
        "KPI Forecasting": "KPI Forecasting",
        "Early Warning": "Early Warning System",
        "AI Recommendations": "AI Recommendations",
        "Regional Map": "Regional Map",
    }

    c1, c2, c3 = st.columns([0.34, 0.44, 0.22], gap="small")
    with c1:
        st.markdown(
            f"""
            <div class="topbar">
              <div class="title">{page_titles.get(page_title, 'Overview')}</div>
              <div class="daterange">Reporting period: {date_range}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown("<div class='topbar' style='padding:10px 12px;'>", unsafe_allow_html=True)
        search_query = st.text_input(
            "Search",
            placeholder="Search KPIs, regions, policies…",
            label_visibility="collapsed",
            key="search_input",
        )
        if search_query:
            st.session_state.search_query = search_query
        st.markdown("</div>", unsafe_allow_html=True)
    with c3:
        st.markdown(
            """
            <div class="topbar" style="display:flex; align-items:center; justify-content:flex-end; gap:10px;">
              <div class="icon-pill">⎋</div>
              <div class="icon-pill">🔔</div>
              <div class="icon-pill">👤</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def main() -> None:
    st.set_page_config(
        page_title="Sustainable Economic Development – Minister View",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    
    # Initialize session state
    init_session_state()
    
    inject_theme_css()

    data = generate_demo_data(seed=11)
    
    # Get current page
    current_page = st.session_state.current_page

    # Root layout: sidebar + main
    side_col, main_col = st.columns([0.24, 0.76], gap="large")
    with side_col:
        render_sidebar(active=current_page)

    with main_col:
        render_header()
        
        # Route to appropriate page
        if current_page == "Dashboard":
            render_dashboard_page(data)
        elif current_page == "KPIs":
            render_kpis_page(data)
        elif current_page == "Trends":
            render_trends_page(data)
        elif current_page == "KPI Forecasting":
            render_forecasting_page(data)
        elif current_page == "Early Warning":
            render_early_warning_page(data)
        elif current_page == "AI Recommendations":
            render_ai_recommendations_page(data)
        elif current_page == "Regional Map":
            render_regional_map_page(data)
        elif current_page == "Data":
            render_data_page(data)
        elif current_page == "Settings":
            render_settings_page()
        else:
            render_dashboard_page(data)


def render_dashboard_page(data: DemoData) -> None:
    """Render the comprehensive dashboard page with all indicators."""
    
    # Check for search query
    search_query = st.session_state.get("search_query", "").lower()
    
    # === TOP ROW: SUSTAINABILITY OVERVIEW ===
    sustainability_score = data.composite_indicators.iloc[-1]["Sustainability Index"]
    show_sustainability = not search_query or any(term in search_query for term in ["sustain", "composite", "index", "overall"])
    
    if show_sustainability:
        sustainability_gauge_card(sustainability_score, "🎯 Sustainability Index")
        st.markdown("<br>", unsafe_allow_html=True)
    
    # === ECONOMIC INDICATORS SECTION ===
    show_economic = not search_query or any(term in search_query for term in ["economic", "gdp", "investment", "complexity", "export"])
    if show_economic:
        st.markdown("### 📊 Economic Performance")
        
        ec1, ec2, ec3 = st.columns([0.4, 0.3, 0.3], gap="large")
        
        with ec1:
            line_chart_card(data.activity_daily, title="Economic Activity Index")
        
        with ec2:
            indicators_summary_card(
                data.economic_indicators, 
                "Economic Indicators",
                ["GDP Growth (%)", "Foreign Investment (M SAR)", "Export Diversity Index"]
            )
        
        with ec3:
            # Latest economic metrics
            latest_econ = data.economic_indicators.iloc[-1]
            complexity = latest_econ["Economic Complexity Index"]
            gdp_total = latest_econ["GDP Total (M SAR)"]
            
            mini_metric_card(
                title="Economic Complexity",
                value=f"{complexity:.2f}",
                delta=float((complexity - data.economic_indicators.iloc[-2]["Economic Complexity Index"]) * 100),
                ring=float(np.clip((complexity + 2) * 25, 0, 100)),
            )

    # === ENVIRONMENTAL INDICATORS SECTION ===
    show_environment = not search_query or any(term in search_query for term in ["environment", "renewable", "co2", "energy", "water", "air"])
    if show_environment:
        st.markdown("### 🌿 Environmental Sustainability")
        
        env1, env2 = st.columns([0.6, 0.4], gap="large")
        
        with env1:
            environmental_trends_card(data.environmental_indicators, "Environmental Trends")
        
        with env2:
            indicators_summary_card(
                data.environmental_indicators,
                "Environmental Indicators", 
                ["CO₂ Intensity Index", "Energy Intensity (MJ/SAR)", "Air Quality Index", "Forest Coverage (%)"]
            )

    # === SOCIAL & LABOR SECTION ===
    show_social = not search_query or any(term in search_query for term in ["social", "digital", "innovation", "jobs", "unemployment", "skills"])
    if show_social:
        st.markdown("### 👥 Social & Labor Development")
        
        soc1, soc2, soc3 = st.columns([0.3, 0.35, 0.35], gap="large")
        
        with soc1:
            indicators_summary_card(
                data.social_indicators,
                "Social Progress",
                ["Social Progress Score", "Digital Readiness Index", "Innovation Index"]
            )
        
        with soc2:
            indicators_summary_card(
                data.labor_indicators,
                "Labor & Skills",
                ["Green Jobs (K)", "Unemployment Rate (%)", "Skills Gap Index"]
            )
        
        with soc3:
            # Green jobs highlight
            latest_labor = data.labor_indicators.iloc[-1]
            green_jobs = latest_labor["Green Jobs (K)"]
            unemployment = latest_labor["Unemployment Rate (%)"]
            
            mini_metric_card(
                title="Green Jobs Growth",
                value=f"{green_jobs:.0f}K",
                delta=float((green_jobs - data.labor_indicators.iloc[-2]["Green Jobs (K)"]) / max(data.labor_indicators.iloc[-2]["Green Jobs (K)"], 1) * 100),
                ring=float(np.clip(100 - unemployment * 8, 20, 90)),
            )

    # === REGIONAL & ENERGY MIX ===
    show_region_energy = not search_query or any(term in search_query for term in ["region", "energy", "mix", "gas", "oil"])
    if show_region_energy:
        st.markdown("### 🗺️ Regional & Energy Overview")
        
        reg1, reg2 = st.columns([0.6, 0.4], gap="large")
        
        with reg1:
            region_bar_card(data.region_snapshot, title="Regional Performance")
        
        with reg2:
            donut_chart_card(data.energy_mix, title="Energy Mix")

    # === COMPOSITE INDICATORS SECTION ===
    show_composite = not search_query or any(term in search_query for term in ["composite", "derived", "capita", "quality"])
    if show_composite:
        st.markdown("### 🎯 Composite & Derived Indicators")
        
        comp1, comp2 = st.columns([0.5, 0.5], gap="large")
        
        with comp1:
            indicators_summary_card(
                data.composite_indicators,
                "Derived Indicators",
                ["CO₂ per GDP (tons/M SAR)", "CO₂ per Capita (tons/capita)", "Data Quality Score"]
            )
        
        with comp2:
            # Data quality metric
            data_quality = data.composite_indicators.iloc[-1]["Data Quality Score"]
            mini_metric_card(
                title="Data Quality",
                value=f"{data_quality:.0f}%",
                delta=float(data_quality - data.composite_indicators.iloc[-2]["Data Quality Score"]),
                ring=float(data_quality),
            )


def render_kpis_page(data: DemoData) -> None:
    """Render the comprehensive KPIs detail page with all indicators."""
    
    st.markdown("### 📈 Key Performance Indicators")
    st.markdown("Complete overview of all sustainability and development indicators")
    
    # === TOP LEVEL METRICS ===
    col1, col2, col3, col4, col5 = st.columns(5)
    
    # Get latest values
    latest_econ = data.economic_indicators.iloc[-1]
    latest_env = data.environmental_indicators.iloc[-1]
    latest_social = data.social_indicators.iloc[-1]
    latest_labor = data.labor_indicators.iloc[-1]
    latest_composite = data.composite_indicators.iloc[-1]
    
    with col1:
        gdp_growth = latest_econ["GDP Growth (%)"]
        st.metric("GDP Growth", f"{gdp_growth:.1f}%", 
                 f"{gdp_growth - data.economic_indicators.iloc[-2]['GDP Growth (%)']:.1f}%")
    
    with col2:
        renewable = latest_env["Renewable Share (%)"]
        st.metric("Renewable Share", f"{renewable:.1f}%",
                 f"{renewable - data.environmental_indicators.iloc[-2]['Renewable Share (%)']:.1f}%")
    
    with col3:
        co2_index = latest_env["CO₂ Intensity Index"]
        st.metric("CO₂ Index", f"{co2_index:.1f}",
                 f"{co2_index - data.environmental_indicators.iloc[-2]['CO₂ Intensity Index']:.1f}",
                 delta_color="inverse")
    
    with col4:
        sustainability = latest_composite["Sustainability Index"]
        st.metric("Sustainability Index", f"{sustainability:.1f}",
                 f"{sustainability - data.composite_indicators.iloc[-2]['Sustainability Index']:.1f}")
    
    with col5:
        green_jobs = latest_labor["Green Jobs (K)"]
        st.metric("Green Jobs", f"{green_jobs:.0f}K",
                 f"{green_jobs - data.labor_indicators.iloc[-2]['Green Jobs (K)']:.0f}K")

    st.markdown("---")

    # === INDICATORS BY CATEGORY ===
    
    # Economic Indicators
    with st.expander("📊 Economic Indicators", expanded=True):
        st.dataframe(data.economic_indicators, width="stretch", hide_index=True)
    
    # Environmental Indicators  
    with st.expander("🌿 Environmental Indicators", expanded=True):
        st.dataframe(data.environmental_indicators, width="stretch", hide_index=True)
    
    # Social & Digital Indicators
    with st.expander("👥 Social & Digital Indicators", expanded=True):
        st.dataframe(data.social_indicators, width="stretch", hide_index=True)
        
    # Labor & Skills Indicators
    with st.expander("💼 Labor & Skills Indicators", expanded=True):
        st.dataframe(data.labor_indicators, width="stretch", hide_index=True)
    
    # Composite & Derived Indicators
    with st.expander("🎯 Composite & Derived Indicators", expanded=True):
        st.dataframe(data.composite_indicators, width="stretch", hide_index=True)

    # === INDICATOR STATUS SUMMARY ===
    st.markdown("### 📊 Indicator Performance Summary")
    
    # Create performance summary
    performance_data = []
    
    # Economic indicators status
    econ_indicators = ["GDP Growth (%)", "Export Diversity Index", "Economic Complexity Index"]
    for indicator in econ_indicators:
        value = latest_econ[indicator] 
        if "Growth" in indicator:
            status = "🟢 Good" if value > 3.0 else "🟡 Fair" if value > 1.0 else "🔴 Needs Improvement"
        elif "Diversity" in indicator:
            status = "🟢 Good" if value > 60 else "🟡 Fair" if value > 40 else "🔴 Needs Improvement"
        else:
            status = "🟢 Good" if value > 0.5 else "🟡 Fair" if value > 0 else "🔴 Needs Improvement"
        
        performance_data.append({"Category": "Economic", "Indicator": indicator, "Value": f"{value:.2f}", "Status": status})
    
    # Environmental indicators status
    env_indicators = ["Renewable Share (%)", "CO₂ Intensity Index", "Water Efficiency Index", "Waste Recycling Rate (%)"]
    for indicator in env_indicators:
        value = latest_env[indicator]
        if "Renewable" in indicator:
            status = "🟢 Good" if value > 30 else "🟡 Fair" if value > 15 else "🔴 Needs Improvement"
        elif "CO₂" in indicator:
            status = "🟢 Good" if value < 85 else "🟡 Fair" if value < 100 else "🔴 Needs Improvement"
        else:
            status = "🟢 Good" if value > 70 else "🟡 Fair" if value > 50 else "🔴 Needs Improvement"
            
        performance_data.append({"Category": "Environmental", "Indicator": indicator, "Value": f"{value:.2f}", "Status": status})
    
    # Social indicators status
    social_indicators = ["Social Progress Score", "Digital Readiness Index", "Innovation Index"]
    for indicator in social_indicators:
        value = latest_social[indicator]
        if indicator == "Innovation Index":
            status = "🟢 Good" if value > 50 else "🟡 Fair" if value > 30 else "🔴 Needs Improvement"
        else:
            status = "🟢 Good" if value > 70 else "🟡 Fair" if value > 50 else "🔴 Needs Improvement"
            
        performance_data.append({"Category": "Social & Digital", "Indicator": indicator, "Value": f"{value:.2f}", "Status": status})
    
    performance_df = pd.DataFrame(performance_data)
    st.dataframe(performance_df, width="stretch", hide_index=True)


def render_trends_page(data: DemoData) -> None:
    """Render the Trends analysis page."""
    st.markdown("### 📉 Trend Analysis")
    
    # Trend selection
    trend_type = st.selectbox("Select Indicator", ["GDP Growth (%)", "Renewable Share (%)", "CO₂ Intensity Index"])
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=data.yearly["Year"],
        y=data.yearly[trend_type],
        mode="lines+markers",
        line=dict(color="#a855f7", width=3),
        marker=dict(size=8),
        fill="tozeroy",
        fillcolor="rgba(168, 85, 247, 0.2)",
    ))
    fig.update_layout(
        title=f"{trend_type} Over Time",
        xaxis_title="Year",
        yaxis_title=trend_type,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
    )
    st.plotly_chart(fig, width="stretch")


def render_forecasting_page(data: DemoData) -> None:
    """Render the KPI Forecasting page."""
    st.markdown("### 🔮 KPI Forecasting")
    st.markdown("ML-powered predictions for key performance indicators")
    
    # Simple forecast visualization
    forecast_data = pd.DataFrame({
        "Quarter": ["Q1 2025", "Q2 2025", "Q3 2025", "Q4 2025"],
        "Predicted": [75.2, 77.8, 79.1, 81.5],
        "Lower Bound": [72.1, 74.5, 75.8, 77.9],
        "Upper Bound": [78.3, 81.1, 82.4, 85.1],
    })
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=forecast_data["Quarter"],
        y=forecast_data["Predicted"],
        mode="lines+markers",
        name="Forecast",
        line=dict(color="#a855f7", width=3),
        marker=dict(size=10),
    ))
    fig.add_trace(go.Scatter(
        x=forecast_data["Quarter"],
        y=forecast_data["Upper Bound"],
        mode="lines",
        name="Upper Bound",
        line=dict(color="rgba(168,85,247,0.3)", dash="dash"),
    ))
    fig.add_trace(go.Scatter(
        x=forecast_data["Quarter"],
        y=forecast_data["Lower Bound"],
        mode="lines",
        name="Lower Bound",
        line=dict(color="rgba(168,85,247,0.3)", dash="dash"),
        fill="tonexty",
        fillcolor="rgba(168,85,247,0.1)",
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        height=350,
        margin=dict(l=20, r=20, t=20, b=40),
    )
    st.plotly_chart(fig, width="stretch")


def render_early_warning_page(data: DemoData) -> None:
    """Render the Early Warning System page."""
    st.markdown("### ⚠️ Early Warning System")
    st.markdown("Anomaly detection for critical KPI deviations")
    
    # Sample warning alerts
    st.warning("⚡ Renewable Share dropped 2.3% below expected threshold")
    st.info("📊 GDP Growth showing unusual volatility in Eastern Region")
    st.success("✅ All other KPIs within normal parameters")


def render_ai_recommendations_page(data: DemoData) -> None:
    """Render the AI Recommendations page."""
    st.markdown("### 🤖 AI Recommendations")
    st.markdown("Smart insights powered by machine learning")
    
    st.markdown("""
        <div style="background: rgba(168,85,247,0.15); padding: 16px; border-radius: 12px; border-left: 4px solid #a855f7; margin-bottom: 12px;">
            <strong style="color: #a855f7;">💡 Recommendation 1:</strong>
            <p style="margin: 8px 0 0 0; color: rgba(255,255,255,0.85);">
                Consider increasing renewable energy investments in Western Region to meet 2025 targets.
            </p>
        </div>
        <div style="background: rgba(34,211,238,0.15); padding: 16px; border-radius: 12px; border-left: 4px solid #22d3ee; margin-bottom: 12px;">
            <strong style="color: #22d3ee;">💡 Recommendation 2:</strong>
            <p style="margin: 8px 0 0 0; color: rgba(255,255,255,0.85);">
                Focus on green job creation in Riyadh to accelerate sustainability index growth.
            </p>
        </div>
    """, unsafe_allow_html=True)


def render_regional_map_page(data: DemoData) -> None:
    """Render the Regional Map page."""
    st.markdown("### 🗺️ Regional Map")
    st.markdown("Geographic performance visualization across Saudi Arabia regions")
    
    # Regional performance data
    region_performance = pd.DataFrame({
        "Region": data.regions,
        "Economic Activity": [78.5, 72.3, 85.1],
        "Renewable Momentum": [32.4, 28.7, 35.2],
        "Score": [85.2, 78.5, 82.1],
        "Status": ["🟢 Excellent", "🟡 Good", "🟢 Excellent"],
    })
    
    # Summary cards
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Top Performing", "Eastern Region", "85.1")
    with col2:
        st.metric("Average Score", "81.9", "+2.3%")
    with col3:
        st.metric("Regions Analyzed", "3", None)
    
    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
    
    # Interactive Map Visualization
    st.markdown("#### 🗺️ Saudi Arabia Regional Performance Map")
    
    # Create a scatter geo map
    map_data = pd.DataFrame({
        "Region": ["Riyadh", "Western Region", "Eastern Region"],
        "lat": [24.7136, 21.4858, 26.4207],
        "lon": [46.6753, 39.1925, 50.0888],
        "Score": [85.2, 78.5, 82.1],
        "Economic Activity": [78.5, 72.3, 85.1],
        "Size": [40, 35, 38],
    })
    
    fig_map = go.Figure()
    
    # Add scatter points for regions
    fig_map.add_trace(go.Scattergeo(
        lon=map_data["lon"],
        lat=map_data["lat"],
        text=map_data["Region"],
        mode="markers+text",
        marker=dict(
            size=map_data["Size"],
            color=map_data["Score"],
            colorscale=[[0, "#ec4899"], [0.5, "#a855f7"], [1, "#22d3ee"]],
            colorbar=dict(
                title=dict(text="Score", font=dict(color="white")),
                thickness=15,
                len=0.7,
                bgcolor="rgba(0,0,0,0.5)",
                tickfont=dict(color="white"),
            ),
            line=dict(width=2, color="rgba(255,255,255,0.5)"),
            showscale=True,
        ),
        textfont=dict(size=12, color="white", family="Arial Black"),
        textposition="top center",
        hovertemplate="<b>%{text}</b><br>" +
                     "Score: %{marker.color:.1f}<br>" +
                     "<extra></extra>",
    ))
    
    fig_map.update_geos(
        scope="asia",
        center=dict(lat=24, lon=45),
        projection_scale=4,
        showcountries=True,
        countrycolor="rgba(255,255,255,0.2)",
        showland=True,
        landcolor="rgba(30, 41, 59, 0.8)",
        showocean=True,
        oceancolor="rgba(15, 23, 42, 0.9)",
        showlakes=False,
        bgcolor="rgba(0,0,0,0)",
    )
    
    fig_map.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        geo=dict(bgcolor="rgba(0,0,0,0)"),
        font=dict(color="white"),
        height=400,
        margin=dict(l=0, r=0, t=0, b=0),
    )
    
    st.plotly_chart(fig_map, width="stretch")
    
    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
    
    # Bar chart for regional comparison
    st.markdown("#### 📊 Regional Comparison")
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=region_performance["Region"],
        y=region_performance["Economic Activity"],
        name="Economic Activity",
        marker_color="#a855f7",
    ))
    fig.add_trace(go.Bar(
        x=region_performance["Region"],
        y=region_performance["Renewable Momentum"],
        name="Renewable Momentum",
        marker_color="#22d3ee",
    ))
    fig.update_layout(
        barmode="group",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        height=300,
        margin=dict(l=20, r=20, t=20, b=40),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
        ),
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor="rgba(255,255,255,0.1)")
    st.plotly_chart(fig, width="stretch")
    
    # Data table
    st.markdown("#### 📋 Regional Performance Details")
    st.dataframe(region_performance, width="stretch", hide_index=True)


def render_regions_page(data: DemoData) -> None:
    """Render the Regions comparison page."""
    st.markdown("### 🗺️ Regional Comparison")
    
    # Region selection
    selected_region = st.selectbox("Select Region", data.regions)
    
    # Show regional data
    col1, col2 = st.columns(2)
    with col1:
        region_data = data.region_snapshot[data.region_snapshot["Region"] == selected_region]
        if len(region_data) > 0:
            st.metric("Economic Activity", f"{region_data.iloc[0]['Economic Activity']:.1f}")
            st.metric("Renewable Momentum", f"{region_data.iloc[0]['Renewable Momentum']:.1f}")
    
    with col2:
        region_bar_card(data.region_snapshot, title="All Regions Comparison")


def render_data_page(data: DemoData) -> None:
    """Render the Data management page."""
    st.markdown("### 📁 Data Management")
    
    # Data export options
    tab1, tab2, tab3 = st.tabs(["Yearly Data", "Regional Data", "Energy Mix"])
    
    with tab1:
        st.dataframe(data.yearly, width="stretch", hide_index=True)
        csv = data.yearly.to_csv(index=False)
        st.download_button("Download CSV", csv, "yearly_kpis.csv", "text/csv")
    
    with tab2:
        st.dataframe(data.region_snapshot, width="stretch", hide_index=True)
        csv = data.region_snapshot.to_csv(index=False)
        st.download_button("Download CSV", csv, "regional_data.csv", "text/csv")
    
    with tab3:
        st.dataframe(data.energy_mix, width="stretch", hide_index=True)
        csv = data.energy_mix.to_csv(index=False)
        st.download_button("Download CSV", csv, "energy_mix.csv", "text/csv")


def render_settings_page() -> None:
    """Render the Settings page."""
    st.markdown("### ⚙️ Settings & Preferences")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Display Settings")
        st.toggle("Dark Mode", value=True, disabled=True)
        st.toggle("Show Tooltips", value=True)
        st.selectbox("Language", ["English", "العربية"], index=0)
    
    with col2:
        st.markdown("#### Data Settings")
        st.selectbox("Default Region", ["All Regions", "Riyadh", "Western Region", "Eastern Region"])
        st.selectbox("Date Range", ["Last 7 Years", "Last 5 Years", "Last 3 Years", "Last Year"])
    
    st.markdown("---")
    st.markdown("#### About")
    st.info("Sustainable Economic Development Analytics Hub v1.0\nMinistry of Economy and Planning")


if __name__ == "__main__":
    main()
