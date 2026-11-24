
import asyncio
import pytest



from training_data_bot.sources.pdf_loader import PDFLoader
from training_data_bot.sources.exceptions import (
    SourceNotFoundError,
    DocumentLoadError,
)
from training_data_bot.core.models import DocumentType


def test_pdf_loader_supported_formats():

    loader = PDFLoader()

    assert loader.supported_formats == [DocumentType.PDF]


def test_missing_pdf():

    with pytest.raises(SourceNotFoundError):
        asyncio.run(
            PDFLoader().load_single("missing.pdf")
        )


def test_reject_non_pdf_file(tmp_path):

    file = tmp_path / "example.txt"
    file.write_text("Hello")

    with pytest.raises(DocumentLoadError):
        asyncio.run(
            PDFLoader().load_single(str(file))
        )


def test_pdf_extraction(tmp_path, monkeypatch):

    file = tmp_path / "example.pdf"
    file.write_bytes(b"fake pdf for mocked extraction")

    loader = PDFLoader()

    def fake_extract(path):
        return "Extracted PDF content"

    monkeypatch.setattr(
        loader,
        "_extract_pdf_text",
        fake_extract,
    )

    document = asyncio.run(
        loader.load_single(str(file))
    )

    assert document.content == "Extracted PDF content"
    assert document.doc_type == DocumentType.PDF
    assert document.word_count == 3
