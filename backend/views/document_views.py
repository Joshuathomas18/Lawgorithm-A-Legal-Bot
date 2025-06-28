#!/usr/bin/env python3
"""
Document Views
=============

FastAPI endpoints for document management and export functionality.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
import logging
import os
from datetime import datetime

from ..models.schemas import (
    DocumentExportRequest, DocumentExportResponse, DocumentVersionResponse
)
from ..services.document_service import DocumentService

logger = logging.getLogger(__name__)

router = APIRouter()

# Dependency to get document service
def get_document_service() -> DocumentService:
    # This would be injected from main.py in a real app
    from main import document_service
    return document_service

@router.post("/export", response_model=DocumentExportResponse)
async def export_document(
    request: DocumentExportRequest,
    document_service: DocumentService = Depends(get_document_service)
):
    """Export a petition in different formats"""
    try:
        logger.info(f"📄 Exporting petition {request.petition_id} in {request.format} format")
        
        result = await document_service.export_document(
            petition_id=request.petition_id,
            format_type=request.format,
            session_id=request.session_id
        )
        
        if not result:
            raise HTTPException(
                status_code=404,
                detail="Petition not found or export failed"
            )
        
        return DocumentExportResponse(
            document_id=result['document_id'],
            petition_id=request.petition_id,
            format=request.format,
            download_url=result['download_url'],
            generated_at=result['generated_at']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error exporting document: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error exporting document: {str(e)}"
        )

@router.get("/{petition_id}/versions", response_model=Dict[str, Any])
async def get_document_versions(
    petition_id: str,
    document_service: DocumentService = Depends(get_document_service)
):
    """Get all versions of a document"""
    try:
        logger.info(f"📜 Getting versions for petition: {petition_id}")
        
        versions = await document_service.get_document_versions(petition_id)
        
        return {
            "petition_id": petition_id,
            "versions": versions,
            "total_versions": len(versions)
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting document versions: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving document versions: {str(e)}"
        )

@router.get("/{petition_id}/version/{version_number}", response_model=Dict[str, Any])
async def get_specific_version(
    petition_id: str,
    version_number: int,
    document_service: DocumentService = Depends(get_document_service)
):
    """Get a specific version of a document"""
    try:
        logger.info(f"📄 Getting version {version_number} of petition: {petition_id}")
        
        version = await document_service.get_specific_version(petition_id, version_number)
        
        if not version:
            raise HTTPException(
                status_code=404,
                detail="Version not found"
            )
        
        return version
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting specific version: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving version: {str(e)}"
        )

@router.get("/download/{document_id}")
async def download_document(
    document_id: str,
    document_service: DocumentService = Depends(get_document_service)
):
    """Download a document file"""
    try:
        logger.info(f"⬇️ Downloading document: {document_id}")
        
        file_path = await document_service.get_document_file_path(document_id)
        
        if not file_path or not os.path.exists(file_path):
            raise HTTPException(
                status_code=404,
                detail="Document file not found"
            )
        
        # Return file path for download
        return {
            "document_id": document_id,
            "file_path": file_path,
            "download_url": f"/static/documents/{os.path.basename(file_path)}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error downloading document: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error downloading document: {str(e)}"
        )

@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    document_service: DocumentService = Depends(get_document_service)
):
    """Delete a document"""
    try:
        logger.info(f"🗑️ Deleting document: {document_id}")
        
        success = await document_service.delete_document(document_id)
        
        if not success:
            raise HTTPException(
                status_code=404,
                detail="Document not found"
            )
        
        return {
            "message": "Document deleted successfully",
            "document_id": document_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error deleting document: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting document: {str(e)}"
        )

@router.get("/session/{session_id}/documents", response_model=Dict[str, Any])
async def get_session_documents(
    session_id: str,
    document_service: DocumentService = Depends(get_document_service)
):
    """Get all documents for a session"""
    try:
        logger.info(f"📄 Getting documents for session: {session_id}")
        
        documents = await document_service.get_session_documents(session_id)
        
        return {
            "session_id": session_id,
            "documents": documents,
            "total": len(documents)
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting session documents: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving session documents: {str(e)}"
        ) 