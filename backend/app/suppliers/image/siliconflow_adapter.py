"""
SiliconFlow image generation adapter.
"""

import time as _time
from typing import Any

import httpx

from app.schemas.supplier import SupplierTestResponse
from app.suppliers.base import ImageBaseSupplier


class SiliconFlowImageAdapter(ImageBaseSupplier):
    """Adapter for SiliconFlow image generation API."""

    provider_name: str = "siliconflow_image"
    is_local: bool = False

    def __init__(self, base_url: str, api_key: str, model: str = "") -> None:
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._model = model
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            headers={"Authorization": f"Bearer {self._api_key}"},
            timeout=300.0,
        )

    async def generate_image(
        self,
        prompt: str,
        negative_prompt: str = "",
        width: int = 1024,
        height: int = 1024,
        num_images: int = 1,
        **kwargs: Any,
    ) -> list[bytes]:
        """Generate images via SiliconFlow API."""
        payload: dict[str, Any] = {
            "model": self._model or "stabilityai/stable-diffusion-xl-base-1.0",
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "image_size": f"{width}x{height}",
            "batch_size": num_images,
        }
        payload.update(kwargs)
        resp = await self._client.post("/images/generations", json=payload)
        resp.raise_for_status()
        data = resp.json()
        images: list[bytes] = []
        for item in data.get("images", data.get("data", [])):
            url = item.get("url", "")
            if url:
                img_resp = await self._client.get(url)
                img_resp.raise_for_status()
                images.append(img_resp.content)
            elif "b64_json" in item:
                import base64
                images.append(base64.b64decode(item["b64_json"]))
        return images

    async def test_connection(self) -> SupplierTestResponse:
        """Test connection by generating a small image."""
        t0 = _time.monotonic()
        try:
            payload: dict[str, Any] = {
                "model": self._model or "stabilityai/stable-diffusion-xl-base-1.0",
                "prompt": "test",
                "image_size": "512x512",
                "batch_size": 1,
            }
            resp = await self._client.post("/images/generations", json=payload)
            resp.raise_for_status()
            latency = int((_time.monotonic() - t0) * 1000)
            return SupplierTestResponse(
                success=True, latency_ms=latency,
                response_preview="SiliconFlow image API reachable", error=None,
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
