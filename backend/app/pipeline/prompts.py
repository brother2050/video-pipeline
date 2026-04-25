"""
所有阶段的提示词模板。
"""

from typing import Any

from app.schemas.enums import StageType


# --- 阶段模板 ---

WORLDBUILDING_TEMPLATE = """你是专业的世界观架构师。根据以下信息构建完整的世界观和角色设定。

题材：{genre}
描述：{description}
目标集数：{target_episodes}

严格按以下 JSON Schema 输出，不要添加任何额外字段：
{schema}

参考示例格式：
{example}

直接输出 JSON，不要包含任何 markdown 标记、代码块或解释文字。"""


OUTLINE_TEMPLATE = """你是专业的编剧。基于以下世界观和角色，编写完整的剧情大纲。

世界观：
{world_bible}

角色：
{characters_json}

目标集数：{target_episodes}

严格按以下 JSON Schema 输出：
{schema}

参考示例格式：
{example}

直接输出 JSON，不要包含任何 markdown 标记或解释文字。"""


SCRIPT_TEMPLATE = """你是专业的编剧。基于以下大纲和世界观，编写详细的逐场景剧本。

世界观摘要：
{world_bible}

角色：
{characters_json}

大纲（当前集）：
{current_episode}

严格按以下 JSON Schema 输出：
{schema}

参考示例格式：
{example}

直接输出 JSON，不要包含任何 markdown 标记或解释文字。"""


STORYBOARD_TEMPLATE = """你是专业的分镜师。基于以下剧本场景，设计详细的分镜方案。

世界观：{world_bible}

角色外貌：
{character_appearances}

场景列表：
{scenes_json}

每个镜头必须包含 camera_angle、camera_movement、description、duration_sec、image_prompt（英文）、video_prompt（英文）、negative_prompt。

严格按以下 JSON Schema 输出：
{schema}

参考示例格式：
{example}

直接输出 JSON，不要包含任何 markdown 标记或解释文字。"""


AUDIO_TEMPLATE = """你是专业的音频设计师。基于以下剧本和角色信息，规划完整的音频方案。

角色信息：
{characters_json}

场景剧本：
{scenes_json}

你需要规划三类音频：
1. voice_cast: 角色配音方案（为每个角色分配 voice_id 和 voice_style）
2. dialogue_plan: 对白音频（从剧本中提取所有对白，标注时间点和情感）
3. bgm_plan: 背景音乐（为每个场景设计音乐风格和情绪）
4. sfx_plan: 音效（为每个场景设计环境音、动作音效等）

严格按以下 JSON Schema 输出：
{schema}

参考示例格式：
{example}

直接输出 JSON，不要包含任何 markdown 标记或解释文字。"""


# --- 示例数据 ---

WORLDBUILDING_EXAMPLE = """{
  "world_bible": "2157年，人类意识可上传至名为'深网'的虚拟世界...",
  "characters": [
    {
      "name": "林远",
      "role": "protagonist",
      "description": "深网安全局前探员",
      "personality": "冷静理性，内心矛盾",
      "appearance": "30岁男性，短发，左眼有疤痕",
      "arc": "从自我放逐到直面真相"
    }
  ]
}"""

OUTLINE_EXAMPLE = """{
  "episodes": [
    {
      "number": 1,
      "title": "深渊回响",
      "summary": "林远在废弃的数据中心发现一段异常信号...",
      "scene_names": ["废弃数据中心", "地下酒吧", "深网入口"]
    }
  ],
  "plot_arcs": [
    {
      "name": "真相之路",
      "description": "林远追查深网核心的秘密",
      "episodes_span": "1-8"
    }
  ]
}"""

SCRIPT_EXAMPLE = """{
  "scenes": [
    {
      "scene_number": 1,
      "episode_ref": 1,
      "location": "废弃数据中心",
      "time_of_day": "night",
      "characters_present": ["林远"],
      "action": "林远在布满灰尘的服务器机架间穿行...",
      "dialogue": [
        {"character": "林远", "line": "这不可能...", "emotion": "震惊", "action": "伸手触碰屏幕"}
      ],
      "visual_notes": "冷色调，蓝色和绿色的电子光芒"
    }
  ]
}"""

STORYBOARD_EXAMPLE = """{
  "shots": [
    {
      "shot_number": 1,
      "scene_ref": 1,
      "camera_angle": "low_angle",
      "camera_movement": "dolly_in",
      "description": "从地面仰视巨大的废弃服务器机架",
      "duration_sec": 4,
      "image_prompt": "massive abandoned server room, low angle shot, blue LED lights, cyberpunk, 8k",
      "video_prompt": "camera slowly dollies forward into massive abandoned server room, dust particles floating",
      "negative_prompt": "cartoon, anime, blurry, low quality"
    }
  ]
}"""

AUDIO_EXAMPLE = """{
  "voice_cast": {
    "林远": {"voice_id": "cosyvoice_male_01", "voice_style": "low calm deep", "supplier": "cosyvoice"}
  },
  "dialogue_plan": [
    {"scene_ref": 1, "character": "林远", "text": "这不可能...", "emotion": "surprise", "start_sec": 2.0, "voice_id": "cosyvoice_male_01"}
  ],
  "bgm_plan": [
    {"scene_ref": 1, "style": "dark ambient electronic", "mood": "mysterious tense", "duration_sec": 120}
  ],
  "sfx_plan": [
    {"scene_ref": 1, "description": "服务器嗡鸣声", "start_sec": 0, "duration_sec": 120, "category": "ambient"}
  ]
}"""


STAGE_TEMPLATES: dict[StageType, str] = {
    StageType.WORLDBUILDING: WORLDBUILDING_TEMPLATE,
    StageType.OUTLINE: OUTLINE_TEMPLATE,
    StageType.SCRIPT: SCRIPT_TEMPLATE,
    StageType.STORYBOARD: STORYBOARD_TEMPLATE,
    StageType.AUDIO: AUDIO_TEMPLATE,
}

STAGE_EXAMPLES: dict[StageType, str] = {
    StageType.WORLDBUILDING: WORLDBUILDING_EXAMPLE,
    StageType.OUTLINE: OUTLINE_EXAMPLE,
    StageType.SCRIPT: SCRIPT_EXAMPLE,
    StageType.STORYBOARD: STORYBOARD_EXAMPLE,
    StageType.AUDIO: AUDIO_EXAMPLE,
}
