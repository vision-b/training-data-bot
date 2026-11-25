
"""
Main interface for the Training Data Curation Bot.

This class coordinates the components of the application.
At this stage, document loading and state management are
implemented. AI processing, quality evaluation, and export
will be connected in later phases.
"""

import inspect
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from training_data_bot.core.models import (
    Dataset,
    Document,
    DocumentType,
    ProcessingJob,
    ProcessingStatus,
    QualityReport,
    TaskType,
)
from training_data_bot.sources.unified import UnifiedLoader


# ============================================================
# 1. CUSTOM EXCEPTIONS
# ============================================================

class TrainingDataBotError(Exception):
    """Base exception for errors raised by TrainingDataBot."""


class ConfigurationError(TrainingDataBotError):
    """Raised when the bot cannot be configured correctly."""


# ============================================================
# 2. MAIN BOT CLASS
# ============================================================

class TrainingDataBot:
    """
    High-level interface for the Training Data Curation Bot.

    The bot coordinates document loading and keeps track of
    documents, datasets, and processing jobs.
    """

    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        loader: Optional[UnifiedLoader] = None,
    ):
        """
        Initialize the bot.

        Args:
            config: Optional application configuration.
            loader: Optional document loader. Supplying one is
                    useful for testing or custom configurations.
        """

        self.logger = logging.getLogger(self.__class__.__name__)

        self.config = config or {}

        # Store the loader so it can be reused.
        self.loader = loader

        # Application state.
        self.documents: Dict[UUID, Document] = {}
        self.datasets: Dict[UUID, Dataset] = {}
        self.jobs: Dict[UUID, ProcessingJob] = {}

        self._init_components()

        self.logger.info("TrainingDataBot initialized successfully")

    # ========================================================
    # 3. COMPONENT INITIALIZATION
    # ========================================================

    def _init_components(self) -> None:
        """
        Initialize the components currently available.

        More components will be added in later phases.
        """

        try:
            if self.loader is None:
                self.loader = UnifiedLoader()

        except Exception as exc:
            raise ConfigurationError(
                "Failed to initialize TrainingDataBot components"
            ) from exc

    # ========================================================
    # 4. DOCUMENT LOADING
    # ========================================================

    async def load_documents(
        self,
        sources: Union[str, Path, List[Union[str, Path]]],
        doc_types: Optional[List[DocumentType]] = None,
        **kwargs: Any,
    ) -> List[Document]:
        """
        Load documents from files, directories, or URLs.

        A single source can be supplied as a string or Path.
        Multiple sources can be supplied as a list.

        Directories are loaded using load_directory().
        Individual files and URLs use load_single().

        Args:
            sources: One source or a list of sources.
            doc_types: Optional list of document types to keep.
            **kwargs: Additional loader options.

        Returns:
            A list of successfully loaded documents.
        """

        # Normalize one source into a list.
        if isinstance(sources, (str, Path)):
            sources = [sources]

        loaded_documents: List[Document] = []

        for source in sources:
            source_string = str(source)

            self.logger.info("Loading source: %s", source_string)

            # A URL is handled as one individual source.
            is_url = source_string.startswith(
                ("http://", "https://")
            )

            # Check whether the source is a directory.
            if not is_url and Path(source_string).is_dir():
                documents = await self.loader.load_directory(
                    source_string,
                    recursive=kwargs.get("recursive", True),
                    max_workers=kwargs.get("max_workers", 4),
                )

            else:
                document = await self.loader.load_single(
                    source_string
                )
                documents = [document]

            # Optionally filter by document type.
            if doc_types is not None:
                allowed_types = {
                    DocumentType(doc_type)
                    for doc_type in doc_types
                }

                documents = [
                    document
                    for document in documents
                    if document.doc_type in allowed_types
                ]

            # Save each document using its unique UUID.
            for document in documents:
                self.documents[document.id] = document
                loaded_documents.append(document)

        self.logger.info(
            "Successfully loaded %d document(s)",
            len(loaded_documents),
        )

        return loaded_documents

    # ========================================================
    # 5. STATE AND STATISTICS
    # ========================================================

    def get_statistics(self) -> Dict[str, Any]:
        """
        Return an overview of the bot's current state.
        """

        documents_by_type: Dict[str, int] = {}

        for document in self.documents.values():
            doc_type = document.doc_type.value

            documents_by_type[doc_type] = (
                documents_by_type.get(doc_type, 0) + 1
            )

        jobs_by_status: Dict[str, int] = {}

        for job in self.jobs.values():
            status = job.status.value

            jobs_by_status[status] = (
                jobs_by_status.get(status, 0) + 1
            )

        total_examples = sum(
            dataset.total_examples
            for dataset in self.datasets.values()
        )

        total_characters = sum(
            document.char_count
            for document in self.documents.values()
        )

        active_jobs = sum(
            1
            for job in self.jobs.values()
            if job.status in (
                ProcessingStatus.PENDING,
                ProcessingStatus.RUNNING,
            )
        )

        return {
            "documents": {
                "total": len(self.documents),
                "by_type": documents_by_type,
                "total_characters": total_characters,
            },
            "datasets": {
                "total": len(self.datasets),
                "total_examples": total_examples,
            },
            "jobs": {
                "total": len(self.jobs),
                "by_status": jobs_by_status,
                "active": active_jobs,
            },
        }

    # ========================================================
    # 6. FUTURE PROCESSING FEATURES
    # ========================================================

    async def process_documents(
        self,
        documents: Optional[List[Document]] = None,
        task_types: Optional[List[TaskType]] = None,
        quality_filter: bool = True,
        **kwargs: Any,
    ) -> Dataset:
        """
        Generate training examples from documents.

        This method will be implemented when the AI,
        preprocessing, task, and evaluation components
        are available in later phases.
        """

        raise NotImplementedError(
            "Document processing will be implemented "
            "in the AI integration and task generation phases."
        )

    async def evaluate_dataset(
        self,
        dataset: Dataset,
        detailed_report: bool = True,
    ) -> QualityReport:
        """
        Evaluate the quality of a dataset.

        This method will be connected to QualityEvaluator
        in the quality evaluation phase.
        """

        raise NotImplementedError(
            "Dataset evaluation will be implemented "
            "in the quality evaluation phase."
        )

    async def export_dataset(
        self,
        dataset: Dataset,
        output_path: Union[str, Path],
        **kwargs: Any,
    ) -> Path:
        """
        Export a dataset to a file.

        This method will be connected to DatasetExporter
        in the storage and export phase.
        """

        raise NotImplementedError(
            "Dataset export will be implemented "
            "in the storage and export phase."
        )

    # ========================================================
    # 7. CLEANUP
    # ========================================================

    async def cleanup(self) -> None:
        """
        Release resources held by components.

        The current loader does not require an explicit
        shutdown, but this method provides a place to close
        components when they are added.
        """

        if self.loader is not None:
            close_method = getattr(self.loader, "close", None)

            if callable(close_method):
                result = close_method()

                if inspect.isawaitable(result):
                    await result

        self.logger.info("TrainingDataBot cleanup completed")

    # ========================================================
    # 8. ASYNCHRONOUS CONTEXT MANAGER
    # ========================================================

    async def __aenter__(self):
        """
        Called when entering an 'async with' block.
        """

        return self

    async def __aexit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ):
        """
        Called when leaving an 'async with' block.
        """

        await self.cleanup()

        # False means exceptions are not suppressed.
        return False
