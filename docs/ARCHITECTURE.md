# Architecture

## Overview
This repository implements a Streamlit multi-page analytics hub with a layered architecture:

- **UI**: Streamlit pages and reusable UI components
- **Domain**: KPI calculations, forecasting, anomaly detection, recommendation logic
- **Data/Infra**: Repository + database/session/config/logging

## Package Map (Current)

```
analytics_hub_platform/
├── app/                      # Forward-looking UI layer (Phase 2+)
│   ├── components/           # Reusable UI building blocks
│   │   ├── kpi_card.py       # KPI tile rendering
│   │   ├── section_header.py # Page section headers
│   │   ├── chart_card.py     # Chart container wrappers
│   │   ├── alert_card.py     # Alert/anomaly display cards
│   │   ├── filter_bar.py     # Filter control bars
│   │   └── empty_states.py   # Loading/error/empty states
│   └── styles/
│       └── charts.py         # Centralized Plotly theming
├── domain/                   # Business logic layer
│   ├── kpis/                 # KPI calculations & indicators
│   ├── forecasting/          # Time series forecasting
│   ├── alerts/               # Anomaly detection
│   └── recommendations/      # Recommendation engine
├── infra/                    # Infrastructure facade
│   └── __init__.py           # Re-exports from infrastructure/
├── data/                     # Data access facade
│   └── __init__.py           # Repository shim
└── infrastructure/           # Legacy infra (being migrated)
    ├── repository.py         # Data access
    ├── async_db.py           # Database sessions
    └── ...
```

### Import Aliases
- `analytics_hub_platform.ui.*` — Streamlit UI and shared components
- `analytics_hub_platform.app.*` — Forward-looking UI components + styles (Phase 2+)
- `analytics_hub_platform.domain.*` — Business logic
- `analytics_hub_platform.data.*` — Data access facade (wraps `infrastructure` for now)
- `analytics_hub_platform.infra.*` — Infrastructure facade (wraps `infrastructure` for now)

## Migration Strategy
To avoid breaking imports, new packages are introduced as **canonical paths** while legacy
modules remain as thin shims. This allows incremental refactors with stable tests.

## Data Flow

```
┌─────────────┐     ┌─────────────────┐     ┌──────────────────┐
│  Streamlit  │────▶│  Domain Layer   │────▶│  Infrastructure  │
│   Pages     │     │  (KPIs, ML, …)  │     │  (Repo, DB, …)   │
└─────────────┘     └─────────────────┘     └──────────────────┘
       │                    │                        │
       ▼                    ▼                        ▼
┌─────────────┐     ┌─────────────────┐     ┌──────────────────┐
│ app/        │     │ domain/         │     │ infra/ & data/   │
│ components/ │     │ kpis/           │     │ (facades)        │
│ styles/     │     │ forecasting/    │     │                  │
└─────────────┘     │ alerts/         │     └──────────────────┘
                    └─────────────────┘
```

## Key Design Principles

1. **Facade Pattern** — New facade packages (`infra/`, `data/`) re-export from legacy
   `infrastructure/` to enable gradual migration without breaking imports.

2. **Component Extraction** — Reusable UI logic lives in `app/components/` with
   consistent theming from `app/styles/charts.py`.

3. **Domain Subpackages** — Business logic split into focused subpackages:
   - `kpis/` — Indicator calculations and thresholds
   - `forecasting/` — Time series prediction (Holt-Winters, linear regression)
   - `alerts/` — Anomaly detection with configurable thresholds
   - `recommendations/` — Actionable insights generation

4. **Backward Compatibility** — Shim modules maintain imports until migration complete.

