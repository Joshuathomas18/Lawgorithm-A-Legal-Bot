# Petition Automator Backend

A comprehensive FastAPI backend for AI-powered legal petition generation using RAG (Retrieval-Augmented Generation) and Ollama LLMs.

## 🚀 Features

- **AI-Powered Petition Generation**: Generate complete legal petitions using RAG and Ollama
- **Real-time Conversations**: Interactive chat with legal AI assistant
- **Document Management**: Export petitions in multiple formats (JSON, TXT, PDF)
- **Session Management**: Track user sessions and activity
- **Version Control**: Maintain petition versions and history
- **RESTful API**: Clean, documented API endpoints
- **Comprehensive Testing**: Unit and integration tests

## 📁 Project Structure

```
backend/
├── main.py                 # FastAPI application entry point
├── start.py               # Startup script
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── config/
│   └── settings.py       # Configuration settings
├── models/
│   ├── database.py       # Database models and repositories
│   └── schemas.py        # Pydantic schemas
├── services/
│   ├── rag_service.py    # RAG system integration
│   ├── ollama_service.py # Ollama LLM integration
│   ├── petition_service.py # Petition generation logic
│   ├── conversation_service.py # Chat functionality
│   ├── document_service.py # Document operations
│   └── session_service.py # Session management
├── views/
│   ├── petition_views.py # Petition API endpoints
│   ├── conversation_views.py # Conversation API endpoints
│   ├── document_views.py # Document API endpoints
│   └── health_views.py   # Health check endpoints
└── tests/
    ├── test_petition_service.py # Petition service tests
    ├── test_conversation_service.py # Conversation service tests
    └── test_api_endpoints.py # API integration tests
```

## 🛠️ Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd backend
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables** (optional):
   ```bash
   export DEBUG=True
   export OLLAMA_BASE_URL=http://localhost:11434
   export OLLAMA_MODEL_NAME=lawgorithm:latest
   ```

## 🚀 Quick Start

1. **Start the server**:
   ```bash
   python start.py
   ```

2. **Or use uvicorn directly**:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

3. **Access the API**:
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/api/v1/health
   - Root Endpoint: http://localhost:8000/

## 📚 API Endpoints

### Health Check
- `GET /api/v1/health` - Check API health status

### Petitions
- `POST /api/v1/petitions/` - Generate new petition
- `GET /api/v1/petitions/{petition_id}` - Get petition by ID
- `PUT /api/v1/petitions/{petition_id}` - Update petition
- `DELETE /api/v1/petitions/{petition_id}` - Delete petition
- `GET /api/v1/petitions/session/{session_id}` - Get session petitions

### Conversations
- `POST /api/v1/conversations/` - Create new conversation
- `GET /api/v1/conversations/{conversation_id}` - Get conversation
- `POST /api/v1/conversations/{conversation_id}/messages` - Add message
- `DELETE /api/v1/conversations/{conversation_id}` - Delete conversation
- `GET /api/v1/conversations/session/{session_id}` - Get session conversations

### Documents
- `POST /api/v1/documents/export/{petition_id}` - Export petition
- `GET /api/v1/documents/versions/{petition_id}` - Get document versions
- `GET /api/v1/documents/{document_id}` - Get specific document
- `DELETE /api/v1/documents/{document_id}` - Delete document

## 🔧 Configuration

The application uses environment variables for configuration. Key settings:

- `DEBUG`: Enable debug mode (default: False)
- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 8000)
- `OLLAMA_BASE_URL`: Ollama server URL (default: http://localhost:11434)
- `OLLAMA_MODEL_NAME`: Ollama model name (default: lawgorithm:latest)
- `VECTOR_STORE_PATH`: Path to RAG vector store
- `SESSION_TIMEOUT_HOURS`: Session timeout in hours (default: 24)

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=.

# Run specific test file
pytest tests/test_petition_service.py

# Run with verbose output
pytest -v
```

## 📝 Example Usage

### Generate a Petition

```python
import requests

# Create petition
response = requests.post("http://localhost:8000/api/v1/petitions/", json={
    "case_details": {
        "case_type": "Criminal",
        "court": "High Court",
        "petitioner_name": "John Doe",
        "respondent_name": "State",
        "brief_details": "Bail application",
        "plan_of_action": "Seek bail",
        "specific_details": "First-time offender"
    },
    "session_id": "user_session_123"
})

petition = response.json()
print(f"Generated petition: {petition['petition_id']}")
```

### Start a Conversation

```python
# Create conversation
response = requests.post("http://localhost:8000/api/v1/conversations/", json={
    "session_id": "user_session_123",
    "initial_message": "I need help with a criminal case"
})

conversation = response.json()
print(f"Conversation ID: {conversation['conversation_id']}")
```

## 🔒 Security

- CORS enabled for cross-origin requests
- Input validation using Pydantic schemas
- Rate limiting support (configurable)
- Session-based authentication (extensible)

## 📊 Monitoring

The application includes comprehensive logging:

- Request/response logging
- Error tracking
- Performance metrics
- Service health monitoring

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the API documentation at `/docs`
- Review the test files for usage examples 