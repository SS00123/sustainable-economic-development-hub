# Risk Register

| Risk ID | Risk Description | Impact | Mitigation Strategy |
| :--- | :--- | :--- | :--- |
| R01 | `app.py` is a large monolith (1779 lines) | Hard to maintain, test, and debug. | Phase 2: Decompose into smaller components. |
| R02 | `unsafe_allow_html` usage scattered | Security risk (XSS), maintenance burden. | Phase 1: Centralize in `ui/html.py`. |
| R03 | Potential `datetime.UTC` usage (Python 3.11+) | Incompatibility with Python 3.10 environments. | Phase 1: Replace with `timezone.utc`. |
| R04 | SQLite in production | Concurrency issues, data loss risk if container is ephemeral. | Phase 3: Ensure persistent volume or switch to Postgres (if applicable, but sticking to SQLite for now as per requirements). |
| R05 | Missing Data Contracts | Data quality issues, UI breaks on schema changes. | Phase 3: Implement Data Contracts. |
| R06 | No Authentication | Unauthorized access to sensitive data. | Phase 3: Implement simple auth gate. |
