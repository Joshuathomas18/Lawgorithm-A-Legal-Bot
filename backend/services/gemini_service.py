#!/usr/bin/env python3
"""
Gemini Service
==============

Service for handling Google Gemini LLM connections and text generation.
"""

import logging
import json
import asyncio
import time
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)

class GeminiService:
    def __init__(self, api_key: str, model_name: str = "gemini-2.5-flash"):
        self.api_key = api_key
        self.model_name = model_name
        self.is_initialized = False
        self.model = None
        self.genai = None
        
        # Batching and rate limiting settings
        self.rate_limit_delay = 2.0  # seconds between requests
        self.max_tokens_per_request = 4000  # increased from 1000
        self.batch_delay = 1.0  # seconds between batches
        self.max_retries = 3  # maximum retry attempts
        self.max_rounds = 15  # maximum rounds for document generation
        self.base_delay = 2.0  # base delay for exponential backoff
        
    async def initialize(self):
        """Initialize the Gemini service"""
        try:
            logger.info("🤖 Initializing Gemini Service...")
            
            # Import Google Generative AI
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self.genai = genai
                self.model = genai.GenerativeModel(self.model_name)
                self.is_initialized = True
                logger.info(f"✅ Gemini Service initialized successfully with {self.model_name}!")
            except ImportError:
                logger.error("❌ google-generativeai not installed. Please install: pip install google-generativeai")
                self.is_initialized = False
                raise
            except Exception as e:
                logger.error(f"❌ Failed to initialize Gemini Service: {e}")
                self.is_initialized = False
                raise
                
        except Exception as e:
            logger.error(f"❌ Failed to initialize Gemini Service: {e}")
            self.is_initialized = False
            raise
    
    async def test_connection(self) -> bool:
        """Test connection to Gemini API"""
        try:
            if not self.is_initialized:
                return False
                
            # Test with a simple prompt
            test_prompt = "Hello, this is a test."
            response = self.model.generate_content(test_prompt)
            
            if response and response.text:
                logger.info("✅ Gemini API connection successful")
                return True
            else:
                logger.error("❌ Gemini API returned empty response")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error testing Gemini connection: {e}")
            return False
    
    async def generate_text(self, prompt: str, options: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """Generate text using Gemini"""
        try:
            if not self.is_initialized:
                raise Exception("Gemini Service not initialized")
            
            # Default options
            default_options = {
                "temperature": 0.7,
                "top_p": 0.9,
                "max_output_tokens": self.max_tokens_per_request,
            }
            
            if options:
                default_options.update(options)
            
            logger.info(f"🤖 Generating text with {self.model_name}...")
            
            # Generate content with safety settings
            safety_settings = [
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                }
            ]
            
            generation_config = self.genai.types.GenerationConfig(
                temperature=default_options["temperature"],
                top_p=default_options["top_p"],
                max_output_tokens=default_options["max_output_tokens"],
            )
            
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config,
                safety_settings=safety_settings
            )
            
            if response and response.text:
                generated_text = response.text
                logger.info("✅ Text generated successfully")
                return generated_text
            else:
                logger.warning("⚠️ No text generated")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error generating text: {e}")
            return None
    
    def _get_document_sections(self, document_type: str) -> List[Dict[str, str]]:
        """Get document sections for batching"""
        sections = {
            "petition": [
                {"name": "main_petition", "description": "Complete petition with header, parties, facts, arguments, prayer, salutations, and affidavit - NO verification section"}
            ],
            "bail_petition": [
                {"name": "main_petition", "description": "Complete bail petition with header, parties, facts, arguments, undertaking, and affidavit"}
            ],
            "complaint": [
                {"name": "main_petition", "description": "Complete complaint with header, parties, facts, arguments, prayer, and affidavit"}
            ],
            "legal_response": [
                {"name": "introduction", "description": "Introduction and context of the legal question"},
                {"name": "analysis", "description": "Legal analysis and principles"},
                {"name": "precedents", "description": "Relevant case law and precedents"},
                {"name": "conclusion", "description": "Conclusion and practical guidance"}
            ]
        }
        
        return sections.get(document_type, sections["petition"])
    
    async def generate_complete_document_iterative(self, prompt: str, document_type: str = "petition") -> str:
        """Generate complete document using iterative batching with rounds"""
        try:
            if not self.is_initialized:
                raise Exception("Gemini Service not initialized")
            
            logger.info(f"📄 Generating complete {document_type} with iterative batching...")
            
            # Get document sections
            sections = self._get_document_sections(document_type)
            logger.info(f"📋 Document sections: {[s['name'] for s in sections]}")
            
            # Initialize document generation
            full_document = ""
            current_round = 0
            section_index = 0
            
            while current_round < self.max_rounds and section_index < len(sections):
                logger.info(f"🔄 Round {current_round + 1}/{self.max_rounds} - Section {section_index + 1}/{len(sections)}")
                
                # Create section-specific prompt
                section = sections[section_index]
                section_prompt = self._create_section_prompt(prompt, section, full_document, document_type)
                
                # Generate section with retry mechanism
                section_content = await self._generate_with_retry(section_prompt, f"section_{section['name']}")
                
                if section_content:
                    full_document += section_content + "\n\n"
                    logger.info(f"✅ Section '{section['name']}' completed: {len(section_content)} characters")
                    section_index += 1
                else:
                    logger.warning(f"⚠️ Section '{section['name']}' failed, retrying...")
                
                current_round += 1
                
                # Rate limiting delay between rounds
                if current_round < self.max_rounds:
                    logger.info(f"⏱️ Waiting {self.batch_delay}s before next round...")
                    await asyncio.sleep(self.batch_delay)
            
            # Final completion check
            if self._is_document_complete(full_document, document_type):
                logger.info(f"✅ Complete {document_type} generated successfully!")
                logger.info(f"📊 Total length: {len(full_document)} characters")
                logger.info(f"🔄 Total rounds: {current_round}")
                return full_document.strip()
            else:
                logger.warning("⚠️ Document may be incomplete, attempting final continuation...")
                final_prompt = f"Complete the following {document_type} by adding any missing sections (verification, affidavit, etc.):\n\n{full_document}\n\nContinue and complete the document:"
                final_content = await self._generate_with_retry(final_prompt, "final_completion")
                
                if final_content:
                    full_document += final_content
                    return full_document.strip()
                else:
                    return full_document.strip() if full_document else "❌ Failed to generate complete document."
            
        except Exception as e:
            logger.error(f"❌ Error generating complete document: {e}")
            return f"❌ Error generating document: {str(e)}"
    
    def _create_section_prompt(self, base_prompt: str, section: Dict[str, str], current_document: str, document_type: str) -> str:
        """Create section-specific prompt"""
        section_name = section["name"]
        section_desc = section["description"]
        
        if not current_document:
            # First section - start the document
            return f"""{base_prompt}

Generate the {section_name} section of the {document_type} which includes: {section_desc}

Start the document with this section. Make sure it follows proper legal format and structure.

{section_name.upper()} SECTION:"""
        else:
            # Continue from previous content
            return f"""Continue generating the {document_type} from where you left off.

PREVIOUS CONTENT:
{current_document}

Now generate the {section_name} section which includes: {section_desc}

Continue the document with this section. Do not repeat what was already written.

{section_name.upper()} SECTION:"""
    
    async def _generate_with_retry(self, prompt: str, context: str) -> Optional[str]:
        """Generate text with retry mechanism and rate limiting"""
        retries = 0
        
        while retries < self.max_retries:
            try:
                logger.info(f"📦 Generating {context} (attempt {retries + 1}/{self.max_retries})...")
                
                response = await self.generate_text(
                    prompt,
                    options={
                        "temperature": 0.3,  # Lower temperature for consistent document generation
                        "max_output_tokens": self.max_tokens_per_request,
                        "top_p": 0.8
                    }
                )
                
                if response:
                    return response
                else:
                    logger.warning(f"⚠️ Empty response for {context}, retrying...")
                    
            except Exception as e:
                error_msg = str(e)
                if "RESOURCE_EXHAUSTED" in error_msg or "rate limit" in error_msg.lower():
                    wait_time = self.base_delay * (2 ** retries)
                    logger.warning(f"⏳ Rate limit exceeded for {context}. Retrying in {wait_time} seconds...")
                    await asyncio.sleep(wait_time)
                    retries += 1
                    if retries >= self.max_retries:
                        logger.error(f"❌ Max retries reached for {context}")
                        return None
                else:
                    logger.error(f"❌ Error generating {context}: {e}")
                    retries += 1
                    if retries >= self.max_retries:
                        return None
            
            # Regular delay between retries
            if retries < self.max_retries:
                await asyncio.sleep(self.rate_limit_delay)
        
        return None
    
    def _is_document_complete(self, document: str, document_type: str) -> bool:
        """Check if document is complete"""
        if not document:
            return False
        
        # Check for essential sections based on document type
        essential_elements = {
            "petition": ["arguments", "affidavit", "prayer", "and for this act of kindness"],
            "bail_petition": ["arguments", "undertaking", "prayer"],
            "complaint": ["arguments", "evidence", "prayer"],
            "legal_response": ["conclusion", "analysis", "precedents"]
        }
        
        required_elements = essential_elements.get(document_type, ["arguments", "prayer"])
        
        document_lower = document.lower()
        missing_elements = [elem for elem in required_elements if elem not in document_lower]
        
        if missing_elements:
            logger.info(f"⚠️ Missing elements: {missing_elements}")
            return False
        
        # Check for forbidden elements
        forbidden_elements = ["verification"]
        present_forbidden = [elem for elem in forbidden_elements if elem in document_lower]
        
        if present_forbidden:
            logger.info(f"⚠️ Forbidden elements present: {present_forbidden}")
            return False
        
        # Check if document ends properly based on document type
        if document_type == "legal_response":
            # For legal responses, check if it has a proper conclusion
            if not any(ending in document_lower for ending in ["conclusion", "summary", "therefore", "thus", "in conclusion"]):
                logger.info("⚠️ Legal response missing proper conclusion")
                return False
        else:
            # For legal documents, check for proper endings
            if not document.strip().endswith(("affidavit", "undertaking", "prayer")):
                return False
        
        return True
    
    async def generate_complete_document(self, prompt: str, document_type: str = "legal_document") -> str:
        """Legacy method - now uses iterative batching"""
        return await self.generate_complete_document_iterative(prompt, document_type)
    
    def _split_prompt_into_chunks(self, prompt: str) -> List[str]:
        """Split long prompts into manageable chunks for batching"""
        # Estimate tokens (rough approximation: 1 token ≈ 4 characters)
        estimated_tokens = len(prompt) // 4
        
        if estimated_tokens <= self.max_tokens_per_request:
            return [prompt]
        
        # Split by sentences to maintain context
        sentences = prompt.split('. ')
        chunks = []
        current_chunk = []
        current_length = 0
        
        for sentence in sentences:
            sentence_length = len(sentence) // 4  # Rough token estimation
            
            if current_length + sentence_length > self.max_tokens_per_request * 0.8:  # Leave some buffer
                chunks.append('. '.join(current_chunk) + '.')
                current_chunk = [sentence]
                current_length = sentence_length
            else:
                current_chunk.append(sentence)
                current_length += sentence_length
        
        if current_chunk:
            chunks.append('. '.join(current_chunk) + '.')
        
        logger.info(f"📦 Split prompt into {len(chunks)} chunks")
        return chunks if chunks else [prompt]
    
    async def get_embedding(self, text: str) -> Optional[List[float]]:
        """Get embedding for text using Gemini"""
        try:
            if not self.is_initialized:
                raise Exception("Gemini Service not initialized")
            
            # Use Gemini's embedding model
            embedding_model = self.genai.get_model('embedding-001')
            result = embedding_model.embed_content(text)
            
            if result and result.embedding:
                embedding = result.embedding
                logger.info(f"✅ Got embedding of length: {len(embedding)}")
                return embedding
            else:
                logger.warning("⚠️ No embedding generated")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error getting embedding: {e}")
            return None
    
    async def get_available_models(self) -> List[Dict[str, Any]]:
        """Get list of available models"""
        try:
            if not self.is_initialized:
                return []
                
            # List available models
            models = []
            for model in self.genai.list_models():
                if 'generateContent' in model.supported_generation_methods:
                    models.append({
                        'name': model.name,
                        'display_name': model.display_name,
                        'description': model.description
                    })
            
            return models
                
        except Exception as e:
            logger.error(f"❌ Error getting available models: {e}")
            return []
    
    async def get_model_info(self, model_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get information about a specific model"""
        try:
            if not self.is_initialized:
                return None
                
            model = model_name or self.model_name
            
            # Get model details
            model_info = self.genai.get_model(model)
            
            return {
                'name': model_info.name,
                'display_name': model_info.display_name,
                'description': model_info.description,
                'generation_methods': list(model_info.supported_generation_methods)
            }
                
        except Exception as e:
            logger.error(f"❌ Error getting model info: {e}")
            return None
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for Gemini service"""
        try:
            is_connected = await self.test_connection()
            models = await self.get_available_models()
            model_info = await self.get_model_info()
            
            return {
                'status': 'healthy' if is_connected else 'unhealthy',
                'initialized': self.is_initialized,
                'connected': is_connected,
                'api_key': self.api_key[:10] + "..." if self.api_key else None,
                'model_name': self.model_name,
                'available_models': [model['name'] for model in models],
                'model_info': model_info,
                'max_tokens_per_request': self.max_tokens_per_request,
                'rate_limit_delay': self.rate_limit_delay,
                'max_retries': self.max_retries,
                'max_rounds': self.max_rounds
            }
            
        except Exception as e:
            logger.error(f"Gemini health check failed: {e}")
            return {
                'status': 'error',
                'initialized': self.is_initialized,
                'connected': False,
                'error': str(e)
            } 