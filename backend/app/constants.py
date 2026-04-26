"""
常量定义：所有可选值的枚举选项
"""

from app.schemas.enums import SupplierCapability


# 影视题材类型
GENRE_OPTIONS = [
    "科幻",
    "悬疑",
    "都市",
    "古装",
    "历史",
    "战争",
    "爱情",
    "喜剧",
    "恐怖",
    "动画",
    "纪录片",
    "其他",
]


# Supplier Capability 标签映射
CAPABILITY_LABELS: dict[SupplierCapability, str] = {
    SupplierCapability.LLM: "LLM",
    SupplierCapability.IMAGE: "图像",
    SupplierCapability.VIDEO: "视频",
    SupplierCapability.TTS: "TTS",
    SupplierCapability.BGM: "BGM",
    SupplierCapability.SFX: "音效",
    SupplierCapability.POST: "后期",
}


# Provider 选项（按能力分类）
PROVIDER_OPTIONS: dict[SupplierCapability, list[str]] = {
    SupplierCapability.LLM: [
        "ollama",
        "gemini",
        "glm",
        "qwen",
        "openai_compatible",
    ],
    SupplierCapability.IMAGE: [
        "comfyui",
        "sdwebui",
        "modelscope_image",
        "siliconflow_image",
    ],
    SupplierCapability.VIDEO: [
        "local_video",
        "modelscope_video",
        "siliconflow_video",
        "comfyui_video",
    ],
    SupplierCapability.TTS: [
        "cosyvoice",
        "chattts",
        "siliconflow_tts",
    ],
    SupplierCapability.BGM: [
        "musicgen",
        "external_bgm",
    ],
    SupplierCapability.SFX: [
        "audiocraft_sfx",
        "sound_library",
    ],
    SupplierCapability.POST: [
        "esrgan",
        "wav2lip",
        "ffmpeg",
    ],
}


# 视频分辨率选项
RESOLUTION_OPTIONS = [
    "1280x720",
    "1920x1080",
    "2560x1440",
    "3840x2160",
]


# 字幕位置选项
SUBTITLE_POSITION_OPTIONS = [
    "bottom_center",
    "bottom_left",
    "bottom_right",
    "top_center",
    "top_left",
    "top_right",
]


# 音频编码选项
AUDIO_CODEC_OPTIONS = [
    "aac",
    "mp3",
    "opus",
    "flac",
]


# 视频码率选项
VIDEO_BITRATE_OPTIONS = [
    "1M",
    "2M",
    "4M",
    "8M",
    "16M",
]


# 音频码率选项
AUDIO_BITRATE_OPTIONS = [
    "64k",
    "128k",
    "192k",
    "256k",
    "320k",
]


# 字体选项
FONT_OPTIONS = [
    "Noto Sans SC",
    "SimHei",
    "Microsoft YaHei",
    "Arial",
    "Helvetica",
]


# 字幕颜色选项
SUBTITLE_COLOR_OPTIONS = [
    "white",
    "yellow",
    "cyan",
    "black",
]