"""
Response generator for voice queries.
"""
from typing import Dict, Any


class ResponseGenerator:
    """Generates natural language responses to queries."""
    
    def generate_response(
        self,
        intent: str,
        entities: Dict[str, Any],
        data: Any = None
    ) -> str:
        """
        Generate response text based on intent and data.
        
        Args:
            intent: Detected intent
            entities: Extracted entities
            data: Response data (from backend API)
            
        Returns:
            Natural language response text
        """
        if intent == 'stock_query':
            if data and 'quantity' in data:
                return f"The current stock level is {data['quantity']} {data.get('unit', 'units')}."
            return "I can help you check stock levels. Please specify which product you're interested in."
        
        elif intent == 'low_stock_alert':
            if data and isinstance(data, list) and len(data) > 0:
                count = len(data)
                return f"There are {count} items with low stock levels that need attention."
            return "I can check for low stock alerts. Let me query the inventory system."
        
        elif intent == 'forecast_query':
            if data and 'predicted_demand' in data:
                return f"The predicted demand is {data['predicted_demand']} units over the forecast period."
            return "I can provide demand forecasts. Please specify the product and time horizon."
        
        elif intent == 'po_creation':
            return "I can help you create a purchase order. Please provide the supplier and items."
        
        elif intent == 'movement_query':
            return "I can help you with inventory movements. What type of movement do you need?"
        
        elif intent == 'product_search':
            if data and isinstance(data, list):
                return f"I found {len(data)} products matching your search."
            return "I can search for products. What product are you looking for?"
        
        else:
            return "I'm here to help with inventory management. You can ask about stock levels, forecasts, purchase orders, or movements."
