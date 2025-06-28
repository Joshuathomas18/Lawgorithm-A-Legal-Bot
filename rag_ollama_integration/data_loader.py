#!/usr/bin/env python3
"""
Data Loader for Legal RAG System
================================

Converts existing RAG data to the new vector store format.
"""

import json
import os
import logging
import math
from typing import List, Dict, Any
from vector_store import VectorStore

logger = logging.getLogger(__name__)

class LegalDataLoader:
    def __init__(self, vector_store_path: str = "rag_ollama_integration/vector_store.json"):
        """Initialize data loader"""
        self.vector_store_path = vector_store_path
        self.vector_store = VectorStore(vector_store_path)
    
    def load_from_existing_rag(self, content_docs_path: str, structure_docs_path: str, batch_size: int = 2000):
        """Load data from existing RAG system in batches"""
        logger.info("🔄 Loading data from existing RAG system (robust, resumable, full-scale)...")
        
        total_processed = 0
        
        # --- Load and batch content documents ---
        logger.info(f"Checking if content path exists: {content_docs_path}")
        logger.info(f"File exists: {os.path.exists(content_docs_path)}")
        
        if os.path.exists(content_docs_path):
            logger.info(f"📚 Loading content documents from {content_docs_path}")
            with open(content_docs_path, 'r', encoding='utf-8') as f:
                content_docs = json.load(f)
            total_content = len(content_docs)
            logger.info(f"Total content documents: {total_content}")
            
            # Resume logic: skip already-indexed docs
            already_indexed = len(self.vector_store.documents)
            logger.info(f"Already indexed: {already_indexed}")
            if already_indexed >= total_content:
                logger.info("✅ All content documents already indexed!")
            else:
                num_batches = math.ceil((total_content - already_indexed) / batch_size)
                for i in range(num_batches):
                    start = already_indexed + i * batch_size
                    end = min(already_indexed + (i + 1) * batch_size, total_content)
                    batch = content_docs[start:end]
                    documents = []
                    metadatas = []
                    for doc in batch:
                        try:
                            text = self._extract_content_text(doc)
                            if text:
                                documents.append(text)
                                metadatas.append({
                                    'type': 'content',
                                    'docid': doc.get('docid', ''),
                                    'title': doc.get('title', ''),
                                    'court': doc.get('court', ''),
                                    'date': doc.get('date', '')
                                })
                        except Exception as e:
                            logger.error(f"Error extracting content text: {e}")
                            continue
                    if documents:
                        logger.info(f"Adding content batch {i+1}/{num_batches} ({len(documents)} docs, index {start}-{end})...")
                        self.vector_store.add_documents(documents, metadatas)
                        total_processed += len(documents)
                        if (end % 10000 == 0) or (end == total_content):
                            logger.info(f"Content progress: {end}/{total_content} ({end/total_content*100:.2f}%) - Total processed: {total_processed}")
        else:
            logger.error(f"❌ Content documents file not found: {content_docs_path}")
        
        # --- Load structure documents ---
        logger.info(f"Checking if structure path exists: {structure_docs_path}")
        logger.info(f"File exists: {os.path.exists(structure_docs_path)}")
        
        if os.path.exists(structure_docs_path):
            logger.info(f"📋 Loading structure documents from {structure_docs_path}")
            with open(structure_docs_path, 'r', encoding='utf-8') as f:
                structure_docs = json.load(f)
            
            total_structure = len(structure_docs)
            logger.info(f"Total structure documents: {total_structure}")
            
            # Only add if not already present
            structure_titles = set([doc.get('title', '') for doc in self.vector_store.metadatas if doc.get('type') == 'structure'])
            documents = []
            metadatas = []
            for doc in structure_docs:
                if doc.get('title', '') in structure_titles:
                    continue
                text = self._extract_structure_text(doc)
                if text:
                    documents.append(text)
                    metadatas.append({
                        'type': 'structure',
                        'docid': doc.get('docid', ''),
                        'title': doc.get('title', ''),
                        'court': doc.get('court', ''),
                        'date': doc.get('date', '')
                    })
            
            if documents:
                logger.info(f"Adding {len(documents)} structure documents...")
                self.vector_store.add_documents(documents, metadatas)
                total_processed += len(documents)
                logger.info(f"Structure documents added. Total processed: {total_processed}")
        else:
            logger.error(f"❌ Structure documents file not found: {structure_docs_path}")
        
        logger.info(f"✅ All documents loaded and indexed! Total: {total_processed}")
    
    def _extract_content_text(self, doc: Dict[str, Any]) -> str:
        """Extract text from content document"""
        sections = doc.get('sections', {})
        
        text_parts = []
        
        # Add title
        if doc.get('title'):
            text_parts.append(f"Title: {doc['title']}")
        
        # Add sections
        if sections.get('facts'):
            text_parts.append(f"Facts: {sections['facts']}")
        
        if sections.get('arguments'):
            text_parts.append(f"Arguments: {sections['arguments']}")
        
        if sections.get('judgment'):
            text_parts.append(f"Judgment: {sections['judgment']}")
        
        if sections.get('relief'):
            text_parts.append(f"Relief: {sections['relief']}")
        
        if sections.get('full_content'):
            text_parts.append(f"Content: {sections['full_content']}")
        
        return "\n\n".join(text_parts)
    
    def _extract_structure_text(self, doc: Dict[str, Any]) -> str:
        """Extract text from structure document"""
        text_parts = []
        
        # Add basic info
        if doc.get('title'):
            text_parts.append(f"Title: {doc['title']}")
        
        if doc.get('court'):
            text_parts.append(f"Court: {doc['court']}")
        
        if doc.get('date'):
            text_parts.append(f"Date: {doc['date']}")
        
        if doc.get('citations'):
            text_parts.append(f"Citations: {', '.join(doc['citations'])}")
        
        if doc.get('text'):
            text_parts.append(f"Text: {doc['text']}")
        
        return "\n\n".join(text_parts)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about loaded data"""
        return self.vector_store.get_stats()

def main():
    """Main function to load data"""
    print("🔄 Legal Data Loader")
    print("=" * 30)
    
    # Initialize loader
    loader = LegalDataLoader()
    
    # Load from the trained RAG data with 4.5 lakh documents
    content_path = "../rag_ready/dual_rag_indexes/content_documents.json"
    structure_path = "../rag_ready/dual_rag_indexes/structure_documents.json"
    
    # Check if the files exist
    if not os.path.exists(content_path):
        print(f"❌ Content documents file not found: {content_path}")
        return
    
    if not os.path.exists(structure_path):
        print(f"❌ Structure documents file not found: {structure_path}")
        return
    
    print(f"📁 Loading from trained RAG data:")
    print(f"   Content: {content_path}")
    print(f"   Structure: {structure_path}")
    
    # Load the trained data
    loader.load_from_existing_rag(content_path, structure_path)
    
    # Show stats
    stats = loader.get_stats()
    print(f"\n📊 Vector Store Stats:")
    print(f"   Total documents: {stats['total_documents']}")
    print(f"   Embedding dimension: {stats['embedding_dimension']}")
    print(f"   Vector store path: {stats['vector_store_path']}")

if __name__ == "__main__":
    main() 