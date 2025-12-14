"""
PurchaseOrderItem model representing items in purchase orders.
"""
from sqlalchemy import Column, Integer, Numeric, ForeignKey, Index, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.models.base import BaseModel


class PurchaseOrderItem(BaseModel):
    """PurchaseOrderItem entity representing items in purchase orders."""
    
    __tablename__ = "purchase_order_items"
    
    purchase_order_id = Column(UUID(as_uuid=True), ForeignKey('purchase_orders.id'), nullable=False, index=True)
    product_id = Column(UUID(as_uuid=True), ForeignKey('products.id'), nullable=False, index=True)
    warehouse_id = Column(UUID(as_uuid=True), ForeignKey('warehouses.id'), nullable=True)  # Destination warehouse
    quantity = Column(Numeric(15, 3), nullable=False)
    unit_cost = Column(Numeric(15, 2), nullable=False)
    total_cost = Column(Numeric(15, 2), nullable=False)  # Calculated: quantity * unit_cost
    received_quantity = Column(Numeric(15, 3), nullable=False, default=0)
    line_number = Column(Integer, nullable=False)  # Ordering within PO
    
    # Relationships
    purchase_order = relationship("PurchaseOrder", back_populates="items")
    product = relationship("Product", backref="purchase_order_items")
    warehouse = relationship("Warehouse", backref="purchase_order_items")
    
    # Constraints
    __table_args__ = (
        Index('idx_purchase_order_items_purchase_order_id', 'purchase_order_id'),
        Index('idx_purchase_order_items_product_id', 'product_id'),
        CheckConstraint('quantity > 0', name='ck_po_item_quantity_positive'),
        CheckConstraint('unit_cost >= 0', name='ck_po_item_cost_non_negative'),
        CheckConstraint('received_quantity >= 0', name='ck_po_item_received_non_negative'),
        CheckConstraint('received_quantity <= quantity', name='ck_po_item_received_leq_quantity'),
    )
    
    def __repr__(self):
        return f"<PurchaseOrderItem(id={self.id}, po_id={self.purchase_order_id}, product_id={self.product_id}, quantity={self.quantity})>"
