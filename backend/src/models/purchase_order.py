"""
PurchaseOrder model representing purchase orders.
"""
from sqlalchemy import Column, String, Numeric, Date, DateTime, ForeignKey, UniqueConstraint, Index, CheckConstraint, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy import func
import enum

from src.models.base import BaseModel


class PurchaseOrderStatus(str, enum.Enum):
    """Purchase order status enumeration."""
    DRAFT = "draft"
    APPROVED = "approved"
    SENT = "sent"
    PARTIALLY_RECEIVED = "partially_received"
    RECEIVED = "received"
    CANCELLED = "cancelled"


class PurchaseOrder(BaseModel):
    """PurchaseOrder entity representing purchase orders."""
    
    __tablename__ = "purchase_orders"
    
    order_number = Column(String(100), nullable=False, index=True)
    supplier_id = Column(UUID(as_uuid=True), ForeignKey('suppliers.id'), nullable=False, index=True)
    status = Column(String(20), nullable=False, default=PurchaseOrderStatus.DRAFT.value, index=True)
    total_amount = Column(Numeric(15, 2), nullable=True)
    currency = Column(String(3), nullable=False, default='USD')
    expected_delivery_date = Column(Date, nullable=True)
    actual_delivery_date = Column(Date, nullable=True)
    created_by = Column(UUID(as_uuid=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    approved_by = Column(UUID(as_uuid=True), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    received_at = Column(DateTime(timezone=True), nullable=True)
    cancelled_at = Column(DateTime(timezone=True), nullable=True)
    cancelled_by = Column(UUID(as_uuid=True), nullable=True)
    cancellation_reason = Column(Text, nullable=True)
    ai_recommendation_id = Column(UUID(as_uuid=True), ForeignKey('ai_recommendations.id'), nullable=True, index=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    supplier = relationship("Supplier", backref="purchase_orders")
    items = relationship("PurchaseOrderItem", back_populates="purchase_order", cascade="all, delete-orphan")
    ai_recommendation = relationship("AIRecommendation", backref="purchase_orders")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('tenant_id', 'order_number', name='uq_purchase_orders_tenant_order_number'),
        Index('idx_purchase_orders_tenant_order_number', 'tenant_id', 'order_number', unique=True),
        Index('idx_purchase_orders_supplier_id', 'supplier_id'),
        Index('idx_purchase_orders_status', 'status'),
        Index('idx_purchase_orders_created_at', 'created_at'),
        Index('idx_purchase_orders_ai_recommendation_id', 'ai_recommendation_id'),
        CheckConstraint(
            "status IN ('draft', 'approved', 'sent', 'partially_received', 'received', 'cancelled')",
            name='ck_po_status'
        ),
    )
    
    def __repr__(self):
        return f"<PurchaseOrder(id={self.id}, order_number={self.order_number}, status={self.status})>"
