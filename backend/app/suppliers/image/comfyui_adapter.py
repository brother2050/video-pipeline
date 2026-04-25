"""
ComfyUI native API adapter.
Based on ComfyUI Universal Workflow Runner design.
Supports any custom workflow JSON, auto-analyzes node structure and injects parameters.
"""

import io
import json
import ssl
import time
import uuid
import urllib.request
import urllib.parse
from pathlib import Path
from typing import Any, Optional

from app.schemas.supplier import SupplierTestResponse
from app.suppliers.base import ImageBaseSupplier, VideoBaseSupplier
from app.suppliers.workflow_parser import WorkflowParser


class ComfyUIClient:
    """ComfyUI HTTP client (urllib-based, no external dependencies)."""

    MIME_MAP: dict[str, str] = {
        ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
        ".webp": "image/webp", ".gif": "image/gif", ".bmp": "image/bmp",
        ".mp4": "video/mp4", ".avi": "video/avi", ".mov": "video/quicktime",
    }

    def __init__(self, base_url: str) -> None:
        self.base = base_url.rstrip("/")
        self.client_id = str(uuid.uuid4())
        self._ssl_ctx = ssl.create_default_context()
        self._ssl_ctx.check_hostname = False
        self._ssl_ctx.verify_mode = ssl.CERT_NONE

    async def _req(self, method: str, path: str, data: Any = None, timeout: int = 30) -> Any:
        """Execute an HTTP request asynchronously via executor."""
        import asyncio
        url = f"{self.base}{path}"
        headers: dict[str, str] = {"Content-Type": "application/json"} if data else {}
        body = json.dumps(data).encode() if data is not None else None
        req = urllib.request.Request(url, data=body, headers=headers, method=method)

        def _do_request() -> Any:
            with urllib.request.urlopen(req, timeout=timeout, context=self._ssl_ctx) as r:
                return json.loads(r.read().decode())

        return await asyncio.get_event_loop().run_in_executor(None, _do_request)

    async def ping(self) -> bool:
        """Check if ComfyUI is reachable."""
        try:
            await self._req("GET", "/system_stats", timeout=10)
            return True
        except Exception:
            return False

    async def upload_image(self, file_bytes: bytes, filename: str, subfolder: str = "") -> str:
        """Upload image to ComfyUI input directory, return server-side filename."""
        import asyncio
        boundary = uuid.uuid4().hex
        body = io.BytesIO()
        ext = Path(filename).suffix.lower()
        mime = self.MIME_MAP.get(ext, "application/octet-stream")

        for key, val in [("subfolder", subfolder), ("type", "input"), ("overwrite", "true")]:
            body.write(f"--{boundary}\r\n".encode())
            body.write(f'Content-Disposition: form-data; name="{key}"\r\n\r\n'.encode())
            body.write(f"{val}\r\n".encode())

        body.write(f"--{boundary}\r\n".encode())
        body.write(f'Content-Disposition: form-data; name="image"; filename="{filename}"\r\n'.encode())
        body.write(f"Content-Type: {mime}\r\n\r\n".encode())
        body.write(file_bytes)
        body.write(b"\r\n")
        body.write(f"--{boundary}--\r\n".encode())

        raw = body.getvalue()
        content_type = f"multipart/form-data; boundary={boundary}"

        url = f"{self.base}/upload/image"
        req = urllib.request.Request(url, data=raw, method="POST")
        req.add_header("Content-Type", content_type)

        def _do_upload() -> Any:
            with urllib.request.urlopen(req, timeout=120, context=self._ssl_ctx) as r:
                return json.loads(r.read().decode())

        resp = await asyncio.get_event_loop().run_in_executor(None, _do_upload)
        return resp.get("name", filename)

    async def queue_prompt(self, workflow: dict[str, Any]) -> dict[str, Any]:
        """Submit a workflow prompt to ComfyUI."""
        payload = {"prompt": workflow, "client_id": self.client_id}
        return await self._req("POST", "/prompt", payload)

    async def get_history(self, prompt_id: str) -> dict[str, Any]:
        """Get execution history for a prompt."""
        return await self._req("GET", f"/history/{prompt_id}")

    async def wait_for_completion(
        self, prompt_id: str, timeout: int = 600, interval: float = 2.0,
    ) -> dict[str, Any]:
        """Poll until task completes or times out."""
        import asyncio
        start = time.monotonic()
        while time.monotonic() - start < timeout:
            try:
                hist = await self.get_history(prompt_id)
            except Exception:
                await asyncio.sleep(interval)
                continue
            if prompt_id in hist:
                entry = hist[prompt_id]
                st = entry.get("status", {})
                if st.get("completed") or st.get("status_str") == "success" or entry.get("outputs"):
                    return entry
                if st.get("status_str") == "error":
                    msgs = st.get("messages", [])
                    raise RuntimeError(f"ComfyUI execution error: {msgs}")
            await asyncio.sleep(interval)
        raise TimeoutError(f"ComfyUI task {prompt_id} timed out after {timeout}s")

    async def download_output(
        self, filename: str, subfolder: str = "", ftype: str = "output",
    ) -> bytes:
        """Download an output file from ComfyUI."""
        import asyncio
        params = urllib.parse.urlencode({"filename": filename, "subfolder": subfolder, "type": ftype})
        url = f"{self.base}/view?{params}"
        req = urllib.request.Request(url)

        def _do_download() -> bytes:
            with urllib.request.urlopen(req, timeout=120, context=self._ssl_ctx) as r:
                return r.read()

        return await asyncio.get_event_loop().run_in_executor(None, _do_download)

    @staticmethod
    def extract_outputs(entry: dict[str, Any]) -> list[dict[str, Any]]:
        """Extract output file list from history entry."""
        files: list[dict[str, Any]] = []
        for nid, out in entry.get("outputs", {}).items():
            for kind, label in [("images", "image"), ("gifs", "video"), ("videos", "video")]:
                for item in out.get(kind, []):
                    if isinstance(item, dict) and "filename" in item:
                        files.append({
                            "type": label, "filename": item["filename"],
                            "subfolder": item.get("subfolder", ""),
                            "ftype": item.get("type", "output"), "node": nid,
                        })
            for ek in ("filenames", "output"):
                for item in out.get(ek, []):
                    if isinstance(item, dict) and "filename" in item:
                        files.append({
                            "type": "file", "filename": item["filename"],
                            "subfolder": item.get("subfolder", ""),
                            "ftype": item.get("type", "output"), "node": nid,
                        })
        return files


