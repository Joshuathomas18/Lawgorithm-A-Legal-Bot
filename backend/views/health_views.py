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

from ..models.schemas import HealthResponse, ErrorResponse

logger = logging.getLogger(__name__)

router = APIRouter()

# Dependency to get services
def get_services():
    # This would be injected from main.py in a real app
    from main import rag_service, gemini_service
    return rag_service, gemini_service

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Basic health check endpoint"""
    try:
        return HealthResponse(
            status="healthy",
            message="Petition Automator API is running",
            timestamp=datetime.now().isoformat(),
            version="1.0.0"
        )
    except Exception as e:
        logger.error(f"❌ Health check failed: {e}")
        raise HTTPException(
            status_code=500,
            detail="Health check failed"
        )

@router.get("/health/detailed", response_model=Dict[str, Any])
async def detailed_health_check(
    services = Depends(get_services)
):
    """Detailed health check with service status"""
    try:
        rag_service, gemini_service = services
        
        # Get health status from all services
        rag_health = await rag_service.health_check()
        gemini_health = await gemini_service.health_check()
        
        # Overall system health
        overall_healthy = (
            rag_health.get('status') == 'healthy' and
            gemini_health.get('status') == 'healthy'
        )
        
        return {
            "status": "healthy" if overall_healthy else "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
            "services": {
                "rag_service": rag_health,
                "gemini_service": gemini_health
            },
            "overall_healthy": overall_healthy
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

@router.get("/health/rag", response_model=Dict[str, Any])
async def rag_health_check(
    services = Depends(get_services)
):
    """RAG service health check"""
    try:
        rag_service, _ = services
        health_status = await rag_service.health_check()
        return health_status
        
    except Exception as e:
        logger.error(f"❌ RAG health check failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"RAG health check failed: {str(e)}"
        )

@router.get("/health/gemini", response_model=Dict[str, Any])
async def gemini_health_check(
    services = Depends(get_services)
):
    """Gemini service health check"""
    try:
        _, gemini_service = services
        health_status = await gemini_service.health_check()
        return health_status
        
    except Exception as e:
        logger.error(f"❌ Gemini health check failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Gemini health check failed: {str(e)}"
        )

@router.get("/status", response_model=Dict[str, Any])
async def system_status(
    services = Depends(get_services)
):
    """Get comprehensive system status"""
    try:
        rag_service, gemini_service = services
        
        # Get detailed status from services
        rag_status = await rag_service.get_vector_store_stats()
        gemini_models = await gemini_service.get_available_models()
        
        return {
            "system": {
                "name": "Petition Automator API",
                "version": "1.0.0",
                "status": "running",
                "timestamp": datetime.now().isoformat()
            },
            "rag_system": {
                "status": "connected" if rag_status else "disconnected",
                "vector_store": rag_status,
                "total_documents": rag_status.get('total_documents', 0) if rag_status else 0
            },
            "gemini_system": {
                "status": "connected" if gemini_models else "disconnected",
                "available_models": [model['name'] for model in gemini_models],
                "total_models": len(gemini_models),
                "current_model": gemini_service.model_name
            },
            "capabilities": {
                "petition_generation": True,
                "conversation_support": True,
                "document_export": True,
                "real_time_chat": True
            }
        }
        
    except Exception as e:
        logger.error(f"❌ System status check failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"System status check failed: {str(e)}"
        ) 