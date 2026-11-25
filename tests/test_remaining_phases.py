import json
import pytest

from training_data_bot.core.models import Document, DocumentType, TaskType, ExportFormat
from training_data_bot.preprocessing import TextPreprocessor
from training_data_bot.evaluation import QualityEvaluator
from training_data_bot.storage import DatasetExporter
from training_data_bot.bot import TrainingDataBot


def sample_document():
    text = "Artificial intelligence is a field of computer science.\n\nIt studies intelligent systems."
    return Document(
        title="AI basics",
        content=text,
        source="sample.txt",
        doc_type=DocumentType.TXT,
        word_count=len(text.split()),
        char_count=len(text),
    )


def test_preprocessor_creates_linked_chunks():
    document = sample_document()
    chunks = TextPreprocessor(chunk_size=5, overlap=1).process_document(document)
    assert chunks
    assert all(chunk.document_id == document.id for chunk in chunks)
    assert all(chunk.token_count > 0 for chunk in chunks)


def test_quality_evaluator_flags_empty_dataset():
    from training_data_bot.core.models import Dataset
    dataset = Dataset(name="empty", description="test", examples=[], total_examples=0)
    report = QualityEvaluator().evaluate_examples(dataset.examples, dataset.id)
    assert report.passed is False
    assert report.issues


@pytest.mark.asyncio
async def test_jsonl_export_writes_split_labels(tmp_path):
    bot = TrainingDataBot(config={"database_path": str(tmp_path / "test.db")})
    dataset = await bot.process_documents(
        [sample_document()],
        [TaskType.QA_GENERATION],
    )
    output = tmp_path / "data.jsonl"
    await DatasetExporter().export_dataset(
        dataset, output, ExportFormat.JSONL, split_data=True
    )
    rows = [json.loads(line) for line in output.read_text().splitlines()]
    assert rows
    assert all(row["split"] in {"train", "validation", "test"} for row in rows)
    await bot.cleanup()
