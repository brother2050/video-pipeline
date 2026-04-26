"""
PaddlePaddle (飞浆) LLM adapter.
Supports PaddlePaddle-based LLM models deployed locally or via API.
"""

import json
import time as _time
from typing import Any, AsyncGenerator

import httpx

from app.schemas.supplier import SupplierTestResponse
from app.suppliers.base import LLMBaseSupplier


class PaddleAdapter(LLMBaseSupplier):
    """Adapter for PaddlePaddle LLM models (OpenAI-compatible API)."""

    provider_name: str = "paddle"
    is_local: bool = False

    def __init__(
        self,
        base_url: str,
        api_key: str = "",
        model: str = "paddle-llm",
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._model = model
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            headers=headers,
            timeout=120.0,
        )

    async def chat(
        self,
        messages: list[dict[str, str]],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs: Any,
    ) -> str:
        """Non-streaming chat via PaddlePaddle API."""
        payload: dict[str, Any] = {
            "model": model or self._model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False,
        }
        payload.update(kwargs)
        resp = await self._client.post("/chat/completions", json=payload)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]

    async def chat_stream(
        self,
        messages: list[dict[str, str]],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs: Any,
    ) -> AsyncGenerator[str, None]:
        """Streaming chat via PaddlePaddle API (SSE)."""
        payload: dict[str, Any] = {
            "model": model or self._model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True,
        }
        payload.update(kwargs)
        async with self._client.stream("POST", "/chat/completions", json=payload) as resp:
            resp.raise_for_status()
            async for line in resp.aiter_lines():
                if not line.startswith("data: "):
                    continue
                data_str = line[6:]
                if data_str.strip() == "[DONE]":
                    break
                try:
                    chunk = json.loads(data_str)
                    delta = chunk.get("choices", [{}])[0].get("delta", {})
                    content = delta.get("content")
                    if content:
                        yield content
                except json.JSONDecodeError:
                    continue

    async def test_connection(self) -> SupplierTestResponse:
        """Test connection with a minimal chat request."""
        t0 = _time.monotonic()
        try:
            payload: dict[str, Any] = {
                "model": self._model,
                "messages": [{"role": "user", "content": "Hi"}],
                "max_tokens": 10,
            }
            resp = await self._client.post("/chat/completions", json=payload)
            resp.raise_for_status()
            data = resp.json()
            preview = data.get("choices", [{}])[0].get("message", {}).get("content", "")[:100]
            latency = int((_time.monotonic() - t0) * 1000)
            return SupplierTestResponse(
                success=True, latency_ms=latency,
                response_preview=preview, error=None,
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