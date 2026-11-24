
"""Unified document loading system."""

import logging
from pathlib import Path
from typing import List

from training_data_bot.core.models import Document, DocumentType
from training_data_bot.sources.base import BaseLoader
from training_data_bot.sources.document_loader import DocumentLoader
from training_data_bot.sources.pdf_loader import PDFLoader
from training_data_bot.sources.web_loader import WebLoader
from training_data_bot.sources.exceptions import (
    DocumentLoadError,
    SourceNotFoundError,
    UnsupportedDocumentTypeError,
)


class UnifiedLoader(BaseLoader):
    """
    Central dispatcher for all supported document types.

    Automatically detects sources and routes them
    to the appropriate specialized loader.
    """

    def __init__(self):
        super().__init__()

        self.document_loader = DocumentLoader()
        self.pdf_loader = PDFLoader()
        self.web_loader = WebLoader()

        self.supported_formats = list(DocumentType)

        self._loader_mapping = {
            DocumentType.TXT: self.document_loader,
            DocumentType.MD: self.document_loader,
            DocumentType.HTML: self.document_loader,
            DocumentType.JSON: self.document_loader,
            DocumentType.CSV: self.document_loader,
            DocumentType.DOCX: self.document_loader,
            DocumentType.PDF: self.pdf_loader,
            DocumentType.URL: self.web_loader,
        }

    def validate_source(self, source: str) -> bool:
        """
        Check whether a source exists and has a supported format.
        """

        if not isinstance(source, str) or not source.strip():
            return False

        if source.startswith(("http://", "https://")):
            return True

        path = Path(source)

        if not path.exists() or not path.is_file():
            return False

        suffix = path.suffix.lower().lstrip(".")

        try:
            doc_type = DocumentType(suffix)
        except ValueError:
            return False

        return doc_type in self._loader_mapping

    def _select_loader(self, source: str) -> BaseLoader:
        """
        Identify the source type and return its specialist loader.
        """

        if source.startswith(("http://", "https://")):
            return self.web_loader

        path = Path(source)

        if not path.exists():
            raise SourceNotFoundError(
                f"Source does not exist: {source}",
                file_path=source,
            )

        if not path.is_file():
            raise DocumentLoadError(
                f"Source is not a file: {source}",
                file_path=source,
            )

        suffix = path.suffix.lower().lstrip(".")

        try:
            doc_type = DocumentType(suffix)
        except ValueError as exc:
            raise UnsupportedDocumentTypeError(
                f"Unsupported document format: {suffix}",
                file_path=source,
                cause=exc,
            ) from exc

        loader = self._loader_mapping.get(doc_type)

        if loader is None:
            raise UnsupportedDocumentTypeError(
                f"No loader registered for: {doc_type.value}",
                file_path=source,
            )

        return loader

    async def load_single(
        self,
        source: str,
        **kwargs
    ) -> Document:
        """
        Load one document using automatic loader selection.
        """

        if not isinstance(source, str) or not source.strip():
            raise DocumentLoadError("Source must be a non-empty string")

        try:
            loader = self._select_loader(source)

            self.logger.info(
                "Routing %s to %s",
                source,
                loader.__class__.__name__,
            )

            return await loader.load_single(source, **kwargs)

        except DocumentLoadError:
            raise

        except Exception as exc:
            raise DocumentLoadError(
                f"Failed to load source: {source}",
                file_path=source,
                cause=exc,
            ) from exc

    def _find_supported_files(
        self,
        directory: Path,
        recursive: bool = True,
    ) -> List[str]:
        """
        Discover supported files inside a directory.
        """

        iterator = directory.rglob("*") if recursive else directory.iterdir()

        supported_files = []

        for path in iterator:
            if not path.is_file():
                continue

            suffix = path.suffix.lower().lstrip(".")

            try:
                doc_type = DocumentType(suffix)
            except ValueError:
                continue

            if doc_type in self._loader_mapping and doc_type != DocumentType.URL:
                supported_files.append(str(path))

        return sorted(supported_files)

    async def load_directory(
        self,
        directory: str,
        recursive: bool = True,
        max_workers: int = 4,
    ) -> List[Document]:
        """
        Load all supported documents from a directory.

        Unsupported files are ignored.
        Failed documents are logged and skipped.
        """

        path = Path(directory)

        if not path.exists():
            raise SourceNotFoundError(
                f"Directory does not exist: {directory}",
                file_path=directory,
            )

        if not path.is_dir():
            raise DocumentLoadError(
                f"Source is not a directory: {directory}",
                file_path=directory,
            )

        sources = self._find_supported_files(
            path,
            recursive=recursive,
        )

        self.logger.info(
            "Discovered %d supported files in %s",
            len(sources),
            directory,
        )

        return await self.load_multiple(
            sources,
            max_workers=max_workers,
        )
