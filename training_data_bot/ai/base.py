from abc import ABC, abstractmethod
from typing import Optional


class BaseAIProvider(ABC):
    """
    Abstract interface for AI providers.

    Every AI provider used by the application must implement
    the generate() method.
    """

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> str:
        """
        Generate text from a prompt.

        Args:
            prompt: Instructions sent to the AI.
            temperature: Controls response variation.
            max_tokens: Optional response-length limit.

        Returns:
            Generated text.
        """
        raise NotImplementedError