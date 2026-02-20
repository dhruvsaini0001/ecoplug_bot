"""
Session Service
MongoDB-based session management for conversation continuity.
"""
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from datetime import datetime
from typing import Dict, Any, Optional
from ..core.logger import setup_logger
from ..core.config import get_settings
from ..utils.text_utils import generate_session_id

logger = setup_logger(__name__)


class SessionService:
    """
    Manages user sessions in MongoDB.
    
    Collection Schema:
    {
        "user_id": "web_user_12345",
        "session_id": "sess_abc123xyz",
        "current_node": "start",
        "platform": "web",
        "created_at": ISODate("2026-02-19T10:00:00Z"),
        "updated_at": ISODate("2026-02-19T10:05:00Z")
    }
    """
    
    def __init__(self, db: AsyncIOMotorDatabase):
        """
        Initialize session service.
        
        Args:
            db: MongoDB database instance (injected)
        """
        self.db = db
        self.collection = db.chat_sessions
        self.settings = get_settings()
    
    async def create_indexes(self) -> None:
        """Create database indexes for optimal query performance."""
        try:
            # Index on user_id for fast session lookup
            await self.collection.create_index("user_id")
            
            # Index on session_id for session retrieval
            await self.collection.create_index("session_id", unique=True)
            
            # TTL index for automatic session cleanup (optional)
            # Sessions expire after 24 hours of inactivity
            await self.collection.create_index(
                "updated_at",
                expireAfterSeconds=86400
            )
            
            logger.info("Session indexes created successfully")
        except Exception as e:
            logger.error(f"Error creating indexes: {e}")
    
    async def get_or_create_session(
        self,
        user_id: str,
        platform: str
    ) -> Dict[str, Any]:
        """
        Get existing session or create new one.
        
        Args:
            user_id: User identifier
            platform: Platform (web/android/ios)
            
        Returns:
            Session document
        """
        # Try to find existing active session
        session = await self.collection.find_one(
            {"user_id": user_id},
            sort=[("updated_at", -1)]  # Get most recent
        )
        
        # Check if session is expired
        if session and self._is_session_expired(session):
            logger.info(f"Session expired for user: {user_id}")
            session = None
        
        # Create new session if none exists or expired
        if not session:
            session = await self._create_new_session(user_id, platform)
            logger.info(
                f"Created new session for user: {user_id}",
                extra={"user_id": user_id, "session_id": session["session_id"]}
            )
        else:
            logger.debug(f"Retrieved existing session: {session['session_id']}")
        
        return session
    
    async def _create_new_session(
        self,
        user_id: str,
        platform: str
    ) -> Dict[str, Any]:
        """
        Create a new session in database.
        
        Args:
            user_id: User identifier
            platform: Platform identifier
            
        Returns:
            New session document
        """
        session = {
            "user_id": user_id,
            "session_id": generate_session_id(),
            "current_node": "start",
            "platform": platform,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        await self.collection.insert_one(session)
        return session
    
    async def update_session(
        self,
        user_id: str,
        session_id: str,
        current_node: Optional[str] = None,
        **extra_data
    ) -> None:
        """
        Update session with new state.
        
        Args:
            user_id: User identifier
            session_id: Session identifier
            current_node: Current conversation node
            **extra_data: Additional fields to update
        """
        update_data = {
            "updated_at": datetime.utcnow()
        }
        
        if current_node:
            update_data["current_node"] = current_node
        
        # Add any extra fields
        update_data.update(extra_data)
        
        await self.collection.update_one(
            {"user_id": user_id, "session_id": session_id},
            {"$set": update_data}
        )
        
        logger.debug(
            f"Updated session: {session_id}",
            extra={"session_id": session_id}
        )
    
    async def get_session_by_id(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve session by session ID.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session document or None
        """
        return await self.collection.find_one({"session_id": session_id})
    
    async def delete_session(self, session_id: str) -> bool:
        """
        Delete a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if deleted, False otherwise
        """
        result = await self.collection.delete_one({"session_id": session_id})
        return result.deleted_count > 0
    
    def _is_session_expired(self, session: Dict[str, Any]) -> bool:
        """
        Check if session is expired based on timeout.
        
        Args:
            session: Session document
            
        Returns:
            True if expired, False otherwise
        """
        if "updated_at" not in session:
            return True
        
        updated_at = session["updated_at"]
        timeout_seconds = self.settings.SESSION_TIMEOUT_MINUTES * 60
        
        age_seconds = (datetime.utcnow() - updated_at).total_seconds()
        return age_seconds > timeout_seconds
    
    async def get_active_session_count(self) -> int:
        """
        Get count of active sessions.
        
        Returns:
            Number of active sessions
        """
        return await self.collection.count_documents({})
