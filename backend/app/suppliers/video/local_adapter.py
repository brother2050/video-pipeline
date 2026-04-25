"""
Local video model adapter.
"""

import asyncio
import time as _time
from typing import Any

import httpx

from app.schemas.supplier import SupplierTestResponse
from app.suppliers.base import VideoBaseSupplier


class LocalVideoAdapter(VideoBaseSupplier):
    """Adapter for local video generation model service."""

    provider_name: str = "local_video"
    is_local: bool = True

    def __init__(self, base_url: str = "http://localhost:8199") -> None:
        self._base_url = base_url.rstrip("/")
        self._client = httpx.AsyncClient(base_url=self._base_url, timeout=1800.0)

    async def generate_video(
        self,
        prompt: str,
        reference_image: bytes | None = None,
        duration_seconds: float = 5.0,
        **kwargs: Any,
    ) -> bytes:
        """Generate video via local model service."""
        import base64
        payload: dict[str, Any] = {
            "prompt": prompt,
            "duration_seconds": duration_seconds,
        }
        if reference_image:
            payload["reference_image"] = base64.b64encode(reference_image).decode()
        payload.update(kwargs)

        resp = await self._client.post("/generate", json=payload)
        resp.raise_for_status()

        content_type = resp.headers.get("content-type", "")
        if "application/json" in content_type:
            data = resp.json()
            if "video_base64" in data:
                return base64.b64decode(data["video_base64"])
            video_url = data.get("video_url", "")
            if video_url:
                video_resp = await self._client.get(video_url)
                video_resp.raise_for_status()
                return video_resp.content
            task_id = data.get("task_id", "")
            if task_id:
                return await self._poll_task(task_id)
            raise RuntimeError("Local video service returned no video data")
        return resp.content

    async def _poll_task(self, task_id: str) -> bytes:
        """Poll async task until completion."""
        import base64
        for _ in range(900):  # max 30 minutes
            await asyncio.sleep(2.0)
            resp = await self._client.get(f"/task/{task_id}")
            resp.raise_for_status()
            data = resp.json()
            status = data.get("status", "")
            if status == "completed":
                if "video_base64" in data:
                    return base64.b64decode(data["video_base64"])
                video_url = data.get("video_url", "")
                if video_url:
                    video_resp = await self._client.get(video_url)
                    video_resp.raise_for_status()
                    return video_resp.content
                raise RuntimeError("Task completed but no video data")
            elif status == "failed":
                raise RuntimeError(f"Local video task failed: {data.get('error', 'Unknown')}")
        raise TimeoutError(f"Local video task {task_id} timed out")

    async def test_connection(self) -> SupplierTestResponse:
        """Test connection to local video service."""
        t0 = _time.monotonic()
        try:
            resp = await self._client.get("/health")
            resp.raise_for_status()
            latency = int((_time.monotonic() - t0) * 1000)
            return SupplierTestResponse(
                success=True, latency_ms=latency,
                response_preview="Local video service reachable", error=None,
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
