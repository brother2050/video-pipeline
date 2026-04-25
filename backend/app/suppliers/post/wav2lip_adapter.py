"""
Wav2Lip lip-sync adapter.
"""

import asyncio
import os
import shutil
import time as _time
from typing import Any

from app.schemas.supplier import SupplierTestResponse
from app.suppliers.base import PostBaseSupplier


class Wav2LipAdapter(PostBaseSupplier):
    """Adapter for Wav2Lip lip-sync processing."""

    provider_name: str = "wav2lip"
    is_local: bool = True

    def __init__(self, command: str = "python", script_path: str = "wav2lip/inference.py") -> None:
        self._command = command
        self._script_path = script_path

    async def process(
        self,
        input_files: list[str],
        output_path: str,
        params: dict[str, Any],
        **kwargs: Any,
    ) -> str:
        """
        Generate lip-synced video.
        input_files: [video_file, audio_file]
        """
        if len(input_files) < 2:
            raise ValueError("Wav2Lip requires 2 input files: [video, audio]")
        video_file = input_files[0]
        audio_file = input_files[1]
        checkpoint = params.get("checkpoint", "wav2lip/checkpoints/wav2lip_gan.pth")
        resize_factor = params.get("resize_factor", 1)
        pad = params.get("pad", "0,10,0,0")

        args = [
            self._script_path,
            "--checkpoint_path", checkpoint,
            "--face", video_file,
            "--audio", audio_file,
            "--outfile", output_path,
            "--resize_factor", str(resize_factor),
            "--pads", pad,
        ]

        process = await asyncio.create_subprocess_exec(
            self._command, *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()
        if process.returncode != 0:
            raise RuntimeError(f"Wav2Lip failed: {stderr.decode()}")
        if not os.path.exists(output_path):
            raise RuntimeError(f"Wav2Lip output not found: {output_path}")
        return output_path

    async def test_connection(self) -> SupplierTestResponse:
        """Test by checking Wav2Lip script availability."""
        t0 = _time.monotonic()
        try:
            if not os.path.exists(self._script_path):
                raise FileNotFoundError(f"Wav2Lip script not found: {self._script_path}")
            python_path = shutil.which(self._command)
            if python_path is None:
                raise FileNotFoundError(f"Python not found: {self._command}")
            latency = int((_time.monotonic() - t0) * 1000)
            return SupplierTestResponse(
                success=True, latency_ms=latency,
                response_preview=f"Wav2Lip ready at {self._script_path}",
                error=None,
            )
        except Exception as e:
            latency = int((_time.monotonic() - t0) * 1000)
            return SupplierTestResponse(
                success=False, latency_ms=latency,
                response_preview=None, error=str(e),
            )
