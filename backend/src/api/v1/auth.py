"""
Authentication endpoints.
"""
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.database.session import get_db
from src.api.middleware.auth import create_access_token
from src.config.settings import settings

router = APIRouter(tags=["authentication"])


class Token(BaseModel):
    """Token response model."""
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    """Login request model."""
    username: str
    password: str
    tenant_id: str  # In production, tenant_id might come from subdomain or other source


@router.post("/login", response_model=Token)
async def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Authenticate user and return JWT token.
    
    NOTE: This is a placeholder implementation. In production:
    - Validate credentials against user database
    - Hash password verification
    - Get user roles from database
    - Implement proper user/tenant validation
    """
    # TODO: Implement actual authentication logic
    # For now, accept any credentials (development only)
    
    # Placeholder validation
    if not login_data.username or not login_data.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # TODO: Validate tenant_id exists
    # TODO: Validate user exists and password is correct
    # TODO: Get user roles from database
    
    # Create token with user data
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={
            "sub": login_data.username,  # User identifier
            "tenant_id": login_data.tenant_id,
            "roles": ["inventory_manager"],  # TODO: Get from database
        },
        expires_delta=access_token_expires,
    )
    
    return Token(access_token=access_token, token_type="bearer")


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    OAuth2 compatible token endpoint.
    """
    # TODO: Implement OAuth2 password flow
    # For now, redirect to /login endpoint
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Use /login endpoint for authentication"
    )

