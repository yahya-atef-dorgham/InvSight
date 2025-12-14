"""
Forecast API endpoints.
"""
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from datetime import date

from src.models.forecasting.forecast_model import ForecastModel

router = APIRouter()


class ForecastRequest(BaseModel):
    """Forecast generation request."""
    product_id: str
    warehouse_id: str
    historical_data: List[dict]  # List of {date, quantity} records
    forecast_horizon_days: int  # 7, 30, or 90
    model_type: Optional[str] = "exponential_smoothing"  # 'arima', 'exponential_smoothing', 'lstm'


class ForecastResponse(BaseModel):
    """Forecast response."""
    product_id: str
    warehouse_id: str
    forecast_horizon_days: int
    forecast_date: str
    predicted_demand: float
    confidence_lower: Optional[float] = None
    confidence_upper: Optional[float] = None
    confidence_level: Optional[float] = 0.80
    model_version: str
    model_type: str
    features_json: Optional[dict] = None


@router.post("", response_model=ForecastResponse)
async def generate_forecast(request: ForecastRequest):
    """
    Generate demand forecast for a product at a warehouse.
    
    Args:
        request: Forecast request with historical data
        
    Returns:
        Forecast response with predicted demand
    """
    if request.forecast_horizon_days not in [7, 30, 90]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="forecast_horizon_days must be 7, 30, or 90"
        )
    
    if not request.historical_data or len(request.historical_data) < 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least 10 historical data points are required"
        )
    
    try:
        # Initialize forecast model
        model = ForecastModel(model_type=request.model_type)
        
        # Generate forecast
        forecast_result = model.forecast(
            historical_data=request.historical_data,
            horizon_days=request.forecast_horizon_days
        )
        
        return ForecastResponse(
            product_id=request.product_id,
            warehouse_id=request.warehouse_id,
            forecast_horizon_days=request.forecast_horizon_days,
            forecast_date=date.today().isoformat(),
            predicted_demand=forecast_result['predicted_demand'],
            confidence_lower=forecast_result.get('confidence_lower'),
            confidence_upper=forecast_result.get('confidence_upper'),
            confidence_level=forecast_result.get('confidence_level', 0.80),
            model_version=forecast_result['model_version'],
            model_type=request.model_type,
            features_json=forecast_result.get('features')
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Forecast generation failed: {str(e)}"
        )
