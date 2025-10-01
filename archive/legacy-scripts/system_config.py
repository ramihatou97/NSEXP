"""
System Configuration - Integrated Reference & Synthesis System
Central configuration for smooth operation
"""

from pathlib import Path
from typing import Dict, Any, Optional
import os
from dataclasses import dataclass, field


@dataclass
class SystemConfig:
    """Main configuration for the integrated system"""

    # Database Configuration
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql://localhost/medical_reference_db"
    )

    # File Storage Paths
    textbooks_path: Path = Path(os.getenv("TEXTBOOKS_PATH", "./textbooks"))
    extracted_images_path: Path = Path(os.getenv("IMAGES_PATH", "./extracted_images"))
    temp_path: Path = Path(os.getenv("TEMP_PATH", "./temp"))

    # AI Service Configuration
    claude_api_key: Optional[str] = os.getenv("CLAUDE_API_KEY")
    openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")

    # Search Configuration
    max_search_results: int = 20
    min_relevance_score: float = 0.3
    chunk_size: int = 1000
    chunk_overlap: int = 200

    # Synthesis Configuration
    include_images: bool = True
    include_tables: bool = True
    max_synthesis_sources: int = 15

    # Processing Configuration
    max_file_size_mb: int = 100
    enable_ocr: bool = True
    enable_virus_scan: bool = False  # Set True in production

    # Performance Configuration
    enable_caching: bool = True
    cache_ttl_hours: int = 24
    max_parallel_processes: int = 4

    def validate(self) -> bool:
        """Validate configuration"""
        if not self.textbooks_path.exists():
            self.textbooks_path.mkdir(parents=True, exist_ok=True)

        if not self.extracted_images_path.exists():
            self.extracted_images_path.mkdir(parents=True, exist_ok=True)

        if not self.temp_path.exists():
            self.temp_path.mkdir(parents=True, exist_ok=True)

        if not self.claude_api_key and not self.openai_api_key:
            raise ValueError("At least one AI service API key must be configured")

        return True


@dataclass
class QuickStartConfig:
    """Simplified configuration for quick setup"""

    textbooks_folder: str = "./my_textbooks"
    ai_service: str = "claude"  # or "openai"
    ai_api_key: str = ""

    def to_system_config(self) -> SystemConfig:
        """Convert to full system configuration"""
        config = SystemConfig(
            textbooks_path=Path(self.textbooks_folder)
        )

        if self.ai_service.lower() == "claude":
            config.claude_api_key = self.ai_api_key
        else:
            config.openai_api_key = self.ai_api_key

        return config


class SystemInitializer:
    """Initialize and configure the integrated system"""

    @staticmethod
    async def initialize_system(config: Optional[SystemConfig] = None):
        """
        Initialize the complete integrated system with configuration

        Args:
            config: System configuration (uses defaults if None)

        Returns:
            Configured IntegratedReferenceSystem ready for use
        """
        # Use default config if none provided
        if config is None:
            config = SystemConfig()

        # Validate configuration
        config.validate()

        # Import required components
        from reference_library import ReferenceLibraryService
        from enhanced_synthesizer_service import EnhancedSynthesisEngine
        from hybrid_ai_manager import HybridAIManager
        from reference_search_bridge import IntegratedReferenceSystem

        # Initialize Reference Library Service
        library_service = ReferenceLibraryService()
        library_service.textbooks_root = config.textbooks_path
        library_service.max_file_size_mb = config.max_file_size_mb
        library_service.chunk_size = config.chunk_size

        # Initialize AI Manager
        ai_config = {}
        if config.claude_api_key:
            ai_config['claude_api_key'] = config.claude_api_key
        if config.openai_api_key:
            ai_config['openai_api_key'] = config.openai_api_key

        ai_manager = HybridAIManager(**ai_config)

        # Initialize PDF Extractor (if needed)
        pdf_extractor = None
        if config.enable_ocr:
            # Initialize OCR-capable PDF extractor
            # from pdf_ocr_extractor import PDFOCRExtractor
            # pdf_extractor = PDFOCRExtractor()
            pass

        # Create integrated system
        integrated_system = IntegratedReferenceSystem(
            library_service=library_service,
            ai_manager=ai_manager,
            pdf_extractor=pdf_extractor
        )

        # Configure search bridge settings
        integrated_system.bridge.config.max_results = config.max_search_results
        integrated_system.bridge.config.min_relevance_score = config.min_relevance_score
        integrated_system.bridge.config.include_images = config.include_images
        integrated_system.bridge.config.include_tables = config.include_tables

        return integrated_system

    @staticmethod
    async def quick_start(
        textbooks_folder: str,
        ai_api_key: str,
        ai_service: str = "claude"
    ):
        """
        Quick start with minimal configuration

        Args:
            textbooks_folder: Path to folder containing PDF textbooks
            ai_api_key: API key for AI service
            ai_service: Which AI service to use ("claude" or "openai")

        Returns:
            Ready-to-use system

        Example:
            system = await SystemInitializer.quick_start(
                "./my_books",
                "sk-...",
                "openai"
            )
            chapter = await system.generate_chapter("Brain Tumors")
        """
        quick_config = QuickStartConfig(
            textbooks_folder=textbooks_folder,
            ai_service=ai_service,
            ai_api_key=ai_api_key
        )

        system_config = quick_config.to_system_config()
        return await SystemInitializer.initialize_system(system_config)


