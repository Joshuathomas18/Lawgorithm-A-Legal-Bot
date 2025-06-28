import json
import numpy as np
import requests
from typing import List, Dict, Any, Optional
import logging
import time
import hashlib
import pickle
import os
from functools import lru_cache
import faiss
from sentence_transformers import SentenceTransformer

class OptimizedLawgorithmRAGInterface:
    def __init__(self, vector_store_path: str, ollama_url: str = "http://localhost:11434", 
                 cache_dir: str = "rag_cache", use_faiss: bool = True):
        self.ollama_url = ollama_url
        self.model_name = "lawgorithm:latest"
        self.cache_dir = cache_dir
        self.use_faiss = use_faiss
        
        # Create cache directory
        os.makedirs(cache_dir, exist_ok=True)
        
        # Initialize embedding model for faster local embeddings
        try:
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            self.use_local_embeddings = True
            logging.info("Using local SentenceTransformer for embeddings")
        except Exception as e:
            self.use_local_embeddings = False
            logging.warning(f"Could not load SentenceTransformer: {e}. Using Ollama embeddings.")
        
        # Load and optimize vector store
        self.load_and_optimize_vector_store(vector_store_path)
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Test LLM connection
        self.test_llm_connection()
    
    def load_and_optimize_vector_store(self, vector_store_path: str):
        """Load vector store and optimize with FAISS HNSW indexing"""
        self.logger.info("Loading vector store...")
        
        with open(vector_store_path, 'r', encoding='utf-8') as f:
            self.vector_store = json.load(f)
        
        self.embeddings = np.array(self.vector_store['embeddings']).astype('float32')
        self.documents = self.vector_store['documents']
        self.metadatas = self.vector_store['metadatas']
        
        self.logger.info(f"Loaded {len(self.documents)} documents")
        
        if self.use_faiss and len(self.embeddings) > 100:  # Only use FAISS for larger datasets
            self.build_faiss_index()
        else:
            self.faiss_index = None
            self.logger.info("Using numpy-based search (small dataset)")
    
    def build_faiss_index(self):
        """Build optimized FAISS HNSW index for fast retrieval"""
        self.logger.info("Building FAISS HNSW index...")
        
        dimension = self.embeddings.shape[1]
        
        # Use HNSW index for fast approximate search
        # M=32: number of connections per layer (higher = more accurate but slower)
        # efConstruction=200: higher = more accurate index construction
        self.faiss_index = faiss.IndexHNSWFlat(dimension, 32)
        self.faiss_index.hnsw.efConstruction = 200
        self.faiss_index.hnsw.efSearch = 50  # Search time vs accuracy trade-off
        
        # Normalize vectors for cosine similarity
        faiss.normalize_L2(self.embeddings)
        self.faiss_index.add(self.embeddings)
        
        self.logger.info(f"Built FAISS HNSW index with {self.faiss_index.ntotal} vectors")
    
    def test_llm_connection(self):
        """Test if the LLM is accessible"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                model_names = [model['name'] for model in models]
                if self.model_name in model_names:
                    self.logger.info("✅ LLM connection successful")
                    return True
                else:
                    self.logger.warning(f"Model {self.model_name} not found. Available: {model_names}")
                    return False
            else:
                self.logger.error(f"LLM connection failed: {response.status_code}")
                return False
        except Exception as e:
            self.logger.error(f"LLM connection error: {e}")
            return False
    
    @lru_cache(maxsize=1000)
    def get_embedding_cached(self, text: str) -> List[float]:
        """Get embedding with caching for repeated queries"""
        # Create cache key
        cache_key = hashlib.md5(text.encode()).hexdigest()
        cache_file = os.path.join(self.cache_dir, f"embedding_{cache_key}.pkl")
        
        # Check cache first
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'rb') as f:
                    return pickle.load(f)
            except:
                pass
        
        # Generate embedding
        if self.use_local_embeddings:
            embedding = self.get_local_embedding(text)
        else:
            embedding = self.get_ollama_embedding(text)
        
        # Cache the result
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(embedding, f)
        except:
            pass
        
        return embedding
    
    def get_local_embedding(self, text: str) -> List[float]:
        """Get embedding using local SentenceTransformer"""
        try:
            embedding = self.embedding_model.encode([text])[0]
            return embedding.tolist()
        except Exception as e:
            self.logger.warning(f"Local embedding failed: {e}. Falling back to Ollama.")
            return self.get_ollama_embedding(text)
    
    def get_ollama_embedding(self, text: str) -> List[float]:
        """Get embedding using Ollama"""
        try:
            # Try nomic-embed-text first (faster, more reliable)
            response = requests.post(
                f"{self.ollama_url}/api/embeddings",
                json={"model": "nomic-embed-text", "prompt": text},
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()['embedding']
            
            # Fallback to lawgorithm model
            response = requests.post(
                f"{self.ollama_url}/api/embeddings",
                json={"model": self.model_name, "prompt": text},
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()['embedding']
            else:
                return self.create_fallback_embedding(text)
                
        except Exception as e:
            self.logger.warning(f"Ollama embedding failed: {e}")
            return self.create_fallback_embedding(text)
    
    def create_fallback_embedding(self, text: str) -> List[float]:
        """Create a simple fallback embedding"""
        hash_obj = hashlib.md5(text.encode())
        hash_bytes = hash_obj.digest()
        
        expected_dim = self.embeddings.shape[1] if hasattr(self, 'embeddings') and self.embeddings.size > 0 else 384
        
        embedding = []
        for i in range(expected_dim):
            embedding.append(float(hash_bytes[i % 16]) / 255.0)
        
        return embedding
    
    def search_similar_optimized(self, query: str, top_k: int = 5) -> List[Dict]:
        """Optimized search using FAISS HNSW or numpy"""
        start_time = time.time()
        
        # Get query embedding
        query_embedding = np.array(self.get_embedding_cached(query), dtype='float32')
        
        # Handle dimension mismatch
        if len(query_embedding) != self.embeddings.shape[1]:
            if len(query_embedding) < self.embeddings.shape[1]:
                padding = np.zeros(self.embeddings.shape[1] - len(query_embedding), dtype='float32')
                query_embedding = np.concatenate([query_embedding, padding])
            else:
                query_embedding = query_embedding[:self.embeddings.shape[1]]
        
        # Normalize query for cosine similarity
        query_norm = np.linalg.norm(query_embedding)
        if query_norm > 0:
            query_embedding = query_embedding / query_norm
        
        # Search using FAISS or numpy
        if self.faiss_index is not None:
            # FAISS search (much faster)
            scores, indices = self.faiss_index.search(query_embedding.reshape(1, -1), top_k)
            similarities = scores[0]
            top_indices = indices[0]
        else:
            # Numpy search (for small datasets)
            similarities = np.dot(self.embeddings, query_embedding)
            top_indices = np.argsort(similarities)[::-1][:top_k]
            similarities = similarities[top_indices]
        
        # Build results
        results = []
        for i, (idx, similarity) in enumerate(zip(top_indices, similarities)):
            if idx < len(self.documents):
                results.append({
                    'document': self.documents[idx],
                    'metadata': self.metadatas[idx],
                    'similarity': float(similarity),
                    'rank': i + 1
                })
        
        search_time = time.time() - start_time
        self.logger.info(f"Search completed in {search_time:.3f}s, found {len(results)} results")
        
        return results
    
    @lru_cache(maxsize=100)
    def generate_response_cached(self, query_hash: str, context_hash: str) -> str:
        """Generate response with caching"""
        # Reconstruct original query and context from hashes
        # This is a simplified approach - in production, you'd want a more sophisticated cache
        return self.generate_response(query_hash, context_hash)
    
    def generate_response(self, query: str, context: str) -> str:
        """Generate response using lawgorithm model"""
        try:
            prompt = f"""
