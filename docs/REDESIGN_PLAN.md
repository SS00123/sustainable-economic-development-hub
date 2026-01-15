# UI/UX Redesign & Codebase Refactor Plan
## Sustainable Economic Development Analytics Hub

**Document Version:** 1.1  
**Date:** January 2026  
**Status:** ✅ IMPLEMENTED

---

## 📋 Implementation Summary (January 13, 2026)

### Completed Actions:
1. ✅ **Advanced Analytics page removed** - Features integrated into main sections
2. ✅ **Module consolidation** - Removed redundant `infra/` facade (kept `infrastructure/`)
3. ✅ **FastAPI isolated** - Moved to optional `[api]` dependency in pyproject.toml
4. ✅ **Smoke tests added** - 16 tests covering critical paths
5. ✅ **Full test suite passing** - 370 tests pass
6. ✅ **Documentation updated** - README updated with navigation mapping

### Feature Location Map:
| Feature | Current Location | Module |
|---------|------------------|--------|
| AI Recommendations | Dashboard (01_Dashboard.py) | `domain/llm_service.py` |
| KPI Forecasting | KPIs (02_KPIs.py) | `domain/ml_services.py` |
| Anomaly Detection | Trends (03_Trends.py) | `domain/ml_services.py` |
| Early Warning System | Trends (03_Trends.py) | `domain/ml_services.py` |
| Pattern Recognition | Trends (03_Trends.py) | `domain/advanced_analytics.py` |

### Files Changed:
- `analytics_hub_platform/infra/` - **DELETED** (facade removed)
- `pyproject.toml` - FastAPI moved to optional `[api]` extra
- `tests/test_smoke.py` - **CREATED** (16 smoke tests)
- `README.md` - Updated structure and navigation mapping

---

# EXECUTIVE HANDOFF (FINAL RESPONSE FORMAT)

This section mirrors the requested final response structure for easy copy/paste into an executive brief.

## 1) UI/UX redesign plan (Figma spec)
- **Primary screens:** Executive Dashboard, KPIs & Forecasting, Trends & Early Warning, Data & Sources
- **Design intent:** calm, credible, minimal clutter; data-dense but scannable
- **Interaction model:** smart defaults + progressive disclosure for advanced options

## 2) Menu restructuring mapping (where each feature goes)
- **No standalone “Advanced Analytics”** item
- Forecasting → KPIs
- Early Warning / Anomalies → Trends
- AI Recommendations → Dashboard
- Regional/Geo analytics → Trends (context) and/or Data (coverage/lineage)

## 3) Design system tokens + components list
- **Tokens:** typography scale, 8pt spacing, radii, 2 shadow levels, institutional palette, chart styling rules
- **Core components:** KPI card, chart card, filter bar, alert pill/card, section header, tables, empty/loading/error states

## 4) Codebase refactor plan (phases)
- **Approach:** incremental, backward-compatible shims while canonical modules are introduced
- **Focus:** remove duplication, standardize patterns, improve separation of concerns (UI vs domain vs data/infra)

## 5) Proposed final project structure
- Target structure defined in Part B (with Streamlit `pages/` preserved)

## 6) De-duplication targets and safe deletion checklist
- Consolidate duplicated chart styling, cards/layout helpers, and service entrypoints
- Safe deletion via grep + static analysis + tests after each removal

## 7) Quality gates + testing + documentation updates
- Ruff formatting/lint, pytest baseline, optional mypy, pre-commit hooks, auditable docs

---

# PART A — UI/UX REDESIGN (FIGMA-READY SPECIFICATION)

## A1) Information Architecture — Screen Definitions

### Screen 1: Executive Dashboard (`pages/01_Dashboard.py`)

**Purpose:** Single-glance executive view for Minister-level decision making.

| Section | Content | Priority |
|---------|---------|----------|
| **Header Bar** | Period selector (Q/Year), Region filter, Language toggle, Data freshness indicator | P0 |
| **KPI Strip** | 3–6 hero metrics selected from the KPI catalog (value, delta, status badge) | P0 |
| **Executive Insights** | AI-generated narrative with 3–5 key insights + recommended next steps (phrased for decision-makers) | P0 |
| **Trust Signals** | Last refresh timestamp, data source count, completeness %, confidence badge | P1 |
| **Status Overview** | Traffic-light summary: on-track / at-risk / off-track counts (no hard-coded targets) | P1 |

