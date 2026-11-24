
"""
Core data models for the Training Data Curation Bot.

These models define the structure of the data that moves
through the application.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


# ============================================================
# 1. BASE ENTITY
# ============================================================

class BaseEntity(BaseModel):
    """Shared fields inherited by the other data models."""

    id: UUID = Field(default_factory=uuid4) # defining a unique random identifier 

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    updated_at: Optional[datetime] = None

    metadata: Dict[str, Any] = Field(default_factory=dict)


# ============================================================
# 2. ENUMS
# ============================================================

class DocumentType(str, Enum):
    PDF = "pdf"
    DOCX = "docx"
    TXT = "txt"
    MD = "md"
    HTML = "html"
    JSON = "json"
    CSV = "csv"
    URL = "url"


class TaskType(str, Enum):
    QA_GENERATION = "qa_generation"
    CLASSIFICATION = "classification"
    SUMMARIZATION = "summarization"
    NER = "named_entity_recognition"
    RED_TEAMING = "red_teaming"
    INSTRUCTION_RESPONSE = "instruction_response"


class QualityMetric(str, Enum):
    TOXICITY = "toxicity"
    BIAS = "bias"
    DIVERSITY = "diversity"
    COHERENCE = "coherence"
    RELEVANCE = "relevance"


class ProcessingStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


# ============================================================
# 3. DOCUMENT MODELS
# ============================================================

class Document(BaseEntity):
    """Represents an original source document."""

    title: str
    content: str
    source: str
    doc_type: DocumentType
    word_count: int
    char_count: int


class TextChunk(BaseEntity):
    """Represents a smaller piece of a document."""

    document_id: UUID
    content: str
    start_index: int
    end_index: int
    chunk_index: int
    token_count: int


# ============================================================
# 4. TASK MODELS
# ============================================================

class TaskTemplate(BaseEntity):
    """Defines instructions for a particular generation task."""

    name: str
    task_type: TaskType
    description: str
    prompt_template: str
    parameters: Dict[str, Any]


class TaskResult(BaseEntity):
    """Stores the result of processing a text chunk."""

    task_id: UUID
    input_chunk_id: UUID
    output: str
    confidence: float
    quality_scores: Dict[str, Any]
    processing_time: float


# ============================================================
# 5. TRAINING DATA MODELS
# ============================================================

class TrainingExample(BaseEntity):
    """Represents one input-output training example."""

    input_text: str
    output_text: str
    task_type: TaskType
    source_document_id: UUID
    quality_scores: Dict[str, Any]

    # The tutorial's data-journey example uses this field,
    # although its earlier class definition omits it.
    source_chunk_id: Optional[UUID] = None


class Dataset(BaseEntity):
    """Represents a collection of training examples."""

    name: str
    description: str
    examples: List[TrainingExample]
    total_examples: int
    train_split: float
    validation_split: float
    test_split: float


# ============================================================
# 6. QUALITY MODEL
# ============================================================

class QualityReport(BaseEntity):
    """Stores the quality assessment of a target object."""

    target_id: UUID
    overall_score: float
    passed: bool
    metric_scores: Dict[str, Any]
    issues: List[str]
    warnings: List[str]


# ============================================================
# 7. PROCESSING MODEL
# ============================================================

class ProcessingJob(BaseEntity):
    """Tracks a processing operation."""

    name: str
    job_type: str
    status: ProcessingStatus
    total_items: int
    processed_items: int
    started_at: datetime
    estimated_completion: datetime
