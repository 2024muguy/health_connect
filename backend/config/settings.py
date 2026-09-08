"""
HealthConnect AI - Application Settings
========================================
Centralized configuration management using Pydantic Settings.
Reads from environment variables with sensible defaults.

Configuration categories:
- Database (Neon DB)
- LLM Providers (OpenAI, Anthropic, Google)
- Vector Database (Pinecone)
- Redis Cache
- RAG Pipeline
- Safety Framework
- Rate Limiting
- Monitoring
"""

import os
from functools import lru_cache
from typing import List, Optional, Dict, Any
from pydantic import Field, validator, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    """Database configuration settings"""
    
    model_config = SettingsConfigDict(env_prefix="DATABASE_", extra="ignore")
    
    # Neon DB Connection
    NEON_DATABASE_URL: str = Field(
        default="",
        description="Neon DB connection string (serverless PostgreSQL)"
    )
    
    # Connection Pool
    POOL_SIZE: int = Field(default=20, description="Database connection pool size")
    MAX_OVERFLOW: int = Field(default=10, description="Maximum overflow connections")
    POOL_TIMEOUT: int = Field(default=30, description="Connection pool timeout in seconds")
    POOL_RECYCLE: int = Field(default=3600, description="Connection recycle time in seconds")
    ECHO: bool = Field(default=False, description="SQL echo for debugging")
    
    @property
    def database_url(self) -> str:
        """Get the database URL"""
        return self.NEON_DATABASE_URL or os.getenv("NEON_DATABASE_URL", "")
    
    @property
    def is_configured(self) -> bool:
        """Check if database is configured"""
        return bool(self.database_url)


class LLMSettings(BaseSettings):
    """LLM Provider configuration settings"""
    
    model_config = SettingsConfigDict(extra="ignore")
    
    # OpenAI
    OPENAI_API_KEY: str = Field(default="", description="OpenAI API key")
    OPENAI_MODEL: str = Field(default="gpt-4", description="OpenAI model name")
    OPENAI_EMBEDDING_MODEL: str = Field(
        default="text-embedding-3-small",
        description="OpenAI embedding model"
    )
    OPENAI_MAX_TOKENS: int = Field(default=2048, description="Maximum tokens for response")
    OPENAI_TEMPERATURE: float = Field(default=0.3, description="Temperature for generation")
    
    # Anthropic Claude
    ANTHROPIC_API_KEY: str = Field(default="", description="Anthropic API key")
    ANTHROPIC_MODEL: str = Field(
        default="claude-3-opus-20240229",
        description="Anthropic model name"
    )
    ANTHROPIC_MAX_TOKENS: int = Field(default=2048, description="Maximum tokens for response")
    ANTHROPIC_TEMPERATURE: float = Field(default=0.3, description="Temperature for generation")
    
    # Google Gemini
    GOOGLE_API_KEY: str = Field(default="", description="Google API key")
    GOOGLE_MODEL: str = Field(default="gemini-pro", description="Google model name")
    GOOGLE_MAX_TOKENS: int = Field(default=2048, description="Maximum tokens for response")
    GOOGLE_TEMPERATURE: float = Field(default=0.3, description="Temperature for generation")
    
    # Default Provider
    DEFAULT_PROVIDER: str = Field(
        default="openai",
        description="Default LLM provider (openai, anthropic, google)"
    )
    
    @property
    def available_providers(self) -> List[str]:
        """Get list of configured providers"""
        providers = []
        if self.OPENAI_API_KEY:
            providers.append("openai")
        if self.ANTHROPIC_API_KEY:
            providers.append("anthropic")
        if self.GOOGLE_API_KEY:
            providers.append("google")
        return providers


