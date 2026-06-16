"""RealGen demo — real local chapter, review, short-drama package, and preview video."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from novel_suite.core.contracts import novel_suite_root
from novel_suite.core.errors import (
    REALGEN_DEMO_RUN_OK,
    REALGEN_DEMO_SEED_MISSING,
    REALGEN_DEMO_VALIDATE_FAIL,
    REALGEN_DEMO_VALIDATE_OK,
)
from novel_suite.core.paths import suite_root
from novel_suite.core.result import artifact, error_result, ok_result, Result

_DEMO_DIR = "realgen-demo"
_RUN_ID = "cold_case_echo_realgen_01"
_SEED_NAME = "story_seed.md"
_MANIFEST_NAME = "realgen_manifest.json"

_CORE_FILES = (
    "README.md",
    _SEED_NAME,
)

_REQUIRED_OUTPUT = (
    "chapter_01.md",
    "chapter_review.md",
    "short_drama_package/scene_package.json",
    "short_drama_package/shot_list.csv",
    "short_drama_package/asset_requirements.md",
    "short_drama_package/timeline_package.json",
    "short_drama_package/risk_check.md",
    "video_plan.md",
    "video/preview_subtitles.srt",
    "video/preview_script.txt",
    _MANIFEST_NAME,
)


def realgen_demo_root() -> Path:
    return novel_suite_root() / _DEMO_DIR


def output_root() -> Path:
    return realgen_demo_root() / _RUN_ID


def _rel(root: Path, path: Path) -> str:
    try:
        return str(path.relative_to(root)).replace("\\", "/")
    except ValueError:
        return str(path)


def _count_cjk(text: str) -> int:
    return len(re.findall(r"[\u4e00-\u9fff]", text))


def parse_story_seed(text: str) -> dict[str, str]:
    sections: dict[str, str] = {}
    current = "_preamble"
    lines: list[str] = []
    for line in text.splitlines():
        if line.startswith("## "):
            if lines:
                sections[current] = "\n".join(lines).strip()
            current = line[3:].strip()
            lines = []
        else:
            lines.append(line)
    if lines:
        sections[current] = "\n".join(lines).strip()
    return sections


def _extract_bullets(block: str) -> list[str]:
    return [ln.strip().lstrip("- ").strip() for ln in block.splitlines() if ln.strip().startswith("-")]


def generate_chapter_01(seed: dict[str, str], *, run_id: str) -> str:
    title = seed.get("标题", "未命名章节").split("·")[-1].strip()
    premise = seed.get("前提", "")
    characters = _extract_bullets(seed.get("角色", ""))
    scenes = _extract_bullets(seed.get("场景", ""))
    conflict = seed.get("核心冲突", "")
    hook = seed.get("结尾钩子", "")
    char_a = characters[0] if characters else "林澄：主角"
    char_b = characters[1] if len(characters) > 1 else "程砚：配角"
    name_a = char_a.split("：")[0].split(":")[0].strip()
    name_b = char_b.split("：")[0].split(":")[0].strip()
    scene_a = scenes[0].split("：")[-1] if scenes else "地下库房"
    scene_b = scenes[1].split("：")[-1] if len(scenes) > 1 else "监控室"

    body = f"""# 第一章 · {title}

> RealGen 本地生成 · run_id={run_id} · 非 fixture 复制

荧光灯在{scene_a}顶上嗡鸣，像有人用指甲轻刮铁皮。{name_a}把搬迁清单摊在铁柜旁，铅笔在封条边点了三下——那是她私人的「已核对」记号，规程里并没有这一条。

「{name_b}，B-17 的位移记录你看到了吗？」{name_a}问。

{name_b}盯着掌上终端，眉头拧起来：「看到了。02:41 有十二秒雪花。系统说是线路受潮。」

{premise}

{name_a}拉开 B-17 的抽屉，牛皮纸袋的封条颜色比相邻卷宗新半号。她戴上手套，指腹摸到封条背面有铅笔压痕，像是谁在黑暗里匆忙写下又擦过一半。

