import json
import numpy as np
import requests
from typing import List, Dict, Any
import logging
import time

class LawgorithmRAGInterface:
    def __init__(self, vector_store_path: str, ollama_url: str = "http://localhost:11434"):
        self.ollama_url = ollama_url
        self.model_name = "lawgorithm:latest"
        
        # Load vector store
        with open(vector_store_path, 'r', encoding='utf-8') as f:
            self.vector_store = json.load(f)
        
        self.embeddings = np.array(self.vector_store['embeddings'])
        self.documents = self.vector_store['documents']
        self.metadatas = self.vector_store['metadatas']
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Test LLM connection
        self.test_llm_connection()
    
    def test_llm_connection(self):
        """Test if the LLM is accessible"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                model_names = [model['name'] for model in models]
                if self.model_name in model_names:
                    return True
                else:
                    return False
            else:
                return False
        except Exception as e:
            return False
    
    def get_embedding(self, text: str) -> List[float]:
        """Get embedding for a text using Ollama"""
        try:
            # Use a simpler embedding model that's more reliable
            response = requests.post(
                f"{self.ollama_url}/api/embeddings",
                json={"model": "nomic-embed-text", "prompt": text},
                timeout=30
            )
            
            if response.status_code == 200:
                embedding = response.json()['embedding']
                return embedding
            else:
                # Try with lawgorithm model directly
                response = requests.post(
                    f"{self.ollama_url}/api/embeddings",
                    json={"model": self.model_name, "prompt": text},
                    timeout=30
                )
                
                if response.status_code == 200:
                    embedding = response.json()['embedding']
                    return embedding
                else:
                    return self.create_fallback_embedding(text)
                
        except Exception as e:
            return self.create_fallback_embedding(text)
    
    def create_fallback_embedding(self, text: str) -> List[float]:
        """Create a simple fallback embedding when the model doesn't support embeddings"""
        # Simple hash-based embedding for fallback
        import hashlib
        hash_obj = hashlib.md5(text.encode())
        hash_bytes = hash_obj.digest()
        
        # Get the expected dimension from the vector store
        expected_dim = self.embeddings.shape[1] if hasattr(self, 'embeddings') and self.embeddings.size > 0 else 4096
        
        # Convert to expected-dimensional vector
        embedding = []
        for i in range(expected_dim):
            embedding.append(float(hash_bytes[i % 16]) / 255.0)
        
        return embedding
    
    def search_similar(self, query: str, top_k: int = 5) -> List[Dict]:
        """Search for similar documents"""
        query_embedding = np.array(self.get_embedding(query))
        
        # Handle dimension mismatch
        if len(query_embedding) != self.embeddings.shape[1]:
            # Resize query embedding to match store dimensions
            if len(query_embedding) < self.embeddings.shape[1]:
                # Pad with zeros
                padding = np.zeros(self.embeddings.shape[1] - len(query_embedding))
                query_embedding = np.concatenate([query_embedding, padding])
            else:
                # Truncate
                query_embedding = query_embedding[:self.embeddings.shape[1]]
        
        # Handle zero vectors to avoid division by zero
        query_norm = np.linalg.norm(query_embedding)
        if query_norm == 0:
            query_embedding = np.random.rand(self.embeddings.shape[1])  # Random fallback
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
        
        return results
    
    def generate_response(self, query: str, context: str) -> str:
        """Generate response using lawgorithm model"""
        try:
            # Create a better prompt structure for petition generation
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
                        "temperature": 0.9,
                        "top_p": 0.95,
                        "top_k": 50,
                        "max_tokens": 1500,
                        "repeat_penalty": 1.1
                    }
                },
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get('response', 'No response generated')
                
                # Verify it's actually from Lawgorithm
                if "I am a large language model, trained by Google" in response_text:
                    return "I apologize, but I'm experiencing technical difficulties with my legal knowledge base. Please try again."
                
                return response_text
            else:
                return f"Sorry, I couldn't generate a response. Error: {response.status_code}"
                
        except Exception as e:
            return f"Sorry, there was an error generating the response: {str(e)}"
    
    def query(self, question: str, top_k: int = 2) -> Dict[str, Any]:
        """Main query interface"""
        # Search for relevant documents
        similar_docs = self.search_similar(question, top_k)
        
        # Combine context from similar documents (increase length for better structure)
        contexts = []
        for doc in similar_docs:
            # Increase limit to 2000 characters to get more complete petition structure
            doc_text = doc['document'][:2000] if len(doc['document']) > 2000 else doc['document']
            contexts.append(doc_text)
        
        context = "\n\n".join(contexts)
        
        # Generate response using LLM
        response = self.generate_response(question, context)
        
        return {
            'question': question,
            'response': response,
            'context_sources': similar_docs,
            'total_sources': len(similar_docs)
        }

# Usage example
if __name__ == "__main__":
    rag = LawgorithmRAGInterface("rag/vector_store_lawgorithm/vector_store.json")
    
    # Test query
    result = rag.query("What are the key legal principles for granting bail in criminal cases?")
    print("Question:", result['question'])
    print("Response:", result['response'])
    print("Sources used:", result['total_sources'])
