
from typing import List


class TextChunker:
    """Split text into chunks with optional overlapping words."""

    def __init__(
        self,
        chunk_size: int = 500,
        overlap: int = 50,
    ):
        if chunk_size <= 0:
            raise ValueError("chunk_size must be greater than zero.")

        if overlap < 0 or overlap >= chunk_size:
            raise ValueError(
                "overlap must be non-negative and smaller than chunk_size."
            )

        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_text(self, text: str) -> List[str]:
        """Split text into chunks measured in words."""

        if not isinstance(text, str):
            raise TypeError("Input must be a string.")

        words = text.split()

        if not words:
            return []

        chunks = []
        start = 0

        while start < len(words):
            end = start + self.chunk_size
            chunk_words = words[start:end]

            chunks.append(" ".join(chunk_words))

            if end >= len(words):
                break

            start = end - self.overlap

        return chunks

