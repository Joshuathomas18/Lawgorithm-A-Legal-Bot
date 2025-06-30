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

logger = logging.getLogger(__name__)

router = APIRouter()

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
        "timestamp": datetime.now().isoformat()
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