class VectorDBSettings(BaseSettings):
    """Vector Database configuration settings"""
    
    model_config = SettingsConfigDict(env_prefix="PINECONE_", extra="ignore")
    
    # Pinecone
    API_KEY: str = Field(default="", description="Pinecone API key")
    ENVIRONMENT: str = Field(default="", description="Pinecone environment")
    INDEX_NAME: str = Field(default="healthconnect-rag", description="Pinecone index name")
    DIMENSION: int = Field(default=1536, description="Vector dimension")
    METRIC: str = Field(default="cosine", description="Similarity metric")
    CLOUD: str = Field(default="aws", description="Cloud provider")
    REGION: str = Field(default="us-west-2", description="Cloud region")
    
    @property
    def is_configured(self) -> bool:
        """Check if Pinecone is configured"""
        return bool(self.API_KEY and self.ENVIRONMENT)


class RedisSettings(BaseSettings):
    """Redis configuration settings"""
    
    model_config = SettingsConfigDict(env_prefix="REDIS_", extra="ignore")
    
    URL: str = Field(default="redis://localhost:6379", description="Redis connection URL")
    PASSWORD: str = Field(default="", description="Redis password")
    DB: int = Field(default=0, description="Redis database number")
    MAX_CONNECTIONS: int = Field(default=50, description="Maximum connections")
    SOCKET_TIMEOUT: int = Field(default=5, description="Socket timeout in seconds")
    SOCKET_CONNECT_TIMEOUT: int = Field(default=5, description="Socket connect timeout")
    
    @property
    def is_configured(self) -> bool:
        """Check if Redis is configured"""
        return bool(self.URL)


class RAGSettings(BaseSettings):
    """RAG Pipeline configuration settings"""
    
    model_config = SettingsConfigDict(extra="ignore")
    
    CHUNK_SIZE: int = Field(default=512, description="Chunk size in tokens")
    CHUNK_OVERLAP: int = Field(default=77, description="Chunk overlap in tokens (15%)")
    TOP_K_RETRIEVAL: int = Field(default=5, description="Number of chunks to retrieve")
    EMBEDDING_MODEL: str = Field(
        default="text-embedding-3-small",
        description="Embedding model name"
    )
    RERANKER_MODEL: str = Field(
        default="cross-encoder/ms-marco-MiniLM-L-6-v2",
        description="Cross-encoder reranker model"
    )
    MAX_CONTEXT_LENGTH: int = Field(default=4096, description="Maximum context length")
    HYBRID_SEARCH_ALPHA: float = Field(
        default=0.6,
        description="Weight for vector search in hybrid (0-1)"
    )
    RRF_CONSTANT: int = Field(default=60, description="Reciprocal Rank Fusion constant")
    
    @property
    def effective_step(self) -> int:
        """Calculate effective step size for chunking"""
        return self.CHUNK_SIZE - self.CHUNK_OVERLAP


class SafetySettings(BaseSettings):
    """Safety Framework configuration settings"""
    
    model_config = SettingsConfigDict(extra="ignore")
    
    SAFETY_THRESHOLD: float = Field(
        default=0.7,
        description="Safety score threshold for blocking"
    )
    EMERGENCY_KEYWORDS: str = Field(
        default="emergency,urgent,severe,critical,unconscious,bleeding,chest pain,difficulty breathing,stroke,heart attack",
        description="Comma-separated emergency keywords"
    )
    MEDICAL_KEYWORDS: str = Field(
        default="diagnosis,treatment,prescription,medication,symptom,condition,disease,illness,prognosis,therapy,surgery",
        description="Comma-separated medical keywords"
    )
    MAX_CONVERSATION_TURNS: int = Field(default=50, description="Maximum conversation turns")
    SESSION_TIMEOUT_MINUTES: int = Field(default=30, description="Session timeout in minutes")
    
    @property
    def emergency_terms(self) -> List[str]:
        """Get emergency terms as list"""
        return [t.strip() for t in self.EMERGENCY_KEYWORDS.split(",") if t.strip()]
    
    @property
    def medical_terms(self) -> List[str]:
        """Get medical terms as list"""
        return [t.strip() for t in self.MEDICAL_KEYWORDS.split(",") if t.strip()]


