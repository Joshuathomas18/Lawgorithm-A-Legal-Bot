#!/usr/bin/env python3
"""
Configuration Settings
======================

Environment configuration for the Petition Automator backend.
"""

import os
from typing import Optional

class Settings:
    # Application settings
    APP_NAME: str = "Petition Automator API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Server settings
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # Database settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "petition_automator.db")
    
    # RAG settings
    VECTOR_STORE_PATH: str = os.getenv(
        "VECTOR_STORE_PATH", 
        "rag/vector_store_lawgorithm/vector_store.json"
    )
    
    # Gemini settings
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "AIzaSyDU7A5_eFsZrtVW20_nVoKFGQ139sRf6IY")
    GEMINI_MODEL_NAME: str = os.getenv("GEMINI_MODEL_NAME", "gemini-2.5-flash")
    
    # Session settings
    SESSION_TIMEOUT_HOURS: int = int(os.getenv("SESSION_TIMEOUT_HOURS", "24"))
    
    # Document settings
    DOCUMENT_BASE_PATH: str = os.getenv("DOCUMENT_BASE_PATH", "static/documents")
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", "10485760"))  # 10MB
    
    # CORS settings
    CORS_ORIGINS: list = os.getenv("CORS_ORIGINS", "*").split(",")
    
    # Logging settings
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Security settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
    
    @classmethod
    def get_database_url(cls) -> str:
        """Get database URL with fallback"""
        return cls.DATABASE_URL
    
    @classmethod
    def get_vector_store_path(cls) -> str:
        """Get vector store path with validation"""
        path = cls.VECTOR_STORE_PATH
        if not os.path.exists(path):
            raise FileNotFoundError(f"Vector store not found: {path}")
        return path
    
    @classmethod
    def get_gemini_config(cls) -> dict:
        """Get Gemini configuration"""
        return {
            "api_key": cls.GEMINI_API_KEY,
            "model_name": cls.GEMINI_MODEL_NAME
        }
    
    @classmethod
    def get_cors_config(cls) -> dict:
        """Get CORS configuration"""
        return {
            "allow_origins": cls.CORS_ORIGINS,
            "allow_credentials": True,
            "allow_methods": ["*"],
            "allow_headers": ["*"]
        }

# Global settings instance
settings = Settings() 