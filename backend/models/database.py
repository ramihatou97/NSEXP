"""
Database Models for Neurosurgical Knowledge Management System
Specialized for neurosurgical content, procedures, and medical data
"""

from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, Text, JSON,
    ForeignKey, Table, Index, UniqueConstraint, CheckConstraint, Enum
)
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSONB, TSVECTOR
from datetime import datetime
import uuid
import enum

Base = declarative_base()


# Enums for neurosurgery-specific categorization
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


# Association tables for many-to-many relationships
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

chapter_anatomical_regions = Table(
    'chapter_anatomical_regions',
    Base.metadata,
    Column('chapter_id', UUID(as_uuid=True), ForeignKey('chapters.id')),
    Column('region', Enum(AnatomicalRegion))
)


class User(Base):
    __tablename__ = 'users'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False)
    username = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))

    # Neurosurgical profile
    specialty = Column(Enum(NeurosurgicalSpecialty))
    years_experience = Column(Integer)
    hospital = Column(String(255))
    residency_program = Column(String(255))
    board_certified = Column(Boolean, default=False)

    # System fields
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Learning preferences (for behavioral AI)
    learning_preferences = Column(JSONB, default={})
    preferred_complexity = Column(String(20), default="intermediate")  # basic, intermediate, advanced

    # Relationships
    chapters = relationship("Chapter", back_populates="author")
    interactions = relationship("UserInteraction", back_populates="user")
    qa_sessions = relationship("QASession", back_populates="user")

    __table_args__ = (
        Index('idx_user_email', 'email'),
        Index('idx_user_specialty', 'specialty'),
    )


class Textbook(Base):
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
    is_reference_standard = Column(Boolean, default=False)  # Gold standard texts

    # File information
    file_path = Column(String(500))
    file_size_mb = Column(Float)
    total_pages = Column(Integer)

    # Processing status
    is_processed = Column(Boolean, default=False)
    processing_started_at = Column(DateTime)
    processing_completed_at = Column(DateTime)
    processing_error = Column(Text)

    # Content analysis
    extracted_chapters = Column(Integer)
    medical_terms_count = Column(Integer)
    figures_count = Column(Integer)
    tables_count = Column(Integer)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Full-text search
    search_vector = Column(TSVECTOR)

    # Relationships
    book_chapters = relationship("BookChapter", back_populates="textbook")

    __table_args__ = (
        Index('idx_textbook_specialty', 'specialty'),
        Index('idx_textbook_search', 'search_vector', postgresql_using='gin'),
    )


class BookChapter(Base):
    __tablename__ = 'book_chapters'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    textbook_id = Column(UUID(as_uuid=True), ForeignKey('textbooks.id'))
    chapter_number = Column(Integer)
    title = Column(String(500))

    # Content
    content_text = Column(Text)
    content_summary = Column(Text)

    # Neurosurgical classification
    anatomical_regions = Column(ARRAY(String))
    procedures_discussed = Column(ARRAY(String))
    pathologies_covered = Column(ARRAY(String))

    # Extraction metadata
    page_start = Column(Integer)
    page_end = Column(Integer)
    word_count = Column(Integer)

    # Medical content analysis
    medical_terms = Column(ARRAY(String))
    drug_mentions = Column(ARRAY(String))
    surgical_instruments = Column(ARRAY(String))
    imaging_modalities = Column(ARRAY(String))  # MRI, CT, angiography, etc.

    # Quality metrics
    completeness_score = Column(Float)
    extraction_confidence = Column(Float)

    # Embeddings for similarity search
    embedding = Column(ARRAY(Float))  # Vector embedding

    # Relationships
    textbook = relationship("Textbook", back_populates="book_chapters")

    __table_args__ = (
        Index('idx_book_chapter_textbook', 'textbook_id'),
        Index('idx_book_chapter_regions', 'anatomical_regions', postgresql_using='gin'),
    )


