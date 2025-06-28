import chromadb
from sentence_transformers import SentenceTransformer
import pandas as pd
import json
from typing import List, Dict, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PetitionVectorStore:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """Initialize the vector store with embedding model and ChromaDB"""
        self.embedding_model = SentenceTransformer(model_name)
        self.client = chromadb.Client()
        
        # Try to get existing collection or create new one
        try:
            self.collection = self.client.get_collection("petitions")
            logger.info("Using existing petitions collection")
        except:
            self.collection = self.client.create_collection("petitions")
            logger.info("Created new petitions collection")
    
    def add_petitions(self, petitions_data: List[Dict]):
        """Add petitions to vector database"""
        if not petitions_data:
            logger.warning("No petitions data provided")
            return
            
        texts = [p['content'] for p in petitions_data]
        embeddings = self.embedding_model.encode(texts)
        
        # Generate IDs for documents
        ids = [f"petition_{p['petition_id']}" for p in petitions_data]
        
        self.collection.add(
            embeddings=embeddings.tolist(),
            documents=texts,
            metadatas=[{
                'petition_id': p['petition_id'],
                'title': p['title'],
                'court': p['court'],
                'date': p['date']
            } for p in petitions_data],
            ids=ids
        )
        
        logger.info(f"Added {len(petitions_data)} petitions to vector database")
    
    def search(self, query: str, n_results: int = 5):
        """Search for relevant petitions"""
        query_embedding = self.embedding_model.encode([query])
        results = self.collection.query(
            query_embeddings=query_embedding.tolist(),
            n_results=n_results
        )
        return results
    
    def get_collection_info(self):
        """Get information about the collection"""
        return {
            'count': self.collection.count(),
            'name': self.collection.name
        } 