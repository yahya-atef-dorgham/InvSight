"""
Voice Service FastAPI application for speech processing.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api import voice_api

# Create FastAPI app
app = FastAPI(
    title="Voice Service API",
    description="Voice Processing Service for Speech-to-Text and Text-to-Speech",
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
app.include_router(voice_api.router, prefix="/voice", tags=["voice"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Voice Service API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "service": "voice-service"}
