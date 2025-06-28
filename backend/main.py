#!/usr/bin/env python3
"""
Main FastAPI Application
========================

Entry point for the Petition Automator backend API.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import logging
from datetime import datetime

# Import routers
from .views.petition_views import router as petition_router
from .views.conversation_views import router as conversation_router
from .views.document_views import router as document_router
from .views.health_views import router as health_router
from .views.chatbot_response_views import router as chatbot_response_router
from .views.chatbot_llm_views import router as chatbot_llm_router

# Import services
from .services.rag_service import RAGService
from .services.gemini_service import GeminiService
from .services.petition_service import PetitionService
from .services.conversation_service import ConversationService
from .services.document_service import DocumentService
from .services.session_service import SessionService

# Import models
from .models.database import init_db

# Import settings
from .config.settings import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Petition Automator API",
    description="AI-powered legal petition generation system",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
rag_service = RAGService()
gemini_service = GeminiService(settings.GEMINI_API_KEY, settings.GEMINI_MODEL_NAME)
petition_service = PetitionService(rag_service, gemini_service)
conversation_service = ConversationService(rag_service, gemini_service)
document_service = DocumentService()
session_service = SessionService()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    try:
        logger.info("Starting Petition Automator API...")
        
        # Initialize database
        await init_db()
        
        # Initialize Gemini service first
        await gemini_service.initialize()
        
        # Initialize RAG service with Gemini service
        rag_service.gemini_service = gemini_service
        await rag_service.initialize()
        
        logger.info("✅ All services initialized successfully!")
        
    except Exception as e:
        logger.error(f"❌ Error during startup: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down Petition Automator API...")

# Include routers with service injection
app.include_router(health_router, prefix="/api/v1", tags=["Health"])
app.include_router(petition_router, prefix="/api/v1/petitions", tags=["Petitions"])
app.include_router(conversation_router, prefix="/api/v1/conversations", tags=["Conversations"])
app.include_router(document_router, prefix="/api/v1/documents", tags=["Documents"])
app.include_router(chatbot_response_router, prefix="/api/v1/conversations", tags=["Chatbot"])
app.include_router(chatbot_llm_router, prefix="/api/v1/chatbot", tags=["ChatbotLLM"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "status": "healthy",
        "message": "Petition Automator API is running",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 