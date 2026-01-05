# UI/UX Audit & Improvement Plan

## 1. Baseline Review

### Architecture
- **Entry Point**: `streamlit_app.py` redirects to `render_unified_dashboard`.
- **Layout**: Custom 2-column layout (Sidebar + Main).
- **State Management**: `st.session_state` used for filters (year, quarter, region).
- **Data Layer**: Cached repository pattern (`get_dashboard_data`).

### Critical Issues

#### A. Scroll Fatigue
- **Observation**: The dashboard renders 7+ vertical sections in a single pass:
  1. Hero Metrics (Gauge + KPIs)
  2. Economic Pillar
  3. Labor & Social Pillars
  4. Environmental Pillar
  5. Trend Analysis
  6. Regional Comparison
  7. Data Quality
  8. Key Insights
- **Impact**: Users must scroll extensively to find specific domain data. No quick navigation between pillars.

#### B. Filter Context Loss
- **Observation**: Filters are placed at the very top of the main column.
- **Impact**: As soon as the user scrolls past the Hero section, they lose context of what Year/Region they are viewing. Changing filters requires scrolling back to the top.

#### C. Chart Readability
- **Observation**: Multi-series charts (e.g., Environmental Trends) plot all available series (8+) simultaneously.
- **Impact**: "Spaghetti charts" are difficult to read. Legend is static.

#### D. Weak Decision Cues
- **Observation**: KPI cards show values and sparklines but lack explicit targets or "On Track/Off Track" status labels.
- **Impact**: Executives cannot instantly discern performance against goals.

## 2. Improvement Plan (Phase B)

### B1. Sticky Filter Bar
- **Action**: Implement a CSS-based sticky header containing the active filter chips and a "Reset" action.
- **Location**: Top of the main column, z-indexed above content.

### B2. Information Architecture (Tabs)
- **Action**: Restructure `unified_dashboard.py` to keep the **Hero Section** (Executive Snapshot) always visible, then use `st.tabs` for detailed pillars:
  - **Overview** (Trends + Insights)
  - **Economic**
  - **Social & Labor**
  - **Environmental**
  - **Regional**
  - **Data Quality**

### B3. Chart Enhancements
- **Action**:
  - Limit default visible series to top 5.
  - Add "Focus Mode" or series selector.
  - Improve tooltips.

### B4. KPI Decision Cues
- **Action**: Update `render_enhanced_kpi_card` to render a target comparison line and a status badge (On Track / Watch / Off Track).

### B5. Performance
- **Action**: Leverage `st.tabs` lazy loading. Ensure heavy charts are only calculated when their tab is active.

## 3. Design System (Phase C)
- **Action**: Centralize CSS tokens. Ensure consistent card padding and border radius.
