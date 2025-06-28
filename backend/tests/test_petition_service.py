#!/usr/bin/env python3
"""
Tests for Petition Service
==========================

Unit tests for petition generation and management.
"""

import pytest
from unittest.mock import Mock, AsyncMock
from services.petition_service import PetitionService
from services.rag_service import RAGService
from services.ollama_service import OllamaService

@pytest.fixture
def mock_rag_service():
    """Mock RAG service"""
    mock = Mock(spec=RAGService)
    mock.query = AsyncMock(return_value={
        'response': 'Mock legal advice',
        'context_sources': []
    })
    return mock

@pytest.fixture
def mock_ollama_service():
    """Mock Ollama service"""
    mock = Mock(spec=OllamaService)
    mock.generate_response = AsyncMock(return_value='Mock petition text')
    return mock

@pytest.fixture
def petition_service(mock_rag_service, mock_ollama_service):
    """Petition service with mocked dependencies"""
    return PetitionService(mock_rag_service, mock_ollama_service)

@pytest.mark.asyncio
async def test_generate_petition(petition_service):
    """Test petition generation"""
    case_details = {
        'case_type': 'Criminal',
        'court': 'High Court',
        'petitioner_name': 'John Doe',
        'respondent_name': 'State',
        'brief_details': 'Test case',
        'plan_of_action': 'Seek bail',
        'specific_details': 'Additional details'
    }
    
    result = await petition_service.generate_petition(case_details, 'test_session')
    
    assert result is not None
    assert 'petition_id' in result
    assert 'petition_text' in result
    assert 'case_details' in result
    assert result['case_details']['case_type'] == 'Criminal'

@pytest.mark.asyncio
async def test_update_petition(petition_service):
    """Test petition update"""
    petition_id = 'test_petition_id'
    updates = {
        'petition_text': 'Updated petition text',
        'status': 'updated'
    }
    
    result = await petition_service.update_petition(petition_id, updates)
    
    assert result is not None
    assert result['petition_id'] == petition_id
    assert result['petition_text'] == 'Updated petition text'

@pytest.mark.asyncio
async def test_get_petition(petition_service):
    """Test getting a petition"""
    petition_id = 'test_petition_id'
    
    result = await petition_service.get_petition(petition_id)
    
    assert result is not None
    assert result['petition_id'] == petition_id

@pytest.mark.asyncio
async def test_get_session_petitions(petition_service):
    """Test getting petitions for a session"""
    session_id = 'test_session_id'
    
    result = await petition_service.get_session_petitions(session_id)
    
    assert isinstance(result, list)

@pytest.mark.asyncio
async def test_delete_petition(petition_service):
    """Test petition deletion"""
    petition_id = 'test_petition_id'
    
    result = await petition_service.delete_petition(petition_id)
    
    assert result is True 