"""
Intent Engine
AI + Rule Hybrid Intent Detection System for EV charging diagnostics.

This engine combines keyword-based rules with AI capabilities:
1. First attempts rule-based detection (fast, deterministic)
2. Falls back to AI service if no rules match
3. Structured for easy integration with OpenAI/LLM APIs
"""
from typing import Optional
from ..core.logger import setup_logger
from ..utils.text_utils import normalize_text

logger = setup_logger(__name__)


class IntentEngine:
    """
    Hybrid intent detection engine for EV charging support.
    
    Supports both rule-based keyword matching and AI-powered detection.
    Rules are checked first for speed; AI is used for complex or ambiguous inputs.
    """
    
    def __init__(self):
        """Initialize the intent engine with keyword rules."""
        # Rule-based intent keywords for EV charging domain
        self.intent_keywords = {
            "greeting": ["hello", "hi", "hey", "good morning", "good afternoon", "greetings"],
            "error_report": ["error", "fault", "problem", "issue", "showing", "displaying"],
            "troubleshoot": ["troubleshoot", "diagnose", "fix", "solve", "repair"],
            "wallet": ["wallet", "balance", "refund", "transaction", "payment failed", "money", "recharge", "wallet charge", "add money"],
            "maintenance": ["maintenance", "service", "inspection", "check"],
            "support": ["help", "support", "assistance", "contact"],
            "status": ["status", "working", "operational", "running"],
            "installation": ["install", "setup", "configure", "connect"],
            "network": ["network", "wifi", "connection", "internet", "ocpp", "communication"],
            "payment": ["payment", "billing", "cost", "price", "pay"],
            "usage": ["how to charge", "charge car", "charge vehicle", "start charging", "charging guide", "how to", "guide", "instructions", "manual", "how to use"],
        }
    
    async def detect_intent(self, text: str) -> Optional[str]:
        """
        Detect user intent from message text.
        
        Process:
        1. Normalize input text
        2. Check rule-based keywords
        3. If no match, could delegate to AI (future enhancement)
        
        Args:
            text: User's message text
            
        Returns:
            Detected intent identifier or None
        """
        if not text:
            return None
        
        normalized_text = normalize_text(text)
        
        # Rule-based detection (fast path)
        intent = self._rule_based_detection(normalized_text)
        
        if intent:
            logger.info(f"Intent detected via rules: {intent}")
            return intent
        
        logger.debug(f"No intent detected for: {text[:50]}")
        return None
    
    def _rule_based_detection(self, normalized_text: str) -> Optional[str]:
        """
        Keyword-based intent detection.
        
        Args:
            normalized_text: Normalized user input

        Returns:
            Matched intent or None
        """
        for intent, keywords in self.intent_keywords.items():
            for keyword in keywords:
                if keyword in normalized_text:
                    return intent
        
        return None
    
    def add_intent_rule(self, intent: str, keywords: list[str]) -> None:
        """
        Add or update intent keywords dynamically.
        
        Args:
            intent: Intent identifier
            keywords: List of keywords for this intent
        """
        self.intent_keywords[intent] = keywords
        logger.info(f"Added/updated intent rule: {intent}")
    
    def get_all_intents(self) -> list[str]:
        """
        Get list of all registered intents.
        
        Returns:
            List of intent identifiers
        """
        return list(self.intent_keywords.keys())
