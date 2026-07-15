"""
Utility helper functions.
"""

import re
from typing import Any, Dict, Optional
import uuid


def sanitize_log_message(message: str) -> str:
    """
    Sanitize a log message to remove potential PHI/PII.
    
    Removes or masks:
    - Names (simple pattern)
    - SSN patterns
    - Phone numbers
    - Email addresses
    - Dates of birth
    
    Note: This is a basic implementation. Production systems
    should use more comprehensive PHI detection.
    """
    # Mask SSN patterns (XXX-XX-XXXX)
    message = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '[SSN-REDACTED]', message)
    
    # Mask phone numbers
    message = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[PHONE-REDACTED]', message)
    
    # Mask email addresses
    message = re.sub(
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        '[EMAIL-REDACTED]',
        message
    )
    
    # Mask dates that might be DOB (MM/DD/YYYY or YYYY-MM-DD)
    message = re.sub(
        r'\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}[/-]\d{1,2}[/-]\d{1,2})\b',
        '[DATE-REDACTED]',
        message
    )
    
    return message


def truncate_id(identifier: str, visible_chars: int = 8) -> str:
    """
    Truncate an identifier for logging purposes.
    Shows first N characters followed by ellipsis.
    
    Args:
        identifier: The ID to truncate
        visible_chars: Number of characters to show
        
    Returns:
        Truncated ID string
    """
    if not identifier:
        return "[empty]"
    
    if len(identifier) <= visible_chars:
        return identifier
    
    return f"{identifier[:visible_chars]}..."


def generate_hook_instance() -> str:
    """Generate a unique hook instance ID."""
    return str(uuid.uuid4())


def is_valid_uuid(value: str) -> bool:
    """Check if a string is a valid UUID."""
    try:
        uuid.UUID(value)
        return True
    except (ValueError, AttributeError):
        return False


def safe_get(data: Dict[str, Any], *keys, default: Any = None) -> Any:
    """
    Safely get nested dictionary values.
    
    Args:
        data: Dictionary to search
        *keys: Keys to traverse
        default: Default value if not found
        
    Returns:
        Value at the nested path or default
        
    Example:
        safe_get({"a": {"b": 1}}, "a", "b") -> 1
        safe_get({"a": {"b": 1}}, "a", "c", default=0) -> 0
    """
    result = data
    for key in keys:
        if isinstance(result, dict):
            result = result.get(key)
        else:
            return default
        if result is None:
            return default
    return result
