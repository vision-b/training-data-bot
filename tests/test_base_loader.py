
import asyncio
import pytest

from training_data_bot.sources.base import BaseLoader
from training_data_bot.core.models import Document, DocumentType


def test_base_loader_is_abstract():
    with pytest.raises(TypeError):
        BaseLoader()


def test_child_must_implement_abstract_method():

    class IncompleteLoader(BaseLoader):
        pass

    with pytest.raises(TypeError):
        IncompleteLoader()


def test_concrete_loader_can_be_created():

    class DummyLoader(BaseLoader):

        async def load_single(self, source, **kwargs):
            return Document(
                title="test",
                content="Hello world",
                source=source,
                doc_type=DocumentType.TXT,
                word_count=2,
                char_count=11,
            )

    loader = DummyLoader()

    assert isinstance(loader, BaseLoader)
    assert loader.logger is not None


def test_load_multiple():

    class DummyLoader(BaseLoader):

        async def load_single(self, source, **kwargs):
            return Document(
                title=source,
                content="Hello world",
                source=source,
                doc_type=DocumentType.TXT,
                word_count=2,
                char_count=11,
            )

    loader = DummyLoader()

    documents = asyncio.run(
        loader.load_multiple(["a.txt", "b.txt"])
    )

    assert len(documents) == 2
    assert documents[0].title == "a.txt"


def test_load_multiple_rejects_invalid_worker_count():

    class DummyLoader(BaseLoader):

        async def load_single(self, source, **kwargs):
            return None

    loader = DummyLoader()

    with pytest.raises(ValueError):
        asyncio.run(
            loader.load_multiple(["a.txt"], max_workers=0)
        )
