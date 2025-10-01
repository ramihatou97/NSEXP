"""
Database Models Package for Neurosurgical Knowledge System

This package contains all SQLAlchemy models for the application.
Import models from this package for cleaner code:

    from models import Chapter, Reference, Citation

Instead of:

    from models.database_simplified import Chapter, Reference, Citation
"""

# Import all models and enums from database_simplified
from models.database_simplified import (
    # Base
    Base,

    # Enums
    NeurosurgicalSpecialty,
    ProcedureType,
    AnatomicalRegion,

    # Association Tables
    chapter_references,
    chapter_procedures,

    # Models
    UserPreferences,
    Textbook,
    BookChapter,
    Chapter,
    SurgicalProcedure,
    Reference,
    Citation,
    QASession,
    SynthesisJob,
    BehavioralPattern,
    KnowledgeGap,
    CitationNetwork,
    MedicalImage,
)

# Define what's available when using "from models import *"
__all__ = [
    # Base
    "Base",

    # Enums
    "NeurosurgicalSpecialty",
    "ProcedureType",
    "AnatomicalRegion",

    # Association Tables
    "chapter_references",
    "chapter_procedures",

    # Models
    "UserPreferences",
    "Textbook",
    "BookChapter",
    "Chapter",
    "SurgicalProcedure",
    "Reference",
    "Citation",
    "QASession",
    "SynthesisJob",
    "BehavioralPattern",
    "KnowledgeGap",
    "CitationNetwork",
    "MedicalImage",
]
