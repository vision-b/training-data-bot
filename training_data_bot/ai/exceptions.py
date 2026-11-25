class AIProviderError(Exception):
    """Base exception for AI provider errors."""


class AIResponseError(AIProviderError):
    """Raised when an AI provider returns an invalid response."""
    