#!/usr/bin/env python3
"""
Ollama Client for Legal RAG System
==================================

Based on LocalAIAgentWithRAG Ollama integration.
"""

import requests
import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class OllamaClient:
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "lawgorithm:latest"):
        """Initialize Ollama client"""
        self.base_url = base_url
        self.model = model
        self.session = requests.Session()
        
    def test_connection(self) -> bool:
        """Test if Ollama is running and model is available"""
        try:
            # Check if Ollama is running
            response = self.session.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code != 200:
                logger.error(f"Ollama connection failed: {response.status_code}")
                return False
            
            # Check if model is available
            models = response.json().get('models', [])
            model_names = [model['name'] for model in models]
            
            if self.model not in model_names:
                logger.warning(f"Model {self.model} not found. Available: {model_names}")
                return False
            
            logger.info(f"✅ Connected to Ollama with model: {self.model}")
            return True
            
        except Exception as e:
            logger.error(f"Ollama connection error: {e}")
            return False
    
    def generate(self, prompt: str, context: str = "", max_tokens: int = 1000) -> str:
        """Generate response using Ollama"""
        try:
            # Prepare the full prompt with context
            if context:
                full_prompt = f"""Context: {context}

Question: {prompt}

Please provide a comprehensive legal answer based on the context provided. If the context doesn't contain relevant information, say so clearly."""
            else:
                full_prompt = prompt
            
            # Make request to Ollama
            payload = {
                "model": self.model,
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "num_predict": max_tokens,
                    "temperature": 0.7,
                    "top_p": 0.9
                }
            }
            
            response = self.session.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '')
            else:
                logger.error(f"Ollama generation failed: {response.status_code}")
                return f"Error: Failed to generate response (Status: {response.status_code})"
                
        except Exception as e:
            logger.error(f"Ollama generation error: {e}")
            return f"Error: {str(e)}"
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model"""
        try:
            response = self.session.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                for model in models:
                    if model['name'] == self.model:
                        return model
            return {}
        except Exception as e:
            logger.error(f"Error getting model info: {e}")
            return {} 