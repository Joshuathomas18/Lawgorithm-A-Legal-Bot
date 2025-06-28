#!/usr/bin/env python3
"""
Tests for Conversation Service
==============================

Unit tests for conversation management and chat functionality.
"""

import pytest
from unittest.mock import Mock, AsyncMock
from services.conversation_service import ConversationService
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
    mock.generate_response = AsyncMock(return_value='Mock response')
    return mock

@pytest.fixture
def conversation_service(mock_rag_service, mock_ollama_service):
    """Conversation service with mocked dependencies"""
    return ConversationService(mock_rag_service, mock_ollama_service)

@pytest.mark.asyncio
async def test_create_conversation(conversation_service):
    """Test conversation creation"""
    session_id = 'test_session_id'
    initial_message = 'Hello, I need legal help'
    
    result = await conversation_service.create_conversation(session_id, initial_message)
    
    assert result is not None
    assert 'conversation_id' in result
    assert 'messages' in result
    assert len(result['messages']) == 1
    assert result['messages'][0]['content'] == initial_message

@pytest.mark.asyncio
async def test_add_message(conversation_service):
    """Test adding message to conversation"""
    conversation_id = 'test_conversation_id'
    message = 'What are my legal rights?'
    
    result = await conversation_service.add_message(conversation_id, message)
    
    assert result is not None
    assert 'message_id' in result
    assert result['content'] == message

@pytest.mark.asyncio
async def test_get_conversation(conversation_service):
    """Test getting a conversation"""
    conversation_id = 'test_conversation_id'
    
    result = await conversation_service.get_conversation(conversation_id)
    
    assert result is not None
    assert result['conversation_id'] == conversation_id

@pytest.mark.asyncio
async def test_get_session_conversations(conversation_service):
    """Test getting conversations for a session"""
    session_id = 'test_session_id'
    
    result = await conversation_service.get_session_conversations(session_id)
    
    assert isinstance(result, list)

@pytest.mark.asyncio
async def test_delete_conversation(conversation_service):
    """Test conversation deletion"""
    conversation_id = 'test_conversation_id'
    
    result = await conversation_service.delete_conversation(conversation_id)
    
    assert result is True

@pytest.mark.asyncio
async def test_get_conversation_history(conversation_service):
    """Test getting conversation history"""
    conversation_id = 'test_conversation_id'
    
    result = await conversation_service.get_conversation_history(conversation_id)
    
    assert isinstance(result, list)

@pytest.mark.asyncio
async def test_clear_conversation_history(conversation_service):
    """Test clearing conversation history"""
    conversation_id = 'test_conversation_id'
    
    result = await conversation_service.clear_conversation_history(conversation_id)
    
    assert result is True 