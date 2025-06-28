#!/usr/bin/env python3
"""
RAG + Ollama Integration for Legal Petition System
=================================================

Based on LocalAIAgentWithRAG pattern for clean integration.
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional
from rag_ollama_integration.vector_store import VectorStore
from rag_ollama_integration.ollama_client import OllamaClient

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LegalRAGAgent:
    def __init__(self, vector_store_path: str = "rag_ollama_integration/vector_store.json"):
        """Initialize the Legal RAG Agent"""
        self.vector_store = VectorStore(vector_store_path)
        self.ollama_client = OllamaClient(model_name="lawgorithm:latest")
        
        logger.info("🤖 Legal RAG Agent initialized")
        logger.info(f"   Vector store: {vector_store_path}")
        logger.info(f"   Model: lawgorithm:latest")
    
    def query(self, question: str, top_k: int = 3) -> Dict[str, Any]:
        """Main query interface - RAG + Ollama integration"""
        logger.info(f"🔍 Processing query: {question}")
        
        try:
            # Step 1: RAG Search
            logger.info("📚 Step 1: Searching vector store...")
            similar_docs = self.vector_store.search_similar(question, top_k)
            
            # Step 2: Extract context
            logger.info("📋 Step 2: Extracting context...")
            context = self._extract_context(similar_docs)
            
            # Step 3: Generate response with Ollama
            logger.info("🤖 Step 3: Generating response with Ollama...")
            response = self.ollama_client.generate_response(question, context)
            
            return {
                'question': question,
                'response': response,
                'context_sources': similar_docs,
                'total_sources': len(similar_docs)
            }
            
        except Exception as e:
            logger.error(f"❌ Error in query: {e}")
            return {
                'question': question,
                'response': f"Error processing query: {str(e)}",
                'context_sources': [],
                'total_sources': 0
            }
    
    def _extract_context(self, similar_docs: List[Dict]) -> str:
        """Extract context from similar documents"""
        if not similar_docs:
            return ""
        
        contexts = []
        for doc in similar_docs:
            # Limit context length for better performance
            doc_text = doc['document'][:1000] if len(doc['document']) > 1000 else doc['document']
            contexts.append(doc_text)
        
        return "\n\n".join(contexts)
    
    def chat(self, user_input: str) -> str:
        """Simple chat interface"""
        result = self.query(user_input)
        return result['response']

def main():
    """Main function to run the Legal RAG Agent"""
    print("🤖 Legal RAG Agent with Ollama Integration")
    print("=" * 50)
    
    # Initialize agent
    agent = LegalRAGAgent()
    
    print("\n💡 Example queries:")
    print("   - 'Draft a Supreme Court petition for a dowry case'")
    print("   - 'What are the grounds for bail?'")
    print("   - 'How to file a property dispute?'")
    print("\nType 'quit' to exit")
    print("-" * 50)
    
    while True:
        try:
            user_input = input("\n👤 You: ").strip()
            
            if user_input.lower() == 'quit':
                print("👋 Goodbye!")
                break
            
            if not user_input:
                continue
            
            print("\n🤖 Assistant: ", end="", flush=True)
            response = agent.chat(user_input)
            print(response)
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main() 