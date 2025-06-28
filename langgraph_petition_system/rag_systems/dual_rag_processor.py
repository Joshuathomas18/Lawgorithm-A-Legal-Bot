"""
Dual RAG Processor for Indian Legal Documents
============================================

Processes collected Indian Kanoon data into two separate RAG systems:
1. Structure RAG: Legal document structure and formatting
2. Content RAG: Legal content and reasoning
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import re

from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

logger = logging.getLogger("dual_rag_processor")
logging.basicConfig(level=logging.INFO)

class DualRAGProcessor:
    def __init__(self, 
                 structure_model_name: str = "all-MiniLM-L6-v2",
                 content_model_name: str = "all-mpnet-base-v2",
                 chunk_size: int = 512,
                 chunk_overlap: int = 50):
        """Initialize the dual RAG processor."""
        self.structure_model_name = structure_model_name
        self.content_model_name = content_model_name
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # Initialize embedding models
        self.structure_encoder = SentenceTransformer(structure_model_name)
        self.content_encoder = SentenceTransformer(content_model_name)
        
        # Vector stores
        self.structure_index = None
        self.content_index = None
        self.structure_documents = []
        self.content_documents = []
        
    def load_processed_data(self, data_file: str) -> Dict[str, Any]:
        """Load the processed data from the collector."""
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        logger.info(f"Loaded {len(data.get('structure_data', []))} structure documents")
        logger.info(f"Loaded {len(data.get('content_data', []))} content documents")
        return data
    
    def split_structure_documents(self, structure_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Split structure documents by legal sections and headers."""
        structure_chunks = []
        
        for doc in structure_data:
            docid = doc.get('docid')
            title = doc.get('title', '')
            court = doc.get('court', '')
            date = doc.get('date', '')
            
            # Create metadata
            metadata = {
                'docid': docid,
                'title': title,
                'court': court,
                'date': date,
                'type': 'structure'
            }
            
            # Extract citations
            citations = doc.get('citations', [])
            if citations:
                citation_text = " ".join([f"{cite.get('citation', '')}" for cite in citations])
                structure_chunks.append({
                    'text': f"Citations: {citation_text}",
                    'metadata': {**metadata, 'section': 'citations'}
                })
            
            # Extract cited by
            cited_by = doc.get('cited_by', [])
            if cited_by:
                cited_text = " ".join([f"{cite.get('citation', '')}" for cite in cited_by])
                structure_chunks.append({
                    'text': f"Cited by: {cited_text}",
                    'metadata': {**metadata, 'section': 'cited_by'}
                })
            
            # Create document header chunk
            header_text = f"Title: {title}\nCourt: {court}\nDate: {date}"
            structure_chunks.append({
                'text': header_text,
                'metadata': {**metadata, 'section': 'header'}
            })
        
        logger.info(f"Created {len(structure_chunks)} structure chunks")
        return structure_chunks
    
    def split_content_documents(self, content_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Split content documents by semantic chunks."""
        content_chunks = []
        
        for doc in content_data:
            docid = doc.get('docid')
            title = doc.get('title', '')
            sections = doc.get('sections', {})
            
            metadata = {
                'docid': docid,
                'title': title,
                'type': 'content'
            }
            
            # Process each section
            for section_name, section_text in sections.items():
                if not section_text or section_text.strip() == "":
                    continue
                
                # Split long sections into chunks
                if len(section_text) > self.chunk_size:
                    chunks = self._split_text_by_size(section_text)
                    for i, chunk in enumerate(chunks):
                        content_chunks.append({
                            'text': chunk,
                            'metadata': {**metadata, 'section': section_name, 'chunk_id': i}
                        })
                else:
                    content_chunks.append({
                        'text': section_text,
                        'metadata': {**metadata, 'section': section_name}
                    })
            
            # Process keywords if available
            keywords = doc.get('keywords', [])
            if keywords:
                keyword_text = f"Keywords: {', '.join(keywords[:10])}"  # Limit to 10 keywords
                content_chunks.append({
                    'text': keyword_text,
                    'metadata': {**metadata, 'section': 'keywords'}
                })
        
        logger.info(f"Created {len(content_chunks)} content chunks")
        return content_chunks
    
    def _split_text_by_size(self, text: str) -> List[str]:
        """Split text into chunks of specified size with overlap."""
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            
            # Try to break at sentence boundary
            if end < len(text):
                # Look for sentence endings
                for i in range(end, max(start, end - 100), -1):
                    if text[i] in '.!?':
                        end = i + 1
                        break
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end - self.chunk_overlap
            if start >= len(text):
                break
        
        return chunks
    
    def build_structure_index(self, structure_chunks: List[Dict[str, Any]]):
        """Build FAISS index for structure chunks."""
        if not structure_chunks:
            logger.warning("No structure chunks to index")
            return
        
        # Extract texts and metadata
        texts = [chunk['text'] for chunk in structure_chunks]
        self.structure_documents = structure_chunks
        
        # Create embeddings
        logger.info("Creating structure embeddings...")
        embeddings = self.structure_encoder.encode(texts, show_progress_bar=True)
        
        # Build FAISS index
        dimension = embeddings.shape[1]
        self.structure_index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity
        self.structure_index.add(embeddings.astype('float32'))
        
        logger.info(f"Built structure index with {len(structure_chunks)} documents")
    
    def build_content_index(self, content_chunks: List[Dict[str, Any]]):
        """Build FAISS index for content chunks."""
        if not content_chunks:
            logger.warning("No content chunks to index")
            return
        
        # Extract texts and metadata
        texts = [chunk['text'] for chunk in content_chunks]
        self.content_documents = content_chunks
        
        # Create embeddings
        logger.info("Creating content embeddings...")
        embeddings = self.content_encoder.encode(texts, show_progress_bar=True)
        
        # Build FAISS index
        dimension = embeddings.shape[1]
        self.content_index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity
        self.content_index.add(embeddings.astype('float32'))
        
        logger.info(f"Built content index with {len(content_chunks)} documents")
    
    def search_structure(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Search structure RAG for legal structure information."""
        if self.structure_index is None:
            logger.error("Structure index not built")
            return []
        
        # Encode query
        query_embedding = self.structure_encoder.encode([query])
        
        # Search
        scores, indices = self.structure_index.search(query_embedding.astype('float32'), k)
        
        # Return results
        results = []
        for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
            if idx < len(self.structure_documents):
                doc = self.structure_documents[idx].copy()
                doc['score'] = float(score)
                doc['rank'] = i + 1
                results.append(doc)
        
        return results
    
    def search_content(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Search content RAG for legal content information."""
        if self.content_index is None:
            logger.error("Content index not built")
            return []
        
        # Encode query
        query_embedding = self.content_encoder.encode([query])
        
        # Search
        scores, indices = self.content_index.search(query_embedding.astype('float32'), k)
        
        # Return results
        results = []
        for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
            if idx < len(self.content_documents):
                doc = self.content_documents[idx].copy()
                doc['score'] = float(score)
                doc['rank'] = i + 1
                results.append(doc)
        
        return results
    
    def dual_search(self, query: str, k: int = 5) -> Dict[str, List[Dict[str, Any]]]:
        """Perform dual RAG search."""
        structure_results = self.search_structure(query, k)
        content_results = self.search_content(query, k)
        
        return {
            'structure': structure_results,
            'content': content_results
        }
    
    def save_indexes(self, output_dir: str):
        """Save the built indexes and documents."""
        os.makedirs(output_dir, exist_ok=True)
        
        # Save structure index
        if self.structure_index is not None:
            faiss.write_index(self.structure_index, os.path.join(output_dir, "structure_index.faiss"))
            with open(os.path.join(output_dir, "structure_documents.json"), 'w', encoding='utf-8') as f:
                json.dump(self.structure_documents, f, ensure_ascii=False, indent=2)
        
        # Save content index
        if self.content_index is not None:
            faiss.write_index(self.content_index, os.path.join(output_dir, "content_index.faiss"))
            with open(os.path.join(output_dir, "content_documents.json"), 'w', encoding='utf-8') as f:
                json.dump(self.content_documents, f, ensure_ascii=False, indent=2)
        
        # Save metadata
        metadata = {
            'structure_model': self.structure_model_name,
            'content_model': self.content_model_name,
            'chunk_size': self.chunk_size,
            'chunk_overlap': self.chunk_overlap,
            'created_at': datetime.now().isoformat(),
            'structure_docs': len(self.structure_documents),
            'content_docs': len(self.content_documents)
        }
        
        with open(os.path.join(output_dir, "rag_metadata.json"), 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Saved RAG indexes to {output_dir}")
    
    def load_indexes(self, input_dir: str):
        """Load previously built indexes."""
        # Load structure index
        structure_index_path = os.path.join(input_dir, "structure_index.faiss")
        if os.path.exists(structure_index_path):
            self.structure_index = faiss.read_index(structure_index_path)
            with open(os.path.join(input_dir, "structure_documents.json"), 'r', encoding='utf-8') as f:
                self.structure_documents = json.load(f)
            logger.info(f"Loaded structure index with {len(self.structure_documents)} documents")
        
        # Load content index
        content_index_path = os.path.join(input_dir, "content_index.faiss")
        if os.path.exists(content_index_path):
            self.content_index = faiss.read_index(content_index_path)
            with open(os.path.join(input_dir, "content_documents.json"), 'r', encoding='utf-8') as f:
                self.content_documents = json.load(f)
            logger.info(f"Loaded content index with {len(self.content_documents)} documents")

def main():
    """Main function to process data and build RAG indexes."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Build dual RAG indexes from collected data')
    parser.add_argument('--data-file', required=True, help='Path to processed data JSON file')
    parser.add_argument('--output-dir', default='rag_indexes', help='Output directory for indexes')
    parser.add_argument('--chunk-size', type=int, default=512, help='Chunk size for content splitting')
    parser.add_argument('--chunk-overlap', type=int, default=50, help='Chunk overlap for content splitting')
    
    args = parser.parse_args()
    
    # Initialize processor
    processor = DualRAGProcessor(
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap
    )
    
    # Load data
    logger.info(f"Loading data from {args.data_file}")
    data = processor.load_processed_data(args.data_file)
    
    # Process structure data
    logger.info("Processing structure data...")
    structure_chunks = processor.split_structure_documents(data.get('structure_data', []))
    processor.build_structure_index(structure_chunks)
    
    # Process content data
    logger.info("Processing content data...")
    content_chunks = processor.split_content_documents(data.get('content_data', []))
    processor.build_content_index(content_chunks)
    
    # Save indexes
    processor.save_indexes(args.output_dir)
    
    logger.info("Dual RAG processing complete!")

if __name__ == "__main__":
    main() 