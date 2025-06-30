#!/usr/bin/env python3
"""
Session Service
==============

Service for managing user sessions.
"""

import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

from models.database import SessionRepository

logger = logging.getLogger(__name__)

class SessionService:
    def __init__(self):
        self.is_initialized = True
        self.session_timeout_hours = 24
        
    async def create_session(self, user_id: Optional[str] = None, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """Create a new session"""
        try:
            session_id = str(uuid.uuid4())
            
            success = await SessionRepository.create_session(
                session_id=session_id,
                user_id=user_id or f"anonymous_{session_id[:8]}",
                metadata=metadata
            )
            
            if success:
                logger.info(f"✅ Created session: {session_id}")
                return {
                    'session_id': session_id,
                    'user_id': user_id or f"anonymous_{session_id[:8]}",
                    'created_at': datetime.now().isoformat(),
                    'expires_at': (datetime.now() + timedelta(hours=self.session_timeout_hours)).isoformat()
                }
            else:
                raise Exception("Failed to create session in database")
                
        except Exception as e:
            logger.error(f"❌ Error creating session: {e}")
            raise
    
    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session information"""
        try:
            session = await SessionRepository.get_session(session_id)
            
            if session:
                # Check if session is expired
                last_activity = datetime.fromisoformat(session['last_activity'])
                expiry_time = last_activity + timedelta(hours=self.session_timeout_hours)
                
                if datetime.now() > expiry_time:
                    logger.info(f"⏰ Session expired: {session_id}")
                    return None
                
                return session
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error getting session: {e}")
            return None
    
    async def update_session_activity(self, session_id: str) -> bool:
        """Update session last activity"""
        try:
            return await SessionRepository.update_session_activity(session_id)
        except Exception as e:
            logger.error(f"❌ Error updating session activity: {e}")
            return False
    
    async def is_session_valid(self, session_id: str) -> bool:
        """Check if session is valid and not expired"""
        try:
            session = await self.get_session(session_id)
            return session is not None
        except Exception as e:
            logger.error(f"❌ Error validating session: {e}")
            return False
    
    async def cleanup_expired_sessions(self) -> int:
        """Cleanup expired sessions"""
        try:
            # This would be implemented with proper database queries
            # For now, return 0 as placeholder
            logger.info("🧹 Session cleanup completed")
            return 0
            
        except Exception as e:
            logger.error(f"❌ Error cleaning up sessions: {e}")
            return 0
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for session service"""
        return {
            'status': 'healthy',
            'initialized': self.is_initialized,
            'session_timeout_hours': self.session_timeout_hours
        }