#!/usr/bin/env python3
"""
Legal RAG Agent
===============

Main agent that combines vector store and Ollama client.
Based on LocalAIAgentWithRAG agent implementation.
"""

import logging
from typing import Dict, List, Any
from .vector_store import LegalVectorStore
from .ollama_client import OllamaClient

logger = logging.getLogger(__name__)

class LegalRAGAgent:
    def __init__(self, indexes_dir: str = "rag_ready/dual_rag_indexes", 
                 ollama_url: str = "http://localhost:11434",
                 model: str = "lawgorithm:latest"):
        """Initialize the Legal RAG Agent"""
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        
        # Initialize components
        self.vector_store = LegalVectorStore(indexes_dir)
        self.ollama_client = OllamaClient(ollama_url, model)
        
        # Test connections
        self._test_connections()
        
    def _test_connections(self):
        """Test all connections"""
        logger.info("Testing connections...")
        
        # Test vector store
        stats = self.vector_store.get_stats()
        logger.info(f"Vector store loaded: {stats['content_documents']} content docs, {stats['structure_documents']} structure docs")
        
        # Test Ollama
        if self.ollama_client.test_connection():
            model_info = self.ollama_client.get_model_info()
            logger.info(f"Ollama connected: {model_info.get('name', 'Unknown model')}")
        else:
            logger.error("❌ Ollama connection failed!")
    
    def query(self, question: str, top_k: int = 5) -> Dict[str, Any]:
        """Main query method - search and generate response"""
        logger.info(f"Processing query: {question}")
        
        # Step 1: Search for relevant documents
        search_results = self.vector_store.dual_search(question, top_k)
        
        # Step 2: Prepare context from search results
        context = self._prepare_context(search_results)
        
        # Step 3: Generate response using Ollama
        response = self.ollama_client.generate(question, context)
        
        # Step 4: Return comprehensive results
        return {
            'question': question,
            'response': response,
            'context': context,
            'search_results': search_results,
            'stats': {
                'structure_results': len(search_results['structure']),
                'content_results': len(search_results['content'])
            }
        }
    
    def _prepare_context(self, search_results: Dict[str, List[Dict]]) -> str:
        """Prepare context from search results"""
        context_parts = []
        
        # Add structure context
        if search_results['structure']:
            context_parts.append("=== STRUCTURE INFORMATION ===")
            for i, result in enumerate(search_results['structure'][:3]):  # Top 3
                context_parts.append(f"Structure {i+1}: {result['document']}")
        
        # Add content context
        if search_results['content']:
            context_parts.append("\n=== CONTENT INFORMATION ===")
            for i, result in enumerate(search_results['content'][:5]):  # Top 5
                context_parts.append(f"Content {i+1}: {result['document']}")
        
        return "\n".join(context_parts)
    
    def search_only(self, query: str, top_k: int = 5) -> Dict[str, List[Dict]]:
        """Search only without generating response"""
        return self.vector_store.dual_search(query, top_k)
    
    def generate_only(self, prompt: str, context: str = "") -> str:
        """Generate response only without searching"""
        return self.ollama_client.generate(prompt, context)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get system statistics"""
        vector_stats = self.vector_store.get_stats()
        model_info = self.ollama_client.get_model_info()
        
        return {
            'vector_store': vector_stats,
            'ollama_model': model_info,
            'total_documents': vector_stats['content_documents'] + vector_stats['structure_documents']
        } 