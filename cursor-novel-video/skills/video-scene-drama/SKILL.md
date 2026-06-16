---
name: video-scene-drama
description: |
  Scene-by-scene narrative video (2-5 min/chapter): split scenes, per-scene TTS and visuals, concat.
  Use for 分场景视频、小说场景化、scene drama, 章节叙事片.
license: MIT
compatibility: Python 3.10+, FFmpeg, edge-tts, full repo clone for scripts/. Optional Seedance/OpenAI via adapters/.
metadata:
  author: cursor-novel-video
  version: "1.0.0"
---

# Video Scene Drama (Advanced)

From super-video-maker beat-lock + mcp-video storyboard planning.

## Pipeline

1. Parse chapter into scenes (## 一 / ## 二 / ## 三 or `---` blocks)
2. **Per scene (knowledge-video style):** TTS → Ken Burns synced to audio → mux → `scenes/scene_sNN.mp4`
3. Concat scene clips → `output/chNN_drama.mp4`
4. Optional `--subtitles`: merge scene audio → beat-lock SRT → burn

## Storyboard Scene Object

```json
{
  "id": "s01",
  "narration": "旁白文本",
  "visual_job": "mechanism",
  "duration_target": 8,
  "asset": "assets/s01.png"
}
```

## Beat-lock Rule

Cut on sentence boundaries; align visuals to TTS segment timestamps when using Whisper (optional enhancement).

## CLI

```bash
python engine/video_cli.py drama --chapter chapters/03_*.md --subtitles
```

Skill scripts: `skills/video-scene-drama/scripts/` (tts_edge, make_title_card, ken_burns, compose_ffmpeg).

## Optional B-roll

See `adapters/seedance.md` for Replicate Seedance; fallback order: user image → OpenAI still → typographic card.

## Sprint 2-4 视频管线完整流程

1. `novel-suite video storyboard` → 从章节生成分镜 JSON
2. `novel-suite video character list/pack/qc` → 角色素材管理
3. `novel-suite video stills generate` → 逐场景静帧
4. `novel-suite video compose` → Ken Burns + TTS + 字幕
5. `novel-suite video pipeline` → 一键 E2E
6. `novel-suite video gate` → 发布前门禁检查
7. `novel-suite video publish upload` → 多平台发布（douyin/kuaishou/bilibili）
