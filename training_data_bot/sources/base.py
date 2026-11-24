
"""Abstract base class for all document loaders."""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import List, Sequence

from training_data_bot.core.models import Document, DocumentType
from training_data_bot.sources.exceptions import DocumentLoadError


class BaseLoader(ABC):
    """
    Defines the common interface and functionality
    shared by all specialized document loaders.
    """

    def __init__(self):
        self.logger = logging.getLogger(
            f"loader.{self.__class__.__name__}"
        )

        self.supported_formats: List[DocumentType] = []

    @abstractmethod
    async def load_single(
        self,
        source: str,
        **kwargs
    ) -> Document:
        """
        Load one source and return a Document object.

        Every concrete loader must implement this method.
        """
        raise NotImplementedError

    async def load_multiple(
        self,
        sources: Sequence[str],
        max_workers: int = 4,
    ) -> List[Document]:
        """
        Load multiple sources concurrently.

        max_workers controls the maximum number
        of simultaneous loading operations.

        Failed documents are logged and skipped.
        """

        if max_workers < 1:
            raise ValueError("max_workers must be at least 1")

        semaphore = asyncio.Semaphore(max_workers)

        async def load_with_semaphore(source: str):
            async with semaphore:
                try:
                    document = await self.load_single(source)

                    if not isinstance(document, Document):
                        raise DocumentLoadError(
                            f"Loader returned an invalid result for {source}"
                        )

                    return document

                except Exception:
                    self.logger.exception(
                        "Failed to load source: %s", source
                    )
                    return None

        tasks = [
            load_with_semaphore(source)
            for source in sources
        ]

        results = await asyncio.gather(*tasks)

        documents = [
            result
            for result in results
            if isinstance(result, Document)
        ]

        self.logger.info(
            "Loaded %d out of %d documents",
            len(documents),
            len(sources),
        )

        return documents
