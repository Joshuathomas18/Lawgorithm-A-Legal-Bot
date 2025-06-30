#!/usr/bin/env python3
"""
Conversation Service
===================

Service for managing conversations and chat functionality.
"""

import logging
import uuid
import json
from datetime import datetime
from typing import Dict, Any, List, Optional

from models.database import db_manager

logger = logging.getLogger(__name__)

class ConversationService:
    def __init__(self, rag_service=None, gemini_service=None):
        self.rag_service = rag_service
        self.gemini_service = gemini_service
        self.is_initialized = True
        
    async def process_message(self, conversation_id: str, session_id: str, message: str) -> Optional[Dict[str, Any]]:
        """Process a user message and generate AI response"""
        try:
            logger.info(f"💬 Processing message in conversation {conversation_id}")
            
            # Generate AI response using RAG
            if self.rag_service and self.rag_service.is_initialized:
                assistant_response = await self.rag_service.generate_legal_response(message)
            else:
                # Fallback response if RAG service is not available
                assistant_response = self._generate_fallback_response(message)
            
            # Generate unique message ID
            message_id = str(uuid.uuid4())
            timestamp = datetime.now().isoformat()
            
            # Store message in database
            try:
                cursor = db_manager.conn.cursor()
                cursor.execute("""
                    INSERT INTO messages (message_id, conversation_id, session_id, user_message, assistant_response, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (message_id, conversation_id, session_id, message, assistant_response, timestamp))
                db_manager.conn.commit()
                logger.info("✅ Message stored in database")
            except Exception as db_error:
                logger.warning(f"⚠️ Database storage failed: {db_error}")
                # Continue even if database storage fails
            
            return {
                'message_id': message_id,
                'user_message': message,
                'assistant_response': assistant_response,
                'timestamp': timestamp,
                'conversation_id': conversation_id,
                'session_id': session_id
            }
            
        except Exception as e:
            logger.error(f"❌ Error processing message: {e}")
            return None
    
    def _generate_fallback_response(self, message: str) -> str:
        """Generate fallback response when AI services are unavailable"""
        message_lower = message.lower()
        
        # Legal advice responses
        if any(word in message_lower for word in ['bail', 'arrest', 'custody']):
            return """Thank you for your query about bail matters. While I'd like to provide specific guidance, I recommend consulting with a qualified criminal lawyer who can:

1. Review the specific circumstances of your case
2. Advise on bail eligibility and procedures
3. Prepare and file the bail application
4. Represent you in court proceedings

**Important**: Bail applications are time-sensitive legal matters. Please contact a lawyer immediately for urgent cases.

**Legal Disclaimer**: This response provides general information only and should not be considered legal advice. Always consult with a qualified legal professional."""

        elif any(word in message_lower for word in ['petition', 'complaint', 'case']):
            return """I understand you need help with legal documentation. For petition and complaint drafting, I recommend:

1. **Consult a Lawyer**: A qualified advocate can draft legally sound documents
2. **Gather Documents**: Collect all relevant evidence and supporting documents
3. **Understand Procedures**: Learn about court procedures and filing requirements

**What I can help with**:
- General guidance on legal procedures
- Information about different types of petitions
- Basic legal terminology explanations

**Legal Disclaimer**: This system provides general information only. For specific legal matters, always consult with a qualified lawyer who can provide personalized advice."""

        elif any(word in message_lower for word in ['hello', 'hi', 'help', 'start']):
            return """Hello! Welcome to Lawgorithm, your AI legal assistant. I'm here to help you with general legal information and guidance.

**How I can assist you**:
- Provide general legal information
- Help understand legal procedures
- Offer guidance on documentation
- Explain legal terminology

**To get started**:
- Tell me about your legal query or situation
- Ask about specific legal procedures
- Request information about legal rights

**Important**: I provide general information only. For specific legal matters, always consult with a qualified lawyer.

What legal topic would you like to know more about?"""

        else:
            return f"""Thank you for your question. While I'd like to provide specific guidance on "{message[:100]}...", I recommend consulting with a qualified lawyer for personalized legal advice.

**General Resources**:
- Contact local bar association for lawyer referrals
- Visit legal aid societies for affordable legal help
- Check government legal portals for information

**Legal Disclaimer**: This system provides general information only and should not be considered legal advice. Always consult with a qualified legal professional for specific legal matters.

Is there a specific aspect of your legal question I can help clarify?"""
    
    async def get_conversation_history(self, conversation_id: str, session_id: str) -> Optional[Dict[str, Any]]:
        """Get conversation history"""
        try:
            cursor = db_manager.conn.cursor()
            cursor.execute("""
                SELECT * FROM messages 
                WHERE conversation_id = ? AND session_id = ?
                ORDER BY timestamp ASC
            """, (conversation_id, session_id))
            
            rows = cursor.fetchall()
            messages = []
            
            for row in rows:
                messages.append({
                    'message_id': row['message_id'],
                    'user_message': row['user_message'],
                    'assistant_response': row['assistant_response'],
                    'timestamp': row['timestamp']
                })
            
            # Get conversation info
            cursor.execute("""
                SELECT created_at, updated_at 
                FROM conversations 
                WHERE conversation_id = ?
            """, (conversation_id,))
            
            conv_row = cursor.fetchone()
            
            return {
                'conversation_id': conversation_id,
                'session_id': session_id,
                'messages': messages,
                'created_at': conv_row['created_at'] if conv_row else datetime.now().isoformat(),
                'updated_at': conv_row['updated_at'] if conv_row else datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting conversation history: {e}")
            return None
    
    async def get_session_conversations(self, session_id: str) -> List[Dict[str, Any]]:
        """Get all conversations for a session"""
        try:
            cursor = db_manager.conn.cursor()
            cursor.execute("""
                SELECT conversation_id, created_at, updated_at, status
                FROM conversations 
                WHERE session_id = ?
                ORDER BY created_at DESC
            """, (session_id,))
            
            rows = cursor.fetchall()
            conversations = []
            
            for row in rows:
                conversations.append({
                    'conversation_id': row['conversation_id'],
                    'created_at': row['created_at'],
                    'updated_at': row['updated_at'],
                    'status': row['status']
                })
            
            return conversations
            
        except Exception as e:
            logger.error(f"❌ Error getting session conversations: {e}")
            return []
    
    async def end_conversation(self, conversation_id: str, session_id: str) -> bool:
        """End a conversation"""
        try:
            cursor = db_manager.conn.cursor()
            cursor.execute("""
                UPDATE conversations 
                SET status = 'ended', updated_at = ?
                WHERE conversation_id = ? AND session_id = ?
            """, (datetime.now().isoformat(), conversation_id, session_id))
            
            db_manager.conn.commit()
            return cursor.rowcount > 0
            
        except Exception as e:
            logger.error(f"❌ Error ending conversation: {e}")
            return False
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for conversation service"""
        return {
            'status': 'healthy',
            'initialized': self.is_initialized,
            'rag_service_available': self.rag_service is not None and self.rag_service.is_initialized,
            'gemini_service_available': self.gemini_service is not None and self.gemini_service.is_initialized
        }