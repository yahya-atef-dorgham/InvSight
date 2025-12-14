"""
Audit log model for tracking all critical operations.
"""
from sqlalchemy import Column, String, Text, Integer, DateTime
from sqlalchemy.dialects.postgresql import UUID, INET, JSONB
from sqlalchemy import func

from src.models.base import BaseModel


class AuditLog(BaseModel):
    """Audit log entry for tracking operations."""
    
    __tablename__ = "audit_logs"
    
    user_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    action = Column(String(100), nullable=False, index=True)  # e.g., 'inventory.movement.create'
    entity_type = Column(String(50), nullable=False, index=True)  # e.g., 'InventoryMovement'
    entity_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    changes_json = Column(JSONB, nullable=True)  # Before/after values for updates
    ip_address = Column(INET, nullable=True)
    user_agent = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