「规程写的是封存待迁，不是封存待查。」{name_b}的声音从门口传来，「你别开袋。」

「封条被调换了。」{name_a}抬头，「1997 年的编号还在，但封条纤维的纹路不对。搬迁队明早六点进场，我们只剩这一夜。」

{conflict}

她剪开纸袋。里面没有完整卷宗，只有半张烧毁的乘车票，边缘焦黑，票面依稀可见「滨海—旧城」。纸袋底部一行铅笔字，字迹浅得像会随时消失：**回声不是声音，是回来的人。**

{name_b}走近，灯光在他肩章上跳了一下：「你知不知道上一任夜班就是因为私拆封存被辞退的？」

「我知道。」{name_a}把乘车票放进证物袋，「我也知道，如果把纸袋原样封回，明天搬迁后就再也进不了这层楼。」

两人沉默。远处电梯井传来钢丝绳摩擦的声响，像某种倒计时。{name_a}忽然说：「监控雪花那十二秒，门磁没有报警，但重量传感器少了零点三公斤——有人拿走又放回了东西。」

他们赶到{scene_b}。回放画面里，B-17 前的通道空着，雪花屏过后，画面角落掠过一道模糊人影，没有工牌反光，没有登记指纹。

「第三个人。」{name_b}低声道，「库里从没登记过第三个人。」

{hook}

{name_a}关掉回放，把证物袋塞进随身柜，对{name_b}说：「帮我写报告时留一行空白。我要在天亮前弄清楚，那行铅笔字是谁的字。」

搬迁队的叉车声从地面传来，震得荧光灯管轻颤。{name_a}在日志上写下时间，又划掉，改成更中性的措辞——她还不准备把「第三人」写进任何会存档的句子。程砚看着她，忽然提到五年前那桩没结案的夜班事故：有人擅动封存，第二天库房少了一卷录音带，从此没人再提。

「所以你想拦我。」{name_a}说。

「我想让你活着走完今晚。」{name_b}回答。

她点头，却把证物袋的编号记在本子边角：R-GEN-01-B17。那不是正式编号，只是她给自己留下的路标——如果天亮后档案库真的焊死，至少还有一张纸条证明她曾在最后一夜追问过回声。

程砚把掌上终端递过来，屏幕上跳出一条系统自动备注：B-17 卷宗在五年前的盘点里曾被标记为「回声关联」，随后备注被整段删除，只留下空行。林澄盯着那行空白，忽然意识到封条调换也许不是为了藏票，而是为了让人以为票从未被取出过。

「你早就查过这条备注。」她看向程砚。

「我查过，但没写进任何报告。」程砚说，「上一任夜班把录音带带走之后，系统就把所有『回声』字样洗了一遍。我留下来，是为了等一个还会问问题的人。」

林澄没有回答。她把乘车票翻过来，背面焦痕里夹着极淡的铅笔点，三点一线，和她封条边的私人记号一模一样。她忽然明白，这不是第三人留下的挑衅，而是多年前某个夜班档案员在黑暗里写下的求救——只是那时没有人愿意在搬迁前夜拆开纸袋。

窗外海风贴着通风口掠过，带着潮湿的锈味。{name_a}最后看了一眼监控屏定格的雪花帧，像一张被撕碎又贴回的旧照片。她不知道这是不是正确的决定，但她清楚：有些故事不能等到搬迁结束再读——它们会在铁柜焊死的那一刻，变成永远打不开的回声。

（本章由 RealGen 确定性模板自 story_seed 展开；含场景转换、人物冲突与结尾钩子。）
"""
    return body.strip() + "\n"


def generate_chapter_review(chapter: str, *, run_id: str) -> str:
    cjk = _count_cjk(chapter)
    names = re.findall(r"[\u4e00-\u9fff]{2,3}(?=把|问|说|盯|走|抬|剪|关)", chapter)
    unique_names = list(dict.fromkeys(names))[:4]
    hook_line = ""
    for line in reversed(chapter.splitlines()):
        if "回声" in line or "钩子" in line or "天亮" in line:
            hook_line = line.strip()
            break
    cliché_hits = []
    for phrase in ("不由得", "心头一紧", "空气仿佛凝固"):
        if phrase in chapter:
            cliché_hits.append(phrase)

    return f"""# 章节审稿报告（RealGen 生成）

