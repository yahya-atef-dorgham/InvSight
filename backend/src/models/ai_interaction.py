"""
AIInteraction model representing AI assistant interactions.
"""
from sqlalchemy import Column, String, Text, Integer, Numeric, DateTime, Index, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy import func

from src.models.base import BaseModel


class AIInteraction(BaseModel):
    """AIInteraction entity representing AI assistant interactions."""
    
    __tablename__ = "ai_interactions"
    
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    interaction_type = Column(String(20), nullable=False)  # 'voice' or 'text'
    query_text = Column(Text, nullable=False)
    query_audio_url = Column(String(500), nullable=True)
    intent = Column(String(100), nullable=True, index=True)
    response_text = Column(Text, nullable=False)
    response_audio_url = Column(String(500), nullable=True)
    processing_duration_ms = Column(Integer, nullable=True)
    confidence_score = Column(Numeric(5, 2), nullable=True)  # 0-100
    entities_json = Column(JSONB, nullable=True)  # Extracted entities
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    # Constraints
    __table_args__ = (
        Index('idx_ai_interactions_tenant_id', 'tenant_id'),
        Index('idx_ai_interactions_user_id', 'user_id'),
        Index('idx_ai_interactions_intent', 'intent'),
        Index('idx_ai_interactions_created_at', 'created_at'),
        CheckConstraint("interaction_type IN ('voice', 'text')", name='ck_interaction_type'),
        CheckConstraint('processing_duration_ms >= 0', name='ck_processing_duration_non_negative'),
    )
    
    def __repr__(self):
        return f"<AIInteraction(id={self.id}, type={self.interaction_type}, intent={self.intent})>"
