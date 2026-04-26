"""
Supplier registry: manages all supplier instances by capability with priority scheduling and elastic fallback.
"""

import asyncio
from datetime import datetime, timezone
from typing import Any

from app.schemas.enums import SupplierCapability
from app.schemas.supplier import (
    CapabilityConfigResponse,
    SupplierSlot,
    SupplierTestResponse,
)
from app.suppliers.base import BaseSupplier
from app.exceptions import AllSuppliersExhausted


class SupplierHealth:
    """Health state for a single supplier instance."""

    def __init__(
        self,
        supplier: BaseSupplier,
        priority: int,
        is_local: bool,
        remote_timeout: int = 60,
        local_timeout: int = 300,
    ) -> None:
        self.supplier = supplier
        self.priority = priority
        self.is_local = is_local
        self.timeout = local_timeout if is_local else remote_timeout
        self.is_healthy: bool = True
        self.consecutive_failures: int = 0
        self.last_success: datetime | None = None
        self.last_failure: datetime | None = None
        self.last_error: str | None = None
        self.total_requests: int = 0
        self.total_failures: int = 0

    def mark_success(self) -> None:
        """Record a successful request."""
        self.is_healthy = True
        self.consecutive_failures = 0
        self.last_success = datetime.now(timezone.utc)
        self.total_requests += 1

    def mark_failure(self, error: str) -> None:
        """Record a failed request. After 3 consecutive failures, mark unhealthy."""
        self.consecutive_failures += 1
        self.total_failures += 1
        self.total_requests += 1
        self.last_failure = datetime.now(timezone.utc)
        self.last_error = error
        if self.consecutive_failures >= 3:
            self.is_healthy = False

    def to_dict(self) -> dict[str, Any]:
        """Serialize health state to dict."""
        return {
            "provider": self.supplier.provider_name,
            "capability": self.supplier.capability.value,
            "is_local": self.is_local,
            "priority": self.priority,
            "is_healthy": self.is_healthy,
            "consecutive_failures": self.consecutive_failures,
            "total_requests": self.total_requests,
            "total_failures": self.total_failures,
            "last_success": self.last_success.isoformat() if self.last_success else None,
            "last_failure": self.last_failure.isoformat() if self.last_failure else None,
            "last_error": self.last_error,
        }


