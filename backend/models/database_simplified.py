"""
Simplified Database Models for Single-User Neurosurgical Knowledge System
All neurosurgical functionality retained, multi-user complexity removed
"""

from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, Text, JSON,
    ForeignKey, Table, Index, Enum
)
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSONB, TSVECTOR
from datetime import datetime
import uuid
import enum

Base = declarative_base()


# Neurosurgical Enums (KEPT - Core functionality)
class NeurosurgicalSpecialty(enum.Enum):
    TUMOR = "tumor"
    VASCULAR = "vascular"
    SPINE = "spine"
    FUNCTIONAL = "functional"
    PEDIATRIC = "pediatric"
    TRAUMA = "trauma"
    PERIPHERAL_NERVE = "peripheral_nerve"
    SKULL_BASE = "skull_base"
    ENDOSCOPIC = "endoscopic"
    STEREOTACTIC = "stereotactic"


class ProcedureType(enum.Enum):
    CRANIOTOMY = "craniotomy"
    CRANIECTOMY = "craniectomy"
    LAMINECTOMY = "laminectomy"
    FUSION = "fusion"
    SHUNT = "shunt"
    ENDOSCOPY = "endoscopy"
    STEREOTACTIC_BIOPSY = "stereotactic_biopsy"
    RADIOSURGERY = "radiosurgery"
    ANEURYSM_CLIPPING = "aneurysm_clipping"
    EMBOLIZATION = "embolization"
    MICRODISCECTOMY = "microdiscectomy"
    DEEP_BRAIN_STIMULATION = "deep_brain_stimulation"


class AnatomicalRegion(enum.Enum):
    FRONTAL = "frontal"
    PARIETAL = "parietal"
    TEMPORAL = "temporal"
    OCCIPITAL = "occipital"
    CEREBELLUM = "cerebellum"
    BRAINSTEM = "brainstem"
    PITUITARY = "pituitary"
    PINEAL = "pineal"
    VENTRICLES = "ventricles"
    CERVICAL_SPINE = "cervical_spine"
    THORACIC_SPINE = "thoracic_spine"
    LUMBAR_SPINE = "lumbar_spine"
    SACRAL = "sacral"


# Association tables (KEPT - Core functionality)
chapter_references = Table(
    'chapter_references',
    Base.metadata,
    Column('chapter_id', UUID(as_uuid=True), ForeignKey('chapters.id')),
    Column('reference_id', UUID(as_uuid=True), ForeignKey('references.id'))
)

chapter_procedures = Table(
    'chapter_procedures',
    Base.metadata,
    Column('chapter_id', UUID(as_uuid=True), ForeignKey('chapters.id')),
    Column('procedure_id', UUID(as_uuid=True), ForeignKey('surgical_procedures.id'))
)


class UserPreferences(Base):
    """Single user preferences and settings (SIMPLIFIED)"""
    __tablename__ = 'user_preferences'

    id = Column(Integer, primary_key=True)

    # Learning preferences
    learning_preferences = Column(JSONB, default={})
    preferred_complexity = Column(String(20), default="intermediate")

    # Display preferences
    theme = Column(String(20), default="light")
    font_size = Column(String(20), default="medium")

    # Feature preferences
    auto_synthesis = Column(Boolean, default=True)
    behavioral_learning_enabled = Column(Boolean, default=True)

    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Textbook(Base):
    """Medical textbooks (KEPT - Core functionality)"""
    __tablename__ = 'textbooks'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(500), nullable=False)
    authors = Column(ARRAY(String))
    isbn = Column(String(20))
    edition = Column(String(50))
    publisher = Column(String(255))
    publication_year = Column(Integer)

    # Neurosurgical categorization
    specialty = Column(Enum(NeurosurgicalSpecialty))
    is_reference_standard = Column(Boolean, default=False)

    # File information
    file_path = Column(String(500))
    file_size_mb = Column(Float)
    total_pages = Column(Integer)

    # Processing status
    is_processed = Column(Boolean, default=False)
    processing_completed_at = Column(DateTime)
    processing_error = Column(Text)

    # Content metrics
    chapters_extracted = Column(Integer)
    medical_terms_count = Column(Integer)

    created_at = Column(DateTime, default=datetime.utcnow)
    search_vector = Column(TSVECTOR)

    # Relationships
    book_chapters = relationship("BookChapter", back_populates="textbook")

    __table_args__ = (
        Index('idx_textbook_specialty', 'specialty'),
        Index('idx_textbook_search', 'search_vector', postgresql_using='gin'),
    )


