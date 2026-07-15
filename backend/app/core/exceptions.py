"""
Custom exception handling for CDS API.
All exceptions return CDS-compliant responses with empty cards array.
Internal error details are never exposed to EHR systems.
"""

from fastapi import Request
from fastapi.responses import JSONResponse
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class CDSAPIException(Exception):
    """
    Base exception for CDS API errors.
    Always returns CDS-compliant response with cards array.
    """
    
    def __init__(
        self,
        status_code: int = 500,
        message: str = "An error occurred",
        log_message: Optional[str] = None,
    ):
        self.status_code = status_code
        self.message = message
        # Internal message for logging - never exposed to client
        self.log_message = log_message or message
        super().__init__(self.message)


class ServiceNotFoundException(CDSAPIException):
    """Raised when a CDS service is not found."""
    
    def __init__(self, service_id: str):
        super().__init__(
            status_code=404,
            message="Service not found",
            log_message=f"CDS service not found: {service_id}",
        )


class InvalidRequestException(CDSAPIException):
    """Raised when request validation fails."""
    
    def __init__(self, detail: str = "Invalid request"):
        super().__init__(
            status_code=400,
            message="Invalid request format",
            log_message=f"Invalid CDS request: {detail}",
        )


class DataSourceException(CDSAPIException):
    """Raised when data source connection fails."""
    
    def __init__(self, source: str = "unknown"):
        super().__init__(
            status_code=503,
            message="Service temporarily unavailable",
            log_message=f"Data source error: {source}",
        )


class AuthenticationException(CDSAPIException):
    """Raised for authentication failures."""
    
    def __init__(self):
        super().__init__(
            status_code=401,
            message="Authentication required",
            log_message="Authentication failed",
        )


async def cds_exception_handler(request: Request, exc: CDSAPIException) -> JSONResponse:
    """
    Handle CDS API exceptions and return compliant responses.
    - Never exposes internal error details
    - Always returns cards array (even if empty)
    - Logs internal details for debugging
    """
    # Log internal message (without PHI/PII)
    logger.error(f"{request.method} {request.url.path}: {exc.log_message}")
    
    # Return CDS-compliant response
    # For 4xx/5xx errors, return empty cards to allow EHR to continue
    return JSONResponse(
        status_code=exc.status_code,
        content={"cards": []},
    )