class SupplierRegistry:
    """Central supplier registry with priority scheduling and elastic fallback."""

    def __init__(self) -> None:
        self._health: dict[str, SupplierHealth] = {}
        self._by_capability: dict[SupplierCapability, list[SupplierHealth]] = {}
        self._lock = asyncio.Lock()

    async def initialize(
        self,
        configs: list[CapabilityConfigResponse],
        supplier_factory: Any = None,
    ) -> None:
        """Create all supplier instances from configuration."""
        for config in configs:
            cap = config.capability
            health_list: list[SupplierHealth] = []
            for slot in config.suppliers:
                supplier = self._create_supplier(cap, slot, supplier_factory)
                if supplier:
                    h = SupplierHealth(
                        supplier=supplier,
                        priority=slot.priority,
                        is_local=slot.is_local,
                        remote_timeout=config.timeout_seconds,
                        local_timeout=config.local_timeout_seconds,
                    )
                    health_list.append(h)
                    key = f"{cap.value}:{slot.provider}"
                    self._health[key] = h
            health_list.sort(key=lambda x: x.priority)
            self._by_capability[cap] = health_list

    def _create_supplier(
        self,
        capability: SupplierCapability,
        slot: SupplierSlot,
        factory: Any = None,
    ) -> BaseSupplier | None:
        """Create a supplier instance from slot config."""
        if factory:
            return factory(capability, slot)

        if capability == SupplierCapability.LLM:
            if slot.provider == "ollama":
                from app.suppliers.llm.ollama_adapter import OllamaAdapter
                return OllamaAdapter(base_url=slot.base_url or "http://localhost:11434", model=slot.model)
            elif slot.provider == "gemini":
                from app.suppliers.llm.gemini_adapter import GeminiAdapter
                return GeminiAdapter(api_key=slot.api_key or "", model=slot.model)
            elif slot.provider == "glm":
                from app.suppliers.llm.glm_adapter import GLMAdapter
                return GLMAdapter(api_key=slot.api_key or "", model=slot.model)
            elif slot.provider == "qwen":
                from app.suppliers.llm.qwen_adapter import QwenAdapter
                return QwenAdapter(api_key=slot.api_key or "", model=slot.model)
            elif slot.provider == "paddle":
                from app.suppliers.llm.paddle_adapter import PaddleAdapter
                return PaddleAdapter(
                    base_url=slot.base_url or "",
                    api_key=slot.api_key or "",
                    model=slot.model
                )
            else:
                from app.suppliers.llm.openai_compatible import OpenAICompatibleAdapter
                return OpenAICompatibleAdapter(
                    base_url=slot.base_url or "",
                    api_key=slot.api_key or "",
                    provider_name=slot.provider,
                    is_local=slot.is_local,
                    model=slot.model
                )

        elif capability == SupplierCapability.IMAGE:
            if slot.provider == "comfyui":
                from app.suppliers.image.comfyui_adapter import ComfyUIAdapter
                return ComfyUIAdapter(base_url=slot.base_url or "http://localhost:8188")
            elif slot.provider == "sdwebui":
                from app.suppliers.image.sdwebui_adapter import SDWebUIAdapter
                return SDWebUIAdapter(base_url=slot.base_url or "http://localhost:7860")
            elif slot.provider == "modelscope_image":
                from app.suppliers.image.modelscope_adapter import ModelScopeImageAdapter
                return ModelScopeImageAdapter(api_key=slot.api_key or "", model=slot.model)
            else:
                from app.suppliers.image.siliconflow_adapter import SiliconFlowImageAdapter
                return SiliconFlowImageAdapter(
                    base_url=slot.base_url or "",
                    api_key=slot.api_key or "",
                    model=slot.model,
                )

        elif capability == SupplierCapability.VIDEO:
            if slot.provider == "local_video":
                from app.suppliers.video.local_adapter import LocalVideoAdapter
                return LocalVideoAdapter(base_url=slot.base_url or "http://localhost:8199")
            elif slot.provider == "modelscope_video":
                from app.suppliers.video.modelscope_adapter import ModelScopeVideoAdapter
                return ModelScopeVideoAdapter(api_key=slot.api_key or "", model=slot.model)
            else:
                from app.suppliers.video.siliconflow_adapter import SiliconFlowVideoAdapter
                return SiliconFlowVideoAdapter(
                    base_url=slot.base_url or "",
                    api_key=slot.api_key or "",
                    model=slot.model,
                )

        elif capability == SupplierCapability.TTS:
            if slot.provider == "cosyvoice":
                from app.suppliers.tts.cosyvoice_adapter import CosyVoiceAdapter
                return CosyVoiceAdapter(base_url=slot.base_url or "http://localhost:5000")
            elif slot.provider == "chattts":
                from app.suppliers.tts.chattts_adapter import ChatTTSAdapter
                return ChatTTSAdapter(base_url=slot.base_url or "http://localhost:5001")
            else:
                from app.suppliers.tts.siliconflow_adapter import SiliconFlowTTSAdapter
                return SiliconFlowTTSAdapter(
                    base_url=slot.base_url or "",
                    api_key=slot.api_key or "",
                )

        elif capability == SupplierCapability.BGM:
            if slot.provider == "musicgen":
                from app.suppliers.bgm.musicgen_adapter import MusicGenAdapter
                return MusicGenAdapter(base_url=slot.base_url or "http://localhost:8200")
            else:
                from app.suppliers.bgm.external_adapter import ExternalBGMAdapter
                return ExternalBGMAdapter(
                    base_url=slot.base_url or "",
                    api_key=slot.api_key or "",
                )

        elif capability == SupplierCapability.SFX:
            if slot.provider == "audiocraft_sfx":
                from app.suppliers.sfx.audiocraft_adapter import AudioCraftSFXAdapter
                return AudioCraftSFXAdapter(base_url=slot.base_url or "http://localhost:8201")
            else:
                from app.suppliers.sfx.library_adapter import SoundLibraryAdapter
                return SoundLibraryAdapter()

        elif capability == SupplierCapability.POST:
            if slot.provider == "esrgan":
                from app.suppliers.post.esrgan_adapter import ESRGANAdapter
                return ESRGANAdapter()
            elif slot.provider == "wav2lip":
                from app.suppliers.post.wav2lip_adapter import Wav2LipAdapter
                return Wav2LipAdapter()
            else:
                from app.suppliers.post.ffmpeg_adapter import FFmpegAdapter
                return FFmpegAdapter()

        return None

    def get(self, capability: SupplierCapability) -> BaseSupplier:
        """Get the highest-priority healthy supplier for a capability."""
        health_list = self._by_capability.get(capability, [])
        for h in health_list:
            if h.is_healthy:
                return h.supplier
        # All unhealthy, return highest priority anyway
        if health_list:
            return health_list[0].supplier
        raise AllSuppliersExhausted(capability.value, ["No suppliers configured"])

    async def get_with_fallback(self, capability: SupplierCapability) -> BaseSupplier:
        """Get supplier (async wrapper, reserved for future extension)."""
        return self.get(capability)

    async def execute(
        self,
        capability: SupplierCapability,
        method: str,
        timeout: int | None = None,
        **kwargs: Any,
    ) -> Any:
        """Core dispatch: try by priority, auto-fallback on failure."""
        health_list = self._by_capability.get(capability, [])
        errors: list[str] = []

        for h in health_list:
            effective_timeout = timeout or h.timeout
            try:
                coro = getattr(h.supplier, method)(**kwargs)
                result = await asyncio.wait_for(coro, timeout=effective_timeout)
                h.mark_success()
                return result
            except asyncio.TimeoutError:
                err = f"{h.supplier.provider_name} timed out ({effective_timeout}s)"
                h.mark_failure(err)
                errors.append(err)
            except ConnectionError as e:
                err = f"{h.supplier.provider_name} connection error: {e}"
                h.mark_failure(err)
                errors.append(err)
            except Exception as e:
                err = f"{h.supplier.provider_name} error: {e}"
                h.mark_failure(err)
                errors.append(err)

        raise AllSuppliersExhausted(capability.value, errors)

    async def test_supplier(
        self,
        capability: SupplierCapability,
        slot: SupplierSlot,
    ) -> SupplierTestResponse:
        """Test a specific supplier slot."""
        supplier = self._create_supplier(capability, slot)
        if supplier is None:
            return SupplierTestResponse(success=False, latency_ms=0, error="Cannot create supplier")
        return await supplier.test_connection()

    def get_all_status(self) -> dict[str, str]:
        """Return health status for all capabilities."""
        status: dict[str, str] = {}
        for cap, health_list in self._by_capability.items():
            healthy_count = sum(1 for h in health_list if h.is_healthy)
            total = len(health_list)
            if healthy_count == 0:
                status[cap.value] = "down"
            elif healthy_count < total:
                status[cap.value] = "degraded"
            else:
                status[cap.value] = "ok"
        return status

    def get_health_details(self) -> list[dict[str, Any]]:
        """Return detailed health info for each supplier."""
        return [h.to_dict() for h in self._health.values()]

    async def reload_config(
        self,
        configs: list[CapabilityConfigResponse],
        supplier_factory: Any = None,
    ) -> None:
        """Hot-reload configuration."""
        async with self._lock:
            self._health.clear()
            self._by_capability.clear()
            await self.initialize(configs, supplier_factory)