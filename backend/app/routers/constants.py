"""
常量相关路由：提供所有可选值的枚举选项
"""

from fastapi import APIRouter

from app.schemas.common import APIResponse
from app.constants import (
    GENRE_OPTIONS,
    PROVIDER_OPTIONS,
    RESOLUTION_OPTIONS,
    SUBTITLE_POSITION_OPTIONS,
    AUDIO_CODEC_OPTIONS,
    VIDEO_BITRATE_OPTIONS,
    AUDIO_BITRATE_OPTIONS,
    FONT_OPTIONS,
    SUBTITLE_COLOR_OPTIONS,
    CAPABILITY_LABELS,
)
from app.schemas.enums import SupplierCapability

router = APIRouter()


@router.get("/constants/genres", response_model=APIResponse[list[str]])
async def get_genre_options() -> APIResponse[list[str]]:
    """获取影视题材类型选项"""
    return APIResponse(data=GENRE_OPTIONS)


@router.get("/constants/providers/{capability}", response_model=APIResponse[list[str]])
async def get_provider_options(capability: SupplierCapability) -> APIResponse[list[str]]:
    """获取指定能力的 Provider 选项"""
    return APIResponse(data=PROVIDER_OPTIONS.get(capability, []))


@router.get("/constants/resolutions", response_model=APIResponse[list[str]])
async def get_resolution_options() -> APIResponse[list[str]]:
    """获取视频分辨率选项"""
    return APIResponse(data=RESOLUTION_OPTIONS)


@router.get("/constants/subtitle-positions", response_model=APIResponse[list[str]])
async def get_subtitle_position_options() -> APIResponse[list[str]]:
    """获取字幕位置选项"""
    return APIResponse(data=SUBTITLE_POSITION_OPTIONS)


@router.get("/constants/audio-codecs", response_model=APIResponse[list[str]])
async def get_audio_codec_options() -> APIResponse[list[str]]:
    """获取音频编码选项"""
    return APIResponse(data=AUDIO_CODEC_OPTIONS)


@router.get("/constants/video-bitrates", response_model=APIResponse[list[str]])
async def get_video_bitrate_options() -> APIResponse[list[str]]:
    """获取视频码率选项"""
    return APIResponse(data=VIDEO_BITRATE_OPTIONS)


@router.get("/constants/audio-bitrates", response_model=APIResponse[list[str]])
async def get_audio_bitrate_options() -> APIResponse[list[str]]:
    """获取音频码率选项"""
    return APIResponse(data=AUDIO_BITRATE_OPTIONS)


@router.get("/constants/fonts", response_model=APIResponse[list[str]])
async def get_font_options() -> APIResponse[list[str]]:
    """获取字体选项"""
    return APIResponse(data=FONT_OPTIONS)


@router.get("/constants/subtitle-colors", response_model=APIResponse[list[str]])
async def get_subtitle_color_options() -> APIResponse[list[str]]:
    """获取字幕颜色选项"""
    return APIResponse(data=SUBTITLE_COLOR_OPTIONS)


@router.get("/constants/capability-labels", response_model=APIResponse[dict])
async def get_capability_labels() -> APIResponse[dict]:
    """获取 Supplier Capability 标签映射"""
    return APIResponse(data={cap.value: label for cap, label in CAPABILITY_LABELS.items()})


@router.get("/constants/all", response_model=APIResponse[dict])
async def get_all_constants() -> APIResponse[dict]:
    """获取所有常量选项"""
    return APIResponse(data={
        "genres": GENRE_OPTIONS,
        "providers": {cap.value: options for cap, options in PROVIDER_OPTIONS.items()},
        "capability_labels": {cap.value: label for cap, label in CAPABILITY_LABELS.items()},
        "resolutions": RESOLUTION_OPTIONS,
        "subtitle_positions": SUBTITLE_POSITION_OPTIONS,
        "audio_codecs": AUDIO_CODEC_OPTIONS,
        "video_bitrates": VIDEO_BITRATE_OPTIONS,
        "audio_bitrates": AUDIO_BITRATE_OPTIONS,
        "fonts": FONT_OPTIONS,
        "subtitle_colors": SUBTITLE_COLOR_OPTIONS,
    })