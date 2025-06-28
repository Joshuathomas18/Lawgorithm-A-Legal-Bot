import json
import os
from vector_store import PetitionVectorStore
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def prepare_instruction_dataset_embeddings():
    """Prepare embeddings from better_instruction_dataset.json for RAG."""
    json_path = 'petition_data/processed/better_instruction_dataset.json'
    if not os.path.exists(json_path):
        logger.error(f"Dataset not found: {json_path}")
        return
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    logger.info(f"Loaded {len(data)} instruction-response pairs from JSON.")
    
    # Prepare data for vector store
    docs = []
    for idx, entry in enumerate(data):
        docs.append({
            'petition_id': str(idx),
            'title': entry.get('instruction', '')[:80],
            'court': '',
            'date': '',
            'content': entry.get('instruction', ''),
            'answer': entry.get('output', '')
        })
        if (idx + 1) % 500 == 0:
            logger.info(f"Prepared {idx + 1} entries...")
    logger.info(f"Prepared {len(docs)} entries for vector database.")
    
    # Initialize vector store
    vector_store = PetitionVectorStore()
    logger.info("Adding entries to vector database...")
    vector_store.add_petitions(docs)
    info = vector_store.get_collection_info()
    logger.info(f"Vector database now contains {info['count']} documents.")
    return vector_store

def test_vector_search():
    logger.info("Testing vector search...")
    vector_store = PetitionVectorStore()
    test_queries = [
        "title of petition 10112739",
        "court is petition 105925409 filed in",
        "summary of petition 109930655"
    ]
    for query in test_queries:
        logger.info(f"\nTesting query: '{query}'")
        results = vector_store.search(query, n_results=3)
        if results['documents']:
            for i, doc in enumerate(results['documents'][0]):
                metadata = results['metadatas'][0][i]
                logger.info(f"Result {i+1}: {metadata['title']}")
        else:
            logger.info("No results found")

if __name__ == "__main__":
    vector_store = prepare_instruction_dataset_embeddings()
    test_vector_search() 