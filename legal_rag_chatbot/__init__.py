#!/usr/bin/env python3
"""
Legal RAG Chatbot Package
=========================

A structured RAG system for legal document analysis using trained FAISS indexes and Ollama.
Based on LocalAIAgentWithRAG architecture.
"""

from .rag_agent import LegalRAGAgent
from .vector_store import LegalVectorStore
from .ollama_client import OllamaClient

__version__ = "1.0.0"
__author__ = "Legal RAG Team"

__all__ = [
    'LegalRAGAgent',
    'LegalVectorStore', 
    'OllamaClient'
] 