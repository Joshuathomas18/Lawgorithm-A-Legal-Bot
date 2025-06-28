#!/usr/bin/env python3
"""
Vector Store for Legal Documents
================================

Based on LocalAIAgentWithRAG vector store implementation.
Adapted to use existing trained FAISS indexes.
"""

import json
import numpy as np
import logging
import os
import faiss
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class LegalVectorStore:
    def __init__(self, indexes_dir: str = "rag_ready/dual_rag_indexes"):
        """Initialize vector store with existing trained indexes"""
        self.indexes_dir = indexes_dir
        
        # Initialize embedding models
        self.structure_encoder = SentenceTransformer('all-MiniLM-L6-v2')
        self.content_encoder = SentenceTransformer('all-mpnet-base-v2')
        
        # Load existing trained indexes
        self.load_trained_indexes()
        
    def load_trained_indexes(self):
        """Load existing trained FAISS indexes and documents"""
        logger.info("Loading trained dual RAG indexes...")
        
        # Load structure index
        structure_index_path = os.path.join(self.indexes_dir, "structure_index.faiss")
        if os.path.exists(structure_index_path):
            self.structure_index = faiss.read_index(structure_index_path)
            with open(os.path.join(self.indexes_dir, "structure_documents.json"), 'r', encoding='utf-8') as f:
                self.structure_documents = json.load(f)
            logger.info(f"Loaded structure index with {len(self.structure_documents)} documents")
        else:
            self.structure_index = None
            self.structure_documents = []
            logger.warning("Structure index not found")
        
        # Load content index
        content_index_path = os.path.join(self.indexes_dir, "content_index.faiss")
        if os.path.exists(content_index_path):
            self.content_index = faiss.read_index(content_index_path)
            with open(os.path.join(self.indexes_dir, "content_documents.json"), 'r', encoding='utf-8') as f:
                self.content_documents = json.load(f)
            logger.info(f"Loaded content index with {len(self.content_documents)} documents")
        else:
            self.content_index = None
            self.content_documents = []
            logger.warning("Content index not found")
        
        # Load metadata
        metadata_path = os.path.join(self.indexes_dir, "rag_metadata.json")
        if os.path.exists(metadata_path):
            with open(metadata_path, 'r') as f:
                self.metadata = json.load(f)
            logger.info(f"Loaded metadata: {self.metadata}")
        else:
            self.metadata = {}
    
    def search_structure(self, query: str, top_k: int = 5) -> List[Dict]:
        """Search structure documents"""
        if not self.structure_index:
            logger.warning("Structure index not loaded")
            return []
        
        # Generate query embedding
        query_embedding = self.structure_encoder.encode([query])
        
        # Normalize for cosine similarity
        faiss.normalize_L2(query_embedding)
        
        # Search
        scores, indices = self.structure_index.search(query_embedding, top_k)
        
        results = []
        for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
            if idx < len(self.structure_documents):
                doc = self.structure_documents[idx].copy()
                results.append({
                    'document': doc.get('text', ''),
                    'metadata': doc.get('metadata', {}),
                    'similarity': float(score),
                    'rank': i + 1
                })
        
        return results
    
    def search_content(self, query: str, top_k: int = 5) -> List[Dict]:
        """Search content documents"""
        if not self.content_index:
            logger.warning("Content index not loaded")
            return []
        
        # Generate query embedding
        query_embedding = self.content_encoder.encode([query])
        
        # Normalize for cosine similarity
        faiss.normalize_L2(query_embedding)
        
        # Search
        scores, indices = self.content_index.search(query_embedding, top_k)
        
        results = []
        for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
            if idx < len(self.content_documents):
                doc = self.content_documents[idx].copy()
                results.append({
                    'document': doc.get('text', ''),
                    'metadata': doc.get('metadata', {}),
                    'similarity': float(score),
                    'rank': i + 1
                })
        
        return results
    
    def dual_search(self, query: str, top_k: int = 5) -> Dict[str, List[Dict]]:
        """Perform dual search on both structure and content"""
        structure_results = self.search_structure(query, top_k)
        content_results = self.search_content(query, top_k)
        
        return {
            'structure': structure_results,
            'content': content_results
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get vector store statistics"""
        return {
            'structure_documents': len(self.structure_documents),
            'content_documents': len(self.content_documents),
            'metadata': self.metadata,
            'indexes_dir': self.indexes_dir
        } 