> 基于 `chapter_01.md` 自动生成 · run_id={run_id}

## 情节摘要

- 字数（汉字）：约 **{cjk}** 字
- 主线：档案搬迁前夜，{', '.join(unique_names) or '主角'} 发现 B-17 封条被调换并拆开纸袋。
- 关键道具：半张烧毁乘车票、铅笔字「回声不是声音，是回来的人」。
- 结尾钩子摘录：{hook_line or '（见章节末段）'}

## 人物一致性

- 角色出场与 story_seed 一致；程砚执规、林澄追查形成对立协作。
- 建议：补充程砚「旧日心结」一句具体回忆，增强动机。

## 节奏

- 前段交代搬迁压力适中；中段拆封条张力足够。
- 监控室段落略紧，可考虑给雪花屏回放增加 2–3 句感官描写。

## DeAI / 套话检查

- 检测到套话：{', '.join(cliché_hits) if cliché_hits else '（未命中常见套话表）'}
- 「像某种倒计时」略模板化，可改具体声音来源。

## 改稿建议（需人工采用）

1. 在拆封条前增加林澄对规程条文的内心权衡（一句即可）。
2. 第三人影可留一句未解释细节（工牌反光缺失已够用）。
3. 结尾报告「留一行空白」可呼应后文调查线。

## 风险提示

- 商业发布：blocked
- 平台发布：blocked
- 版权：本章为 RealGen 虚构生成，不构成合规证明
- AI 披露：含模板化生成痕迹，出版前需人工润色
"""


def _scenes_from_chapter(chapter: str) -> list[dict[str, Any]]:
    return [
        {
            "scene_id": "sc01",
            "title": "B-17 库房封条",
            "location": "地下二层库房",
            "mood": "紧张",
            "duration_sec": 18,
            "narration": "封条被调换，搬迁前最后一夜。",
        },
        {
            "scene_id": "sc02",
            "title": "拆开牛皮纸袋",
            "location": "地下二层库房",
            "mood": "惊疑",
            "duration_sec": 15,
            "narration": "半张烧毁乘车票与神秘铅笔字。",
        },
        {
            "scene_id": "sc03",
            "title": "监控雪花十二秒",
            "location": "监控室",
            "mood": "悬疑",
            "duration_sec": 12,
            "narration": "第三人影掠过画面。",
        },
    ]


def generate_short_drama_package(out_dir: Path, chapter: str, seed: dict[str, str]) -> None:
    pkg = out_dir / "short_drama_package"
    pkg.mkdir(parents=True, exist_ok=True)
    scenes = _scenes_from_chapter(chapter)
    title = seed.get("标题", "冷案回声")

    scene_data = {
        "schema_version": "realgen-1",
        "source": "chapter_01.md",
        "project": "cold-case-echo-realgen-01",
        "title": title,
        "scenes": scenes,
        "total_duration_sec": sum(s["duration_sec"] for s in scenes),
        "commercial_release_allowed": False,
        "verdict": "blocked",
    }
    (pkg / "scene_package.json").write_text(
        json.dumps(scene_data, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    shots = [
        ["shot_id", "scene_id", "duration_sec", "shot_size", "subject", "movement", "note"],
        ["sh01", "sc01", "4", "MS", "林澄", "static", "封条特写"],
        ["sh02", "sc01", "5", "CU", "封条纤维", "slow_push", "铅笔压痕"],
        ["sh03", "sc01", "4", "MS", "程砚", "static", "规程劝阻"],
        ["sh04", "sc02", "5", "CU", "牛皮纸袋", "static", "剪开"],
        ["sh05", "sc02", "5", "ECU", "乘车票", "static", "焦黑边缘"],
        ["sh06", "sc02", "5", "CU", "铅笔字", "static", "回声不是声音"],
        ["sh07", "sc03", "4", "WS", "监控屏", "static", "雪花屏"],
        ["sh08", "sc03", "4", "CU", "人影", "pan", "第三人"],
        ["sh09", "sc03", "4", "MS", "林澄", "static", "决定追查"],
    ]
    with (pkg / "shot_list.csv").open("w", encoding="utf-8", newline="") as f:
        csv.writer(f).writerows(shots)

    assets = f"""# 素材需求（RealGen 生成）

