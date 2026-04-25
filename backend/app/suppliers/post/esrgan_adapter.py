"""
ESRGAN super-resolution adapter.
"""

import asyncio
import os
import shutil
import time as _time
from typing import Any

from app.schemas.supplier import SupplierTestResponse
from app.suppliers.base import PostBaseSupplier


class ESRGANAdapter(PostBaseSupplier):
    """Adapter for ESRGAN image/video super-resolution."""

    provider_name: str = "esrgan"
    is_local: bool = True

    def __init__(self, command: str = "realesrgan-ncnn-vulkan") -> None:
        self._command = command

    async def process(
        self,
        input_files: list[str],
        output_path: str,
        params: dict[str, Any],
        **kwargs: Any,
    ) -> str:
        """Upscale images/video using ESRGAN."""
        if not input_files:
            raise ValueError("ESRGAN requires at least 1 input file")
        scale = params.get("scale", 4)
        model_name = params.get("model", "realesr-animevideov3")
        input_path = input_files[0]

        # For video: extract frames, upscale each, reassemble
        if input_path.lower().endswith((".mp4", ".avi", ".mov", ".mkv")):
            return await self._upscale_video(input_path, output_path, scale, model_name, params)

        # For image: direct upscale
        args = [
            "-i", input_path,
            "-o", output_path,
            "-s", str(scale),
            "-n", model_name,
        ]
        rc, _, stderr = await self._run_command(args)
        if rc != 0:
            raise RuntimeError(f"ESRGAN upscale failed: {stderr}")
        return output_path

    async def _upscale_video(
        self,
        input_path: str,
        output_path: str,
        scale: int,
        model_name: str,
        params: dict[str, Any],
    ) -> str:
        """Upscale video by extracting frames, upscaling, and reassembling."""
        import tempfile
        work_dir = tempfile.mkdtemp(prefix="esrgan_")
        frames_dir = os.path.join(work_dir, "frames")
        upscaled_dir = os.path.join(work_dir, "upscaled")
        os.makedirs(frames_dir)
        os.makedirs(upscaled_dir)

        # Extract frames
        extract_args = [
            "-y", "-i", input_path,
            os.path.join(frames_dir, "frame_%06d.png"),
        ]
        ffmpeg = params.get("ffmpeg_path", "ffmpeg")
        process = await asyncio.create_subprocess_exec(
            ffmpeg, *extract_args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        await process.communicate()

        # Upscale each frame
        frames = sorted(os.listdir(frames_dir))
        for frame in frames:
            frame_in = os.path.join(frames_dir, frame)
            frame_out = os.path.join(upscaled_dir, frame)
            args = ["-i", frame_in, "-o", frame_out, "-s", str(scale), "-n", model_name]
            rc, _, stderr = await self._run_command(args)
            if rc != 0:
                raise RuntimeError(f"ESRGAN frame upscale failed: {stderr}")

        # Reassemble video
        fps = params.get("fps", 24)
        assemble_args = [
            "-y", "-framerate", str(fps),
            "-i", os.path.join(upscaled_dir, "frame_%06d.png"),
            "-i", input_path,
            "-map", "0:v", "-map", "1:a?",
            "-c:v", "libx264", "-crf", "18",
            "-pix_fmt", "yuv420p",
            output_path,
        ]
        process = await asyncio.create_subprocess_exec(
            ffmpeg, *assemble_args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        _, stderr = await process.communicate()
        if process.returncode != 0:
            raise RuntimeError(f"ESRGAN video reassemble failed: {stderr.decode()}")

        # Cleanup
        shutil.rmtree(work_dir, ignore_errors=True)
        return output_path

    async def _run_command(self, args: list[str]) -> tuple[int, str, str]:
        """Execute ESRGAN command."""
        process = await asyncio.create_subprocess_exec(
            self._command, *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()
        return process.returncode, stdout.decode(), stderr.decode()

    async def test_connection(self) -> SupplierTestResponse:
        """Test by checking ESRGAN availability."""
        t0 = _time.monotonic()
        try:
            cmd_path = shutil.which(self._command)
            if cmd_path is None:
                raise FileNotFoundError(f"ESRGAN command not found: {self._command}")
            latency = int((_time.monotonic() - t0) * 1000)
            return SupplierTestResponse(
                success=True, latency_ms=latency,
                response_preview=f"ESRGAN available at {cmd_path}",
                error=None,
            )
        except Exception as e:
            latency = int((_time.monotonic() - t0) * 1000)
            return SupplierTestResponse(
                success=False, latency_ms=latency,
                response_preview=None, error=str(e),
            )
