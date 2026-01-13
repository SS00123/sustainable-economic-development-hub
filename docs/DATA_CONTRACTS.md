# Data Contracts

## KPI Catalog
Source of truth: `analytics_hub_platform/config/kpi_catalog.yaml`

Each KPI definition is expected to include:
- `id` (string)
- `display_name_en` / `display_name_ar`
- `unit`
- `min_value` / `max_value` (for normalization)
- `thresholds` (green/amber/red ranges)
- `higher_is_better` (boolean)
- `default_weight_in_sustainability_index` (float)

## Repository Outputs
The repository layer should return values as:
- `float | None` for numeric KPIs
- ISO8601 strings for timestamps
- consistent region identifiers (e.g., `"national"`, `"riyadh"`)

