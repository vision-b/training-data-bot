import pytest

from training_data_bot.ai import MockAIProvider
from training_data_bot.core.models import (
    DocumentType,
    TaskType,
    TextChunk,
)
from training_data_bot.tasks import (
    TaskGenerator,
    create_qa_template,
    create_summarization_template,
)


@pytest.fixture
def sample_chunk():
    return TextChunk(
        document_id="11111111-1111-1111-1111-111111111111",
        content="Artificial intelligence is a field of computer science.",
        start_index=0,
        end_index=58,
        chunk_index=0,
        token_count=10,
    )


@pytest.fixture
def generator():
    return TaskGenerator(provider=MockAIProvider())


@pytest.mark.asyncio
async def test_generate_task(generator, sample_chunk):
    template = create_qa_template()

    result = await generator.generate_task(
        chunk=sample_chunk,
        template=template,
    )

    assert result.output
    assert result.task_id == template.id
    assert result.input_chunk_id == sample_chunk.id
    assert result.processing_time >= 0


@pytest.mark.asyncio
async def test_create_training_example(generator, sample_chunk):
    template = create_qa_template()

    result = await generator.generate_task(
        chunk=sample_chunk,
        template=template,
    )

    example = generator.create_training_example(
        chunk=sample_chunk,
        template=template,
        result=result,
    )

    assert example.input_text == sample_chunk.content
    assert example.output_text == result.output
    assert example.task_type == TaskType.QA_GENERATION
    assert example.source_document_id == sample_chunk.document_id
    assert example.source_chunk_id == sample_chunk.id


@pytest.mark.asyncio
async def test_generate_multiple_examples(generator, sample_chunk):
    template = create_summarization_template()

    examples = await generator.generate_examples(
        chunks=[sample_chunk, sample_chunk],
        template=template,
    )

    assert len(examples) == 2
    assert all(
        example.task_type == TaskType.SUMMARIZATION
        for example in examples
    )


def test_build_prompt_includes_chunk_content(generator, sample_chunk):
    template = create_qa_template()

    prompt = generator._build_prompt(sample_chunk, template)

    assert sample_chunk.content in prompt
    assert "{content}" not in prompt


@pytest.mark.asyncio
async def test_empty_prompt_is_rejected():
    provider = MockAIProvider()

    with pytest.raises(ValueError):
        await provider.generate("")