"""
All supplier base class definitions.
"""

from abc import ABC, abstractmethod
from typing import Any, AsyncGenerator

from app.schemas.enums import SupplierCapability
from app.schemas.supplier import SupplierTestResponse
from app.exceptions import UnsupportedOperationError


class BaseSupplier(ABC):
    """Base class for all suppliers."""

    capability: SupplierCapability
    provider_name: str
    is_local: bool

    @abstractmethod
    async def test_connection(self) -> SupplierTestResponse:
        """Test supplier connectivity."""
        ...

    async def health_check(self) -> bool:
        """Quick health check via test_connection."""
        try:
            result = await self.test_connection()
            return result.success
        except Exception:
            return False


class LLMBaseSupplier(BaseSupplier):
    """Base class for LLM suppliers."""

    capability: SupplierCapability = SupplierCapability.LLM

    @abstractmethod
    async def chat(
        self,
        messages: list[dict[str, str]],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs: Any,
    ) -> str:
        ...

    @abstractmethod
    async def chat_stream(
        self,
        messages: list[dict[str, str]],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs: Any,
    ) -> AsyncGenerator[str, None]:
        ...


class ImageBaseSupplier(BaseSupplier):
    """Base class for image generation suppliers."""

    capability: SupplierCapability = SupplierCapability.IMAGE

    @abstractmethod
    async def generate_image(
        self,
        prompt: str,
        negative_prompt: str = "",
        width: int = 1024,
        height: int = 1024,
        num_images: int = 1,
        **kwargs: Any,
    ) -> list[bytes]:
        ...

    async def generate_image_to_image(
        self,
        prompt: str,
        init_image: bytes,
        negative_prompt: str = "",
        denoising_strength: float = 0.75,
        width: int = 1024,
        height: int = 1024,
        **kwargs: Any,
    ) -> list[bytes]:
        raise UnsupportedOperationError(f"{self.provider_name} does not support img2img")


class VideoBaseSupplier(BaseSupplier):
    """Base class for video generation suppliers."""

    capability: SupplierCapability = SupplierCapability.VIDEO

    @abstractmethod
    async def generate_video(
        self,
        prompt: str,
        reference_image: bytes | None = None,
        duration_seconds: float = 5.0,
        **kwargs: Any,
    ) -> bytes:
        ...


class TTSBaseSupplier(BaseSupplier):
    """Base class for TTS suppliers."""

    capability: SupplierCapability = SupplierCapability.TTS

    @abstractmethod
    async def synthesize(
        self,
        text: str,
        voice_id: str = "default",
        speed: float = 1.0,
        emotion: str = "neutral",
        **kwargs: Any,
    ) -> bytes:
        ...


class BGMBaseSupplier(BaseSupplier):
    """Base class for background music suppliers."""

    capability: SupplierCapability = SupplierCapability.BGM

    @abstractmethod
    async def generate_bgm(
        self,
        prompt: str,
        duration_sec: float = 60.0,
        **kwargs: Any,
    ) -> bytes:
        ...


class SFXBaseSupplier(BaseSupplier):
    """Base class for sound effect suppliers."""

    capability: SupplierCapability = SupplierCapability.SFX

    @abstractmethod
    async def generate_sfx(
        self,
        prompt: str,
        duration_sec: float = 3.0,
        **kwargs: Any,
    ) -> bytes:
        ...


class PostBaseSupplier(BaseSupplier):
    """Base class for post-production suppliers."""

    capability: SupplierCapability = SupplierCapability.POST

    @abstractmethod
    async def process(
        self,
        input_files: list[str],
        output_path: str,
        params: dict[str, Any],
        **kwargs: Any,
    ) -> str:
        ...
