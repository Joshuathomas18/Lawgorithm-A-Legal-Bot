# Legal RAG Chatbot

A structured RAG (Retrieval-Augmented Generation) system for legal document analysis using trained FAISS indexes and Ollama.

## Features

- 🤖 **Dual RAG System**: Structure + Content search
- 📚 **445,938 trained legal documents**
- 🧠 **lawgorithm:latest model integration**
- 🔍 **FAISS vector search**
- 💬 **Interactive chat interface**

## Quick Start

### 1. Prerequisites

- Python 3.8+
- Ollama installed and running
- lawgorithm:latest model installed

### 2. Install Dependencies

```bash
cd legal_rag_chatbot
pip install -r requirements.txt
```

### 3. Start Ollama

```bash
ollama serve
```

### 4. Run the Chatbot

```bash
python main.py
```

## Usage

### Interactive Mode

```bash
python main.py
```

Commands:
- `ask <question>` - Ask a legal question
- `search <query>` - Search documents only
- `stats` - Show system statistics
- `help` - Show help
- `quit` - Exit

### Command Line Mode

```bash
# Test the system
python main.py test

# Show statistics
python main.py stats
```

## Example Queries

```
ask What are the grounds for filing a writ petition?
ask How to resolve contract disputes?
search constitutional rights
search criminal procedure
```

## Architecture

Based on [LocalAIAgentWithRAG](https://github.com/techwithtim/LocalAIAgentWithRAG):

- `vector_store.py` - FAISS index management
- `ollama_client.py` - Ollama API integration
- `rag_agent.py` - Main RAG agent logic
- `main.py` - Interactive interface

## Data Sources

- **Content Documents**: 445,938 legal document chunks
- **Structure Documents**: 1,508 legal structure chunks
- **Trained Indexes**: Pre-built FAISS indexes for fast retrieval

## License

MIT License 