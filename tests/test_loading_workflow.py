
import asyncio

from training_data_bot.sources import UnifiedLoader


async def main():

    loader = UnifiedLoader()

    # Load one document automatically
    document = await loader.load_single(
        "data/example.txt"
    )

    print("Title:", document.title)
    print("Type:", document.doc_type)
    print("Words:", document.word_count)
    print("Content:", document.content)

    # Load an entire directory
    documents = await loader.load_directory(
        "data/",
        recursive=True,
        max_workers=4,
    )

    print("\nTotal documents loaded:", len(documents))

    for doc in documents:
        print(
            doc.title,
            doc.doc_type.value,
            doc.word_count,
        )


if __name__ == "__main__":
    asyncio.run(main())
