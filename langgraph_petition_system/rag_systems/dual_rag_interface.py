"""
Dual RAG Interface for LangGraph Petition System
===============================================

Integrates with the trained dual RAG system for legal document retrieval.
"""

import os
import sys
import json
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path

# Add the rag_ready directory to path to import the trained RAG system
sys.path.append(str(Path(__file__).parent.parent.parent / "rag_ready"))
from optimized_dual_rag_interface import OptimizedDualRAGInterface

from langgraph_petition_system.config import Jurisdiction, PetitionType

logger = logging.getLogger(__name__)

class DualRAGInterface:
    """Dual RAG interface for LangGraph petition system"""
    
    def __init__(self, indexes_dir: str = None):
        """Initialize the dual RAG interface"""
        if indexes_dir is None:
            # Use the trained RAG indexes
            indexes_dir = str(Path(__file__).parent.parent.parent / "rag_ready" / "dual_rag_indexes")
        
        self.indexes_dir = indexes_dir
        self.rag_interface = OptimizedDualRAGInterface(indexes_dir)
        
        logger.info(f"Initialized Dual RAG Interface with indexes from: {indexes_dir}")
    
    def retrieve_dual_context(self, query: str, jurisdiction: Jurisdiction, 
                            petition_type: PetitionType, top_k: int = 5) -> Dict[str, Any]:
        """
        Retrieve context from both structure and content RAG systems
        
        Args:
            query: Search query
            jurisdiction: Legal jurisdiction
            petition_type: Type of petition
            top_k: Number of top results to retrieve
            
        Returns:
            Dictionary with structure_chunks and content_chunks
        """
        try:
            # Enhance query with jurisdiction and petition type context
            enhanced_query = self._enhance_query(query, jurisdiction, petition_type)
            
            # Perform dual search
            search_results = self.rag_interface.dual_search(enhanced_query, k=top_k)
            
            # Extract and format chunks
            structure_chunks = self._format_structure_chunks(search_results.get('structure', []))
            content_chunks = self._format_content_chunks(search_results.get('content', []))
            
            return {
                'structure_chunks': structure_chunks,
                'content_chunks': content_chunks,
                'search_time': search_results.get('search_time', 0),
                'query': enhanced_query
            }
            
        except Exception as e:
            logger.error(f"Error in dual RAG retrieval: {e}")
            return {
                'structure_chunks': [],
                'content_chunks': [],
                'search_time': 0,
                'error': str(e)
            }
    
    def _enhance_query(self, query: str, jurisdiction: Jurisdiction, 
                      petition_type: PetitionType) -> str:
        """Enhance query with jurisdiction and petition type context"""
        enhanced = f"{query} jurisdiction:{jurisdiction.value} petition_type:{petition_type.value}"
        return enhanced
    
    def _format_structure_chunks(self, structure_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format structure search results into chunks"""
        chunks = []
        for result in structure_results:
            chunk = {
                'docid': result.get('docid', ''),
                'title': result.get('title', ''),
                'court': result.get('court', ''),
                'date': result.get('date', ''),
                'citations': result.get('citations', []),
                'cited_by': result.get('cited_by', []),
                'docsize': result.get('docsize', 0),
                'score': result.get('score', 0.0),
                'rank': result.get('rank', 0),
                'chunk_type': 'structure'
            }
            chunks.append(chunk)
        return chunks
    
    def _format_content_chunks(self, content_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format content search results into chunks"""
        chunks = []
        for result in content_results:
            sections = result.get('sections', {})
            chunk = {
                'docid': result.get('docid', ''),
                'title': result.get('title', ''),
                'facts': sections.get('facts', ''),
                'arguments': sections.get('arguments', ''),
                'judgment': sections.get('judgment', ''),
                'relief': sections.get('relief', ''),
                'full_content': sections.get('full_content', ''),
                'keywords': result.get('keywords', []),
                'score': result.get('score', 0.0),
                'rank': result.get('rank', 0),
                'chunk_type': 'content'
            }
            chunks.append(chunk)
        return chunks
    
    def generate_petition_with_rag(self, query: str, structure_context: str, 
                                 content_context: str) -> str:
        """Generate petition using the trained RAG system"""
        try:
            return self.rag_interface.generate_response(query, structure_context, content_context)
        except Exception as e:
            logger.error(f"Error generating petition with RAG: {e}")
            return f"Error generating petition: {str(e)}"
    
    def test_connection(self) -> bool:
        """Test if the RAG system is working properly"""
        try:
            # Test with a simple query
            test_query = "contract dispute"
            results = self.rag_interface.dual_search(test_query, k=1)
            
            structure_ok = len(results.get('structure', [])) > 0
            content_ok = len(results.get('content', [])) > 0
            
            logger.info(f"RAG connection test - Structure: {structure_ok}, Content: {content_ok}")
            return structure_ok and content_ok
            
        except Exception as e:
            logger.error(f"RAG connection test failed: {e}")
            return False 