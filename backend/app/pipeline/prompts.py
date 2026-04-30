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
请生成 {target_episodes} 集完整的大纲，每集都要有独立的标题、摘要和场景名称列表。

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

完整大纲（{episode_count}集）：
{current_episode}

请为所有 {episode_count} 集编写完整的剧本，每集都要有多个场景，每个场景都要有详细的对白和动作描述。

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
      "summary": "林远在废弃的数据中心发现一段异常信号，追踪线索至地下酒吧，最终找到深网入口...",
      "scene_names": ["废弃数据中心", "地下酒吧", "深网入口"]
    },
    {
      "number": 2,
      "title": "迷雾重重",
      "summary": "林远进入深网后遭遇神秘黑客袭击，在虚拟空间中展开追逐战...",
      "scene_names": ["深网入口", "虚拟街道", "黑客据点"]
    },
    {
      "number": 3,
      "title": "记忆碎片",
      "summary": "林远发现袭击者竟然是自己曾经的搭档，开始调查真相...",
      "scene_names": ["安全局档案室", "虚拟记忆空间", "旧日公寓"]
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
      "action": "林远在布满灰尘的服务器机架间穿行，突然发现一个闪烁的信号灯...",
      "dialogue": [
        {"character": "林远", "line": "这不可能...这个信号来自深网核心...", "emotion": "震惊", "action": "伸手触碰屏幕"}
      ],
      "visual_notes": "冷色调，蓝色和绿色的电子光芒"
    },
    {
      "scene_number": 2,
      "episode_ref": 1,
      "location": "地下酒吧",
      "time_of_day": "night",
      "characters_present": ["林远", "神秘黑客"],
      "action": "林远在酒吧角落等待接头人，一个戴着面具的黑客走过来...",
      "dialogue": [
        {"character": "神秘黑客", "line": "你找的东西很危险，林远。", "emotion": "警告", "action": "压低声音"}
      ],
      "visual_notes": "昏暗的灯光，霓虹灯闪烁"
    },
    {
      "scene_number": 3,
      "episode_ref": 2,
      "location": "深网入口",
      "time_of_day": "dawn",
      "characters_present": ["林远", "神秘黑客"],
      "action": "两人进入深网入口，周围是虚拟的数字世界...",
      "dialogue": [
        {"character": "林远", "line": "这就是深网...比传说中还要壮观。", "emotion": "震撼", "action": "环顾四周"}
      ],
      "visual_notes": "虚拟世界，数字化的城市景观"
    },
    {
      "scene_number": 4,
      "episode_ref": 2,
      "location": "虚拟街道",
      "time_of_day": "afternoon",
      "characters_present": ["林远", "神秘黑客"],
      "action": "在虚拟街道上，突然出现一群追踪者...",
      "dialogue": [
        {"character": "神秘黑客", "line": "快跑！他们来了！", "emotion": "紧张", "action": "拉着林远奔跑"}
      ],
      "visual_notes": "快速移动的镜头，紧张的追逐场面"
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