class Chapter(Base):
    __tablename__ = 'chapters'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(500), nullable=False)
    topic = Column(String(500), nullable=False)

    # Author
    author_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))

    # Neurosurgical categorization
    specialty = Column(Enum(NeurosurgicalSpecialty), nullable=False)
    anatomical_focus = Column(ARRAY(String))
    procedure_focus = Column(ARRAY(String))
    complexity_level = Column(String(20))  # resident, fellow, attending

    # Content structure (neurosurgery-specific sections)
    content = Column(JSONB, nullable=False)  # Structured content with all sections

    # Neurosurgery-specific sections
    surgical_anatomy = Column(Text)
    surgical_approaches = Column(Text)
    surgical_technique = Column(Text)
    intraoperative_monitoring = Column(Text)
    surgical_pearls = Column(Text)
    complications_avoidance = Column(Text)
    case_illustrations = Column(JSONB)  # Case examples with images

    # Medical content
    icd10_codes = Column(ARRAY(String))
    cpt_codes = Column(ARRAY(String))  # Procedure codes
    relevant_trials = Column(JSONB)  # Clinical trials data

    # Version control
    version = Column(Integer, default=1)
    parent_chapter_id = Column(UUID(as_uuid=True), ForeignKey('chapters.id'))

    # Quality and completeness
    completeness_score = Column(Float)
    medical_accuracy_score = Column(Float)
    evidence_level = Column(String(10))  # I, II, III, IV, V
    last_reviewed_at = Column(DateTime)
    reviewer_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))

    # AI Enhancement metadata
    ai_enhanced = Column(Boolean, default=False)
    knowledge_gaps = Column(JSONB)
    behavioral_insights = Column(JSONB)

    # Status
    status = Column(String(20), default='draft')  # draft, review, published
    is_published = Column(Boolean, default=False)
    published_at = Column(DateTime)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Full-text search
    search_vector = Column(TSVECTOR)

    # Relationships
    author = relationship("User", back_populates="chapters", foreign_keys=[author_id])
    references = relationship("Reference", secondary=chapter_references, back_populates="chapters")
    procedures = relationship("SurgicalProcedure", secondary=chapter_procedures, back_populates="chapters")
    qa_sessions = relationship("QASession", back_populates="chapter")
    synthesis_jobs = relationship("SynthesisJob", back_populates="chapter")

    __table_args__ = (
        Index('idx_chapter_specialty', 'specialty'),
        Index('idx_chapter_status', 'status'),
        Index('idx_chapter_search', 'search_vector', postgresql_using='gin'),
    )


class SurgicalProcedure(Base):
    """Detailed surgical procedure information specific to neurosurgery"""
    __tablename__ = 'surgical_procedures'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    procedure_type = Column(Enum(ProcedureType))
    cpt_code = Column(String(20))

    # Anatomical details
    anatomical_region = Column(Enum(AnatomicalRegion))
    approach = Column(String(255))  # anterior, posterior, lateral, etc.

    # Procedure details
    average_duration_minutes = Column(Integer)
    positioning = Column(String(100))  # prone, supine, lateral, sitting

    # Equipment and tools
    required_equipment = Column(ARRAY(String))
    neuronavigation_required = Column(Boolean, default=False)
    microscope_required = Column(Boolean, default=False)
    endoscope_required = Column(Boolean, default=False)
    neuromonitoring_type = Column(ARRAY(String))  # MEP, SSEP, EMG, etc.

    # Steps
    procedure_steps = Column(JSONB)  # Detailed step-by-step guide
    key_anatomical_landmarks = Column(ARRAY(String))

    # Risks and complications
    common_complications = Column(ARRAY(String))
    complication_rates = Column(JSONB)

    # Outcomes
    success_rate = Column(Float)
    typical_recovery_days = Column(Integer)

    # References and evidence
    evidence_level = Column(String(10))
    key_references = Column(JSONB)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    chapters = relationship("Chapter", secondary=chapter_procedures, back_populates="procedures")

    __table_args__ = (
        Index('idx_procedure_type', 'procedure_type'),
        Index('idx_procedure_region', 'anatomical_region'),
        UniqueConstraint('cpt_code', name='unique_cpt_code'),
    )


class Reference(Base):
    __tablename__ = 'references'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Citation information
    title = Column(String(500), nullable=False)
    authors = Column(ARRAY(String))
    journal = Column(String(255))
    year = Column(Integer)
    volume = Column(String(20))
    issue = Column(String(20))
    pages = Column(String(50))

    # Identifiers
    doi = Column(String(255), unique=True)
    pmid = Column(String(20), unique=True)
    pmc_id = Column(String(20))

    # Neurosurgery-specific classification
    study_type = Column(String(50))  # RCT, cohort, case series, review, etc.
    evidence_level = Column(String(10))
    specialty_focus = Column(Enum(NeurosurgicalSpecialty))

    # Content
    abstract = Column(Text)
    key_findings = Column(JSONB)

    # Quality metrics
    impact_factor = Column(Float)
    citation_count = Column(Integer)
    h_index = Column(Integer)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    chapters = relationship("Chapter", secondary=chapter_references, back_populates="references")

    __table_args__ = (
        Index('idx_reference_year', 'year'),
        Index('idx_reference_specialty', 'specialty_focus'),
    )


