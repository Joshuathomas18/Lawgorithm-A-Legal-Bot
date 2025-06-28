#!/usr/bin/env python3
"""
Database Models and Connection
==============================

Database setup and models for the petition automator.
"""

import sqlite3
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional
import os

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, db_path: str = "petition_automator.db"):
        self.db_path = db_path
        self.conn = None
        
    async def connect(self):
        """Initialize database connection"""
        try:
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
            await self.create_tables()
            logger.info("✅ Database connected successfully")
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            raise
    
    async def create_tables(self):
        """Create database tables"""
        cursor = self.conn.cursor()
        
        # Sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                user_id TEXT,
                created_at TEXT NOT NULL,
                last_activity TEXT NOT NULL,
                is_active BOOLEAN DEFAULT TRUE,
                metadata TEXT
            )
        """)
        
        # Conversations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                conversation_id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                status TEXT DEFAULT 'active',
                FOREIGN KEY (session_id) REFERENCES sessions (session_id)
            )
        """)
        
        # Messages table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                message_id TEXT PRIMARY KEY,
                conversation_id TEXT NOT NULL,
                session_id TEXT NOT NULL,
                user_message TEXT NOT NULL,
                assistant_response TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (conversation_id) REFERENCES conversations (conversation_id),
                FOREIGN KEY (session_id) REFERENCES sessions (session_id)
            )
        """)
        
        # Petitions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS petitions (
                petition_id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                case_details TEXT NOT NULL,
                petition_text TEXT NOT NULL,
                generated_at TEXT NOT NULL,
                status TEXT DEFAULT 'generated',
                version_number INTEGER DEFAULT 1,
                FOREIGN KEY (session_id) REFERENCES sessions (session_id)
            )
        """)
        
        # Document versions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS document_versions (
                version_id TEXT PRIMARY KEY,
                petition_id TEXT NOT NULL,
                version_number INTEGER NOT NULL,
                petition_text TEXT NOT NULL,
                changes_made TEXT,
                created_at TEXT NOT NULL,
                file_path TEXT,
                FOREIGN KEY (petition_id) REFERENCES petitions (petition_id)
            )
        """)
        
        # Documents table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                document_id TEXT PRIMARY KEY,
                petition_id TEXT NOT NULL,
                format TEXT NOT NULL,
                file_path TEXT NOT NULL,
                generated_at TEXT NOT NULL,
                download_url TEXT,
                FOREIGN KEY (petition_id) REFERENCES petitions (petition_id)
            )
        """)
        
        self.conn.commit()
        logger.info("✅ Database tables created successfully")
    
    async def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")

# Global database instance
db_manager = DatabaseManager()

async def init_db():
    """Initialize database"""
    await db_manager.connect()

async def close_db():
    """Close database"""
    await db_manager.close()

# Database operations
class SessionRepository:
    @staticmethod
    async def create_session(session_id: str, user_id: Optional[str] = None, metadata: Optional[Dict] = None) -> bool:
        """Create a new session"""
        try:
            cursor = db_manager.conn.cursor()
            cursor.execute("""
                INSERT INTO sessions (session_id, user_id, created_at, last_activity, metadata)
                VALUES (?, ?, ?, ?, ?)
            """, (
                session_id,
                user_id,
                datetime.now().isoformat(),
                datetime.now().isoformat(),
                json.dumps(metadata) if metadata else None
            ))
            db_manager.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error creating session: {e}")
            return False
    
    @staticmethod
    async def get_session(session_id: str) -> Optional[Dict[str, Any]]:
        """Get session by ID"""
        try:
            cursor = db_manager.conn.cursor()
            cursor.execute("SELECT * FROM sessions WHERE session_id = ?", (session_id,))
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
        except Exception as e:
            logger.error(f"Error getting session: {e}")
            return None
    
    @staticmethod
    async def update_session_activity(session_id: str) -> bool:
        """Update session last activity"""
        try:
            cursor = db_manager.conn.cursor()
            cursor.execute("""
                UPDATE sessions 
                SET last_activity = ? 
                WHERE session_id = ?
            """, (datetime.now().isoformat(), session_id))
            db_manager.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error updating session: {e}")
            return False

class PetitionRepository:
    @staticmethod
    async def create_petition(petition_id: str, session_id: str, case_details: Dict, petition_text: str) -> bool:
        """Create a new petition"""
        try:
            cursor = db_manager.conn.cursor()
            cursor.execute("""
                INSERT INTO petitions (petition_id, session_id, case_details, petition_text, generated_at)
                VALUES (?, ?, ?, ?, ?)
            """, (
                petition_id,
                session_id,
                json.dumps(case_details),
                petition_text,
                datetime.now().isoformat()
            ))
            db_manager.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error creating petition: {e}")
            return False
    
    @staticmethod
    async def get_petition(petition_id: str) -> Optional[Dict[str, Any]]:
        """Get petition by ID"""
        try:
            cursor = db_manager.conn.cursor()
            cursor.execute("SELECT * FROM petitions WHERE petition_id = ?", (petition_id,))
            row = cursor.fetchone()
            if row:
                data = dict(row)
                data['case_details'] = json.loads(data['case_details'])
                return data
            return None
        except Exception as e:
            logger.error(f"Error getting petition: {e}")
            return None
    
    @staticmethod
    async def update_petition(petition_id: str, petition_text: str, changes_made: str) -> bool:
        """Update petition with new version"""
        try:
            cursor = db_manager.conn.cursor()
            
            # Get current version
            cursor.execute("SELECT version_number FROM petitions WHERE petition_id = ?", (petition_id,))
            current_version = cursor.fetchone()['version_number']
            new_version = current_version + 1
            
            # Update petition
            cursor.execute("""
                UPDATE petitions 
                SET petition_text = ?, version_number = ?
                WHERE petition_id = ?
            """, (petition_text, new_version, petition_id))
            
            # Create version record
            version_id = f"{petition_id}_v{new_version}"
            cursor.execute("""
                INSERT INTO document_versions (version_id, petition_id, version_number, petition_text, changes_made, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                version_id,
                petition_id,
                new_version,
                petition_text,
                changes_made,
                datetime.now().isoformat()
            ))
            
            db_manager.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error updating petition: {e}")
            return False 