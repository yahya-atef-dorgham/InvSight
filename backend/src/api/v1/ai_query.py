"""
AI Query API endpoints for voice interactions.
"""
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel

from src.database.session import get_db
from src.api.middleware.tenant import get_tenant_id, get_user_id
from src.services.voice_service import VoiceService
from src.models.ai_interaction import AIInteraction

router = APIRouter(prefix="/ai", tags=["ai"])


class VoiceQueryRequest(BaseModel):
    """Voice query request."""
    query_text: str
    interaction_type: str = "voice"  # 'voice' or 'text'
    language: str = "en-US"


class VoiceQueryResponse(BaseModel):
    """Voice query response."""
    id: str
    query_text: str
    intent: str | None
    response_text: str
    response_audio_url: str | None
    confidence_score: float | None
    processing_duration_ms: int | None
    entities_json: dict | None
    created_at: str
    
    class Config:
        from_attributes = True


class AIInteractionResponse(BaseModel):
    """AI interaction response model."""
    id: str
    tenant_id: str
    user_id: str
    interaction_type: str
    query_text: str
    intent: str | None
    response_text: str
    confidence_score: float | None
    created_at: str
    
    class Config:
        from_attributes = True


@router.post("/voice/query", response_model=VoiceQueryResponse)
async def process_voice_query(
    query_data: VoiceQueryRequest,
    tenant_id: UUID = Depends(get_tenant_id),
    user_id: UUID = Depends(get_user_id),
    db: Session = Depends(get_db)
):
    """Process voice query and generate response."""
    if query_data.interaction_type not in ['voice', 'text']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="interaction_type must be 'voice' or 'text'"
        )
    
    try:
        interaction = await VoiceService.process_voice_query(
            db=db,
            query_text=query_data.query_text,
            user_id=user_id,
            tenant_id=tenant_id,
            interaction_type=query_data.interaction_type,
            language=query_data.language
        )
        return interaction
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Voice query processing failed: {str(e)}"
        )


@router.get("/interactions", response_model=List[AIInteractionResponse])
async def get_interaction_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    user_id: Optional[UUID] = Query(None),
    intent: Optional[str] = Query(None),
    tenant_id: UUID = Depends(get_tenant_id),
    db: Session = Depends(get_db)
):
    """Get AI interaction history."""
    interactions = VoiceService.get_interaction_history(
        db=db,
        tenant_id=tenant_id,
        user_id=user_id,
        intent=intent,
        skip=skip,
        limit=limit
    )
    return interactions
