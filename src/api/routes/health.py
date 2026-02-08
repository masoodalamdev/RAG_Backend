from fastapi import APIRouter
from pydantic import BaseModel
from datetime import datetime
import time
import logging

from src.utils.helpers import app_logger

router = APIRouter()


class HealthResponse(BaseModel):
    status: str
    timestamp: str
    uptime: float


# Store the start time to calculate uptime
start_time = time.time()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint to verify the application is running.
    """
    current_time = time.time()
    uptime = current_time - start_time
    
    # Log the health check access
    app_logger.info("Health check endpoint accessed")
    
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        uptime=round(uptime, 2)
    )


@router.get("/ready")
async def readiness_check():
    """
    Readiness check endpoint to verify the application is ready to serve traffic.
    """
    # In a real implementation, you'd check dependencies like database connectivity,
    # external API availability, etc.
    # For now, we'll just return that we're ready
    
    app_logger.info("Readiness check endpoint accessed")
    
    return {"status": "ready"}