"""LLM-powered character profile generation from novel text (文档C 节点2.3)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from novel_suite.core.prompt_template import safe_json_prompt

CHARACTER_SCHEMA = {
    "type": "object",
    "required": ["name", "identity", "appearance", "personality", "background", "motivation"],
    "properties": {
        "name": {"type": "string", "description": "角色姓名"},
        "identity": {"type": "string", "description": "身份/职业"},
        "appearance": {"type": "string", "description": "外貌描述（发色/瞳色/身高/体型/服饰）"},
        "personality": {"type": "string", "description": "性格特征"},
        "abilities": {"type": "string", "description": "能力/特长"},
        "background": {"type": "string", "description": "背景故事"},
        "motivation": {"type": "string", "description": "核心动机"},
        "role": {"type": "string", "enum": ["主角", "重要配角", "配角", "反派", "龙套"]},
        "age": {"type": "string"},
    },
}

SYSTEM_INSTRUCTION = """你是一个小说角色分析专家。从小说文本中提取角色信息，生成完整的角色设定卡。
注意：
1. 所有信息必须来自文本，不虚构
2. 如果某字段在文本中未提及，标注"未提及"
3. 外貌描述要具体（发色、瞳色、体型、服饰）"""


def extract_character(text: str, character_name: str) -> dict[str, Any]:
    """从小说文本中提取某个角色的设定（返回 prompt，由 Agent 调用 LLM）。"""
    prompt = safe_json_prompt(
        system_instruction=SYSTEM_INSTRUCTION,
        user_input=f"小说文本：\n{text[:3000]}\n\n请提取角色「{character_name}」的完整设定。",
        json_schema=json.dumps(CHARACTER_SCHEMA, ensure_ascii=False),
    )
    return {"prompt": prompt, "character_name": character_name}


def generate_cvdp_from_chapters(project: Path) -> list[dict[str, Any]]:
    """从已完成的章节准备 CVDP 角色设定生成任务。"""
    chapters_dir = project / "chapters"
    if not chapters_dir.is_dir():
        return []

    md_files = sorted(chapters_dir.glob("*.md"))
    if not md_files:
        return []

    combined_text = ""
    for f in md_files[:3]:
        if f.name.startswith("_"):
            continue
        try:
            combined_text += f.read_text(encoding="utf-8") + "\n"
        except OSError:
            continue

    return [
        {
            "source_chapters": len(md_files),
            "text_preview_len": len(combined_text),
            "note": "Run character_gen.extract_character() for each character",
        }
    ]
