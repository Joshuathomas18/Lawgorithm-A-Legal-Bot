#!/usr/bin/env python3
"""
RAG Service
===========

Service for Retrieval Augmented Generation using legal document knowledge base.
"""

import os
import json
import logging
import asyncio
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import sqlite3

logger = logging.getLogger(__name__)

class RAGService:
    def __init__(self):
        self.is_initialized = False
        self.vector_store_path = None
        self.knowledge_base = []
        self.gemini_service = None
        
    async def initialize(self):
        """Initialize RAG service"""
        try:
            logger.info("🔍 Initializing RAG service...")
            
            # Set up vector store path
            self.vector_store_path = "rag/vector_store_lawgorithm"
            
            # Load knowledge base
            await self._load_knowledge_base()
            
            self.is_initialized = True
            logger.info("✅ RAG service initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize RAG service: {e}")
            self.is_initialized = False
            raise
    
    async def _load_knowledge_base(self):
        """Load legal knowledge base"""
        try:
            # Try to load existing vector store
            vector_store_file = Path(self.vector_store_path) / "vector_store.json"
            
            if vector_store_file.exists():
                with open(vector_store_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.knowledge_base = data.get('documents', [])
                    logger.info(f"📚 Loaded {len(self.knowledge_base)} documents from vector store")
            else:
                # Create basic legal knowledge base
                await self._create_basic_knowledge_base()
                
        except Exception as e:
            logger.warning(f"⚠️ Could not load vector store: {e}")
            await self._create_basic_knowledge_base()
    
    async def _create_basic_knowledge_base(self):
        """Create basic legal knowledge base"""
        try:
            logger.info("📝 Creating basic legal knowledge base...")
            
            # Basic legal documents and templates
            basic_knowledge = [
                {
                    "id": "petition_template_1",
                    "title": "Criminal Petition Template",
                    "content": """
                    CRIMINAL PETITION TEMPLATE:
                    
                    IN THE COURT OF [COURT NAME]
                    [CASE NUMBER]
                    
                    BETWEEN:
                    [PETITIONER NAME] - Petitioner
                    AND
                    [RESPONDENT NAME] - Respondent
                    
                    MOST RESPECTFULLY SHEWETH:
                    
                    1. That the petitioner is a law-abiding citizen of India.
                    2. That the facts of the case are as follows: [CASE FACTS]
                    3. That the petitioner submits that [LEGAL GROUNDS]
                    
                    PRAYER:
                    In the premises aforesaid, it is most respectfully prayed that this Hon'ble Court may be pleased to:
                    a) [RELIEF SOUGHT]
                    b) Pass such other orders as this Hon'ble Court may deem fit.
                    
                    And for this act of kindness, the petitioner shall ever pray.
                    
                    AFFIDAVIT
                    I, [NAME], do hereby solemnly affirm and declare as under:
                    1. That I am the petitioner in the above case.
                    2. That the contents of the above petition are true to my knowledge.
                    
                    [PETITIONER SIGNATURE]
                    """,
                    "category": "petition_template",
                    "document_type": "criminal"
                },
                {
                    "id": "bail_template_1", 
                    "title": "Bail Application Template",
                    "content": """
                    BAIL APPLICATION TEMPLATE:
                    
                    IN THE COURT OF [COURT NAME]
                    
                    APPLICATION FOR BAIL
                    
                    MOST RESPECTFULLY SHEWETH:
                    
                    1. That the applicant/accused is innocent and has been falsely implicated.
                    2. That there is no likelihood of the applicant fleeing from justice.
                    3. That the applicant has deep roots in society and permanent residence.
                    4. That the investigation is complete and no further custodial interrogation is required.
                    
                    UNDERTAKING:
                    The applicant undertakes to:
                    1. Appear before the court as and when required
                    2. Not tamper with evidence or influence witnesses
                    3. Not commit any offense while on bail
                    
                    PRAYER:
                    It is respectfully prayed that bail may be granted to the applicant.
                    """,
                    "category": "bail_template", 
                    "document_type": "bail"
                },
                {
                    "id": "legal_principles_1",
                    "title": "Legal Principles and Precedents",
                    "content": """
                    IMPORTANT LEGAL PRINCIPLES:
                    
                    1. PRESUMPTION OF INNOCENCE: Every accused is presumed innocent until proven guilty.
                    
                    2. BURDEN OF PROOF: The burden of proving guilt lies on the prosecution.
                    
                    3. REASONABLE DOUBT: If there is reasonable doubt, benefit goes to the accused.
                    
                    4. NATURAL JUSTICE: Audi alteram partem - hear the other side.
                    
                    5. CONSTITUTIONAL RIGHTS:
                       - Right to life and liberty (Article 21)
                       - Right to legal representation (Article 22)
                       - Protection against self-incrimination (Article 20)
                    
                    6. BAIL PRINCIPLES:
                       - Bail is the rule, jail is the exception
                       - Bail should not be refused to humiliate the accused
                       - Consider flight risk and tampering potential
                    """,
                    "category": "legal_principles",
                    "document_type": "reference"
                }
            ]
            
            self.knowledge_base = basic_knowledge
            
            # Save to vector store
            os.makedirs(self.vector_store_path, exist_ok=True)
            vector_store_file = Path(self.vector_store_path) / "vector_store.json"
            
            with open(vector_store_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "documents": self.knowledge_base,
                    "created_at": "2024-01-01",
                    "version": "1.0"
                }, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Created basic knowledge base with {len(basic_knowledge)} documents")
            
        except Exception as e:
            logger.error(f"❌ Error creating knowledge base: {e}")
            self.knowledge_base = []
    
    async def search_relevant_documents(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search for relevant documents based on query"""
        try:
            if not self.knowledge_base:
                return []
            
            # Simple keyword-based search for now
            query_lower = query.lower()
            relevant_docs = []
            
            for doc in self.knowledge_base:
                content_lower = doc.get('content', '').lower()
                title_lower = doc.get('title', '').lower()
                
                # Calculate relevance score
                score = 0
                
                # Check for keyword matches
                query_words = query_lower.split()
                for word in query_words:
                    if word in content_lower:
                        score += content_lower.count(word)
                    if word in title_lower:
                        score += title_lower.count(word) * 2  # Title matches are more important
                
                if score > 0:
                    relevant_docs.append({
                        **doc,
                        'relevance_score': score
                    })
            
            # Sort by relevance score
            relevant_docs.sort(key=lambda x: x['relevance_score'], reverse=True)
            
            logger.info(f"🔍 Found {len(relevant_docs)} relevant documents for query: {query[:50]}...")
            return relevant_docs[:limit]
            
        except Exception as e:
            logger.error(f"❌ Error searching documents: {e}")
            return []
    
    async def get_context_for_query(self, query: str) -> str:
        """Get relevant context for a query"""
        try:
            relevant_docs = await self.search_relevant_documents(query, limit=3)
            
            if not relevant_docs:
                return "No specific legal precedents found for this query."
            
            context_parts = []
            for doc in relevant_docs:
                context_parts.append(f"**{doc['title']}**\n{doc['content'][:500]}...")
            
            context = "\n\n".join(context_parts)
            return context
            
        except Exception as e:
            logger.error(f"❌ Error getting context: {e}")
            return "Error retrieving legal context."
    
    async def generate_legal_response(self, query: str, context: str = None) -> str:
        """Generate legal response using RAG"""
        try:
            if not self.gemini_service or not self.gemini_service.is_initialized:
                return "AI service not available. Please try again later."
            
            # Get context if not provided
            if not context:
                context = await self.get_context_for_query(query)
            
            # Create enhanced prompt with legal context
            prompt = f"""
            You are an AI legal assistant for the Indian legal system. Provide helpful, accurate legal guidance while always recommending consultation with qualified lawyers.

            Legal Context:
            {context}

            User Query: {query}

            Please provide a comprehensive response that:
            1. Addresses the user's legal question
            2. References relevant legal principles
            3. Suggests appropriate next steps
            4. Includes a disclaimer about seeking professional legal advice
            5. Uses the provided legal context appropriately

            Important: Always end with a legal disclaimer and recommend consulting with a qualified lawyer.
            """
            
            response = await self.gemini_service.generate_text(prompt)
            
            if not response:
                return """I apologize, but I'm unable to generate a response at the moment. 
                
For legal matters, I strongly recommend consulting with a qualified lawyer who can provide personalized advice based on your specific situation.

**Legal Disclaimer**: This system provides general information only and should not be considered as legal advice. Always consult with a qualified legal professional for specific legal matters."""
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Error generating legal response: {e}")
            return "I apologize, but there was an error processing your request. Please consult with a qualified lawyer for legal advice."
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for RAG service"""
        try:
            return {
                'status': 'healthy' if self.is_initialized else 'unhealthy',
                'initialized': self.is_initialized,
                'knowledge_base_size': len(self.knowledge_base),
                'vector_store_path': str(self.vector_store_path),
                'gemini_service_available': self.gemini_service is not None and self.gemini_service.is_initialized
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'initialized': False
            }
    
    async def get_vector_store_stats(self) -> Dict[str, Any]:
        """Get vector store statistics"""
        try:
            if not self.knowledge_base:
                return {'total_documents': 0}
            
            # Count documents by category
            categories = {}
            for doc in self.knowledge_base:
                category = doc.get('category', 'unknown')
                categories[category] = categories.get(category, 0) + 1
            
            return {
                'total_documents': len(self.knowledge_base),
                'categories': categories,
                'vector_store_path': str(self.vector_store_path),
                'status': 'operational'
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting vector store stats: {e}")
            return {'total_documents': 0, 'error': str(e)}