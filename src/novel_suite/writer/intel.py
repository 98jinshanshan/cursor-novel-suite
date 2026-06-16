"""Phase 0 market scan — wraps legacy intel_scan with Result Contract metadata."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from novel_suite.core import errors as E
from novel_suite.core.paths import suite_root
from novel_suite.core.result import Result, artifact, error_result, ok_result
from novel_suite.writer._legacy import load_script_module


def _intel_scan():
    return load_script_module("intel_scan")


def _intel_paths():
    return load_script_module("intel_paths")


def source_type_for_run(*, demo: bool, input_path: Path | None) -> str:
    if demo:
        return "demo_fixture"
    if input_path is not None:
        return "user_input"
    return "public_search"


def confidence_from_score(score: int, sample_size: int) -> str:
    if sample_size < 5:
        return "low"
    if score >= 8:
        return "high"
    if score >= 3:
        return "medium"
    return "low"


def _suggest_platform(platform_names: set[str] | frozenset[str]) -> str:
    """根据题材覆盖的平台来源，建议最适合的发布平台。"""
    video_platforms = {"douyin", "kuaishou", "bilibili"}
    video_count = len(set(platform_names) & video_platforms)
    if video_count >= 2:
        return "douyin"
    return "fanqie"


def scrape_platform_trending(platform: str, max_items: int = 50) -> list[dict[str, Any]]:
    """爬取指定平台热门列表（stub，可替换为 MediaCrawler / Playwright）。"""
    return [
        {
            "platform": platform,
            "title": f"热门标题 #{i}",
            "heat_score": 100 - i * 2,
            "source": "scraper_stub",
            "note": "Replace with MediaCrawler or Playwright scraper",
        }
        for i in range(min(max_items, 10))
    ]


def predict_trend(historical_scores: list[float], days_ahead: int = 7) -> dict[str, Any]:
    """基于简单移动平均预测热度趋势。"""
    if len(historical_scores) < 3:
        return {"predictions": [], "trend": "unknown", "confidence": 0}

    window = min(7, len(historical_scores))
    sma = sum(historical_scores[-window:]) / window
    last = historical_scores[-1]

    if last > sma * 1.05:
        trend = "up"
    elif last < sma * 0.95:
        trend = "down"
    else:
        trend = "stable"

    confidence = min(0.9, len(historical_scores) * 0.1)

    return {
        "predictions": [round(sma * (1 + 0.02 * i), 1) for i in range(1, days_ahead + 1)],
        "trend": trend,
        "confidence": round(confidence, 2),
        "based_on_samples": len(historical_scores),
    }


def analyze_competition(topic: str, hits: list[Any]) -> dict[str, Any]:
    """分析某题材的竞争格局。"""
    _ = topic
    competitor_count = len(hits)

    if competitor_count == 0:
        return {
            "competitor_count": 0,
            "content_density": "空白",
            "gap_opportunity": "蓝海，建议快速入场",
        }
    if competitor_count < 10:
        return {
            "competitor_count": competitor_count,
            "content_density": "低",
            "gap_opportunity": "轻度竞争，差异化容易",
        }
    if competitor_count < 30:
        return {
            "competitor_count": competitor_count,
            "content_density": "中",
            "gap_opportunity": "中等竞争，需找到独特角度",
        }
    return {
        "competitor_count": competitor_count,
        "content_density": "高",
        "gap_opportunity": "红海市场，不建议入局",
    }


def _enrich_theme_metadata(theme: dict[str, Any], hits: list[Any]) -> dict[str, Any]:
    theme["competition_analysis"] = analyze_competition(theme.get("theme", ""), hits)
    theme["trend_prediction"] = predict_trend(
        [float(theme.get("score", 50))] * 3,
        days_ahead=7,
    )
    return theme


def theme_record(
    *,
    theme: str,
    score: int,
    sample_size: int,
    platform_coverage: int,
    source_type: str,
    verified: bool,
    platform_names: set[str] | frozenset[str] | None = None,
) -> dict[str, Any]:
    names = platform_names if platform_names is not None else set()
    return {
        "theme": theme,
        "score": score,
        "confidence": confidence_from_score(score, sample_size),
        "sample_size": sample_size,
        "platform_coverage": platform_coverage,
        "source_type": source_type,
        "verified": verified,
        "risks": [] if verified else ["source_unverified"],
        "suggested_platform": _suggest_platform(names),
    }


def run_scan(
    *,
    period: str = "week",
    platforms: str = "douyin,bilibili,kuaishou,xiaohongshu,weibo",
    demo: bool = False,
    input_path: Path | None = None,
    radar_path: Path | None = None,
    concepts_dir: Path | None = None,
    no_concepts: bool = False,
    concept_top: int = 3,
    max_results: int = 6,
    timeout: float = 12.0,
) -> Result:
    scan = _intel_scan()
    intel = _intel_paths()
    reg = load_script_module("project_registry")

    intel.ensure_intel_dirs()
    try:
        platform_list = scan.parse_platforms(platforms)
    except ValueError as exc:
        return error_result(E.SCAN_INVALID_PLATFORMS, str(exc))

    src_type = source_type_for_run(demo=demo, input_path=input_path)
    verified = src_type == "verified_platform"  # reserved; all V1 paths unverified
    scan_warnings: list[str] = ["source_unverified"] if not verified else []

    raw_hits: list[Any] = []
    if demo:
        fixture = suite_root() / "intel" / "fixtures" / "smoke-hits.json"
        if not fixture.is_file():
            return error_result(
                E.DEMO_FIXTURE_MISSING,
                f"Demo fixture missing: {fixture}",
                next_actions=["Run from monorepo root or restore intel/fixtures/smoke-hits.json"],
            )
        raw_hits.extend(scan.load_hits_from_input(fixture))
    elif input_path is not None:
        if not input_path.is_file():
            return error_result(
                E.SCAN_INPUT_NOT_FOUND,
                f"Input file not found: {input_path}",
                next_actions=["Provide --input JSON/NDJSON hits file"],
            )
        raw_hits.extend(scan.load_hits_from_input(input_path))
    else:
        failed_platforms: set[str] = set()
        for p in platform_list:
            platform_failed = True
            for q in scan.iter_queries(p, period):
                try:
                    rows = scan.ddg_search(q, limit=max_results, timeout_sec=timeout)
                    platform_failed = False
                except Exception:  # noqa: BLE001
                    continue
                for r in rows:
                    raw_hits.append(
                        scan.Hit(
                            platform=p,
                            title=r.get("title", ""),
                            url=r.get("url", ""),
                            snippet=r.get("snippet", ""),
                        )
                    )
            if platform_failed:
                failed_platforms.add(p)
        for p in sorted(failed_platforms):
            scan_warnings.append(f"live_scan_partial_failure:{p}")

    hits = scan.normalize_hits(raw_hits)
    hits = [h for h in hits if h.platform in platform_list]
    if not hits:
        return error_result(
            E.SCAN_NO_HITS,
            "No scan hits collected",
            next_actions=[
                "Use --demo for offline smoke",
                "Provide --input with curated hits",
                "Retry live scan later",
            ],
        )

    topic_scores, topic_coverage = scan.score_topics(hits)
    out_radar = radar_path or scan.default_radar_path(period)
    out_radar.parent.mkdir(parents=True, exist_ok=True)
    radar_text = scan.render_radar(
        period=period,
        platforms=platform_list,
        hits=hits,
        topic_scores=topic_scores,
        topic_coverage=topic_coverage,
    )
    out_radar.write_text(radar_text, encoding="utf-8")

    nec = load_script_module("node_completion")
    tag = intel.iso_week_id() if period == "week" else datetime.now().strftime("%Y-%m")
    out_concepts = concepts_dir or intel.CONCEPTS_DIR
    completion = nec.mark_phase0_cli_done(
        radar_md=out_radar,
        period_id=tag,
        concepts_dir=out_concepts if not no_concepts else None,
        no_concepts=no_concepts,
    )

    root = suite_root()
    concept_paths: list[Path] = []
    themes_meta: list[dict[str, Any]] = []
    ranked = [kv for kv in sorted(topic_scores.items(), key=lambda kv: kv[1], reverse=True) if kv[1] > 0]

    if not no_concepts:
        out_concepts.mkdir(parents=True, exist_ok=True)
        for i, (topic, score) in enumerate(ranked[:concept_top], start=1):
            slug = reg.slug_from_title(topic)
            out = out_concepts / f"{tag}-{i:02d}-{slug}.md"
            scan.make_concept_brief(topic=topic, week_or_month=tag, score=score, output=out)
            concept_paths.append(out)
            coverage = topic_coverage.get(topic, set())
            rec = theme_record(
                theme=topic,
                score=score,
                sample_size=len(hits),
                platform_coverage=len(coverage),
                source_type=src_type,
                verified=verified,
                platform_names=coverage,
            )
            rec["concept_path"] = _rel(root, out)
            themes_meta.append(rec)
        manifest = nec.load_manifest(completion)
        if manifest:
            nec.recompute_phase0_status(manifest, out_radar)
            nec.write_manifest(completion, manifest)
        nec.promote_phase0_if_demo_project_linked(out_radar)

    arts = [
        artifact(_rel(root, out_radar), label="radar"),
        artifact(_rel(root, completion), label="completion"),
    ]
    for cp in concept_paths:
        arts.append(artifact(_rel(root, cp), label="concept"))

    top3 = themes_meta[:3] if themes_meta else [
        theme_record(
            theme=t,
            score=topic_scores[t],
            sample_size=len(hits),
            platform_coverage=len(topic_coverage.get(t, set())),
            source_type=src_type,
            verified=verified,
            platform_names=topic_coverage.get(t, set()),
        )
        for t in [k for k, v in sorted(topic_scores.items(), key=lambda kv: kv[1], reverse=True) if v > 0][:3]
    ]

    for theme in themes_meta:
        _enrich_theme_metadata(theme, hits)
    for theme in top3:
        if "competition_analysis" not in theme:
            _enrich_theme_metadata(theme, hits)

    scan_json_path = out_radar.with_name(f"{out_radar.stem}.scan.json")
    scan_payload = {
        "version": 1,
        "period": period,
        "radar_path": _rel(root, out_radar),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_type": src_type,
        "sample_size": len(hits),
        "themes": top3,
    }
    scan_json_path.write_text(
        json.dumps(scan_payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    arts.append(artifact(_rel(root, scan_json_path), label="scan_json"))

    return ok_result(
        "SCAN_OK",
        f"Market scan complete ({src_type}, {len(hits)} hits)",
        artifacts=arts,
        next_actions=[
            "Review Top3 concepts and mark one as approved",
            f"novel-suite writer init --from-scan {scan_json_path.as_posix()} --json",
        ],
        scan_json_path=_rel(root, scan_json_path),
        period=period,
        source_type=src_type,
        verified=verified,
        sample_size=len(hits),
        themes=top3,
        demo=demo,
        warnings=scan_warnings,
    )


def _rel(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return str(path)