You are writing a legal petition. Use the following petition structure as a template and fill in the content based on the case details provided.

PETITION TEMPLATE FROM LEGAL DOCUMENTS:
{context}

CASE DETAILS TO FILL INTO THE TEMPLATE:
{query}

INSTRUCTIONS:
1. Use the structure and format from the legal documents above as your template
2. Fill in the content using the case details provided
3. Maintain the same sections, headings, and formatting style
4. Only change the content, not the structure
5. Use proper legal language and terminology

Write the complete petition following the template structure but with your case details.
"""

            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,  # Reduced for more consistent output
                        "top_p": 0.9,
                        "top_k": 40,
                        "max_tokens": 1200,  # Reduced for faster generation
                        "repeat_penalty": 1.1
                    }
                },
                timeout=60  # Reduced timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get('response', 'No response generated')
                
                if "I am a large language model, trained by Google" in response_text:
                    return "I apologize, but I'm experiencing technical difficulties with my legal knowledge base. Please try again."
                
                return response_text
            else:
                return f"Sorry, I couldn't generate a response. Error: {response.status_code}"
                
        except Exception as e:
            return f"Sorry, there was an error generating the response: {str(e)}"
    
    def query(self, question: str, top_k: int = 3) -> Dict[str, Any]:
        """Optimized main query interface"""
        start_time = time.time()
        
        # Search for relevant documents
        similar_docs = self.search_similar_optimized(question, top_k)
        
        # Combine context efficiently
        contexts = []
        for doc in similar_docs:
            # Limit context length for faster processing
            doc_text = doc['document'][:1500] if len(doc['document']) > 1500 else doc['document']
            contexts.append(doc_text)
        
        context = "\n\n".join(contexts)
        
        # Generate response
        response = self.generate_response(question, context)
        
        total_time = time.time() - start_time
        
        return {
            'question': question,
            'response': response,
            'context_sources': similar_docs,
            'total_sources': len(similar_docs),
            'search_time': total_time,
            'cache_hits': getattr(self.get_embedding_cached, 'cache_info', lambda: None)()
        }

# Usage example
if __name__ == "__main__":
    rag = OptimizedLawgorithmRAGInterface("vector_store_lawgorithm/vector_store.json")
    
    # Test query
    result = rag.query("What are the key legal principles for granting bail in criminal cases?")
    print("Question:", result['question'])
    print("Response:", result['response'][:200] + "...")
    print("Sources used:", result['total_sources'])
    print("Total time:", result['search_time']) 