class RateLimitSettings(BaseSettings):
    """Rate Limiting configuration settings"""
    
    model_config = SettingsConfigDict(env_prefix="RATE_LIMIT_", extra="ignore")
    
    ENABLED: bool = Field(default=True, description="Enable rate limiting")
    REQUESTS: int = Field(default=100, description="Number of requests allowed")
    PERIOD: int = Field(default=60, description="Time period in seconds")
    BURST: int = Field(default=150, description="Burst capacity")
    
    @property
    def rate_string(self) -> str:
        """Get rate limit string for slowapi"""
        return f"{self.REQUESTS}/{self.PERIOD}seconds"


class MonitoringSettings(BaseSettings):
    """Monitoring configuration settings"""
    
    model_config = SettingsConfigDict(env_prefix="PROMETHEUS_", extra="ignore")
    
    ENABLED: bool = Field(default=True, description="Enable Prometheus monitoring")
    PORT: int = Field(default=9090, description="Prometheus port")
    GRAFANA_PORT: int = Field(default=3000, description="Grafana port")
    GRAFANA_ADMIN_PASSWORD: str = Field(default="admin", description="Grafana admin password")


class Settings(BaseSettings):
    """
    Main application settings aggregating all configuration categories.
    
    Usage:
        from config.settings import get_settings
        settings = get_settings()
        settings.llm.openai_api_key
    """
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
    
    # Application
    APP_NAME: str = Field(default="HealthConnect AI Assistant", description="Application name")
    APP_VERSION: str = Field(default="1.0.0", description="Application version")
    ENVIRONMENT: str = Field(default="development", description="Environment (development, staging, production)")
    DEBUG: bool = Field(default=False, description="Debug mode")
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    API_PREFIX: str = Field(default="/api/v1", description="API prefix")
    SECRET_KEY: str = Field(default="", description="Secret key for JWT")
    
    # Access Token
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, description="Access token expiry in minutes")
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, description="Refresh token expiry in days")
    
    # CORS
    CORS_ORIGINS: str = Field(default="*", description="CORS origins (comma-separated)")
    CORS_METHODS: str = Field(default="GET,POST,PUT,DELETE,OPTIONS", description="CORS methods")
    CORS_HEADERS: str = Field(default="*", description="CORS headers")
    
    # Sub-settings
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    llm: LLMSettings = Field(default_factory=LLMSettings)
    vector_db: VectorDBSettings = Field(default_factory=VectorDBSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)
    rag: RAGSettings = Field(default_factory=RAGSettings)
    safety: SafetySettings = Field(default_factory=SafetySettings)
    rate_limit: RateLimitSettings = Field(default_factory=RateLimitSettings)
    monitoring: MonitoringSettings = Field(default_factory=MonitoringSettings)
    
    @property
    def is_production(self) -> bool:
        """Check if running in production"""
        return self.ENVIRONMENT.lower() == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development"""
        return self.ENVIRONMENT.lower() in ["development", "dev", "local"]
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Get CORS origins as list"""
        if self.CORS_ORIGINS == "*":
            return ["*"]
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]
    
    @property
    def cors_methods_list(self) -> List[str]:
        """Get CORS methods as list"""
        return [method.strip() for method in self.CORS_METHODS.split(",") if method.strip()]
    
    def validate(self) -> bool:
        """Validate critical configuration"""
        errors = []
        
        if not self.SECRET_KEY:
            errors.append("SECRET_KEY is not set")
        
        if not self.llm.OPENAI_API_KEY and not self.llm.ANTHROPIC_API_KEY:
            errors.append("At least one LLM provider API key must be set")
        
        if not self.vector_db.API_KEY:
            errors.append("PINECONE_API_KEY is not set")
        
        if errors:
            for error in errors:
                import logging
                logging.error(f"Configuration error: {error}")
            return False
        
        return True


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    
    Returns:
        Settings: Application settings
    """
    settings = Settings()
    return settings


# Create default settings instance
settings = get_settings()