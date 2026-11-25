from training_data_bot.core.models import TaskTemplate, TaskType


def create_qa_template() -> TaskTemplate:
    """Create a template for question-and-answer generation."""

    return TaskTemplate(
        name="Question and Answer Generation",
        task_type=TaskType.QA_GENERATION,
        description="Generate a question and answer based on source text.",
        prompt_template=(
            "Read the following text and create one useful question "
            "and its answer.\n\n"
            "Use only information supported by the source text.\n\n"
            "Source text:\n"
            "{content}\n\n"
            "Return the question and answer clearly labelled."
        ),
        parameters={
            "temperature": 0.7,
            "max_tokens": 500,
        },
    )


def create_summarization_template() -> TaskTemplate:
    """Create a template for summarization."""

    return TaskTemplate(
        name="Text Summarization",
        task_type=TaskType.SUMMARIZATION,
        description="Create a concise summary of source text.",
        prompt_template=(
            "Summarize the following text clearly and accurately.\n\n"
            "Do not introduce information that is not in the source.\n\n"
            "Source text:\n"
            "{content}"
        ),
        parameters={
            "temperature": 0.5,
            "max_tokens": 500,
        },
    )