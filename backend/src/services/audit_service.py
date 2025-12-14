"""
Audit service for logging operations.
"""
from uuid import UUID
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from src.models.audit_log import AuditLog


class AuditService:
    """Service for creating audit log entries."""
    
    @staticmethod
    def log_action(
        db: Session,
        tenant_id: UUID,
        action: str,
        entity_type: str,
        entity_id: UUID,
        user_id: Optional[UUID] = None,
        changes: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> AuditLog:
        """
        Create an audit log entry.
        
        Args:
            db: Database session
            tenant_id: Tenant ID
            action: Action name (e.g., 'inventory.movement.create')
            entity_type: Entity type (e.g., 'InventoryMovement')
            entity_id: Entity ID
            user_id: User ID who performed the action
            changes: Dictionary of changes (before/after)
            ip_address: Client IP address
            user_agent: Client user agent
            
        Returns:
            Created AuditLog entry
        """
        audit_log = AuditLog(
            tenant_id=tenant_id,
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            changes_json=changes,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        
        db.add(audit_log)
        db.commit()
        db.refresh(audit_log)
        
        return audit_log

