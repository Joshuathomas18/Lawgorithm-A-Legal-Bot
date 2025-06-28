#!/usr/bin/env python3
"""
Legal RAG Chatbot - Main Application
====================================

Main application for the Legal RAG Chatbot system.
Based on LocalAIAgentWithRAG main.py structure.
"""

import logging
import sys
from typing import Optional
from .rag_agent import LegalRAGAgent

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def print_banner():
    """Print application banner"""
    print("=" * 60)
    print("🤖 LEGAL RAG CHATBOT")
    print("=" * 60)
    print("📚 Powered by 445,938 trained legal documents")
    print("🧠 Using lawgorithm:latest model")
    print("🔍 Dual RAG: Structure + Content search")
    print("=" * 60)

def print_help():
    """Print help information."""
    print("\n📖 COMMANDS:")
    print("  ask <question>     - Ask a legal question (or just type your question)")
    print("  search <query>     - Search documents only (no generation)")
    print("  stats              - Show system statistics")
    print("  help               - Show this help")
    print("  quit/exit          - Exit the chatbot")
    print()
    print("💡 EXAMPLES:")
    print("  ask What are the grounds for filing a writ petition?")
    print("  How do I file a dowry case petition?")
    print("  search contract dispute cases")
    print("  stats")

def interactive_mode():
    """Run interactive chat mode"""
    print_banner()
    
    try:
        # Initialize the RAG agent
        logger.info("Initializing Legal RAG Agent...")
        agent = LegalRAGAgent()
        
        # Show initial stats
        stats = agent.get_stats()
        print(f"\n✅ System Ready!")
        print(f"📊 Documents loaded: {stats['total_documents']:,}")
        print(f"🤖 Model: {stats['ollama_model'].get('name', 'Unknown')}")
        
        print_help()
        
        while True:
            try:
                # Get user input
                user_input = input("\n🤖 Legal RAG > ").strip()
                
                if not user_input:
                    continue
                
                # Parse command
                parts = user_input.split(' ', 1)
                command = parts[0].lower()
                
                if command in ['quit', 'exit']:
                    print("👋 Goodbye!")
                    break
                
                elif command == 'help':
                    print_help()
                
                elif command == 'stats':
                    stats = agent.get_stats()
                    print(f"\n📊 SYSTEM STATISTICS:")
                    print(f"   Content documents: {stats['vector_store']['content_documents']:,}")
                    print(f"   Structure documents: {stats['vector_store']['structure_documents']:,}")
                    print(f"   Total documents: {stats['total_documents']:,}")
                    print(f"   Model: {stats['ollama_model'].get('name', 'Unknown')}")
                    print(f"   Model size: {stats['ollama_model'].get('size', 'Unknown')}")
                
                elif command == 'ask':
                    if len(parts) < 2:
                        print("❌ Please provide a question: ask <your question>")
                        continue
                    
                    question = parts[1]
                    print(f"\n🔍 Searching for: {question}")
                    
                    # Process the query
                    result = agent.query(question)
                    
                    print(f"\n💡 ANSWER:")
                    print("-" * 40)
                    print(result['response'])
                    print("-" * 40)
                    print(f"📊 Found {result['stats']['content_results']} content matches, {result['stats']['structure_results']} structure matches")
                
                elif command == 'search':
                    if len(parts) < 2:
                        print("❌ Please provide a search query: search <your query>")
                        continue
                    
                    query = parts[1]
                    print(f"\n🔍 Searching documents for: {query}")
                    
                    # Search only
                    results = agent.search_only(query)
                    
                    print(f"\n📄 SEARCH RESULTS:")
                    print("-" * 40)
                    
                    # Show structure results
                    if results['structure']:
                        print("🏗️ STRUCTURE MATCHES:")
                        for i, result in enumerate(results['structure'][:3]):
                            print(f"  {i+1}. Score: {result['similarity']:.3f}")
                            print(f"     {result['document'][:200]}...")
                            print()
                    
                    # Show content results
                    if results['content']:
                        print("📖 CONTENT MATCHES:")
                        for i, result in enumerate(results['content'][:3]):
                            print(f"  {i+1}. Score: {result['similarity']:.3f}")
                            print(f"     {result['document'][:200]}...")
                            print()
                
                else:
                    # Treat any other input as a question
                    question = user_input
                    print(f"\n🔍 Searching for: {question}")
                    
                    # Process the query
                    result = agent.query(question)
                    
                    print(f"\n💡 ANSWER:")
                    print("-" * 40)
                    print(result['response'])
                    print("-" * 40)
                    print(f"📊 Found {result['stats']['content_results']} content matches, {result['stats']['structure_results']} structure matches")
            
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                logger.error(f"Error processing command: {e}")
                print(f"❌ Error: {e}")
    
    except Exception as e:
        logger.error(f"Failed to initialize system: {e}")
        print(f"❌ System initialization failed: {e}")
        print("💡 Make sure:")
        print("   - Ollama is running (ollama serve)")
        print("   - lawgorithm:latest model is installed")
        print("   - Trained indexes exist in rag_ready/dual_rag_indexes/")

def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        # Command line mode
        command = sys.argv[1].lower()
        
        if command == 'test':
            # Test mode
            print("🧪 Testing Legal RAG System...")
            agent = LegalRAGAgent()
            stats = agent.get_stats()
            print(f"✅ System ready: {stats['total_documents']:,} documents loaded")
            
            # Test query
            test_question = "What are the grounds for filing a writ petition?"
            print(f"\n🔍 Testing query: {test_question}")
            result = agent.query(test_question)
            print(f"✅ Response generated successfully!")
            print(f"📊 Found {result['stats']['content_results']} content matches")
        
        elif command == 'stats':
            # Stats mode
            agent = LegalRAGAgent()
            stats = agent.get_stats()
            print(f"📊 Legal RAG System Statistics:")
            print(f"   Content documents: {stats['vector_store']['content_documents']:,}")
            print(f"   Structure documents: {stats['vector_store']['structure_documents']:,}")
            print(f"   Total documents: {stats['total_documents']:,}")
            print(f"   Model: {stats['ollama_model'].get('name', 'Unknown')}")
        
        else:
            print("❌ Unknown command. Use: test, stats, or no arguments for interactive mode")
    else:
        # Interactive mode
        interactive_mode()

if __name__ == "__main__":
    main() 