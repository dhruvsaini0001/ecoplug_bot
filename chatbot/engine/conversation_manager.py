"""
Conversation Manager
★ CORE ORCHESTRATOR ★
Manages conversation priority logic and response routing.

PRIORITY LOGIC FLOW:
═══════════════════════════════════════════════════════════════

STEP 1: ERROR CODE DETECTION (HIGHEST PRIORITY)
────────────────────────────────────────────────────────────────
If message contains error code pattern → Return diagnostic response
Examples: "ER001", "error 15", "301", "gun temperature high"
→ Type: "diagnostic"

STEP 2: EXPLICIT ACTION
────────────────────────────────────────────────────────────────
If action parameter exists → Return flow node
Examples: action="start", action="troubleshoot"
→ Type: "flow"

STEP 3: INTENT DETECTION
────────────────────────────────────────────────────────────────
If message has detectable intent → Map to flow node
Examples: "I need help" → support flow
→ Type: "flow"

STEP 4: AI FALLBACK (LOWEST PRIORITY)
────────────────────────────────────────────────────────────────
If nothing else matches → Call AI service
Examples: Open-ended questions, general queries
→ Type: "ai"
"""
from typing import Optional
import re
from difflib import SequenceMatcher
from ..core.logger import setup_logger
from ..models.response_models import ChatResponse
from .flow_engine import FlowEngine
from .intent_engine import IntentEngine
from .diagnostic_engine import DiagnosticEngine
from ..utils.text_utils import normalize_text

logger = setup_logger(__name__)


