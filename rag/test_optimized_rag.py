import time
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from lawgorithm_rag_interface import LawgorithmRAGInterface
from optimized_rag_interface import OptimizedLawgorithmRAGInterface

def test_performance_comparison():
    print("🚀 Performance Comparison: Original vs Optimized RAG")
    print("=" * 60)
    
    # Test queries
    test_queries = [
        "What are the grounds for granting bail in criminal cases?",
        "How to draft a writ petition?",
        "What is the procedure for filing a civil appeal?",
        "What are the requirements for filing a criminal complaint?",
        "How to file a consumer complaint?"
    ]
    
    # Test original RAG
    print("\n📊 Testing Original RAG System...")
    print("-" * 40)
    
    try:
        original_rag = LawgorithmRAGInterface("vector_store_lawgorithm/vector_store.json")
        original_times = []
        
        for i, query in enumerate(test_queries[:2], 1):  # Test first 2 queries only
            print(f"Query {i}: {query[:50]}...")
            start_time = time.time()
            
            try:
                result = original_rag.query(query)
                end_time = time.time()
                query_time = end_time - start_time
                original_times.append(query_time)
                print(f"  ✅ Completed in {query_time:.2f}s")
            except Exception as e:
                print(f"  ❌ Failed: {e}")
                original_times.append(float('inf'))
        
        avg_original_time = sum(original_times) / len(original_times) if original_times else float('inf')
        print(f"Average original time: {avg_original_time:.2f}s")
        
    except Exception as e:
        print(f"❌ Original RAG failed to initialize: {e}")
        avg_original_time = float('inf')
    
    # Test optimized RAG
    print("\n📊 Testing Optimized RAG System...")
    print("-" * 40)
    
    try:
        optimized_rag = OptimizedLawgorithmRAGInterface("vector_store_lawgorithm/vector_store.json")
        optimized_times = []
        
        for i, query in enumerate(test_queries, 1):
            print(f"Query {i}: {query[:50]}...")
            start_time = time.time()
            
            try:
                result = optimized_rag.query(query)
                end_time = time.time()
                query_time = end_time - start_time
                optimized_times.append(query_time)
                print(f"  ✅ Completed in {query_time:.2f}s")
                print(f"  📋 Response preview: {result['response'][:100]}...")
                print(f"  📚 Sources: {result['total_sources']}")
            except Exception as e:
                print(f"  ❌ Failed: {e}")
                optimized_times.append(float('inf'))
        
        avg_optimized_time = sum(optimized_times) / len(optimized_times) if optimized_times else float('inf')
        print(f"Average optimized time: {avg_optimized_time:.2f}s")
        
    except Exception as e:
        print(f"❌ Optimized RAG failed to initialize: {e}")
        avg_optimized_time = float('inf')
    
    # Performance comparison
    print("\n📈 Performance Comparison Results")
    print("=" * 40)
    
    if avg_original_time != float('inf') and avg_optimized_time != float('inf'):
        speedup = avg_original_time / avg_optimized_time
        improvement = ((avg_original_time - avg_optimized_time) / avg_original_time) * 100
        
        print(f"Original RAG average time: {avg_original_time:.2f}s")
        print(f"Optimized RAG average time: {avg_optimized_time:.2f}s")
        print(f"Speedup: {speedup:.2f}x faster")
        print(f"Improvement: {improvement:.1f}% faster")
        
        if speedup > 1.5:
            print("🎉 Significant performance improvement achieved!")
        elif speedup > 1.1:
            print("✅ Moderate performance improvement achieved!")
        else:
            print("⚠️ Minimal performance improvement - may need further optimization")
    else:
        print("❌ Could not complete performance comparison due to errors")
    
    # Test optimized RAG features
    print("\n🔧 Testing Optimized RAG Features...")
    print("-" * 40)
    
    try:
        # Test caching
        print("Testing caching...")
        start_time = time.time()
        result1 = optimized_rag.query("test query for caching")
        first_time = time.time() - start_time
        
        start_time = time.time()
        result2 = optimized_rag.query("test query for caching")  # Same query
        second_time = time.time() - start_time
        
        if second_time < first_time * 0.5:  # Should be much faster due to caching
            print(f"✅ Caching working: {first_time:.2f}s → {second_time:.2f}s")
        else:
            print(f"⚠️ Caching may not be working optimally: {first_time:.2f}s → {second_time:.2f}s")
        
        # Test FAISS
        if hasattr(optimized_rag, 'faiss_index') and optimized_rag.faiss_index is not None:
            print("✅ FAISS HNSW index is active")
        else:
            print("ℹ️ Using numpy-based search (small dataset)")
            
    except Exception as e:
        print(f"❌ Feature test failed: {e}")

if __name__ == "__main__":
    test_performance_comparison() 