class ComfyUIAdapter(ImageBaseSupplier):
    """ComfyUI image generation adapter."""

    provider_name: str = "comfyui"
    is_local: bool = True

    def __init__(
        self,
        base_url: str = "http://localhost:8188",
        workflow_template: dict[str, Any] | None = None,
    ) -> None:
        self._client = ComfyUIClient(base_url)
        self._workflow_template = workflow_template or self._default_txt2img_workflow()

    async def generate_image(
        self,
        prompt: str,
        negative_prompt: str = "",
        width: int = 1024,
        height: int = 1024,
        num_images: int = 1,
        steps: int = 30,
        cfg_scale: float = 7.0,
        seed: int = -1,
        checkpoint: str = "",
        **kwargs: Any,
    ) -> list[bytes]:
        """
        Universal image generation:
        1. Use WorkflowParser to analyze workflow template
        2. Inject prompts, dimensions, sampler params via apply_overrides
        3. Submit to ComfyUI and wait for completion
        4. Download all output images
        """
        parser = WorkflowParser(self._workflow_template)
        overrides: dict[str, Any] = {
            "positive": prompt,
            "negative": negative_prompt,
            "width": width,
            "height": height,
            "batch_size": num_images,
            "steps": steps,
            "cfg": cfg_scale,
            "seed": seed,
        }
        if checkpoint:
            overrides["checkpoint"] = checkpoint

        modified_workflow = parser.apply_overrides(overrides)
        result = await self._client.queue_prompt(modified_workflow)
        prompt_id = result.get("prompt_id", "")
        entry = await self._client.wait_for_completion(prompt_id)
        outputs = ComfyUIClient.extract_outputs(entry)

        image_bytes_list: list[bytes] = []
        for out in outputs:
            if out["type"] == "image":
                data = await self._client.download_output(
                    out["filename"], out["subfolder"], out["ftype"],
                )
                image_bytes_list.append(data)

        return image_bytes_list

    async def generate_with_reference_image(
        self,
        prompt: str,
        reference_image: bytes,
        reference_image_name: str = "ref.png",
        negative_prompt: str = "",
        width: int = 1024,
        height: int = 1024,
        steps: int = 30,
        cfg_scale: float = 7.0,
        seed: int = -1,
        **kwargs: Any,
    ) -> list[bytes]:
        """
        Image generation with reference image (img2img / ControlNet etc.):
        1. Upload reference image to ComfyUI
        2. Use WorkflowParser to auto-track image slots and inject
        """
        server_name = await self._client.upload_image(reference_image, reference_image_name)

        parser = WorkflowParser(self._workflow_template)
        overrides: dict[str, Any] = {
            "positive": prompt,
            "negative": negative_prompt,
            "width": width,
            "height": height,
            "steps": steps,
            "cfg": cfg_scale,
            "seed": seed,
            "image": server_name,
        }

        modified_workflow = parser.apply_overrides(overrides)
        result = await self._client.queue_prompt(modified_workflow)
        prompt_id = result.get("prompt_id", "")
        entry = await self._client.wait_for_completion(prompt_id)
        outputs = ComfyUIClient.extract_outputs(entry)

        image_bytes_list: list[bytes] = []
        for out in outputs:
            if out["type"] == "image":
                data = await self._client.download_output(
                    out["filename"], out["subfolder"], out["ftype"],
                )
                image_bytes_list.append(data)

        return image_bytes_list

    async def test_connection(self) -> SupplierTestResponse:
        """Test ComfyUI connectivity."""
        import time as _time
        t0 = _time.monotonic()
        ok = await self._client.ping()
        latency = int((_time.monotonic() - t0) * 1000)
        return SupplierTestResponse(
            success=ok, latency_ms=latency,
            response_preview="ComfyUI is running" if ok else None,
            error=None if ok else "Connection failed",
        )

    async def get_models(self) -> list[str]:
        """Get available checkpoint models."""
        data = await self._client._req("GET", "/object_info/CheckpointLoaderSimple")
        try:
            return data["CheckpointLoaderSimple"]["inputs"]["ckpt_name"][0]
        except (KeyError, IndexError):
            return []

    async def get_samplers(self) -> list[str]:
        """Get available sampler names."""
        data = await self._client._req("GET", "/object_info/KSampler")
        try:
            return data["KSampler"]["inputs"]["sampler_name"][0]
        except (KeyError, IndexError):
            return []

    async def analyze_workflow(self, workflow: dict[str, Any]) -> dict[str, Any]:
        """Analyze workflow structure, return node info for frontend."""
        parser = WorkflowParser(workflow)
        return parser.get_node_info()

    def _default_txt2img_workflow(self) -> dict[str, Any]:
        """Return a default txt2img workflow template."""
        return {
            "3": {"class_type": "KSampler", "inputs": {
                "seed": 0, "steps": 30, "cfg": 7.0, "sampler_name": "euler",
                "scheduler": "normal", "denoise": 1.0,
                "model": ["4", 0], "positive": ["6", 0], "negative": ["7", 0], "latent_image": ["5", 0],
            }},
            "4": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": "model.safetensors"}},
            "5": {"class_type": "EmptyLatentImage", "inputs": {"width": 1024, "height": 1024, "batch_size": 1}},
            "6": {"class_type": "CLIPTextEncode", "inputs": {"text": "POSITIVE_PROMPT", "clip": ["4", 1]}},
            "7": {"class_type": "CLIPTextEncode", "inputs": {"text": "NEGATIVE_PROMPT", "clip": ["4", 1]}},
            "8": {"class_type": "VAEDecode", "inputs": {"samples": ["3", 0], "vae": ["4", 2]}},
            "9": {"class_type": "SaveImage", "inputs": {"filename_prefix": "pipeline", "images": ["8", 0]}},
        }


