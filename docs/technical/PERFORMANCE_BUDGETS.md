# Performance Budgets

## Sustainable Economic Development Analytics Hub

**Version:** 1.0  
**Last Updated:** January 2026  
**Owner:** Engineering Team

---

## Overview

This document defines performance budgets for the Analytics Hub Platform. Performance budgets are critical metrics that must be met to ensure a good user experience, particularly for government stakeholders accessing the dashboard from various network conditions across Saudi Arabia.

---

## Page Load Budgets

### Initial Page Load

| Metric | Budget | Measurement | Tool |
|--------|--------|-------------|------|
| First Contentful Paint (FCP) | < 1.5s | Time to first content render | Lighthouse / Browser DevTools |
| Largest Contentful Paint (LCP) | < 2.5s | Time to largest element render | Lighthouse / Browser DevTools |
| Time to Interactive (TTI) | < 3.5s | Time until page is fully interactive | Lighthouse |
| Total Page Weight | < 2MB | Complete page resources | Network tab |

### Streamlit-Specific Metrics

| Metric | Budget | Description |
|--------|--------|-------------|
| Streamlit Connection Time | < 1s | WebSocket connection established |
| Initial Render | < 2s | First meaningful content displayed |
| Component Re-render | < 500ms | Update after filter change |
| Cache Hit Latency | < 50ms | Cached data retrieval |

---

## API Response Budgets

### Database Queries

| Query Type | Budget | Example |
|------------|--------|---------|
| Simple SELECT | < 100ms | Get all indicators for current tenant |
| Filtered SELECT | < 200ms | Indicators by pillar and year |
| Aggregation | < 300ms | SUM/AVG across years |
| Complex JOIN | < 500ms | Multi-table queries |
| Full Table Scan | < 1s | Should be avoided; add indexes |

### Data Operations

| Operation | Budget | Constraint |
|-----------|--------|------------|
| CSV Upload (< 1MB) | < 2s | Includes parsing + validation |
| CSV Upload (1-10MB) | < 10s | Progress indicator required |
| Excel Upload (< 1MB) | < 3s | Additional parsing overhead |
| Data Quality Check | < 5s | All 9 DQ rules on 10K rows |
| Export to CSV | < 1s | Up to 100K rows |
| Export to PNG | < 3s | Single chart |
| Export to PDF | < 5s | Executive brief with 3 sections |

---

## Dashboard-Specific Budgets

### Main Dashboard (Page 1)

| Component | Budget | Notes |
|-----------|--------|-------|
| KPI Cards Load | < 500ms | 4-6 summary cards |
| Primary Chart | < 1s | Main visualization |
| Filter Dropdown | < 200ms | Options populated |
| Filter Apply | < 500ms | Dashboard update |

### KPIs Page (Page 2)

| Component | Budget | Notes |
|-----------|--------|-------|
| KPI List Render | < 1s | All KPIs with sparklines |
| KPI Detail View | < 500ms | Single KPI expanded view |
| Trend Chart | < 1s | Historical trend rendering |

### Trends Page (Page 3)

| Component | Budget | Notes |
|-----------|--------|-------|
| Multi-year Chart | < 1.5s | 10 years of data |
| Pillar Comparison | < 1s | 4 pillars side-by-side |
| Animation Frame | < 16ms | 60fps for transitions |

### Data Management (Page 8)

| Component | Budget | Notes |
|-----------|--------|-------|
| Data Preview | < 500ms | First 100 rows |
| DQ Report | < 5s | Full data quality analysis |
| Upload Progress | Real-time | Updates every 100ms |

### Diagnostics (Page 7)

| Component | Budget | Notes |
|-----------|--------|-------|
| Health Checks | < 2s | All system checks |
| Cache Stats | < 100ms | In-memory stats |
| Log Fetch | < 500ms | Last 50 entries |

---

## Memory Budgets

### Application Memory

