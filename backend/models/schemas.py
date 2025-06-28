#!/usr/bin/env python3
"""
Pydantic Schemas
================

Data models for request/response validation.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class CaseType(str, Enum):
    CRIMINAL = "criminal"
    CIVIL = "civil"
    FAMILY = "family"
    CONSTITUTIONAL = "constitutional"
    ENVIRONMENTAL = "environmental"
    COMMERCIAL = "commercial"
    TAX = "tax"
    LABOR = "labor"
    CONSUMER = "consumer"
    PROPERTY = "property"
    CONTRACT = "contract"
    TORT = "tort"

class CourtType(str, Enum):
    SUPREME_COURT = "Supreme Court"
    HIGH_COURT = "High Court"
    DISTRICT_COURT = "District Court"
    MAGISTRATE_COURT = "Magistrate Court"
    CONSUMER_COURT = "Consumer Court"
    FAMILY_COURT = "Family Court"
    LABOR_COURT = "Labor Court"
    COMMERCIAL_COURT = "Commercial Court"
    TRIBUNAL = "Tribunal"

# Health Check Schemas
class HealthResponse(BaseModel):
    status: str
    message: str
    timestamp: str
    version: str = "1.0.0"

# Petition Schemas
class CaseDetails(BaseModel):
    case_type: CaseType
    court: CourtType
    petitioner_name: str = Field(..., min_length=1)
    respondent_name: str = Field(..., min_length=1)
    incident_date: str
    filing_date: str
    case_number: Optional[str] = None
    facts: str = Field(..., min_length=10)
    evidence: str = Field(..., min_length=10)
    relief: str = Field(..., min_length=10)
    legal_grounds: str = Field(..., min_length=10)

class PetitionRequest(BaseModel):
    case_details: CaseDetails
    session_id: Optional[str] = None

class PetitionResponse(BaseModel):
    petition_id: str
    petition_text: str
    case_details: CaseDetails
    generated_at: str
    session_id: str
    status: str = "generated"

class PetitionEditRequest(BaseModel):
    changes_requested: str = Field(..., min_length=10)
    session_id: str

class PetitionEditResponse(BaseModel):
    petition_id: str
    updated_petition_text: str
    changes_made: str
    updated_at: str

# Conversation Schemas
class ConversationStartRequest(BaseModel):
    user_id: Optional[str] = None
    initial_message: Optional[str] = None

class ConversationStartResponse(BaseModel):
    session_id: str
    conversation_id: str
    status: str = "started"

class MessageRequest(BaseModel):
    message: str = Field(..., min_length=1)
    session_id: str
    conversation_id: str

class MessageResponse(BaseModel):
    message_id: str
    user_message: str
    assistant_response: str
    timestamp: str
    session_id: str
    conversation_id: str

class ConversationHistoryResponse(BaseModel):
    conversation_id: str
    session_id: str
    messages: List[MessageResponse]
    created_at: str
    updated_at: str

# Document Schemas
class DocumentExportRequest(BaseModel):
    petition_id: str
    format: str = Field(..., pattern="^(json|txt|pdf)$")
    session_id: str

class DocumentExportResponse(BaseModel):
    document_id: str
    petition_id: str
    format: str
    download_url: str
    generated_at: str

class DocumentVersionResponse(BaseModel):
    version_id: str
    petition_id: str
    version_number: int
    changes_made: str
    created_at: str
    document_url: str

# Session Schemas
class SessionCreateRequest(BaseModel):
    user_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class SessionResponse(BaseModel):
    session_id: str
    user_id: Optional[str]
    created_at: str
    last_activity: str
    is_active: bool
    metadata: Optional[Dict[str, Any]] = None

# Error Schemas
class ErrorResponse(BaseModel):
    error: str
    message: str
    timestamp: str
    details: Optional[Dict[str, Any]] = None 