
"""Public interface for the document loading package."""

from training_data_bot.sources.base import BaseLoader
from training_data_bot.sources.document_loader import DocumentLoader
from training_data_bot.sources.pdf_loader import PDFLoader
from training_data_bot.sources.web_loader import WebLoader
from training_data_bot.sources.unified import UnifiedLoader

from training_data_bot.sources.exceptions import (
    DocumentLoadError,
    SourceNotFoundError,
    UnsupportedDocumentTypeError,
    InvalidSourceError,
)

__all__ = [
    "BaseLoader",
    "DocumentLoader",
    "PDFLoader",
    "WebLoader",
    "UnifiedLoader",
    "DocumentLoadError",
    "SourceNotFoundError",
    "UnsupportedDocumentTypeError",
    "InvalidSourceError",
]
