"""
Simplified Settings for Single-User Neurosurgical Knowledge System
All functionality retained, unnecessary complexity removed
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List, Optional
from pathlib import Path
import os


class Settings(BaseSettings):
    """Simplified application settings"""

    # Application
    APP_NAME: str = "Neurosurgical Knowledge System"
    VERSION: str = "2.0.0-simplified"
    DEBUG: bool = True

    # Database (using asyncpg for async support)
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://neurosurg:neurosurg123@localhost:5432/neurosurgical_knowledge"
    )

    # Redis Cache
    REDIS_URL: str = Field(default="redis://localhost:6379/0")
    CACHE_TTL_SECONDS: int = 3600

    # AI Services (only what you need)
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    GOOGLE_API_KEY: Optional[str] = None
    PERPLEXITY_API_KEY: Optional[str] = None

    # AI Model Configurations
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    ANTHROPIC_MODEL: str = "claude-3-opus-20240229"
    GEMINI_MODEL: str = "gemini-1.5-pro"
    PERPLEXITY_MODEL: str = "llama-3.1-sonar-small-128k-online"

    # Medical APIs
    PUBMED_API_KEY: Optional[str] = None

    # File Storage (local only)
    TEXTBOOKS_PATH: Path = Path("./textbooks")
    STORAGE_PATH: Path = Path("./storage")
    TEMP_PATH: Path = Path("./temp")

    # Content Processing
    MAX_FILE_SIZE_MB: int = 100
    MAX_SOURCES_PER_SYNTHESIS: int = 15
    MIN_RELEVANCE_SCORE: float = 0.3

    # Neurosurgical Sections (Core feature)
    NEUROSURGICAL_SECTIONS: List[str] = Field(
        default=[
            "Introduction",
            "Neuroanatomy",
            "Pathophysiology",
            "Clinical Presentation",
            "Neuroimaging",
            "Differential Diagnosis",
            "Surgical Indications",
            "Surgical Technique",
            "Complications",
            "Outcomes",
            "Key References"
        ]
    )

    # Feature Flags (keep what you use)
    ENABLE_BEHAVIORAL_LEARNING: bool = True
    ENABLE_CITATION_NETWORK: bool = True
    ENABLE_EXTERNAL_SEARCH: bool = True
    ENABLE_MEDICAL_VALIDATION: bool = True

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # Ignore frontend/other service variables

    @property
    def database_url_async(self) -> str:
        """Get async database URL"""
        if self.DATABASE_URL.startswith("postgresql://"):
            return self.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
        return self.DATABASE_URL

    def validate_paths(self):
        """Create necessary directories"""
        for path in [self.TEXTBOOKS_PATH, self.STORAGE_PATH, self.TEMP_PATH]:
            path.mkdir(parents=True, exist_ok=True)

    def get_ai_config(self):
        """Get available AI services"""
        config = {}

        if self.OPENAI_API_KEY:
            config["openai"] = {
                "api_key": self.OPENAI_API_KEY,
                "model": "gpt-4-turbo-preview"
            }

        if self.ANTHROPIC_API_KEY:
            config["anthropic"] = {
                "api_key": self.ANTHROPIC_API_KEY,
                "model": "claude-3-opus-20240229"
            }

        if self.GOOGLE_API_KEY:
            config["google"] = {
                "api_key": self.GOOGLE_API_KEY,
                "model": "gemini-1.5-pro"
            }

        return config


# Create settings instance
settings = Settings()
settings.validate_paths()