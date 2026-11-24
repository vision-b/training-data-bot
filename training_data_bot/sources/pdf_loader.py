
"""Specialized loader for PDF documents."""

import asyncio
from pathlib import Path

from pypdf import PdfReader

from training_data_bot.core.models import Document, DocumentType
from training_data_bot.sources.base import BaseLoader
from training_data_bot.sources.exceptions import (
    DocumentLoadError,
    SourceNotFoundError,
)


class PDFLoader(BaseLoader):
    """Extracts text from PDF documents."""

    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB
    MAX_PAGES = 1000

    def __init__(self):
        super().__init__()

        self.supported_formats = [DocumentType.PDF]

    async def load_single(
        self,
        source: str,
        **kwargs
    ) -> Document:

        path = Path(source)

        if not path.exists():
            raise SourceNotFoundError(
                f"PDF does not exist: {path}",
                file_path=str(path),
            )

        if not path.is_file():
            raise DocumentLoadError(
                f"Source is not a file: {path}",
                file_path=str(path),
            )

        if path.suffix.lower() != ".pdf":
            raise DocumentLoadError(
                f"Expected a PDF file: {path}",
                file_path=str(path),
            )

        if path.stat().st_size > self.MAX_FILE_SIZE:
            raise DocumentLoadError(
                "PDF exceeds the maximum allowed size",
                file_path=str(path),
            )

        try:
            content = await asyncio.to_thread(
                self._extract_pdf_text,
                path,
            )

            return Document(
                title=path.stem,
                content=content,
                source=str(path),
                doc_type=DocumentType.PDF,
                word_count=len(content.split()),
                char_count=len(content),
            )

        except DocumentLoadError:
            raise

        except Exception as exc:
            raise DocumentLoadError(
                f"Failed to extract PDF: {path}",
                file_path=str(path),
                cause=exc,
            ) from exc

    def _extract_pdf_text(self, path: Path) -> str:
        """Extract text from all pages of a PDF."""

        reader = PdfReader(str(path))

        if reader.is_encrypted:
            raise DocumentLoadError(
                "Encrypted PDFs are not supported",
                file_path=str(path),
            )

        if len(reader.pages) > self.MAX_PAGES:
            raise DocumentLoadError(
                f"PDF exceeds the maximum of {self.MAX_PAGES} pages",
                file_path=str(path),
            )

        pages = []

        for page in reader.pages:
            text = page.extract_text() or ""

            if text.strip():
                pages.append(text.strip())

        return "\n\n".join(pages)
