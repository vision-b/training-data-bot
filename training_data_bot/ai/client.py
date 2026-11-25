
from typing import Optional
import os
import httpx
from dotenv import load_dotenv

from training_data_bot.ai.exceptions import AIProviderError, AIResponseError

# Load environment variables from the project's .env file
load_dotenv()


class AIClient:
    """HTTP AI client compatible with OpenAI-style chat completions."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://openrouter.ai/api/v1",
        model: str = "openrouter/free",
        timeout: float = 60.0,
    ):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout

    async def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> str:
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty.")

        if not self.api_key:
            raise AIProviderError(
                "OPENROUTER_API_KEY is not configured. "
                "Check your .env file."
            )

        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
        }

        if max_tokens is not None:
            payload["max_tokens"] = max_tokens

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                )

                response.raise_for_status()
                data = response.json()

            return data["choices"][0]["message"]["content"]

        except (httpx.HTTPError, KeyError, IndexError, TypeError) as exc:
            raise AIResponseError(f"AI request failed: {exc}") from exc
