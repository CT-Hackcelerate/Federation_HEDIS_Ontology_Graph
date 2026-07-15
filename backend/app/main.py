"""
Main FastAPI application entry point.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging

from app.core.config import settings
from app.core.logging import setup_logging
from app.core.exceptions import CDSAPIException, cds_exception_handler
from app.routes import health, cds_services


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup and shutdown events."""
    # Startup
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("CDS API starting up...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    yield
    # Shutdown
    logger.info("CDS API shutting down...")


app = FastAPI(
    title=settings.APP_NAME,
    description="Clinical Decision Support API - CDS Hooks compatible",
    version="1.0.0",
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
    openapi_url="/openapi.json" if settings.ENVIRONMENT != "production" else None,
    lifespan=lifespan,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Register exception handlers
app.add_exception_handler(CDSAPIException, cds_exception_handler)


@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint - API information and available endpoints.
    """
    return {
        "name": settings.APP_NAME,
        "version": "1.0.0",
        "description": "CDS Hooks compatible Clinical Decision Support API",
        "endpoints": {
            "health": "/health",
            "discovery": "/cds-services",
            "documentation": "/docs",
        }
    }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler to prevent internal error exposure to EHR.
    Does not log PHI/PII - only logs error type and path.
    """
    logger = logging.getLogger(__name__)
    logger.error(f"Unhandled exception on {request.method} {request.url.path}: {type(exc).__name__}")
    
    # Return CDS-compliant empty cards response on error
    return JSONResponse(
        status_code=500,
        content={"cards": []},
    )


# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(cds_services.router, tags=["CDS Services"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.ENVIRONMENT == "development",
    )
