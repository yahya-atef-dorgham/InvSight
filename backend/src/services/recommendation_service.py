"""
Recommendation service for managing AI recommendations.
"""
from typing import List, Optional
from uuid import UUID
from decimal import Decimal
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc

from src.models.ai_recommendation import AIRecommendation, RecommendationStatus
from src.models.inventory import Inventory
from src.models.forecast import Forecast
from src.services.ai_service_client import ai_service_client


class RecommendationService:
    """Service for recommendation operations."""
    
    @staticmethod
    async def generate_recommendation(
        db: Session,
        recommendation_type: str,
        product_id: UUID,
        warehouse_id: UUID,
        tenant_id: UUID,
        forecast_id: Optional[UUID] = None
    ) -> AIRecommendation:
        """
        Generate recommendation using AI service.
        
        Args:
            db: Database session
            recommendation_type: Type of recommendation
            product_id: Product ID
            warehouse_id: Warehouse ID
            tenant_id: Tenant ID
            forecast_id: Optional forecast ID to base recommendation on
            
        Returns:
            Created AIRecommendation
        """
        # Get current inventory
        inventory = db.query(Inventory).filter(
            and_(
                Inventory.tenant_id == tenant_id,
                Inventory.product_id == product_id,
                Inventory.warehouse_id == warehouse_id
            )
        ).first()
        
        if not inventory:
            raise ValueError(f"Inventory not found for product {product_id} at warehouse {warehouse_id}")
        
        current_stock = float(inventory.quantity)
        safety_stock = float(inventory.safety_stock) if inventory.safety_stock else None
        minimum_stock = float(inventory.minimum_stock) if inventory.minimum_stock else None
        
        # Get latest forecast if not provided
        if not forecast_id:
            forecast = db.query(Forecast).filter(
                and_(
                    Forecast.tenant_id == tenant_id,
                    Forecast.product_id == product_id,
                    Forecast.warehouse_id == warehouse_id
                )
            ).order_by(desc(Forecast.generated_at)).first()
        else:
            forecast = db.query(Forecast).filter(
                and_(
                    Forecast.id == forecast_id,
                    Forecast.tenant_id == tenant_id
                )
            ).first()
        
        if not forecast:
            raise ValueError("No forecast available. Generate forecast first.")
        
        predicted_demand = float(forecast.predicted_demand)
        
        # Call AI service
        recommendation_result = await ai_service_client.generate_recommendation(
            recommendation_type=recommendation_type,
            product_id=product_id,
            warehouse_id=warehouse_id,
            current_stock=current_stock,
            predicted_demand=predicted_demand,
            lead_time_days=7,  # Default lead time
            safety_stock=safety_stock,
            minimum_stock=minimum_stock
        )
        
        # Create recommendation record
        recommendation = AIRecommendation(
            tenant_id=tenant_id,
            recommendation_type=recommendation_type,
            product_id=product_id,
            warehouse_id=warehouse_id,
            forecast_id=forecast.id,
            recommended_value=Decimal(str(recommendation_result['recommended_value'])),
            current_value=Decimal(str(recommendation_result.get('current_value', current_stock))),
            urgency_score=Decimal(str(recommendation_result['urgency_score'])),
            confidence_score=Decimal(str(recommendation_result['confidence_score'])),
            explanation=recommendation_result['explanation'],
            explanation_json=recommendation_result['explanation_json'],
            status=RecommendationStatus.ACTIVE.value
        )
        
        db.add(recommendation)
        db.commit()
        db.refresh(recommendation)
        
        return recommendation
    
    @staticmethod
    def get_recommendations(
        db: Session,
        tenant_id: UUID,
        product_id: Optional[UUID] = None,
        warehouse_id: Optional[UUID] = None,
        recommendation_type: Optional[str] = None,
        status: Optional[str] = None,
        urgency_min: Optional[float] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[AIRecommendation]:
        """Get recommendations with optional filters."""
        query = db.query(AIRecommendation).filter(AIRecommendation.tenant_id == tenant_id)
        
        if product_id:
            query = query.filter(AIRecommendation.product_id == product_id)
        
        if warehouse_id:
            query = query.filter(AIRecommendation.warehouse_id == warehouse_id)
        
        if recommendation_type:
            query = query.filter(AIRecommendation.recommendation_type == recommendation_type)
        
        if status:
            query = query.filter(AIRecommendation.status == status)
        
        if urgency_min is not None:
            query = query.filter(AIRecommendation.urgency_score >= Decimal(str(urgency_min)))
        
        return query.order_by(desc(AIRecommendation.urgency_score), desc(AIRecommendation.created_at)).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_recommendation_by_id(
        db: Session,
        recommendation_id: UUID,
        tenant_id: UUID
    ) -> Optional[AIRecommendation]:
        """Get a recommendation by ID."""
        return db.query(AIRecommendation).filter(
            and_(
                AIRecommendation.id == recommendation_id,
                AIRecommendation.tenant_id == tenant_id
            )
        ).first()
    
    @staticmethod
    def update_recommendation_status(
        db: Session,
        recommendation_id: UUID,
        status: str,
        tenant_id: UUID,
        user_id: UUID
    ) -> Optional[AIRecommendation]:
        """Update recommendation status."""
        recommendation = RecommendationService.get_recommendation_by_id(
            db, recommendation_id, tenant_id
        )
        
        if not recommendation:
            return None
        
        recommendation.status = status
        recommendation.actioned_at = datetime.now(timezone.utc)
        recommendation.actioned_by = user_id
        
        db.commit()
        db.refresh(recommendation)
        
        return recommendation
