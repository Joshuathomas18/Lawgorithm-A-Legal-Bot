#!/usr/bin/env python3
"""
RAG Service
===========

Service for handling RAG operations with the trained dual RAG system using Gemini.
"""

import json
import logging
import sys
import os
from typing import List, Dict, Any, Optional
import numpy as np
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import the new Gemini-powered dual RAG system
# from rag_ready.optimized_dual_rag_interface_v2 import OptimizedDualRAGInterfaceV2
# Import the comprehensive chatbot
from comprehensive_gemini_rag_chatbot import ComprehensiveGeminiRAGChatbot

logger = logging.getLogger(__name__)

class RAGService:
    def __init__(self, indexes_dir: str = None, gemini_service = None):
        if indexes_dir is None:
            # Use the trained RAG indexes
            indexes_dir = str(Path(__file__).parent.parent.parent / "rag_ready" / "dual_rag_indexes")
        
        self.indexes_dir = indexes_dir
        self.gemini_service = gemini_service
        self.is_initialized = True
        
    async def initialize(self):
        # No-op for now
        self.is_initialized = True
    
    async def test_connection(self) -> bool:
        return True
    
    async def search_legal_context(self, query: str, top_k: int = 5) -> dict:
        # Return mock search results
        return {
            'structure_results': [{'title': 'Mock Structure', 'court': 'Supreme Court', 'date': '2022-01-01'}],
            'content_results': [{'title': 'Mock Content', 'sections': {'facts': 'Mock facts', 'arguments': 'Mock arguments', 'judgment': 'Mock judgment'}}],
            'search_time': 0.01
        }
    
    async def generate_legal_response(self, query: str, context: str = "") -> str:
        return f"[MOCK LEGAL RESPONSE] You asked: {query}"
    
    def _extract_structure_context(self, structure_results: List[Dict[str, Any]]) -> str:
        """Extract structure context from search results"""
        context_parts = []
        for result in structure_results:
            context_parts.append(f"Title: {result.get('title', '')}")
            context_parts.append(f"Court: {result.get('court', '')}")
            context_parts.append(f"Date: {result.get('date', '')}")
            if result.get('citations'):
                context_parts.append(f"Citations: {', '.join(result.get('citations', []))}")
        
        return "\n".join(context_parts)
    
    def _extract_content_context(self, content_results: List[Dict[str, Any]]) -> str:
        """Extract content context from search results"""
        context_parts = []
        for result in content_results:
            sections = result.get('sections', {})
            if sections.get('facts'):
                context_parts.append(f"Facts: {sections['facts'][:500]}...")
            if sections.get('arguments'):
                context_parts.append(f"Arguments: {sections['arguments'][:500]}...")
            if sections.get('judgment'):
                context_parts.append(f"Judgment: {sections['judgment'][:500]}...")
        
        return "\n".join(context_parts)
    
    async def get_legal_precedents(self, case_type: str, court: str, keywords: list) -> dict:
        return {
            'structure_precedents': [{'title': 'Mock Precedent', 'court': court, 'date': '2022-01-01'}],
            'content_precedents': [{'title': 'Mock Content', 'sections': {'facts': 'Mock facts', 'arguments': 'Mock arguments', 'judgment': 'Mock judgment'}}],
            'search_time': 0.01
        }
    
    async def get_vector_store_stats(self) -> dict:
        return {
            'status': 'healthy',
            'initialized': self.is_initialized,
            'indexes_dir': self.indexes_dir,
            'metadata': {},
            'total_documents': 1,
            'structure_documents': 1,
            'content_documents': 1,
            'performance_stats': {},
            'gpu_info': {}
        }
    
    async def health_check(self) -> dict:
        return {
            'status': 'healthy',
            'initialized': self.is_initialized,
            'connected': True,
            'indexes_dir': self.indexes_dir,
            'total_documents': 1,
            'structure_documents': 1,
            'content_documents': 1,
            'performance_stats': {},
            'gpu_info': {}
        } 