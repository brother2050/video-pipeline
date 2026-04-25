"""
AI 生成服务：调用供应商生成内容，包含 JSON 提取和校验重试。
"""

import json
import re
from typing import Any

from app.schemas.enums import SupplierCapability
from app.exceptions import GenerationError


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

    messages: list[dict[str, str]] = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    last_error = ""
    for attempt in range(max_retries):
        supplier = await registry.get_with_fallback(SupplierCapability.LLM)
        raw_response = await supplier.chat(messages=messages, model="")

        json_str = extract_json_from_response(raw_response)

        try:
            content = json.loads(json_str)
            validate(instance=content, schema=schema)
            return content
        except json.JSONDecodeError as e:
            last_error = f"JSON 解析失败: {e}"
            messages.append({"role": "assistant", "content": raw_response})
            messages.append({
                "role": "user",
                "content": f"JSON 解析失败: {e}。请确保输出合法的 JSON，不要包含 markdown 标记或代码块。只输出纯 JSON。",
            })
        except JsonSchemaError as e:
            last_error = f"JSON Schema 校验失败: {e.message}"
            messages.append({"role": "assistant", "content": raw_response})
            messages.append({
                "role": "user",
                "content": f"JSON 格式错误: {e.message} (路径: {'.'.join(str(p) for p in e.absolute_path)})。请修正后重新输出，只输出 JSON。",
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