**Visual Hierarchy:**
1. Primary composite KPI (if configured) as the hero element
2. KPI cards grid (2×2, right)
3. Executive Insights panel (full width, below)
4. Trust signals (footer bar)

---

### Screen 2: KPIs & Forecasting (`pages/02_KPIs.py`)

**Purpose:** Deep-dive into individual KPIs with ML-powered forecasting.

| Section | Content | Priority |
|---------|---------|----------|
| **KPI Categories** | Economic, Labor & Skills, Social & Digital, Environmental (collapsible sections) | P0 |
| **Metric Cards** | Value, delta, trend spark, status badge per KPI | P0 |
| **Forecasting Panel** | KPI selector, horizon slider (2–12 quarters), model selector, confidence bands chart | P0 |
| **Interpretation** | "What This Means" text + "Suggested Actions" bullets | P1 |
| **Forecast Details** | Expandable table with predicted values, upper/lower bounds | P2 |

**Visual Hierarchy:**
1. Category tabs or accordion
2. 3–4 column metric grid within each category
3. Forecasting section with prominent chart
4. Progressive disclosure for model details

---

### Screen 3: Trends & Early Warning (`pages/03_Trends.py`)

**Purpose:** Historical analysis + anomaly detection for proactive risk management.

| Section | Content | Priority |
|---------|---------|----------|
| **Indicator Trends** | Time-series chart, KPI selector, region filter | P0 |
| **Early Warning Panel** | Alert summary: Critical/Warning/Normal counts | P0 |
| **Anomaly Cards** | Severity badge, KPI name, period, description, Z-score | P0 |
| **Regional Comparison** | Horizontal bar chart, national average line | P1 |
| **Geographic Map** | Choropleth map with KPI selector | P1 |

**Visual Hierarchy:**
1. Alert summary strip (critical = red, warning = amber)
2. Trend chart (dominant visual)
3. Anomaly list (scrollable, max 5 visible)
4. Regional section below

---

### Screen 4: Data & Sources (`pages/04_Data.py`)

**Purpose:** Data lineage, quality metrics, and raw data exploration.

| Section | Content | Priority |
|---------|---------|----------|
| **Data Quality Overview** | Completeness %, freshness, issue count | P0 |
| **Source Systems** | List of integrated sources with last-sync status | P1 |
| **Coverage Matrix** | KPI × Period availability grid | P1 |
| **Raw Data Preview** | Paginated table with search/filter | P2 |
| **Export Options** | Excel, PDF, PowerPoint buttons | P2 |

---

## A2) Menu Mapping (No "Advanced Analytics")

**Previous Structure:**
```
├── Dashboard
├── KPIs
├── Trends
├── Data
├── Advanced Analytics ← REMOVED
├── Settings
├── Diagnostics
├── Data Management
└── Documentation
```

**New Structure:**
```
├── Dashboard           ← + AI Recommendations
├── KPIs                ← + Forecasting
├── Trends              ← + Early Warning + Regional Map
├── Data                ← (unchanged)
├── Settings            ← (unchanged)
├── Diagnostics         ← (unchanged, admin only)
└── Help                ← Merged: Data Management + Documentation
```

**Feature Redistribution:**

| Feature | FROM | TO | Rationale |
|---------|------|-----|-----------|
| KPI Forecasting | Advanced Analytics | KPIs | Forecasting is a KPI extension |
| Early Warning / Anomalies | Advanced Analytics | Trends | Anomalies are trend deviations |
| AI Recommendations | Advanced Analytics | Dashboard | Strategic guidance belongs at executive level |
| Regional Map | Advanced Analytics | Trends | Geographic analysis supports trend context |

---

## A3) Design System — Tokens & Components

### Typography Scale

| Token | Size | Weight | Usage |
|-------|------|--------|-------|
| `hero` | 48px | 800 | Gauge number, hero metrics |
| `h1` | 32px | 700 | Page titles |
| `h2` | 24px | 600 | Section headers |
| `h3` | 18px | 600 | Card titles |
| `h4` | 16px | 600 | Subsection titles |
| `body` | 14px | 400 | Body text |
| `caption` | 12px | 500 | Captions, labels |
| `small` | 11px | 400 | Secondary info |
| `tiny` | 10px | 500 | Badges, tags |

**Font Family:** `'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif`

---

### Spacing (8pt Grid)

