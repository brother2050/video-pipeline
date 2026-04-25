"""
Local sound effect library adapter.
"""

import os
import random
import time as _time
from pathlib import Path
from typing import Any

from app.schemas.supplier import SupplierTestResponse
from app.suppliers.base import SFXBaseSupplier


class SoundLibraryAdapter(SFXBaseSupplier):
    """Adapter for local sound effect file library."""

    provider_name: str = "sound_library"
    is_local: bool = True

    def __init__(self, library_path: str = "data/sfx") -> None:
        self._library_path = Path(library_path)
        self._index: dict[str, list[Path]] = {}
        self._build_index()

    def _build_index(self) -> None:
        """Build keyword index from sound library directory structure."""
        if not self._library_path.exists():
            return
        for audio_file in self._library_path.rglob("*.wav"):
            category = audio_file.parent.name.lower()
            if category not in self._index:
                self._index[category] = []
            self._index[category].append(audio_file)
        for audio_file in self._library_path.rglob("*.mp3"):
            category = audio_file.parent.name.lower()
            if category not in self._index:
                self._index[category] = []
            self._index[category].append(audio_file)

    def _search(self, prompt: str) -> Path | None:
        """Search library for a matching sound effect by keyword."""
        prompt_lower = prompt.lower()
        # Try exact category match
        for category, files in self._index.items():
            if category in prompt_lower or prompt_lower in category:
                return random.choice(files)
        # Try partial keyword match
        for category, files in self._index.items():
            for word in prompt_lower.split():
                if word in category:
                    return random.choice(files)
        # Fallback: return random file
        all_files: list[Path] = []
        for files in self._index.values():
            all_files.extend(files)
        return random.choice(all_files) if all_files else None

    async def generate_sfx(
        self,
        prompt: str,
        duration_sec: float = 3.0,
        **kwargs: Any,
    ) -> bytes:
        """Search and return a matching sound effect from the library."""
        match = self._search(prompt)
        if match is None:
            raise FileNotFoundError(f"No sound effect found for prompt: {prompt}")
        return match.read_bytes()

    async def test_connection(self) -> SupplierTestResponse:
        """Test by checking if library directory exists and has files."""
        t0 = _time.monotonic()
        try:
            total_files = sum(len(files) for files in self._index.values())
            latency = int((_time.monotonic() - t0) * 1000)
            if total_files > 0:
                return SupplierTestResponse(
                    success=True, latency_ms=latency,
                    response_preview=f"{total_files} sound effects indexed",
                    error=None,
                )
            return SupplierTestResponse(
                success=False, latency_ms=latency,
                response_preview=None,
                error=f"Sound library empty or not found at {self._library_path}",
            )
        except Exception as e:
            latency = int((_time.monotonic() - t0) * 1000)
            return SupplierTestResponse(
                success=False, latency_ms=latency,
                response_preview=None, error=str(e),
            )

    def list_categories(self) -> list[str]:
        """List all available sound categories."""
        return sorted(self._index.keys())

    def reload(self) -> None:
        """Reload the sound library index."""
        self._index.clear()
        self._build_index()
