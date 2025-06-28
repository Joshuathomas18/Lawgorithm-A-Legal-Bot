# RAG + Ollama Integration for Legal Petition System

Clean integration of RAG (Retrieval-Augmented Generation) with Ollama for legal petition generation, based on the [LocalAIAgentWithRAG](https://github.com/techwithtim/LocalAIAgentWithRAG) pattern.

## 🏗️ Architecture

```
User Query → Vector Store Search → Context Extraction → Ollama Generation → Response
```

## 📁 Structure

```
rag_ollama_integration/
├── __init__.py              # Package initialization
├── main.py                  # Main RAG agent
├── vector_store.py          # Vector store implementation
├── ollama_client.py         # Ollama API client
├── data_loader.py           # Data loading utilities
├── requirements.txt         # Dependencies
└── README.md               # This file
```

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r rag_ollama_integration/requirements.txt
```

### 2. Load Your Data
```bash
python -m rag_ollama_integration.data_loader
```

### 3. Run the RAG Agent
```bash
python -m rag_ollama_integration.main
```

## 🔧 Components

### LegalRAGAgent
Main agent that orchestrates the RAG + Ollama workflow.

### VectorStore
Handles document storage, embedding generation, and similarity search.

### OllamaClient
Clean interface to Ollama API with proper error handling.

### LegalDataLoader
Converts existing RAG data to the new vector store format.

## 💡 Usage Examples

```python
from rag_ollama_integration import LegalRAGAgent

# Initialize agent
agent = LegalRAGAgent()

# Query the system
result = agent.query("Draft a Supreme Court petition for a dowry case")
print(result['response'])
```

## 🎯 Features

- ✅ Clean separation of concerns
- ✅ Proper error handling
- ✅ Logging and monitoring
- ✅ Easy data loading
- ✅ Scalable architecture
- ✅ Based on proven patterns

## 🔄 Integration with Existing System

This integration works alongside your existing dual RAG system and provides a cleaner interface for Ollama integration.

## 📊 Performance

- Vector search: ~0.1-0.5s
- Ollama generation: ~2-5s
- Total response time: ~2-6s

## 🛠️ Configuration

The system uses your existing:
- 445,938 content documents
- 1,508 structure documents
- `lawgorithm:latest` model 