class ComfyUIVideoAdapter(VideoBaseSupplier):
    """ComfyUI video generation adapter (reuses same client)."""

    provider_name: str = "comfyui_video"
    is_local: bool = True

    def __init__(
        self,
        base_url: str = "http://localhost:8188",
        workflow_template: dict[str, Any] | None = None,
    ) -> None:
        self._client = ComfyUIClient(base_url)
        self._workflow_template = workflow_template or {}

    async def generate_video(
        self,
        prompt: str,
        reference_image: bytes | None = None,
        duration_seconds: float = 5.0,
        fps: int = 24,
        width: int = 1280,
        height: int = 720,
        **kwargs: Any,
    ) -> bytes:
        """Generate video via ComfyUI workflow."""
        frames = int(duration_seconds * fps)
        parser = WorkflowParser(self._workflow_template)
        overrides: dict[str, Any] = {
            "positive": prompt,
            "width": width, "height": height,
            "frames": frames,
        }

        if reference_image:
            server_name = await self._client.upload_image(reference_image, "start_frame.png")
            overrides["start_image"] = server_name

        modified_workflow = parser.apply_overrides(overrides)
        result = await self._client.queue_prompt(modified_workflow)
        prompt_id = result.get("prompt_id", "")
        entry = await self._client.wait_for_completion(prompt_id, timeout=1800, interval=3.0)
        outputs = ComfyUIClient.extract_outputs(entry)

        for out in outputs:
            if out["type"] == "video":
                return await self._client.download_output(
                    out["filename"], out["subfolder"], out["ftype"],
                )
            if out["type"] == "image":
                return await self._client.download_output(
                    out["filename"], out["subfolder"], out["ftype"],
                )

        raise RuntimeError("No video or image output from ComfyUI")

    async def test_connection(self) -> SupplierTestResponse:
        """Test ComfyUI video adapter connectivity."""
        import time as _time
        t0 = _time.monotonic()
        ok = await self._client.ping()
        latency = int((_time.monotonic() - t0) * 1000)
        return SupplierTestResponse(
            success=ok, latency_ms=latency,
            response_preview="ComfyUI video ready" if ok else None,
            error=None if ok else "Connection failed",
        )
