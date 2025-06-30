#!/usr/bin/env python3
"""
Pydantic Schemas
===============

Data models and schemas for the Lawgorithm API.
"""

from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

# Health Check Schemas
class HealthResponse(BaseModel):
    status: str
    message: str
    timestamp: str
    version: str

class ErrorResponse(BaseModel):
    error: str
    detail: str
    timestamp: str

# Session Schemas
class SessionCreateRequest(BaseModel):
    user_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class SessionResponse(BaseModel):
    session_id: str
    user_id: str
    created_at: str
    expires_at: str

# Conversation Schemas
class ConversationStartRequest(BaseModel):
    user_id: Optional[str] = None
    initial_message: Optional[str] = None

class ConversationStartResponse(BaseModel):
    session_id: str
    conversation_id: str
    status: str = "started"

class MessageRequest(BaseModel):
    conversation_id: str
    session_id: str
    message: str

class MessageResponse(BaseModel):
    message_id: str
    user_message: str
    assistant_response: str
    timestamp: str
    session_id: str
    conversation_id: str

class ConversationMessage(BaseModel):
    message_id: str
    user_message: str
    assistant_response: str
    timestamp: str

class ConversationHistoryResponse(BaseModel):
    conversation_id: str
    session_id: str
    messages: List[ConversationMessage]
    created_at: str
    updated_at: str

# Chatbot Schemas
class ChatbotMessageRequest(BaseModel):
    message: str
    session_id: str
    conversation_id: str

class ChatbotMessageResponse(BaseModel):
    message_id: str
    user_message: str
    assistant_response: str
    timestamp: str
    session_id: str
    conversation_id: str

# Petition Schemas
class PetitionGenerateRequest(BaseModel):
    session_id: str
    case_type: str
    case_facts: str
    relief_sought: str
    additional_details: Optional[Dict[str, Any]] = None

class PetitionResponse(BaseModel):
    petition_id: str
    petition_text: str
    case_details: Dict[str, Any]
    generated_at: str
    status: str

class PetitionUpdateRequest(BaseModel):
    petition_text: str
    changes_made: str

# Document Schemas
class DocumentExportRequest(BaseModel):
    document_text: str
    format: str  # txt, pdf, docx
    filename: str

class DocumentExportResponse(BaseModel):
    success: bool
    file_path: Optional[str] = None
    download_url: Optional[str] = None
    format: Optional[str] = None
    error: Optional[str] = None

class DocumentInfo(BaseModel):
    filename: str
    file_path: str
    size: int
    created: float
    modified: float
    format: str

# RAG Schemas
class RAGQueryRequest(BaseModel):
    query: str
    limit: Optional[int] = 5

class RAGDocument(BaseModel):
    id: str
    title: str
    content: str
    category: str
    document_type: str
    relevance_score: Optional[float] = None

class RAGQueryResponse(BaseModel):
    query: str
    documents: List[RAGDocument]
    context: str
    response: str