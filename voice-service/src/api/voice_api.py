"""
Voice API endpoints.
"""
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Optional, Dict, Any

from src.speech_to_text.service import SpeechToTextService
from src.text_to_speech.service import TextToSpeechService
from src.nlp_processor.intent_classifier import IntentClassifier
from src.nlp_processor.response_generator import ResponseGenerator

router = APIRouter()


class VoiceQueryRequest(BaseModel):
    """Voice query request."""
    query_text: str  # Transcribed text (from client-side Web Speech API)
    interaction_type: str = "voice"  # 'voice' or 'text'
    language: str = "en-US"
    audio_data: Optional[str] = None  # Base64 encoded audio (optional, for server-side processing)


class VoiceQueryResponse(BaseModel):
    """Voice query response."""
    query_text: str
    intent: str
    confidence_score: float
    entities: Dict[str, Any]
    response_text: str
    response_audio_url: Optional[str] = None
    processing_duration_ms: int


@router.post("/query", response_model=VoiceQueryResponse)
async def process_voice_query(request: VoiceQueryRequest):
    """
    Process voice query and generate response.
    
    Args:
        request: Voice query request with transcribed text
        
    Returns:
        Voice query response with text and audio
    """
    import time
    start_time = time.time()
    
    # Classify intent
    intent_classifier = IntentClassifier()
    intent_result = intent_classifier.classify(request.query_text)
    
    # Generate response
    response_generator = ResponseGenerator()
    response_text = response_generator.generate_response(
        intent=intent_result['intent'],
        entities=intent_result.get('entities', {}),
        data=None  # In production, fetch actual data from backend
    )
    
    # Generate TTS (client-side, but return metadata)
    tts_service = TextToSpeechService()
    tts_result = await tts_service.synthesize(
        text=response_text,
        language=request.language
    )
    
    processing_time = int((time.time() - start_time) * 1000)
    
    return VoiceQueryResponse(
        query_text=request.query_text,
        intent=intent_result['intent'],
        confidence_score=intent_result['confidence'],
        entities=intent_result.get('entities', {}),
        response_text=response_text,
        response_audio_url=tts_result.get('audio_url'),
        processing_duration_ms=processing_time
    )
