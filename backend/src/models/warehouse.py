"""
Warehouse model representing physical storage locations.
"""
from sqlalchemy import Column, String, Text, Boolean, Numeric, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import UUID

from src.models.base import BaseModel


class Warehouse(BaseModel):
    """Warehouse entity representing physical storage locations."""
    
    __tablename__ = "warehouses"
    
    name = Column(String(255), nullable=False)
    address = Column(Text, nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    country = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)
    capacity_total = Column(Numeric(15, 2), nullable=True)  # Total capacity
    capacity_unit = Column(String(50), nullable=True)  # e.g., 'cubic_meters', 'square_meters'
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    created_by = Column(UUID(as_uuid=True), nullable=True)
    updated_by = Column(UUID(as_uuid=True), nullable=True)
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('tenant_id', 'name', name='uq_warehouses_tenant_name'),
        Index('idx_warehouses_tenant_name', 'tenant_id', 'name', unique=True),
        Index('idx_warehouses_active', 'is_active'),
    )
    
    def __repr__(self):
        return f"<Warehouse(id={self.id}, name={self.name}, is_active={self.is_active})>"
