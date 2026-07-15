"""
Application configuration using Pydantic Settings.
Environment-based configuration with validation.
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    APP_NAME: str = "Clinical Decision Support API"
    ENVIRONMENT: str = Field(default="development", description="development | staging | production")
    DEBUG: bool = Field(default=False)
    
    # API Security
    API_KEY: str = Field(default="", description="API key for authentication")
    BEARER_TOKEN_SECRET: str = Field(default="", description="Secret for bearer token validation")
    
    # CORS
    ALLOWED_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080"],
        description="Allowed CORS origins"
    )
    
    # Lakebase PostgreSQL Configuration
    LAKEBASE_POSTGRES_HOST: str = Field(default="", description="Lakebase PostgreSQL host")
    LAKEBASE_POSTGRES_PORT: int = Field(default=5432, description="Lakebase PostgreSQL port")
    LAKEBASE_POSTGRES_DATABASE: str = Field(default="", description="Lakebase database name")
    LAKEBASE_POSTGRES_USER: str = Field(default="", description="Lakebase PostgreSQL user")
    LAKEBASE_POSTGRES_PASSWORD: str = Field(default="", description="Lakebase PostgreSQL password (Databricks PAT)")
    LAKEBASE_POSTGRES_SCHEMA: str = Field(default="public", description="PostgreSQL schema name")
    LAKEBASE_POSTGRES_TABLE: str = Field(default="input_hackathon", description="Table name")
    
    # Parquet Configuration (alternative to Databricks)
    PARQUET_DATA_PATH: str = Field(
        default="./data/clinical",
        description="Path to Parquet files for local/mock data"
    )
    USE_MOCK_DATA: bool = Field(
        default=True,
        description="Use mock data instead of real Databricks connection"
    )
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO")
    LOG_FORMAT: str = Field(default="json", description="json | text")
    
    # Server
    HOST: str = Field(default="0.0.0.0")
    PORT: int = Field(default=8000)
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Cached settings instance."""
    return Settings()


settings = get_settings()