class BookChapter(Base):
    """Book chapters (KEPT - Core functionality)"""
    __tablename__ = 'book_chapters'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    textbook_id = Column(UUID(as_uuid=True), ForeignKey('textbooks.id'))
    chapter_number = Column(Integer)
    title = Column(String(500))

    content_text = Column(Text)
    page_start = Column(Integer)
    page_end = Column(Integer)

    # Medical content
    medical_terms = Column(ARRAY(String))
    anatomical_regions = Column(ARRAY(String))
    procedures_discussed = Column(ARRAY(String))

    # Embeddings for search
    embedding = Column(ARRAY(Float))

    textbook = relationship("Textbook", back_populates="book_chapters")


class Chapter(Base):
    """Synthesized chapters (SIMPLIFIED - No user_id)"""
    __tablename__ = 'chapters'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(500), nullable=False)
    topic = Column(String(500), nullable=False)

    # Neurosurgical categorization
    specialty = Column(Enum(NeurosurgicalSpecialty), nullable=False)
    anatomical_focus = Column(ARRAY(String))
    procedure_focus = Column(ARRAY(String))

    # Content
    content = Column(JSONB, nullable=False)
    surgical_anatomy = Column(Text)
    surgical_technique = Column(Text)
    complications_avoidance = Column(Text)

    # Medical codes
    icd10_codes = Column(ARRAY(String))
    cpt_codes = Column(ARRAY(String))

    # Version control
    version = Column(Integer, default=1)
    parent_chapter_id = Column(UUID(as_uuid=True), ForeignKey('chapters.id'))

    # Quality metrics
    completeness_score = Column(Float)
    medical_accuracy_score = Column(Float)
    evidence_level = Column(String(10))

    # AI Enhancement
    ai_enhanced = Column(Boolean, default=False)
    knowledge_gaps = Column(JSONB)

    # Status
    status = Column(String(20), default='draft')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    search_vector = Column(TSVECTOR)

    # Relationships
    references = relationship("Reference", secondary=chapter_references)
    procedures = relationship("SurgicalProcedure", secondary=chapter_procedures)
    qa_sessions = relationship("QASession", back_populates="chapter")

    __table_args__ = (
        Index('idx_chapter_specialty', 'specialty'),
        Index('idx_chapter_status', 'status'),
        Index('idx_chapter_created_at', 'created_at'),
        Index('idx_chapter_updated_at', 'updated_at'),
        Index('idx_chapter_evidence_level', 'evidence_level'),
        Index('idx_chapter_search', 'search_vector', postgresql_using='gin'),
    )


class SurgicalProcedure(Base):
    """Surgical procedures (KEPT - Core functionality)"""
    __tablename__ = 'surgical_procedures'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    procedure_type = Column(Enum(ProcedureType))
    cpt_code = Column(String(20))

    anatomical_region = Column(Enum(AnatomicalRegion))
    approach = Column(String(255))

    # Procedure details
    average_duration_minutes = Column(Integer)
    positioning = Column(String(100))
    required_equipment = Column(ARRAY(String))

    # Steps and complications
    procedure_steps = Column(JSONB)
    common_complications = Column(ARRAY(String))

    created_at = Column(DateTime, default=datetime.utcnow)

    chapters = relationship("Chapter", secondary=chapter_procedures)


