"""
API Routes v1
Versioned REST API endpoints for EV charging diagnostic chatbot.
"""
from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
from typing import Any

from ..models.request_models import ChatRequest
from ..models.response_models import ChatResponse, HealthResponse
from ..engine.conversation_manager import ConversationManager
from ..core.logger import setup_logger

logger = setup_logger(__name__)

# Create API router with versioning
router = APIRouter(prefix="/v1", tags=["chat"])


# Dependency injection placeholder
# This will be set by main.py during startup
_conversation_manager: ConversationManager = None


def set_conversation_manager(manager: ConversationManager):
    """Set the conversation manager instance (called from main.py)."""
    global _conversation_manager
    _conversation_manager = manager


def get_conversation_manager() -> ConversationManager:
    """Dependency to get conversation manager."""
    if _conversation_manager is None:
        raise HTTPException(status_code=503, detail="Service not initialized")
    return _conversation_manager


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    manager: ConversationManager = Depends(get_conversation_manager)
) -> ChatResponse:
    """
    ★★★ UNIVERSAL CHAT ENDPOINT ★★★
    
    Handle chat requests from web, Android, and iOS platforms.
    
    This endpoint:
    1. Detects error codes in messages (highest priority)
    2. Processes explicit actions
    3. Detects intents from natural language
    4. Falls back to AI for unknown queries
    
    Request Examples:
    ────────────────────────────────────────────────────────────────
    
    Error Code Detection:
    ```json
    {
        "user_id": "web_user_123",
        "message": "I'm getting ER001 error",
        "platform": "web"
    }
    ```
    
    Explicit Action:
    ```json
    {
        "user_id": "android_user_456",
        "action": "start",
        "platform": "android"
    }
    ```
    
    Natural Language Query:
    ```json
    {
        "user_id": "ios_user_789",
        "message": "How do I troubleshoot my charging station?",
        "platform": "ios"
    }
    ```
    
    Response Types:
    ────────────────────────────────────────────────────────────────
    
    type="diagnostic" → Error code detected with solutions
    type="flow" → Rule-based conversation flow
    type="ai" → AI-generated response
    
    Args:
        request: ChatRequest with user_id, message, action, platform
        manager: Injected ConversationManager
        
    Returns:
        ChatResponse with appropriate response data
    """
    try:
        logger.info(
            f"Chat request received from {request.platform}",
            extra={
                "user_id": request.user_id,
                "platform": request.platform,
                "has_message": request.message is not None,
                "has_action": request.action is not None
            }
        )
        
        # Process message through conversation manager
        response = await manager.process_message(
            user_id=request.user_id,
            message=request.message,
            action=request.action,
            platform=request.platform
        )
        
        logger.info(
            f"Response generated: type={response.type}",
            extra={
                "user_id": request.user_id,
                "response_type": response.type,
                "session_id": response.session_id
            }
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error processing chat request: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing your request. Please try again."
        )


@router.get("/health", response_model=HealthResponse)
async def health_check(
    manager: ConversationManager = Depends(get_conversation_manager)
) -> HealthResponse:
    """
    Health check endpoint.
    
    Returns system health status and diagnostic database info.
    
    Returns:
        HealthResponse with system status
    """
    from ..core.config import get_settings
    
    settings = get_settings()
    
    # Check if diagnostic database is loaded
    diagnostics_loaded = manager.diagnostic_engine.is_database_loaded()
    error_codes_count = manager.diagnostic_engine.get_total_error_count()
    
    return HealthResponse(
        status="healthy" if diagnostics_loaded else "degraded",
        version=settings.APP_VERSION,
        timestamp=datetime.utcnow().isoformat(),
        diagnostics_loaded=diagnostics_loaded,
        error_codes_count=error_codes_count
    )
