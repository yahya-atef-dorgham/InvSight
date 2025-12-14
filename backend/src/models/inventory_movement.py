"""
InventoryMovement model representing changes in inventory quantity.
"""
from sqlalchemy import Column, String, Text, Numeric, DateTime, ForeignKey, CheckConstraint, Index, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy import func
import enum

from src.models.base import BaseModel


class MovementType(str, enum.Enum):
    """Movement type enumeration."""
    INBOUND = "inbound"
    OUTBOUND = "outbound"
    TRANSFER = "transfer"


class InventoryMovement(BaseModel):
    """InventoryMovement entity representing changes in inventory quantity."""
    
    __tablename__ = "inventory_movements"
    
    movement_type = Column(String(20), nullable=False, index=True)
    product_id = Column(UUID(as_uuid=True), ForeignKey('products.id'), nullable=False, index=True)
    source_warehouse_id = Column(UUID(as_uuid=True), ForeignKey('warehouses.id'), nullable=True, index=True)
    destination_warehouse_id = Column(UUID(as_uuid=True), ForeignKey('warehouses.id'), nullable=True, index=True)
    quantity = Column(Numeric(15, 3), nullable=False)
    quantity_before = Column(Numeric(15, 3), nullable=True)  # At source for transfers
    quantity_after = Column(Numeric(15, 3), nullable=True)  # At destination for transfers
    reference_number = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    performed_by = Column(UUID(as_uuid=True), nullable=False, index=True)
    performed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    approved_by = Column(UUID(as_uuid=True), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    product = relationship("Product", backref="movements")
    source_warehouse = relationship("Warehouse", foreign_keys=[source_warehouse_id], backref="outbound_movements")
    destination_warehouse = relationship("Warehouse", foreign_keys=[destination_warehouse_id], backref="inbound_movements")
    
    # Constraints
    __table_args__ = (
        Index('idx_inventory_movements_tenant_id', 'tenant_id'),
        Index('idx_inventory_movements_product_id', 'product_id'),
        Index('idx_inventory_movements_performed_at', 'performed_at'),
        Index('idx_inventory_movements_performed_by', 'performed_by'),
        Index('idx_inventory_movements_type', 'movement_type'),
        CheckConstraint(
            "movement_type IN ('inbound', 'outbound', 'transfer')",
            name='ck_movement_type'
        ),
        CheckConstraint(
            "(movement_type = 'inbound' AND source_warehouse_id IS NULL AND destination_warehouse_id IS NOT NULL) OR "
            "(movement_type = 'outbound' AND source_warehouse_id IS NOT NULL AND destination_warehouse_id IS NULL) OR "
            "(movement_type = 'transfer' AND source_warehouse_id IS NOT NULL AND destination_warehouse_id IS NOT NULL)",
            name='ck_movement_warehouses'
        ),
        CheckConstraint('quantity > 0', name='ck_movement_quantity_positive'),
    )
    
    def __repr__(self):
        return f"<InventoryMovement(id={self.id}, type={self.movement_type}, quantity={self.quantity})>"
