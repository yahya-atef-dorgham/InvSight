"""
Inventory model representing current stock levels for products at warehouses.
"""
from sqlalchemy import Column, Numeric, Integer, DateTime, ForeignKey, UniqueConstraint, Index, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy import func

from src.models.base import BaseModel


class Inventory(BaseModel):
    """Inventory entity representing stock levels for products at warehouses."""
    
    __tablename__ = "inventory"
    
    product_id = Column(UUID(as_uuid=True), ForeignKey('products.id'), nullable=False, index=True)
    warehouse_id = Column(UUID(as_uuid=True), ForeignKey('warehouses.id'), nullable=False, index=True)
    quantity = Column(Numeric(15, 3), nullable=False, default=0)
    reserved_quantity = Column(Numeric(15, 3), nullable=False, default=0)  # For pending outbound movements
    minimum_stock = Column(Numeric(15, 3), nullable=True)
    safety_stock = Column(Numeric(15, 3), nullable=True)
    reorder_point = Column(Numeric(15, 3), nullable=True)  # Calculated from forecasts
    last_movement_at = Column(DateTime(timezone=True), nullable=True)
    last_updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    version = Column(Integer, nullable=False, default=0)  # For optimistic locking
    
    # Relationships
    product = relationship("Product", backref="inventory_items")
    warehouse = relationship("Warehouse", backref="inventory_items")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('tenant_id', 'product_id', 'warehouse_id', name='uq_inventory_product_warehouse'),
        Index('idx_inventory_product_warehouse', 'tenant_id', 'product_id', 'warehouse_id', unique=True),
        Index('idx_inventory_low_stock', 'tenant_id', 'quantity', 'minimum_stock'),
        Index('idx_inventory_warehouse', 'warehouse_id'),
        CheckConstraint('quantity >= 0', name='ck_inventory_quantity_non_negative'),
        CheckConstraint('reserved_quantity >= 0', name='ck_inventory_reserved_non_negative'),
        CheckConstraint('reserved_quantity <= quantity', name='ck_inventory_reserved_leq_quantity'),
    )
    
    @property
    def available_quantity(self):
        """Calculate available quantity (quantity - reserved)."""
        return float(self.quantity) - float(self.reserved_quantity)
    
    @property
    def is_low_stock(self):
        """Check if stock is below minimum threshold."""
        if self.minimum_stock is None:
            return False
        return float(self.quantity) < float(self.minimum_stock)
    
    def __repr__(self):
        return f"<Inventory(id={self.id}, product_id={self.product_id}, warehouse_id={self.warehouse_id}, quantity={self.quantity})>"
