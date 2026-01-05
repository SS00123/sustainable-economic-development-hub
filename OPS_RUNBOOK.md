# Operations Runbook

## Sustainable Economic Development Analytics Hub

**Version:** 1.0  
**Last Updated:** January 2026  
**Owner:** Ministry of Economy and Planning - IT Operations

---

## Table of Contents

1. [Quick Reference](#quick-reference)
2. [System Overview](#system-overview)
3. [Startup and Shutdown](#startup-and-shutdown)
4. [Health Checks](#health-checks)
5. [Common Issues and Resolutions](#common-issues-and-resolutions)
6. [Monitoring and Alerts](#monitoring-and-alerts)
7. [Backup and Recovery](#backup-and-recovery)
8. [Scaling](#scaling)
9. [Security Procedures](#security-procedures)
10. [Emergency Contacts](#emergency-contacts)

---

## Quick Reference

### Key URLs

| Environment | URL | Purpose |
|-------------|-----|---------|
| Production | https://analytics.mep.gov.sa | Production dashboard |
| Staging | https://staging-analytics.mep.gov.sa | Pre-production testing |
| Development | http://localhost:8501 | Local development |

### Quick Commands

```bash
# Check application health
curl -s https://analytics.mep.gov.sa/healthz

# View logs (Docker)
docker logs analytics-hub-prod --tail 100 -f

# Restart application (Docker)
docker-compose restart app

# Database backup
python scripts/backup_db.py --output /backups/$(date +%Y%m%d).sql
```

### Critical Contacts

| Role | Name | Phone | Email |
|------|------|-------|-------|
| On-Call Engineer | Rotation | +966-XXX-XXXX | oncall@mep.gov.sa |
| Database Admin | TBD | +966-XXX-XXXX | dba@mep.gov.sa |
| Security Team | SOC | +966-XXX-XXXX | security@mep.gov.sa |

---

## System Overview

### Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Load Balancer │────▶│  Streamlit App  │────▶│    SQLite DB    │
│   (nginx/ALB)   │     │   (Container)   │     │   (analytics    │
│                 │     │                 │     │    _hub.db)     │
└─────────────────┘     └─────────────────┘     └─────────────────┘
         │                      │
         │                      ▼
         │              ┌─────────────────┐
         │              │   File Storage  │
         │              │   (logs, cache) │
         │              └─────────────────┘
         │
         ▼
┌─────────────────┐
│   Monitoring    │
│   (Prometheus/  │
│   CloudWatch)   │
└─────────────────┘
```

### Components

| Component | Technology | Port | Health Endpoint |
|-----------|------------|------|-----------------|
| Web Application | Streamlit | 8501 | /Diagnostics |
| Database | SQLite | N/A | N/A |
| Cache | Streamlit Cache | N/A | Session state |
| Logging | Python logging | N/A | logs/*.log |

### Dependencies

- Python 3.11+
- Streamlit 1.28+
- pandas 2.0+
- SQLAlchemy 2.0+
- reportlab (optional, for PDF)
- kaleido (optional, for PNG)

---

## Startup and Shutdown

### Starting the Application

#### Docker (Production)

```bash
# Navigate to deployment directory
cd /opt/analytics-hub

# Start containers
docker-compose up -d

# Verify startup
docker-compose ps
docker-compose logs --tail 50 app
```

#### Local Development

```bash
# Activate virtual environment
source .venv/bin/activate  # Linux/Mac
.\.venv\Scripts\activate   # Windows

# Start application
streamlit run streamlit_app.py --server.port 8501

# Or with production settings
ANALYTICS_HUB_ENV=production streamlit run streamlit_app.py
```

### Graceful Shutdown

```bash
# Docker
docker-compose down

# Or force stop after timeout
docker-compose down --timeout 30

# Local
# Press Ctrl+C in terminal
```

### Startup Checklist

- [ ] Database file exists and is readable
- [ ] Log directory has write permissions
- [ ] Environment variables are set
- [ ] Port 8501 is available
- [ ] Memory >= 1GB available

---

## Health Checks

### Manual Health Check

1. Navigate to `/Diagnostics` page in browser
2. Verify all smoke checks pass:
   - ✅ Database Connection
   - ✅ Data Available
   - ✅ Environment Set
   - ✅ Version Defined
   - ✅ Disk Space OK

### Automated Health Check Script

```bash
#!/bin/bash
# health_check.sh

BASE_URL=${1:-"http://localhost:8501"}
TIMEOUT=10

# Check if app responds
if curl -s --max-time $TIMEOUT "$BASE_URL" > /dev/null; then
    echo "✅ Application responding"
else
    echo "❌ Application not responding"
    exit 1
fi

# Check database (via diagnostics page)
if curl -s --max-time $TIMEOUT "$BASE_URL/Diagnostics" | grep -q "healthy"; then
    echo "✅ Database healthy"
else
    echo "⚠️ Database check inconclusive"
fi

echo "Health check complete"
```

### Database Health Check

```python
# Quick database connectivity test
from analytics_hub_platform.infrastructure.db_init import get_engine

engine = get_engine()
with engine.connect() as conn:
    result = conn.execute(text("SELECT COUNT(*) FROM sustainability_indicators"))
    count = result.scalar()
    print(f"Database OK: {count} records")
```

---

## Common Issues and Resolutions

### Issue 1: Application Not Starting

**Symptoms:**
- Port 8501 not responding
- Container exits immediately

**Troubleshooting:**

```bash
# Check logs
docker logs analytics-hub-prod --tail 200

# Common fixes:
# 1. Port conflict
lsof -i :8501  # Check if port is in use
docker-compose down && docker-compose up -d

# 2. Missing environment variables
docker-compose config  # Verify env vars

# 3. Database file permissions
ls -la analytics_hub.db
chmod 644 analytics_hub.db
```

### Issue 2: Database Locked

**Symptoms:**
- "database is locked" errors
- Slow queries

**Resolution:**

```bash
# 1. Find and kill stuck processes
fuser analytics_hub.db  # Linux
handle analytics_hub.db  # Windows (Sysinternals)

# 2. Restart application
docker-compose restart app

# 3. If persists, copy database and restart
cp analytics_hub.db analytics_hub.db.bak
docker-compose restart app
```

### Issue 3: High Memory Usage

**Symptoms:**
- OOM kills
- Slow response times

**Resolution:**

```bash
# Check memory usage
docker stats

# Clear Streamlit cache
# Navigate to /Settings and click "Clear Cache"

# Or restart with memory limit
docker-compose down
# Update docker-compose.yml with mem_limit
docker-compose up -d
```

### Issue 4: Slow Dashboard Load

**Symptoms:**
- Page load > 5 seconds
- Timeout errors

**Troubleshooting:**

1. Check database query times in logs
2. Verify network connectivity
3. Check for large data uploads in progress
4. Review cache statistics on Diagnostics page

**Resolution:**

```bash
# Analyze slow queries
sqlite3 analytics_hub.db "EXPLAIN QUERY PLAN SELECT * FROM sustainability_indicators LIMIT 1;"

# Add indexes if needed
sqlite3 analytics_hub.db "CREATE INDEX IF NOT EXISTS idx_tenant_year ON sustainability_indicators(tenant_id, year);"

# Vacuum database
sqlite3 analytics_hub.db "VACUUM;"
```

### Issue 5: Export Failures

**Symptoms:**
- CSV export empty
- PDF generation fails
- PNG shows fallback message

**Resolution:**

```bash
# CSV: Check data exists
python -c "from analytics_hub_platform.infrastructure.repository import get_repository; print(len(get_repository().get_all_indicators()))"

# PDF: Verify reportlab installed
pip install reportlab

# PNG: Install kaleido
pip install -U kaleido
```

---

## Monitoring and Alerts

### Key Metrics to Monitor

| Metric | Warning | Critical | Action |
|--------|---------|----------|--------|
| Response Time | > 2s | > 5s | Scale up / optimize |
| Error Rate | > 1% | > 5% | Investigate logs |
| Memory Usage | > 70% | > 90% | Clear cache / scale |
| Disk Usage | > 80% | > 95% | Archive logs / expand |
| Database Size | > 500MB | > 1GB | Archive old data |

### Log Locations

| Log Type | Path | Rotation |
|----------|------|----------|
| Application | logs/analytics_hub.log | 10MB, 5 backups |
| Access | logs/access.log | Daily |
| Telemetry | logs/telemetry.jsonl | Weekly |
| Errors | logs/errors.log | 10MB, 10 backups |

### Alert Configuration (Example: Prometheus)

```yaml
groups:
  - name: analytics-hub
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate on Analytics Hub"
          
      - alert: SlowResponses
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 5
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Slow response times detected"
```

---

## Backup and Recovery

### Backup Procedures

#### Daily Database Backup

```bash
#!/bin/bash
# backup_daily.sh

BACKUP_DIR="/backups/daily"
DB_FILE="analytics_hub.db"
DATE=$(date +%Y%m%d)

# Create backup
sqlite3 $DB_FILE ".backup '$BACKUP_DIR/analytics_hub_$DATE.db'"

# Compress
gzip "$BACKUP_DIR/analytics_hub_$DATE.db"

# Retain last 7 days
find $BACKUP_DIR -name "*.gz" -mtime +7 -delete

echo "Backup complete: $BACKUP_DIR/analytics_hub_$DATE.db.gz"
```

#### Weekly Full Backup

```bash
#!/bin/bash
# backup_weekly.sh

BACKUP_DIR="/backups/weekly"
DATE=$(date +%Y%m%d)

# Full application backup
tar -czf "$BACKUP_DIR/analytics_hub_full_$DATE.tar.gz" \
    analytics_hub.db \
    .streamlit/ \
    logs/ \
    --exclude='*.pyc' \
    --exclude='__pycache__'
```

### Recovery Procedures

#### Database Recovery

```bash
# 1. Stop application
docker-compose down

# 2. Restore from backup
gunzip -c /backups/daily/analytics_hub_20260105.db.gz > analytics_hub.db

# 3. Verify integrity
sqlite3 analytics_hub.db "PRAGMA integrity_check;"

# 4. Restart application
docker-compose up -d
```

#### Full Recovery

```bash
# 1. Extract backup
tar -xzf /backups/weekly/analytics_hub_full_20260101.tar.gz

# 2. Verify files
ls -la analytics_hub.db
ls -la .streamlit/

# 3. Restart
docker-compose up -d
```

---

## Scaling

### Horizontal Scaling (Multiple Instances)

```yaml
# docker-compose-scaled.yml
version: '3.8'
services:
  app:
    image: analytics-hub:latest
    deploy:
      replicas: 3
    # Note: SQLite does not support multiple writers
    # Consider PostgreSQL for true horizontal scaling
```

### Vertical Scaling

```bash
# Increase container resources
docker update --memory 4g --cpus 2 analytics-hub-prod
```

### Database Scaling Path

For production beyond prototype:

1. **SQLite → PostgreSQL migration**
2. Connection pooling with PgBouncer
3. Read replicas for dashboard queries
4. Time-series partitioning for indicators

---

## Security Procedures

### Access Control

```bash
# Rotate secrets
# 1. Generate new password
NEW_PASSWORD=$(openssl rand -base64 32)

# 2. Update .env file
sed -i "s/AUTH_PASSWORD=.*/AUTH_PASSWORD=$NEW_PASSWORD/" .env

# 3. Restart application
docker-compose restart app

# 4. Notify administrators of new credentials
```

### Security Checklist

- [ ] HTTPS enabled with valid certificate
- [ ] Authentication enabled in production
- [ ] Secrets stored in secure vault (not .env in production)
- [ ] Database file permissions restricted (600)
- [ ] Log files don't contain PII
- [ ] Dependencies updated monthly

### Incident Response

1. **Detect**: Alert received or issue reported
2. **Contain**: Isolate affected components
3. **Analyze**: Review logs, identify root cause
4. **Remediate**: Apply fix
5. **Document**: Update runbook with learnings
6. **Review**: Post-incident review within 48 hours

---

## Emergency Contacts

| Level | Contact | When to Use |
|-------|---------|-------------|
| L1 | On-Call Engineer | Any issue during business hours |
| L2 | Team Lead | Escalation after 30 min |
| L3 | IT Director | Major outage > 1 hour |
| Security | SOC Team | Security incidents |

### Escalation Matrix

| Severity | Response Time | Escalation After |
|----------|--------------|------------------|
| Critical | 15 min | 30 min |
| High | 1 hour | 2 hours |
| Medium | 4 hours | 8 hours |
| Low | 24 hours | 48 hours |

---

## Appendix: Command Reference

### Docker Commands

```bash
# View running containers
docker-compose ps

# View logs
docker-compose logs -f app

# Enter container shell
docker-compose exec app /bin/bash

# Restart single service
docker-compose restart app

# Full rebuild
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Database Commands

```bash
# Connect to SQLite
sqlite3 analytics_hub.db

# Show tables
.tables

# Show schema
.schema sustainability_indicators

# Quick row count
SELECT COUNT(*) FROM sustainability_indicators;

# Export to CSV
.mode csv
.output export.csv
SELECT * FROM sustainability_indicators;
.output stdout
```

### Log Analysis

```bash
# Search for errors
grep -i error logs/analytics_hub.log | tail -20

# Count errors by type
grep -i error logs/analytics_hub.log | cut -d':' -f4 | sort | uniq -c | sort -rn

# View telemetry events
tail -100 logs/telemetry.jsonl | jq '.'

# Filter by event type
cat logs/telemetry.jsonl | jq 'select(.event_type == "page_view")'
```

---

*Last updated: January 2026*  
*Document owner: IT Operations Team*
