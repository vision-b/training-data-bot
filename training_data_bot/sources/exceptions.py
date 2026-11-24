
"""Custom exceptions for the document loading system."""


class DocumentLoadError(Exception):
    """Raised when a document cannot be loaded."""


    def __init__(
        self,
        message: str,
        file_path: str | None = None,
        cause: Exception | None = None,
    ):
        super().__init__(message)
        self.file_path = file_path
        self.cause = cause


class SourceNotFoundError(DocumentLoadError):
    """Raised when a requested source does not exist."""


class UnsupportedDocumentTypeError(DocumentLoadError):
    """Raised when a document format is unsupported."""


class InvalidSourceError(DocumentLoadError):
    """Raised when a source is invalid or cannot be accessed."""
