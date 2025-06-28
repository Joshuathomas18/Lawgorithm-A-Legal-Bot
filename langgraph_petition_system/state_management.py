"""
State Management for LangGraph Petition System
"""

from typing import TypedDict, List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from langgraph_petition_system.config import Jurisdiction, PetitionType

class PetitionState(TypedDict):
    """Main state object for LangGraph petition generation"""
    # Input data
    user_input: str
    jurisdiction: Jurisdiction
    petition_type: PetitionType
    case_details: Dict[str, Any]
    
    # RAG retrieval results
    structure_chunks: List[Dict[str, Any]]
    content_chunks: List[Dict[str, Any]]
    
    # Processing data
    final_prompt: str
    llm_output: str
    validated_output: str
    
    # Metadata
    session_id: str
    timestamp: str
    errors: Optional[str]
    processing_steps: List[str]

class CaseDetails(BaseModel):
    """Structured case details model"""
    petitioner_name: str = Field(..., description="Name of the petitioner")
    respondent_name: str = Field(..., description="Name of the respondent")
    incident_date: str = Field(..., description="Date of incident")
    filing_date: str = Field(..., description="Date of filing")
    case_number: Optional[str] = Field(None, description="Case number if available")
    facts: str = Field(..., description="Facts of the case")
    evidence: str = Field(..., description="Evidence available")
    relief: str = Field(..., description="Relief sought")
    legal_grounds: str = Field(..., description="Legal grounds for the petition")

class RAGChunk(BaseModel):
    """Model for RAG retrieved chunks"""
    content: str = Field(..., description="Content of the chunk")
    source: str = Field(..., description="Source document")
    score: float = Field(..., description="Relevance score")
    chunk_type: str = Field(..., description="Type of chunk (structure/content)")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class ProcessingStep(BaseModel):
    """Model for tracking processing steps"""
    step_name: str = Field(..., description="Name of the processing step")
    timestamp: str = Field(..., description="Timestamp of the step")
    status: str = Field(..., description="Status (success/error)")
    details: Optional[str] = Field(None, description="Additional details")

class StateManager:
    """Manages state transitions and validation"""
    
    def __init__(self):
        self.state_history: List[PetitionState] = []
    
    def create_initial_state(self, user_input: str, jurisdiction: Jurisdiction, 
                           petition_type: PetitionType, case_details: Dict[str, Any]) -> PetitionState:
        """Create initial state for petition generation"""
        session_id = f"petition_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        initial_state: PetitionState = {
            "user_input": user_input,
            "jurisdiction": jurisdiction,
            "petition_type": petition_type,
            "case_details": case_details,
            "structure_chunks": [],
            "content_chunks": [],
            "final_prompt": "",
            "llm_output": "",
            "validated_output": "",
            "session_id": session_id,
            "timestamp": datetime.now().isoformat(),
            "errors": None,
            "processing_steps": []
        }
        
        self.state_history.append(initial_state)
        return initial_state
    
    def update_state(self, current_state: PetitionState, updates: Dict[str, Any]) -> PetitionState:
        """Update state with new information"""
        updated_state = current_state.copy()
        updated_state.update(updates)
        updated_state["timestamp"] = datetime.now().isoformat()
        
        self.state_history.append(updated_state)
        return updated_state
    
    def add_processing_step(self, state: PetitionState, step_name: str, 
                          status: str = "success", details: Optional[str] = None) -> PetitionState:
        """Add a processing step to the state"""
        step = ProcessingStep(
            step_name=step_name,
            timestamp=datetime.now().isoformat(),
            status=status,
            details=details
        )
        
        steps = state.get("processing_steps", [])
        steps.append(step.dict())
        
        return self.update_state(state, {"processing_steps": steps})
    
    def add_error(self, state: PetitionState, error_message: str) -> PetitionState:
        """Add error to state"""
        return self.update_state(state, {"errors": error_message})
    
    def validate_state(self, state: PetitionState) -> bool:
        """Validate state completeness"""
        required_fields = [
            "user_input", "jurisdiction", "petition_type", 
            "case_details", "session_id"
        ]
        
        for field in required_fields:
            if field not in state or not state[field]:
                return False
        
        return True
    
    def get_state_summary(self, state: PetitionState) -> Dict[str, Any]:
        """Get a summary of the current state"""
        return {
            "session_id": state["session_id"],
            "jurisdiction": state["jurisdiction"].value,
            "petition_type": state["petition_type"].value,
            "processing_steps": len(state.get("processing_steps", [])),
            "has_errors": bool(state.get("errors")),
            "rag_chunks": {
                "structure": len(state.get("structure_chunks", [])),
                "content": len(state.get("content_chunks", []))
            },
            "has_output": bool(state.get("validated_output")),
            "timestamp": state["timestamp"]
        }
    
    def save_state(self, state: PetitionState, filepath: str) -> bool:
        """Save state to file for debugging/audit"""
        try:
            import json
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(state, f, ensure_ascii=False, indent=2, default=str)
            return True
        except Exception as e:
            print(f"Error saving state: {e}")
            return False
    
    def load_state(self, filepath: str) -> Optional[PetitionState]:
        """Load state from file"""
        try:
            import json
            with open(filepath, 'r', encoding='utf-8') as f:
                state_data = json.load(f)
            
            # Convert string values back to enums
            state_data["jurisdiction"] = Jurisdiction(state_data["jurisdiction"])
            state_data["petition_type"] = PetitionType(state_data["petition_type"])
            
            return state_data
        except Exception as e:
            print(f"Error loading state: {e}")
            return None 