class QASession(Base):
    """Question-Answer sessions within chapters"""
    __tablename__ = 'qa_sessions'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    chapter_id = Column(UUID(as_uuid=True), ForeignKey('chapters.id'))

    # Question details
    question = Column(Text, nullable=False)
    question_context = Column(Text)  # Section of chapter where question was asked
    question_type = Column(String(50))  # definition, explanation, clinical, etc.

    # Medical context
    anatomical_context = Column(ARRAY(String))
    procedure_context = Column(String)
    urgency_level = Column(Integer)  # 1-5 scale

    # Answer details
    answer = Column(Text)
    answer_sources = Column(JSONB)  # Sources used for answer
    confidence_score = Column(Float)
    medical_accuracy_verified = Column(Boolean, default=False)

    # Integration status
    integrated_into_chapter = Column(Boolean, default=False)
    integration_point = Column(Text)
    integration_type = Column(String(50))

    # Timestamps
    asked_at = Column(DateTime, default=datetime.utcnow)
    answered_at = Column(DateTime)

    # Relationships
    user = relationship("User", back_populates="qa_sessions")
    chapter = relationship("Chapter", back_populates="qa_sessions")

    __table_args__ = (
        Index('idx_qa_user', 'user_id'),
        Index('idx_qa_chapter', 'chapter_id'),
        Index('idx_qa_timestamp', 'asked_at'),
    )


class UserInteraction(Base):
    """Track user interactions for behavioral learning"""
    __tablename__ = 'user_interactions'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    chapter_id = Column(UUID(as_uuid=True), ForeignKey('chapters.id'))
    session_id = Column(String(100))

    # Interaction details
    interaction_type = Column(String(50))  # read, edit, search, question, etc.
    interaction_data = Column(JSONB)

    # Context
    section_context = Column(Text)
    scroll_depth = Column(Float)
    duration_seconds = Column(Float)

    # Learning metrics
    focus_areas = Column(ARRAY(String))
    concepts_viewed = Column(ARRAY(String))

    # Timestamp
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="interactions")

    __table_args__ = (
        Index('idx_interaction_user', 'user_id'),
        Index('idx_interaction_session', 'session_id'),
        Index('idx_interaction_timestamp', 'timestamp'),
    )


class SynthesisJob(Base):
    """Track chapter synthesis jobs"""
    __tablename__ = 'synthesis_jobs'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chapter_id = Column(UUID(as_uuid=True), ForeignKey('chapters.id'))
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))

    # Job configuration
    topic = Column(String(500), nullable=False)
    specialty = Column(Enum(NeurosurgicalSpecialty))
    synthesis_config = Column(JSONB)

    # Sources
    source_chapters = Column(ARRAY(UUID(as_uuid=True)))
    external_sources = Column(JSONB)

    # Status
    status = Column(String(20), default='pending')  # pending, processing, completed, failed
    progress_percentage = Column(Integer, default=0)
    current_step = Column(String(100))

    # Results
    result_data = Column(JSONB)
    error_message = Column(Text)

    # Metrics
    sources_processed = Column(Integer)
    sections_generated = Column(Integer)
    knowledge_gaps_identified = Column(Integer)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)

    # Relationships
    chapter = relationship("Chapter", back_populates="synthesis_jobs")

    __table_args__ = (
        Index('idx_synthesis_status', 'status'),
        Index('idx_synthesis_user', 'user_id'),
    )


class CitationNetwork(Base):
    """Track citation relationships between chapters and references"""
    __tablename__ = 'citation_networks'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_chapter_id = Column(UUID(as_uuid=True), ForeignKey('chapters.id'))
    target_chapter_id = Column(UUID(as_uuid=True), ForeignKey('chapters.id'))

    # Citation details
    citation_type = Column(String(50))  # explicit, implicit, semantic
    citation_strength = Column(Float)
    citation_context = Column(Text)

    # Medical relevance
    shared_anatomical_regions = Column(ARRAY(String))
    shared_procedures = Column(ARRAY(String))
    shared_pathologies = Column(ARRAY(String))

    # Metadata
    auto_detected = Column(Boolean, default=False)
    verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index('idx_citation_source', 'source_chapter_id'),
        Index('idx_citation_target', 'target_chapter_id'),
        UniqueConstraint('source_chapter_id', 'target_chapter_id', name='unique_citation_pair'),
    )


class MedicalImage(Base):
    """Store medical images, diagrams, and surgical illustrations"""
    __tablename__ = 'medical_images'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chapter_id = Column(UUID(as_uuid=True), ForeignKey('chapters.id'))

    # Image metadata
    filename = Column(String(255))
    file_path = Column(String(500))
    file_size_kb = Column(Integer)
    mime_type = Column(String(50))

    # Medical classification
    image_type = Column(String(50))  # MRI, CT, angiography, illustration, photograph
    anatomical_region = Column(Enum(AnatomicalRegion))
    pathology_shown = Column(String(255))

    # Image details
    caption = Column(Text)
    description = Column(Text)
    modality_details = Column(JSONB)  # T1, T2, FLAIR, contrast, etc.

    # Clinical relevance
    key_findings = Column(ARRAY(String))
    annotations = Column(JSONB)  # Marked regions, arrows, labels

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index('idx_image_chapter', 'chapter_id'),
        Index('idx_image_type', 'image_type'),
    )