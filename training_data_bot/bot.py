"""Main orchestration interface for the Training Data Curation Bot."""

import inspect
import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from training_data_bot.ai import AIClient, MockAIProvider
from training_data_bot.core.models import (
    Dataset, Document, DocumentType, ExportFormat, ProcessingJob,
    ProcessingStatus, QualityReport, TaskType,
)
from training_data_bot.evaluation import QualityEvaluator
from training_data_bot.preprocessing import TextPreprocessor
from training_data_bot.sources.unified import UnifiedLoader
from training_data_bot.storage import DatabaseManager, DatasetExporter
from training_data_bot.tasks import TaskManager


class TrainingDataBotError(Exception):
    """Base exception for bot errors."""


class ConfigurationError(TrainingDataBotError):
    """Raised when bot components cannot be initialized."""


class TrainingDataBot:
    """Coordinates loading, preprocessing, generation, evaluation and export."""

    def __init__(self, config: Optional[Dict[str, Any]] = None, loader=None):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.config = config or {}
        self.loader = loader
        self.documents: Dict[UUID, Document] = {}
        self.datasets: Dict[UUID, Dataset] = {}
        self.jobs: Dict[UUID, ProcessingJob] = {}
        self._init_components()
        self.logger.info("TrainingDataBot initialized successfully")

    def _init_components(self) -> None:
        try:
            if self.loader is None:
                self.loader = UnifiedLoader()

            # Local mock is the safe default; set use_mock_ai=False to use API.
            if self.config.get("use_mock_ai", True):
                self.ai_client = MockAIProvider()
            else:
                self.ai_client = AIClient(
                    api_key=self.config.get("api_key"),
                    base_url=self.config.get("base_url", "https://api.openai.com/v1"),
                    model=self.config.get("model", "gpt-4o-mini"),
                )

            self.preprocessor = TextPreprocessor(
                chunk_size=self.config.get("chunk_size", 500),
                overlap=self.config.get("chunk_overlap", 50),
            )
            self.task_manager = TaskManager(self.ai_client)
            self.evaluator = QualityEvaluator(
                pass_threshold=self.config.get("quality_threshold", 0.6)
            )
            self.exporter = DatasetExporter()
            self.db_manager = DatabaseManager(
                self.config.get("database_path", "data/training_data_bot.db")
            )
        except Exception as exc:
            raise ConfigurationError("Failed to initialize TrainingDataBot components") from exc

    async def load_documents(
        self,
        sources: Union[str, Path, List[Union[str, Path]]],
        doc_types: Optional[List[DocumentType]] = None,
        **kwargs: Any,
    ) -> List[Document]:
        if isinstance(sources, (str, Path)):
            sources = [sources]
        loaded_documents = []
        for source in sources:
            source_string = str(source)
            is_url = source_string.startswith(("http://", "https://"))
            if not is_url and Path(source_string).is_dir():
                documents = await self.loader.load_directory(
                    source_string,
                    recursive=kwargs.get("recursive", True),
                    max_workers=kwargs.get("max_workers", 4),
                )
            else:
                documents = [await self.loader.load_single(source_string)]
            if doc_types is not None:
                allowed_types = {DocumentType(item) for item in doc_types}
                documents = [d for d in documents if d.doc_type in allowed_types]
            for document in documents:
                self.documents[document.id] = document
                loaded_documents.append(document)
        self.logger.info("Successfully loaded %d document(s)", len(loaded_documents))
        return loaded_documents

    async def process_documents(
        self,
        documents: Optional[List[Document]] = None,
        task_types: Optional[List[TaskType]] = None,
        quality_filter: bool = True,
        **kwargs: Any,
    ) -> Dataset:
        documents = documents if documents is not None else list(self.documents.values())
        task_types = task_types or [TaskType.QA_GENERATION, TaskType.SUMMARIZATION]
        task_types = [TaskType(item) for item in task_types]

        job = ProcessingJob(
            name="Document processing",
            job_type="training_data_generation",
            status=ProcessingStatus.RUNNING,
            total_items=len(documents),
            processed_items=0,
            started_at=datetime.now(timezone.utc),
            estimated_completion=datetime.now(timezone.utc),
        )
        self.jobs[job.id] = job

        examples = []
        try:
            for document in documents:
                chunks = self.preprocessor.process_document(document)
                generated = await self.task_manager.generate_examples(chunks, task_types)
                examples.extend(generated)
                job.processed_items += 1

            if quality_filter:
                examples = self.evaluator.filter_examples(examples)

            dataset = Dataset(
                name=kwargs.get("dataset_name", "Generated Training Dataset"),
                description=kwargs.get("description", "Generated from source documents."),
                examples=examples,
                total_examples=len(examples),
                train_split=kwargs.get("train_split", 0.8),
                validation_split=kwargs.get("validation_split", 0.1),
                test_split=kwargs.get("test_split", 0.1),
            )

            if quality_filter and dataset.examples:
                report = await self.evaluator.evaluate_dataset(dataset)
                if not report.passed:
                    self.logger.warning("Dataset did not pass the configured quality threshold.")
                # The report is retained in dataset metadata for traceability.
                dataset.metadata["quality_report_id"] = str(report.id)

            self.datasets[dataset.id] = dataset
            job.status = ProcessingStatus.COMPLETED
            return dataset
        except Exception:
            job.status = ProcessingStatus.FAILED
            raise

    async def evaluate_dataset(
        self, dataset: Dataset, detailed_report: bool = True
    ) -> QualityReport:
        report = await self.evaluator.evaluate_dataset(dataset, detailed_report)
        return report

    async def export_dataset(
        self,
        dataset: Dataset,
        output_path: Union[str, Path],
        format: ExportFormat = ExportFormat.JSONL,
        split_data: bool = True,
        **kwargs: Any,
    ) -> Path:
        path = await self.exporter.export_dataset(
            dataset, output_path, format=format, split_data=split_data
        )
        self.db_manager.save_dataset(dataset)
        return path

    async def quick_process(
        self,
        source: Union[str, Path],
        output_path: Union[str, Path],
        task_types: Optional[List[TaskType]] = None,
        export_format: ExportFormat = ExportFormat.JSONL,
    ) -> Dataset:
        documents = await self.load_documents([source])
        dataset = await self.process_documents(documents=documents, task_types=task_types)
        await self.export_dataset(dataset, output_path, format=export_format)
        return dataset

    def get_statistics(self) -> Dict[str, Any]:
        documents_by_type = {}
        for document in self.documents.values():
            key = document.doc_type.value
            documents_by_type[key] = documents_by_type.get(key, 0) + 1

        jobs_by_status = {}
        for job in self.jobs.values():
            key = job.status.value
            jobs_by_status[key] = jobs_by_status.get(key, 0) + 1

        return {
            "documents": {
                "total": len(self.documents),
                "by_type": documents_by_type,
                "total_characters": sum(d.char_count for d in self.documents.values()),
            },
            "datasets": {
                "total": len(self.datasets),
                "total_examples": sum(d.total_examples for d in self.datasets.values()),
            },
            "jobs": {
                "total": len(self.jobs),
                "by_status": jobs_by_status,
                "active": sum(
                    1 for job in self.jobs.values()
                    if job.status in (ProcessingStatus.PENDING, ProcessingStatus.RUNNING)
                ),
            },
        }

    async def cleanup(self) -> None:
        if self.loader is not None:
            close_method = getattr(self.loader, "close", None)
            if callable(close_method):
                result = close_method()
                if inspect.isawaitable(result):
                    await result
        if getattr(self, "db_manager", None) is not None:
            await self.db_manager.close()
        if getattr(self, "ai_client", None) is not None:
            close_method = getattr(self.ai_client, "close", None)
            if callable(close_method):
                result = close_method()
                if inspect.isawaitable(result):
                    await result
        self.logger.info("TrainingDataBot cleanup completed")

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.cleanup()
        return False

