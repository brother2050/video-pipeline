"""
ModelScope (DashScope) video generation adapter.
"""

import asyncio
import time as _time
from typing import Any

import httpx

from app.schemas.supplier import SupplierTestResponse
from app.suppliers.base import VideoBaseSupplier


class ModelScopeVideoAdapter(VideoBaseSupplier):
    """Adapter for Alibaba DashScope video generation (async task polling)."""

    provider_name: str = "modelscope_video"
    is_local: bool = False
    _API_URL: str = "https://dashscope.aliyuncs.com/api/v1/services/aigc/video-generation/video-synthesis"
    _TASK_URL: str = "https://dashscope.aliyuncs.com/api/v1/tasks"

    def __init__(self, api_key: str, model: str = "wanx-v1") -> None:
        self._api_key = api_key
        self._model = model
        self._client = httpx.AsyncClient(timeout=600.0)

    async def generate_video(
        self,
        prompt: str,
        reference_image: bytes | None = None,
        duration_seconds: float = 5.0,
        **kwargs: Any,
    ) -> bytes:
        """Generate video via DashScope async task API."""
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
            "X-DashScope-Async": "enable",
        }
        input_data: dict[str, Any] = {"prompt": prompt}
        if reference_image:
            import base64
            input_data["ref_image_url"] = f"data:image/png;base64,{base64.b64encode(reference_image).decode()}"

        payload: dict[str, Any] = {
            "model": self._model,
            "input": input_data,
            "parameters": {"duration": int(duration_seconds)},
        }
        payload.update(kwargs)

        resp = await self._client.post(self._API_URL, json=payload, headers=headers)
        resp.raise_for_status()
        task_data = resp.json()
        task_id = task_data.get("output", {}).get("task_id", "")

        # Poll for completion
        poll_headers = {"Authorization": f"Bearer {self._api_key}"}
        for _ in range(300):  # max 5 minutes
            await asyncio.sleep(2.0)
            poll_resp = await self._client.get(
                f"{self._TASK_URL}/{task_id}", headers=poll_headers,
            )
            poll_resp.raise_for_status()
            poll_data = poll_resp.json()
            status = poll_data.get("output", {}).get("task_status", "")
            if status == "SUCCEEDED":
                video_url = poll_data.get("output", {}).get("video_url", "")
                if video_url:
                    video_resp = await self._client.get(video_url)
                    video_resp.raise_for_status()
                    return video_resp.content
                results = poll_data.get("output", {}).get("results", [])
                if results:
                    url = results[0].get("url", "")
                    if url:
                        video_resp = await self._client.get(url)
                        video_resp.raise_for_status()
                        return video_resp.content
                raise RuntimeError("ModelScope video completed but no video URL")
            elif status == "FAILED":
                error_msg = poll_data.get("output", {}).get("message", "Unknown error")
                raise RuntimeError(f"ModelScope video task failed: {error_msg}")

        raise TimeoutError(f"ModelScope video task {task_id} timed out")

    async def test_connection(self) -> SupplierTestResponse:
        """Test connection."""
        t0 = _time.monotonic()
        try:
            headers = {"Authorization": f"Bearer {self._api_key}"}
            resp = await self._client.get(self._TASK_URL, headers=headers)
            latency = int((_time.monotonic() - t0) * 1000)
            return SupplierTestResponse(
                success=True, latency_ms=latency,
                response_preview="ModelScope video API reachable", error=None,
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
