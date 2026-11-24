
import asyncio
import pytest

from training_data_bot.sources import (
    UnifiedLoader,
    DocumentLoader,
    PDFLoader,
    WebLoader,
)
from training_data_bot.sources.exceptions import (
    SourceNotFoundError,
    UnsupportedDocumentTypeError,
)
from training_data_bot.core.models import DocumentType


def test_loader_initialization():

    loader = UnifiedLoader()

    assert isinstance(loader.document_loader, DocumentLoader)
    assert isinstance(loader.pdf_loader, PDFLoader)
    assert isinstance(loader.web_loader, WebLoader)


def test_url_routing():

    loader = UnifiedLoader()

    selected = loader._select_loader(
        "https://example.com"
    )

    assert isinstance(selected, WebLoader)


def test_pdf_routing(tmp_path):

    file = tmp_path / "example.pdf"
    file.write_bytes(b"fake pdf")

    loader = UnifiedLoader()

    selected = loader._select_loader(str(file))

    assert isinstance(selected, PDFLoader)


def test_text_routing(tmp_path):

    file = tmp_path / "example.txt"
    file.write_text("Hello")

    loader = UnifiedLoader()

    selected = loader._select_loader(str(file))

    assert isinstance(selected, DocumentLoader)


def test_validate_source(tmp_path):

    file = tmp_path / "example.txt"
    file.write_text("Hello")

    loader = UnifiedLoader()

    assert loader.validate_source(str(file))
    assert loader.validate_source("https://example.com")
    assert not loader.validate_source("missing.txt")


def test_unsupported_file(tmp_path):

    file = tmp_path / "example.xyz"
    file.write_text("Hello")

    loader = UnifiedLoader()

    with pytest.raises(UnsupportedDocumentTypeError):
        loader._select_loader(str(file))


def test_missing_file():

    loader = UnifiedLoader()

    with pytest.raises(SourceNotFoundError):
        loader._select_loader("missing.txt")


def test_load_single(tmp_path):

    file = tmp_path / "example.txt"
    file.write_text("Hello from UnifiedLoader")

    document = asyncio.run(
        UnifiedLoader().load_single(str(file))
    )

    assert document.doc_type == DocumentType.TXT
    assert document.content == "Hello from UnifiedLoader"


def test_load_directory(tmp_path):

    (tmp_path / "first.txt").write_text("First document")
    (tmp_path / "second.md").write_text("# Second document")
    (tmp_path / "ignored.xyz").write_text("Ignored")

    loader = UnifiedLoader()

    documents = asyncio.run(
        loader.load_directory(str(tmp_path))
    )

    assert len(documents) == 2

    titles = {document.title for document in documents}

    assert titles == {"first", "second"}


def test_load_directory_non_recursive(tmp_path):

    (tmp_path / "first.txt").write_text("First")

    nested = tmp_path / "nested"
    nested.mkdir()
    (nested / "second.txt").write_text("Second")

    documents = asyncio.run(
        UnifiedLoader().load_directory(
            str(tmp_path),
            recursive=False,
        )
    )

    assert len(documents) == 1
    assert documents[0].title == "first"
