"""
AI 生成服务：调用供应商生成内容，包含 JSON 提取和校验重试。
"""

import json
import re
from typing import Any, TYPE_CHECKING

from app.schemas.enums import SupplierCapability
from app.exceptions import GenerationError

if TYPE_CHECKING:
    from app.suppliers.registry import SupplierRegistry


async def call_llm_for_json(
    registry: "SupplierRegistry",
    system_prompt: str,
    user_prompt: str,
    schema: dict[str, Any],
    max_retries: int = 3,
) -> dict[str, Any]:
    """
    调用 LLM 并确保返回有效 JSON。
    重试策略：解析失败 → 将错误信息反馈给 LLM → 重试。
    """
    from jsonschema import validate, ValidationError as JsonSchemaError
    from app.suppliers.base import LLMBaseSupplier

    messages: list[dict[str, str]] = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    last_error = ""
    for attempt in range(max_retries):
        # 每次重试都在 messages 里追加上次的错误信息
        enriched_messages = list(messages)
        if last_error:
            enriched_messages.append({
                "role": "user",
                "content": (
                    f"Your previous response was invalid. Error: {last_error}\n"
                    f"Your response was: {raw_response[:200]}\n"
                    f"Please fix and return ONLY a valid JSON object matching the schema. "
                    f"No markdown, no extra text, no trailing characters."
                )
            })
        
        supplier = await registry.get_with_fallback(SupplierCapability.LLM)
        # 类型断言：确保 supplier 是 LLMBaseSupplier
        from app.suppliers.base import LLMBaseSupplier
        assert isinstance(supplier, LLMBaseSupplier), f"Expected LLMBaseSupplier, got {type(supplier)}"
        
        # 使用合理的 token 限制，确保完整生成 JSON
        try:
            raw_response = await supplier.chat(
                messages=enriched_messages, 
                model="",
                max_tokens=8192,  # 使用合理的 token 限制
                schema=schema,
            )
        except Exception as e:
            # 如果是 token 限制错误，尝试更小的值
            if "400" in str(e) or "Bad Request" in str(e):
                raw_response = await supplier.chat(
                    messages=enriched_messages, 
                    model="",
                    max_tokens=4096,  # 回退到更小的值
                    schema=schema,
                )
            else:
                raise

        json_str = extract_json_from_response(raw_response)

        try:
            content = json.loads(json_str)
            validate(instance=content, schema=schema)
            return content
        except json.JSONDecodeError as e:
            # 检查是否是 JSON 不完整的问题
            if "Expecting" in str(e) or "Unterminated" in str(e):
                last_error = f"JSON 不完整: {e}。请生成完整的 JSON，确保所有括号都闭合。"
            else:
                last_error = f"JSON 解析失败: {e}"
            
            messages.append({"role": "assistant", "content": raw_response})
            messages.append({
                "role": "user",
                "content": f"{last_error}。请确保输出完整的、合法的 JSON，不要包含 markdown 标记或代码块。只输出纯 JSON。",
            })
        except JsonSchemaError as e:
            last_error = f"JSON Schema 校验失败: {e.message}"
            # 如果是缺少必需字段，给出更明确的提示
            if "'world_bible' is a required property" in e.message:
                error_msg = "缺少必需字段 'world_bible'。请确保使用英文字段名 'world_bible'（世界观描述，字符串类型）和 'characters'（角色数组，数组类型），不要使用中文字段名。"
            elif "'characters' is a required property" in e.message:
                error_msg = "缺少必需字段 'characters'。请确保使用英文字段名 'characters'（角色数组，数组类型），不要使用中文字段名。"
            elif "'role' is a required property" in e.message or "'name' is a required property" in e.message:
                error_msg = "角色对象缺少必需字段。每个角色必须包含6个英文字段：name, role, description, personality, appearance, arc。注意：字段名是 'role' 不是 'type' 或 '角色'。"
            elif "'world_bible' is not of type 'string'" in e.message:
                error_msg = "'world_bible' 字段类型错误。'world_bible' 必须是字符串类型（文本描述），不能是对象或数组。"
            elif "'characters' is not of type 'array'" in e.message:
                error_msg = "'characters' 字段类型错误。'characters' 必须是数组类型（角色列表），不能是对象或字符串。"
            elif "'name' is a required property" in e.message or "'description' is a required property" in e.message:
                error_msg = "角色对象缺少必需字段。角色对象必须使用英文字段名：name, role, description, personality, appearance, arc。不能使用中文字段名（如'名称'、'特征'、'威胁'等）。"
            elif "故事名称" in str(e.message) or "背景设定" in str(e.message) or "角色设定" in str(e.message):
                error_msg = "检测到中文字段名。必须使用英文字段名：'world_bible'（字符串）和 'characters'（数组）。角色字段必须使用：name, role, description, personality, appearance, arc。"
            else:
                error_msg = f"JSON 格式错误: {e.message} (路径: {'.'.join(str(p) for p in e.absolute_path)})"
            
            messages.append({"role": "assistant", "content": raw_response})
            messages.append({
                "role": "user",
                "content": f"{error_msg}。请修正后重新输出，只输出 JSON，使用英文字段名。",
            })

    raise GenerationError(f"LLM 在 {max_retries} 次尝试后仍无法输出有效 JSON。最后错误: {last_error}")


def extract_json_from_response(response: str) -> str:
    """
    从 LLM 响应中提取 JSON 字符串。
    处理以下情况：
    1. 纯 JSON
    2. markdown 代码块包裹的 JSON
    3. 前后有解释文字的 JSON
    """
    response = response.strip()

    # 尝试匹配 markdown 代码块
    code_block_pattern = r"```(?:json)?\s*\n?(.*?)\n?\s*```"
    match = re.search(code_block_pattern, response, re.DOTALL)
    if match:
        return match.group(1).strip()

    # 尝试找到第一个 { 和最后一个 }
    first_brace = response.find("{")
    last_brace = response.rfind("}")
    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        return response[first_brace:last_brace + 1]

    # 原样返回
    return response