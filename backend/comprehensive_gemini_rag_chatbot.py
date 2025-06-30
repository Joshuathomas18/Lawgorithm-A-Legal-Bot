#!/usr/bin/env python3
"""
Comprehensive Gemini RAG Chatbot
===============================

Advanced chatbot combining Google Gemini AI with RAG capabilities for legal assistance.
"""

import logging
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime

from services.gemini_service import GeminiService
from services.rag_service import RAGService

logger = logging.getLogger(__name__)

class ComprehensiveGeminiRAGChatbot:
    def __init__(self):
        self.gemini_service = None
        self.rag_service = None
        self.is_initialized = False
        self.conversation_history = {}
        
    async def initialize(self):
        """Initialize the chatbot with AI services"""
        try:
            logger.info("🤖 Initializing Comprehensive Gemini RAG Chatbot...")
            
            # Initialize Gemini service
            self.gemini_service = GeminiService(
                api_key="AIzaSyDU7A5_eFsZrtVW20_nVoKFGQ139sRf6IY",
                model_name="gemini-2.0-flash-exp"
            )
            await self.gemini_service.initialize()
            
            # Initialize RAG service
            self.rag_service = RAGService()
            self.rag_service.gemini_service = self.gemini_service
            await self.rag_service.initialize()
            
            self.is_initialized = True
            logger.info("✅ Comprehensive Gemini RAG Chatbot initialized successfully!")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize chatbot: {e}")
            self.is_initialized = False
            raise
    
    async def chat(self, message: str, conversation_id: Optional[str] = None) -> str:
        """Main chat function with RAG capabilities"""
        try:
            if not self.is_initialized:
                await self.initialize()
            
            logger.info(f"💬 Processing chat message: {message[:100]}...")
            
            # Store conversation history
            if conversation_id:
                if conversation_id not in self.conversation_history:
                    self.conversation_history[conversation_id] = []
                self.conversation_history[conversation_id].append({
                    'role': 'user',
                    'content': message,
                    'timestamp': datetime.now().isoformat()
                })
            
            # Generate response using RAG
            response = await self._generate_rag_response(message, conversation_id)
            
            # Store assistant response
            if conversation_id:
                self.conversation_history[conversation_id].append({
                    'role': 'assistant',
                    'content': response,
                    'timestamp': datetime.now().isoformat()
                })
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Error in chat: {e}")
            return self._get_error_response()
    
    async def _generate_rag_response(self, message: str, conversation_id: Optional[str] = None) -> str:
        """Generate response using RAG system"""
        try:
            # Get conversation context
            context = self._get_conversation_context(conversation_id)
            
            # Use RAG service to generate response
            if self.rag_service and self.rag_service.is_initialized:
                response = await self.rag_service.generate_legal_response(message, context)
                return response
            else:
                return self._get_fallback_response(message)
                
        except Exception as e:
            logger.error(f"❌ Error generating RAG response: {e}")
            return self._get_error_response()
    
    def _get_conversation_context(self, conversation_id: Optional[str] = None) -> str:
        """Get conversation context for better responses"""
        try:
            if not conversation_id or conversation_id not in self.conversation_history:
                return ""
            
            history = self.conversation_history[conversation_id]
            
            # Get last few messages for context
            recent_messages = history[-6:]  # Last 3 exchanges
            
            context_parts = []
            for msg in recent_messages:
                role = msg['role'].upper()
                content = msg['content'][:200]  # Limit length
                context_parts.append(f"{role}: {content}")
            
            return "\n".join(context_parts)
            
        except Exception as e:
            logger.error(f"❌ Error getting conversation context: {e}")
            return ""
    
    def _get_fallback_response(self, message: str) -> str:
        """Generate fallback response when AI services are unavailable"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['hello', 'hi', 'start', 'help']):
            return """Hello! Welcome to Lawgorithm, your AI legal assistant. 

I'm here to help you with:
- General legal information and guidance
- Understanding legal procedures
- Legal document drafting assistance
- Legal terminology explanations

