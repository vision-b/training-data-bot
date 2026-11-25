"""Training Data Curation Bot public package interface."""

__version__ = "0.1.0"
__author__ = "Training Data Bot Team"

from training_data_bot.bot import TrainingDataBot
from training_data_bot.ai import AIClient, BaseAIProvider, MockAIProvider
from training_data_bot.core.models import (
    Dataset, Document, DocumentType, ExportFormat, QualityReport,
    TaskResult, TaskTemplate, TaskType, TextChunk, TrainingExample,
)
from training_data_bot.evaluation import QualityEvaluator
from training_data_bot.preprocessing import TextPreprocessor
from training_data_bot.sources import (
    BaseLoader, DocumentLoader, PDFLoader, UnifiedLoader, WebLoader,
)
from training_data_bot.storage import DatabaseManager, DatasetExporter
from training_data_bot.tasks import (
    ClassificationGenerator, QAGenerator, SummarizationGenerator, TaskManager,
)

__all__ = [
    "TrainingDataBot", "AIClient", "BaseAIProvider", "MockAIProvider",
    "Dataset", "Document", "DocumentType", "ExportFormat", "QualityReport",
    "TaskResult", "TaskTemplate", "TaskType", "TextChunk", "TrainingExample",
    "QualityEvaluator", "TextPreprocessor", "BaseLoader", "DocumentLoader",
    "PDFLoader", "UnifiedLoader", "WebLoader", "DatabaseManager",
    "DatasetExporter", "ClassificationGenerator", "QAGenerator",
    "SummarizationGenerator", "TaskManager",
]
