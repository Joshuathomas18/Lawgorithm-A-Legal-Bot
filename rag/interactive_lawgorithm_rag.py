import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from rag.lawgorithm_rag_interface import LawgorithmRAGInterface

def main():
    print("🤖 Lawgorithm RAG Bot - Legal Petition Assistant")
    print("=" * 50)
    
    # Initialize RAG interface
    try:
        rag = LawgorithmRAGInterface("rag/vector_store_lawgorithm/vector_store.json")
        print("✅ RAG system loaded successfully!")
    except Exception as e:
        print(f"❌ Error loading RAG system: {e}")
        return
    
    print("\n💡 You can ask questions about:")
    print("   • Legal principles and precedents")
    print("   • Case law and judgments")
    print("   • Petition drafting guidance")
    print("   • Court procedures and rules")
    print("   • Legal research queries")
    print("\nType 'quit' to exit\n")
    
    while True:
        try:
            question = input("🔍 Your legal question: ").strip()
            
            if question.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if not question:
                continue
            
            print("\n🤔 Thinking...")
            result = rag.query(question)
            
            print("\n📋 Answer:")
            print("-" * 40)
            print(result['response'])
            print("-" * 40)
            print(f"📚 Sources used: {result['total_sources']}")
            print()
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            print()

if __name__ == "__main__":
    main()
