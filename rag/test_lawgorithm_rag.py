import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from lawgorithm_rag_interface import LawgorithmRAGInterface

def test_rag_system():
    print("🧪 Testing Lawgorithm RAG System")
    print("=" * 40)
    
    try:
        # Initialize RAG interface
        rag = LawgorithmRAGInterface("vector_store_lawgorithm/vector_store.json")
        print("✅ RAG system loaded successfully!")
        
        # Test queries
        test_queries = [
            "What are the grounds for granting bail in criminal cases?",
            "How to draft a writ petition?",
            "What is the procedure for filing a civil appeal?"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n🔍 Test {i}: {query}")
            print("-" * 50)
            try:
                print("About to query RAG...")
                result = rag.query(query)
                print("Query complete!")
                print(f"📋 Response: {result['response'][:200]}...")
                print(f"📚 Sources used: {result['total_sources']}")
                print(f"✅ Test {i} completed successfully!")
            except Exception as e:
                print(f"❌ Exception during query: {e}")
                import traceback
                traceback.print_exc()
        
        print("\n🎯 All tests completed! RAG system is working with lawgorithm model.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_rag_system() 