class Reference(Base):
    """References (KEPT - Core functionality)"""
    __tablename__ = 'references'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    title = Column(String(500), nullable=False)
    authors = Column(ARRAY(String))
    journal = Column(String(255))
    year = Column(Integer)

    # Identifiers
    doi = Column(String(255), unique=True)
    pmid = Column(String(20), unique=True)

    # Content
    abstract = Column(Text)
    key_findings = Column(JSONB)
    evidence_level = Column(String(10))

    created_at = Column(DateTime, default=datetime.utcnow)

    chapters = relationship("Chapter", secondary=chapter_references)


class Citation(Base):
    """Citation linking chapters to references"""
    __tablename__ = 'citations'

    id = Column(Integer, primary_key=True)
    chapter_id = Column(Integer, ForeignKey('chapters.id'))
    reference_id = Column(Integer, ForeignKey('references.id'))

    context = Column(Text)
    location = Column(String(100))

    created_at = Column(DateTime, default=datetime.utcnow)


class QASession(Base):
    """Q&A sessions (SIMPLIFIED - No user_id)"""
    __tablename__ = 'qa_sessions'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chapter_id = Column(UUID(as_uuid=True), ForeignKey('chapters.id'))

    question = Column(Text, nullable=False)
    question_context = Column(Text)
    question_type = Column(String(50))

    answer = Column(Text)
    answer_sources = Column(JSONB)
    confidence_score = Column(Float)

    integrated_into_chapter = Column(Boolean, default=False)

    asked_at = Column(DateTime, default=datetime.utcnow)

    chapter = relationship("Chapter", back_populates="qa_sessions")


class SynthesisJob(Base):
    """Synthesis jobs (SIMPLIFIED - No user_id)"""
    __tablename__ = 'synthesis_jobs'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chapter_id = Column(UUID(as_uuid=True), ForeignKey('chapters.id'))

    topic = Column(String(500), nullable=False)
    specialty = Column(Enum(NeurosurgicalSpecialty))
    synthesis_config = Column(JSONB)

    # Status
    status = Column(String(20), default='pending')
    progress_percentage = Column(Integer, default=0)
    current_step = Column(String(100))

    # Results
    result_data = Column(JSONB)
    error_message = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)


class BehavioralPattern(Base):
    """Behavioral learning patterns (SIMPLIFIED - Single user)"""
    __tablename__ = 'behavioral_patterns'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    pattern_type = Column(String(50))  # search, read, synthesis, qa
    pattern_data = Column(JSONB)
    frequency = Column(Integer, default=1)

    last_occurrence = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)


class KnowledgeGap(Base):
    """Identified knowledge gaps (KEPT - Core functionality)"""
    __tablename__ = 'knowledge_gaps'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chapter_id = Column(UUID(as_uuid=True), ForeignKey('chapters.id'))

    gap_type = Column(String(50))
    description = Column(Text)
    confidence = Column(Float)

    auto_filled = Column(Boolean, default=False)
    filled_at = Column(DateTime)

    created_at = Column(DateTime, default=datetime.utcnow)


class CitationNetwork(Base):
    """Citation relationships (KEPT - Core functionality)"""
    __tablename__ = 'citation_networks'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_chapter_id = Column(UUID(as_uuid=True), ForeignKey('chapters.id'))
    target_chapter_id = Column(UUID(as_uuid=True), ForeignKey('chapters.id'))

    citation_type = Column(String(50))
    citation_strength = Column(Float)

    created_at = Column(DateTime, default=datetime.utcnow)


class MedicalImage(Base):
    """Medical images (KEPT - Core functionality)"""
    __tablename__ = 'medical_images'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chapter_id = Column(UUID(as_uuid=True), ForeignKey('chapters.id'))

    filename = Column(String(255))
    file_path = Column(String(500))

    image_type = Column(String(50))  # MRI, CT, illustration
    anatomical_region = Column(Enum(AnatomicalRegion))

    caption = Column(Text)
    key_findings = Column(ARRAY(String))

    created_at = Column(DateTime, default=datetime.utcnow)