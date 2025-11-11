"""
Health check endpoint
"""

from fastapi import APIRouter
from api.models.response import HealthResponse

router = APIRouter()

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint
    Returns API status and version
    """
    return HealthResponse(
        status="healthy",
        version="1.0.0"
    )

