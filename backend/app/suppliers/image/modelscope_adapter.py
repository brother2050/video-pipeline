"""
ModelScope (DashScope Wanx) image generation adapter.
"""

import asyncio
import time as _time
from typing import Any

import httpx

from app.schemas.supplier import SupplierTestResponse
from app.suppliers.base import ImageBaseSupplier


class ModelScopeImageAdapter(ImageBaseSupplier):
    """Adapter for Alibaba DashScope Wanx image generation (async task polling)."""

    provider_name: str = "modelscope_image"
    is_local: bool = False
    _API_URL: str = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis"
    _TASK_URL: str = "https://dashscope.aliyuncs.com/api/v1/tasks"

    def __init__(self, api_key: str, model: str = "wanx-v1") -> None:
        self._api_key = api_key
        self._model = model
        self._client = httpx.AsyncClient(timeout=300.0)

    async def generate_image(
        self,
        prompt: str,
        negative_prompt: str = "",
        width: int = 1024,
        height: int = 1024,
        num_images: int = 1,
        **kwargs: Any,
    ) -> list[bytes]:
        """Generate images via DashScope Wanx async task API."""
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
            "X-DashScope-Async": "enable",
        }
        payload: dict[str, Any] = {
            "model": self._model,
            "input": {"prompt": prompt},
            "parameters": {
                "n": num_images,
                "size": f"{width}*{height}",
            },
        }
        if negative_prompt:
            payload["input"]["negative_prompt"] = negative_prompt
        payload.update(kwargs)

        resp = await self._client.post(self._API_URL, json=payload, headers=headers)
        resp.raise_for_status()
        task_data = resp.json()
        task_id = task_data.get("output", {}).get("task_id", "")

        # Poll for completion
        poll_headers = {"Authorization": f"Bearer {self._api_key}"}
        for _ in range(120):  # max 2 minutes polling
            await asyncio.sleep(1.0)
            poll_resp = await self._client.get(
                f"{self._TASK_URL}/{task_id}", headers=poll_headers,
            )
            poll_resp.raise_for_status()
            poll_data = poll_resp.json()
            status = poll_data.get("output", {}).get("task_status", "")
            if status == "SUCCEEDED":
                results = poll_data.get("output", {}).get("results", [])
                images: list[bytes] = []
                for r in results:
                    url = r.get("url", "")
                    if url:
                        img_resp = await self._client.get(url)
                        img_resp.raise_for_status()
                        images.append(img_resp.content)
                return images
            elif status == "FAILED":
                error_msg = poll_data.get("output", {}).get("message", "Unknown error")
                raise RuntimeError(f"ModelScope image task failed: {error_msg}")

        raise TimeoutError(f"ModelScope image task {task_id} timed out")

    async def test_connection(self) -> SupplierTestResponse:
        """Test connection by submitting a minimal task."""
        t0 = _time.monotonic()
        try:
            headers = {
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
                "X-DashScope-Async": "enable",
            }
            payload: dict[str, Any] = {
                "model": self._model,
                "input": {"prompt": "test"},
                "parameters": {"n": 1, "size": "512*512"},
            }
            resp = await self._client.post(self._API_URL, json=payload, headers=headers)
            resp.raise_for_status()
            latency = int((_time.monotonic() - t0) * 1000)
            return SupplierTestResponse(
                success=True, latency_ms=latency,
                response_preview="ModelScope image API reachable", error=None,
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
