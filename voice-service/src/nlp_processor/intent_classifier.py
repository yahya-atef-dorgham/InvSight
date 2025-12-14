"""
NLP intent classifier for inventory domain.
"""
from typing import Dict, Any, List
import re


class IntentClassifier:
    """Classifies user intents from natural language queries."""
    
    # Intent patterns
    INTENT_PATTERNS = {
        'stock_query': [
            r'how much.*stock',
            r'what.*quantity',
            r'check.*inventory',
            r'stock level',
            r'available.*quantity'
        ],
        'low_stock_alert': [
            r'low stock',
            r'running low',
            r'need.*reorder',
            r'out of stock'
        ],
        'forecast_query': [
            r'forecast',
            r'prediction',
            r'future demand',
            r'expected.*demand'
        ],
        'po_creation': [
            r'create.*purchase order',
            r'order.*from.*supplier',
            r'generate.*po',
            r'place.*order'
        ],
        'movement_query': [
            r'movement',
            r'transfer',
            r'shipment',
            r'received'
        ],
        'product_search': [
            r'find.*product',
            r'search.*product',
            r'where.*product',
            r'product.*location'
        ]
    }
    
    def classify(self, query_text: str) -> Dict[str, Any]:
        """
        Classify intent from query text.
        
        Args:
            query_text: User query text
            
        Returns:
            Dictionary with intent, confidence, and entities
        """
        query_lower = query_text.lower()
        
        # Score each intent
        intent_scores = {}
        for intent, patterns in self.INTENT_PATTERNS.items():
            score = 0
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    score += 1
            intent_scores[intent] = score
        
        # Get best intent
        best_intent = max(intent_scores.items(), key=lambda x: x[1]) if intent_scores else ('unknown', 0)
        intent_name = best_intent[0] if best_intent[1] > 0 else 'unknown'
        confidence = min(95, 50 + (best_intent[1] * 15))  # Scale to 0-100
        
        # Extract entities (simplified)
        entities = self._extract_entities(query_text)
        
        return {
            'intent': intent_name,
            'confidence': round(confidence, 2),
            'entities': entities,
            'query_text': query_text
        }
    
    def _extract_entities(self, query_text: str) -> Dict[str, Any]:
        """Extract entities from query (product names, quantities, etc.)."""
        entities = {
            'products': [],
            'warehouses': [],
            'quantities': [],
            'dates': []
        }
        
        # Simple entity extraction (in production, use NER model)
        # Extract numbers (potential quantities)
        numbers = re.findall(r'\d+', query_text)
        entities['quantities'] = [int(n) for n in numbers[:3]]  # Limit to 3
        
        return entities
