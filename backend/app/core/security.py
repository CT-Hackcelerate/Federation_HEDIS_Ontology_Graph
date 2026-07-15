"""
Security middleware and authentication utilities.
Placeholder implementation for API key and bearer token validation.
"""

from fastapi import HTTPException, Security, Depends
from fastapi.security import APIKeyHeader, HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

# Security schemes
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
bearer_scheme = HTTPBearer(auto_error=False)


async def verify_api_key(api_key: Optional[str] = Security(api_key_header)) -> bool:
    """
    Verify API key from X-API-Key header.
    Returns True if valid or if security is disabled in development.
    """
    # Skip validation in development if no API key configured
    if settings.ENVIRONMENT == "development" and not settings.API_KEY:
        return True
    
    if not api_key:
        logger.warning("API key missing in request")
        raise HTTPException(
            status_code=401,
            detail="API key required",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    if api_key != settings.API_KEY:
        logger.warning("Invalid API key provided")
        raise HTTPException(
            status_code=403,
            detail="Invalid API key",
        )
    
    return True


async def verify_bearer_token(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(bearer_scheme)
) -> bool:
    """
    Verify Bearer token from Authorization header.
    Placeholder implementation - extend with JWT validation as needed.
    """
    # Skip validation in development if no secret configured
    if settings.ENVIRONMENT == "development" and not settings.BEARER_TOKEN_SECRET:
        return True
    
    if not credentials:
        logger.warning("Bearer token missing in request")
        raise HTTPException(
            status_code=401,
            detail="Bearer token required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Placeholder: Simple token comparison
    # In production, implement proper JWT validation
    if credentials.credentials != settings.BEARER_TOKEN_SECRET:
        logger.warning("Invalid bearer token provided")
        raise HTTPException(
            status_code=403,
            detail="Invalid token",
        )
    
    return True


async def verify_any_auth(
    api_key: Optional[str] = Security(api_key_header),
    bearer: Optional[HTTPAuthorizationCredentials] = Security(bearer_scheme),
) -> bool:
    """
    Accept either API key or Bearer token authentication.
    Use this for flexible authentication requirements.
    """
    # Skip in development if no security configured
    if settings.ENVIRONMENT == "development":
        if not settings.API_KEY and not settings.BEARER_TOKEN_SECRET:
            return True
    
    # Try API key first
    if api_key and api_key == settings.API_KEY:
        return True
    
    # Try bearer token
    if bearer and bearer.credentials == settings.BEARER_TOKEN_SECRET:
        return True
    
    # Neither valid
    logger.warning("Authentication failed - no valid credentials")
    raise HTTPException(
        status_code=401,
        detail="Valid authentication required",
        headers={"WWW-Authenticate": "Bearer, ApiKey"},
    )
