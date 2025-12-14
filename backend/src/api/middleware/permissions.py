"""
Role-Based Access Control (RBAC) permission checking.
"""
from typing import List
from fastapi import Depends, HTTPException, status
from src.api.middleware.auth import get_current_user


# Role definitions
ROLE_ADMIN = "admin"
ROLE_INVENTORY_MANAGER = "inventory_manager"
ROLE_WAREHOUSE_STAFF = "warehouse_staff"
ROLE_ANALYST = "analyst"

# Permission mappings
PERMISSIONS = {
    ROLE_ADMIN: ["*"],  # All permissions
    ROLE_INVENTORY_MANAGER: [
        "inventory:read",
        "inventory:write",
        "purchase_order:approve",
        "purchase_order:read",
        "purchase_order:write",
        "product:read",
        "product:write",
        "warehouse:read",
        "warehouse:write",
    ],
    ROLE_WAREHOUSE_STAFF: [
        "inventory:read",
        "inventory:movement:write",
        "product:read",
        "warehouse:read",
        "voice:query",
    ],
    ROLE_ANALYST: [
        "inventory:read",
        "product:read",
        "warehouse:read",
        "purchase_order:read",
        "forecast:read",
        "recommendation:read",
    ],
}


def check_permission(required_permission: str):
    """
    Dependency factory to check if user has required permission.
    
    Args:
        required_permission: Permission string (e.g., "inventory:write")
        
    Returns:
        Dependency function that raises HTTPException if permission denied
    """
    async def permission_checker(current_user: dict = Depends(get_current_user)) -> dict:
        user_roles = current_user.get("roles", [])
        
        # Get all permissions for user's roles
        user_permissions = set()
        for role in user_roles:
            if role in PERMISSIONS:
                role_perms = PERMISSIONS[role]
                if "*" in role_perms:
                    # Admin has all permissions
                    return current_user
                user_permissions.update(role_perms)
        
        # Check if user has required permission
        if required_permission not in user_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required: {required_permission}"
            )
        
        return current_user
    
    return permission_checker


def require_role(*allowed_roles: str):
    """
    Dependency factory to check if user has one of the allowed roles.
    
    Args:
        *allowed_roles: Allowed role names
        
    Returns:
        Dependency function that raises HTTPException if role not allowed
    """
    allowed_set = set(allowed_roles)
    
    async def role_checker(current_user: dict = Depends(get_current_user)) -> dict:
        user_roles = current_user.get("roles", [])
        
        if not allowed_set.intersection(user_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {', '.join(allowed_roles)}"
            )
        
        return current_user
    
    return role_checker

