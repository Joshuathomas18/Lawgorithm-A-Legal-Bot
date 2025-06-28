#!/usr/bin/env python3
"""
API Endpoint Tests
==================

Integration tests for FastAPI endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from main import app

client = TestClient(app)

@pytest.fixture
def mock_services():
    """Mock all services"""
    with patch('services.petition_service.PetitionService') as mock_petition, \
         patch('services.conversation_service.ConversationService') as mock_conversation, \
         patch('services.document_service.DocumentService') as mock_document, \
         patch('services.session_service.SessionService') as mock_session:
        
        # Mock petition service methods
        mock_petition.return_value.generate_petition = AsyncMock(return_value={
            'petition_id': 'test_petition_id',
            'petition_text': 'Test petition text',
            'case_details': {'case_type': 'Criminal'}
        })
        
        # Mock conversation service methods
        mock_conversation.return_value.create_conversation = AsyncMock(return_value={
            'conversation_id': 'test_conversation_id',
            'messages': [{'content': 'Hello'}]
        })
        
        yield {
            'petition': mock_petition,
            'conversation': mock_conversation,
            'document': mock_document,
            'session': mock_session
        }

def test_health_check():
    """Test health check endpoint"""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"

def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "message" in data

@pytest.mark.asyncio
async def test_create_petition(mock_services):
    """Test petition creation endpoint"""
    petition_data = {
        "case_details": {
            "case_type": "Criminal",
            "court": "High Court",
            "petitioner_name": "John Doe",
            "respondent_name": "State",
            "brief_details": "Test case",
            "plan_of_action": "Seek bail",
            "specific_details": "Additional details"
        },
        "session_id": "test_session_id"
    }
    
    response = client.post("/api/v1/petitions/", json=petition_data)
    assert response.status_code == 200
    data = response.json()
    assert "petition_id" in data
    assert "petition_text" in data

@pytest.mark.asyncio
async def test_get_petition(mock_services):
    """Test get petition endpoint"""
    petition_id = "test_petition_id"
    
    # Mock the get_petition method
    mock_services['petition'].return_value.get_petition = AsyncMock(return_value={
        'petition_id': petition_id,
        'petition_text': 'Test petition',
        'case_details': {'case_type': 'Criminal'}
    })
    
    response = client.get(f"/api/v1/petitions/{petition_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["petition_id"] == petition_id

@pytest.mark.asyncio
async def test_create_conversation(mock_services):
    """Test conversation creation endpoint"""
    conversation_data = {
        "session_id": "test_session_id",
        "initial_message": "Hello, I need legal help"
    }
    
    response = client.post("/api/v1/conversations/", json=conversation_data)
    assert response.status_code == 200
    data = response.json()
    assert "conversation_id" in data
    assert "messages" in data

@pytest.mark.asyncio
async def test_add_message(mock_services):
    """Test adding message to conversation"""
    conversation_id = "test_conversation_id"
    message_data = {
        "content": "What are my legal rights?",
        "session_id": "test_session_id"
    }
    
    # Mock the add_message method
    mock_services['conversation'].return_value.add_message = AsyncMock(return_value={
        'message_id': 'test_message_id',
        'content': message_data['content']
    })
    
    response = client.post(f"/api/v1/conversations/{conversation_id}/messages", json=message_data)
    assert response.status_code == 200
    data = response.json()
    assert "message_id" in data

@pytest.mark.asyncio
async def test_export_document(mock_services):
    """Test document export endpoint"""
    petition_id = "test_petition_id"
    export_data = {
        "format_type": "txt",
        "session_id": "test_session_id"
    }
    
    # Mock the export_document method
    mock_services['document'].return_value.export_document = AsyncMock(return_value={
        'document_id': 'test_document_id',
        'download_url': '/static/documents/test.txt'
    })
    
    response = client.post(f"/api/v1/documents/export/{petition_id}", json=export_data)
    assert response.status_code == 200
    data = response.json()
    assert "document_id" in data
    assert "download_url" in data

def test_invalid_endpoint():
    """Test invalid endpoint returns 404"""
    response = client.get("/api/v1/invalid")
    assert response.status_code == 404

def test_invalid_json():
    """Test invalid JSON returns 422"""
    response = client.post("/api/v1/petitions/", json={"invalid": "data"})
    assert response.status_code == 422 