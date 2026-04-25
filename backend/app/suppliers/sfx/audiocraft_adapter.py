"""
AudioCraft SFX adapter.
"""

import asyncio
import time as _time
from typing import Any

import httpx

from app.schemas.supplier import SupplierTestResponse
from app.suppliers.base import SFXBaseSupplier


class AudioCraftSFXAdapter(SFXBaseSupplier):
    """Adapter for AudioCraft local sound effect generation service."""

    provider_name: str = "audiocraft_sfx"
    is_local: bool = True

    def __init__(self, base_url: str = "http://localhost:8201") -> None:
        self._base_url = base_url.rstrip("/")
        self._client = httpx.AsyncClient(base_url=self._base_url, timeout=300.0)

    async def generate_sfx(
        self,
        prompt: str,
        duration_sec: float = 3.0,
        **kwargs: Any,
    ) -> bytes:
        """Generate sound effects via AudioCraft API."""
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
            raise RuntimeError("AudioCraft SFX returned no audio data")
        return resp.content

    async def _poll_task(self, task_id: str) -> bytes:
        """Poll async task until completion."""
        import base64
        for _ in range(150):
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
                raise RuntimeError("AudioCraft SFX task completed but no audio data")
            elif status == "failed":
                raise RuntimeError(f"AudioCraft SFX task failed: {data.get('error', 'Unknown')}")
        raise TimeoutError(f"AudioCraft SFX task {task_id} timed out")

    async def test_connection(self) -> SupplierTestResponse:
        """Test connection to AudioCraft SFX service."""
        t0 = _time.monotonic()
        try:
            resp = await self._client.get("/health")
            resp.raise_for_status()
            latency = int((_time.monotonic() - t0) * 1000)
            return SupplierTestResponse(
                success=True, latency_ms=latency,
                response_preview="AudioCraft SFX reachable", error=None,
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
