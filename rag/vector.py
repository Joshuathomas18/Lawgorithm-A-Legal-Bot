"""
Vector Store Module for Petition RAG System
===========================================

This module handles all vector operations including:
- Loading and managing vector embeddings
- Similarity search using cosine similarity
- Embedding generation and storage
- Vector database operations
"""

import json
import numpy as np
import requests
import hashlib
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

class VectorStore:
    """
    Vector store for legal document embeddings.
    
    This class manages the vector database of legal documents,
    providing similarity search capabilities for RAG operations.
    """
    
    def __init__(self, vector_store_path: str, ollama_url: str = "http://localhost:11434"):
        """
        Initialize the vector store.
        
        Args:
            vector_store_path: Path to the vector store JSON file
            ollama_url: URL for Ollama API
        """
        self.vector_store_path = vector_store_path
        self.ollama_url = ollama_url
        self.model_name = "lawgorithm:latest"
        
        # Initialize logging
        self.logger = logging.getLogger(__name__)
        
        # Load vector store data
        self.vector_store = self._load_vector_store()
        self.embeddings = np.array(self.vector_store.get('embeddings', []))
        self.documents = self.vector_store.get('documents', [])
        self.metadatas = self.vector_store.get('metadatas', [])
        
        self.logger.info(f"✅ Vector store loaded: {len(self.documents)} documents")
    
    def _load_vector_store(self) -> Dict[str, Any]:
        """Load vector store from JSON file."""
        try:
            with open(self.vector_store_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.logger.info(f"📁 Loaded vector store from {self.vector_store_path}")
            return data
        except FileNotFoundError:
            self.logger.warning(f"⚠️ Vector store not found at {self.vector_store_path}")
            return {'embeddings': [], 'documents': [], 'metadatas': []}
        except Exception as e:
            self.logger.error(f"❌ Error loading vector store: {e}")
            return {'embeddings': [], 'documents': [], 'metadatas': []}
    
    def get_embedding(self, text: str) -> List[float]:
        """
        Get embedding for a text using Ollama API.
        
        Args:
            text: Input text to embed
            
        Returns:
            List of embedding values
        """
        try:
            # Try using Ollama embedding API
            response = requests.post(
                f"{self.ollama_url}/api/embeddings",
                json={"model": self.model_name, "prompt": text},
                timeout=30
            )
            
            if response.status_code == 200:
                embedding = response.json()['embedding']
                self.logger.debug(f"✅ Got embedding of length: {len(embedding)}")
                return embedding
            else:
                self.logger.warning(f"⚠️ Embedding API failed ({response.status_code}), using fallback")
                return self._create_fallback_embedding(text)
                
        except Exception as e:
            self.logger.warning(f"⚠️ Embedding error: {e}, using fallback")
            return self._create_fallback_embedding(text)
    
    def _create_fallback_embedding(self, text: str) -> List[float]:
        """
        Create a simple fallback embedding when the model doesn't support embeddings.
        
        Args:
            text: Input text
            
        Returns:
            List of embedding values
        """
        # Simple hash-based embedding for fallback
        hash_obj = hashlib.md5(text.encode())
        hash_bytes = hash_obj.digest()
        
        # Convert to 4096-dimensional vector
        embedding = []
        for i in range(4096):
            embedding.append(float(hash_bytes[i % 16]) / 255.0)
        
        return embedding
    
    def search_similar(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for similar documents using cosine similarity.
        
        Args:
            query: Search query
            top_k: Number of top results to return
            
        Returns:
            List of similar documents with metadata and similarity scores
        """
        if len(self.embeddings) == 0:
            self.logger.warning("⚠️ No embeddings available for search")
            return []
        
        try:
            # Get query embedding
            query_embedding = np.array(self.get_embedding(query))
            
            # Handle zero vectors to avoid division by zero
            query_norm = np.linalg.norm(query_embedding)
            if query_norm == 0:
                query_embedding = np.random.rand(4096)  # Random fallback
                query_norm = np.linalg.norm(query_embedding)
            
            # Calculate cosine similarities safely
            doc_norms = np.linalg.norm(self.embeddings, axis=1)
            doc_norms = np.where(doc_norms == 0, 1e-8, doc_norms)  # Avoid division by zero
            
            similarities = np.dot(self.embeddings, query_embedding) / (doc_norms * query_norm)
            
            # Get top-k similar documents
            top_indices = np.argsort(similarities)[::-1][:top_k]
            
            results = []
            for idx in top_indices:
                results.append({
                    'document': self.documents[idx],
                    'metadata': self.metadatas[idx],
                    'similarity': float(similarities[idx])
                })
            
            self.logger.info(f"🔍 Found {len(results)} similar documents")
            return results
            
        except Exception as e:
            self.logger.error(f"❌ Error in similarity search: {e}")
            return []
    
    def add_documents(self, documents: List[Dict[str, Any]]) -> bool:
        """
        Add new documents to the vector store.
        
        Args:
            documents: List of documents with 'text' and 'metadata' keys
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Extract texts and metadata
            texts = [doc['text'] for doc in documents]
            metadatas = [doc['metadata'] for doc in documents]
            
            # Generate embeddings
            embeddings = []
            for text in texts:
                embedding = self.get_embedding(text)
                embeddings.append(embedding)
            
            # Add to existing data
            self.documents.extend(texts)
            self.metadatas.extend(metadatas)
            self.embeddings = np.vstack([self.embeddings, np.array(embeddings)]) if len(self.embeddings) > 0 else np.array(embeddings)
            
            # Save updated vector store
            self._save_vector_store()
            
            self.logger.info(f"✅ Added {len(documents)} documents to vector store")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error adding documents: {e}")
            return False
    
    def _save_vector_store(self):
        """Save vector store to JSON file."""
        try:
            vector_store_data = {
                'embeddings': self.embeddings.tolist(),
                'documents': self.documents,
                'metadatas': self.metadatas,
                'updated_at': datetime.now().isoformat(),
                'total_documents': len(self.documents)
            }
            
            with open(self.vector_store_path, 'w', encoding='utf-8') as f:
                json.dump(vector_store_data, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"💾 Vector store saved to {self.vector_store_path}")
            
        except Exception as e:
            self.logger.error(f"❌ Error saving vector store: {e}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the vector store.
        
        Returns:
            Dictionary with vector store statistics
        """
        return {
            'total_documents': len(self.documents),
            'embedding_dimensions': self.embeddings.shape[1] if len(self.embeddings) > 0 else 0,
            'vector_store_path': self.vector_store_path,
            'last_updated': self.vector_store.get('updated_at', 'Unknown'),
            'model_used': self.model_name
        }
    
    def clear(self):
        """Clear all documents from the vector store."""
        self.embeddings = np.array([])
        self.documents = []
        self.metadatas = []
        self._save_vector_store()
        self.logger.info("🗑️ Vector store cleared")
    
    def test_connection(self) -> bool:
        """
        Test connection to Ollama API.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                model_names = [model['name'] for model in models]
                if self.model_name in model_names:
                    self.logger.info(f"✅ Ollama connection successful, {self.model_name} available")
                    return True
                else:
                    self.logger.warning(f"⚠️ {self.model_name} not found. Available: {model_names}")
                    return False
            else:
                self.logger.error("❌ Cannot connect to Ollama")
                return False
        except Exception as e:
            self.logger.error(f"❌ Error testing Ollama connection: {e}")
            return False

# Example usage
if __name__ == "__main__":
    # Test vector store
    vector_store = VectorStore("rag/vector_store_lawgorithm/vector_store.json")
    
    # Test search
    results = vector_store.search_similar("bail in criminal cases", top_k=3)
    print(f"Found {len(results)} results")
    
    # Print statistics
    stats = vector_store.get_statistics()
    print(f"Vector store statistics: {stats}") 