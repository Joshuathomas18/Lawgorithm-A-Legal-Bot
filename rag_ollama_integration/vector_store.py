#!/usr/bin/env python3
"""
Vector Store for Legal Documents
================================

Based on LocalAIAgentWithRAG vector store implementation.
"""

import os
import json
import numpy as np
import logging
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class VectorStore:
    def __init__(self, vector_store_path: str):
        """Initialize vector store"""
        self.vector_store_path = vector_store_path
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Initialize attributes
        self.documents = []
        self.metadatas = []
        self.embeddings = np.array([])
        
        # Load or create vector store
        if os.path.exists(vector_store_path):
            self.load_vector_store()
        else:
            self.vector_store = {
                'embeddings': [],
                'documents': [],
                'metadatas': []
            }
            logger.info(f"Created new vector store at {vector_store_path}")
    
    def load_vector_store(self):
        """Load vector store from file"""
        try:
            with open(self.vector_store_path, 'r', encoding='utf-8') as f:
                self.vector_store = json.load(f)
            
            # Convert embeddings back to numpy array
            self.embeddings = np.array(self.vector_store['embeddings'])
            self.documents = self.vector_store['documents']
            self.metadatas = self.vector_store['metadatas']
            
            logger.info(f"Loaded vector store with {len(self.documents)} documents")
            
        except Exception as e:
            logger.error(f"Error loading vector store: {e}")
            self.vector_store = {
                'embeddings': [],
                'documents': [],
                'metadatas': []
            }
    
    def save_vector_store(self):
        """Save vector store to file"""
        try:
            # Convert numpy array to list for JSON serialization
            self.vector_store['embeddings'] = self.embeddings.tolist()
            self.vector_store['documents'] = self.documents
            self.vector_store['metadatas'] = self.metadatas
            
            # Ensure the directory exists
            os.makedirs(os.path.dirname(self.vector_store_path), exist_ok=True)
            
            with open(self.vector_store_path, 'w', encoding='utf-8') as f:
                json.dump(self.vector_store, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Saved vector store to {self.vector_store_path}")
            
        except Exception as e:
            logger.error(f"Error saving vector store: {e}")
    
    def add_documents(self, documents: List[str], metadatas: List[Dict] = None):
        """Add documents to vector store"""
        if not documents:
            return
        
        logger.info(f"Adding {len(documents)} documents to vector store...")
        
        # Generate embeddings
        embeddings = self.embedding_model.encode(documents, show_progress_bar=True)
        
        # Add to existing store
        if hasattr(self, 'embeddings') and len(self.embeddings) > 0:
            self.embeddings = np.vstack([self.embeddings, embeddings])
        else:
            self.embeddings = embeddings
        
        # Add documents and metadata
        self.documents.extend(documents)
        
        if metadatas:
            self.metadatas.extend(metadatas)
        else:
            self.metadatas.extend([{} for _ in documents])
        
        # Save to file
        self.save_vector_store()
        
        logger.info(f"Added {len(documents)} documents. Total: {len(self.documents)}")
    
    def search_similar(self, query: str, top_k: int = 5) -> List[Dict]:
        """Search for similar documents"""
        if not hasattr(self, 'embeddings') or len(self.embeddings) == 0:
            logger.warning("Vector store is empty")
            return []
        
        # Generate query embedding
        query_embedding = self.embedding_model.encode([query])
        
        # Calculate cosine similarities
        similarities = np.dot(self.embeddings, query_embedding.T).flatten()
        
        # Get top-k similar documents
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            results.append({
                'document': self.documents[idx],
                'metadata': self.metadatas[idx],
                'similarity': float(similarities[idx])
            })
        
        return results
    
    def get_stats(self) -> Dict[str, Any]:
        """Get vector store statistics"""
        embedding_dim = 0
        if hasattr(self, 'embeddings') and len(self.embeddings) > 0:
            if len(self.embeddings.shape) > 1:
                embedding_dim = self.embeddings.shape[1]
            else:
                embedding_dim = self.embeddings.shape[0]
        
        return {
            'total_documents': len(self.documents),
            'embedding_dimension': embedding_dim,
            'vector_store_path': self.vector_store_path
        } 