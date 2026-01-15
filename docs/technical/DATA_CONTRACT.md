# Data Contract
## Sustainable Economic Development Analytics Hub

**Version:** 1.0  
**Last Updated:** 2026-01-05  
**Owner:** Eng. Sultan Albuqami  

---

## Overview

This document defines the data contracts for each dashboard section, including:
- Required fields and their specifications
- Data grain (granularity)
- Units and formats
- Allowed ranges and validation rules
- Data sources

---

## Core Data Table: `sustainability_indicators`

### Table Grain
- **Primary Key:** `(tenant_id, year, quarter, region)`
- **Grain:** One row per tenant, year, quarter, and region combination
- **Refresh Frequency:** Quarterly

### Common Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `tenant_id` | STRING(50) | ✅ | Tenant identifier (e.g., "ministry_economy") |
| `year` | INTEGER | ✅ | Calendar year (2020-2030) |
| `quarter` | INTEGER | ✅ | Quarter (1-4) |
| `region` | STRING(100) | ✅ | Administrative region name |
| `load_timestamp` | DATETIME | Auto | UTC timestamp of data load |
| `load_batch_id` | STRING(50) | Auto | Batch identifier for tracing |
| `source_system` | STRING(100) | ⚪ | Origin system identifier |
| `data_quality_score` | FLOAT | ⚪ | Quality score (0-100) |

---

## Section 1: Economic Pillar

### Dashboard Location
- Hero KPI Cards (GDP Growth, Foreign Investment)
- Economic Pillar Section
- Trends Page

### Fields

| Field | Type | Unit | Range | Source | Description |
|-------|------|------|-------|--------|-------------|
| `gdp_growth` | FLOAT | Percent | -20.0 to 30.0 | GASTAT | Year-over-year GDP growth rate |
| `gdp_total` | FLOAT | Billion SAR | 0 to 5000 | GASTAT | Total GDP value |
| `foreign_investment` | FLOAT | Billion SAR | 0 to 500 | MISA | Foreign direct investment inflows |
| `export_diversity_index` | FLOAT | Index (0-100) | 0 to 100 | MOC | Export diversification score |
| `economic_complexity` | FLOAT | Index | -5.0 to 5.0 | Vision 2030 | Economic complexity index |

### Validation Rules

```python
# GDP growth should be within realistic bounds
assert -20.0 <= gdp_growth <= 30.0, "GDP growth out of range"

# Foreign investment must be non-negative
assert foreign_investment >= 0, "FDI cannot be negative"

# Export diversity is a normalized index
assert 0 <= export_diversity_index <= 100, "Export index must be 0-100"
```

### Aggregation Rules
- **National Level:** Sum of regional `gdp_total`, weighted average of `gdp_growth`
- **Trend Calculation:** Quarter-over-quarter percentage change

---

## Section 2: Social Pillar

### Dashboard Location
- Hero KPI Cards (Unemployment Rate)
- Social Pillar Section
- KPIs Page

### Fields

| Field | Type | Unit | Range | Source | Description |
|-------|------|------|-------|--------|-------------|
| `unemployment_rate` | FLOAT | Percent | 0 to 50 | GASTAT | Unemployment rate |
| `green_jobs` | FLOAT | Thousands | 0 to 10000 | MLSD | Number of green economy jobs |
| `skills_gap_index` | FLOAT | Index (0-100) | 0 to 100 | HRDF | Skills mismatch indicator |
| `social_progress_score` | FLOAT | Index (0-100) | 0 to 100 | SPI | Social Progress Index score |
| `digital_readiness` | FLOAT | Index (0-100) | 0 to 100 | MCIT | Digital transformation readiness |
| `innovation_index` | FLOAT | Index (0-100) | 0 to 100 | KACST | Innovation capability score |
| `population` | FLOAT | Millions | 0 to 50 | GASTAT | Regional population |

### Validation Rules

```python
# Unemployment rate constraints
assert 0 <= unemployment_rate <= 50, "Unemployment rate out of range"

# Index fields must be 0-100
for field in [social_progress_score, digital_readiness, innovation_index]:
    assert 0 <= field <= 100, f"{field} must be 0-100"

# Population must be positive
assert population > 0, "Population must be positive"
```

### Aggregation Rules
- **National Level:** Population-weighted averages for rates/indices
- **Green Jobs:** Sum across regions

---

## Section 3: Environmental Pillar

### Dashboard Location
- Hero KPI Cards (Renewable Share)
- Environmental Pillar Section
- Trends Page

### Fields

| Field | Type | Unit | Range | Source | Description |
|-------|------|------|-------|--------|-------------|
| `co2_index` | FLOAT | Index (0-100) | 0 to 100 | PME | Carbon efficiency index |
| `co2_total` | FLOAT | Million tonnes | 0 to 1000 | PME | Total CO2 emissions |
| `renewable_share` | FLOAT | Percent | 0 to 100 | SEC | Renewable energy percentage |
| `energy_intensity` | FLOAT | MJ/SAR | 0 to 50 | SEC | Energy per unit GDP |
| `water_efficiency` | FLOAT | Index (0-100) | 0 to 100 | MEWA | Water use efficiency |
| `waste_recycling_rate` | FLOAT | Percent | 0 to 100 | MME | Waste recycling percentage |
| `forest_coverage` | FLOAT | Percent | 0 to 100 | PME | Forest/green coverage |
| `air_quality_index` | FLOAT | AQI | 0 to 500 | PME | Air quality index |

