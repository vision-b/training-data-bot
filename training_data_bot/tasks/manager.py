from typing import List
from training_data_bot.core.models import TaskType, TextChunk, TrainingExample
from training_data_bot.tasks.generators import (
    QAGenerator, ClassificationGenerator, SummarizationGenerator,
)


class TaskManager:
    """Coordinates the specialized task generators."""

    def __init__(self, ai_client):
        self.ai_client = ai_client
        self.generators = {
            TaskType.QA_GENERATION: QAGenerator(ai_client),
            TaskType.CLASSIFICATION: ClassificationGenerator(ai_client),
            TaskType.SUMMARIZATION: SummarizationGenerator(ai_client),
        }

    async def generate_examples(
        self,
        chunks: List[TextChunk],
        task_types: List[TaskType],
    ) -> List[TrainingExample]:
        examples = []
        for task_type in task_types:
            generator = self.generators.get(task_type)
            if generator is None:
                continue
            for chunk in chunks:
                examples.append(await generator.generate(chunk))
        return examples
