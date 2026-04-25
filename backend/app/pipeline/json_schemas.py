"""
所有阶段的 JSON Schema 定义。
用于校验 LLM 输出是否符合预期格式。
"""

from typing import Any

from app.schemas.enums import StageType


WORLDBUILDING_SCHEMA: dict[str, Any] = {
    "type": "object",
    "required": ["world_bible", "characters"],
    "properties": {
        "world_bible": {"type": "string", "minLength": 100},
        "characters": {
            "type": "array",
            "minItems": 1,
            "items": {
                "type": "object",
                "required": ["name", "role", "description", "personality", "appearance", "arc"],
                "properties": {
                    "name": {"type": "string"},
                    "role": {"type": "string", "enum": ["protagonist", "antagonist", "supporting", "minor"]},
                    "description": {"type": "string"},
                    "personality": {"type": "string"},
                    "appearance": {"type": "string"},
                    "arc": {"type": "string"},
                },
            },
        },
    },
}

OUTLINE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "required": ["episodes", "plot_arcs"],
    "properties": {
        "episodes": {
            "type": "array",
            "minItems": 1,
            "items": {
                "type": "object",
                "required": ["number", "title", "summary", "scene_names"],
                "properties": {
                    "number": {"type": "integer", "minimum": 1},
                    "title": {"type": "string", "minLength": 1},
                    "summary": {"type": "string", "minLength": 50},
                    "scene_names": {"type": "array", "items": {"type": "string"}, "minItems": 3},
                },
            },
        },
        "plot_arcs": {
            "type": "array",
            "minItems": 1,
            "items": {
                "type": "object",
                "required": ["name", "description", "episodes_span"],
                "properties": {
                    "name": {"type": "string"},
                    "description": {"type": "string"},
                    "episodes_span": {"type": "string"},
                },
            },
        },
    },
}

SCRIPT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "required": ["scenes"],
    "properties": {
        "scenes": {
            "type": "array",
            "minItems": 1,
            "items": {
                "type": "object",
                "required": ["scene_number", "episode_ref", "location", "time_of_day", "characters_present", "action", "dialogue"],
                "properties": {
                    "scene_number": {"type": "integer", "minimum": 1},
                    "episode_ref": {"type": "integer", "minimum": 1},
                    "location": {"type": "string"},
                    "time_of_day": {"type": "string", "enum": ["dawn", "morning", "noon", "afternoon", "dusk", "night"]},
                    "characters_present": {"type": "array", "items": {"type": "string"}},
                    "action": {"type": "string", "minLength": 30},
                    "dialogue": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "required": ["character", "line"],
                            "properties": {
                                "character": {"type": "string"},
                                "line": {"type": "string"},
                                "emotion": {"type": "string"},
                                "action": {"type": "string"},
                            },
                        },
                    },
                    "visual_notes": {"type": "string"},
                },
            },
        },
    },
}

STORYBOARD_SCHEMA: dict[str, Any] = {
    "type": "object",
    "required": ["shots"],
    "properties": {
        "shots": {
            "type": "array",
            "minItems": 1,
            "items": {
                "type": "object",
                "required": ["shot_number", "scene_ref", "camera_angle", "camera_movement", "description", "duration_sec", "image_prompt", "video_prompt"],
                "properties": {
                    "shot_number": {"type": "integer", "minimum": 1},
                    "scene_ref": {"type": "integer", "minimum": 1},
                    "camera_angle": {"type": "string", "enum": ["eye_level", "low_angle", "high_angle", "birds_eye", "dutch_angle", "over_shoulder", "close_up", "extreme_close_up"]},
                    "camera_movement": {"type": "string", "enum": ["static", "pan_left", "pan_right", "tilt_up", "tilt_down", "dolly_in", "dolly_out", "tracking", "crane", "handheld"]},
                    "description": {"type": "string"},
                    "duration_sec": {"type": "number", "minimum": 1, "maximum": 30},
                    "image_prompt": {"type": "string", "minLength": 20},
                    "video_prompt": {"type": "string", "minLength": 20},
                    "negative_prompt": {"type": "string", "default": ""},
                },
            },
        },
    },
}

AUDIO_SCHEMA: dict[str, Any] = {
    "type": "object",
    "required": ["voice_cast", "dialogue_plan", "bgm_plan", "sfx_plan"],
    "properties": {
        "voice_cast": {
            "type": "object",
            "additionalProperties": {
                "type": "object",
                "required": ["voice_id", "voice_style"],
                "properties": {
                    "voice_id": {"type": "string"},
                    "voice_style": {"type": "string"},
                    "supplier": {"type": "string"},
                },
            },
        },
        "dialogue_plan": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["scene_ref", "character", "text", "emotion", "start_sec"],
                "properties": {
                    "scene_ref": {"type": "integer"},
                    "character": {"type": "string"},
                    "text": {"type": "string"},
                    "emotion": {"type": "string", "enum": ["neutral", "happy", "sad", "angry", "fear", "surprise", "disgust"]},
                    "start_sec": {"type": "number"},
                    "voice_id": {"type": "string"},
                },
            },
        },
        "bgm_plan": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["scene_ref", "style", "mood", "duration_sec"],
                "properties": {
                    "scene_ref": {"type": "integer"},
                    "style": {"type": "string"},
                    "mood": {"type": "string"},
                    "duration_sec": {"type": "number"},
                    "reference_track": {"type": "string"},
                },
            },
        },
        "sfx_plan": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["scene_ref", "description", "start_sec", "duration_sec"],
                "properties": {
                    "scene_ref": {"type": "integer"},
                    "description": {"type": "string"},
                    "start_sec": {"type": "number"},
                    "duration_sec": {"type": "number"},
                    "category": {"type": "string", "enum": ["ambient", "impact", "foley", "transition", "music_sting"]},
                },
            },
        },
    },
}


STAGE_SCHEMAS: dict[StageType, dict[str, Any]] = {
    StageType.WORLDBUILDING: WORLDBUILDING_SCHEMA,
    StageType.OUTLINE: OUTLINE_SCHEMA,
    StageType.SCRIPT: SCRIPT_SCHEMA,
    StageType.STORYBOARD: STORYBOARD_SCHEMA,
    StageType.AUDIO: AUDIO_SCHEMA,
}