| Component | Budget | Notes |
|-----------|--------|-------|
| Base Application | < 256MB | Without data loaded |
| Per Session | < 100MB | Additional per user session |
| DataFrame Cache | < 512MB | LRU eviction at limit |
| Total Application | < 1GB | Container memory limit |

### Browser Memory

| Metric | Budget | Notes |
|--------|--------|-------|
| JavaScript Heap | < 100MB | Avoid memory leaks |
| DOM Nodes | < 1500 | Streamlit manages this |
| Event Listeners | < 500 | Cleanup on page change |

---

## Network Budgets

### Asset Sizes

| Asset Type | Budget | Notes |
|------------|--------|-------|
| HTML | < 50KB | Initial page |
| CSS | < 200KB | All stylesheets |
| JavaScript | < 500KB | Bundled, gzipped |
| Images | < 500KB | Total per page |
| Fonts | < 100KB | Subset if possible |

### API Payloads

| Endpoint | Budget | Notes |
|----------|--------|-------|
| Dashboard data | < 100KB | JSON response |
| Full export | < 5MB | Chunked if larger |
| Chart data | < 50KB | Per visualization |

### Network Conditions

The application should be usable under these conditions:

| Condition | Min Speed | Latency | Target |
|-----------|-----------|---------|--------|
| Fast 4G | 12 Mbps | 50ms | Excellent experience |
| Slow 4G | 4 Mbps | 150ms | Good experience |
| 3G | 1.5 Mbps | 300ms | Acceptable experience |
| Slow 3G | 400 Kbps | 400ms | Basic functionality |

---

## Measurement Methods

### Automated Testing

```python
# Performance test example
import time
from analytics_hub_platform.infrastructure.telemetry import timed

@timed
def measure_database_query():
    """Measure database query performance."""
    from analytics_hub_platform.infrastructure.repository import get_repository
    repo = get_repository()
    start = time.perf_counter()
    indicators = repo.get_all_indicators()
    elapsed = time.perf_counter() - start
    assert elapsed < 0.5, f"Query too slow: {elapsed:.3f}s"
    return len(indicators)
```

### Integration with Telemetry

```python
from analytics_hub_platform.infrastructure.telemetry import (
    get_telemetry,
    TimingContext,
)

# Track operation timing
with TimingContext("data_load", {"page": "dashboard"}):
    data = load_dashboard_data()
```

### Lighthouse CI Configuration

```yaml
# .lighthouserc.json
{
  "ci": {
    "collect": {
      "url": ["http://localhost:8501/"],
      "numberOfRuns": 3
    },
    "assert": {
      "assertions": {
        "first-contentful-paint": ["error", {"maxNumericValue": 1500}],
        "largest-contentful-paint": ["error", {"maxNumericValue": 2500}],
        "interactive": ["error", {"maxNumericValue": 3500}],
        "total-byte-weight": ["warning", {"maxNumericValue": 2097152}]
      }
    }
  }
}
```

### Pytest Performance Tests

```python
# tests/test_performance.py
import pytest
import time

class TestPerformanceBudgets:
    """Verify performance budgets are met."""
    
    def test_database_query_under_budget(self, repository):
        """Database queries complete within budget."""
        start = time.perf_counter()
        indicators = repository.get_all_indicators()
        elapsed = time.perf_counter() - start
        
        assert elapsed < 0.5, f"Query exceeded 500ms budget: {elapsed:.3f}s"
    
    def test_dq_check_under_budget(self, sample_dataframe):
        """Data quality check completes within budget."""
        from analytics_hub_platform.infrastructure.data_quality import (
            DataQualityChecker,
        )
        
        checker = DataQualityChecker(sample_dataframe)
        start = time.perf_counter()
        report = checker.generate_report()
        elapsed = time.perf_counter() - start
        
        assert elapsed < 5.0, f"DQ check exceeded 5s budget: {elapsed:.3f}s"
    
    def test_csv_export_under_budget(self, large_dataframe):
        """CSV export completes within budget."""
        from analytics_hub_platform.utils.export_utils import (
            export_dataframe_to_csv,
        )
        
        start = time.perf_counter()
        csv_bytes = export_dataframe_to_csv(large_dataframe)
        elapsed = time.perf_counter() - start
        
        assert elapsed < 1.0, f"Export exceeded 1s budget: {elapsed:.3f}s"
```

