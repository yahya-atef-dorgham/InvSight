"""
Recommendations API endpoints.
"""
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel

from src.database.session import get_db
from src.api.middleware.tenant import get_tenant_id, get_user_id
from src.services.recommendation_service import RecommendationService
from src.models.ai_recommendation import AIRecommendation

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


class RecommendationResponse(BaseModel):
    """Recommendation response model."""
    id: str
    tenant_id: str
    recommendation_type: str
    product_id: str
    warehouse_id: str
    forecast_id: str | None
    recommended_value: float | None
    current_value: float | None
    urgency_score: float | None
    confidence_score: float | None
    explanation: str | None
    explanation_json: dict | None
    status: str
    created_at: str
    actioned_at: str | None
    actioned_by: str | None
    
    class Config:
        from_attributes = True


class RecommendationCreate(BaseModel):
    """Recommendation creation model."""
    recommendation_type: str  # 'reorder_point', 'reorder_quantity', 'purchase_order'
    product_id: str
    warehouse_id: str
    forecast_id: str | None = None


class RecommendationStatusUpdate(BaseModel):
    """Recommendation status update model."""
    status: str  # 'approved', 'rejected', 'superseded'


@router.get("", response_model=List[RecommendationResponse])
async def list_recommendations(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    product_id: Optional[UUID] = Query(None),
    warehouse_id: Optional[UUID] = Query(None),
    recommendation_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    urgency_min: Optional[float] = Query(None),
    tenant_id: UUID = Depends(get_tenant_id),
    db: Session = Depends(get_db)
):
    """Get list of recommendations with optional filters."""
    recommendations = RecommendationService.get_recommendations(
        db=db,
        tenant_id=tenant_id,
        product_id=product_id,
        warehouse_id=warehouse_id,
        recommendation_type=recommendation_type,
        status=status,
        urgency_min=urgency_min,
        skip=skip,
        limit=limit
    )
    return recommendations


@router.get("/{recommendation_id}", response_model=RecommendationResponse)
async def get_recommendation(
    recommendation_id: UUID,
    tenant_id: UUID = Depends(get_tenant_id),
    db: Session = Depends(get_db)
):
    """Get a recommendation by ID."""
    recommendation = RecommendationService.get_recommendation_by_id(
        db, recommendation_id, tenant_id
    )
    
    if not recommendation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recommendation not found"
        )
    
    return recommendation


@router.get("/{recommendation_id}/explanation", response_model=dict)
async def get_recommendation_explanation(
    recommendation_id: UUID,
    tenant_id: UUID = Depends(get_tenant_id),
    db: Session = Depends(get_db)
):
    """Get detailed explanation for a recommendation."""
    recommendation = RecommendationService.get_recommendation_by_id(
        db, recommendation_id, tenant_id
    )
    
    if not recommendation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recommendation not found"
        )
    
    return {
        "explanation": recommendation.explanation,
        "explanation_json": recommendation.explanation_json,
        "urgency_score": float(recommendation.urgency_score) if recommendation.urgency_score else None,
        "confidence_score": float(recommendation.confidence_score) if recommendation.confidence_score else None,
        "recommended_value": float(recommendation.recommended_value) if recommendation.recommended_value else None,
        "current_value": float(recommendation.current_value) if recommendation.current_value else None
    }


@router.post("", response_model=RecommendationResponse, status_code=status.HTTP_201_CREATED)
async def create_recommendation(
    recommendation_data: RecommendationCreate,
    tenant_id: UUID = Depends(get_tenant_id),
    db: Session = Depends(get_db)
):
    """Generate a new recommendation using AI service."""
    if recommendation_data.recommendation_type not in ['reorder_point', 'reorder_quantity', 'purchase_order']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="recommendation_type must be 'reorder_point', 'reorder_quantity', or 'purchase_order'"
        )
    
    try:
        forecast_id = UUID(recommendation_data.forecast_id) if recommendation_data.forecast_id else None
        
        recommendation = await RecommendationService.generate_recommendation(
            db=db,
            recommendation_type=recommendation_data.recommendation_type,
            product_id=UUID(recommendation_data.product_id),
            warehouse_id=UUID(recommendation_data.warehouse_id),
            tenant_id=tenant_id,
            forecast_id=forecast_id
        )
        return recommendation
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Recommendation generation failed: {str(e)}"
        )


@router.put("/{recommendation_id}/status", response_model=RecommendationResponse)
async def update_recommendation_status(
    recommendation_id: UUID,
    status_data: RecommendationStatusUpdate,
    tenant_id: UUID = Depends(get_tenant_id),
    user_id: UUID = Depends(get_user_id),
    db: Session = Depends(get_db)
):
    """Update recommendation status."""
    if status_data.status not in ['approved', 'rejected', 'superseded']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="status must be 'approved', 'rejected', or 'superseded'"
        )
    
    recommendation = RecommendationService.update_recommendation_status(
        db=db,
        recommendation_id=recommendation_id,
        status=status_data.status,
        tenant_id=tenant_id,
        user_id=user_id
    )
    
    if not recommendation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recommendation not found"
        )
    
    return recommendation
