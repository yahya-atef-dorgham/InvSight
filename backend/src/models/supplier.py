"""
Supplier model representing external vendors.
"""
from sqlalchemy import Column, String, Text, Boolean, Numeric, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import UUID

from src.models.base import BaseModel


class Supplier(BaseModel):
    """Supplier entity representing external vendors."""
    
    __tablename__ = "suppliers"
    
    name = Column(String(255), nullable=False)
    contact_email = Column(String(255), nullable=True)
    contact_phone = Column(String(50), nullable=True)
    address = Column(Text, nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    country = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)
    payment_terms = Column(String(100), nullable=True)  # e.g., 'Net 30', 'Net 60'
    tax_id = Column(String(100), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    performance_score = Column(Numeric(5, 2), nullable=True)  # 0-100
    created_by = Column(UUID(as_uuid=True), nullable=True)
    updated_by = Column(UUID(as_uuid=True), nullable=True)
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('tenant_id', 'name', name='uq_suppliers_tenant_name'),
        Index('idx_suppliers_tenant_name', 'tenant_id', 'name', unique=True),
        Index('idx_suppliers_active', 'is_active'),
    )
    
    def __repr__(self):
        return f"<Supplier(id={self.id}, name={self.name}, is_active={self.is_active})>"
