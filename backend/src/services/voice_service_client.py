"""
Voice Service API client for communicating with the voice service.
"""
import httpx
from typing import Dict, Any, Optional

from src.config.settings import settings


class VoiceServiceClient:
    """Client for communicating with the voice service."""
    
    def __init__(self, base_url: Optional[str] = None):
        """
        Initialize voice service client.
        
        Args:
            base_url: Base URL of voice service (defaults to settings)
        """
        self.base_url = base_url or settings.voice_service_url or "http://localhost:8002"
        self.timeout = 10.0
    
    async def process_query(
        self,
        query_text: str,
        interaction_type: str = "voice",
        language: str = "en-US"
    ) -> Dict[str, Any]:
        """
        Process voice query.
        
        Args:
            query_text: Transcribed query text
            interaction_type: Type of interaction ('voice' or 'text')
            language: Language code
            
        Returns:
            Query processing result
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/voice/query",
                json={
                    "query_text": query_text,
                    "interaction_type": interaction_type,
                    "language": language
                }
            )
            response.raise_for_status()
            return response.json()


# Global client instance
voice_service_client = VoiceServiceClient()
