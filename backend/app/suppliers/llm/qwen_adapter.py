"""
Qwen (Tongyi Qianwen / DashScope) LLM adapter.
"""

import json
import time as _time
from typing import Any, AsyncGenerator

import httpx

from app.schemas.supplier import SupplierTestResponse
from app.suppliers.base import LLMBaseSupplier


class QwenAdapter(LLMBaseSupplier):
    """Adapter for Alibaba DashScope Qwen API (OpenAI-compatible mode)."""

    provider_name: str = "qwen"
    is_local: bool = False
    _BASE_URL: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"

    def __init__(self, api_key: str, model: str = "qwen-turbo") -> None:
        self._api_key = api_key
        self._model = model
        self._client = httpx.AsyncClient(
            base_url=self._BASE_URL,
            headers={"Authorization": f"Bearer {self._api_key}"},
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
        """Non-streaming chat via DashScope OpenAI-compatible API."""
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
        """Streaming chat via DashScope OpenAI-compatible API (SSE)."""
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
            latency = int((_time.monotonic() - t0) * 1000)
            return SupplierTestResponse(
                success=True, latency_ms=latency,
                response_preview="Qwen API reachable", error=None,
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
