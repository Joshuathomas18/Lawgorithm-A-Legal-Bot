import json
import numpy as np
import requests
from typing import List, Dict, Any, Optional, Tuple
import logging
import time
import os
import faiss
import re
from sentence_transformers import SentenceTransformer
from functools import lru_cache
import concurrent.futures
import torch

class OptimizedDualRAGInterface:
    def __init__(self, indexes_dir: str, ollama_url: str = "http://localhost:11434", use_gpu: bool = True):
        # Initialize logging first
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        self.ollama_url = ollama_url
        self.model_name = "lawgorithm:latest"
        self.indexes_dir = indexes_dir
        self.use_gpu = use_gpu
        
        # Check GPU availability
        self.device = self._setup_device()
        self.logger.info(f"Using device: {self.device}")
        
        # Initialize embedding models with GPU support
        self.structure_encoder = SentenceTransformer('all-MiniLM-L6-v2', device=self.device)
        self.content_encoder = SentenceTransformer('all-mpnet-base-v2', device=self.device)
        
        # Performance optimizations
        self.query_cache = {}
        self.metadata_filters = {}
        
        # Load trained indexes
        self.load_indexes()
        self.build_filters()
        
        # Test LLM connection
        self.test_llm_connection()
    
    def _setup_device(self) -> str:
        """Setup GPU device if available"""
        if self.use_gpu and torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3  # GB
            self.logger.info(f"🎮 GPU detected: {gpu_name} ({gpu_memory:.1f}GB)")
            
            # Check if we have enough GPU memory
            if gpu_memory >= 4.0:  # RTX 2050 has 4GB
                self.logger.info("✅ GPU memory sufficient for RAG operations")
                return "cuda"
            else:
                self.logger.warning(f"⚠️ GPU memory ({gpu_memory:.1f}GB) may be insufficient, using CPU")
                return "cpu"
        else:
            if self.use_gpu:
                self.logger.warning("⚠️ GPU requested but CUDA not available, using CPU")
                self.logger.info("💡 To enable GPU acceleration, install PyTorch with CUDA support")
            else:
                self.logger.info("🖥️ Using CPU for RAG operations")
            return "cpu"
    
    def load_indexes(self):
        """Load the trained FAISS indexes and documents"""
        self.logger.info("Loading dual RAG indexes...")
        
        # Load structure index
        structure_index_path = os.path.join(self.indexes_dir, "structure_index.faiss")
        if os.path.exists(structure_index_path):
            self.structure_index = faiss.read_index(structure_index_path)
            
            # Move to GPU if available
            if self.device == "cuda":
                try:
                    self.structure_index = faiss.index_cpu_to_gpu(
                        faiss.StandardGpuResources(), 0, self.structure_index
                    )
                    self.logger.info("✅ Structure index moved to GPU")
                except Exception as e:
                    self.logger.warning(f"⚠️ Could not move structure index to GPU: {e}")
                    self.logger.info("🖥️ Using CPU FAISS index instead")
            else:
                self.logger.info("🖥️ Using CPU FAISS index for structure")
            
            with open(os.path.join(self.indexes_dir, "structure_documents.json"), 'r', encoding='utf-8') as f:
                self.structure_documents = json.load(f)
            self.logger.info(f"Loaded structure index with {len(self.structure_documents)} documents")
        else:
            self.structure_index = None
            self.structure_documents = []
            self.logger.warning("Structure index not found")
        
        # Load content index
        content_index_path = os.path.join(self.indexes_dir, "content_index.faiss")
        if os.path.exists(content_index_path):
            self.content_index = faiss.read_index(content_index_path)
            
            # Move to GPU if available
            if self.device == "cuda":
                try:
                    self.content_index = faiss.index_cpu_to_gpu(
                        faiss.StandardGpuResources(), 0, self.content_index
                    )
                    self.logger.info("✅ Content index moved to GPU")
                except Exception as e:
                    self.logger.warning(f"⚠️ Could not move content index to GPU: {e}")
                    self.logger.info("🖥️ Using CPU FAISS index instead")
            else:
                self.logger.info("🖥️ Using CPU FAISS index for content")
            
            with open(os.path.join(self.indexes_dir, "content_documents.json"), 'r', encoding='utf-8') as f:
                self.content_documents = json.load(f)
            self.logger.info(f"Loaded content index with {len(self.content_documents)} documents")
        else:
            self.content_index = None
            self.content_documents = []
            self.logger.warning("Content index not found")
        
        # Load metadata
        metadata_path = os.path.join(self.indexes_dir, "rag_metadata.json")
        if os.path.exists(metadata_path):
            with open(metadata_path, 'r') as f:
                self.metadata = json.load(f)
            self.logger.info(f"Loaded metadata: {self.metadata}")
        else:
            self.metadata = {}
    
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
    
    def search_structure(self, query: str, k: int = 3) -> List[Dict[str, Any]]:
        """Search structure RAG for legal structure information"""
        if self.structure_index is None:
            self.logger.error("Structure index not loaded")
            return []
        
        start_time = time.time()
        
        # Use cached embedding
        query_embedding = self.get_cached_embedding(query, 'structure')
        
        # Normalize for cosine similarity
        faiss.normalize_L2(query_embedding)
        
        # Search
        scores, indices = self.structure_index.search(query_embedding, k)
        
        # Build results
        results = []
        for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
            if idx < len(self.structure_documents):
                doc = self.structure_documents[idx].copy()
                doc['score'] = float(score)
                doc['rank'] = i + 1
                results.append(doc)
        
        search_time = time.time() - start_time
        self.logger.info(f"Structure search completed in {search_time:.3f}s")
        
        return results
    
    def search_content(self, query: str, k: int = 3) -> List[Dict[str, Any]]:
        """Search content RAG for legal content information"""
        if self.content_index is None:
            self.logger.error("Content index not loaded")
            return []
        
        start_time = time.time()
        
        # Use cached embedding
        query_embedding = self.get_cached_embedding(query, 'content')
        
        # Normalize for cosine similarity
        faiss.normalize_L2(query_embedding)
        
        # Search
        scores, indices = self.content_index.search(query_embedding, k)
        
        # Build results
        results = []
        for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
            if idx < len(self.content_documents):
                doc = self.content_documents[idx].copy()
                doc['score'] = float(score)
                doc['rank'] = i + 1
                results.append(doc)
        
        search_time = time.time() - start_time
        self.logger.info(f"Content search completed in {search_time:.3f}s")
        
        return results
    
    def dual_search(self, query: str, k: int = 3) -> Dict[str, List[Dict[str, Any]]]:
        """Perform dual RAG search - both structure and content"""
        start_time = time.time()
        
        # Search both indexes in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            structure_future = executor.submit(self.search_structure, query, k)
            content_future = executor.submit(self.search_content, query, k)
            
            structure_results = structure_future.result()
            content_results = content_future.result()
        
        total_time = time.time() - start_time
        self.logger.info(f"Dual search completed in {total_time:.3f}s")
        
        return {
            'structure': structure_results,
            'content': content_results,
            'search_time': total_time
        }
    
    def optimized_dual_search(self, query: str, k: int = 3) -> Dict[str, List[Dict[str, Any]]]:
        """Optimized dual search with pre-filtering and caching"""
        # Check cache first
        cache_key = f"{query}_{k}"
        if cache_key in self.query_cache:
            self.logger.info("Returning cached results")
            return self.query_cache[cache_key]
        
        start_time = time.time()
        
        # Step 1: Pre-filter documents
        structure_indices, content_indices = self.pre_filter_documents(query)
        
        self.logger.info(f"Pre-filtered: {len(structure_indices)} structure, {len(content_indices)} content documents")
        
        # Step 2: Parallel search execution
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            structure_future = executor.submit(self.search_structure, query, k)
            content_future = executor.submit(self.search_content, query, k)
            
            structure_results = structure_future.result()
            content_results = content_future.result()
        
        total_time = time.time() - start_time
        
        results = {
            'structure': structure_results,
            'content': content_results,
            'search_time': total_time,
            'pre_filtered_structure': len(structure_indices),
            'pre_filtered_content': len(content_indices)
        }
        
        # Cache results
        self.query_cache[cache_key] = results
        
        self.logger.info(f"Optimized dual search completed in {total_time:.3f}s")
        
        return results
    
    def generate_response(self, query: str, structure_context: str, content_context: str) -> str:
        """Generate response using both structure and content context"""
        try:
            prompt = f"""
You are writing a legal petition. Use the following information to create a comprehensive legal document.

LEGAL STRUCTURE TEMPLATE:
{structure_context}

LEGAL CONTENT AND REASONING:
{content_context}

CASE DETAILS TO FILL INTO THE TEMPLATE:
{query}

INSTRUCTIONS:
1. Use the structure template above as your document format
2. Incorporate the legal content and reasoning provided
3. Fill in the content using the case details provided
4. Maintain proper legal language and terminology
5. Ensure the document follows the correct legal structure

Write the complete petition following the structure template but with your case details and legal reasoning.
"""

            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "top_k": 40,
                        "max_tokens": 1500,
                        "repeat_penalty": 1.1
                    }
                },
                timeout=60
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
    
    def query(self, question: str, k: int = 3) -> Dict[str, Any]:
        """Main query interface using optimized dual RAG"""
        start_time = time.time()
        
        # Perform optimized dual search
        search_results = self.optimized_dual_search(question, k)
        
        # Extract contexts
        structure_contexts = [doc.get('text', '') for doc in search_results['structure']]
        content_contexts = [doc.get('text', '') for doc in search_results['content']]
        
        # Combine contexts
        structure_context = "\n\n".join(structure_contexts[:2])  # Limit to 2 structure docs
        content_context = "\n\n".join(content_contexts[:2])      # Limit to 2 content docs
        
        # Generate response
        response = self.generate_response(question, structure_context, content_context)
        
        total_time = time.time() - start_time
        
        return {
            'question': question,
            'response': response,
            'structure_sources': search_results['structure'],
            'content_sources': search_results['content'],
            'total_structure_sources': len(search_results['structure']),
            'total_content_sources': len(search_results['content']),
            'search_time': search_results['search_time'],
            'total_time': total_time,
            'pre_filtered_structure': search_results.get('pre_filtered_structure', 0),
            'pre_filtered_content': search_results.get('pre_filtered_content', 0)
        }
    
    def build_filters(self):
        """Build metadata filters for pre-filtering"""
        self.logger.info("Building metadata filters for pre-filtering...")
        
        # Build filters from documents
        self.metadata_filters = {
            'courts': set(),
            'case_types': set(),
            'keywords': set()
        }
        
        # Process structure documents
        for doc in self.structure_documents:
            if 'court' in doc:
                self.metadata_filters['courts'].add(doc['court'])
            if 'title' in doc:
                case_type = self.extract_case_type(doc['title'])
                if case_type:
                    self.metadata_filters['case_types'].add(case_type)
        
        # Process content documents
        for doc in self.content_documents:
            if 'court' in doc:
                self.metadata_filters['courts'].add(doc['court'])
            if 'title' in doc:
                case_type = self.extract_case_type(doc['title'])
                if case_type:
                    self.metadata_filters['case_types'].add(case_type)
        
        self.logger.info(f"Built filters: {len(self.metadata_filters['courts'])} courts, {len(self.metadata_filters['case_types'])} case types")
    
    def extract_case_type(self, title: str) -> Optional[str]:
        """Extract case type from document title"""
        title_lower = title.lower()
        
        case_types = {
            'contract': ['contract', 'agreement', 'breach'],
            'criminal': ['criminal', 'bail', 'appeal', 'conviction'],
            'civil': ['civil', 'property', 'damages'],
            'constitutional': ['constitutional', 'fundamental', 'rights'],
            'family': ['family', 'divorce', 'custody'],
            'commercial': ['commercial', 'business', 'corporate']
        }
        
        for case_type, keywords in case_types.items():
            if any(keyword in title_lower for keyword in keywords):
                return case_type
        
        return None
    
    @lru_cache(maxsize=1000)
    def get_cached_embedding(self, text: str, model_type: str):
        """Get cached embedding for text"""
        if model_type == 'structure':
            return self.structure_encoder.encode([text])
        else:
            return self.content_encoder.encode([text])
    
    def pre_filter_documents(self, query: str) -> Tuple[List[int], List[int]]:
        """Pre-filter documents based on query keywords and metadata"""
        query_lower = query.lower()
        
        # Extract keywords from query
        keywords = re.findall(r'\b\w+\b', query_lower)
        
        # Extract case type from query
        case_type = self.extract_case_type(query)
        
        # Extract court mentions
        courts = [court for court in self.metadata_filters['courts'] 
                 if court.lower() in query_lower]
        
        structure_indices = []
        content_indices = []
        
        # Filter structure documents
        for i, doc in enumerate(self.structure_documents):
            score = 0
            
            # Check case type match
            if case_type and self.extract_case_type(doc.get('title', '')) == case_type:
                score += 3
            
            # Check court match
            if courts and doc.get('court', '').lower() in [c.lower() for c in courts]:
                score += 2
            
            # Check keyword matches
            doc_text = doc.get('title', '') + ' ' + doc.get('text', '')
            doc_lower = doc_text.lower()
            keyword_matches = sum(1 for keyword in keywords if keyword in doc_lower)
            score += keyword_matches * 0.5
            
            if score > 0:
                structure_indices.append(i)
        
        # Filter content documents
        for i, doc in enumerate(self.content_documents):
            score = 0
            
            # Check case type match
            if case_type and self.extract_case_type(doc.get('title', '')) == case_type:
                score += 3
            
            # Check court match
            if courts and doc.get('court', '').lower() in [c.lower() for c in courts]:
                score += 2
            
            # Check keyword matches
            doc_text = doc.get('title', '') + ' ' + doc.get('text', '')
            doc_lower = doc_text.lower()
            keyword_matches = sum(1 for keyword in keywords if keyword in doc_lower)
            score += keyword_matches * 0.5
            
            if score > 0:
                content_indices.append(i)
        
        return structure_indices, content_indices

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        stats = {
            'cache_size': len(self.query_cache),
            'embedding_cache_size': self.get_cached_embedding.cache_info(),
            'filters': {
                'courts': len(self.metadata_filters['courts']),
                'case_types': len(self.metadata_filters['case_types'])
            },
            'device': self.device
        }
        
        # Add GPU information if using GPU
        if self.device == "cuda":
            gpu_info = self.get_gpu_memory_info()
            if gpu_info:
                stats['gpu'] = gpu_info
        
        return stats

    def get_gpu_memory_info(self) -> Dict[str, Any]:
        """Get GPU memory information"""
        if self.device == "cuda":
            try:
                allocated = torch.cuda.memory_allocated(0) / 1024**3  # GB
                reserved = torch.cuda.memory_reserved(0) / 1024**3   # GB
                total = torch.cuda.get_device_properties(0).total_memory / 1024**3  # GB
                
                return {
                    'allocated_gb': allocated,
                    'reserved_gb': reserved,
                    'total_gb': total,
                    'free_gb': total - reserved,
                    'utilization_percent': (reserved / total) * 100
                }
            except Exception as e:
                self.logger.warning(f"Could not get GPU memory info: {e}")
                return {}
        return {}
    
    def clear_gpu_cache(self):
        """Clear GPU cache to free memory"""
        if self.device == "cuda":
            torch.cuda.empty_cache()
            self.logger.info("🧹 GPU cache cleared")
    
    def optimize_for_gpu(self):
        """Optimize settings for GPU usage"""
        if self.device == "cuda":
            # Set optimal batch sizes for GPU
            torch.backends.cudnn.benchmark = True
            torch.backends.cudnn.deterministic = False
            
            # Monitor GPU memory
            memory_info = self.get_gpu_memory_info()
            if memory_info:
                self.logger.info(f"🎮 GPU Memory: {memory_info['allocated_gb']:.2f}GB allocated, "
                               f"{memory_info['free_gb']:.2f}GB free")
            
            return True
        return False

# Usage example
if __name__ == "__main__":
    rag = OptimizedDualRAGInterface("dual_rag_indexes")
    
    # Test query
    result = rag.query("What are the key legal principles for granting bail in criminal cases?")
    print("Question:", result['question'])
    print("Response:", result['response'][:200] + "...")
    print("Structure sources:", result['total_structure_sources'])
    print("Content sources:", result['total_content_sources'])
    print("Total time:", result['total_time']) 