#!/usr/bin/env python3
"""
Conversation Service
===================

Service for managing conversations and chat sessions.
"""

import logging
import uuid
import json
from datetime import datetime
from typing import Dict, Any, Optional, List
from ..models.database import SessionRepository

logger = logging.getLogger(__name__)

class ConversationService:
    def __init__(self, rag_service, gemini_service):
        self.rag_service = rag_service
        self.gemini_service = gemini_service
        
    async def start_conversation(self, user_id: Optional[str] = None, initial_message: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Start a new conversation"""
        try:
            logger.info(f"💬 Starting new conversation for user: {user_id}")
            
            # Generate session and conversation IDs
            session_id = str(uuid.uuid4())
            conversation_id = str(uuid.uuid4())
            
            # Create session
            success = await SessionRepository.create_session(session_id, user_id)
            if not success:
                logger.error("❌ Failed to create session")
                return None
            
            # Create conversation record (would be in database)
            conversation_data = {
                'conversation_id': conversation_id,
                'session_id': session_id,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
                'status': 'active'
            }
            
            # Process initial message if provided
            if initial_message:
                await self.process_message(conversation_id, session_id, initial_message)
            
            return {
                'session_id': session_id,
                'conversation_id': conversation_id,
                'status': 'started'
            }
            
        except Exception as e:
            logger.error(f"❌ Error starting conversation: {e}")
            return None
    
    async def process_message(self, conversation_id: str, session_id: str, message: str) -> Optional[Dict[str, Any]]:
        """Process a message in a conversation"""
        try:
            logger.info(f"💬 Processing message in conversation: {conversation_id}")
            
            # Update session activity
            await SessionRepository.update_session_activity(session_id)
            
            # Generate response using RAG and Gemini
            response = await self._generate_response(message)
            
            if not response:
                logger.error("❌ Failed to generate response")
                return None
            
            # Create message record
            message_id = str(uuid.uuid4())
            timestamp = datetime.now().isoformat()
            
            # Store message (would be in database)
            message_data = {
                'message_id': message_id,
                'conversation_id': conversation_id,
                'session_id': session_id,
                'user_message': message,
                'assistant_response': response,
                'timestamp': timestamp
            }
            
            return {
                'message_id': message_id,
                'assistant_response': response,
                'timestamp': timestamp
            }
            
        except Exception as e:
            logger.error(f"❌ Error processing message: {e}")
            return None
    
    async def get_conversation_history(self, conversation_id: str, session_id: str) -> Optional[Dict[str, Any]]:
        """Get conversation history"""
        try:
            logger.info(f"📜 Getting history for conversation: {conversation_id}")
            
            # This would query the database
            # For now, return placeholder data
            return {
                'conversation_id': conversation_id,
                'session_id': session_id,
                'messages': [],  # Would be populated from database
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting conversation history: {e}")
            return None
    
    async def get_session_conversations(self, session_id: str) -> List[Dict[str, Any]]:
        """Get all conversations for a session"""
        try:
            logger.info(f"📜 Getting conversations for session: {session_id}")
            
            # This would query the database
            # For now, return empty list
            return []
            
        except Exception as e:
            logger.error(f"❌ Error getting session conversations: {e}")
            return []
    
    async def end_conversation(self, conversation_id: str, session_id: str) -> bool:
        """End a conversation"""
        try:
            logger.info(f"🔚 Ending conversation: {conversation_id}")
            
            # This would update the database
            # For now, return success
            return True
            
        except Exception as e:
            logger.error(f"❌ Error ending conversation: {e}")
            return False
    
    async def _generate_response(self, message: str) -> Optional[str]:
        """Generate response using RAG and Gemini"""
        try:
            # Use RAG service to get legal context and generate response
            response = await self.rag_service.generate_legal_response(message)
            
            if response:
                return response
            else:
                # Fallback to direct Gemini generation
                prompt = f"""
You are Lawgorithm, a specialized legal AI assistant. A user has asked: "{message}"

Please provide a helpful legal response. If this is a legal question, provide accurate information. If this is not a legal question, politely redirect to legal topics.

Response:"""
                
                return await self.gemini_service.generate_text(prompt)
                
        except Exception as e:
            logger.error(f"❌ Error generating response: {e}")
            return None 