**Important**: I provide general information only. For specific legal matters, always consult with a qualified lawyer.

How can I assist you with your legal query today?"""

        elif any(word in message_lower for word in ['bail', 'arrest', 'custody']):
            return """I understand you have questions about bail procedures. Here's some general information:

**Bail Process Overview**:
1. **File Bail Application**: Submit application to appropriate court
2. **Provide Sureties**: Arrange for bail bonds and sureties
3. **Court Hearing**: Attend bail hearing
4. **Compliance**: Follow all bail conditions

**Important Considerations**:
- Bail applications are time-sensitive
- Different types of offenses have different bail provisions
- Sureties must meet court requirements

**Immediate Steps**:
- Contact a criminal lawyer immediately
- Gather necessary documents
- Arrange for potential sureties

**Legal Disclaimer**: This is general information only. Consult with a qualified criminal lawyer for specific advice about your situation."""

        elif any(word in message_lower for word in ['petition', 'complaint', 'legal document']):
            return """I can help you understand legal document preparation. Here's general guidance:

**Document Preparation Steps**:
1. **Identify Document Type**: Petition, complaint, application, etc.
2. **Gather Information**: Facts, evidence, legal grounds
3. **Structure Document**: Header, parties, facts, arguments, prayer
4. **Legal Review**: Have a lawyer review before filing

**Common Document Types**:
- **Petitions**: For seeking court orders or relief
- **Complaints**: For filing civil or criminal cases
- **Applications**: For specific court orders

**Professional Advice**: While I can provide general guidance, it's essential to have any legal document reviewed by a qualified lawyer before filing.

What type of legal document are you looking to prepare?"""

        else:
            return f"""Thank you for your question about: "{message[:100]}..."

I'm here to provide general legal information and guidance. However, for specific legal advice tailored to your situation, I strongly recommend consulting with a qualified lawyer.

**How I can help**:
- Explain legal concepts and procedures
- Provide general guidance on legal processes
- Help understand legal terminology
- Offer information about legal rights

**What you should do**:
- Consult with a qualified lawyer for specific advice
- Gather all relevant documents and evidence
- Consider your legal options carefully

**Legal Disclaimer**: This response provides general information only and should not be considered legal advice.

Could you please provide more specific details about your legal question so I can offer more targeted general guidance?"""
    
    def _get_error_response(self) -> str:
        """Get error response when system fails"""
        return """I apologize, but I'm experiencing technical difficulties at the moment. 

For immediate legal assistance, please:
- Contact a qualified lawyer directly
- Visit your local legal aid center
- Call your local bar association for referrals

**Legal Disclaimer**: This system provides general information only. Always consult with a qualified legal professional for specific legal matters.

Please try again in a few moments, or contact legal professionals directly for urgent matters."""
    
    async def get_conversation_history(self, conversation_id: str) -> List[Dict[str, Any]]:
        """Get conversation history"""
        try:
            return self.conversation_history.get(conversation_id, [])
        except Exception as e:
            logger.error(f"❌ Error getting conversation history: {e}")
            return []
    
    async def clear_conversation(self, conversation_id: str) -> bool:
        """Clear conversation history"""
        try:
            if conversation_id in self.conversation_history:
                del self.conversation_history[conversation_id]
                return True
            return False
        except Exception as e:
            logger.error(f"❌ Error clearing conversation: {e}")
            return False
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for the chatbot"""
        try:
            return {
                'status': 'healthy' if self.is_initialized else 'unhealthy',
                'initialized': self.is_initialized,
                'gemini_service': {
                    'available': self.gemini_service is not None,
                    'initialized': self.gemini_service.is_initialized if self.gemini_service else False
                },
                'rag_service': {
                    'available': self.rag_service is not None,
                    'initialized': self.rag_service.is_initialized if self.rag_service else False
                },
                'active_conversations': len(self.conversation_history)
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'initialized': False
            }