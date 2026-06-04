#!/usr/bin/env python3
"""Phase 0 market scan: cross-platform hot short-video topic radar."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from html import unescape
from pathlib import Path
from urllib.parse import quote_plus
from urllib.request import Request, urlopen

ENGINE_DIR = Path(__file__).resolve().parents[1]
if str(ENGINE_DIR) not in sys.path:
    sys.path.insert(0, str(ENGINE_DIR))

from scripts import intel_paths as intel
from scripts import project_registry as reg
from scripts import suite_paths as sp

PLATFORM_SITES: dict[str, tuple[str, str]] = {
    "douyin": ("抖音", "douyin.com"),
    "bilibili": ("B站", "bilibili.com"),
    "kuaishou": ("快手", "kuaishou.com"),
    "xiaohongshu": ("小红书", "xiaohongshu.com"),
    "weibo": ("微博", "weibo.com"),
}

THEME_KEYWORDS: dict[str, tuple[str, ...]] = {
    "逆袭复仇爽文": ("逆袭", "复仇", "打脸", "重生", "爽文", "翻盘"),
    "都市情感婚恋": ("都市", "总裁", "婚恋", "离婚", "虐恋", "豪门"),
    "悬疑刑侦推理": ("悬疑", "刑侦", "破案", "谜案", "反转", "推理"),
    "古言权谋宅斗": ("古言", "权谋", "宫斗", "侯府", "王爷", "将军"),
    "玄幻仙侠升级": ("玄幻", "仙侠", "修仙", "宗门", "灵根", "飞升"),
    "科幻脑洞系统": ("科幻", "赛博", "系统", "无限流", "未来", "异能"),
    "校园青春成长": ("校园", "青春", "学霸", "暗恋", "校花", "成长"),
    "家庭伦理现实": ("家庭", "婆媳", "亲子", "现实", "二婚", "赘婿"),
}

HOOK_WORDS = ("反转", "打脸", "复仇", "重生", "离婚", "失忆", "真相", "黑化")
VISUAL_WORDS = ("豪门", "婚礼", "刑侦", "古装", "宫斗", "修仙", "赛博", "校园")
TWIST_WORDS = ("反转", "真相", "谜", "误会", "身份", "卧底", "背叛")
RISK_WORDS = ("血腥", "极端", "仇恨", "违法", "毒品")


@dataclass
class Hit:
    platform: str
    title: str
    url: str
    snippet: str

    @property
    def text(self) -> str:
        return f"{self.title} {self.snippet}".strip()


def _strip_html(raw: str) -> str:
    no_tags = re.sub(r"<[^>]+>", "", raw)
    squashed = re.sub(r"\s+", " ", no_tags)
    return unescape(squashed).strip()


def ddg_search(query: str, *, limit: int, timeout_sec: float) -> list[dict[str, str]]:
    url = f"https://duckduckgo.com/html/?q={quote_plus(query)}"
    req = Request(
        url=url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
            )
        },
    )
    max_html = 2 * 1024 * 1024
    with urlopen(req, timeout=timeout_sec) as resp:  # noqa: S310
        raw = resp.read(max_html + 1)
        if len(raw) > max_html:
            raw = raw[:max_html]
        html = raw.decode("utf-8", errors="ignore")

    chunks = re.findall(
        r'(?s)<div class="result__body".*?</div>\s*</div>',
        html,
    )
    out: list[dict[str, str]] = []
    for chunk in chunks:
        a = re.search(r'<a[^>]*class="result__a"[^>]*href="(?P<u>[^"]+)"[^>]*>(?P<t>.*?)</a>', chunk)
        if not a:
            continue
        s = re.search(r'class="result__snippet"[^>]*>(?P<s>.*?)</a>', chunk)
        title = _strip_html(a.group("t"))
        snippet = _strip_html(s.group("s")) if s else ""
        out.append({"title": title, "url": a.group("u"), "snippet": snippet})
        if len(out) >= limit:
            break
    return out


def iter_queries(platform: str, period: str) -> list[str]:
    cn, site = PLATFORM_SITES[platform]
    cadence = "本周" if period == "week" else "本月"
    return [
        f"site:{site} {cadence} 热门 短视频 小说 推文",
        f"site:{site} 爆款 剧情 反转 短视频",
        f"site:{site} {cadence} 热门 书单 文案",
    ]


def normalize_hits(raw_hits: list[Hit]) -> list[Hit]:
    seen: set[tuple[str, str]] = set()
    deduped: list[Hit] = []
    for h in raw_hits:
        key = (h.url.strip(), h.title.strip())
        if not h.title or key in seen:
            continue
        seen.add(key)
        deduped.append(h)
    return deduped


def score_topics(hits: list[Hit]) -> tuple[dict[str, int], dict[str, set[str]]]:
    scores = {k: 0 for k in THEME_KEYWORDS}
    coverage = {k: set() for k in THEME_KEYWORDS}
    for h in hits:
        text = h.text
        for topic, kws in THEME_KEYWORDS.items():
            matched = sum(1 for kw in kws if kw in text)
            if matched > 0:
                scores[topic] += matched
                coverage[topic].add(h.platform)
    return scores, coverage


def short_video_fit(topic: str, sample_text: str) -> tuple[int, int, int, int, int]:
    hook = min(5, 1 + sum(1 for w in HOOK_WORDS if w in sample_text))
    visual = min(5, 1 + sum(1 for w in VISUAL_WORDS if w in sample_text))
    clip = min(5, 2 + sample_text.count("，") + sample_text.count("。"))
    twist = min(5, 1 + sum(1 for w in TWIST_WORDS if w in sample_text))
    compliance = 5 - min(3, sum(1 for w in RISK_WORDS if w in sample_text))
    compliance = max(1, compliance)
    return hook, visual, clip, twist, compliance


def default_radar_path(period: str) -> Path:
    if period == "week":
        return intel.radar_path_for_week()
    now = datetime.now()
    return intel.RADAR_DIR / f"{now.year}-{now.month:02d}.md"


def _finalize_markdown(lines: list[str]) -> str:
    while lines and not lines[-1].strip():
        lines.pop()
    return "\n".join(lines) + "\n"


def render_radar(
    *,
    period: str,
    platforms: list[str],
    hits: list[Hit],
    topic_scores: dict[str, int],
    topic_coverage: dict[str, set[str]],
) -> str:
    stamp = datetime.now(timezone.utc).isoformat()
    by_platform: dict[str, int] = {p: 0 for p in platforms}
    for h in hits:
        by_platform[h.platform] = by_platform.get(h.platform, 0) + 1

    top_topics = [k for k, v in sorted(topic_scores.items(), key=lambda kv: kv[1], reverse=True) if v > 0][:5]
    lines = [
        f"# 市场雷达（{ '周报' if period == 'week' else '月报' }）",
        "",
        f"- 生成时间（UTC）：{stamp}",
        f"- 扫描平台：{', '.join(PLATFORM_SITES[p][0] for p in platforms)}",
        f"- 热点样本数：{len(hits)}",
        "- 数据源：跨平台公开网页搜索（V1 Agent 扫描模式）",
        "",
        "## 平台样本覆盖",
        "",
        "| 平台 | 样本数 |",
        "| --- | ---: |",
    ]
    for p in platforms:
        lines.append(f"| {PLATFORM_SITES[p][0]} | {by_platform.get(p, 0)} |")

    lines.extend(
        [
            "",
            "## 热点样本（Top 20）",
            "",
            "| 平台 | 标题 | 链接 |",
            "| --- | --- | --- |",
        ]
    )
    for h in hits[:20]:
        title = h.title.replace("|", "/")
        link = f"[链接]({h.url})" if h.url else "—"
        lines.append(f"| {PLATFORM_SITES[h.platform][0]} | {title} | {link} |")

    lines.extend(
        [
            "",
            "## 平台快照",
            "",
            "> Agent（P0-S2）：按 platform-scan-guide 补全表格；无法验证标 `(unverified)`",
            "",
            "### 番茄小说",
            "",
            "| 排名区间 | 类型/标签 | 高频设定 | 来源 |",
            "| --- | --- | --- | --- |",
            "| (待补全) | | | |",
            "",
            "### 起点中文网",
            "",
            "| 排名区间 | 类型/标签 | 高频设定 | 来源 |",
            "| --- | --- | --- | --- |",
            "| (待补全) | | | |",
            "",
            "### 晋江文学城",
            "",
            "| 排名区间 | 类型/标签 | 高频设定 | 来源 |",
            "| --- | --- | --- | --- |",
            "| (待补全) | | | |",
            "",
            "### 知乎盐选（短篇）",
            "",
            "| 热度信号 | 类型 | 钩子模式 | 来源 |",
            "| --- | --- | --- | --- |",
            "| (待补全) | | | |",
            "",
            "## 题材热度榜（短视频导向）",
            "",
            "| 排名 | 题材 | 热度分 | 平台覆盖 |",
            "| ---: | --- | ---: | --- |",
        ]
    )
    for idx, t in enumerate(top_topics, start=1):
        lines.append(f"| {idx} | {t} | {topic_scores[t]} | {len(topic_coverage[t])} |")

    lines.extend(["", "## 立项候选（Top 3）", ""])
    if not top_topics:
        lines.append("- 暂无有效热点，建议提高 `--max-results` 或改为 `--input` 导入人工搜集样本。")
        return _finalize_markdown(lines)

    for idx, topic in enumerate(top_topics[:3], start=1):
        sample = next((h.text for h in hits if any(kw in h.text for kw in THEME_KEYWORDS[topic])), topic)
        hook, visual, clip, twist, compliance = short_video_fit(topic, sample)
        total = hook + visual + clip + twist + compliance
        lines.extend(
            [
                f"### {idx}. {topic}",
                "",
                f"- 短视频适配：{total}/25（钩子{hook} 可视化{visual} 可剪性{clip} 反转{twist} 合规{compliance}）",
                f"- 一句话方向：围绕“{topic}”设计首章强钩子，优先可视化冲突与反转。",
                "",
            ]
        )

    return _finalize_markdown(lines)


def parse_platforms(raw: str) -> list[str]:
    parts = [p.strip().lower() for p in raw.split(",") if p.strip()]
    unknown = [p for p in parts if p not in PLATFORM_SITES]
    if unknown:
        raise ValueError(f"Unknown platforms: {', '.join(unknown)}")
    return parts


def load_hits_from_input(path: Path) -> list[Hit]:
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return []
    if text.startswith("["):
        rows = json.loads(text)
    else:
        rows = [json.loads(line) for line in text.splitlines() if line.strip()]
    out: list[Hit] = []
    for row in rows:
        out.append(
            Hit(
                platform=str(row.get("platform", "")).strip().lower(),
                title=str(row.get("title", "")).strip(),
                url=str(row.get("url", "")).strip(),
                snippet=str(row.get("snippet", "")).strip(),
            )
        )
    return out


def make_concept_brief(
    *,
    topic: str,
    week_or_month: str,
    score: int,
    output: Path,
) -> None:
    tpl = (
        (sp.writer_root() / "templates" / "concept-brief.md")
        .read_text(encoding="utf-8")
        .replace("{{TITLE}}", topic)
        .replace("{{YYYY-Www}}", week_or_month)
    )
    if "| 状态 | draft / approved |" in tpl:
        tpl = tpl.replace("| 状态 | draft / approved |", "| 状态 | draft（待确认） |")
    marker = "## 题材摘要\n\n"
    if marker in tpl:
        insert = (
            "## 热点来源摘要\n\n"
            f"- 题材热度分：{score}\n"
            "- 来源：`novel intel scan` 跨平台热榜扫描\n\n"
        )
        tpl = tpl.replace(marker, insert + marker)
    output.write_text(tpl, encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description="Cross-platform hot short-video scan for novel topic selection")
    ap.add_argument("--period", choices=("week", "month"), default="week")
    ap.add_argument(
        "--platforms",
        default="douyin,bilibili,kuaishou,xiaohongshu,weibo",
        help="Comma-separated platform ids",
    )
    ap.add_argument("--max-results", type=int, default=6, help="Max hits per query")
    ap.add_argument("--timeout", type=float, default=12.0, help="HTTP timeout seconds")
    ap.add_argument("--input", type=Path, default=None, help="Optional JSON/NDJSON hit input")
    ap.add_argument(
        "--demo",
        action="store_true",
        help="Offline smoke: use intel/fixtures/smoke-hits.json (not live market data)",
    )
    ap.add_argument("--radar", type=Path, default=None, help="Output radar markdown path")
    ap.add_argument("--concepts-dir", type=Path, default=None, help="Directory for generated concept briefs")
    ap.add_argument("--concept-top", type=int, default=3, help="Number of concept briefs to generate")
    ap.add_argument("--no-concepts", action="store_true", help="Do not generate concept briefs")
    args = ap.parse_args()

    intel.ensure_intel_dirs()
    try:
        platforms = parse_platforms(args.platforms)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    raw_hits: list[Hit] = []
    if args.demo:
        fixture = sp.suite_root() / "intel" / "fixtures" / "smoke-hits.json"
        if not fixture.is_file():
            print(f"ERROR: demo fixture missing: {fixture}", file=sys.stderr)
            return 1
        print("WARN: --demo uses offline fixture; not live market scan.", file=sys.stderr)
        raw_hits.extend(load_hits_from_input(fixture))
    elif args.input:
        raw_hits.extend(load_hits_from_input(args.input))
    else:
        for p in platforms:
            for q in iter_queries(p, args.period):
                try:
                    rows = ddg_search(q, limit=args.max_results, timeout_sec=args.timeout)
                except Exception as exc:  # noqa: BLE001
                    print(f"WARN: scan failed for {p} query='{q}': {exc}", file=sys.stderr)
                    continue
                for r in rows:
                    raw_hits.append(
                        Hit(
                            platform=p,
                            title=r.get("title", ""),
                            url=r.get("url", ""),
                            snippet=r.get("snippet", ""),
                        )
                    )

    hits = normalize_hits(raw_hits)
    hits = [h for h in hits if h.platform in platforms]
    if not hits:
        print("ERROR: no scan hits collected; provide --input or retry later", file=sys.stderr)
        return 1

    topic_scores, topic_coverage = score_topics(hits)
    radar_path = args.radar or default_radar_path(args.period)
    radar_path.parent.mkdir(parents=True, exist_ok=True)
    radar_text = render_radar(
        period=args.period,
        platforms=platforms,
        hits=hits,
        topic_scores=topic_scores,
        topic_coverage=topic_coverage,
    )
    radar_path.write_text(radar_text, encoding="utf-8")
    print(f"OK: radar -> {radar_path}")

    from scripts import node_completion as nec  # noqa: PLC0415

    tag = intel.iso_week_id() if args.period == "week" else datetime.now().strftime("%Y-%m")
    concepts_dir = args.concepts_dir or intel.CONCEPTS_DIR
    completion = nec.mark_phase0_cli_done(
        radar_md=radar_path,
        period_id=tag,
        concepts_dir=concepts_dir if not args.no_concepts else None,
        no_concepts=args.no_concepts,
    )
    print(f"OK: completion -> {completion}")

    if args.no_concepts:
        return 0

    concepts_dir = args.concepts_dir or intel.CONCEPTS_DIR
    concepts_dir.mkdir(parents=True, exist_ok=True)
    tag = intel.iso_week_id() if args.period == "week" else datetime.now().strftime("%Y-%m")
    ranked = [kv for kv in sorted(topic_scores.items(), key=lambda kv: kv[1], reverse=True) if kv[1] > 0]
    created = 0
    for i, (topic, score) in enumerate(ranked[: args.concept_top], start=1):
        slug = reg.slug_from_title(topic)
        out = concepts_dir / f"{tag}-{i:02d}-{slug}.md"
        make_concept_brief(topic=topic, week_or_month=tag, score=score, output=out)
        created += 1
        print(f"OK: concept -> {out}")
    if created == 0:
        print("WARN: no concept briefs generated because no topic score > 0", file=sys.stderr)
    manifest = nec.load_manifest(completion)
    if manifest:
        nec.recompute_phase0_status(manifest, radar_path)
        nec.write_manifest(completion, manifest)
    nec.promote_phase0_if_demo_project_linked(radar_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
