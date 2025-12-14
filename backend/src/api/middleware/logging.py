"""
Request logging middleware.
"""
import time
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all HTTP requests."""
    
    async def dispatch(self, request: Request, call_next):
        """Log request details and response time."""
        start_time = time.time()
        
        # Log request
        logger.info(
            f"Request: {request.method} {request.url.path} - "
            f"Client: {request.client.host if request.client else 'unknown'}"
        )
        
        # Process request
        response = await call_next(request)
        
        # Calculate duration
        process_time = time.time() - start_time
        
        # Log response
        logger.info(
            f"Response: {response.status_code} - "
            f"Duration: {process_time:.3f}s"
        )
        
        # Add header with process time
        response.headers["X-Process-Time"] = str(process_time)
        
        return response

