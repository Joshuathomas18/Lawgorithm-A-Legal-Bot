#!/usr/bin/env python3
"""
Main Server Entry Point
=======================

Main FastAPI server for the Lawgorithm legal petition automation system.
This is the primary entry point that initializes all services and routes.
"""

import os
import sys
import uuid
import logging
import asyncio
from datetime import datetime
from pathlib import Path

# Add the current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import uvicorn

# Import configuration
from config.settings import settings

# Import services
from services.gemini_service import GeminiService
from services.rag_service import RAGService
from services.conversation_service import ConversationService
from services.petition_service import PetitionService
from services.document_service import DocumentService
from services.session_service import SessionService

# Import database
from models.database import init_db, close_db

# Import routers
from views.health_views import router as health_router
from views.conversation_views import router as conversation_router
from views.chatbot_llm_views import router as chatbot_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Lawgorithm API",
    description="AI-powered legal petition automation system",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global service instances
gemini_service = None
rag_service = None
conversation_service = None
petition_service = None
document_service = None
session_service = None

async def initialize_services():
    """Initialize all services"""
    global gemini_service, rag_service, conversation_service, petition_service, document_service, session_service
    
    try:
        logger.info("🚀 Initializing Lawgorithm services...")
        
        # Initialize database first
        await init_db()
        logger.info("✅ Database initialized")
        
        # Initialize Gemini service
        gemini_service = GeminiService(
            api_key=settings.GEMINI_API_KEY,
            model_name=settings.GEMINI_MODEL_NAME
        )
        await gemini_service.initialize()
        logger.info("✅ Gemini service initialized")
        
        # Initialize RAG service
        rag_service = RAGService()
        rag_service.gemini_service = gemini_service
        await rag_service.initialize()
        logger.info("✅ RAG service initialized")
        
        # Initialize other services
        session_service = SessionService()
        document_service = DocumentService()
        conversation_service = ConversationService(rag_service, gemini_service)
        petition_service = PetitionService(rag_service, gemini_service)
        
        logger.info("✅ All services initialized successfully!")
        
    except Exception as e:
        logger.error(f"❌ Error initializing services: {e}")
        raise

@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    try:
        await initialize_services()
        logger.info("🎉 Lawgorithm API started successfully!")
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event"""
    try:
        await close_db()
        logger.info("👋 Lawgorithm API shutdown complete")
    except Exception as e:
        logger.error(f"⚠️ Shutdown error: {e}")

# Include routers
app.include_router(health_router, prefix="/api", tags=["Health"])
app.include_router(conversation_router, prefix="/api/v1/conversations", tags=["Conversations"])
app.include_router(chatbot_router, prefix="/api/v1/chatbot", tags=["Chatbot"])

# Create static directory if it doesn't exist
static_dir = Path("static")
static_dir.mkdir(exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/api")
async def root():
    """Root API endpoint"""
    return {
        "message": "Welcome to Lawgorithm API",
        "description": "AI-powered legal petition automation system",
        "version": "1.0.0",
        "status": "operational",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "health": "/api/health",
            "docs": "/api/docs",
            "conversations": "/api/v1/conversations",
            "chatbot": "/api/v1/chatbot"
        }
    }

@app.get("/api/test")
async def test_frontend():
    """Test endpoint for frontend debugging"""
    return {
        "message": "Backend is working!",
        "timestamp": datetime.now().isoformat(),
        "test_data": {
            "session_test": str(uuid.uuid4()),
            "conversation_test": str(uuid.uuid4())
        }
    }

@app.get("/")
async def redirect_to_api():
    """Redirect root to API endpoint"""
    return {
        "message": "Lawgorithm Legal AI System",
        "api_endpoint": "/api",
        "documentation": "/api/docs"
    }

# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"❌ Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)}
    )

# Health check endpoint
@app.get("/api/health")
async def health_check():
    """Quick health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "gemini": gemini_service.is_initialized if gemini_service else False,
            "rag": rag_service.is_initialized if rag_service else False,
            "database": True
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        "server:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )