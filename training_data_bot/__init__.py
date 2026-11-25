
"""Training Data Curation Bot public package interface."""

__version__ = "0.1.0"
__author__ = "Training Data Bot Team"

from .bot import TrainingDataBot

from .ai import AIClient, BaseAIProvider, MockAIProvider

from .core.models import (
    Dataset,
    Document,
    DocumentType,
    ExportFormat,
    QualityReport,
    TaskResult,
    TaskTemplate,
    TaskType,
    TextChunk,
    TrainingExample,
)

from .evaluation import QualityEvaluator
from .preprocessing import TextPreprocessor

from .sources import (
    BaseLoader,
    DocumentLoader,
    PDFLoader,
    UnifiedLoader,
    WebLoader,
)

from .storage import DatabaseManager, DatasetExporter

from .tasks import (
    ClassificationGenerator,
    QAGenerator,
    SummarizationGenerator,
    TaskManager,
)

__all__ = [
    "TrainingDataBot",
    "AIClient",
    "BaseAIProvider",
    "MockAIProvider",
    "Dataset",
    "Document",
    "DocumentType",
    "ExportFormat",
    "QualityReport",
    "TaskResult",
    "TaskTemplate",
    "TaskType",
    "TextChunk",
    "TrainingExample",
    "QualityEvaluator",
    "TextPreprocessor",
    "BaseLoader",
    "DocumentLoader",
    "PDFLoader",
    "UnifiedLoader",
    "WebLoader",
    "DatabaseManager",
    "DatasetExporter",
    "ClassificationGenerator",
    "QAGenerator",
    "SummarizationGenerator",
    "TaskManager",
]
