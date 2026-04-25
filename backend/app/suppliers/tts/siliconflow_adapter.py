"""
SiliconFlow TTS adapter.
"""

import time as _time
from typing import Any

import httpx

from app.schemas.supplier import SupplierTestResponse
from app.suppliers.base import TTSBaseSupplier


class SiliconFlowTTSAdapter(TTSBaseSupplier):
    """Adapter for SiliconFlow TTS API."""

    provider_name: str = "siliconflow_tts"
    is_local: bool = False

    def __init__(self, base_url: str, api_key: str) -> None:
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            headers={"Authorization": f"Bearer {self._api_key}"},
            timeout=120.0,
        )

    async def synthesize(
        self,
        text: str,
        voice_id: str = "default",
        speed: float = 1.0,
        emotion: str = "neutral",
        **kwargs: Any,
    ) -> bytes:
        """Synthesize speech via SiliconFlow TTS API."""
        payload: dict[str, Any] = {
            "model": "FunAudioLLM/CosyVoice2-0.5B",
            "input": {"text": text},
            "voice": voice_id,
            "speed": speed,
        }
        payload.update(kwargs)
        resp = await self._client.post("/audio/speech", json=payload)
        resp.raise_for_status()
        return resp.content

    async def test_connection(self) -> SupplierTestResponse:
        """Test connection with a minimal synthesis request."""
        t0 = _time.monotonic()
        try:
            payload: dict[str, Any] = {
                "model": "FunAudioLLM/CosyVoice2-0.5B",
                "input": {"text": "test"},
                "voice": "default",
            }
            resp = await self._client.post("/audio/speech", json=payload)
            resp.raise_for_status()
            latency = int((_time.monotonic() - t0) * 1000)
            return SupplierTestResponse(
                success=True, latency_ms=latency,
                response_preview="SiliconFlow TTS reachable", error=None,
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
