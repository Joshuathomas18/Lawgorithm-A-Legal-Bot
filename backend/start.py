#!/usr/bin/env python3
"""
Startup Script
==============

Script to start the Petition Automator backend server.
"""

import uvicorn
import logging
import sys
import os
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from .config.settings import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format=settings.LOG_FORMAT
)

logger = logging.getLogger(__name__)

def main():
    """Main startup function"""
    try:
        logger.info("🚀 Starting Petition Automator Backend...")
        logger.info(f"📁 Working directory: {os.getcwd()}")
        logger.info(f"🔧 Debug mode: {settings.DEBUG}")
        logger.info(f"🌐 Host: {settings.HOST}")
        logger.info(f"🔌 Port: {settings.PORT}")
        
        # Start the server
        uvicorn.run(
            "main:app",
            host=settings.HOST,
            port=settings.PORT,
            reload=settings.DEBUG,
            log_level=settings.LOG_LEVEL.lower()
        )
        
    except KeyboardInterrupt:
        logger.info("👋 Shutting down gracefully...")
    except Exception as e:
        logger.error(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 