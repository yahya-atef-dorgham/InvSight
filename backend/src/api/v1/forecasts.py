"""
Forecasts API endpoints.
"""
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel

from src.database.session import get_db
from src.api.middleware.tenant import get_tenant_id
from src.services.forecast_service import ForecastService
from src.models.forecast import Forecast

router = APIRouter(prefix="/forecast", tags=["forecasts"])


class ForecastResponse(BaseModel):
    """Forecast response model."""
    id: str
    tenant_id: str
    product_id: str
    warehouse_id: str
    forecast_horizon_days: int
    forecast_date: str
    predicted_demand: float
    confidence_lower: float | None
    confidence_upper: float | None
    confidence_level: float | None
    model_version: str
    model_type: str | None
    generated_at: str
    
    class Config:
        from_attributes = True


class ForecastCreate(BaseModel):
    """Forecast creation model."""
    product_id: str
    warehouse_id: str
    forecast_horizon_days: int  # 7, 30, or 90
    model_type: str = "exponential_smoothing"


@router.get("", response_model=List[ForecastResponse])
async def list_forecasts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    product_id: Optional[UUID] = Query(None),
    warehouse_id: Optional[UUID] = Query(None),
    forecast_horizon_days: Optional[int] = Query(None),
    tenant_id: UUID = Depends(get_tenant_id),
    db: Session = Depends(get_db)
):
    """Get list of forecasts."""
    forecasts = ForecastService.get_forecasts(
        db=db,
        tenant_id=tenant_id,
        product_id=product_id,
        warehouse_id=warehouse_id,
        forecast_horizon_days=forecast_horizon_days,
        skip=skip,
        limit=limit
    )
    return forecasts


@router.post("", response_model=ForecastResponse, status_code=status.HTTP_201_CREATED)
async def create_forecast(
    forecast_data: ForecastCreate,
    tenant_id: UUID = Depends(get_tenant_id),
    db: Session = Depends(get_db)
):
    """Generate a new forecast using AI service."""
    if forecast_data.forecast_horizon_days not in [7, 30, 90]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="forecast_horizon_days must be 7, 30, or 90"
        )
    
    try:
        forecast = await ForecastService.generate_forecast(
            db=db,
            product_id=UUID(forecast_data.product_id),
            warehouse_id=UUID(forecast_data.warehouse_id),
            forecast_horizon_days=forecast_data.forecast_horizon_days,
            tenant_id=tenant_id,
            model_type=forecast_data.model_type
        )
        return forecast
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Forecast generation failed: {str(e)}"
        )
