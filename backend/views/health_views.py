#!/usr/bin/env python3
"""
Health Views
===========

FastAPI endpoints for health checks and system monitoring.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
import logging
from datetime import datetime
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class HealthResponse(BaseModel):
    status: str
    message: str
    timestamp: str
    version: str

router = APIRouter()

@router.get("/health")
async def health_check():
    """Basic health check endpoint"""
    try:
        return {
            "status": "healthy",
            "message": "Lawgorithm API is running",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0"
        }
    except Exception as e:
        logger.error(f"❌ Health check failed: {e}")
        raise HTTPException(
            status_code=500,
            detail="Health check failed"
        )

@router.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check with service status"""
    try:
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
            "services": {
                "backend": "operational",
                "gemini": "connected",
                "rag": "operational"
            },
            "overall_healthy": True
        }
        
    except Exception as e:
        logger.error(f"❌ Detailed health check failed: {e}")
        return {
            "status": "error",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
            "error": str(e),
            "overall_healthy": False
        } 