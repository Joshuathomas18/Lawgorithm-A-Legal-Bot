#!/usr/bin/env python3
"""
Debug RAG System
================

Debug script to see what RAG documents are being retrieved and how they're being used.
"""

import sys
import os

# Add the current directory to Python path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag.lawgorithm_rag_interface import LawgorithmRAGInterface

def debug_rag():
    """Debug the RAG system to see what's happening"""
    print("🔍 DEBUGGING RAG SYSTEM")
    print("=" * 50)
    
    # Initialize the RAG interface
    rag = LawgorithmRAGInterface("vector_store_lawgorithm/vector_store.json")
    
    # Test query similar to what the petition automator uses
    test_query = """
Write a legal petition for this case:

CASE DETAILS:
- Case Type: criminal
- Court: supreme
- Petitioner: Mrs. Ananya Mehta
- Respondent: Mr. Devansh Kapoor
- Incident Date: April 10, 2025
- Filing Date: June 18, 2025
- Case Number: CR-2025-001

FACTS OF THE CASE:
The petitioner alleges that her husband's death was pre-meditated murder.

EVIDENCE:
Threatening emails, forensic evidence, witness statements.

RELIEF SOUGHT:
Full criminal trial and charges under Section 302 IPC.

LEGAL GROUNDS:
Section 302 IPC (Murder), Section 120B IPC (Conspiracy).

Write a complete legal petition using proper legal language and format.
"""
    
    print("🔍 Searching for similar documents...")
    similar_docs = rag.search_similar(test_query, top_k=3)
    
    print(f"\n📄 Found {len(similar_docs)} similar documents:")
    print("-" * 50)
    
    for i, doc in enumerate(similar_docs, 1):
        print(f"\n📋 Document {i}:")
        print(f"   Similarity Score: {doc['similarity']:.4f}")
        print(f"   Metadata: {doc['metadata']}")
        print(f"   Content Preview: {doc['document'][:200]}...")
        print("-" * 30)
    
    print("\n🔍 Now testing full RAG query...")
    result = rag.query(test_query, top_k=3)
    
    print(f"\n📊 RAG Query Result:")
    print(f"   Total sources used: {result['total_sources']}")
    print(f"   Response length: {len(result['response'])} characters")
    print(f"   Response preview: {result['response'][:300]}...")
    
    print("\n🔍 Context that was sent to LLM:")
    print("-" * 50)
    
    # Reconstruct the context that was sent
    contexts = []
    for doc in result['context_sources']:
        doc_text = doc['document'][:500] if len(doc['document']) > 500 else doc['document']
        contexts.append(doc_text)
    
    context = "\n\n".join(contexts)
    print(f"Context length: {len(context)} characters")
    print(f"Context preview: {context[:500]}...")
    
    print("\n🔍 Full prompt sent to LLM:")
    print("-" * 50)
    full_prompt = f"""
LEGAL CONTEXT:
{context}

QUESTION:
{test_query}

Answer this legal question.
"""
    print(full_prompt)

if __name__ == "__main__":
    debug_rag() 