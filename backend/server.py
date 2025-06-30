#!/usr/bin/env python3
"""
LegalAI Pro Server
==================

Advanced AI-powered legal platform with premium features.
"""

import os
import sys
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
from views.premium_legal_views import router as premium_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="LegalAI Pro API",
    description="Advanced AI-powered legal intelligence platform",
    version="2.0.0",
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
        logger.info("🚀 Initializing LegalAI Pro services...")
        
        # Initialize database first
        await init_db()
        logger.info("✅ Database initialized")
        
        # Initialize Gemini service
        gemini_service = GeminiService(
            api_key=settings.GEMINI_API_KEY,
            model_name=settings.GEMINI_MODEL_NAME
        )
        await gemini_service.initialize()
        logger.info("✅ Gemini AI service initialized")
        
        # Initialize RAG service
        rag_service = RAGService()
        rag_service.gemini_service = gemini_service
        await rag_service.initialize()
        logger.info("✅ RAG system initialized")
        
        # Initialize other services
        session_service = SessionService()
        document_service = DocumentService()
        conversation_service = ConversationService(rag_service, gemini_service)
        petition_service = PetitionService(rag_service, gemini_service)
        
        # Inject services into premium views
        import views.premium_legal_views as premium_views
        premium_views.gemini_service = gemini_service
        premium_views.rag_service = rag_service
        
        logger.info("✅ All services initialized successfully!")
        
    except Exception as e:
        logger.error(f"❌ Error initializing services: {e}")
        raise

@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    try:
        await initialize_services()
        logger.info("🎉 LegalAI Pro started successfully!")
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event"""
    try:
        await close_db()
        logger.info("👋 LegalAI Pro shutdown complete")
    except Exception as e:
        logger.error(f"⚠️ Shutdown error: {e}")

# Include routers
app.include_router(health_router, prefix="/api", tags=["Health"])
app.include_router(conversation_router, prefix="/api/v1/conversations", tags=["Conversations"])
app.include_router(chatbot_router, prefix="/api/v1/chatbot", tags=["AI Assistant"])
app.include_router(premium_router, prefix="/api/v1/premium", tags=["Premium Features"])

# Create static directory if it doesn't exist
static_dir = Path("static")
static_dir.mkdir(exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/api")
async def root():
    """Root API endpoint"""
    return {
        "message": "Welcome to LegalAI Pro API",
        "description": "Advanced AI-powered legal intelligence platform",
        "version": "2.0.0",
        "status": "operational",
        "timestamp": datetime.now().isoformat(),
        "features": {
            "ai_assistant": "Advanced legal consultation",
            "document_analyzer": "AI-powered document analysis",
            "legal_generator": "Professional document generation",
            "legal_research": "Comprehensive legal research",
            "case_predictor": "AI case outcome prediction",
            "lawyer_directory": "Verified lawyer network"
        },
        "endpoints": {
            "health": "/api/health",
            "docs": "/api/docs",
            "conversations": "/api/v1/conversations",
            "chatbot": "/api/v1/chatbot",
            "premium": "/api/v1/premium"
        }
    }

@app.get("/")
async def redirect_to_api():
    """Redirect root to API endpoint"""
    return {
        "message": "LegalAI Pro - Advanced Legal Intelligence Platform",
        "api_endpoint": "/api",
        "documentation": "/api/docs",
        "platform_version": "2.0.0"
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

# Enhanced health check endpoint
@app.get("/api/health")
async def health_check():
    """Comprehensive health check"""
    try:
        service_status = {
            "gemini_ai": gemini_service.is_initialized if gemini_service else False,
            "rag_system": rag_service.is_initialized if rag_service else False,
            "database": True,
            "conversation_service": conversation_service is not None,
            "document_service": document_service is not None
        }
        
        overall_health = all(service_status.values())
        
        return {
            "status": "healthy" if overall_health else "degraded",
            "timestamp": datetime.now().isoformat(),
            "version": "2.0.0",
            "services": service_status,
            "features": {
                "ai_consultation": service_status["gemini_ai"] and service_status["rag_system"],
                "document_analysis": service_status["gemini_ai"],
                "legal_research": service_status["rag_system"],
                "document_generation": service_status["gemini_ai"],
                "case_prediction": service_status["gemini_ai"]
            },
            "overall_healthy": overall_health
        }
    except Exception as e:
        logger.error(f"❌ Health check failed: {e}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
            "overall_healthy": False
        }

if __name__ == "__main__":
    uvicorn.run(
        "server:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )