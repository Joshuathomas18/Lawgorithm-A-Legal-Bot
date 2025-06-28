"""
RAG + Ollama Integration Package
===============================

Clean integration of RAG system with Ollama for legal petition generation.
"""

from .main import LegalRAGAgent
from .vector_store import VectorStore
from .ollama_client import OllamaClient

__version__ = "1.0.0"
__author__ = "Legal RAG System"

__all__ = [
    "LegalRAGAgent",
    "VectorStore", 
    "OllamaClient"
] 