"""
Main RAG System for Petition Automation
=======================================

This is the main entry point for the RAG (Retrieval-Augmented Generation) system
that powers the petition automation platform.

Features:
- Legal document retrieval using vector search
- Context-aware petition generation
- Multi-model support (Ollama, Gemini, etc.)
- Interactive conversation interface
"""

import sys
import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag.vector import VectorStore
from rag.models import ModelManager
from rag.utils import setup_logging, validate_input

class PetitionRAGSystem:
    """
    Main RAG system for petition automation.
    
    This class coordinates between vector search, model generation,
    and provides a clean interface for petition generation.
    """
    
    def __init__(self, config_path: str = "rag/config.json"):
        """Initialize the RAG system with configuration."""
        self.logger = setup_logging("PetitionRAGSystem")
        self.config = self._load_config(config_path)
        
        # Initialize components
        self.vector_store = VectorStore(
            vector_store_path=self.config.get("vector_store_path", "rag/vector_store_lawgorithm/vector_store.json")
        )
        self.model_manager = ModelManager(
            model_config=self.config.get("models", {})
        )
        
        self.logger.info("✅ Petition RAG System initialized successfully")
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                # Default configuration
                return {
                    "vector_store_path": "rag/vector_store_lawgorithm/vector_store.json",
                    "models": {
                        "default": "lawgorithm:latest",
                        "ollama_url": "http://localhost:11434"
                    },
                    "search": {
                        "top_k": 3,
                        "similarity_threshold": 0.7
                    }
                }
        except Exception as e:
            self.logger.error(f"Error loading config: {e}")
            return {}
    
    def search_legal_context(self, query: str, top_k: int = None) -> List[Dict[str, Any]]:
        """
        Search for relevant legal context using vector similarity.
        
        Args:
            query: The search query
            top_k: Number of results to return
            
        Returns:
            List of relevant documents with metadata
        """
        top_k = top_k or self.config.get("search", {}).get("top_k", 3)
        
        try:
            self.logger.info(f"🔍 Searching for: {query}")
            results = self.vector_store.search_similar(query, top_k)
            self.logger.info(f"📚 Found {len(results)} relevant documents")
            return results
        except Exception as e:
            self.logger.error(f"Error in legal context search: {e}")
            return []
    
    def generate_petition(self, case_type: str, court: str, details: str = "", 
                         use_context: bool = True) -> Dict[str, Any]:
        """
        Generate a petition using RAG-enhanced context.
        
        Args:
            case_type: Type of case (criminal, civil, family, etc.)
            court: Target court
            details: Specific case details
            use_context: Whether to use RAG context
            
        Returns:
            Generated petition with metadata
        """
        try:
            self.logger.info(f"🤖 Generating {case_type} petition for {court}")
            
            # Get relevant legal context if requested
            context = ""
            if use_context:
                legal_query = f"{case_type} case petition {court} legal principles"
                context_results = self.search_legal_context(legal_query)
                context = "\n\n".join([doc['document'] for doc in context_results])
            
            # Create prompt
            prompt = self._create_petition_prompt(case_type, court, details, context)
            
            # Generate response
            response = self.model_manager.generate_response(prompt)
            
            # Create result
            result = {
                'petition_text': response,
                'case_type': case_type,
                'court': court,
                'details': details,
                'context_used': bool(context),
                'context_sources': len(context_results) if use_context else 0,
                'generated_at': datetime.now().isoformat(),
                'model_used': self.model_manager.current_model
            }
            
            self.logger.info("✅ Petition generated successfully")
            return result
            
        except Exception as e:
            self.logger.error(f"Error generating petition: {e}")
            return {
                'error': str(e),
                'petition_text': "Error generating petition. Please try again."
            }
    
    def _create_petition_prompt(self, case_type: str, court: str, 
                               details: str, context: str) -> str:
        """Create a well-structured prompt for petition generation."""
        
        prompt = f"""Generate a professional {case_type} petition for {court}.

LEGAL CONTEXT & PRECEDENTS:
{context if context else "No specific legal context provided."}

PETITION REQUIREMENTS:
- Case type: {case_type}
- Court: {court}
- Include: Court name, case number, parties, facts, prayer, date
- Format: Professional legal document structure
- Style: Formal legal language

SPECIFIC DETAILS: {details if details else "Standard case details"}

Generate a complete petition in proper legal format:"""
        
        return prompt
    
    def interactive_mode(self):
        """Start interactive mode for testing and development."""
        print("🤖 Petition RAG System - Interactive Mode")
        print("=" * 50)
        print("💡 Available commands:")
        print("   • 'search <query>' - Search legal context")
        print("   • 'generate <case_type> <court> [details]' - Generate petition")
        print("   • 'quit' - Exit")
        print()
        
        while True:
            try:
                command = input("🔍 Command: ").strip()
                
                if command.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break
                
                if command.startswith('search '):
                    query = command[7:]  # Remove 'search ' prefix
                    results = self.search_legal_context(query)
                    print(f"\n📚 Found {len(results)} results:")
                    for i, result in enumerate(results, 1):
                        print(f"{i}. Similarity: {result['similarity']:.3f}")
                        print(f"   Content: {result['document'][:200]}...")
                        print()
                
                elif command.startswith('generate '):
                    parts = command[9:].split(' ', 2)  # Remove 'generate ' prefix
                    if len(parts) >= 2:
                        case_type = parts[0]
                        court = parts[1]
                        details = parts[2] if len(parts) > 2 else ""
                        
                        result = self.generate_petition(case_type, court, details)
                        print(f"\n📄 Generated Petition:")
                        print("-" * 50)
                        print(result['petition_text'])
                        print("-" * 50)
                        print(f"Model: {result['model_used']}")
                        print(f"Context sources: {result['context_sources']}")
                        print()
                    else:
                        print("❌ Usage: generate <case_type> <court> [details]")
                
                else:
                    print("❌ Unknown command. Type 'quit' to exit.")
                    
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

def main():
    """Main entry point for the RAG system."""
    try:
        # Initialize RAG system
        rag_system = PetitionRAGSystem()
        
        # Check if interactive mode is requested
        if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
            rag_system.interactive_mode()
        else:
            # Example usage
            print("🚀 Petition RAG System")
            print("=" * 30)
            
            # Test search
            results = rag_system.search_legal_context("bail in criminal cases")
            print(f"📚 Search test: Found {len(results)} results")
            
            # Test generation
            result = rag_system.generate_petition("criminal", "High Court", "bail application")
            print(f"📄 Generation test: {len(result['petition_text'])} characters")
            
            print("\n✅ System is working! Use --interactive for full features.")
            
    except Exception as e:
        print(f"❌ Error initializing RAG system: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 