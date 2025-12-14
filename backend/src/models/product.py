"""
Product model representing items in the inventory catalog.
"""
from sqlalchemy import Column, String, Text, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import UUID

from src.models.base import BaseModel


class Product(BaseModel):
    """Product entity representing items in inventory catalog."""
    
    __tablename__ = "products"
    
    sku = Column(String(100), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True, index=True)
    unit_of_measure = Column(String(50), nullable=False)  # e.g., 'pieces', 'kg', 'liters'
    created_by = Column(UUID(as_uuid=True), nullable=True)
    updated_by = Column(UUID(as_uuid=True), nullable=True)
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('tenant_id', 'sku', name='uq_products_tenant_sku'),
        Index('idx_products_tenant_sku', 'tenant_id', 'sku', unique=True),
        Index('idx_products_category', 'category'),
    )
    
    def __repr__(self):
        return f"<Product(id={self.id}, sku={self.sku}, name={self.name})>"
