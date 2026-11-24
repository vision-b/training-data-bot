
"""Loader for text-based and structured documents."""

import asyncio
import csv
import io
import json
from pathlib import Path
from typing import Optional

from bs4 import BeautifulSoup
from docx import Document as DocxDocument

from training_data_bot.core.models import Document, DocumentType
from training_data_bot.sources.base import BaseLoader
from training_data_bot.sources.exceptions import (
    DocumentLoadError,
    SourceNotFoundError,
    UnsupportedDocumentTypeError,
)


class DocumentLoader(BaseLoader):
    """Loads TXT, MD, HTML, JSON, CSV and DOCX files."""

    MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB

    def __init__(self):
        super().__init__()

        self.supported_formats = [
            DocumentType.TXT,
            DocumentType.MD,
            DocumentType.HTML,
            DocumentType.JSON,
            DocumentType.CSV,
            DocumentType.DOCX,
        ]

    async def load_single(
        self,
        source: str,
        **kwargs
    ) -> Document:

        path = Path(source)

        if not path.exists():
            raise SourceNotFoundError(
                f"File does not exist: {path}",
                file_path=str(path),
            )

        if not path.is_file():
            raise DocumentLoadError(
                f"Source is not a file: {path}",
                file_path=str(path),
            )

        if path.stat().st_size > self.MAX_FILE_SIZE:
            raise DocumentLoadError(
                f"File exceeds the maximum size of "
                f"{self.MAX_FILE_SIZE} bytes",
                file_path=str(path),
            )

        suffix = path.suffix.lower().lstrip(".")

        try:
            doc_type = DocumentType(suffix)
        except ValueError as exc:
            raise UnsupportedDocumentTypeError(
                f"Unsupported document format: {suffix}",
                file_path=str(path),
                cause=exc,
            ) from exc

        if doc_type not in self.supported_formats:
            raise UnsupportedDocumentTypeError(
                f"DocumentLoader cannot handle {doc_type.value}",
                file_path=str(path),
            )

        try:
            content = await asyncio.to_thread(
                self._extract_content,
                path,
                doc_type,
            )

            return Document(
                title=path.stem,
                content=content,
                source=str(path),
                doc_type=doc_type,
                word_count=len(content.split()),
                char_count=len(content),
            )

        except DocumentLoadError:
            raise

        except Exception as exc:
            raise DocumentLoadError(
                f"Failed to load document: {path}",
                file_path=str(path),
                cause=exc,
            ) from exc

    def _extract_content(
        self,
        path: Path,
        doc_type: DocumentType,
    ) -> str:
        """Extract content based on the document format."""

        if doc_type in (DocumentType.TXT, DocumentType.MD):
            return path.read_text(
                encoding="utf-8-sig",
                errors="replace",
            )

        if doc_type == DocumentType.HTML:
            html = path.read_text(
                encoding="utf-8",
                errors="replace",
            )
            soup = BeautifulSoup(html, "html.parser")

            for element in soup(
                ["script", "style", "noscript"]
            ):
                element.decompose()

            return soup.get_text(separator="\n", strip=True)

        if doc_type == DocumentType.JSON:
            raw = path.read_text(
                encoding="utf-8-sig",
                errors="replace",
            )

            data = json.loads(raw)

            return json.dumps(
                data,
                ensure_ascii=False,
                indent=2,
            )

        if doc_type == DocumentType.CSV:
            raw = path.read_text(
                encoding="utf-8-sig",
                errors="replace",
            )

            rows = csv.reader(io.StringIO(raw))

            return "\n".join(
                " | ".join(row)
                for row in rows
            )

        if doc_type == DocumentType.DOCX:
            doc = DocxDocument(str(path))

            paragraphs = [
                paragraph.text
                for paragraph in doc.paragraphs
                if paragraph.text.strip()
            ]

            return "\n".join(paragraphs)

        raise UnsupportedDocumentTypeError(
            f"Unsupported document format: {doc_type.value}"
        )
