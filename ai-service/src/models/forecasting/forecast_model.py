"""
Time-series forecasting model for demand prediction.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import statistics
import math


class ForecastModel:
    """Forecasting model using exponential smoothing (simple implementation)."""
    
    def __init__(self, model_type: str = "exponential_smoothing"):
        """
        Initialize forecast model.
        
        Args:
            model_type: Type of model ('exponential_smoothing', 'arima', 'lstm')
        """
        self.model_type = model_type
        self.model_version = "1.0.0"
    
    def forecast(
        self,
        historical_data: List[Dict[str, Any]],
        horizon_days: int,
        alpha: float = 0.3
    ) -> Dict[str, Any]:
        """
        Generate forecast using exponential smoothing.
        
        Args:
            historical_data: List of {date, quantity} records
            horizon_days: Forecast horizon (7, 30, or 90 days)
            alpha: Smoothing parameter (0-1)
            
        Returns:
            Dictionary with forecast results
        """
        if not historical_data:
            raise ValueError("Historical data is required")
        
        # Extract quantities from historical data
        quantities = [float(item.get('quantity', 0)) for item in historical_data]
        
        if len(quantities) < 2:
            # Simple average if insufficient data
            avg_demand = statistics.mean(quantities) if quantities else 0
            predicted = avg_demand * (horizon_days / 7)  # Scale to horizon
        else:
            # Exponential smoothing
            predicted = self._exponential_smoothing(quantities, alpha, horizon_days)
        
        # Calculate confidence interval (simplified)
        std_dev = statistics.stdev(quantities) if len(quantities) > 1 else predicted * 0.2
        confidence_level = 0.80
        z_score = 1.28  # For 80% confidence
        
        confidence_lower = max(0, predicted - z_score * std_dev)
        confidence_upper = predicted + z_score * std_dev
        
        # Extract features for explainability
        features = {
            'historical_mean': statistics.mean(quantities) if quantities else 0,
            'historical_std': std_dev,
            'data_points': len(quantities),
            'trend': self._calculate_trend(quantities),
            'seasonality_factor': 1.0  # Simplified
        }
        
        return {
            'predicted_demand': round(predicted, 3),
            'confidence_lower': round(confidence_lower, 3),
            'confidence_upper': round(confidence_upper, 3),
            'confidence_level': confidence_level,
            'model_version': self.model_version,
            'features': features
        }
    
    def _exponential_smoothing(self, data: List[float], alpha: float, horizon: int) -> float:
        """Apply exponential smoothing to predict future demand."""
        if not data:
            return 0.0
        
        # Simple exponential smoothing
        forecast = data[0]
        for value in data[1:]:
            forecast = alpha * value + (1 - alpha) * forecast
        
        # Project forward for horizon
        # Assume daily demand, scale to horizon
        daily_demand = forecast
        return daily_demand * horizon
    
    def _calculate_trend(self, data: List[float]) -> float:
        """Calculate trend in historical data."""
        if len(data) < 2:
            return 0.0
        
        # Simple linear trend
        n = len(data)
        x_mean = (n - 1) / 2
        y_mean = statistics.mean(data)
        
        numerator = sum((i - x_mean) * (data[i] - y_mean) for i in range(n))
        denominator = sum((i - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            return 0.0
        
        trend = numerator / denominator
        return round(trend, 3)
