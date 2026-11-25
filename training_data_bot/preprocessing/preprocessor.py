import re
from typing import List
from training_data_bot.core.models import Document, TextChunk
from training_data_bot.preprocessing.cleaner import TextCleaner
from training_data_bot.preprocessing.normalizer import TextNormalizer
from training_data_bot.preprocessing.chunker import TextChunker


class TextPreprocessor:
    """Normalizes, cleans, and splits documents into traceable TextChunk objects."""

    def __init__(self, chunk_size: int = 500, overlap: int = 50):
        self.normalizer = TextNormalizer()
        self.cleaner = TextCleaner()
        self.chunker = TextChunker(chunk_size=chunk_size, overlap=overlap)

    def process_document(self, document: Document) -> List[TextChunk]:
        text = self.normalizer.normalize(document.content)
        text = self.cleaner.clean(text)
        raw_chunks = self.chunker.chunk_text(text)

        chunks = []
        search_from = 0
        for index, content in enumerate(raw_chunks):
            start = text.find(content, search_from)
            if start < 0:
                start = search_from
            end = start + len(content)
            search_from = max(start + 1, end - self.chunker.overlap)
            chunks.append(TextChunk(
                document_id=document.id,
                content=content,
                start_index=start,
                end_index=end,
                chunk_index=index,
                token_count=len(re.findall(r"\w+", content)),
            ))
        return chunks

    def process_documents(self, documents: List[Document]) -> List[TextChunk]:
        chunks = []
        for document in documents:
            chunks.extend(self.process_document(document))
        return chunks