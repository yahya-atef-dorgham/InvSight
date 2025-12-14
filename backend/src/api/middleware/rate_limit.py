"""
Rate limiting middleware.
"""
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from typing import Dict
from datetime import datetime, timedelta, timezone
from collections import defaultdict


class RateLimiter:
    """Simple in-memory rate limiter (use Redis in production)."""
    
    def __init__(self):
        self.requests: Dict[str, list] = defaultdict(list)
    
    def is_allowed(self, key: str, max_requests: int, window_seconds: int) -> bool:
        """
        Check if request is allowed.
        
        Args:
            key: Rate limit key (e.g., IP address or user ID)
            max_requests: Maximum requests allowed
            window_seconds: Time window in seconds
            
        Returns:
            True if allowed, False if rate limited
        """
        now = datetime.now(timezone.utc)
        window_start = now - timedelta(seconds=window_seconds)
        
        # Clean old requests
        self.requests[key] = [
            req_time for req_time in self.requests[key]
            if req_time > window_start
        ]
        
        # Check limit
        if len(self.requests[key]) >= max_requests:
            return False
        
        # Record request
        self.requests[key].append(now)
        return True


# Global rate limiter instance
rate_limiter = RateLimiter()


async def rate_limit_middleware(request: Request, call_next):
    """
    Rate limiting middleware.
    
    Limits: 100 requests per minute per IP
    """
    client_ip = request.client.host if request.client else "unknown"
    
    if not rate_limiter.is_allowed(
        key=f"ip:{client_ip}",
        max_requests=100,
        window_seconds=60
    ):
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={"detail": "Rate limit exceeded. Please try again later."}
        )
    
    response = await call_next(request)
    return response
