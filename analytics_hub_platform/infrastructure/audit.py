"""
Audit Logging Utility
Sustainable Economic Development Analytics Hub
Ministry of Economy and Planning

Provides audit logging functionality for tracking user actions.
"""

import json
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any

from analytics_hub_platform.infrastructure.db_init import get_engine, audit_log


logger = logging.getLogger(__name__)


def log_audit_event(
    action: str,
    tenant_id: Optional[str] = None,
    user_id: Optional[str] = None,
    resource_type: Optional[str] = None,
    resource_id: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    ip_address: Optional[str] = None,
) -> None:
    """
    Log an audit event to the database.
    
    Args:
        action: The action performed (e.g., "export_pdf", "view_dashboard")
        tenant_id: The tenant ID
        user_id: The user ID who performed the action
        resource_type: Type of resource affected (e.g., "report", "indicator")
        resource_id: ID of the specific resource
        details: Additional details as a dictionary
        ip_address: IP address of the client
    """
    try:
        engine = get_engine()
        
        details_json = json.dumps(details) if details else None
        
        with engine.connect() as conn:
            conn.execute(
                audit_log.insert().values(
                    timestamp=datetime.now(timezone.utc),
                    tenant_id=tenant_id,
                    user_id=user_id,
                    action=action,
                    resource_type=resource_type,
                    resource_id=resource_id,
                    details=details_json,
                    ip_address=ip_address,
                )
            )
            conn.commit()
            
        logger.info(
            f"Audit: {action} by {user_id or 'anonymous'} on {resource_type or 'N/A'}"
        )
        
    except Exception as e:
        # Don't fail the main operation if audit logging fails
        logger.warning(f"Failed to log audit event: {e}")


def get_audit_log(
    tenant_id: Optional[str] = None,
    user_id: Optional[str] = None,
    action: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = 100,
) -> list:
    """
    Retrieve audit log entries.
    
    Args:
        tenant_id: Filter by tenant
        user_id: Filter by user
        action: Filter by action type
        start_date: Filter by start date
        end_date: Filter by end date
        limit: Maximum number of entries to return
        
    Returns:
        List of audit log entries
    """
    try:
        engine = get_engine()
        
        query = audit_log.select()
        
        if tenant_id:
            query = query.where(audit_log.c.tenant_id == tenant_id)
        if user_id:
            query = query.where(audit_log.c.user_id == user_id)
        if action:
            query = query.where(audit_log.c.action == action)
        if start_date:
            query = query.where(audit_log.c.timestamp >= start_date)
        if end_date:
            query = query.where(audit_log.c.timestamp <= end_date)
            
        query = query.order_by(audit_log.c.timestamp.desc()).limit(limit)
        
        with engine.connect() as conn:
            result = conn.execute(query)
            return [dict(row._mapping) for row in result]
            
    except Exception as e:
        logger.error(f"Failed to retrieve audit log: {e}")
        return []
