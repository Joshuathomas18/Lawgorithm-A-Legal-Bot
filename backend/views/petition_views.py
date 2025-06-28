#!/usr/bin/env python3
"""
Petition Views
=============

FastAPI endpoints for petition generation and management.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
import logging
from datetime import datetime

from ..models.schemas import (
    PetitionRequest, PetitionResponse, PetitionEditRequest, 
    PetitionEditResponse, ErrorResponse
)
from ..models.database import SessionRepository
from ..services.petition_service import PetitionService
from ..models.schemas import CaseDetails

logger = logging.getLogger(__name__)

router = APIRouter()

# Dependency to get petition service
def get_petition_service() -> PetitionService:
    # This would be injected from main.py in a real app
    from main import petition_service
    return petition_service

@router.post("/generate", response_model=PetitionResponse)
async def generate_petition(
    request: PetitionRequest,
    petition_service: PetitionService = Depends(get_petition_service)
):
    """Generate a new petition"""
    try:
        logger.info(f"📄 Generating petition for session: {request.session_id}")
        
        # Create session if not exists
        if request.session_id:
            await SessionRepository.create_session(request.session_id)
        
        # Generate petition
        result = await petition_service.generate_petition(
            request.case_details, 
            request.session_id or "default"
        )
        
        if not result:
            raise HTTPException(
                status_code=500,
                detail="Failed to generate petition"
            )
        
        return PetitionResponse(
            petition_id=result['petition_id'],
            petition_text=result['petition_text'],
            case_details=request.case_details,
            generated_at=result['generated_at'],
            session_id=result['session_id'],
            status=result['status']
        )
        
    except Exception as e:
        logger.error(f"❌ Error generating petition: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating petition: {str(e)}"
        )

@router.get("/{petition_id}", response_model=Dict[str, Any])
async def get_petition(
    petition_id: str,
    petition_service: PetitionService = Depends(get_petition_service)
):
    """Get petition by ID"""
    try:
        petition = await petition_service.get_petition(petition_id)
        
        if not petition:
            raise HTTPException(
                status_code=404,
                detail="Petition not found"
            )
        
        return petition
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting petition: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving petition: {str(e)}"
        )

@router.put("/{petition_id}/edit", response_model=PetitionEditResponse)
async def edit_petition(
    petition_id: str,
    request: PetitionEditRequest,
    petition_service: PetitionService = Depends(get_petition_service)
):
    """Edit an existing petition"""
    try:
        logger.info(f"📝 Editing petition: {petition_id}")
        
        result = await petition_service.update_petition(
            petition_id,
            request.changes_requested,
            request.session_id
        )
        
        if not result:
            raise HTTPException(
                status_code=404,
                detail="Petition not found or update failed"
            )
        
        return PetitionEditResponse(
            petition_id=result['petition_id'],
            updated_petition_text=result['updated_petition_text'],
            changes_made=result['changes_made'],
            updated_at=result['updated_at']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error editing petition: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error editing petition: {str(e)}"
        )

@router.post("/{petition_id}/regenerate", response_model=Dict[str, Any])
async def regenerate_petition(
    petition_id: str,
    session_id: str,
    petition_service: PetitionService = Depends(get_petition_service)
):
    """Regenerate petition completely"""
    try:
        logger.info(f"🔄 Regenerating petition: {petition_id}")
        
        # Get original petition
        original_petition = await petition_service.get_petition(petition_id)
        if not original_petition:
            raise HTTPException(
                status_code=404,
                detail="Petition not found"
            )
        
        # Regenerate with same case details
        case_details = CaseDetails(**original_petition['case_details'])
        
        result = await petition_service.generate_petition(
            case_details,
            session_id
        )
        
        if not result:
            raise HTTPException(
                status_code=500,
                detail="Failed to regenerate petition"
            )
        
        return {
            "message": "Petition regenerated successfully",
            "new_petition_id": result['petition_id'],
            "original_petition_id": petition_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error regenerating petition: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error regenerating petition: {str(e)}"
        )

@router.get("/session/{session_id}/petitions", response_model=Dict[str, Any])
async def get_session_petitions(
    session_id: str,
    petition_service: PetitionService = Depends(get_petition_service)
):
    """Get all petitions for a session"""
    try:
        # This would need to be implemented in PetitionRepository
        # For now, return a placeholder
        return {
            "session_id": session_id,
            "petitions": [],
            "total": 0,
            "message": "Session petitions endpoint - to be implemented"
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting session petitions: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving session petitions: {str(e)}"
        ) 