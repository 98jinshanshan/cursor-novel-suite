"""Phase 0 market scan — wraps legacy intel_scan with Result Contract metadata."""

from __future__ import annotations

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


def theme_record(
    *,
    theme: str,
    score: int,
    sample_size: int,
    platform_coverage: int,
    source_type: str,
    verified: bool,
) -> dict[str, Any]:
    return {
        "theme": theme,
        "score": score,
        "confidence": confidence_from_score(score, sample_size),
        "sample_size": sample_size,
        "platform_coverage": platform_coverage,
        "source_type": source_type,
        "verified": verified,
        "risks": [] if verified else ["source_unverified"],
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
            themes_meta.append(
                theme_record(
                    theme=topic,
                    score=score,
                    sample_size=len(hits),
                    platform_coverage=len(topic_coverage.get(topic, set())),
                    source_type=src_type,
                    verified=verified,
                )
            )
        manifest = nec.load_manifest(completion)
        if manifest:
            nec.recompute_phase0_status(manifest, out_radar)
            nec.write_manifest(completion, manifest)
        nec.promote_phase0_if_demo_project_linked(out_radar)

    root = suite_root()
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
        )
        for t in [k for k, v in sorted(topic_scores.items(), key=lambda kv: kv[1], reverse=True) if v > 0][:3]
    ]

    return ok_result(
        "SCAN_OK",
        f"Market scan complete ({src_type}, {len(hits)} hits)",
        artifacts=arts,
        next_actions=[
            "Review Top3 concepts and mark one as approved",
            "novel-suite writer init --concept intel/concepts/<file>.md --json (or legacy novel init)",
        ],
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
