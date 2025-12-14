"""
Main FastAPI application entry point.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.config.settings import settings
from src.api.middleware.security import SecurityHeadersMiddleware
from src.api.v1 import auth, products, warehouses, inventory, forecasts, recommendations, suppliers, purchase_orders, ai_query
from src.api.websocket import websocket_endpoint

# Create FastAPI app
app = FastAPI(
    title="Inventory Management API",
    description="AI-Powered Inventory Management System API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add security headers
app.add_middleware(SecurityHeadersMiddleware)

# Include routers
app.include_router(auth.router, prefix=settings.api_v1_prefix)
app.include_router(products.router, prefix=settings.api_v1_prefix)
app.include_router(warehouses.router, prefix=settings.api_v1_prefix)
app.include_router(inventory.router, prefix=settings.api_v1_prefix)
app.include_router(forecasts.router, prefix=settings.api_v1_prefix)
app.include_router(recommendations.router, prefix=settings.api_v1_prefix)
app.include_router(suppliers.router, prefix=settings.api_v1_prefix)
app.include_router(purchase_orders.router, prefix=settings.api_v1_prefix)
app.include_router(ai_query.router, prefix=settings.api_v1_prefix)

# WebSocket endpoint
app.websocket("/ws/inventory")(websocket_endpoint)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Inventory Management API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

