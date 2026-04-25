"""
所有枚举定义。
"""

from enum import Enum


class StageType(str, Enum):
    WORLDBUILDING = "worldbuilding"
    OUTLINE = "outline"
    SCRIPT = "script"
    STORYBOARD = "storyboard"
    KEYFRAME = "keyframe"
    VIDEO = "video"
    AUDIO = "audio"
    ROUGH_CUT = "rough_cut"
    FINAL_CUT = "final_cut"


class StageStatus(str, Enum):
    PENDING = "pending"
    READY = "ready"
    GENERATING = "generating"
    REVIEW = "review"
    APPROVED = "approved"
    LOCKED = "locked"


class ReviewAction(str, Enum):
    APPROVE = "approve"
    REJECT = "reject"
    REGENERATE = "regenerate"


class SupplierCapability(str, Enum):
    LLM = "llm"
    IMAGE = "image"
    VIDEO = "video"
    TTS = "tts"
    BGM = "bgm"
    SFX = "sfx"
    POST = "post"


class NodeStatus(str, Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    BUSY = "busy"
    ERROR = "error"


class FileType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    JSON_DATA = "json"
