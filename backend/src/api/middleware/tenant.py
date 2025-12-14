"""
Tenant resolution middleware and dependencies.
"""
from uuid import UUID
from fastapi import Depends, HTTPException, status
from src.api.middleware.auth import get_current_user


def get_tenant_id(current_user: dict = Depends(get_current_user)) -> UUID:
    """
    Dependency to extract tenant_id from authenticated user.
    
    Args:
        current_user: Current authenticated user (from get_current_user dependency)
        
    Returns:
        Tenant UUID
        
    Raises:
        HTTPException: If tenant_id is missing
    """
    tenant_id_str = current_user.get("tenant_id")
    
    if tenant_id_str is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tenant context required"
        )
    
    try:
        return UUID(tenant_id_str)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid tenant_id format"
        )


def get_user_id(current_user: dict = Depends(get_current_user)) -> UUID:
    """
    Dependency to extract user_id from authenticated user.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User UUID
    """
    user_id_str = current_user.get("user_id")
    
    if user_id_str is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User context required"
        )
    
    try:
        return UUID(user_id_str)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user_id format"
        )