| Token | Value | Usage |
|-------|-------|-------|
| `xs` | 4px | Tight spacing |
| `sm` | 8px | Inline gaps |
| `md` | 16px | Component padding |
| `lg` | 24px | Section gaps |
| `xl` | 32px | Page margins |
| `xxl` | 48px | Major separations |

---

### Colors — Institutional Palette

**Background Hierarchy:**
| Token | Hex | Usage |
|-------|-----|-------|
| `bg-deep` | `#0B1120` | Page background |
| `bg-main` | `#111827` | Canvas |
| `bg-card` | `#1E293B` | Cards |
| `bg-hover` | `#334155` | Hover states |

**Primary Accents:**
| Token | Hex | Usage |
|-------|-----|-------|
| `primary` | `#06B6D4` | Primary actions, links |
| `secondary` | `#3B82F6` | Secondary elements |
| `accent-purple` | `#8B5CF6` | Highlights, gauges |

**Status Colors:**
| Token | Hex | Usage |
|-------|-----|-------|
| `success` | `#10B981` | On-track, green status |
| `warning` | `#F59E0B` | At-risk, amber status |
| `critical` | `#EF4444` | Off-track, red status |

**Text Colors:**
| Token | Value | Usage |
|-------|-------|-------|
| `text-primary` | `rgba(255,255,255,0.95)` | Headlines |
| `text-secondary` | `rgba(255,255,255,0.78)` | Body |
| `text-muted` | `rgba(255,255,255,0.55)` | Labels |

---

### Border Radius

| Token | Value | Usage |
|-------|-------|-------|
| `radius-sm` | 6px | Buttons, inputs |
| `radius-md` | 8px | Small cards |
| `radius-lg` | 12px | Standard cards |
| `radius-xl` | 16px | Large cards, panels |
| `radius-full` | 9999px | Pills, badges |

---

### Shadows (2 Levels Only)

| Token | Value | Usage |
|-------|-------|-------|
| `shadow-card` | `0 4px 6px rgba(0,0,0,0.1), 0 20px 50px rgba(0,0,0,0.4)` | Default card |
| `shadow-elevated` | `0 8px 16px rgba(0,0,0,0.15), 0 30px 60px rgba(0,0,0,0.45)` | Hover, modals |

---

### Component Inventory

| Component | Variants | Usage |
|-----------|----------|-------|
| `KPICard` | default, compact, hero | Metric display |
| `StatusBadge` | green, amber, red, neutral | Status indicators |
| `SectionHeader` | with icon, without icon | Section titles |
| `ChartCard` | line, bar, gauge, map | Data visualization containers |
| `AlertCard` | critical, warning | Anomaly/alert display |
| `FilterBar` | period, region, kpi selector | Filter controls |
| `DataTable` | sortable, paginated | Data grid |
| `InsightPanel` | executive, detailed | AI insights display |
| `ProgressRing` | single, multi | Gauge visualizations |
| `EmptyState` | no-data, loading, error | Placeholder states |

---

## A4) Figma File Structure

```
📁 Analytics Hub Design System
├── 📄 00 — Foundations
│   ├── Colors
│   ├── Typography
│   ├── Spacing & Grid
│   ├── Shadows & Effects
│   └── Icons
├── 📄 01 — Components
│   ├── Buttons
│   ├── Cards
│   │   ├── KPI Card
│   │   ├── Chart Card
│   │   ├── Alert Card
│   │   └── Insight Panel
│   ├── Navigation
│   │   ├── Sidebar
│   │   └── Tabs
│   ├── Forms
│   │   ├── Selectors
│   │   ├── Sliders
│   │   └── Toggles
│   ├── Data Display
│   │   ├── Tables
│   │   ├── Badges
│   │   └── Progress
│   └── Feedback
│       ├── Empty States
│       └── Loaders
├── 📄 02 — Screens
│   ├── Dashboard
│   ├── KPIs
│   ├── Trends
│   └── Data
├── 📄 03 — Prototypes
│   └── Main Flow
└── 📄 04 — Handoff
    ├── Spacing Specs
    ├── Color Tokens
    └── Component States
```

**Auto-Layout Rules:**
- All components use Auto-Layout
- Consistent padding: 16px inner, 24px section
- Gap between elements: 8px (tight), 16px (normal), 24px (loose)
- Responsive breakpoints: 1280px (desktop), 1024px (tablet)

---

## A5) UX Rules & Patterns

### Progressive Disclosure
- Advanced forecasting options (model selection) behind "More Options" toggle
- Forecast details in collapsible expander
- Map visualization optional, collapses on mobile

