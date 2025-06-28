# LangGraph Petition Generation System

A sophisticated legal petition generator using LangGraph with dual RAG systems for Indian legal documents.

## 🎯 Overview

This system implements a complete LangGraph workflow for generating legal petitions with the following features:

- **Dual RAG Systems**: Separate retrieval for document structure and legal content
- **Jurisdiction-Specific**: Support for 5 different court jurisdictions
- **Petition Types**: 5 different types of legal petitions
- **XML Prompt Generation**: Structured prompts for consistent LLM output
- **Error Recovery**: Built-in feedback loops for quality assurance
- **State Management**: Comprehensive tracking of the generation process

## 🏗️ Architecture

### Core Components

1. **State Management** (`state_management.py`)
   - TypedDict-based state definition
   - State validation and persistence
   - Processing step tracking

2. **Dual RAG Interface** (`rag_systems/dual_rag_interface.py`)
   - Structure-focused RAG for document templates
   - Content-focused RAG for legal arguments
   - Jurisdiction-aware retrieval

3. **XML Prompt Builder** (`prompts/xml_prompt_templates.py`)
   - Structured XML prompt generation
   - Template-based approach
   - Validation and error handling

4. **LangGraph Workflow** (`main/langgraph_petition_workflow.py`)
   - Complete workflow orchestration
   - 7-node processing pipeline
   - Conditional flow control

### Workflow Nodes

```
Input Processor → Dual RAG Retriever → Prompt Builder → LLM Generator → Output Validator → [Feedback Handler] → Output Formatter
```

## 📊 Data Structure

### Jurisdictions (5)
- **Supreme Court (SC)**: Constitutional law, precedents, SLP
- **High Court (HC)**: Writ jurisdiction, appellate, state law
- **District Court (DC)**: Civil/criminal trials, evidence
- **Specialized Tribunal (ST)**: Administrative law, technical expertise
- **Consumer Court (CC)**: Consumer protection, simplified language

### Petition Types (5)
- **Public Interest Litigation (PIL)**: Public interest, constitutional rights
- **Civil Petition (CIVIL)**: Civil disputes, contracts, property
- **Criminal Petition (CRIMINAL)**: Criminal law, evidence, procedure
- **Writ Petition (WRIT)**: Constitutional remedies, fundamental rights
- **Special Leave Petition (SLP)**: Supreme Court appeals, constitutional questions

### Data Collection
- **250 cases total**: 5 jurisdictions × 10 cases × 5 petition types
- **Source**: Indian Kanoon API
- **Processing**: Dual embedding for structure and content

## 🚀 Quick Start

### Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up the system:
```bash
# Create necessary directories
mkdir -p langgraph_petition_system/collected_data
mkdir -p langgraph_petition_system/logs
```

### Basic Usage

```python
from langgraph_petition_system.main.langgraph_petition_workflow import LangGraphPetitionWorkflow
from langgraph_petition_system.config import Jurisdiction, PetitionType

# Create workflow
workflow = LangGraphPetitionWorkflow()

# Define case details
case_details = {
    'petitioner_name': 'John Doe',
    'respondent_name': 'Jane Smith',
    'incident_date': '2024-01-15',
    'filing_date': '2024-02-01',
    'case_number': 'CR123/2024',
    'facts': 'The petitioner alleges breach of contract...',
    'evidence': 'Contract documents and correspondence...',
    'relief': 'Compensation for damages...',
    'legal_grounds': 'Breach of contract under Indian Contract Act...'
}

# Generate petition
result = workflow.generate_petition(
    user_input="Generate a civil petition for breach of contract",
    jurisdiction=Jurisdiction.HIGH_COURT,
    petition_type=PetitionType.CIVIL_PETITION,
    case_details=case_details
)

print(f"Success: {result['success']}")
print(f"Petition: {result['petition_text']}")
```

### Running Tests

```bash
python test_langgraph_system.py
```

## 📁 File Structure

```
langgraph_petition_system/
├── __init__.py
├── config.py                          # Configuration and enums
├── state_management.py                # State management system
├── data_processing/
│   └── indian_kanoon_collector.py    # Data collection from Indian Kanoon
├── rag_systems/
│   └── dual_rag_interface.py         # Dual RAG implementation
├── prompts/
│   └── xml_prompt_templates.py       # XML prompt generation
├── main/
│   └── langgraph_petition_workflow.py # Main LangGraph workflow
└── README.md
```

