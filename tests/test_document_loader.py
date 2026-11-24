
import asyncio
import pytest

from training_data_bot.sources.document_loader import DocumentLoader
from training_data_bot.sources.exceptions import (
    SourceNotFoundError,
    UnsupportedDocumentTypeError,
)
from training_data_bot.core.models import DocumentType


def test_load_txt(tmp_path):

    file = tmp_path / "example.txt"
    file.write_text("Hello world from Python", encoding="utf-8")

    loader = DocumentLoader()

    document = asyncio.run(
        loader.load_single(str(file))
    )

    assert document.title == "example"
    assert document.content == "Hello world from Python"
    assert document.doc_type == DocumentType.TXT
    assert document.word_count == 4
    assert document.char_count == 23


def test_load_markdown(tmp_path):

    file = tmp_path / "notes.md"
    file.write_text("# Introduction\nHello", encoding="utf-8")

    document = asyncio.run(
        DocumentLoader().load_single(str(file))
    )

    assert "# Introduction" in document.content
    assert document.doc_type == DocumentType.MD


def test_load_html(tmp_path):

    file = tmp_path / "page.html"
    file.write_text(
        "<html><body><h1>Hello</h1>"
        "<script>alert('test')</script></body></html>",
        encoding="utf-8",
    )

    document = asyncio.run(
        DocumentLoader().load_single(str(file))
    )

    assert "Hello" in document.content
    assert "alert" not in document.content


def test_load_json(tmp_path):

    file = tmp_path / "data.json"
    file.write_text('{"name": "Python"}', encoding="utf-8")

    document = asyncio.run(
        DocumentLoader().load_single(str(file))
    )

    assert '"Python"' in document.content
    assert document.doc_type == DocumentType.JSON


def test_load_csv(tmp_path):

    file = tmp_path / "data.csv"
    file.write_text(
        "name,age\nAlice,20",
        encoding="utf-8",
    )

    document = asyncio.run(
        DocumentLoader().load_single(str(file))
    )

    assert "Alice" in document.content
    assert "20" in document.content


def test_missing_file():

    with pytest.raises(SourceNotFoundError):
        asyncio.run(
            DocumentLoader().load_single("missing.txt")
        )


def test_unsupported_format(tmp_path):

    file = tmp_path / "example.xyz"
    file.write_text("content")

    with pytest.raises(UnsupportedDocumentTypeError):
        asyncio.run(
            DocumentLoader().load_single(str(file))
        )
