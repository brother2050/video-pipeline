"""
MusicGen BGM adapter.
"""

import asyncio
import time as _time
from typing import Any

import httpx

from app.schemas.supplier import SupplierTestResponse
from app.suppliers.base import BGMBaseSupplier


class MusicGenAdapter(BGMBaseSupplier):
    """Adapter for MusicGen local music generation service."""

    provider_name: str = "musicgen"
    is_local: bool = True

    def __init__(self, base_url: str = "http://localhost:8200") -> None:
        self._base_url = base_url.rstrip("/")
        self._client = httpx.AsyncClient(base_url=self._base_url, timeout=600.0)

    async def generate_bgm(
        self,
        prompt: str,
        duration_sec: float = 60.0,
        **kwargs: Any,
    ) -> bytes:
        """Generate background music via MusicGen API."""
        payload: dict[str, Any] = {
            "prompt": prompt,
            "duration": duration_sec,
        }
        payload.update(kwargs)
        resp = await self._client.post("/generate", json=payload)
        resp.raise_for_status()

        content_type = resp.headers.get("content-type", "")
        if "application/json" in content_type:
            data = resp.json()
            import base64
            audio_b64 = data.get("audio_base64", "")
            if audio_b64:
                return base64.b64decode(audio_b64)
            task_id = data.get("task_id", "")
            if task_id:
                return await self._poll_task(task_id)
            raise RuntimeError("MusicGen returned no audio data")
        return resp.content

    async def _poll_task(self, task_id: str) -> bytes:
        """Poll async task until completion."""
        import base64
        for _ in range(300):
            await asyncio.sleep(2.0)
            resp = await self._client.get(f"/task/{task_id}")
            resp.raise_for_status()
            data = resp.json()
            status = data.get("status", "")
            if status == "completed":
                audio_b64 = data.get("audio_base64", "")
                if audio_b64:
                    return base64.b64decode(audio_b64)
                audio_url = data.get("audio_url", "")
                if audio_url:
                    audio_resp = await self._client.get(audio_url)
                    audio_resp.raise_for_status()
                    return audio_resp.content
                raise RuntimeError("MusicGen task completed but no audio data")
            elif status == "failed":
                raise RuntimeError(f"MusicGen task failed: {data.get('error', 'Unknown')}")
        raise TimeoutError(f"MusicGen task {task_id} timed out")

    async def test_connection(self) -> SupplierTestResponse:
        """Test connection to MusicGen service."""
        t0 = _time.monotonic()
        try:
            resp = await self._client.get("/health")
            resp.raise_for_status()
            latency = int((_time.monotonic() - t0) * 1000)
            return SupplierTestResponse(
                success=True, latency_ms=latency,
                response_preview="MusicGen reachable", error=None,
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
