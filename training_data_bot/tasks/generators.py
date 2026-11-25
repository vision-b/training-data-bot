from typing import List
from training_data_bot.core.models import TaskResult, TaskTemplate, TextChunk, TrainingExample, TaskType


class _BaseTaskGenerator:
    def __init__(self, ai_client):
        self.ai_client = ai_client

    async def generate(self, chunk: TextChunk) -> TrainingExample:
        prompt = self.template.prompt_template.format(content=chunk.content)
        output = await self.ai_client.generate(
            prompt=prompt,
            temperature=self.template.parameters.get("temperature", 0.7),
            max_tokens=self.template.parameters.get("max_tokens"),
        )
        result = TaskResult(
            task_id=self.template.id,
            input_chunk_id=chunk.id,
            output=output,
            confidence=0.0,
            quality_scores={},
            processing_time=0.0,
        )
        return TrainingExample(
            input_text=chunk.content,
            output_text=result.output,
            task_type=self.template.task_type,
            source_document_id=chunk.document_id,
            source_chunk_id=chunk.id,
            quality_scores=result.quality_scores,
        )


class QAGenerator(_BaseTaskGenerator):
    def __init__(self, ai_client):
        super().__init__(ai_client)
        self.template = TaskTemplate(
            name="Question and Answer Generation",
            task_type=TaskType.QA_GENERATION,
            description="Generate a question and answer from source text.",
            prompt_template=(
                "Read the source text and create one useful question and its answer. "
                "Use only information supported by the source text.\n\n{content}"
            ),
            parameters={"temperature": 0.7, "max_tokens": 500},
        )


class ClassificationGenerator(_BaseTaskGenerator):
    def __init__(self, ai_client):
        super().__init__(ai_client)
        self.template = TaskTemplate(
            name="Text Classification",
            task_type=TaskType.CLASSIFICATION,
            description="Assign a concise category to source text.",
            prompt_template=(
                "Classify the following text. Return the category and a brief reason. "
                "Do not invent information.\n\n{content}"
            ),
            parameters={"temperature": 0.2, "max_tokens": 250},
        )


class SummarizationGenerator(_BaseTaskGenerator):
    def __init__(self, ai_client):
        super().__init__(ai_client)
        self.template = TaskTemplate(
            name="Text Summarization",
            task_type=TaskType.SUMMARIZATION,
            description="Create a concise summary of source text.",
            prompt_template="Summarize the following text accurately.\n\n{content}",
            parameters={"temperature": 0.5, "max_tokens": 500},
        )
