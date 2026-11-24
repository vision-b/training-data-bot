
from training_data_bot.core.models import (
    Document,
    DocumentType,
    TextChunk,
    TaskType,
    TrainingExample,
    Dataset,
)


def main():
    # 1. Create a document
    document = Document(
        title="Introduction to Artificial Intelligence",
        content="Artificial intelligence is a field of computer science.",
        source="example.txt",
        doc_type=DocumentType.TXT,
        word_count=9,
        char_count=55,
    )

    print("DOCUMENT:")
    print(document)
    print("Document ID:", document.id)

    # 2. Create a text chunk linked to the document
    chunk = TextChunk(
        document_id=document.id,
        content=document.content,
        start_index=0,
        end_index=len(document.content),
        chunk_index=0,
        token_count=9,
    )

    print("\nTEXT CHUNK:")
    print(chunk)

    # 3. Create a training example
    example = TrainingExample(
        input_text="What is artificial intelligence?",
        output_text="A field of computer science.",
        task_type=TaskType.QA_GENERATION,
        source_document_id=document.id,
        source_chunk_id=chunk.id,
        quality_scores={"relevance": 0.95},
    )

    print("\nTRAINING EXAMPLE:")
    print(example)

    # 4. Create a dataset
    dataset = Dataset(
        name="AI Introduction Dataset",
        description="A small example dataset",
        examples=[example],
        total_examples=1,
        train_split=0.8,
        validation_split=0.1,
        test_split=0.1,
    )

    print("\nDATASET:")
    print(dataset)

    # 5. Convert the dataset to JSON
    print("\nDATASET JSON:")
    print(dataset.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
