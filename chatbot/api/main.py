"""
FastAPI Main Application
★ EV CHARGING DIAGNOSTIC CHATBOT PLATFORM ★

Production-ready headless chatbot backend with:
- Intelligent error code detection
- Multi-platform support (Web, Android, iOS)
- AI + Rule hybrid architecture
- In-memory session management (MongoDB optional)
- Async-first design
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from ..core.config import get_settings
from ..core.logger import setup_logger
from ..engine.flow_engine import FlowEngine
from ..engine.intent_engine import IntentEngine
from ..engine.diagnostic_engine import DiagnosticEngine
from ..engine.conversation_manager import ConversationManager
from ..services.session_service_inmemory import InMemorySessionService
from ..services.session_service import SessionService
from ..services.ai_service import AIService
from .routes_v1 import router as chat_router, set_conversation_manager
from motor.motor_asyncio import AsyncIOMotorClient

logger = setup_logger(__name__)
settings = get_settings()

# Global instances (initialized during startup)
conversation_manager: ConversationManager = None
mongo_client: AsyncIOMotorClient = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    
    Handles startup and shutdown events:
    - Startup: Load configurations, connect to MongoDB, initialize engines
    - Shutdown: Close database connections, cleanup resources
    """
    # ═══════════════════════════════════════════════════════════════
    # STARTUP
    # ═══════════════════════════════════════════════════════════════
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    
    global conversation_manager, mongo_client
    
    try:
        # ──────────────────────────────────────────────────────────
        # 1. Initialize Services (MongoDB or In-Memory)
        # ──────────────────────────────────────────────────────────
        if settings.MONGODB_URL:
            logger.info("Connecting to MongoDB...")
            mongo_client = AsyncIOMotorClient(settings.MONGODB_URL)
            db = mongo_client[settings.MONGODB_DB_NAME]
            session_service = SessionService(db)
            await session_service.create_indexes()
            logger.info("✓ MongoDB session service initialized")
        else:
            logger.info("Using in-memory session storage (no MongoDB required)")
            session_service = InMemorySessionService()
            await session_service.create_indexes()
            logger.info("✓ In-memory session service initialized")
        
        ai_service = AIService()
        logger.info("AI service initialized")
        
        # ──────────────────────────────────────────────────────────
        # 3. Initialize Engines
        # ──────────────────────────────────────────────────────────
        
        # Flow Engine - loads conversation flows
        flow_engine = FlowEngine()
        await flow_engine.load_flows()
        logger.info(f"✓ Flow engine loaded: {flow_engine.is_flow_loaded()}")
        
        # Intent Engine - keyword-based intent detection
        intent_engine = IntentEngine()
        logger.info("✓ Intent engine initialized")
        
        # ★ Diagnostic Engine - ERROR CODE DETECTION ★
        diagnostic_engine = DiagnosticEngine()
        await diagnostic_engine.load_error_codes()
        logger.info(
            f"✓ Diagnostic engine loaded: {diagnostic_engine.get_total_error_count()} error codes"
        )
        
        # ──────────────────────────────────────────────────────────
        # 3. Initialize Conversation Manager
        # ──────────────────────────────────────────────────────────
        conversation_manager = ConversationManager(
            flow_engine=flow_engine,
            intent_engine=intent_engine,
            diagnostic_engine=diagnostic_engine,
            session_service=session_service,
            ai_service=ai_service
        )
        
        # Inject into routes
        set_conversation_manager(conversation_manager)
        
        logger.info("✓ All systems initialized successfully")
        logger.info("=" * 60)
        logger.info(f"API available at: {settings.API_V1_PREFIX}")
        logger.info(f"Health check: {settings.API_V1_PREFIX}/health")
        logger.info(f"Chat endpoint: {settings.API_V1_PREFIX}/chat")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"Startup failed: {e}", exc_info=True)
        raise
    
    yield
    
    # ═══════════════════════════════════════════════════════════════
    # SHUTDOWN
    # ═══════════════════════════════════════════════════════════════
    logger.info("Shutting down application...")
    if mongo_client:
        mongo_client.close()
        logger.info("✓ MongoDB connection closed")
    logger.info("Shutdown complete")


# ═══════════════════════════════════════════════════════════════
# CREATE FASTAPI APPLICATION
# ═══════════════════════════════════════════════════════════════

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
    🔌 EV Charging Diagnostic Chatbot Platform
    
    Industry-grade headless chatbot backend for EV charging station diagnostics.
    
    Features:
    -  Intelligent error code detection
    -  AI + Rule hybrid architecture
    -  Multi-platform support (Web, Android, iOS)
    -  Advanced diagnostic database
    -  MongoDB session management
    -  Async-first design
    
    Integration:
    - REST API (Platform independent)
    - Standardized request/response format
    - CORS enabled for web apps
    - Rate-limit ready
    """,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# ═══════════════════════════════════════════════════════════════
# MIDDLEWARE
# ═══════════════════════════════════════════════════════════════

# CORS Configuration (allows web, Android, iOS clients)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# TODO: Add rate limiting middleware here
# Example:
# from slowapi import Limiter, _rate_limit_exceeded_handler
# from slowapi.util import get_remote_address
# limiter = Limiter(key_func=get_remote_address)
# app.state.limiter = limiter
# app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ═══════════════════════════════════════════════════════════════
# REGISTER ROUTES
# ═══════════════════════════════════════════════════════════════

app.include_router(chat_router)


# ═══════════════════════════════════════════════════════════════
# ROOT ENDPOINT
# ═══════════════════════════════════════════════════════════════

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "operational",
        "endpoints": {
            "chat": f"{settings.API_V1_PREFIX}/chat",
            "health": f"{settings.API_V1_PREFIX}/health",
            "docs": "/docs"
        }
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "chatbot.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
