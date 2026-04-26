"""
Ollama LLM adapter.
"""

import json
import logging
import re
import time as _time
from typing import Any, AsyncGenerator

import httpx

from app.schemas.supplier import SupplierTestResponse
from app.suppliers.base import LLMBaseSupplier


class OllamaAdapter(LLMBaseSupplier):
    """Adapter for Ollama local LLM service."""

    provider_name: str = "ollama"
    is_local: bool = True

    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama2") -> None:
        self._base_url = base_url.rstrip("/")
        self._client = httpx.AsyncClient(base_url=self._base_url, timeout=600.0)
        self._model = model

    async def chat(
        self,
        messages: list[dict[str, str]],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        schema: dict[str, Any] = {}, 
        **kwargs: Any,
    ) -> str:
        # 把调用从 chat() 改为 chat_stream()
        raw_response = ""
        async for chunk in self.chat_stream(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            schema=schema,
        ):
            raw_response += chunk
        # """Non-streaming chat via Ollama API."""
        # payload: dict[str, Any] = {
        #     "model": model or self._model,
        #     "messages": messages,
        #     "stream": False,
        #     "options": {"temperature": temperature, "num_predict": max_tokens},
        #     "format": schema,
        # }
        # payload.update(kwargs)
        # resp = await self._client.post("/api/chat", json=payload, timeout=600.0)
        # resp.raise_for_status()
        # data = resp.json()
        # return data.get("message", {}).get("content", "")
        return raw_response

    async def chat_stream(
        self,
        messages: list[dict[str, str]],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        schema: dict[str, Any] = {},
        **kwargs: Any,
    ) -> AsyncGenerator[str, None]:
        """Streaming chat via Ollama API."""
        payload: dict[str, Any] = {
            "model": model or self._model,
            "messages": messages,
            "stream": True,
            "options": {"temperature": temperature, "num_predict": max_tokens},
            "format": schema,
        }
        payload.update(kwargs)
        async with self._client.stream("POST", "/api/chat", json=payload) as resp:
            resp.raise_for_status()
            async for line in resp.aiter_lines():
                if not line.strip():
                    continue
                try:
                    chunk = json.loads(line)
                    content = chunk.get("message", {}).get("content")
                    if content:
                        yield content
                    if chunk.get("done"):
                        break
                except json.JSONDecodeError:
                    continue

    async def test_connection(self) -> SupplierTestResponse:
        """Test connection by listing available models."""
        t0 = _time.monotonic()
        try:
            resp = await self._client.get("/api/tags")
            resp.raise_for_status()
            data = resp.json()
            models = [m.get("name", "") for m in data.get("models", [])]
            latency = int((_time.monotonic() - t0) * 1000)
            return SupplierTestResponse(
                success=True, latency_ms=latency,
                response_preview=f"{len(models)} models: {', '.join(models[:3])}",
                error=None,
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
