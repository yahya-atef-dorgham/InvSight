"""
Recommendation calculation service.
"""
from typing import Dict, Any, List
from decimal import Decimal


class RecommendationService:
    """Service for calculating inventory recommendations."""
    
    @staticmethod
    def calculate_reorder_quantity(
        current_stock: float,
        predicted_demand: float,
        lead_time_days: int,
        safety_stock: float,
        minimum_stock: float
    ) -> Dict[str, Any]:
        """
        Calculate recommended reorder quantity.
        
        Args:
            current_stock: Current inventory level
            predicted_demand: Predicted demand over lead time
            lead_time_days: Supplier lead time in days
            safety_stock: Safety stock level
            minimum_stock: Minimum stock threshold
            
        Returns:
            Dictionary with recommendation details
        """
        # Calculate demand during lead time
        daily_demand = predicted_demand / 30  # Assume monthly forecast
        lead_time_demand = daily_demand * lead_time_days
        
        # Calculate reorder point
        reorder_point = lead_time_demand + safety_stock
        
        # Calculate reorder quantity
        # Order enough to reach reorder point + buffer
        target_stock = reorder_point + (lead_time_demand * 0.5)  # 50% buffer
        reorder_quantity = max(0, target_stock - current_stock)
        
        # Calculate urgency (0-100)
        stock_ratio = current_stock / minimum_stock if minimum_stock > 0 else 1.0
        if stock_ratio < 0.5:
            urgency = 100
        elif stock_ratio < 0.8:
            urgency = 75
        elif stock_ratio < 1.0:
            urgency = 50
        else:
            urgency = 25
        
        # Calculate confidence based on data quality
        confidence = min(95, 70 + (min(100, predicted_demand) / 10))
        
        return {
            'recommended_value': round(reorder_quantity, 3),
            'reorder_point': round(reorder_point, 3),
            'current_stock': current_stock,
            'urgency_score': round(urgency, 2),
            'confidence_score': round(confidence, 2),
            'explanation': (
                f"Based on predicted demand of {predicted_demand:.1f} units/month and "
                f"lead time of {lead_time_days} days, recommend ordering {reorder_quantity:.1f} units "
                f"to maintain optimal stock levels."
            ),
            'explanation_json': {
                'predicted_demand': predicted_demand,
                'lead_time_days': lead_time_days,
                'current_stock': current_stock,
                'safety_stock': safety_stock,
                'calculation_method': 'reorder_point_with_buffer'
            }
        }
    
    @staticmethod
    def calculate_reorder_point(
        predicted_demand: float,
        lead_time_days: int,
        safety_stock: float
    ) -> Dict[str, Any]:
        """
        Calculate recommended reorder point.
        
        Args:
            predicted_demand: Predicted demand over period
            lead_time_days: Supplier lead time
            safety_stock: Safety stock level
            
        Returns:
            Dictionary with recommendation details
        """
        daily_demand = predicted_demand / 30
        lead_time_demand = daily_demand * lead_time_days
        reorder_point = lead_time_demand + safety_stock
        
        return {
            'recommended_value': round(reorder_point, 3),
            'urgency_score': 50.0,
            'confidence_score': 80.0,
            'explanation': (
                f"Recommended reorder point of {reorder_point:.1f} units based on "
                f"{lead_time_days}-day lead time and predicted demand."
            ),
            'explanation_json': {
                'predicted_demand': predicted_demand,
                'lead_time_days': lead_time_days,
                'safety_stock': safety_stock,
                'calculation_method': 'lead_time_demand_plus_safety_stock'
            }
        }
