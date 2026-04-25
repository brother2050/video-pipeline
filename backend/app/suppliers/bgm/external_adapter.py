"""
External BGM API adapter.
"""

import time as _time
from typing import Any

import httpx

from app.schemas.supplier import SupplierTestResponse
from app.suppliers.base import BGMBaseSupplier


class ExternalBGMAdapter(BGMBaseSupplier):
    """Adapter for external BGM generation API."""

    provider_name: str = "external_bgm"
    is_local: bool = False

    def __init__(self, base_url: str, api_key: str) -> None:
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            headers={"Authorization": f"Bearer {self._api_key}"},
            timeout=300.0,
        )

    async def generate_bgm(
        self,
        prompt: str,
        duration_sec: float = 60.0,
        **kwargs: Any,
    ) -> bytes:
        """Generate BGM via external API."""
        payload: dict[str, Any] = {
            "prompt": prompt,
            "duration": duration_sec,
        }
        payload.update(kwargs)
        resp = await self._client.post("/api/generate", json=payload)
        resp.raise_for_status()

        content_type = resp.headers.get("content-type", "")
        if "application/json" in content_type:
            data = resp.json()
            import base64
            audio_b64 = data.get("audio_base64", "")
            if audio_b64:
                return base64.b64decode(audio_b64)
            audio_url = data.get("audio_url", data.get("url", ""))
            if audio_url:
                audio_resp = await self._client.get(audio_url)
                audio_resp.raise_for_status()
                return audio_resp.content
            raise RuntimeError("External BGM API returned no audio data")
        return resp.content

    async def test_connection(self) -> SupplierTestResponse:
        """Test connection to external BGM API."""
        t0 = _time.monotonic()
        try:
            resp = await self._client.get("/api/health")
            resp.raise_for_status()
            latency = int((_time.monotonic() - t0) * 1000)
            return SupplierTestResponse(
                success=True, latency_ms=latency,
                response_preview="External BGM API reachable", error=None,
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
