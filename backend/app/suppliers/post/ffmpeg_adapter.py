"""
FFmpeg post-production adapter.
"""

import asyncio
import os
import shutil
import time as _time
from typing import Any

from app.schemas.supplier import SupplierTestResponse
from app.suppliers.base import PostBaseSupplier


class FFmpegAdapter(PostBaseSupplier):
    """Adapter for FFmpeg-based post-production processing."""

    provider_name: str = "ffmpeg"
    is_local: bool = True

    def __init__(self, ffmpeg_path: str = "ffmpeg") -> None:
        self._ffmpeg = ffmpeg_path

    async def process(
        self,
        input_files: list[str],
        output_path: str,
        params: dict[str, Any],
        **kwargs: Any,
    ) -> str:
        """
        Process files with FFmpeg.
        Supported operations: concat, audio_mix, merge, color_grade,
        subtitle, rough_cut, final_cut.
        """
        operation = params.get("operation", "concat")
        handler = getattr(self, f"_op_{operation}", None)
        if handler is None:
            raise ValueError(f"Unsupported FFmpeg operation: {operation}")
        return await handler(input_files, output_path, params)

    async def _run_ffmpeg(self, args: list[str]) -> tuple[int, str, str]:
        """Execute FFmpeg and return (returncode, stdout, stderr)."""
        process = await asyncio.create_subprocess_exec(
            self._ffmpeg, *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()
        return process.returncode, stdout.decode(), stderr.decode()

    async def _op_concat(
        self, input_files: list[str], output_path: str, params: dict[str, Any],
    ) -> str:
        """Concatenate video files."""
        if len(input_files) < 2:
            raise ValueError("Concat requires at least 2 input files")
        list_file = output_path + ".list.txt"
        with open(list_file, "w") as f:
            for path in input_files:
                f.write(f"file '{os.path.abspath(path)}'\n")
        args = ["-y", "-f", "concat", "-safe", "0", "-i", list_file, "-c", "copy", output_path]
        rc, _, stderr = await self._run_ffmpeg(args)
        os.unlink(list_file)
        if rc != 0:
            raise RuntimeError(f"FFmpeg concat failed: {stderr}")
        return output_path

    async def _op_audio_mix(
        self, input_files: list[str], output_path: str, params: dict[str, Any],
    ) -> str:
        """Mix audio tracks with video."""
        if len(input_files) < 2:
            raise ValueError("Audio mix requires at least 2 input files (video + audio)")
        video_file = input_files[0]
        audio_file = input_files[1]
        audio_volume = params.get("audio_volume", 0.3)
        args = [
            "-y", "-i", video_file, "-i", audio_file,
            "-filter_complex", f"[1:a]volume={audio_volume}[a1];[0:a][a1]amix=inputs=2:duration=first[aout]",
            "-map", "0:v", "-map", "[aout]", "-c:v", "copy", output_path,
        ]
        rc, _, stderr = await self._run_ffmpeg(args)
        if rc != 0:
            raise RuntimeError(f"FFmpeg audio_mix failed: {stderr}")
        return output_path

    async def _op_merge(
        self, input_files: list[str], output_path: str, params: dict[str, Any],
    ) -> str:
        """Merge video and audio into single file."""
        if len(input_files) < 2:
            raise ValueError("Merge requires at least 2 input files")
        args = ["-y", "-i", input_files[0], "-i", input_files[1], "-c:v", "copy", "-c:a", "aac", output_path]
        rc, _, stderr = await self._run_ffmpeg(args)
        if rc != 0:
            raise RuntimeError(f"FFmpeg merge failed: {stderr}")
        return output_path

    async def _op_color_grade(
        self, input_files: list[str], output_path: str, params: dict[str, Any],
    ) -> str:
        """Apply color grading via LUT or filter."""
        if not input_files:
            raise ValueError("Color grade requires at least 1 input file")
        lut_file = params.get("lut_file", "")
        brightness = params.get("brightness", 0)
        contrast = params.get("contrast", 1)
        saturation = params.get("saturation", 1)
        if lut_file and os.path.exists(lut_file):
            vf = f"lut3d={lut_file}"
        else:
            vf = f"eq=brightness={brightness}:contrast={contrast}:saturation={saturation}"
        args = ["-y", "-i", input_files[0], "-vf", vf, "-c:a", "copy", output_path]
        rc, _, stderr = await self._run_ffmpeg(args)
        if rc != 0:
            raise RuntimeError(f"FFmpeg color_grade failed: {stderr}")
        return output_path

    async def _op_subtitle(
        self, input_files: list[str], output_path: str, params: dict[str, Any],
    ) -> str:
        """Burn subtitles into video."""
        if not input_files:
            raise ValueError("Subtitle requires at least 1 input file")
        subtitle_file = params.get("subtitle_file", input_files[1] if len(input_files) > 1 else "")
        if not subtitle_file:
            raise ValueError("No subtitle file specified")
        font_size = params.get("font_size", 24)
        font_color = params.get("font_color", "white")
        args = [
            "-y", "-i", input_files[0],
            "-vf", f"subtitles={subtitle_file}:force_style='FontSize={font_size},PrimaryColour={font_color}'",
            "-c:a", "copy", output_path,
        ]
        rc, _, stderr = await self._run_ffmpeg(args)
        if rc != 0:
            raise RuntimeError(f"FFmpeg subtitle failed: {stderr}")
        return output_path

    async def _op_rough_cut(
        self, input_files: list[str], output_path: str, params: dict[str, Any],
    ) -> str:
        """Create rough cut with trim and basic transitions."""
        if not input_files:
            raise ValueError("Rough cut requires at least 1 input file")
        start_time = params.get("start_time", "00:00:00")
        end_time = params.get("end_time", "")
        args = ["-y", "-i", input_files[0], "-ss", start_time]
        if end_time:
            args.extend(["-to", end_time])
        args.extend(["-c", "copy", output_path])
        rc, _, stderr = await self._run_ffmpeg(args)
        if rc != 0:
            raise RuntimeError(f"FFmpeg rough_cut failed: {stderr}")
        return output_path

    async def _op_final_cut(
        self, input_files: list[str], output_path: str, params: dict[str, Any],
    ) -> str:
        """Final cut with re-encoding and quality settings."""
        if not input_files:
            raise ValueError("Final cut requires at least 1 input file")
        crf = params.get("crf", 18)
        preset = params.get("preset", "slow")
        args = [
            "-y", "-i", input_files[0],
            "-c:v", "libx264", "-crf", str(crf), "-preset", preset,
            "-c:a", "aac", "-b:a", "192k",
            output_path,
        ]
        rc, _, stderr = await self._run_ffmpeg(args)
        if rc != 0:
            raise RuntimeError(f"FFmpeg final_cut failed: {stderr}")
        return output_path

    async def test_connection(self) -> SupplierTestResponse:
        """Test by checking FFmpeg availability."""
        t0 = _time.monotonic()
        try:
            ffmpeg_path = shutil.which(self._ffmpeg)
            if ffmpeg_path is None:
                raise FileNotFoundError(f"FFmpeg not found: {self._ffmpeg}")
            process = await asyncio.create_subprocess_exec(
                self._ffmpeg, "-version",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, _ = await process.communicate()
            version_line = stdout.decode().split("\n")[0] if stdout else "unknown"
            latency = int((_time.monotonic() - t0) * 1000)
            return SupplierTestResponse(
                success=True, latency_ms=latency,
                response_preview=version_line, error=None,
            )
        except Exception as e:
            latency = int((_time.monotonic() - t0) * 1000)
            return SupplierTestResponse(
                success=False, latency_ms=latency,
                response_preview=None, error=str(e),
            )
