
"""Loader for web pages and URLs."""

from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup

from training_data_bot.core.models import Document, DocumentType
from training_data_bot.sources.base import BaseLoader
from training_data_bot.sources.exceptions import (
    DocumentLoadError,
    InvalidSourceError,
)


class WebLoader(BaseLoader):
    """Downloads and extracts readable website content."""

    MAX_RESPONSE_SIZE = 10 * 1024 * 1024  # 10 MB

    def __init__(self, timeout: float = 20.0):
        super().__init__()

        self.timeout = timeout
        self.supported_formats = [DocumentType.URL]

    async def load_single(
        self,
        source: str,
        **kwargs
    ) -> Document:

        parsed = urlparse(source)

        if parsed.scheme not in ("http", "https") or not parsed.netloc:
            raise InvalidSourceError(
                f"Invalid URL: {source}",
                file_path=source,
            )

        try:
            async with httpx.AsyncClient(
                timeout=self.timeout,
                follow_redirects=True,
                headers={
                    "User-Agent": "TrainingDataBot/1.0"
                },
            ) as client:

                async with client.stream(
                    "GET",
                    source,
                ) as response:

                    response.raise_for_status()

                    content_type = response.headers.get(
                        "content-type", ""
                    ).lower()

                    if "text/html" not in content_type:
                        raise DocumentLoadError(
                            "URL does not return an HTML document",
                            file_path=source,
                        )

                    chunks = []
                    total_size = 0

                    async for chunk in response.aiter_bytes():
                        total_size += len(chunk)

                        if total_size > self.MAX_RESPONSE_SIZE:
                            raise DocumentLoadError(
                                "Web page exceeds the maximum allowed size",
                                file_path=source,
                            )

                        chunks.append(chunk)

            html = b"".join(chunks).decode(
                response.encoding or "utf-8",
                errors="replace",
            )

            content = self._extract_text(html)

            title = self._extract_title(html) or parsed.netloc

            return Document(
                title=title,
                content=content,
                source=source,
                doc_type=DocumentType.URL,
                word_count=len(content.split()),
                char_count=len(content),
            )

        except DocumentLoadError:
            raise

        except httpx.HTTPError as exc:
            raise DocumentLoadError(
                f"HTTP request failed for: {source}",
                file_path=source,
                cause=exc,
            ) from exc

        except Exception as exc:
            raise DocumentLoadError(
                f"Failed to load webpage: {source}",
                file_path=source,
                cause=exc,
            ) from exc

    @staticmethod
    def _extract_text(html: str) -> str:
        """Remove irrelevant elements and extract readable text."""

        soup = BeautifulSoup(html, "html.parser")

        for element in soup(
            ["script", "style", "noscript", "svg", "iframe"]
        ):
            element.decompose()

        main_content = soup.find("main") or soup.find("article") or soup.body

        if main_content is None:
            main_content = soup

        return main_content.get_text(
            separator="\n",
            strip=True,
        )

    @staticmethod
    def _extract_title(html: str) -> str | None:
        """Extract the webpage title."""

        soup = BeautifulSoup(html, "html.parser")

        if soup.title:
            return soup.title.get_text(strip=True)

        return None
