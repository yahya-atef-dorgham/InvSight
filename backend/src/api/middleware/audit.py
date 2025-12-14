"""
Audit logging middleware and decorators.
"""
from functools import wraps
from typing import Callable, Any
from uuid import UUID
from fastapi import Request, Depends
from sqlalchemy.orm import Session

from src.database.session import get_db
from src.api.middleware.auth import get_current_user
from src.services.audit_service import AuditService


def audit_action(action: str, entity_type: str):
    """
    Decorator to automatically audit an action.
    
    Args:
        action: Action name (e.g., 'inventory.movement.create')
        entity_type: Entity type (e.g., 'InventoryMovement')
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Extract dependencies
            request: Request = kwargs.get('request')
            db: Session = kwargs.get('db')
            current_user: dict = kwargs.get('current_user')
            
            if not db or not current_user:
                # If dependencies not available, just call function
                return await func(*args, **kwargs)
            
            # Call the function
            result = await func(*args, **kwargs)
            
            # Get entity_id from result (assuming result has id attribute or is a dict with id)
            entity_id = None
            if hasattr(result, 'id'):
                entity_id = result.id
            elif isinstance(result, dict) and 'id' in result:
                entity_id = UUID(result['id'])
            
            if entity_id:
                # Log the action
                AuditService.log_action(
                    db=db,
                    tenant_id=UUID(current_user['tenant_id']),
                    action=action,
                    entity_type=entity_type,
                    entity_id=entity_id,
                    user_id=UUID(current_user['user_id']) if current_user.get('user_id') else None,
                    ip_address=request.client.host if request and request.client else None,
                    user_agent=request.headers.get('user-agent') if request else None,
                )
            
            return result
        
        return wrapper
    return decorator

