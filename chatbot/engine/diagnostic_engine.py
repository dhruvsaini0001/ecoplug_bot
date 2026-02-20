"""
Diagnostic Engine
★ CORE COMPONENT ★ 
Intelligent EV charging error code detection and solution retrieval.

This engine:
1. Loads error_codes_complete.json at startup (cached in memory)
2. Detects error codes using regex + fuzzy matching
3. Returns structured diagnostic information
4. Supports multiple error code formats
"""
import json
from pathlib import Path
from typing import Optional, Dict, Any, List
from ..core.logger import setup_logger
from ..utils.text_utils import extract_error_pattern, fuzzy_match_title, normalize_text, extract_keywords

logger = setup_logger(__name__)


class DiagnosticEngine:
    """
    EV Charging Station Error Code Detection and Diagnostic Engine.
    
    This is the BRAIN of the diagnostic system.
    """
    
    def __init__(self, error_codes_path: Optional[str] = None):
        """
        Initialize the diagnostic engine.
        
        Args:
            error_codes_path: Path to error codes JSON file
        """
        self.error_codes: List[Dict[str, Any]] = []
        self.error_index: Dict[str, Dict[str, Any]] = {}  # Fast lookup by code
        self.error_codes_path = error_codes_path or self._get_default_path()
        
    def _get_default_path(self) -> str:
        """Get default path to error codes JSON file."""
        # Navigate from engine/ to root
        base_path = Path(__file__).parent.parent.parent
        return str(base_path / "error_codes_complete.json")
    
    async def load_error_codes(self) -> None:
        """
        Load error codes from JSON file at startup.
        This is called ONCE during application initialization.
        All error data is cached in memory for fast lookup.
        """
        try:
            with open(self.error_codes_path, "r", encoding="utf-8") as f:
                self.error_codes = json.load(f)
            
            # Build index for O(1) lookup by error code
            for error in self.error_codes:
                error_code = error.get("Error_Code", "").upper()
                if error_code:
                    self.error_index[error_code] = error
            
            logger.info(
                f"Loaded {len(self.error_codes)} error codes from diagnostic database",
                extra={"error_count": len(self.error_codes)}
            )
            
        except FileNotFoundError:
            logger.error(f"Error codes file not found: {self.error_codes_path}")
            self.error_codes = []
            self.error_index = {}
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in error codes file: {e}")
            self.error_codes = []
            self.error_index = {}
    
    async def detect_error_code(self, message: str) -> Optional[Dict[str, Any]]:
        """
        ★★★ MAIN DIAGNOSTIC FUNCTION ★★★
        
        Detect error code from user message and return structured diagnostic info.
        
        Detection Strategy:
        1. Extract error code pattern using regex (ER001, error 15, 301, etc.)
        2. Direct lookup in error index
        3. Fuzzy match against error titles/descriptions
        4. Keyword-based search in descriptions
        
        Args:
            message: User's input message
            
        Returns:
            Structured error object or None:
            {
                "error_code": "ER001",
                "title": "Gun Temperature Limit",
                "description": "The gun temperature exceeded...",
                "solutions": ["Remove the gun...", "If physical heating..."]
            }
        """
        if not message or not self.error_codes:
            return None
        
        # STEP 1: Try regex pattern extraction
        error_code = extract_error_pattern(message)
        
        if error_code:
            logger.info(f"Extracted error code from pattern: {error_code}")
            result = self._lookup_by_code(error_code)
            if result:
                return result
        
        # STEP 2: Fuzzy match against error titles
        normalized_msg = normalize_text(message)
        result = self._fuzzy_match_titles(normalized_msg)
        if result:
            logger.info(f"Matched error via fuzzy title matching: {result['error_code']}")
            return result
        
        # STEP 3: Keyword search in descriptions
        result = self._keyword_search(normalized_msg)
        if result:
            logger.info(f"Matched error via keyword search: {result['error_code']}")
            return result
        
        logger.debug(f"No error code detected in message: {message[:50]}")
        return None
    
    def _lookup_by_code(self, error_code: str) -> Optional[Dict[str, Any]]:
        """
        Direct lookup by error code.
        
        Supports multiple formats:
        - "301" → checks "301" then "ER301"
        - "ER001" → checks "ER001" then "001"
        
        Args:
            error_code: Error code (e.g., "ER001" or "301")
            
        Returns:
            Structured error object or None
        """
        error_code_upper = error_code.upper().strip()
        
        # Try direct lookup first
        if error_code_upper in self.error_index:
            return self._format_error_response(self.error_index[error_code_upper])
        
        # If numeric without ER prefix, try adding ER prefix
        if not error_code_upper.startswith("ER") and error_code_upper.isdigit():
            er_version = f"ER{error_code_upper}"
            if er_version in self.error_index:
                return self._format_error_response(self.error_index[er_version])
        
        # If has ER prefix, try without it
        if error_code_upper.startswith("ER"):
            numeric_version = error_code_upper[2:]
            if numeric_version in self.error_index:
                return self._format_error_response(self.error_index[numeric_version])
        
        return None
    
    def _fuzzy_match_titles(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Fuzzy match against error titles.
        
        Args:
            query: Normalized user query
            
        Returns:
            Best matching error object or None
        """
        titles = [error.get("Tittle", "") for error in self.error_codes]
        matched_title = fuzzy_match_title(query, titles, threshold=0.6)
        
        if matched_title:
            # Find the error with this title
            for error in self.error_codes:
                if error.get("Tittle") == matched_title:
                    return self._format_error_response(error)
        
        return None
    
    def _keyword_search(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Search error descriptions using keywords.
        
        Args:
            query: Normalized user query
            
        Returns:
            Best matching error object or None
        """
        keywords = extract_keywords(query)
        
        if not keywords:
            return None
        
        best_match = None
        best_score = 0
        
        for error in self.error_codes:
            description = normalize_text(error.get("Description", ""))
            title = normalize_text(error.get("Tittle", ""))
            
            # Count keyword matches
            score = 0
            for keyword in keywords:
                if keyword in description or keyword in title:
                    score += 1
            
            # Require at least 2 keyword matches to avoid false positives
            if score > best_score and score >= 2:
                best_score = score
                best_match = error
        
        if best_match:
            return self._format_error_response(best_match)
        
        return None
    
    def _format_error_response(self, error_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format error data into standardized response structure.
        
        Args:
            error_data: Raw error data from JSON
            
        Returns:
            Formatted error object
        """
        return {
            "error_code": error_data.get("Error_Code", ""),
            "title": error_data.get("Tittle", ""),  # Note: JSON has typo "Tittle"
            "description": error_data.get("Description", ""),
            "solutions": error_data.get("Solution", [])
        }
    
    def get_error_by_code(self, error_code: str) -> Optional[Dict[str, Any]]:
        """
        Get error information by exact error code.
        
        Args:
            error_code: Error code (e.g., "ER001")
            
        Returns:
            Formatted error object or None
        """
        return self._lookup_by_code(error_code)
    
    def is_database_loaded(self) -> bool:
        """
        Check if error database is loaded.
        
        Returns:
            True if database is loaded, False otherwise
        """
        return len(self.error_codes) > 0
    
    def get_total_error_count(self) -> int:
        """
        Get total number of error codes in database.
        
        Returns:
            Count of error codes
        """
        return len(self.error_codes)