## 🔧 Configuration

### Environment Variables

```bash
# Optional: Indian Kanoon API key
INDIAN_KANOON_API_KEY=your_api_key_here

# LangGraph settings
LANGRAPH_DEBUG_MODE=true
LANGRAPH_STATE_PERSISTENCE=true
```

### Model Configuration

```python
# In config.py
LLM_CONFIG = {
    "model": "lawgorithm:latest",
    "temperature": 0.7,
    "max_tokens": 4000,
    "top_p": 0.9
}
```

## 📈 Performance Metrics

### Success Criteria
- **Retrieval Accuracy**: >90% relevant content from both RAG systems
- **Generation Quality**: >95% structurally correct legal documents
- **Performance**: <30 seconds end-to-end generation
- **Reliability**: <5% error rate in workflow execution

### Monitoring
- State persistence for debugging
- Processing step tracking
- Error logging and recovery
- Performance benchmarking

## 🔄 Workflow Details

### 1. Input Processing
- Validates user input and case details
- Creates initial state with session tracking
- Prepares data for RAG retrieval

### 2. Dual RAG Retrieval
- **Structure RAG**: Retrieves document templates, headers, legal phrases
- **Content RAG**: Retrieves case content, arguments, precedents
- Jurisdiction and petition type filtering

### 3. XML Prompt Building
- Combines RAG results into structured XML
- Includes jurisdiction-specific rules
- Validates prompt structure

### 4. LLM Generation
- Sends XML prompt to Ollama/Lawgorithm
- Maintains existing workflow compatibility
- Generates structured legal document

### 5. Output Validation
- Checks for required sections (FACTS, GROUNDS, RELIEF)
- Validates document length and structure
- Routes to feedback if validation fails

### 6. Feedback Loop (Optional)
- Handles validation errors
- Refines prompts based on feedback
- Re-routes to generation

### 7. Output Formatting
- Adds metadata and formatting
- Prepares final document
- Saves to database if needed

## 🛠️ Integration

### With Existing Ollama Service

The system is designed to integrate with your existing Ollama service:

```python
# In _call_llm method of LangGraphPetitionWorkflow
def _call_llm(self, xml_prompt: str) -> str:
    # Integrate with your existing ollama_service.py
    from backend.services.ollama_service import OllamaService
    
    ollama_service = OllamaService()
    return await ollama_service.generate_text(xml_prompt)
```

### With Existing RAG System

The dual RAG can be enhanced with your existing RAG system:

```python
# In dual_rag_interface.py
def _load_and_index_data(self):
    # Load your existing RAG data
    existing_rag_data = load_existing_rag_data()
    
    # Combine with new Indian Kanoon data
    combined_data = merge_rag_data(existing_rag_data, new_data)
    
    # Index combined data
    self.structure_rag.index_data(combined_data['structure'])
    self.content_rag.index_data(combined_data['content'])
```

## 🧪 Testing

### Unit Tests
- State management validation
- RAG retrieval accuracy
- XML prompt generation
- Workflow node testing

### Integration Tests
- End-to-end petition generation
- Error recovery scenarios
- Performance benchmarking

### Test Cases
- Civil petition (High Court)
- Criminal petition (District Court)
- PIL (Supreme Court)

## 📝 Output Format

### Generated Petition Structure
```
Generated by LangGraph Petition System
Session ID: petition_20240201_143022
Jurisdiction: HC
Petition Type: CIVIL
Generated at: 2024-02-01T14:30:22

[Complete legal petition with proper structure]
```

### State Summary
```json
{
  "session_id": "petition_20240201_143022",
  "jurisdiction": "HC",
  "petition_type": "CIVIL",
  "processing_steps": 7,
  "has_errors": false,
  "rag_chunks": {
    "structure": 5,
    "content": 5
  },
  "has_output": true,
  "timestamp": "2024-02-01T14:30:22"
}
```

## 🔮 Future Enhancements

### Phase 2 Features
- Advanced XML schemas for different petition types
- Multi-language support (Hindi, English)
- Integration with court filing systems
- Real-time collaboration features

### Phase 3 Features
- AI-powered legal research assistant
- Automated case law citation
- Document comparison and analysis
- Mobile application

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check the documentation
2. Review test cases
3. Open an issue with detailed information
4. Contact the development team

---

**Built with ❤️ for the Indian Legal System** 