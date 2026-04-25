"""
ChatTTS adapter.
"""

import time as _time
from typing import Any

import httpx

from app.schemas.supplier import SupplierTestResponse
from app.suppliers.base import TTSBaseSupplier


class ChatTTSAdapter(TTSBaseSupplier):
    """Adapter for ChatTTS local TTS service."""

    provider_name: str = "chattts"
    is_local: bool = True

    def __init__(self, base_url: str = "http://localhost:5001") -> None:
        self._base_url = base_url.rstrip("/")
        self._client = httpx.AsyncClient(base_url=self._base_url, timeout=120.0)

    async def synthesize(
        self,
        text: str,
        voice_id: str = "default",
        speed: float = 1.0,
        emotion: str = "neutral",
        **kwargs: Any,
    ) -> bytes:
        """Synthesize speech via ChatTTS API."""
        payload: dict[str, Any] = {
            "text": text,
            "speaker": voice_id,
            "speed": speed,
            "emotion": emotion,
        }
        payload.update(kwargs)
        resp = await self._client.post("/api/tts", json=payload)
        resp.raise_for_status()

        content_type = resp.headers.get("content-type", "")
        if "application/json" in content_type:
            data = resp.json()
            import base64
            audio_b64 = data.get("audio_base64", "")
            if audio_b64:
                return base64.b64decode(audio_b64)
            audio_url = data.get("audio_url", "")
            if audio_url:
                audio_resp = await self._client.get(audio_url)
                audio_resp.raise_for_status()
                return audio_resp.content
            raise RuntimeError("ChatTTS returned no audio data")
        return resp.content

    async def test_connection(self) -> SupplierTestResponse:
        """Test connection to ChatTTS service."""
        t0 = _time.monotonic()
        try:
            resp = await self._client.get("/health")
            resp.raise_for_status()
            latency = int((_time.monotonic() - t0) * 1000)
            return SupplierTestResponse(
                success=True, latency_ms=latency,
                response_preview="ChatTTS reachable", error=None,
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
