"""
Text Processing Utilities
Smart text handling for EV charging diagnostic chatbot.
"""
import re
from typing import Optional
from difflib import SequenceMatcher


def normalize_text(text: str) -> str:
    """
    Normalize text for processing.
    
    Args:
        text: Input text
        
    Returns:
        Normalized lowercase text with extra spaces removed
    """
    if not text:
        return ""
    
    # Convert to lowercase
    text = text.lower().strip()
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    return text


def extract_error_pattern(message: str) -> Optional[str]:
    """
    Extract error code patterns from user message using regex.
    
    Supports patterns like:
    - ER001, ER015 (standard format)
    - er001 (lowercase)
    - Error 15, ERROR 001 (with 'error' prefix)
    - 301, 404 (numeric codes)
    - E301, E15 (E prefix)
    
    Args:
        message: User's input message
        
    Returns:
        Extracted error code in standardized format or None
    """
    if not message:
        return None
    
    # Pattern 1: ER### format (case insensitive)
    pattern1 = re.search(r'\b(er\d{3,4})\b', message, re.IGNORECASE)
    if pattern1:
        return pattern1.group(1).upper()
    
    # Pattern 2: "error ###" or "error code ###"
    pattern2 = re.search(r'\berror\s*(?:code)?\s*(\d{1,4})\b', message, re.IGNORECASE)
    if pattern2:
        error_num = pattern2.group(1).zfill(3)
        return f"ER{error_num}"
    
    # Pattern 3: E### format
    pattern3 = re.search(r'\b(e\d{1,4})\b', message, re.IGNORECASE)
    if pattern3:
        error_num = pattern3.group(1)[1:].zfill(3)
        return f"ER{error_num}"
    
    # Pattern 4: Standalone 3-4 digit numbers (less specific, check context)
    pattern4 = re.search(r'\b(\d{3,4})\b', message)
    if pattern4:
        # Return as-is if it's a short message (likely user typing just the code)
        # or if context keywords suggest it's an error code
        message_stripped = message.strip()
        if len(message_stripped) <= 4 or re.match(r'^\d{3,4}\s*$', message_stripped):
            # Just a number - return as-is, let diagnostic engine handle format
            return pattern4.group(1)
        
        # Check for context keywords
        context_keywords = ['error', 'code', 'fault', 'issue', 'problem', 'showing']
        if any(keyword in message.lower() for keyword in context_keywords):
            return pattern4.group(1)
    
    return None


def fuzzy_match_title(query: str, titles: list[str], threshold: float = 0.6) -> Optional[str]:
    """
    Perform fuzzy matching on error titles/descriptions.
    
    This allows matching user queries like:
    - "gun temperature" → "Gun Temperature Limit"
    - "rfid fail" → "RFID Communication Fail"
    - "ocpp communication" → "OCPP Communication Error"
    
    Args:
        query: Search query (normalized)
        titles: List of error titles to match against
        threshold: Similarity threshold (0.0 to 1.0)
        
    Returns:
        Best matching title or None
    """
    if not query or not titles:
        return None
    
    query_normalized = normalize_text(query)
    best_match = None
    best_ratio = 0.0
    
    for title in titles:
        title_normalized = normalize_text(title)
        
        # Calculate similarity ratio
        ratio = SequenceMatcher(None, query_normalized, title_normalized).ratio()
        
        # Also check if query words are in title (partial match boost)
        query_words = set(query_normalized.split())
        title_words = set(title_normalized.split())
        word_overlap = len(query_words & title_words) / len(query_words) if query_words else 0
        
        # Combined score
        combined_score = (ratio * 0.6) + (word_overlap * 0.4)
        
        if combined_score > best_ratio and combined_score >= threshold:
            best_ratio = combined_score
            best_match = title
    
    return best_match


def sanitize_user_input(text: str, max_length: int = 2000) -> str:
    """
    Sanitize user input text.
    
    Args:
        text: Input text to sanitize
        max_length: Maximum allowed length
        
    Returns:
        Sanitized text
    """
    if not text:
        return ""
    
    # Strip whitespace
    text = text.strip()
    
    # Truncate if too long
    if len(text) > max_length:
        text = text[:max_length]
    
    return text


def generate_session_id() -> str:
    """
    Generate a unique session identifier.
    
    Returns:
        Unique session ID string
    """
    import uuid
    return f"sess_{uuid.uuid4().hex[:16]}"


def extract_keywords(text: str) -> list[str]:
    """
    Extract meaningful keywords from text.
    
    Args:
        text: Input text
        
    Returns:
        List of keywords
    """
    if not text:
        return []
    
    # Remove common stop words
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'is', 'it', 'this', 'that', 'i', 'my'
    }
    
    # Normalize and split
    normalized = normalize_text(text)
    words = normalized.split()
    
    # Filter out stop words and short words
    keywords = [w for w in words if w not in stop_words and len(w) > 2]
    
    return keywords
