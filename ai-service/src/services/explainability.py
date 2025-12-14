"""
Explainability module for AI model predictions.
"""
from typing import Dict, Any, List


class ExplainabilityService:
    """Service for generating explanations of AI predictions."""
    
    @staticmethod
    def explain_forecast(
        predicted_demand: float,
        historical_data: List[Dict[str, Any]],
        model_type: str,
        features: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate explanation for forecast prediction.
        
        Args:
            predicted_demand: Predicted demand value
            historical_data: Historical data used for prediction
            model_type: Type of model used
            features: Model features
            
        Returns:
            Explanation dictionary
        """
        historical_mean = features.get('historical_mean', 0)
        trend = features.get('trend', 0)
        
        explanation = f"Forecast of {predicted_demand:.1f} units based on {len(historical_data)} historical data points. "
        
        if trend > 0:
            explanation += f"Trend shows increasing demand (+{trend:.2f} units/day). "
        elif trend < 0:
            explanation += f"Trend shows decreasing demand ({trend:.2f} units/day). "
        else:
            explanation += "Demand appears stable. "
        
        if predicted_demand > historical_mean * 1.2:
            explanation += "Predicted demand is significantly higher than historical average."
        elif predicted_demand < historical_mean * 0.8:
            explanation += "Predicted demand is lower than historical average."
        else:
            explanation += "Predicted demand aligns with historical patterns."
        
        return {
            'explanation': explanation,
            'key_factors': {
                'historical_mean': historical_mean,
                'trend': trend,
                'data_points': len(historical_data),
                'model_type': model_type
            },
            'confidence_factors': {
                'data_quality': 'high' if len(historical_data) > 30 else 'medium',
                'trend_consistency': 'high' if abs(trend) < historical_mean * 0.1 else 'medium'
            }
        }
    
    @staticmethod
    def explain_recommendation(
        recommendation_type: str,
        recommended_value: float,
        current_value: float,
        urgency_score: float,
        factors: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate explanation for recommendation.
        
        Args:
            recommendation_type: Type of recommendation
            recommended_value: Recommended value
            current_value: Current value
            urgency_score: Urgency score (0-100)
            factors: Calculation factors
            
        Returns:
            Explanation dictionary
        """
        explanation = f"Recommend {recommendation_type.replace('_', ' ')} of {recommended_value:.1f} units. "
        
        if urgency_score >= 75:
            explanation += "URGENT: Immediate action required to prevent stockout. "
        elif urgency_score >= 50:
            explanation += "Action recommended soon to maintain optimal stock levels. "
        else:
            explanation += "Preventive recommendation to optimize inventory. "
        
        if recommended_value > current_value:
            explanation += f"Current stock ({current_value:.1f}) is below recommended level."
        else:
            explanation += f"Current stock ({current_value:.1f}) meets or exceeds recommendation."
        
        return {
            'explanation': explanation,
            'urgency_level': 'high' if urgency_score >= 75 else 'medium' if urgency_score >= 50 else 'low',
            'calculation_factors': factors
        }
