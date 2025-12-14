"""
Forecast service for managing forecasts and integrating with AI service.
"""
from typing import List, Optional, Dict
from uuid import UUID
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, or_

from src.models.forecast import Forecast
from src.models.inventory import Inventory
from src.models.inventory_movement import InventoryMovement
from src.services.ai_service_client import ai_service_client


class ForecastService:
    """Service for forecast operations."""
    
    @staticmethod
    async def generate_forecast(
        db: Session,
        product_id: UUID,
        warehouse_id: UUID,
        forecast_horizon_days: int,
        tenant_id: UUID,
        model_type: str = "exponential_smoothing"
    ) -> Forecast:
        """
        Generate forecast using AI service.
        
        Args:
            db: Database session
            product_id: Product ID
            warehouse_id: Warehouse ID
            forecast_horizon_days: Forecast horizon (7, 30, or 90)
            tenant_id: Tenant ID
            model_type: Model type to use
            
        Returns:
            Created Forecast
        """
        # Get historical inventory movement data
        historical_data = ForecastService._get_historical_data(
            db, product_id, warehouse_id, tenant_id, days=90
        )
        
        if len(historical_data) < 10:
            raise ValueError("Insufficient historical data. Need at least 10 data points.")
        
        # Call AI service
        forecast_result = await ai_service_client.generate_forecast(
            product_id=product_id,
            warehouse_id=warehouse_id,
            historical_data=historical_data,
            forecast_horizon_days=forecast_horizon_days,
            model_type=model_type
        )
        
        # Create forecast record
        forecast = Forecast(
            tenant_id=tenant_id,
            product_id=product_id,
            warehouse_id=warehouse_id,
            forecast_horizon_days=forecast_horizon_days,
            forecast_date=date.today(),
            predicted_demand=Decimal(str(forecast_result['predicted_demand'])),
            confidence_lower=Decimal(str(forecast_result['confidence_lower'])) if forecast_result.get('confidence_lower') else None,
            confidence_upper=Decimal(str(forecast_result['confidence_upper'])) if forecast_result.get('confidence_upper') else None,
            confidence_level=Decimal(str(forecast_result.get('confidence_level', 0.80))),
            model_version=forecast_result['model_version'],
            model_type=model_type,
            features_json=forecast_result.get('features')
        )
        
        db.add(forecast)
        db.commit()
        db.refresh(forecast)
        
        return forecast
    
    @staticmethod
    def _get_historical_data(
        db: Session,
        product_id: UUID,
        warehouse_id: UUID,
        tenant_id: UUID,
        days: int = 90
    ) -> List[dict]:
        """Get historical inventory data for forecasting."""
        # Get inventory movements for the last N days
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        
        movements = db.query(InventoryMovement).filter(
            and_(
                InventoryMovement.tenant_id == tenant_id,
                InventoryMovement.product_id == product_id,
                InventoryMovement.performed_at >= cutoff_date
            )
        ).filter(
            or_(
                InventoryMovement.destination_warehouse_id == warehouse_id,
                InventoryMovement.source_warehouse_id == warehouse_id
            )
        ).order_by(InventoryMovement.performed_at).all()
        
        # Get current inventory
        inventory = db.query(Inventory).filter(
            and_(
                Inventory.tenant_id == tenant_id,
                Inventory.product_id == product_id,
                Inventory.warehouse_id == warehouse_id
            )
        ).first()
        
        # Build historical data points
        # For simplicity, aggregate by day
        daily_data: Dict[date, float] = {}
        current_quantity = float(inventory.quantity) if inventory else 0.0
        
        # Work backwards from today
        for i in range(days):
            day = date.today() - timedelta(days=i)
            daily_data[day] = 0.0
        
        # Process movements to calculate daily quantities
        for movement in movements:
            movement_date = movement.performed_at.date()
            if movement.destination_warehouse_id == warehouse_id:
                # Inbound or transfer in
                daily_data[movement_date] = daily_data.get(movement_date, 0) + float(movement.quantity)
            elif movement.source_warehouse_id == warehouse_id:
                # Outbound or transfer out
                daily_data[movement_date] = daily_data.get(movement_date, 0) - float(movement.quantity)
        
        # Convert to list format
        historical_data = [
            {
                "date": day.isoformat(),
                "quantity": current_quantity + daily_data.get(day, 0)
            }
            for day in sorted(daily_data.keys())
        ]
        
        return historical_data
    
    @staticmethod
    def get_forecasts(
        db: Session,
        tenant_id: UUID,
        product_id: Optional[UUID] = None,
        warehouse_id: Optional[UUID] = None,
        forecast_horizon_days: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Forecast]:
        """Get forecasts with optional filters."""
        query = db.query(Forecast).filter(Forecast.tenant_id == tenant_id)
        
        if product_id:
            query = query.filter(Forecast.product_id == product_id)
        
        if warehouse_id:
            query = query.filter(Forecast.warehouse_id == warehouse_id)
        
        if forecast_horizon_days:
            query = query.filter(Forecast.forecast_horizon_days == forecast_horizon_days)
        
        return query.order_by(desc(Forecast.generated_at)).offset(skip).limit(limit).all()
