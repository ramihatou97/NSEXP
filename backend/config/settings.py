"""
Configuration Settings for Neurosurgical Knowledge Management System
Environment-specific settings with neurosurgery-focused defaults
"""

from pydantic_settings import BaseSettings
from pydantic import Field, validator
from typing import List, Optional, Dict, Any
from pathlib import Path
import os
from enum import Enum


class Environment(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"


class Settings(BaseSettings):
    """
    Application settings with neurosurgery-specific configurations
    """

    # Application
    APP_NAME: str = "Neurosurgical Knowledge Management System"
    APP_VERSION: str = "2.0.0"
    ENVIRONMENT: Environment = Environment.DEVELOPMENT
    DEBUG: bool = Field(default=False)
    HOST: str = Field(default="0.0.0.0")
    PORT: int = Field(default=8000)

    # Security
    SECRET_KEY: str = Field(..., min_length=32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # CORS
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"]
    )
    ALLOWED_HOSTS: List[str] = Field(default=["*"])

    # Database
    DATABASE_URL: str = Field(
        default="postgresql://neurosurg:password@localhost:5432/neurosurgical_knowledge"
    )
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 40
    DATABASE_POOL_TIMEOUT: int = 30

    # Redis Cache
    REDIS_URL: str = Field(default="redis://localhost:6379/0")
    CACHE_TTL_SECONDS: int = 3600  # 1 hour

    # Elasticsearch
    ELASTICSEARCH_URL: str = Field(default="http://localhost:9200")
    ELASTICSEARCH_INDEX_PREFIX: str = "neurosurg"

    # Vector Database (for embeddings)
    VECTOR_DB_TYPE: str = "pinecone"  # pinecone, weaviate, chromadb
    PINECONE_API_KEY: Optional[str] = None
    PINECONE_ENVIRONMENT: Optional[str] = None
    PINECONE_INDEX: str = "neurosurgical-knowledge"
    EMBEDDING_DIMENSION: int = 1536  # OpenAI embedding dimension

    # AI Services
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-large"

    ANTHROPIC_API_KEY: Optional[str] = None
    ANTHROPIC_MODEL: str = "claude-3-opus-20240229"

    GOOGLE_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-1.5-pro"

    PERPLEXITY_API_KEY: Optional[str] = None

    # Medical APIs
    PUBMED_API_KEY: Optional[str] = None
    PUBMED_RATE_LIMIT: int = 10  # requests per second

    # Neurosurgery-Specific Settings
    DEFAULT_SPECIALTY: str = "neurosurgery"
    MEDICAL_ONTOLOGY_PATH: str = "resources/medical_ontologies"
    ICD10_DATABASE_PATH: str = "resources/icd10_codes.db"
    CPT_DATABASE_PATH: str = "resources/cpt_codes.db"

    # Content Processing
    MAX_FILE_SIZE_MB: int = 100
    SUPPORTED_FILE_TYPES: List[str] = Field(
        default=[".pdf", ".docx", ".pptx", ".epub"]
    )
    OCR_ENABLED: bool = True
    OCR_LANGUAGE: str = "eng"

    # Chapter Synthesis Settings
    MAX_SOURCES_PER_SYNTHESIS: int = 20
    MIN_RELEVANCE_SCORE: float = 0.3
    SYNTHESIS_TIMEOUT_SECONDS: int = 300  # 5 minutes
    INCLUDE_IMAGES_BY_DEFAULT: bool = True
    INCLUDE_TABLES_BY_DEFAULT: bool = True

    # Neurosurgical Sections (for chapter structure)
    NEUROSURGICAL_SECTIONS: List[str] = Field(
        default=[
            "Introduction",
            "Epidemiology",
            "Neuroanatomy",
            "Pathophysiology",
            "Clinical Presentation",
            "Neurological Examination",
            "Neuroimaging",
            "Differential Diagnosis",
            "Surgical Indications",
            "Preoperative Planning",
            "Surgical Anatomy",
            "Patient Positioning",
            "Surgical Approach",
            "Surgical Technique",
            "Neuronavigation",
            "Intraoperative Monitoring",
            "Surgical Pearls and Pitfalls",
            "Closure Technique",
            "Postoperative Care",
            "Complications and Management",
            "Outcomes and Prognosis",
            "Case Examples",
            "Key References"
        ]
    )

    # Quality Metrics
    MIN_MEDICAL_ACCURACY_SCORE: float = 0.8
    MIN_COMPLETENESS_SCORE: float = 0.7
    REQUIRE_EVIDENCE_LEVEL: bool = True

    # File Storage
    UPLOAD_PATH: Path = Path("uploads")
    TEXTBOOK_STORAGE_PATH: Path = Path("storage/textbooks")
    IMAGE_STORAGE_PATH: Path = Path("storage/images")
    TEMP_PATH: Path = Path("temp")

    # AWS S3 (optional)
    USE_S3: bool = False
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    S3_BUCKET: Optional[str] = None
    S3_REGION: str = "us-east-1"

    # Monitoring & Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"  # json or text
    SENTRY_DSN: Optional[str] = None
    PROMETHEUS_ENABLED: bool = True

    # Email (for notifications)
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAIL_FROM: str = "noreply@neurosurgicalknowledge.com"

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000

    # Background Tasks
    CELERY_BROKER_URL: str = Field(default="redis://localhost:6379/1")
    CELERY_RESULT_BACKEND: str = Field(default="redis://localhost:6379/2")
    CELERY_TASK_TIME_LIMIT: int = 600  # 10 minutes

    # WebSocket
    WS_MESSAGE_QUEUE_SIZE: int = 100
    WS_HEARTBEAT_INTERVAL: int = 30

    # Feature Flags
    ENABLE_BEHAVIORAL_LEARNING: bool = True
    ENABLE_CITATION_NETWORK: bool = True
    ENABLE_EXTERNAL_SEARCH: bool = True
    ENABLE_NUANCE_MERGE: bool = True
    ENABLE_MEDICAL_VALIDATION: bool = True

    # Neurosurgery-Specific Integrations
    ENABLE_DICOM_SUPPORT: bool = True
    ENABLE_NEURONAVIGATION: bool = False
    ENABLE_SURGICAL_PLANNING: bool = False
    ENABLE_3D_VISUALIZATION: bool = False

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

    @validator("ENVIRONMENT", pre=True)
    def validate_environment(cls, v):
        if isinstance(v, str):
            return Environment(v.lower())
        return v

    @validator("DATABASE_URL")
    def validate_database_url(cls, v):
        if not v.startswith(("postgresql://", "postgresql+asyncpg://")):
            raise ValueError("Database URL must be PostgreSQL")
        return v

    @validator("UPLOAD_PATH", "TEXTBOOK_STORAGE_PATH", "IMAGE_STORAGE_PATH", "TEMP_PATH")
    def create_directories(cls, v):
        path = Path(v)
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == Environment.PRODUCTION

    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT == Environment.DEVELOPMENT

    @property
    def database_url_async(self) -> str:
        """Get async database URL"""
        if self.DATABASE_URL.startswith("postgresql://"):
            return self.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
        return self.DATABASE_URL

    def get_ai_config(self) -> Dict[str, Any]:
        """Get AI service configuration"""
        config = {}

        if self.OPENAI_API_KEY:
            config["openai"] = {
                "api_key": self.OPENAI_API_KEY,
                "model": self.OPENAI_MODEL,
                "embedding_model": self.OPENAI_EMBEDDING_MODEL
            }

        if self.ANTHROPIC_API_KEY:
            config["anthropic"] = {
                "api_key": self.ANTHROPIC_API_KEY,
                "model": self.ANTHROPIC_MODEL
            }

        if self.GOOGLE_API_KEY:
            config["google"] = {
                "api_key": self.GOOGLE_API_KEY,
                "model": self.GEMINI_MODEL
            }

        if self.PERPLEXITY_API_KEY:
            config["perplexity"] = {
                "api_key": self.PERPLEXITY_API_KEY
            }

        return config

    def get_vector_db_config(self) -> Dict[str, Any]:
        """Get vector database configuration"""
        if self.VECTOR_DB_TYPE == "pinecone":
            return {
                "type": "pinecone",
                "api_key": self.PINECONE_API_KEY,
                "environment": self.PINECONE_ENVIRONMENT,
                "index_name": self.PINECONE_INDEX,
                "dimension": self.EMBEDDING_DIMENSION
            }
        # Add other vector DB configs as needed
        return {}


# Environment-specific configurations
class DevelopmentSettings(Settings):
    """Development environment settings"""
    DEBUG: bool = True
    LOG_LEVEL: str = "DEBUG"
    RATE_LIMIT_ENABLED: bool = False


class StagingSettings(Settings):
    """Staging environment settings"""
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"


class ProductionSettings(Settings):
    """Production environment settings"""
    DEBUG: bool = False
    LOG_LEVEL: str = "WARNING"
    RATE_LIMIT_ENABLED: bool = True
    REQUIRE_EVIDENCE_LEVEL: bool = True
    ENABLE_MEDICAL_VALIDATION: bool = True

    @validator("SECRET_KEY")
    def validate_secret_key(cls, v):
        if len(v) < 64:
            raise ValueError("Production secret key must be at least 64 characters")
        return v


class TestingSettings(Settings):
    """Testing environment settings"""
    ENVIRONMENT: Environment = Environment.TESTING
    DATABASE_URL: str = "postgresql://test:test@localhost:5432/test_neurosurg"
    REDIS_URL: str = "redis://localhost:6379/15"
    LOG_LEVEL: str = "DEBUG"
    RATE_LIMIT_ENABLED: bool = False


# Factory function to get settings based on environment
def get_settings() -> Settings:
    """
    Get settings based on environment
    """
    env = os.getenv("ENVIRONMENT", "development").lower()

    settings_map = {
        "development": DevelopmentSettings,
        "staging": StagingSettings,
        "production": ProductionSettings,
        "testing": TestingSettings
    }

    settings_class = settings_map.get(env, DevelopmentSettings)
    return settings_class()


# Create settings instance
settings = get_settings()


# Validate critical settings for production
if settings.is_production:
    required_settings = [
        "SECRET_KEY",
        "DATABASE_URL",
        "OPENAI_API_KEY",
        "SENTRY_DSN"
    ]

    for setting in required_settings:
        if not getattr(settings, setting, None):
            raise ValueError(f"Missing required production setting: {setting}")

    # Ensure secure settings
    if settings.DEBUG:
        raise ValueError("DEBUG must be False in production")

    if "*" in settings.ALLOWED_HOSTS:
        raise ValueError("ALLOWED_HOSTS cannot contain '*' in production")