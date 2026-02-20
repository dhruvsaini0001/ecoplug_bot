"""
Structured Logging System
Production-ready logging with JSON formatting for EV diagnostic platform.
"""
import logging
import sys
import json
from datetime import datetime
from typing import Any, Dict
from .config import get_settings


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields for tracking
        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id
        if hasattr(record, "session_id"):
            log_data["session_id"] = record.session_id
        if hasattr(record, "platform"):
            log_data["platform"] = record.platform
        if hasattr(record, "error_code"):
            log_data["error_code"] = record.error_code
            
        return json.dumps(log_data)


def setup_logger(name: str = __name__) -> logging.Logger:
    """
    Setup and configure application logger.
    
    Args:
        name: Logger name (usually module name)
        
    Returns:
        Configured logger instance
    """
    settings = get_settings()
    logger = logging.getLogger(name)
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))
    
    handler = logging.StreamHandler(sys.stdout)
    
    if settings.LOG_FORMAT == "json":
        handler.setFormatter(JSONFormatter())
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
    
    logger.addHandler(handler)
    logger.propagate = False
    
    return logger


# Default logger instance
logger = setup_logger("ev_chatbot")
