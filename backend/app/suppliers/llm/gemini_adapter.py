"""
Google Gemini LLM adapter.
"""

import json
import time as _time
from typing import Any, AsyncGenerator

import httpx

from app.schemas.supplier import SupplierTestResponse
from app.suppliers.base import LLMBaseSupplier


class GeminiAdapter(LLMBaseSupplier):
    """Adapter for Google Gemini API."""

    provider_name: str = "gemini"
    is_local: bool = False
    _BASE_URL: str = "https://generativelanguage.googleapis.com/v1beta"

    def __init__(self, api_key: str, model: str = "gemini-pro") -> None:
        self._api_key = api_key
        self._model = model
        self._client = httpx.AsyncClient(timeout=120.0)

    def _build_contents(self, messages: list[dict[str, str]]) -> list[dict[str, Any]]:
        """Convert OpenAI-style messages to Gemini format."""
        contents: list[dict[str, Any]] = []
        for msg in messages:
            role = msg.get("role", "user")
            gemini_role = "model" if role == "assistant" else "user"
            contents.append({"role": gemini_role, "parts": [{"text": msg.get("content", "")}]})
        return contents

    async def chat(
        self,
        messages: list[dict[str, str]],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs: Any,
    ) -> str:
        """Non-streaming chat via Gemini API."""
        url = f"{self._BASE_URL}/models/{model}:generateContent?key={self._api_key}"
        payload: dict[str, Any] = {
            "contents": self._build_contents(messages),
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
            },
        }
        resp = await self._client.post(url, json=payload)
        resp.raise_for_status()
        data = resp.json()
        candidates = data.get("candidates", [])
        if candidates:
            parts = candidates[0].get("content", {}).get("parts", [])
            return "".join(p.get("text", "") for p in parts)
        return ""

    async def chat_stream(
        self,
        messages: list[dict[str, str]],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs: Any,
    ) -> AsyncGenerator[str, None]:
        """Streaming chat via Gemini streamGenerateContent."""
        url = f"{self._BASE_URL}/models/{model}:streamGenerateContent?alt=sse&key={self._api_key}"
        payload: dict[str, Any] = {
            "contents": self._build_contents(messages),
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
            },
        }
        async with self._client.stream("POST", url, json=payload) as resp:
            resp.raise_for_status()
            async for line in resp.aiter_lines():
                if not line.startswith("data: "):
                    continue
                data_str = line[6:]
                try:
                    chunk = json.loads(data_str)
                    candidates = chunk.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        for p in parts:
                            text = p.get("text", "")
                            if text:
                                yield text
                except json.JSONDecodeError:
                    continue

    async def test_connection(self) -> SupplierTestResponse:
        """Test connection with a minimal request."""
        t0 = _time.monotonic()
        try:
            url = f"{self._BASE_URL}/models/{self._model}:generateContent?key={self._api_key}"
            payload: dict[str, Any] = {
                "contents": [{"role": "user", "parts": [{"text": "Hi"}]}],
                "generationConfig": {"maxOutputTokens": 10},
            }
            resp = await self._client.post(url, json=payload)
            resp.raise_for_status()
            latency = int((_time.monotonic() - t0) * 1000)
            return SupplierTestResponse(
                success=True, latency_ms=latency,
                response_preview="Gemini API reachable", error=None,
            )
        except Exception as e:
            latency = int((_time.monotonic() - t0) * 1000)
            return SupplierTestResponse(
                success=False, latency_ms=latency,
                response_preview=None, error=str(e),
            )

    async def close(self) -> None:
        """Close the HTTP client."""
        await self._client.aclose()