class ConversationManager:
    """
    Central conversation orchestrator with diagnostic priority.
    
    This is where all conversation logic decisions are made.
    """
    
    def __init__(
        self,
        flow_engine: FlowEngine,
        intent_engine: IntentEngine,
        diagnostic_engine: DiagnosticEngine,
        session_service,
        ai_service
    ):
        """
        Initialize conversation manager.
        
        Args:
            flow_engine: Flow engine instance
            intent_engine: Intent engine instance
            diagnostic_engine: Diagnostic engine instance
            session_service: Session management service
            ai_service: AI service for generating responses
        """
        self.flow_engine = flow_engine
        self.intent_engine = intent_engine
        self.diagnostic_engine = diagnostic_engine
        self.session_service = session_service
        self.ai_service = ai_service
    
    async def process_message(
        self,
        user_id: str,
        message: Optional[str],
        action: Optional[str],
        platform: str
    ) -> ChatResponse:
        """
        ★★★ MAIN CONVERSATION PROCESSING ★★★
        
        Process incoming user message with priority routing.
        
        Priority Flow:
        1. Diagnostic detection (error codes)
        2. Explicit actions
        3. Intent-based routing
        4. AI fallback
        
        Args:
            user_id: Unique user identifier
            message: User's text message
            action: Explicit action/command
            platform: Client platform (web/android/ios)
            
        Returns:
            Standardized ChatResponse
        """
        logger.info(
            f"Processing message - user_id: {user_id}, platform: {platform}",
            extra={"user_id": user_id, "platform": platform}
        )
        
        # Get or create session
        session = await self.session_service.get_or_create_session(user_id, platform)
        session_id = session["session_id"]
        current_node = session.get("current_node", "start")
        
        # Save user message to history
        if message:
            await self.session_service.add_message_to_history(
                user_id=user_id,
                session_id=session_id,
                role="user",
                content=message
            )
        
        # ═══════════════════════════════════════════════════════════════
        # STEP 0.5: DIRECT OPTION BUTTON MAPPING (HIGHEST PRIORITY)
        # ═══════════════════════════════════════════════════════════════
        # Button clicks should route directly without any intent checks
        if message:
            option_node = self._map_option_to_node(message)
            
            if option_node:
                logger.debug(f"Routing option '{message}' to node: {option_node}")
                
                response = await self._generate_flow_response(
                    session_id=session_id,
                    node_id=option_node
                )
                
                # Update session with new node
                await self.session_service.update_session(
                    user_id=user_id,
                    session_id=session_id,
                    current_node=option_node
                )
                
                return await self._save_and_return_response(user_id, session_id, response)
        
        # ═══════════════════════════════════════════════════════════════
        # STEP 1: ERROR CODE DETECTION (HIGH PRIORITY FOR FREE TEXT)
        # ═══════════════════════════════════════════════════════════════
        if message:
            diagnostic_result = await self.diagnostic_engine.detect_error_code(message)
            
            if diagnostic_result:
                logger.info(
                    f"Diagnostic match found: {diagnostic_result['error_code']}",
                    extra={"error_code": diagnostic_result["error_code"]}
                )
                
                response = self._generate_diagnostic_response(
                    session_id=session_id,
                    diagnostic_data=diagnostic_result
                )
                
                # Update session (keep current node, just update timestamp)
                await self.session_service.update_session(
                    user_id=user_id,
                    session_id=session_id,
                    current_node=current_node
                )
                
                return await self._save_and_return_response(user_id, session_id, response)
        
        # ═══════════════════════════════════════════════════════════════
        # STEP 1.5: PAYMENT/WALLET INTENT CHECK (BEFORE FREE TEXT INTENT)
        # ═══════════════════════════════════════════════════════════════
        # Use fuzzy matching to catch typos like "payement", "pamyent"
        if message:
            if self._is_payment_intent(message):
                logger.debug("Payment/Wallet keywords detected (fuzzy), routing to wallet flow")
                response = await self._generate_flow_response(
                    session_id=session_id,
                    node_id="wallet_issues"
                )
                
                # Update session with new node
                await self.session_service.update_session(
                    user_id=user_id,
                    session_id=session_id,
                    current_node="wallet_issues"
                )
                
                return await self._save_and_return_response(user_id, session_id, response)
        
        # ═══════════════════════════════════════════════════════════════
        # STEP 2: EXPLICIT ACTION
        # ═══════════════════════════════════════════════════════════════
        if action:
            logger.debug(f"Routing to explicit action: {action}")
            
            response = await self._generate_flow_response(
                session_id=session_id,
                node_id=action
            )
            
            # Update session with new node
            await self.session_service.update_session(
                user_id=user_id,
                session_id=session_id,
                current_node=action
            )
            
            return await self._save_and_return_response(user_id, session_id, response)
        
        # ═══════════════════════════════════════════════════════════════
        # STEP 3: INTENT DETECTION
        # ═══════════════════════════════════════════════════════════════
        if message:
            intent = await self.intent_engine.detect_intent(message)
            
            if intent:
                # Map intent to flow node
                node_id = self._map_intent_to_node(intent)
                logger.debug(f"Mapped intent '{intent}' to node: {node_id}")
                
                response = await self._generate_flow_response(
                    session_id=session_id,
                    node_id=node_id
                )
                
                # Update session
                await self.session_service.update_session(
                    user_id=user_id,
                    session_id=session_id,
                    current_node=node_id
                )
                
                return await self._save_and_return_response(user_id, session_id, response)
        
        # ═══════════════════════════════════════════════════════════════
        # STEP 4: AI FALLBACK (LOWEST PRIORITY)
        # ═══════════════════════════════════════════════════════════════
        logger.debug("No match found, using AI fallback")
        
        response = await self._generate_ai_response(
            session_id=session_id,
            message=message or "Hello"
        )
        
        # Update session (keep current node)
        await self.session_service.update_session(
            user_id=user_id,
            session_id=session_id,
            current_node=current_node
        )
        
        return await self._save_and_return_response(user_id, session_id, response)
    
    def _generate_diagnostic_response(
        self,
        session_id: str,
        diagnostic_data: dict
    ) -> ChatResponse:
        """
        Generate diagnostic response from error code detection.
        
        Args:
            session_id: Session identifier
            diagnostic_data: Diagnostic information from diagnostic engine
            
        Returns:
            ChatResponse with diagnostic data and follow-up options
        """
        error_code = diagnostic_data["error_code"]
        title = diagnostic_data["title"]
        
        text = f"I found information about {error_code} - {title}. Please review the solutions below."
        
        # Add smart follow-up options to get feedback
        follow_up_options = [
            "✅ Yes, issue resolved",
            "❌ No, still having issues",
            "Back to Menu"
        ]
        
        return ChatResponse(
            type="diagnostic",
            text=text,
            error_code=error_code,
            description=diagnostic_data["description"],
            solutions=diagnostic_data["solutions"],
            options=follow_up_options,  # Add follow-up options
            steps=None,
            action=None,
            session_id=session_id
        )
    
    async def _generate_flow_response(
        self,
        session_id: str,
        node_id: str
    ) -> ChatResponse:
        """
        Generate response from flow node.
        
        Args:
            session_id: Session identifier
            node_id: Flow node ID
            
        Returns:
            ChatResponse from flow data
        """
        node_data = await self.flow_engine.get_node(node_id)
        
        return ChatResponse(
            type="flow",
            text=node_data.get("text", "I'm not sure how to respond."),
            error_code=None,
            description=None,
            solutions=None,
            options=node_data.get("options"),
            steps=node_data.get("steps"),
            action=node_data.get("action"),
            session_id=session_id
        )
    
    async def _generate_ai_response(
        self,
        session_id: str,
        message: str
    ) -> ChatResponse:
        """
        Generate AI-powered response.
        
        Args:
            session_id: Session identifier
            message: User's message
            
        Returns:
            ChatResponse from AI service
        """
        ai_text = await self.ai_service.generate_response(message)
        
        return ChatResponse(
            type="ai",
            text=ai_text,
            error_code=None,
            description=None,
            solutions=None,
            options=None,
            steps=None,
            action=None,
            session_id=session_id
        )
    
    def _map_option_to_node(self, option_text: str) -> Optional[str]:
        """
        Map button option text to flow node ID.
        
        This provides direct routing for button clicks to avoid ambiguity
        in intent detection.
        
        Args:
            option_text: The text from the clicked button
            
        Returns:
            Flow node ID or None if no direct match
        """
        # Normalize the option text for matching
        normalized = option_text.lower().strip()
        
        # Direct mappings for main menu options
        option_mapping = {
            "report error code": "error_reporting",
            "wallet related issues": "wallet_issues",
            "troubleshoot issue": "troubleshooting",
            "maintenance guide": "maintenance",
            "contact support": "support",
            "back to menu": "start",
            "other error code": "other_error_code",
            # Wallet sub-options
            "balance not updating": "balance_not_updating",
            "payment failed": "payment_failed",
            "refund issues": "refund_issues",
            "transaction history": "transaction_history",
            # Troubleshooting sub-options
            "charging not starting": "troubleshooting",
            "connection issues": "troubleshooting",
            "display problems": "troubleshooting",
            "physical damage": "troubleshooting",
            # Smart follow-up options (Yes/No feedback)
            "✅ yes, issue resolved": "solution_resolved",
            "yes, issue resolved": "solution_resolved",
            "✅ yes, this helped": "solution_resolved",
            "yes, this helped": "solution_resolved",
            "yes": "solution_resolved",
            "❌ no, still having issues": "solution_not_resolved",
            "no, still having issues": "solution_not_resolved",
            "❌ no, still have questions": "solution_not_resolved",
            "no, still have questions": "solution_not_resolved",
            "❌ no, still need help": "solution_not_resolved",
            "no, still need help": "solution_not_resolved",
            "❌ no, need more guidance": "solution_not_resolved",
            "no, need more guidance": "solution_not_resolved",
            "no": "solution_not_resolved",
            "no, i'm all set": "done_chatting",
            "no i'm all set": "done_chatting",
            "i'm all set": "done_chatting",
            "all set": "done_chatting",
            "report another error": "report_another_error",
        }
        
        # Check if the option starts with an error code (e.g., "ER001 - Gun Temperature")
        # If so, return None to let it fall through to diagnostic detection
        if re.match(r'^er\d{3,4}\s*-', normalized, re.IGNORECASE):
            return None
        
        return option_mapping.get(normalized)
    
    def _map_intent_to_node(self, intent: str) -> str:
        """
        Map detected intent to flow node ID.
        
        This mapping can be externalized to a config file in production.
        
        Args:
            intent: Detected intent
            
        Returns:
            Flow node ID
        """
        intent_mapping = {
            "greeting": "start",
            "error_report": "error_reporting",
            "troubleshoot": "troubleshooting",
            "wallet": "wallet_issues",
            "maintenance": "maintenance",
            "support": "support",
            "status": "status_check",
            "installation": "installation_guide",
            "network": "network_help",
            "payment": "wallet_issues",
            "usage": "user_guide",
        }
        
        return intent_mapping.get(intent, "start")
    
    def _is_payment_intent(self, message: str) -> bool:
        """
        Check if message is about payment/wallet using fuzzy matching.
        
        Handles typos like:
        - "pamyent" → "payment"
        - "payement" → "payment"
        - "walit" → "wallet"
        - "bilng" → "billing"
        
        Args:
            message: User's message text
            
        Returns:
            True if message appears to be about payments/wallet
        """
        payment_keywords = ['payment', 'wallet', 'balance', 'refund', 'billing']
        normalized_msg = normalize_text(message)
        
        # Extract words from message
        msg_words = normalized_msg.split()
        
        # For each word in message, check if it fuzzy matches any payment keyword
        for msg_word in msg_words:
            for keyword in payment_keywords:
                # Calculate similarity ratio
                ratio = SequenceMatcher(None, msg_word, keyword).ratio()
                
                # Accept matches with 70%+ similarity (handles typos)
                if ratio >= 0.70:
                    logger.debug(f"Payment keyword fuzzy match: '{msg_word}' ≈ '{keyword}' ({ratio:.2%})")
                    return True
        
        return False
    
    async def _save_and_return_response(
        self,
        user_id: str,
        session_id: str,
        response: ChatResponse
    ) -> ChatResponse:
        """
        Save assistant response to conversation history and return it.
        
        Args:
            user_id: User identifier
            session_id: Session identifier
            response: ChatResponse to save and return
            
        Returns:
            The same ChatResponse after saving to history
        \"\"\"\n        # Extract text content from response\n        assistant_message = response.text or \"\"\n        \n        # Save to conversation history\n        await self.session_service.add_message_to_history(\n            user_id=user_id,\n            session_id=session_id,\n            role=\"assistant\",\n            content=assistant_message\n        )\n        \n        return response
