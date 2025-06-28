#!/usr/bin/env python3
"""
Conversation Views
=================

FastAPI endpoints for conversation management and chat functionality.
"""

from fastapi import APIRouter, HTTPException, Depends, WebSocket, WebSocketDisconnect
from typing import Dict, Any, List
import logging
import json
from datetime import datetime
from pydantic import BaseModel
import uuid
from typing import Optional

from models.schemas import (
    ConversationStartRequest, ConversationStartResponse,
    MessageRequest, MessageResponse, ConversationHistoryResponse
)
from models.database import SessionRepository
from services.conversation_service import ConversationService

logger = logging.getLogger(__name__)

router = APIRouter()

# Dependency to get conversation service
def get_conversation_service() -> ConversationService:
    # This would be injected from main.py in a real app
    from main import conversation_service
    return conversation_service

class ConversationStartRequest(BaseModel):
    user_id: Optional[str] = None
    initial_message: Optional[str] = None

class ConversationStartResponse(BaseModel):
    session_id: str
    conversation_id: str
    status: str = "started"

# In-memory store for mock conversation history (for demo)
conversation_history_store: Dict[str, Any] = {}

@router.post("/start", response_model=ConversationStartResponse)
async def start_conversation(request: ConversationStartRequest):
    session_id = str(uuid.uuid4())
    conversation_id = str(uuid.uuid4())
    # Store initial message in mock history
    conversation_history_store[conversation_id] = [{
        "role": "user",
        "content": request.initial_message or "",
        "timestamp": ""
    }]
    return ConversationStartResponse(
        session_id=session_id,
        conversation_id=conversation_id,
        status="started"
    )

@router.get("/{conversation_id}/history")
async def get_conversation_history(conversation_id: str):
    # Return mock conversation history
    return {
        "conversation_id": conversation_id,
        "messages": conversation_history_store.get(conversation_id, [])
    }

@router.post("/message", response_model=MessageResponse)
async def send_message(
    request: MessageRequest,
    conversation_service: ConversationService = Depends(get_conversation_service)
):
    """Send a message in a conversation"""
    try:
        logger.info(f"💬 Processing message in conversation: {request.conversation_id}")
        
        result = await conversation_service.process_message(
            conversation_id=request.conversation_id,
            session_id=request.session_id,
            message=request.message
        )
        
        if not result:
            raise HTTPException(
                status_code=500,
                detail="Failed to process message"
            )
        
        return MessageResponse(
            message_id=result['message_id'],
            user_message=request.message,
            assistant_response=result['assistant_response'],
            timestamp=result['timestamp'],
            session_id=request.session_id,
            conversation_id=request.conversation_id
        )
        
    except Exception as e:
        logger.error(f"❌ Error processing message: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing message: {str(e)}"
        )

@router.get("/{conversation_id}/history", response_model=ConversationHistoryResponse)
async def get_conversation_history(
    conversation_id: str,
    session_id: str,
    conversation_service: ConversationService = Depends(get_conversation_service)
):
    """Get conversation history"""
    try:
        logger.info(f"📜 Getting history for conversation: {conversation_id}")
        
        result = await conversation_service.get_conversation_history(
            conversation_id=conversation_id,
            session_id=session_id
        )
        
        if not result:
            raise HTTPException(
                status_code=404,
                detail="Conversation not found"
            )
        
        return ConversationHistoryResponse(
            conversation_id=result['conversation_id'],
            session_id=result['session_id'],
            messages=result['messages'],
            created_at=result['created_at'],
            updated_at=result['updated_at']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting conversation history: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving conversation history: {str(e)}"
        )

@router.get("/session/{session_id}/conversations", response_model=Dict[str, Any])
async def get_session_conversations(
    session_id: str,
    conversation_service: ConversationService = Depends(get_conversation_service)
):
    """Get all conversations for a session"""
    try:
        logger.info(f"📜 Getting conversations for session: {session_id}")
        
        conversations = await conversation_service.get_session_conversations(session_id)
        
        return {
            "session_id": session_id,
            "conversations": conversations,
            "total": len(conversations)
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting session conversations: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving session conversations: {str(e)}"
        )

@router.delete("/{conversation_id}")
async def end_conversation(
    conversation_id: str,
    session_id: str,
    conversation_service: ConversationService = Depends(get_conversation_service)
):
    """End a conversation"""
    try:
        logger.info(f"🔚 Ending conversation: {conversation_id}")
        
        success = await conversation_service.end_conversation(
            conversation_id=conversation_id,
            session_id=session_id
        )
        
        if not success:
            raise HTTPException(
                status_code=404,
                detail="Conversation not found"
            )
        
        return {
            "message": "Conversation ended successfully",
            "conversation_id": conversation_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error ending conversation: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error ending conversation: {str(e)}"
        )

# WebSocket endpoint for real-time chat
@router.websocket("/ws/{conversation_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    conversation_id: str,
    session_id: str
):
    """WebSocket endpoint for real-time conversation"""
    try:
        await websocket.accept()
        logger.info(f"🔌 WebSocket connected for conversation: {conversation_id}")
        
        # Get conversation service
        conversation_service = get_conversation_service()
        
        while True:
            try:
                # Receive message from client
                data = await websocket.receive_text()
                message_data = json.loads(data)
                
                # Process message
                result = await conversation_service.process_message(
                    conversation_id=conversation_id,
                    session_id=session_id,
                    message=message_data.get('message', '')
                )
                
                if result:
                    # Send response back to client
                    response = {
                        "type": "message",
                        "message_id": result['message_id'],
                        "assistant_response": result['assistant_response'],
                        "timestamp": result['timestamp']
                    }
                    await websocket.send_text(json.dumps(response))
                else:
                    # Send error response
                    error_response = {
                        "type": "error",
                        "message": "Failed to process message"
                    }
                    await websocket.send_text(json.dumps(error_response))
                    
            except WebSocketDisconnect:
                logger.info(f"🔌 WebSocket disconnected for conversation: {conversation_id}")
                break
            except Exception as e:
                logger.error(f"❌ WebSocket error: {e}")
                error_response = {
                    "type": "error",
                    "message": f"Error: {str(e)}"
                }
                await websocket.send_text(json.dumps(error_response))
                
    except Exception as e:
        logger.error(f"❌ WebSocket connection error: {e}")
        await websocket.close() 