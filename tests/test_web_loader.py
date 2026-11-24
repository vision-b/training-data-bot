
import asyncio
import pytest

from training_data_bot.sources.web_loader import WebLoader
from training_data_bot.sources.exceptions import InvalidSourceError
from training_data_bot.core.models import DocumentType


def test_web_loader_supported_formats():

    loader = WebLoader()

    assert loader.supported_formats == [DocumentType.URL]


def test_invalid_url():

    with pytest.raises(InvalidSourceError):
        asyncio.run(
            WebLoader().load_single("not-a-valid-url")
        )


def test_extract_text():

    html = """
    <html>
        <head><title>Example Page</title></head>
        <body>
            <h1>Hello World</h1>
            <script>secret_script()</script>
            <p>Welcome to Python.</p>
        </body>
    </html>
    """

    content = WebLoader._extract_text(html)

    assert "Hello World" in content
    assert "Welcome to Python." in content
    assert "secret_script" not in content


def test_extract_title():

    html = "<html><head><title>My Website</title></head></html>"

    title = WebLoader._extract_title(html)

    assert title == "My Website"
