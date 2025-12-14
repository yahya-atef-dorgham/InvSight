"""
Voice service for managing voice queries and integrating with voice service.
"""
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc

from src.models.ai_interaction import AIInteraction
from src.services.voice_service_client import voice_service_client
from src.services.audit_service import AuditService


class VoiceService:
    """Service for voice query operations."""
    
    @staticmethod
    async def process_voice_query(
        db: Session,
        query_text: str,
        user_id: UUID,
        tenant_id: UUID,
        interaction_type: str = "voice",
        language: str = "en-US"
    ) -> AIInteraction:
        """
        Process voice query and generate response.
        
        Args:
            db: Database session
            query_text: Transcribed query text
            user_id: User ID
            tenant_id: Tenant ID
            interaction_type: Type of interaction
            language: Language code
            
        Returns:
            Created AIInteraction
        """
        import time
        start_time = time.time()
        
        # Call voice service
        try:
            voice_result = await voice_service_client.process_query(
                query_text=query_text,
                interaction_type=interaction_type,
                language=language
            )
        except Exception as e:
            # Fallback response if voice service unavailable
            voice_result = {
                "query_text": query_text,
                "intent": "unknown",
                "confidence_score": 0.0,
                "entities": {},
                "response_text": "I'm sorry, I'm having trouble processing your request right now. Please try again.",
                "response_audio_url": None,
                "processing_duration_ms": 0
            }
        
        processing_duration = int((time.time() - start_time) * 1000)
        
        # Create interaction record
        interaction = AIInteraction(
            tenant_id=tenant_id,
            user_id=user_id,
            interaction_type=interaction_type,
            query_text=query_text,
            intent=voice_result.get('intent'),
            response_text=voice_result.get('response_text', ''),
            response_audio_url=voice_result.get('response_audio_url'),
            processing_duration_ms=processing_duration,
            confidence_score=voice_result.get('confidence_score'),
            entities_json=voice_result.get('entities', {})
        )
        
        db.add(interaction)
        
        # Audit log
        AuditService.log_action(
            db,
            tenant_id=tenant_id,
            user_id=user_id,
            action="ai.voice.query",
            entity_type="AIInteraction",
            entity_id=interaction.id,
            changes={
                "query_text": query_text,
                "intent": voice_result.get('intent'),
                "confidence": float(voice_result.get('confidence_score', 0))
            }
        )
        
        db.commit()
        db.refresh(interaction)
        
        return interaction
    
    @staticmethod
    def get_interaction_history(
        db: Session,
        tenant_id: UUID,
        user_id: Optional[UUID] = None,
        intent: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[AIInteraction]:
        """Get interaction history with optional filters."""
        query = db.query(AIInteraction).filter(AIInteraction.tenant_id == tenant_id)
        
        if user_id:
            query = query.filter(AIInteraction.user_id == user_id)
        
        if intent:
            query = query.filter(AIInteraction.intent == intent)
        
        return query.order_by(desc(AIInteraction.created_at)).offset(skip).limit(limit).all()