---

## Budget Enforcement

### CI/CD Gate

Performance budgets should be checked in CI/CD:

```yaml
# .github/workflows/performance.yml
name: Performance Budget Check

on: [push, pull_request]

jobs:
  performance:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Run performance tests
        run: pytest tests/test_performance.py -v --tb=short
```

### Real-time Monitoring

Track budgets in production via telemetry:

```python
from analytics_hub_platform.infrastructure.telemetry import (
    get_telemetry,
    EventType,
)

telemetry = get_telemetry()

# After each page load, check against budget
def check_performance_budget(metric: str, value: float, budget: float):
    """Log budget violations."""
    if value > budget:
        telemetry.track_error(
            f"Performance budget exceeded: {metric}",
            {
                "metric": metric,
                "value": value,
                "budget": budget,
                "exceeded_by": f"{((value - budget) / budget) * 100:.1f}%",
            },
        )
```

---

## Budget Review Process

### Monthly Review

1. **Collect metrics** from telemetry logs
2. **Analyze trends** - are we trending toward or away from budgets?
3. **Identify outliers** - which pages/operations exceed budgets?
4. **Prioritize fixes** - address critical budget violations
5. **Adjust budgets** - if consistently meeting, tighten; if unrealistic, discuss

### Budget Change Process

1. Create RFC (Request for Comments) explaining proposed change
2. Provide data showing current performance
3. Get engineering team approval
4. Update this document
5. Update CI/CD gates

---

## Appendix: Performance Optimization Tips

### Database Optimization

```sql
-- Add indexes for common queries
CREATE INDEX IF NOT EXISTS idx_indicators_tenant_year 
    ON sustainability_indicators(tenant_id, year);

CREATE INDEX IF NOT EXISTS idx_indicators_pillar 
    ON sustainability_indicators(pillar);

-- Vacuum periodically
VACUUM;

-- Analyze for query optimizer
ANALYZE;
```

### Streamlit Optimization

```python
# Use caching effectively
@st.cache_data(ttl=300)  # 5 minute TTL
def load_dashboard_data():
    """Cache dashboard data."""
    return repository.get_dashboard_summary()

# Use session state for expensive computations
if "processed_data" not in st.session_state:
    st.session_state.processed_data = expensive_computation()

# Lazy load heavy components
if st.button("Show detailed analysis"):
    # Only load when user requests
    detailed_data = load_detailed_analysis()
```

### Data Loading Optimization

```python
# Load only needed columns
df = pd.read_csv(file, usecols=["indicator_name", "value", "year"])

# Use appropriate dtypes
df = pd.read_csv(file, dtype={
    "indicator_name": "category",
    "pillar": "category",
    "value": "float32",
    "year": "int16",
})

# Chunk large files
for chunk in pd.read_csv(file, chunksize=10000):
    process_chunk(chunk)
```

---

## Summary Table

| Category | Metric | Budget | Priority |
|----------|--------|--------|----------|
| Page Load | FCP | < 1.5s | P0 |
| Page Load | LCP | < 2.5s | P0 |
| Page Load | TTI | < 3.5s | P0 |
| Database | Simple Query | < 100ms | P1 |
| Database | Complex Query | < 500ms | P1 |
| Export | CSV | < 1s | P1 |
| Export | PDF | < 5s | P2 |
| Memory | Application | < 1GB | P1 |
| Memory | Browser Heap | < 100MB | P2 |
| Network | API Response | < 100KB | P2 |

---

*Last updated: January 2026*  
*Document owner: Engineering Team*
