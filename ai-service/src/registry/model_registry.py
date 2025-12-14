"""
Model registry for versioning and tracking AI models.
"""
from typing import Dict, Any, Optional
from datetime import datetime


class ModelRegistry:
    """Registry for managing AI model versions."""
    
    def __init__(self):
        self.models: Dict[str, Dict[str, Any]] = {}
    
    def register_model(
        self,
        model_name: str,
        model_type: str,
        version: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Register a new model version.
        
        Args:
            model_name: Name of the model
            model_type: Type of model (e.g., 'forecast', 'recommendation')
            version: Version string (e.g., '1.0.0')
            metadata: Additional metadata
            
        Returns:
            Model ID
        """
        model_id = f"{model_name}_{version}"
        
        self.models[model_id] = {
            'model_name': model_name,
            'model_type': model_type,
            'version': version,
            'registered_at': datetime.utcnow().isoformat(),
            'metadata': metadata or {},
            'is_active': True
        }
        
        return model_id
    
    def get_model(self, model_id: str) -> Optional[Dict[str, Any]]:
        """Get model information by ID."""
        return self.models.get(model_id)
    
    def list_models(self, model_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all registered models, optionally filtered by type."""
        models = list(self.models.values())
        
        if model_type:
            models = [m for m in models if m['model_type'] == model_type]
        
        return models
    
    def deactivate_model(self, model_id: str) -> bool:
        """Deactivate a model version."""
        if model_id in self.models:
            self.models[model_id]['is_active'] = False
            return True
        return False


# Global registry instance
registry = ModelRegistry()

# Register default models
registry.register_model('forecast_exponential_smoothing', 'forecast', '1.0.0')
registry.register_model('recommendation_reorder', 'recommendation', '1.0.0')
