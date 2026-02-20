"""
AI Service
AI-powered response generation with OpenAI integration support.

★ OPENAI INTEGRATION GUIDE ★

STEP 1: Install OpenAI SDK
────────────────────────────────────────────────────────────────
pip install openai

STEP 2: Set environment variable
────────────────────────────────────────────────────────────────
Add to .env file:
OPENAI_API_KEY=sk-your-api-key-here

STEP 3: Uncomment the OpenAI client code below
────────────────────────────────────────────────────────────────
Replace the mock implementation in generate_response() with the
commented OpenAI integration code.

STEP 4: Deploy
────────────────────────────────────────────────────────────────
The system will automatically use OpenAI for AI responses.
"""
from typing import Optional
from ..core.logger import setup_logger
from ..core.config import get_settings

# UNCOMMENT WHEN READY FOR OPENAI INTEGRATION:
# from openai import AsyncOpenAI

logger = setup_logger(__name__)


class AIService:
    """
    AI-powered response generation service.
    
    This service provides intelligent fallback responses when:
    1. No error code is detected
    2. No flow rule matches
    3. User asks open-ended questions
    """
    
    def __init__(self):
        """Initialize AI service."""
        self.settings = get_settings()
        
        # OPENAI INTEGRATION POINT:
        # Uncomment the following lines when ready to use OpenAI
        # ──────────────────────────────────────────────────────────
        # if self.settings.OPENAI_API_KEY:
        #     self.client = AsyncOpenAI(api_key=self.settings.OPENAI_API_KEY)
        #     logger.info("OpenAI client initialized successfully")
        # else:
        #     self.client = None
        #     logger.warning("OPENAI_API_KEY not set - using mock responses")
        
        self.client = None  # Mock mode
    
    async def generate_response(self, message: str, context: Optional[str] = None) -> str:
        """
        Generate AI response to user message.
        
        Args:
            message: User's message
            context: Optional conversation context
            
        Returns:
            AI-generated response text
        """
        # Check if OpenAI is available
        if self.client:
            return await self._openai_response(message, context)
        else:
            return await self._mock_response(message)
    
    async def _mock_response(self, message: str) -> str:
        """
        Generate mock AI response (used when OpenAI is not configured).
        
        Args:
            message: User's message
            
        Returns:
            Mock response
        """
        logger.debug("Generating mock AI response")
        
        # Simple keyword-based mock responses for demo
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["help", "assist", "support"]):
            return (
                "I'm here to help you with EV charging station diagnostics. "
                "You can report error codes (like ER001, ER015, etc.), "
                "troubleshoot issues, or ask technical questions. "
                "How can I assist you today?"
            )
        
        if any(word in message_lower for word in ["how", "what", "why", "when"]):
            return (
                "I can help answer questions about EV charging stations. "
                "For specific technical issues, please provide the error code "
                "displayed on your charging station, and I'll provide detailed diagnostics."
            )
        
        if any(word in message_lower for word in ["thank", "thanks"]):
            return "You're welcome! Is there anything else I can help you with?"
        
        # Default fallback
        return (
            "I understand you need assistance with EV charging. "
            "Could you please provide more details or share any error codes "
            "you're seeing on your charging station? This will help me provide "
            "more accurate diagnostics and solutions."
        )
    
    async def _openai_response(self, message: str, context: Optional[str] = None) -> str:
        """
        Generate response using OpenAI API.
        
        IMPLEMENTATION GUIDE:
        ────────────────────────────────────────────────────────────
        
        Args:
            message: User's message
            context: Conversation context
            
        Returns:
            OpenAI-generated response
        """
        # UNCOMMENT AND USE THIS CODE WHEN OPENAI IS CONFIGURED:
        # ──────────────────────────────────────────────────────────
        """
        try:
            # Build system prompt for EV charging domain
            system_prompt = '''
            You are an expert EV charging station technical support assistant.
            Your role is to help users diagnose and troubleshoot charging station issues.
            
            Guidelines:
            - Be concise and technical
            - Ask for error codes if not provided
            - Provide actionable solutions
            - Be professional and helpful
            - If you don't know, recommend contacting support
            
            Focus areas:
            - EV charging station errors
            - OCPP protocol issues
            - Electrical diagnostics
            - Hardware troubleshooting
            '''
            
            # Build messages
            messages = [
                {"role": "system", "content": system_prompt}
            ]
            
            if context:
                messages.append({"role": "assistant", "content": context})
            
            messages.append({"role": "user", "content": message})
            
            # Call OpenAI API
            response = await self.client.chat.completions.create(
                model=self.settings.OPENAI_MODEL,
                messages=messages,
                temperature=self.settings.OPENAI_TEMPERATURE,
                max_tokens=self.settings.OPENAI_MAX_TOKENS
            )
            
            ai_response = response.choices[0].message.content.strip()
            
            logger.info("Generated OpenAI response", extra={
                "model": self.settings.OPENAI_MODEL,
                "tokens": response.usage.total_tokens
            })
            
            return ai_response
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            # Fallback to mock response on error
            return await self._mock_response(message)
        """
        
        # Placeholder return (replace with above code when ready)
        return await self._mock_response(message)
    
    def is_ai_enabled(self) -> bool:
        """
        Check if AI service is properly configured.
        
        Returns:
            True if OpenAI is configured, False otherwise
        """
        return self.client is not None
