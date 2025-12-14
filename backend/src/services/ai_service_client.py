"""
AI Service API client for communicating with the AI service.
"""
import httpx
from typing import Dict, Any, List, Optional
from uuid import UUID

from src.config.settings import settings


class AIServiceClient:
    """Client for communicating with the AI service."""
    
    def __init__(self, base_url: Optional[str] = None):
        """
        Initialize AI service client.
        
        Args:
            base_url: Base URL of AI service (defaults to settings)
        """
        self.base_url = base_url or settings.ai_service_url or "http://localhost:8001"
        self.timeout = 30.0
    
    async def generate_forecast(
        self,
        product_id: UUID,
        warehouse_id: UUID,
        historical_data: List[Dict[str, Any]],
        forecast_horizon_days: int,
        model_type: str = "exponential_smoothing"
    ) -> Dict[str, Any]:
        """
        Generate demand forecast.
        
        Args:
            product_id: Product ID
            warehouse_id: Warehouse ID
            historical_data: Historical inventory data
            forecast_horizon_days: Forecast horizon (7, 30, or 90)
            model_type: Model type to use
            
        Returns:
            Forecast result dictionary
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/forecast",
                json={
                    "product_id": str(product_id),
                    "warehouse_id": str(warehouse_id),
                    "historical_data": historical_data,
                    "forecast_horizon_days": forecast_horizon_days,
                    "model_type": model_type
                }
            )
            response.raise_for_status()
            return response.json()
    
    async def generate_recommendation(
        self,
        recommendation_type: str,
        product_id: UUID,
        warehouse_id: UUID,
        current_stock: float,
        predicted_demand: float,
        lead_time_days: int = 7,
        safety_stock: Optional[float] = None,
        minimum_stock: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Generate inventory recommendation.
        
        Args:
            recommendation_type: Type of recommendation
            product_id: Product ID
            warehouse_id: Warehouse ID
            current_stock: Current stock level
            predicted_demand: Predicted demand
            lead_time_days: Supplier lead time
            safety_stock: Safety stock level
            minimum_stock: Minimum stock threshold
            
        Returns:
            Recommendation result dictionary
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            payload = {
                "recommendation_type": recommendation_type,
                "product_id": str(product_id),
                "warehouse_id": str(warehouse_id),
                "current_stock": current_stock,
                "predicted_demand": predicted_demand,
                "lead_time_days": lead_time_days
            }
            
            if safety_stock is not None:
                payload["safety_stock"] = safety_stock
            if minimum_stock is not None:
                payload["minimum_stock"] = minimum_stock
            
            response = await client.post(
                f"{self.base_url}/recommendations",
                json=payload
            )
            response.raise_for_status()
            return response.json()


# Global client instance
ai_service_client = AIServiceClient()
