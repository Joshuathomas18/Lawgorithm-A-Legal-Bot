# 🧠 Petition Bot Fine-Tuning System

A complete pipeline to fine-tune the **OPT-1.3B** model on Indian court petition data and build a domain-specific chatbot with RAG capabilities.

---

## 📁 Project Structure

```
.
├── preprocessing/
│   └── data_processor.py       # Preprocess petition CSV data
├── training/
│   └── fine_tuner.py           # Fine-tunes OPT-1.3B with LoRA (PEFT)
├── inference/
│   └── petition_bot.py         # PetitionBot class for inference
├── petition_data/
│   ├── raw/                    # Unprocessed court petitions
│   └── processed/              # Cleaned CSV + fine-tune ready data
├── fine_tuned_model/           # Saved model weights
├── conversations/              # Chat history logs
└── requirements.txt            # Python dependencies
```

---

## ⚙️ Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Prepare Petition Data

- Place CSV file at: `petition_data/processed/petitions.csv`
- Required columns:
  - `petition_id`, `title`, `court`, `date`, `judges`, `citations`, `url`

---

## 🛠️ Usage

### 🔹 Step 1: Preprocess the Data

```bash
python preprocessing/data_processor.py
```

- Loads petitions
- Creates instruction-response pairs
- Embeds text
- Outputs: `petition_data/processed/finetuning_data.json`

---

### 🔹 Step 2: Fine-Tune the Model

```bash
python training/fine_tuner.py
```

- Loads processed JSON
- Fine-tunes OPT-1.3B using LoRA (via PEFT)
- Outputs model to `fine_tuned_model/`

---

### 🔹 Step 3: Run the Petition Bot

```python
from inference.petition_bot import PetitionBot

bot = PetitionBot()
response = bot.generate_response(
    instruction="What is the title of the petition with ID 154721154?",
    query_type="basic"
)
print(response['response'])
```

---

## 🧩 Features

- ✅ Parameter-Efficient Fine-Tuning (LoRA via PEFT)
- ✅ Disclaimer auto-injection for legal answers
- ✅ RAG-enabled via LangChain-style prompting
- ✅ Diagram-aware preprocessing and formatting
- ✅ Structured JSON/CSV outputs for downstream use
- ✅ GPU acceleration + error handling

---

## 🔎 What is RAG? (Retrieval-Augmented Generation)

Retrieval-Augmented Generation bridges the gap between LLMs and real-time, domain-specific knowledge.

### 📌 RAG Workflow

1. **Prompt:** User asks: *"Draft argument against Land Acquisition Act, 2013"*
2. **Query Generation:** LLM generates search query: *"Land Acquisition Act 2013, natural justice, validity"*
3. **Vector Search:** Query is embedded + matched against indexed legal texts (e.g., judgments)
4. **Context Retrieval:** Relevant docs (e.g., *Krishna Kant vs. Mysore Municipality*) are appended to prompt
5. **Answer Generation:** LLM uses the augmented prompt to generate a grounded legal response

### ⚙️ Tech Stack for RAG

- **Embedding Models:** Sentence-BERT, OpenAI Embeddings, etc.
- **Vector DBs:** ChromaDB, Pinecone, Weaviate, Milvus
- **Hybrid Retrieval:** Optional keyword + dense search combo

### 🔁 Diagram

```mermaid
graph TD;
    A[User Prompt] --> B{LLM (Query Generation)}
    B --> C[Vector DB Search]
    C --> D[Retrieved Context]
    D --> E[Augmented Prompt]
    E --> F[LLM (Final Response)]
```

---

## 📦 Model Details

- **Base Model:** OPT-1.3B
- **Fine-tuning:** LoRA (Low-Rank Adaptation)
- **Context Length:** 2048 tokens
- **Precision:** Mixed FP16

---

## 🛡️ Safety & Legal

- ⚠️ Not a substitute for legal advice
- ⚖️ Includes automatic disclaimers
- 📚 Cites sources when generating legal summaries
- 📉 Offers confidence scores for responses

---

## 💻 System Requirements

- Python 3.8+
- CUDA-enabled GPU (recommended)
- 16 GB+ RAM
- 50 GB+ disk space

---

## 📌 Notes

- This tool is for **research & informational** purposes only
- Fine-tuned model is not legally certified or production-secure
- Always validate legal outputs with certified professionals
```
}