### Smart Defaults
- Default period: Current quarter
- Default region: National (all)
- Default forecast horizon: 4 quarters
- Default model: Gradient Boosting (labeled "Standard Model")

### Cause → Insight → Action Flow
Every section follows:
1. **Cause:** What happened (the data)
2. **Insight:** Why it matters (interpretation)
3. **Action:** What to do (recommendation)

---

## A6) Developer Handoff Checklist

| Item | Specification |
|------|---------------|
| Spacing | Use 8pt grid; tokens: xs(4), sm(8), md(16), lg(24), xl(32) |
| Typography | Inter font; sizes per scale above |
| Colors | Use semantic tokens (status-green, not #10B981) |
| States | Define: default, hover, active, disabled, loading |
| Interactions | Hover: 150ms ease; Click: 100ms; Page: 200ms |
| Responsive | Desktop-first; graceful degradation to 1024px |
| RTL | Support Arabic with `dir="rtl"`; margins flip |
| Accessibility | Target strong contrast, visible focus, and readable charts; document known limitations | 

---

# PART B — CODEBASE REFACTOR PLAN

## B1) Refactor Objectives

1. **Remove unused code** — dead modules, orphaned functions
2. **Eliminate duplication** — consolidated theme, shared components
3. **Standardize patterns** — consistent naming, structure
4. **Improve modularity** — clear separation: UI / Domain / Data
5. **Ensure testability** — injectable dependencies, pure functions
6. **Add quality gates** — linting, formatting, type hints

---

## B2) Proposed Final Project Structure

```
analytics_hub_platform/
├── streamlit_app.py              # Entry point
├── pyproject.toml
├── requirements.txt
├── requirements-dev.txt
├── ruff.toml
├── alembic.ini
│
├── pages/                        # Streamlit multipage routes
│   ├── 01_Dashboard.py
│   ├── 02_KPIs.py
│   ├── 03_Trends.py
│   ├── 04_Data.py
│   ├── 05_Settings.py            # Renumbered
│   └── 06_Help.py                # Merged: Docs + Data Mgmt
│
├── app/                          # Application layer (NEW)
│   ├── __init__.py
│   ├── components/               # Reusable Streamlit components
│   │   ├── __init__.py
│   │   ├── kpi_card.py
│   │   ├── chart_card.py
│   │   ├── alert_card.py
│   │   ├── section_header.py
│   │   ├── filter_bar.py
│   │   └── empty_states.py
│   ├── layouts/                  # Page layouts
│   │   ├── __init__.py
│   │   ├── sidebar.py
│   │   └── page_shell.py
│   └── styles/                   # Consolidated styling
│       ├── __init__.py
│       ├── theme.py              # Single source: tokens, CSS
│       └── charts.py             # Plotly config
│
├── domain/                       # Business logic (MOVED)
│   ├── __init__.py
│   ├── models.py                 # Pydantic models
│   ├── kpis/
│   │   ├── __init__.py
│   │   ├── indicators.py         # KPI calculations
│   │   ├── catalog.py            # KPI catalog loader
│   │   └── thresholds.py         # Status logic
│   ├── forecasting/
│   │   ├── __init__.py
│   │   ├── forecaster.py         # KPIForecaster class
│   │   └── models.py             # ML model wrappers
│   ├── alerts/
│   │   ├── __init__.py
│   │   ├── anomaly_detector.py   # AnomalyDetector class
│   │   └── severity.py           # Severity enum
│   ├── recommendations/
│   │   ├── __init__.py
│   │   ├── insight_engine.py
│   │   └── llm_service.py
│   └── services.py               # Orchestration services
│
├── data/                         # Data access layer (NEW)
│   ├── __init__.py
│   ├── repository.py             # Repository pattern
│   ├── schemas/                  # SQLAlchemy models
│   │   ├── __init__.py
│   │   └── tables.py
│   ├── sources/                  # Data source adapters
│   │   └── __init__.py
│   └── quality/
│       ├── __init__.py
│       ├── checks.py
│       └── metrics.py
│
├── infra/                        # Infrastructure (RENAMED)
│   ├── __init__.py
│   ├── config.py                 # Settings, env loading
│   ├── database.py               # Engine, session
│   ├── logging.py                # Logging setup
│   ├── caching.py
│   └── auth.py                   # Auth stubs
│
├── config/                       # Static configuration
│   ├── kpi_catalog.yaml
│   ├── kpi_register.yaml
│   └── branding.py
│
├── locales/                      # i18n
│   ├── en.yaml
│   └── ar.yaml
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── unit/
│   │   ├── test_indicators.py
│   │   ├── test_forecaster.py
│   │   └── test_anomaly.py
│   ├── integration/
│   │   └── test_repository.py
│   └── smoke/
│       └── test_app_loads.py
│
├── scripts/
│   ├── audit_unused.py
│   ├── format_lint.ps1
│   └── run_tests.ps1
│
├── alembic/
│   └── versions/
│
└── docs/
    ├── ARCHITECTURE.md
    ├── DATA_CONTRACTS.md
    ├── CONFIGURATION.md
    └── REDESIGN_PLAN.md          # This document
```

---

## B3) Duplication Targets — Consolidation Plan

### Theme Duplication

**Current State (3 files):**
- `ui/theme.py` — Main theme (1170 lines)
- `ui/ui_theme.py` — Deprecated copy (180 lines)
- `ui/dark_components.py` — Inline styles + theme fragments

**Action:**
1. DELETE `ui/ui_theme.py` (marked deprecated)
2. EXTRACT all inline styles from `dark_components.py` → `theme.py`
3. CONSOLIDATE to single `app/styles/theme.py`

---

### Component Duplication

| Pattern | Current Files | Target |
|---------|--------------|--------|
| `section_header()` | `ui_components.py` + inline in pages | `app/components/section_header.py` |
| `metric_card()` | `ui_components.py` | `app/components/kpi_card.py` |
| `card_open/card_close` | `dark_components.py` | `app/components/chart_card.py` |
| `render_sidebar` | `dark_components.py` | `app/layouts/sidebar.py` |
| `apply_chart_theme` | Duplicated in multiple pages | `app/styles/charts.py` |

---

### Service Duplication

| Pattern | Current Files | Target |
|---------|--------------|--------|
| KPI Forecasting | `ml_services.py` + pages | `domain/forecasting/forecaster.py` |
| Anomaly Detection | `ml_services.py` | `domain/alerts/anomaly_detector.py` |
| LLM Recommendations | `llm_service.py` | `domain/recommendations/llm_service.py` |
| Executive Snapshot | `services.py` | `domain/services.py` (keep) |

---

### Chart Config Duplication

**Current:** `apply_chart_theme()` / `apply_dark_chart_layout()` appear in:
- `pages/02_KPIs.py`
- `pages/03_Trends.py`
- `ui/dark_components.py`
- `ui/pages/unified_dashboard.py`

**Action:** Single `get_chart_config()` in `app/styles/charts.py`

---

## B4) Safe Deletion Plan

### Phase 1: Static Analysis

```powershell
# Find unused imports
ruff check . --select F401 --output-format=json > unused_imports.json

# Find unused functions (via vulture)
pip install vulture
vulture analytics_hub_platform/ --min-confidence 80 > dead_code.txt
```

### Phase 2: Files to Delete

| File | Reason | Verification |
|------|--------|--------------|
| `ui/ui_theme.py` | Deprecated, superseded by `theme.py` | Grep for imports |
| `pages/05_Advanced_Analytics.py` | Already deleted | ✓ |
| `pages/07_Diagnostics.py` | Admin-only, move to Settings | Conditional |
| `pages/08_Data_Management.py` | Merged into Data (Management tab) | ✓ (no Python refs; file removed) |
| `pages/09_Documentation.py` | Replaced by Help (`pages/06_Help.py`) | ✓ (no Python refs; file removed) |
| `domain/advanced_analytics.py` | Functionality moved to submodules | Grep usage |

### Phase 3: Function Cleanup

| Function | Location | Action |
|----------|----------|--------|
| `render_advanced_analytics_sidebar` | `dark_components.py` | DELETE (no usages) |
| Inline `apply_chart_theme` | Multiple pages | CONSOLIDATE |
| `inject_dark_theme` | `dark_components.py` | CONSOLIDATE into theme |

### Phase 4: Verification

After each deletion:
```powershell
# Run app
streamlit run streamlit_app.py

# Run tests
pytest tests/ -v --tb=short

# Check imports
ruff check . --select F401,F811
```

---

## B5) Quality Gates

### Linting & Formatting (Already Configured)

```toml
# ruff.toml (existing, extend)
[lint]
select = [
    "E", "W", "F", "I", "B", "C4", "UP", "SIM",
    "PIE",    # Misc lints
    "PT",     # pytest style
    "RUF",    # Ruff-specific
]

[lint.isort]
known-first-party = ["analytics_hub_platform", "app", "domain", "data", "infra"]
```

### Type Checking

```powershell
# Add to CI
mypy analytics_hub_platform/ --ignore-missing-imports --check-untyped-defs
```

### Test Coverage

```powershell
# Optional coverage reporting (set thresholds only after agreeing a baseline)
pytest tests/ --cov=analytics_hub_platform
```

### Pre-commit Config

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.6.9
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.8.0
    hooks:
      - id: mypy
        additional_dependencies: [pydantic, pandas-stubs]
```

---

## B6) Phased Refactor Plan

### Phase 1: Immediate Cleanup
- [ ] Delete `ui/ui_theme.py`
- [ ] Delete orphaned `render_advanced_analytics_sidebar`
- [ ] Remove "Advanced" tab from unified dashboard
- [ ] Renumber pages: remove gaps (05, 06, 07 → 05, 06)
- [ ] Run full test suite, fix breaks

### Phase 2: Component Extraction
- [ ] Create `app/components/` folder
- [ ] Extract `kpi_card.py`, `section_header.py`, `chart_card.py`
- [ ] Update page imports to use new components
- [ ] Consolidate `apply_chart_theme` to `app/styles/charts.py`

### Phase 3: Domain Reorganization
- [ ] Create `domain/kpis/`, `domain/forecasting/`, `domain/alerts/`
- [ ] Move `indicators.py` → `domain/kpis/`
- [ ] Move `KPIForecaster` → `domain/forecasting/`
- [ ] Move `AnomalyDetector` → `domain/alerts/`
- [ ] Update all imports

### Phase 4: Infrastructure Cleanup
- [ ] Rename `infrastructure/` → `infra/`
- [ ] Merge `db_init.py` + `repository.py` into `data/`
- [ ] Delete unused infrastructure modules (audit, middleware, observability if not used)
- [ ] Consolidate config loading

### Phase 5: Documentation & Tests
- [ ] Update README with new structure
- [ ] Create ARCHITECTURE.md diagram
- [ ] Add DATA_CONTRACTS.md
- [ ] Add coverage reporting and set thresholds once baseline is agreed
- [ ] Add smoke tests for all pages

---

## B7) Minimal Test Plan

### Smoke Tests (Must Pass)

```python
# tests/smoke/test_app_loads.py
def test_streamlit_app_imports():
    """Verify main app imports without error."""
    import streamlit_app  # noqa

def test_all_pages_import():
    """Verify all pages import cleanly."""
    import pages.p01_Dashboard
    import pages.p02_KPIs
    import pages.p03_Trends
    import pages.p04_Data
    import pages.p05_Settings
```

### Unit Tests (Critical Path)

| Module | Test File | Coverage Target |
|--------|-----------|-----------------|
| `domain/kpis/indicators.py` | `test_indicators.py` | 90% |
| `domain/forecasting/forecaster.py` | `test_forecaster.py` | 80% |
| `domain/alerts/anomaly_detector.py` | `test_anomaly.py` | 80% |
| `data/repository.py` | `test_repository.py` | 75% |

### Integration Tests

```python
# tests/integration/test_full_flow.py
def test_dashboard_renders_with_data(test_db):
    """Dashboard renders with sample data."""
    from domain.services import get_executive_snapshot
    snapshot = get_executive_snapshot(...)
    assert snapshot["status"] != "error"
```

---

# SUMMARY CHECKLIST

## UI/UX Deliverables ✓
- [x] Information Architecture (4 screens)
- [x] Menu restructuring (no Advanced Analytics)
- [x] Design tokens (typography, spacing, colors)
- [x] Component inventory (10 components)
- [x] Figma file structure
- [x] UX rules (progressive disclosure, smart defaults)
- [x] Developer handoff checklist

## Codebase Deliverables ✓
- [x] Proposed folder structure
- [x] Duplication targets (theme, components, services)
- [x] Safe deletion checklist
- [x] Quality gates (ruff, mypy, pytest)
- [x] Phased refactor plan
- [x] Minimal test plan

---

**Next Steps:**
1. Review this plan with stakeholders
2. Create Figma file from tokens/specs
3. Execute Phase 1 cleanup
4. Iterate on component extraction
