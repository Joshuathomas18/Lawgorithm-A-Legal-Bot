"""
Models Module for Petition RAG System
====================================

This module handles different AI model integrations including:
- Ollama models (local)
- Google Gemini (cloud)
- OpenAI models (cloud)
- Model switching and fallback
"""

import requests
import json
import logging
import time
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod

class BaseModel(ABC):
    """Abstract base class for all AI models."""
    
    @abstractmethod
    def generate_response(self, prompt: str, **kwargs) -> str:
        """Generate response from prompt."""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if model is available."""
        pass

class OllamaModel(BaseModel):
    """Ollama model integration for local AI generation."""
    
    def __init__(self, model_name: str = "lawgorithm:latest", 
                 ollama_url: str = "http://localhost:11434"):
        """
        Initialize Ollama model.
        
        Args:
            model_name: Name of the Ollama model
            ollama_url: URL for Ollama API
        """
        self.model_name = model_name
        self.ollama_url = ollama_url
        self.logger = logging.getLogger(__name__)
        
        # Test connection on initialization
        self._test_connection()
    
    def _test_connection(self) -> bool:
        """Test connection to Ollama API."""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                model_names = [model['name'] for model in models]
                if self.model_name in model_names:
                    self.logger.info(f"✅ Ollama model {self.model_name} is available")
                    return True
                else:
                    self.logger.warning(f"⚠️ {self.model_name} not found. Available: {model_names}")
                    return False
            else:
                self.logger.error("❌ Cannot connect to Ollama")
                return False
        except Exception as e:
            self.logger.error(f"❌ Error testing Ollama connection: {e}")
            return False
    
    def is_available(self) -> bool:
        """Check if Ollama model is available."""
        return self._test_connection()
    
    def generate_response(self, prompt: str, **kwargs) -> str:
        """
        Generate response using Ollama API.
        
        Args:
            prompt: Input prompt
            **kwargs: Additional parameters (temperature, max_tokens, etc.)
            
        Returns:
            Generated response text
        """
        try:
            # Prepare request parameters
            params = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": kwargs.get("temperature", 0.7),
                    "top_p": kwargs.get("top_p", 0.9),
                    "max_tokens": kwargs.get("max_tokens", 1000)
                }
            }
            
            # Make API request
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=params,
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                generated_text = result.get('response', '')
                self.logger.info(f"✅ Generated {len(generated_text)} characters")
                return generated_text
            else:
                error_msg = f"Ollama API error: {response.status_code}"
                self.logger.error(error_msg)
                return f"Error: {error_msg}"
                
        except Exception as e:
            error_msg = f"Error generating response: {str(e)}"
            self.logger.error(error_msg)
            return f"Error: {error_msg}"

class GeminiModel(BaseModel):
    """Google Gemini model integration."""
    
    def __init__(self, api_key: str, model_name: str = "gemini-pro"):
        """
        Initialize Gemini model.
        
        Args:
            api_key: Google API key
            model_name: Gemini model name
        """
        self.api_key = api_key
        self.model_name = model_name
        self.logger = logging.getLogger(__name__)
        
        # Import Google Generative AI
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            self.genai = genai
            self.model = genai.GenerativeModel(model_name)
            self.logger.info(f"✅ Gemini model {model_name} initialized")
        except ImportError:
            self.logger.error("❌ google-generativeai not installed")
            self.model = None
        except Exception as e:
            self.logger.error(f"❌ Error initializing Gemini: {e}")
            self.model = None
    
    def is_available(self) -> bool:
        """Check if Gemini model is available."""
        return self.model is not None and self.api_key is not None
    
    def generate_response(self, prompt: str, **kwargs) -> str:
        """
        Generate response using Gemini API.
        
        Args:
            prompt: Input prompt
            **kwargs: Additional parameters
            
        Returns:
            Generated response text
        """
        if not self.is_available():
            return "Error: Gemini model not available"
        
        try:
            # Generate response
            response = self.model.generate_content(prompt)
            generated_text = response.text
            self.logger.info(f"✅ Generated {len(generated_text)} characters")
            return generated_text
            
        except Exception as e:
            error_msg = f"Error generating response: {str(e)}"
            self.logger.error(error_msg)
            return f"Error: {error_msg}"

class OpenAIModel(BaseModel):
    """OpenAI model integration."""
    
    def __init__(self, api_key: str, model_name: str = "gpt-3.5-turbo"):
        """
        Initialize OpenAI model.
        
        Args:
            api_key: OpenAI API key
            model_name: OpenAI model name
        """
        self.api_key = api_key
        self.model_name = model_name
        self.logger = logging.getLogger(__name__)
    
    def is_available(self) -> bool:
        """Check if OpenAI model is available."""
        return self.api_key is not None and self.api_key != ""
    
    def generate_response(self, prompt: str, **kwargs) -> str:
        """
        Generate response using OpenAI API.
        
        Args:
            prompt: Input prompt
            **kwargs: Additional parameters
            
        Returns:
            Generated response text
        """
        if not self.is_available():
            return "Error: OpenAI model not available"
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.model_name,
                "messages": [
                    {"role": "system", "content": "You are a legal assistant specialized in Indian law."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": kwargs.get("max_tokens", 1000),
                "temperature": kwargs.get("temperature", 0.7)
            }
            
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                generated_text = result['choices'][0]['message']['content']
                self.logger.info(f"✅ Generated {len(generated_text)} characters")
                return generated_text
            else:
                error_msg = f"OpenAI API error: {response.status_code}"
                self.logger.error(error_msg)
                return f"Error: {error_msg}"
                
        except Exception as e:
            error_msg = f"Error generating response: {str(e)}"
            self.logger.error(error_msg)
            return f"Error: {error_msg}"

class ModelManager:
    """
    Model manager for handling multiple AI models with fallback.
    
    This class manages different AI models and provides fallback
    mechanisms when primary models are unavailable.
    """
    
    def __init__(self, model_config: Dict[str, Any]):
        """
        Initialize model manager.
        
        Args:
            model_config: Configuration dictionary for models
        """
        self.logger = logging.getLogger(__name__)
        self.models = {}
        self.current_model = None
        self.fallback_chain = []
        
        # Initialize models based on configuration
        self._initialize_models(model_config)
        
        # Set up fallback chain
        self._setup_fallback_chain()
    
    def _initialize_models(self, config: Dict[str, Any]):
        """Initialize available models."""
        try:
            # Initialize Ollama model
            if "ollama_url" in config:
                ollama_model = OllamaModel(
                    model_name=config.get("default", "lawgorithm:latest"),
                    ollama_url=config.get("ollama_url", "http://localhost:11434")
                )
                self.models["ollama"] = ollama_model
            
            # Initialize Gemini model
            if "gemini_api_key" in config:
                gemini_model = GeminiModel(
                    api_key=config["gemini_api_key"],
                    model_name=config.get("gemini_model", "gemini-pro")
                )
                self.models["gemini"] = gemini_model
            
            # Initialize OpenAI model
            if "openai_api_key" in config:
                openai_model = OpenAIModel(
                    api_key=config["openai_api_key"],
                    model_name=config.get("openai_model", "gpt-3.5-turbo")
                )
                self.models["openai"] = openai_model
                
        except Exception as e:
            self.logger.error(f"❌ Error initializing models: {e}")
    
    def _setup_fallback_chain(self):
        """Set up fallback chain for models."""
        # Priority order: Ollama (local) -> Gemini -> OpenAI
        self.fallback_chain = ["ollama", "gemini", "openai"]
        
        # Find first available model
        for model_name in self.fallback_chain:
            if model_name in self.models and self.models[model_name].is_available():
                self.current_model = model_name
                self.logger.info(f"✅ Using {model_name} as primary model")
                break
        
        if not self.current_model:
            self.logger.warning("⚠️ No models available")
    
    def generate_response(self, prompt: str, **kwargs) -> str:
        """
        Generate response using available models with fallback.
        
        Args:
            prompt: Input prompt
            **kwargs: Additional parameters
            
        Returns:
            Generated response text
        """
        if not self.current_model:
            return "Error: No AI models available"
        
        # Try current model first
        try:
            response = self.models[self.current_model].generate_response(prompt, **kwargs)
            if not response.startswith("Error:"):
                return response
        except Exception as e:
            self.logger.warning(f"⚠️ Error with {self.current_model}: {e}")
        
        # Try fallback models
        for model_name in self.fallback_chain:
            if model_name == self.current_model:
                continue
                
            if model_name in self.models and self.models[model_name].is_available():
                try:
                    self.logger.info(f"🔄 Falling back to {model_name}")
                    response = self.models[model_name].generate_response(prompt, **kwargs)
                    if not response.startswith("Error:"):
                        self.current_model = model_name
                        return response
                except Exception as e:
                    self.logger.warning(f"⚠️ Error with fallback {model_name}: {e}")
        
        return "Error: All models failed to generate response"
    
    def switch_model(self, model_name: str) -> bool:
        """
        Switch to a specific model.
        
        Args:
            model_name: Name of the model to switch to
            
        Returns:
            True if successful, False otherwise
        """
        if model_name in self.models and self.models[model_name].is_available():
            self.current_model = model_name
            self.logger.info(f"✅ Switched to {model_name}")
            return True
        else:
            self.logger.warning(f"⚠️ Cannot switch to {model_name}")
            return False
    
    def get_available_models(self) -> List[str]:
        """Get list of available models."""
        available = []
        for name, model in self.models.items():
            if model.is_available():
                available.append(name)
        return available
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about current model."""
        if not self.current_model:
            return {"error": "No model available"}
        
        return {
            "current_model": self.current_model,
            "available_models": self.get_available_models(),
            "fallback_chain": self.fallback_chain
        }

# Example usage
if __name__ == "__main__":
    # Test model manager
    config = {
        "default": "lawgorithm:latest",
        "ollama_url": "http://localhost:11434"
    }
    
    manager = ModelManager(config)
    
    # Test generation
    response = manager.generate_response("What is the procedure for filing a writ petition?")
    print(f"Response: {response[:200]}...")
    
    # Print model info
    info = manager.get_model_info()
    print(f"Model info: {info}") 