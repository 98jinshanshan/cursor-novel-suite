"""Snowflake method — 5-step progressive outline generation (文档C 节点2.2)."""

from __future__ import annotations

from typing import Any

from novel_suite.core.prompt_template import safe_prompt

SYSTEM_INSTRUCTION = """你是一位专业网络小说架构师。请按照「雪花法」逐步创作小说大纲。
每步独立调用，上一步的输出作为下一步的输入。"""

SNOWFLAKE_STEPS = [
    {
        "name": "一句话故事",
        "instruction": "用 15 字以内概括一个完整的故事核心（主角+困境+转变）。\n格式：一个[主角描述]的[故事类型]故事",
        "output_example": "一个废柴少年在末日觉醒系统的逆袭故事",
    },
    {
        "name": "一段摘要",
        "instruction": "将一句话故事扩展为 5 行以内的故事摘要。包含：主角身份、核心冲突、关键转折、结局暗示。",
        "output_example": "林墨在末日废土觉醒了「万物合成系统」，从无人问津的拾荒者一步步成长为人类最后的希望...",
    },
    {
        "name": "一页大纲",
        "instruction": "扩展为完整的一页大纲。包含：\n1. 主角设定（姓名、身份、金手指）\n2. 核心反派/障碍\n3. 三幕结构（每幕 3-5 个关键事件）\n4. 核心爽点设计",
    },
    {
        "name": "章节蓝图",
        "instruction": "扩展为 50-100 章的章节蓝图。每章包含：章节名、核心事件、爽点标记。\n输出格式：Markdown 列表。",
    },
]


def run_snowflake(topic: str, genre: str = "通用", target_chapters: int = 50) -> dict[str, Any]:
    """执行完整的雪花法 4 步大纲生成（返回每步 prompt，由 Agent 调用 LLM 填充）。"""
    results: dict[str, Any] = {}
    current_context = f"题材：{topic}，类型：{genre}，目标章节数：{target_chapters}"

    for step in SNOWFLAKE_STEPS:
        prompt = safe_prompt(
            system_instruction=f"{SYSTEM_INSTRUCTION}\n\n当前步骤：{step['name']}\n{step['instruction']}",
            user_input=current_context,
        )
        results[step["name"]] = {
            "prompt": prompt,
            "instruction": step["instruction"],
        }

    results["topic"] = topic
    results["genre"] = genre
    results["target_chapters"] = target_chapters
    return results


def format_snowflake_output(results: dict[str, Any]) -> str:
    """将雪花法结果格式化为可读的大纲文档。"""
    lines = [f"# {results.get('topic', 'Untitled')} — 雪花法大纲", ""]
    for step in SNOWFLAKE_STEPS:
        name = step["name"]
        lines.append(f"## {name}")
        lines.append("")
        block = results.get(name)
        if isinstance(block, dict) and block.get("prompt"):
            lines.append(block["prompt"])
        else:
            lines.append(step["instruction"])
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"
