"""
AIRecommendation model representing AI-generated recommendations.
"""
from sqlalchemy import Column, String, Numeric, DateTime, ForeignKey, Index, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB, TEXT
from sqlalchemy.orm import relationship
from sqlalchemy import func
import enum

from src.models.base import BaseModel


class RecommendationType(str, enum.Enum):
    """Recommendation type enumeration."""
    REORDER_POINT = "reorder_point"
    REORDER_QUANTITY = "reorder_quantity"
    PURCHASE_ORDER = "purchase_order"


class RecommendationStatus(str, enum.Enum):
    """Recommendation status enumeration."""
    ACTIVE = "active"
    APPROVED = "approved"
    REJECTED = "rejected"
    SUPERSEDED = "superseded"


class AIRecommendation(BaseModel):
    """AIRecommendation entity representing AI-generated recommendations."""
    
    __tablename__ = "ai_recommendations"
    
    recommendation_type = Column(String(50), nullable=False, index=True)
    product_id = Column(UUID(as_uuid=True), ForeignKey('products.id'), nullable=False, index=True)
    warehouse_id = Column(UUID(as_uuid=True), ForeignKey('warehouses.id'), nullable=False, index=True)
    forecast_id = Column(UUID(as_uuid=True), ForeignKey('forecasts.id'), nullable=True)
    recommended_value = Column(Numeric(15, 3), nullable=True)
    current_value = Column(Numeric(15, 3), nullable=True)
    urgency_score = Column(Numeric(5, 2), nullable=True)  # 0-100
    confidence_score = Column(Numeric(5, 2), nullable=True)  # 0-100
    explanation = Column(TEXT, nullable=True)
    explanation_json = Column(JSONB, nullable=True)  # Structured explanation data
    status = Column(String(20), nullable=False, default=RecommendationStatus.ACTIVE.value, index=True)
    actioned_at = Column(DateTime(timezone=True), nullable=True)
    actioned_by = Column(UUID(as_uuid=True), nullable=True)
    purchase_order_id = Column(UUID(as_uuid=True), nullable=True)  # FK to purchase_orders (will be added in US4)
    
    # Relationships
    product = relationship("Product", backref="recommendations")
    warehouse = relationship("Warehouse", backref="recommendations")
    forecast = relationship("Forecast", backref="recommendations")
    
    # Constraints
    __table_args__ = (
        Index('idx_ai_recommendations_product_warehouse', 'product_id', 'warehouse_id'),
        Index('idx_ai_recommendations_type_status', 'recommendation_type', 'status'),
        Index('idx_ai_recommendations_urgency', 'urgency_score'),
        CheckConstraint(
            "recommendation_type IN ('reorder_point', 'reorder_quantity', 'purchase_order')",
            name='ck_recommendation_type'
        ),
        CheckConstraint(
            "status IN ('active', 'approved', 'rejected', 'superseded')",
            name='ck_recommendation_status'
        ),
        CheckConstraint('recommended_value >= 0', name='ck_recommendation_value_non_negative'),
    )
    
    def __repr__(self):
        return f"<AIRecommendation(id={self.id}, type={self.recommendation_type}, status={self.status})>"
