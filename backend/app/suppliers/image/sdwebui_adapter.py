"""
SD WebUI native API adapter.
"""

import base64
import time as _time
from typing import Any

import httpx

from app.schemas.supplier import SupplierTestResponse
from app.suppliers.base import ImageBaseSupplier


class SDWebUIAdapter(ImageBaseSupplier):
    """Adapter for Stable Diffusion WebUI API."""

    provider_name: str = "sdwebui"
    is_local: bool = True

    def __init__(self, base_url: str = "http://localhost:7860") -> None:
        self._base_url = base_url.rstrip("/")
        self._client = httpx.AsyncClient(base_url=self._base_url, timeout=600.0)

    async def generate_image(
        self,
        prompt: str,
        negative_prompt: str = "",
        width: int = 1024,
        height: int = 1024,
        num_images: int = 1,
        steps: int = 30,
        cfg_scale: float = 7.0,
        sampler_name: str = "Euler a",
        seed: int = -1,
        **kwargs: Any,
    ) -> list[bytes]:
        """Generate images via SD WebUI txt2img API."""
        payload: dict[str, Any] = {
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "width": width,
            "height": height,
            "batch_size": num_images,
            "steps": steps,
            "cfg_scale": cfg_scale,
            "sampler_name": sampler_name,
            "seed": seed if seed >= 0 else -1,
        }
        resp = await self._client.post("/sdapi/v1/txt2img", json=payload)
        resp.raise_for_status()
        data = resp.json()
        images_b64: list[str] = data.get("images", [])
        return [base64.b64decode(img_b64) for img_b64 in images_b64]

    async def generate_image_to_image(
        self,
        prompt: str,
        init_image: bytes,
        negative_prompt: str = "",
        denoising_strength: float = 0.75,
        width: int = 1024,
        height: int = 1024,
        steps: int = 30,
        cfg_scale: float = 7.0,
        **kwargs: Any,
    ) -> list[bytes]:
        """Generate images via SD WebUI img2img API."""
        payload: dict[str, Any] = {
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "init_images": [base64.b64encode(init_image).decode()],
            "denoising_strength": denoising_strength,
            "width": width,
            "height": height,
            "steps": steps,
            "cfg_scale": cfg_scale,
        }
        resp = await self._client.post("/sdapi/v1/img2img", json=payload)
        resp.raise_for_status()
        data = resp.json()
        return [base64.b64decode(img) for img in data.get("images", [])]

    async def test_connection(self) -> SupplierTestResponse:
        """Test connection by listing available models."""
        t0 = _time.monotonic()
        try:
            resp = await self._client.get("/sdapi/v1/sd-models")
            resp.raise_for_status()
            models = resp.json()
            latency = int((_time.monotonic() - t0) * 1000)
            return SupplierTestResponse(
                success=True, latency_ms=latency,
                response_preview=f"{len(models)} models available",
                error=None,
            )
        except Exception as e:
            latency = int((_time.monotonic() - t0) * 1000)
            return SupplierTestResponse(
                success=False, latency_ms=latency,
                response_preview=None, error=str(e),
            )

    async def get_models(self) -> list[str]:
        """Get available SD models."""
        resp = await self._client.get("/sdapi/v1/sd-models")
        resp.raise_for_status()
        return [m["title"] for m in resp.json()]

    async def get_samplers(self) -> list[str]:
        """Get available samplers."""
        resp = await self._client.get("/sdapi/v1/samplers")
        resp.raise_for_status()
        return [s["name"] for s in resp.json()]

    async def get_progress(self) -> dict[str, Any]:
        """Get current generation progress."""
        resp = await self._client.get("/sdapi/v1/progress")
        resp.raise_for_status()
        return resp.json()

    async def close(self) -> None:
        """Close the HTTP client."""
        await self._client.aclose()
