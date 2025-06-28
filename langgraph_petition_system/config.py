"""
Configuration for LangGraph Petition System
"""

from enum import Enum
from typing import Dict, List, Any

class Jurisdiction(Enum):
    SUPREME_COURT = "SC"
    HIGH_COURT = "HC"
    DISTRICT_COURT = "DC"
    SPECIALIZED_TRIBUNAL = "ST"
    CONSUMER_COURT = "CC"

class PetitionType(Enum):
    PUBLIC_INTEREST_LITIGATION = "PIL"
    CIVIL_PETITION = "CIVIL"
    CRIMINAL_PETITION = "CRIMINAL"
    WRIT_PETITION = "WRIT"
    SPECIAL_LEAVE_PETITION = "SLP"

# Jurisdiction configurations
JURISDICTION_CONFIG = {
    Jurisdiction.SUPREME_COURT: {
        "name": "Supreme Court of India",
        "focus": ["constitutional_law", "precedents", "slp"],
        "formatting": "formal_constitutional",
        "required_sections": ["title", "parties", "facts", "grounds", "relief", "verification"]
    },
    Jurisdiction.HIGH_COURT: {
        "name": "High Court",
        "focus": ["writ_jurisdiction", "appellate", "state_law"],
        "formatting": "formal_appellate",
        "required_sections": ["title", "parties", "facts", "grounds", "relief", "verification"]
    },
    Jurisdiction.DISTRICT_COURT: {
        "name": "District Court",
        "focus": ["civil_trial", "criminal_trial", "evidence"],
        "formatting": "trial_court",
        "required_sections": ["title", "parties", "facts", "grounds", "relief", "verification"]
    },
    Jurisdiction.SPECIALIZED_TRIBUNAL: {
        "name": "Specialized Tribunal",
        "focus": ["administrative_law", "technical_expertise"],
        "formatting": "tribunal_specific",
        "required_sections": ["title", "parties", "facts", "grounds", "relief", "verification"]
    },
    Jurisdiction.CONSUMER_COURT: {
        "name": "Consumer Court",
        "focus": ["consumer_protection", "simplified_language"],
        "formatting": "consumer_friendly",
        "required_sections": ["title", "parties", "facts", "grounds", "relief", "verification"]
    }
}

# Petition type configurations
PETITION_TYPE_CONFIG = {
    PetitionType.PUBLIC_INTEREST_LITIGATION: {
        "name": "Public Interest Litigation",
        "focus": ["public_interest", "constitutional_rights", "social_justice"],
        "structure": "pil_specific",
        "language": "formal_public_interest"
    },
    PetitionType.CIVIL_PETITION: {
        "name": "Civil Petition",
        "focus": ["civil_disputes", "contracts", "property"],
        "structure": "civil_specific",
        "language": "formal_civil"
    },
    PetitionType.CRIMINAL_PETITION: {
        "name": "Criminal Petition",
        "focus": ["criminal_law", "evidence", "procedure"],
        "structure": "criminal_specific",
        "language": "formal_criminal"
    },
    PetitionType.WRIT_PETITION: {
        "name": "Writ Petition",
        "focus": ["constitutional_remedies", "fundamental_rights"],
        "structure": "writ_specific",
        "language": "formal_constitutional"
    },
    PetitionType.SPECIAL_LEAVE_PETITION: {
        "name": "Special Leave Petition",
        "focus": ["supreme_court_appeal", "constitutional_questions"],
        "structure": "slp_specific",
        "language": "formal_supreme_court"
    }
}

# Data collection configuration
DATA_CONFIG = {
    "total_cases": 250,
    "jurisdictions": 5,
    "cases_per_jurisdiction_type": 10,
    "petition_types": 5,
    "api_source": "indian_kanoon",
    "embedding_models": {
        "structure": "sentence-transformers/all-MiniLM-L6-v2",
        "content": "sentence-transformers/all-mpnet-base-v2"
    },
    "vector_stores": {
        "structure": "structure_embeddings.db",
        "content": "content_embeddings.db"
    }
}

# LangGraph configuration
LANGRAPH_CONFIG = {
    "max_retries": 3,
    "timeout": 30,
    "state_persistence": True,
    "debug_mode": True
}

# LLM configuration
LLM_CONFIG = {
    "model": "lawgorithm:latest",
    "temperature": 0.7,
    "max_tokens": 4000,
    "top_p": 0.9
} 