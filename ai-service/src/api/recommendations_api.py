"""
Recommendations API endpoints.
"""
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Optional

from src.services.recommendation_service import RecommendationService

router = APIRouter()


class RecommendationRequest(BaseModel):
    """Recommendation calculation request."""
    recommendation_type: str  # 'reorder_point', 'reorder_quantity', 'purchase_order'
    product_id: str
    warehouse_id: str
    current_stock: float
    predicted_demand: float
    lead_time_days: int = 7
    safety_stock: Optional[float] = None
    minimum_stock: Optional[float] = None


class RecommendationResponse(BaseModel):
    """Recommendation response."""
    recommendation_type: str
    product_id: str
    warehouse_id: str
    recommended_value: float
    current_value: float
    urgency_score: float
    confidence_score: float
    explanation: str
    explanation_json: dict


@router.post("", response_model=RecommendationResponse)
async def generate_recommendation(request: RecommendationRequest):
    """
    Generate inventory recommendation.
    
    Args:
        request: Recommendation request with current stock and forecast data
        
    Returns:
        Recommendation response with suggested action
    """
    if request.recommendation_type not in ['reorder_point', 'reorder_quantity', 'purchase_order']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="recommendation_type must be 'reorder_point', 'reorder_quantity', or 'purchase_order'"
        )
    
    try:
        service = RecommendationService()
        
        if request.recommendation_type == 'reorder_quantity':
            if request.minimum_stock is None:
                request.minimum_stock = request.current_stock * 0.5  # Default to 50% of current
            
            if request.safety_stock is None:
                request.safety_stock = request.minimum_stock * 0.3  # Default to 30% of minimum
            
            result = service.calculate_reorder_quantity(
                current_stock=request.current_stock,
                predicted_demand=request.predicted_demand,
                lead_time_days=request.lead_time_days,
                safety_stock=request.safety_stock,
                minimum_stock=request.minimum_stock
            )
        elif request.recommendation_type == 'reorder_point':
            if request.safety_stock is None:
                request.safety_stock = request.current_stock * 0.2  # Default
            
            result = service.calculate_reorder_point(
                predicted_demand=request.predicted_demand,
                lead_time_days=request.lead_time_days,
                safety_stock=request.safety_stock
            )
        else:  # purchase_order
            # For purchase orders, use reorder quantity logic
            if request.minimum_stock is None:
                request.minimum_stock = request.current_stock * 0.5
            
            if request.safety_stock is None:
                request.safety_stock = request.minimum_stock * 0.3
            
            result = service.calculate_reorder_quantity(
                current_stock=request.current_stock,
                predicted_demand=request.predicted_demand,
                lead_time_days=request.lead_time_days,
                safety_stock=request.safety_stock,
                minimum_stock=request.minimum_stock
            )
        
        return RecommendationResponse(
            recommendation_type=request.recommendation_type,
            product_id=request.product_id,
            warehouse_id=request.warehouse_id,
            recommended_value=result['recommended_value'],
            current_value=result.get('current_stock', request.current_stock),
            urgency_score=result['urgency_score'],
            confidence_score=result['confidence_score'],
            explanation=result['explanation'],
            explanation_json=result['explanation_json']
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Recommendation generation failed: {str(e)}"
        )
