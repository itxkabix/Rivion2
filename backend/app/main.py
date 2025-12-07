from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import asyncio

# Import routes
from app.routes import search, health
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events"""
    # Startup
    logger.info("🚀 Application starting...")
    logger.info(f"📊 Processing mode: emotion analysis with image search")
    
    yield
    
    # Shutdown
    logger.info("🛑 Application shutting down...")


# Create FastAPI app
app = FastAPI(
    title="Face Emotion Analyzer",
    version="1.0.0",
    description="Capture your face and discover your emotional state. Search similar images from local folder + backend storage.",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(search.router, prefix="/api", tags=["search"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Face Emotion Detection API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "✅ Running"
    }


@app.get("/api/health")
async def health_endpoint():
    """Health check endpoint"""
    return {
        "status": "✅ healthy",
        "service": "face-emotion-analyzer",
        "features": [
            "Face capture from camera",
            "Emotion analysis",
            "Local folder image search",
            "Backend storage search",
            "Combined results"
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
