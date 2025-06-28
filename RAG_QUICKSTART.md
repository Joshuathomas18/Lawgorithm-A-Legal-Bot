# RAG Quick Start Guide 🚀

## What We Just Built

I've created a complete RAG (Retrieval-Augmented Generation) system for your petition automation project! Here's what you now have:

### 📁 New Files Created:
- `rag/vector_store.py` - Vector database for storing petition embeddings
- `rag/prepare_embeddings.py` - Script to prepare and index petition data
- `inference/rag_petition_bot.py` - RAG-enhanced petition bot
- `test_rag_setup.py` - Test script to verify everything works
- `rag_implementation_plan.md` - Detailed implementation plan
- `RAG_QUICKSTART.md` - This guide

### 🔧 Updated Files:
- `requirements.txt` - Added RAG dependencies
- `README.md` - Added RAG explanation and diagram

## 🚀 Quick Start (5 Minutes)

### Step 1: Install Dependencies
```bash
pip install chromadb sentence-transformers faiss-cpu
```

### Step 2: Test the Setup
```bash
python test_rag_setup.py
```

### Step 3: Prepare Your Data (if you have petition data)
```bash
python rag/prepare_embeddings.py
```

### Step 4: Test the RAG Bot
```bash
python inference/rag_petition_bot.py
```

## 🎯 How It Works

1. **Vector Database**: Your petition data gets converted into numerical embeddings
2. **Query Processing**: When you ask a question, it finds the most relevant petitions
3. **Context Augmentation**: Relevant petition info gets added to your question
4. **Enhanced Response**: The LLM generates a response using both your question AND the relevant petition context

## 📊 Example Queries to Test

```python
# Test these queries with your RAG bot:
queries = [
    "What are the key arguments in land acquisition cases?",
    "Find petitions related to fundamental rights violations", 
    "What is the procedure for filing a writ petition?",
    "Show me cases about environmental protection"
]
```

## 🔍 What Makes This Special

### Before RAG:
- Bot gives generic responses based on training data
- No access to specific petition details
- Limited to pre-trained knowledge

### After RAG:
- Bot finds relevant petitions from your database
- Provides specific case examples and precedents
- Context-aware responses based on actual petition data
- Can handle new petitions without retraining

## 🛠️ Customization Options

### Change Embedding Model:
```python
# In rag/vector_store.py
vector_store = PetitionVectorStore(model_name="all-mpnet-base-v2")  # Better but slower
```

### Adjust Search Results:
```python
# In inference/rag_petition_bot.py
context = self._retrieve_relevant_context(instruction, n_results=5)  # More context
```

### Use Different LLM:
```python
# In inference/rag_petition_bot.py
bot = RAGPetitionBot(
    api_key="your-key",
    model="anthropic/claude-3-sonnet"  # Different model
)
```

## 📈 Performance Tips

1. **Start Small**: Test with 100-1000 petitions first
2. **Monitor Response Times**: RAG adds ~1-2 seconds to responses
3. **Tune Context Length**: More context = better responses but slower
4. **Cache Embeddings**: Vector database persists between runs

## 🐛 Troubleshooting

### "ChromaDB import failed"
```bash
pip install chromadb --upgrade
```

### "No petition data found"
- Make sure `petition_data/processed/petitions.csv` exists
- Run `python rag/prepare_embeddings.py` first

### "API request failed"
- Check your OpenRouter API key
- Verify internet connection

## 🎉 Next Steps

1. **Test with your data**: Run the scripts with your petition dataset
2. **Compare responses**: Test RAG vs non-RAG bot responses
3. **Fine-tune**: Adjust embedding model, context length, etc.
4. **Scale up**: Add more petition data and optimize performance

## 💡 Pro Tips

- **Hybrid Search**: Combine semantic + keyword search for better results
- **Query Enhancement**: Add legal terms to improve retrieval
- **Caching**: Cache frequently asked queries
- **Monitoring**: Track which petitions are most relevant

Ready to revolutionize your petition bot? Start with `python test_rag_setup.py` and let me know how it goes! 🚀 