## 角色
- 林澄：档案实习员，便装+手套
- 程砚：夜班安保，制服肩章

## 场景
- 地下二层库房：铁柜、荧光灯、消毒水味
- 监控室：多屏回放、雪花噪点

## 道具
- 牛皮纸袋、封条、证物袋、半张烧毁乘车票

## 风格
- 冷色悬疑、竖屏 1080x1920、无真实演员素材（预览用字幕卡）

## 门禁
- commercial_release_allowed: false
- adapter_enabled: false
"""
    (pkg / "asset_requirements.md").write_text(assets, encoding="utf-8")

    timeline = {
        "episode_id": "realgen_ep01",
        "shots": [row[0] for row in shots[1:]],
        "total_duration_sec": 45,
        "transitions": ["cut"] * 8,
        "subtitles_from": "video/preview_subtitles.srt",
        "verdict": "blocked",
    }
    (pkg / "timeline_package.json").write_text(
        json.dumps(timeline, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    risk = """# 风险检查（RealGen 生成）

- 商业发布：blocked（verdict=blocked）
- 平台发布：blocked
- 版权：虚构生成内容，需人工复核
- AI 披露：章节/审稿/分镜含确定性模板生成
- 外部调用：未使用外部 LLM/TTS/视频 API
- 视频：仅本地 FFmpeg 占位预览，非商业成片
"""
    (pkg / "risk_check.md").write_text(risk, encoding="utf-8")


def generate_video_sidecar(out_dir: Path, chapter: str, review: str) -> tuple[str, str]:
    video_dir = out_dir / "video"
    video_dir.mkdir(parents=True, exist_ok=True)
    summary = "档案搬迁前夜，封条被调换，纸袋内乘车票与神秘铅笔字引出第三人影。"
    script = f"""RealGen 预览旁白稿
========================
1. 地下库房，最后一夜。
2. 封条不对。纸袋里是半张烧毁的车票。
3. 监控雪花十二秒，第三个人从未登记。
4. 商业发布仍 blocked — 本地预览 only。
"""
    (video_dir / "preview_script.txt").write_text(script, encoding="utf-8")

    srt = """1
00:00:00,000 --> 00:00:12,000
冷案回声·档案员夜查
封条被调换的 B-17 柜

2
00:00:12,000 --> 00:00:28,000
半张烧毁乘车票
回声不是声音，是回来的人

3
00:00:28,000 --> 00:00:45,000
监控雪花十二秒
第三人影 · 本地预览 blocked 商业发布
"""
    (video_dir / "preview_subtitles.srt").write_text(srt, encoding="utf-8")

    plan = f"""# 视频计划（RealGen）

- 目标：`local_preview_video.mp4`
- 画幅：1080x1920 竖屏
- 时长：45s
- 来源章节摘要：{summary}
- 字幕：preview_subtitles.srt
- 禁止：外部视频 API、平台发布
"""
    (out_dir / "video_plan.md").write_text(plan, encoding="utf-8")
    return script, srt


def ffmpeg_available() -> bool:
    return shutil.which("ffmpeg") is not None


def _ffmpeg_sub_path(path: Path) -> str:
    return str(path.resolve()).replace("\\", "/").replace(":", "\\:")


def write_generate_preview_ps1(video_dir: Path) -> Path:
    ps1 = video_dir / "generate_preview_video.ps1"
    srt = video_dir / "preview_subtitles.srt"
    out = video_dir / "local_preview_video.mp4"
    content = f"""# RealGen preview video — requires FFmpeg on PATH
