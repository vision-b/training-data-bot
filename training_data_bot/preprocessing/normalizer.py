
class TextNormalizer:
    """Standardize text formatting."""

    def normalize(self, text: str) -> str:
        """Normalize line endings and Unicode text."""

        if not isinstance(text, str):
            raise TypeError("Input must be a string.")

        import unicodedata

        # Standardize Unicode characters.
        text = unicodedata.normalize("NFC", text)

        # Standardize Windows and old Mac line endings.
        text = text.replace("\r\n", "\n")
        text = text.replace("\r", "\n")

        return text
