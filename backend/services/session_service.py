#!/usr/bin/env python3
"""
Session Service
==============

Service for managing user sessions and activity tracking.
"""

import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from ..models.database import SessionRepository

logger = logging.getLogger(__name__)

class SessionService:
    def __init__(self, session_timeout_hours: int = 24):
        self.session_timeout_hours = session_timeout_hours
        
    async def create_session(self, user_id: Optional[str] = None, metadata: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
        """Create a new session"""
        try:
            logger.info(f"🔐 Creating new session for user: {user_id}")
            
            session_id = str(uuid.uuid4())
            
            success = await SessionRepository.create_session(
                session_id=session_id,
                user_id=user_id,
                metadata=metadata
            )
            
            if not success:
                logger.error("❌ Failed to create session")
                return None
            
            return {
                'session_id': session_id,
                'user_id': user_id,
                'created_at': datetime.now().isoformat(),
                'last_activity': datetime.now().isoformat(),
                'is_active': True,
                'metadata': metadata
            }
            
        except Exception as e:
            logger.error(f"❌ Error creating session: {e}")
            return None
    
    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session by ID"""
        try:
            logger.info(f"🔍 Getting session: {session_id}")
            
            session = await SessionRepository.get_session(session_id)
            
            if not session:
                logger.warning(f"⚠️ Session not found: {session_id}")
                return None
            
            # Check if session is expired
            if await self._is_session_expired(session):
                logger.info(f"⏰ Session expired: {session_id}")
                await self.deactivate_session(session_id)
                return None
            
            return session
            
        except Exception as e:
            logger.error(f"❌ Error getting session: {e}")
            return None
    
    async def update_session_activity(self, session_id: str) -> bool:
        """Update session last activity"""
        try:
            logger.debug(f"🔄 Updating session activity: {session_id}")
            
            success = await SessionRepository.update_session_activity(session_id)
            
            if not success:
                logger.warning(f"⚠️ Failed to update session activity: {session_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Error updating session activity: {e}")
            return False
    
    async def deactivate_session(self, session_id: str) -> bool:
        """Deactivate a session"""
        try:
            logger.info(f"🔚 Deactivating session: {session_id}")
            
            # This would update the database to mark session as inactive
            # For now, return success
            return True
            
        except Exception as e:
            logger.error(f"❌ Error deactivating session: {e}")
            return False
    
    async def get_active_sessions(self, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all active sessions for a user"""
        try:
            logger.info(f"📋 Getting active sessions for user: {user_id}")
            
            # This would query the database for active sessions
            # For now, return empty list
            return []
            
        except Exception as e:
            logger.error(f"❌ Error getting active sessions: {e}")
            return []
    
    async def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions"""
        try:
            logger.info("🧹 Cleaning up expired sessions")
            
            # This would query and deactivate expired sessions
            # For now, return 0
            return 0
            
        except Exception as e:
            logger.error(f"❌ Error cleaning up expired sessions: {e}")
            return 0
    
    async def _is_session_expired(self, session: Dict[str, Any]) -> bool:
        """Check if session is expired"""
        try:
            last_activity_str = session.get('last_activity')
            if not last_activity_str:
                return True
            
            last_activity = datetime.fromisoformat(last_activity_str)
            expiry_time = last_activity + timedelta(hours=self.session_timeout_hours)
            
            return datetime.now() > expiry_time
            
        except Exception as e:
            logger.error(f"❌ Error checking session expiry: {e}")
            return True
    
    async def get_session_stats(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session statistics"""
        try:
            logger.info(f"📊 Getting stats for session: {session_id}")
            
            session = await self.get_session(session_id)
            if not session:
                return None
            
            # Calculate session duration
            created_at = datetime.fromisoformat(session['created_at'])
            last_activity = datetime.fromisoformat(session['last_activity'])
            duration = last_activity - created_at
            
            return {
                'session_id': session_id,
                'user_id': session.get('user_id'),
                'created_at': session['created_at'],
                'last_activity': session['last_activity'],
                'duration_seconds': duration.total_seconds(),
                'is_active': session.get('is_active', True),
                'is_expired': await self._is_session_expired(session)
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting session stats: {e}")
            return None 