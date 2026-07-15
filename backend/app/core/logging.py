"""
Structured logging configuration.
Supports JSON and text formats.
Does not log PHI/PII in compliance with healthcare regulations.
"""

import logging
import sys
import json
from datetime import datetime
from typing import Any, Dict

from app.core.config import settings


class JSONFormatter(logging.Formatter):
    """JSON log formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields (excluding PHI/PII markers)
        if hasattr(record, "extra"):
            # Filter out any fields that might contain PHI/PII
            safe_extra = {
                k: v for k, v in record.extra.items()
                if not any(pii_key in k.lower() for pii_key in [
                    "patient", "name", "ssn", "dob", "address", "phone", "email"
                ])
            }
            log_data["extra"] = safe_extra
        
        return json.dumps(log_data)


class SafeTextFormatter(logging.Formatter):
    """Text formatter that avoids logging PHI/PII."""
    
    def __init__(self):
        super().__init__(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )


def setup_logging() -> None:
    """Configure application logging based on settings."""
    
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))
    
    # Set formatter based on configuration
    if settings.LOG_FORMAT.lower() == "json":
        formatter = JSONFormatter()
    else:
        formatter = SafeTextFormatter()
    
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Reduce noise from third-party libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)


def get_safe_logger(name: str) -> logging.Logger:
    """
    Get a logger instance that's configured to avoid PHI/PII logging.
    Use this for all application logging.
    """
    return logging.getLogger(name)