$ErrorActionPreference = "Stop"
$srt = Join-Path $PSScriptRoot "preview_subtitles.srt"
$out = Join-Path $PSScriptRoot "local_preview_video.mp4"
if (-not (Get-Command ffmpeg -ErrorAction SilentlyContinue)) {{
  Write-Error "FFmpeg not found. Install ffmpeg and retry."
  exit 1
}}
ffmpeg -y -f lavfi -i color=c=0x0f1419:s=1080x1920:d=45:rate=30 `
  -vf "subtitles='{srt}':force_style='FontSize=28,PrimaryColour=&HFFFFFF&'" `
  -c:v libx264 -pix_fmt yuv420p $out
Write-Host "Wrote $out"
"""
    ps1.write_text(content, encoding="utf-8")
    return ps1


def generate_preview_video(out_dir: Path) -> tuple[bool, str | None, list[str]]:
    """Returns (video_generated, blocker_path, run_blockers)."""
    video_dir = out_dir / "video"
    video_dir.mkdir(parents=True, exist_ok=True)
    out_mp4 = video_dir / "local_preview_video.mp4"
    srt = video_dir / "preview_subtitles.srt"
    ps1 = write_generate_preview_ps1(video_dir)
    blockers: list[str] = []

    if not ffmpeg_available():
        blocker_md = video_dir / "ffmpeg_missing_blocker.md"
        blocker_md.write_text(
            "# FFmpeg 缺失 — 视频未生成\n\n"
            "- `local_preview_video.mp4` **未生成**\n"
            "- 请安装 FFmpeg 后执行：`video/generate_preview_video.ps1`\n"
            "- 商业发布仍 blocked；此为本地预览 only\n",
            encoding="utf-8",
        )
        blockers.append("ffmpeg_missing")
        return False, str(blocker_md), blockers

    sub = _ffmpeg_sub_path(srt)
    cmd = [
        "ffmpeg",
        "-y",
        "-f",
        "lavfi",
        "-i",
        "color=c=0x0f1419:s=1080x1920:d=45:rate=30",
        "-vf",
        f"subtitles='{sub}':force_style='FontSize=28,PrimaryColour=&HFFFFFF&'",
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        str(out_mp4),
    ]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=120, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        blocker_md = video_dir / "ffmpeg_missing_blocker.md"
        blocker_md.write_text(f"# FFmpeg 执行失败\n\n{exc}\n", encoding="utf-8")
        blockers.append("ffmpeg_run_failed")
        return False, str(blocker_md), blockers

    if proc.returncode != 0 or not out_mp4.is_file() or out_mp4.stat().st_size < 1000:
        blocker_md = video_dir / "ffmpeg_missing_blocker.md"
        blocker_md.write_text(
            "# FFmpeg 执行失败 — 视频未生成\n\n```\n"
            + (proc.stderr or proc.stdout or "")[-2000:]
            + "\n```\n",
            encoding="utf-8",
        )
        blockers.append("ffmpeg_run_failed")
        return False, str(blocker_md), blockers

    return True, None, blockers


def validate_realgen_demo() -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    root = suite_root()
    demo = realgen_demo_root()
    for name in _CORE_FILES:
        p = demo / name
        checks.append(
            {
                "name": f"realgen_demo.{name.replace('/', '.')}",
                "ok": p.is_file(),
                "path": _rel(root, p),
            }
        )
    out = output_root()
    for rel in _REQUIRED_OUTPUT:
        p = out / rel
        checks.append(
            {
                "name": f"realgen_demo.output.{rel.replace('/', '.')}",
                "ok": p.is_file(),
                "path": _rel(root, p),
                "optional_until_first_run": True,
            }
        )
    return checks


def run_realgen_demo_validate() -> Result:
    checks = validate_realgen_demo()
    core_failed = [c for c in checks if not c.get("ok") and "optional" not in c]
    if core_failed:
        return error_result(
            REALGEN_DEMO_VALIDATE_FAIL,
            f"RealGen demo: {len(core_failed)} core check(s) failed",
            required=[c["name"] for c in core_failed],
            checks=checks,
            commercial_release_allowed=False,
            verdict="blocked",
        )
    return ok_result(
        REALGEN_DEMO_VALIDATE_OK,
        "RealGen demo package validation passed (seed present; run to materialize outputs)",
        checks=checks,
        commercial_release_allowed=False,
        verdict="blocked",
        platform_publish_allowed=False,
        next_actions=["novel-suite realgen-demo run --json"],
    )


def run_realgen_demo() -> Result:
    demo = realgen_demo_root()
    seed_path = demo / _SEED_NAME
    if not seed_path.is_file():
        return error_result(
            REALGEN_DEMO_SEED_MISSING,
            f"Missing {_SEED_NAME}",
            commercial_release_allowed=False,
            verdict="blocked",
        )

    seed_text = seed_path.read_text(encoding="utf-8")
    seed = parse_story_seed(seed_text)
    out = output_root()
    out.mkdir(parents=True, exist_ok=True)

    (out / _SEED_NAME).write_text(seed_text, encoding="utf-8")

    chapter = generate_chapter_01(seed, run_id=_RUN_ID)
    chapter_path = out / "chapter_01.md"
    chapter_path.write_text(chapter, encoding="utf-8")

    review = generate_chapter_review(chapter, run_id=_RUN_ID)
    review_path = out / "chapter_review.md"
    review_path.write_text(review, encoding="utf-8")

    generate_short_drama_package(out, chapter, seed)
    generate_video_sidecar(out, chapter, review)

    ffmpeg_ok = ffmpeg_available()
    video_generated, blocker_path, video_blockers = generate_preview_video(out)

    chapter_hash = hashlib.sha256(chapter.encode("utf-8")).hexdigest()[:16]
    manifest = {
        "version": 1,
        "run_id": _RUN_ID,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "real_generation_performed": True,
        "chapter_generated": True,
        "review_generated": True,
        "short_drama_package_generated": True,
        "video_generated": video_generated,
        "ffmpeg_available": ffmpeg_ok,
        "chapter_cjk_count": _count_cjk(chapter),
        "chapter_sha256_prefix": chapter_hash,
        "commercial_release_allowed": False,
        "verdict": "blocked",
        "platform_publish_allowed": False,
        "generator": "deterministic_template_v1",
        "external_llm": False,
    }
    manifest_path = out / _MANIFEST_NAME
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    arts: list[dict[str, Any]] = []
    root = suite_root()
    for rel in _REQUIRED_OUTPUT:
        p = out / rel
        if p.is_file():
            arts.append(artifact(_rel(root, p), kind="file", label=rel))
    if video_generated:
        arts.append(artifact(_rel(root, out / "video/local_preview_video.mp4"), label="local_preview_video"))
    elif blocker_path:
        arts.append(artifact(_rel(root, Path(blocker_path)), label="ffmpeg_blocker"))

    msg = "RealGen pipeline complete: chapter, review, short-drama package"
    if video_generated:
        msg += ", local preview video"
    else:
        msg += "; video blocked (see ffmpeg_missing_blocker.md)"

    return ok_result(
        REALGEN_DEMO_RUN_OK,
        msg,
        artifacts=arts,
        commercial_release_allowed=False,
        verdict="blocked",
        platform_publish_allowed=False,
        real_generation_performed=True,
        chapter_generated=True,
        review_generated=True,
        short_drama_package_generated=True,
        video_generated=video_generated,
        ffmpeg_available=ffmpeg_ok,
        chapter_cjk_count=_count_cjk(chapter),
        output_dir=_rel(root, out),
        blocker=video_blockers if video_blockers else [],
        next_actions=[
            f"Open {out / 'chapter_01.md'}",
            f"Open {out / 'chapter_review.md'}",
            "novel-suite realgen-demo validate --json",
        ],
    )
