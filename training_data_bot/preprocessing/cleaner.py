
import re


class TextCleaner:
    """Clean unnecessary characters and whitespace from text."""

    def clean(self, text: str) -> str:
        """Remove unnecessary whitespace while preserving paragraphs."""

        if not isinstance(text, str):
            raise TypeError("Input must be a string.")

        # Replace tabs and repeated spaces with a single space.
        text = re.sub(r"[ \t]+", " ", text)

        # Remove spaces at the beginning and end of lines.
        text = "\n".join(line.strip() for line in text.splitlines())

        # Replace three or more consecutive newlines with two.
        text = re.sub(r"\n{3,}", "\n\n", text)

        return text.strip()

    def remove_special_characters(
        self,
        text: str,
        keep: str = "",
    ) -> str:
        """Remove special characters while preserving letters and numbers."""

        if not isinstance(text, str):
            raise TypeError("Input must be a string.")

        pattern = rf"[^a-zA-Z0-9\s{re.escape(keep)}]"
        return re.sub(pattern, "", text)
