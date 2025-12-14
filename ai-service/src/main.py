"""
AI Service FastAPI application for forecasting and recommendations.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api import forecast_api, recommendations_api

# Create FastAPI app
app = FastAPI(
    title="AI Service API",
    description="AI-Powered Forecasting and Recommendations Service",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(forecast_api.router, prefix="/forecast", tags=["forecast"])
app.include_router(recommendations_api.router, prefix="/recommendations", tags=["recommendations"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "AI Service API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "service": "ai-service"}
