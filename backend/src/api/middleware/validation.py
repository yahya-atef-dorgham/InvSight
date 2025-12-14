"""
Input validation and sanitization middleware.
"""
from fastapi import Request, HTTPException, status
from typing import Any
import re


def sanitize_string(value: str, max_length: int = 1000) -> str:
    """
    Sanitize string input.
    
    Args:
        value: Input string
        max_length: Maximum allowed length
        
    Returns:
        Sanitized string
    """
    if not isinstance(value, str):
        return str(value)
    
    # Remove null bytes
    value = value.replace('\x00', '')
    
    # Truncate if too long
    if len(value) > max_length:
        value = value[:max_length]
    
    return value.strip()


def validate_uuid(value: str) -> str:
    """
    Validate UUID format.
    
    Args:
        value: UUID string
        
    Returns:
        Validated UUID string
        
    Raises:
        HTTPException if invalid
    """
    uuid_pattern = re.compile(
        r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
        re.IGNORECASE
    )
    
    if not uuid_pattern.match(value):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid UUID format: {value}"
        )
    
    return value


def sanitize_dict(data: dict) -> dict:
    """
    Recursively sanitize dictionary values.
    
    Args:
        data: Dictionary to sanitize
        
    Returns:
        Sanitized dictionary
    """
    sanitized = {}
    for key, value in data.items():
        if isinstance(value, str):
            sanitized[key] = sanitize_string(value)
        elif isinstance(value, dict):
            sanitized[key] = sanitize_dict(value)
        elif isinstance(value, list):
            sanitized[key] = [
                sanitize_string(item) if isinstance(item, str) else item
                for item in value
            ]
        else:
            sanitized[key] = value
    
    return sanitized
