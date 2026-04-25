"""
SiliconFlow video generation adapter.
"""

import asyncio
import time as _time
from typing import Any

import httpx

from app.schemas.supplier import SupplierTestResponse
from app.suppliers.base import VideoBaseSupplier


class SiliconFlowVideoAdapter(VideoBaseSupplier):
    """Adapter for SiliconFlow video generation API."""

    provider_name: str = "siliconflow_video"
    is_local: bool = False

    def __init__(self, base_url: str, api_key: str, model: str = "") -> None:
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._model = model
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            headers={"Authorization": f"Bearer {self._api_key}"},
            timeout=600.0,
        )

    async def generate_video(
        self,
        prompt: str,
        reference_image: bytes | None = None,
        duration_seconds: float = 5.0,
        **kwargs: Any,
    ) -> bytes:
        """Generate video via SiliconFlow API."""
        payload: dict[str, Any] = {
            "model": self._model or "tencent/HunyuanVideo",
            "prompt": prompt,
        }
        if reference_image:
            import base64
            payload["image"] = base64.b64encode(reference_image).decode()
        payload.update(kwargs)

        # Submit async task
        resp = await self._client.post("/video/submit", json=payload)
        resp.raise_for_status()
        task_data = resp.json()
        task_id = task_data.get("request_id", task_data.get("task_id", ""))

        # Poll for completion
        for _ in range(300):  # max 5 minutes
            await asyncio.sleep(2.0)
            poll_resp = await self._client.get(f"/video/status/{task_id}")
            poll_resp.raise_for_status()
            poll_data = poll_resp.json()
            status = poll_data.get("status", "")
            if status == "completed":
                video_url = poll_data.get("video_url", poll_data.get("output", {}).get("video_url", ""))
                if video_url:
                    video_resp = await self._client.get(video_url)
                    video_resp.raise_for_status()
                    return video_resp.content
                raise RuntimeError("SiliconFlow video completed but no URL returned")
            elif status == "failed":
                raise RuntimeError(f"SiliconFlow video task failed: {poll_data}")

        raise TimeoutError(f"SiliconFlow video task {task_id} timed out")

    async def test_connection(self) -> SupplierTestResponse:
        """Test connection."""
        t0 = _time.monotonic()
        try:
            resp = await self._client.get("/models")
            resp.raise_for_status()
            latency = int((_time.monotonic() - t0) * 1000)
            return SupplierTestResponse(
                success=True, latency_ms=latency,
                response_preview="SiliconFlow video API reachable", error=None,
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
