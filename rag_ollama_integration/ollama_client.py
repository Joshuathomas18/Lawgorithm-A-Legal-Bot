#!/usr/bin/env python3
"""
Ollama Client for Legal RAG System
==================================

Clean Ollama integration based on LocalAIAgentWithRAG pattern.
"""

import requests
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class OllamaClient:
    def __init__(self, model_name: str = "lawgorithm:latest", base_url: str = "http://localhost:11434"):
        """Initialize Ollama client"""
        self.model_name = model_name
        self.base_url = base_url
        
        # Test connection
        self.test_connection()
    
    def test_connection(self) -> bool:
        """Test if Ollama is running and model is available"""
        try:
            # Test if Ollama is running
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code != 200:
                logger.error(f"Ollama not responding: {response.status_code}")
                return False
            
            # Test if model is available
            models = response.json().get('models', [])
            model_names = [model['name'] for model in models]
            
            if self.model_name in model_names:
                logger.info(f"✅ Ollama connection successful, {self.model_name} available")
                return True
            else:
                logger.warning(f"⚠️ {self.model_name} not found. Available: {model_names}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Ollama connection failed: {e}")
            return False
    
    def generate_response(self, question: str, context: str = "") -> str:
        """Generate response using Ollama"""
        try:
            # Create prompt with context
            if context:
                prompt = f"""You are Lawgorithm, a specialized legal AI assistant trained on Indian law.

LEGAL CONTEXT:
{context}

USER QUESTION:
{question}

Please provide a comprehensive legal answer based on the context provided. If this is a request for drafting a legal document, please provide the complete document with proper legal structure and language."""
            else:
                prompt = f"""You are Lawgorithm, a specialized legal AI assistant trained on Indian law.

USER QUESTION:
{question}

Please provide a comprehensive legal answer. If this is a request for drafting a legal document, please provide the complete document with proper legal structure and language."""
            
            # Make API call to Ollama
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "top_k": 40,
                        "max_tokens": 2000,
                        "repeat_penalty": 1.1
                    }
                },
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get('response', 'No response generated')
                
                # Check for error responses
                if "I am a large language model, trained by Google" in response_text:
                    return "I apologize, but I'm experiencing technical difficulties with my legal knowledge base. Please try again."
                
                return response_text
            else:
                logger.error(f"Ollama API error: {response.status_code} - {response.text}")
                return f"Error: {response.status_code} - {response.text}"
                
        except requests.exceptions.Timeout:
            logger.error("Ollama request timed out")
            return "Request timed out. Please try again."
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return f"Error generating response: {str(e)}"
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                for model in models:
                    if model['name'] == self.model_name:
                        return {
                            'name': model['name'],
                            'size': model.get('size', 0),
                            'modified_at': model.get('modified_at', ''),
                            'available': True
                        }
            
            return {'name': self.model_name, 'available': False}
            
        except Exception as e:
            logger.error(f"Error getting model info: {e}")
            return {'name': self.model_name, 'available': False}
    
    def list_models(self) -> list:
        """List all available models"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                return [model['name'] for model in models]
            return []
            
        except Exception as e:
            logger.error(f"Error listing models: {e}")
            return [] 