# Production configuration presets
class ConfigPresets:
    """Pre-configured settings for different environments"""

    @staticmethod
    def development() -> SystemConfig:
        """Development environment settings"""
        return SystemConfig(
            database_url="postgresql://dev:dev@localhost/medical_dev",
            max_search_results=10,
            enable_virus_scan=False,
            enable_caching=False,
            max_parallel_processes=2
        )

    @staticmethod
    def production() -> SystemConfig:
        """Production environment settings"""
        return SystemConfig(
            database_url=os.getenv("DATABASE_URL"),
            max_search_results=30,
            min_relevance_score=0.5,
            enable_virus_scan=True,
            enable_caching=True,
            cache_ttl_hours=48,
            max_parallel_processes=8
        )

    @staticmethod
    def testing() -> SystemConfig:
        """Testing environment settings"""
        return SystemConfig(
            database_url="postgresql://test:test@localhost/medical_test",
            textbooks_path=Path("./test_data/textbooks"),
            max_search_results=5,
            enable_virus_scan=False,
            enable_caching=False,
            max_parallel_processes=1
        )


# Environment-based auto-configuration
def get_config() -> SystemConfig:
    """Get configuration based on environment"""
    env = os.getenv("ENVIRONMENT", "development").lower()

    if env == "production":
        return ConfigPresets.production()
    elif env == "testing":
        return ConfigPresets.testing()
    else:
        return ConfigPresets.development()


# Validation utilities
def validate_textbook_structure(textbooks_path: Path) -> Dict[str, Any]:
    """
    Validate textbook folder structure

    Expected structure:
    textbooks/
    ├── neurosurgery_handbook/
    │   ├── metadata.json
    │   ├── 01-introduction.pdf
    │   ├── 02-anatomy.pdf
    │   └── ...
    ├── surgical_techniques/
    │   ├── metadata.json
    │   └── ...
    """
    validation_result = {
        "valid": True,
        "textbooks_found": 0,
        "chapters_found": 0,
        "issues": []
    }

    if not textbooks_path.exists():
        validation_result["valid"] = False
        validation_result["issues"].append(f"Path does not exist: {textbooks_path}")
        return validation_result

    # Check each subfolder
    for folder in textbooks_path.iterdir():
        if folder.is_dir():
            validation_result["textbooks_found"] += 1

            # Check for PDFs
            pdfs = list(folder.glob("*.pdf"))
            validation_result["chapters_found"] += len(pdfs)

            if len(pdfs) == 0:
                validation_result["issues"].append(f"No PDFs in {folder.name}")

            # Check for metadata (optional but recommended)
            if not (folder / "metadata.json").exists():
                validation_result["issues"].append(f"No metadata.json in {folder.name}")

    if validation_result["textbooks_found"] == 0:
        validation_result["valid"] = False
        validation_result["issues"].append("No textbook folders found")

    return validation_result