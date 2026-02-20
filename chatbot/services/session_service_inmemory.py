"""
In-Memory Session Service
Simple session management without MongoDB for quick testing/demo.
"""
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from ..core.logger import setup_logger
from ..core.config import get_settings
from ..utils.text_utils import generate_session_id

logger = setup_logger(__name__)


class InMemorySessionService:
    """
    In-memory session storage (no database required).
    Perfect for testing and development.
    """
    
    def __init__(self):
        """Initialize in-memory storage."""
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.settings = get_settings()
        logger.info("In-memory session service initialized (no MongoDB required)")
    
    async def create_indexes(self) -> None:
        """No-op for compatibility."""
        pass
    
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
        # Try to find existing session
        session = self.sessions.get(user_id)
        
        # Check if session is expired
        if session and self._is_session_expired(session):
            logger.info(f"Session expired for user: {user_id}")
            session = None
        
        # Create new session if none exists or expired
        if not session:
            session = self._create_new_session(user_id, platform)
            self.sessions[user_id] = session
            logger.info(
                f"Created new in-memory session for user: {user_id}",
                extra={"user_id": user_id, "session_id": session["session_id"]}
            )
        else:
            logger.debug(f"Retrieved existing session: {session['session_id']}")
        
        return session
    
    def _create_new_session(
        self,
        user_id: str,
        platform: str
    ) -> Dict[str, Any]:
        """
        Create a new session in memory.
        
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
        session = self.sessions.get(user_id)
        
        if session:
            session["updated_at"] = datetime.utcnow()
            
            if current_node:
                session["current_node"] = current_node
            
            # Add any extra fields
            session.update(extra_data)
            
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
        for session in self.sessions.values():
            if session.get("session_id") == session_id:
                return session
        return None
    
    async def delete_session(self, session_id: str) -> bool:
        """
        Delete a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if deleted, False otherwise
        """
        for user_id, session in list(self.sessions.items()):
            if session.get("session_id") == session_id:
                del self.sessions[user_id]
                return True
        return False
    
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
        return len(self.sessions)