### Derived Fields

| Field | Calculation | Unit |
|-------|-------------|------|
| `co2_per_gdp` | `co2_total / gdp_total` | Tonnes/Million SAR |
| `co2_per_capita` | `co2_total / population` | Tonnes/person |

### Validation Rules

```python
# Percentage fields must be 0-100
for field in [renewable_share, waste_recycling_rate, forest_coverage]:
    assert 0 <= field <= 100, f"{field} must be 0-100"

# AQI uses standard range
assert 0 <= air_quality_index <= 500, "AQI must be 0-500"

# CO2 must be non-negative
assert co2_total >= 0, "CO2 cannot be negative"
```

---

## Section 4: Composite Indicators

### Dashboard Location
- Hero Section (Sustainability Index)
- Key Insights Section
- KPIs (Forecasting)
- Trends (Early Warning)

### Fields

| Field | Type | Unit | Range | Source | Description |
|-------|------|------|-------|--------|-------------|
| `sustainability_index` | FLOAT | Index (0-100) | 0 to 100 | Calculated | Composite sustainability score |

### Calculation Method

Authoritative definitions for composite indicators live in:
- `analytics_hub_platform/config/kpi_catalog.yaml` (definitions/thresholds if configured)
- `analytics_hub_platform/domain/kpis/indicators.py` (calculation utilities)

This section is informational only and should not be treated as a formal specification of weights/thresholds.

---

## Section 5: Regional Breakdown

### Dashboard Location
- Regional Analysis (Director View)
- Data Page (detailed tables)

### Grain
- Same as core table: one row per region per period

### Required Regions (Saudi Arabia)

| Region Code | English Name | Arabic Name |
|-------------|--------------|-------------|
| RIY | Riyadh | الرياض |
| MKH | Makkah | مكة المكرمة |
| MDN | Madinah | المدينة المنورة |
| QAS | Qassim | القصيم |
| EST | Eastern | الشرقية |
| ASR | Asir | عسير |
| TBK | Tabuk | تبوك |
| HAL | Hail | حائل |
| NBO | Northern Borders | الحدود الشمالية |
| JZN | Jazan | جازان |
| NJN | Najran | نجران |
| BAH | Bahah | الباحة |
| JWF | Jawf | الجوف |

---

## Data Quality Rules

### Completeness

| Category | Required Coverage | Threshold |
|----------|-------------------|-----------|
| Core fields | All required fields populated | 100% |
| Economic indicators | GDP, FDI | ≥ 95% |
| Social indicators | Unemployment, Green Jobs | ≥ 90% |
| Environmental indicators | CO2, Renewable | ≥ 90% |

### Timeliness

| Check | Rule |
|-------|------|
| Data freshness | `load_timestamp` within 45 days of quarter end |
| Historical coverage | At least 8 quarters of history |
| No future data | `year` ≤ current year |

### Validity

| Check | Rule |
|-------|------|
| Range validation | All values within documented ranges |
| Referential integrity | All regions match allowed list |
| No duplicates | Unique constraint on (tenant, year, quarter, region) |

### Outlier Detection

```python
# Z-score based outlier detection (|z| > 3)
for field in numeric_fields:
    z_score = (value - mean) / std_dev
    if abs(z_score) > 3:
        flag_as_outlier(field, value)

# Quarter-over-quarter change bounds
max_quarterly_change = {
    "gdp_growth": 10,  # percentage points
    "unemployment_rate": 5,
    "renewable_share": 5,
}
```

---

## Data Sources

| Source Code | Full Name | Data Types | Update Frequency |
|-------------|-----------|------------|------------------|
| GASTAT | General Authority for Statistics | GDP, Population, Employment | Quarterly |
| MISA | Ministry of Investment | FDI | Quarterly |
| MOC | Ministry of Commerce | Trade, Exports | Monthly |
| PME | Presidency of Meteorology and Environment | Emissions, Air Quality | Monthly |
| SEC | Saudi Electricity Company | Energy, Renewables | Monthly |
| MLSD | Ministry of Labor and Social Development | Jobs, Labor | Quarterly |
| MEWA | Ministry of Environment, Water, Agriculture | Water, Agriculture | Quarterly |
| HRDF | Human Resources Development Fund | Skills, Training | Annual |

---

## Change Log

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-05 | System | Initial contract definition |

---

## Appendix: Sample Upload Template

See `templates/data_upload_template.xlsx` for the expected upload format.

### Required Columns
```
tenant_id, year, quarter, region, gdp_growth, gdp_total, foreign_investment,
export_diversity_index, economic_complexity, unemployment_rate, green_jobs,
skills_gap_index, social_progress_score, digital_readiness, innovation_index,
population, co2_index, co2_total, renewable_share, energy_intensity,
water_efficiency, waste_recycling_rate, forest_coverage, air_quality_index
```

### Optional Columns
```
source_system, data_quality_score
```
