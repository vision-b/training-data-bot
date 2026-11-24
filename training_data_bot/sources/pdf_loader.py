
"""Specialized loader for PDF documents."""

import asyncio
from pathlib import Path
import fitz

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
        """Extract text from every PDF page."""

        pages = []

        with fitz.open(str(path)) as pdf:
            if pdf.is_encrypted:
                raise DocumentLoadError(
                    "Encrypted PDFs are not supported",
                    file_path=str(path),
                )

            if pdf.page_count > self.MAX_PAGES:
                raise DocumentLoadError(
                    "PDF exceeds the maximum page count",
                    file_path=str(path),
                )

            for page_number, page in enumerate(pdf, start=1):
                text = page.get_text()

                if text.strip():
                    pages.append(
                        f"Page {page_number}:\n{text}"
                    )

        return "\n\n".join(pages)
