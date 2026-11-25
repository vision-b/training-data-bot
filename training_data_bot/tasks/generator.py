import time
from typing import List

from training_data_bot.ai.base import BaseAIProvider
from training_data_bot.core.models import (
    TaskResult,
    TaskTemplate,
    TextChunk,
    TrainingExample,
)


class TaskGenerator:
    """
    Generates training tasks from text chunks using an AI provider.
    """

    def __init__(self, provider: BaseAIProvider):
        self.provider = provider

    def _build_prompt(
        self,
        chunk: TextChunk,
        template: TaskTemplate,
    ) -> str:
        """Insert chunk content into the task template."""

        try:
            return template.prompt_template.format(
                content=chunk.content
            )
        except KeyError as exc:
            raise ValueError(
                f"Unknown placeholder in task template: {exc}"
            ) from exc

    async def generate_task(
        self,
        chunk: TextChunk,
        template: TaskTemplate,
    ) -> TaskResult:
        """Generate one task result from one text chunk."""

        prompt = self._build_prompt(chunk, template)

        parameters = template.parameters or {}
        temperature = parameters.get("temperature", 0.7)
        max_tokens = parameters.get("max_tokens")

        start_time = time.perf_counter()

        output = await self.provider.generate(
            prompt=prompt,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        processing_time = time.perf_counter() - start_time

        return TaskResult(
            task_id=template.id,
            input_chunk_id=chunk.id,
            output=output,
            confidence=0.0,
            quality_scores={},
            processing_time=processing_time,
)

    def create_training_example(
        self,
        chunk: TextChunk,
        template: TaskTemplate,
        result: TaskResult,
    ) -> TrainingExample:
        """Convert a task result into a training example."""

        return TrainingExample(
            input_text=chunk.content,
            output_text=result.output,
            task_type=template.task_type,
            source_document_id=chunk.document_id,
            source_chunk_id=chunk.id,
        )

    async def generate_examples(
        self,
        chunks: List[TextChunk],
        template: TaskTemplate,
    ) -> List[TrainingExample]:
        """Generate training examples from multiple chunks."""

        examples = []

        for chunk in chunks:
            result = await self.generate_task(chunk, template)

            example = self.create_training_example(
                chunk=chunk,
                template=template,
                result=result,
            )

            examples.append(example)

        return examples