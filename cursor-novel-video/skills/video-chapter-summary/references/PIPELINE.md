# Chapter Summary Pipeline（SVM-09）

60–180s 竖屏章节摘要成片流水线。引擎实现：`cursor-novel-video/engine/`。

## 阶段

| Stage | 脚本 | 产出 |
| --- | --- | --- |
| intake | `video_cli.py summary` | `tmp/video_jobs/<id>/storyboard.json`, `script.md` |
| tts | `engine/scripts/tts_edge.py` | `audio.mp3` |
| subtitles（可选） | `beat_lock.py` | `subtitles.srt` |
| visual | `make_title_card.py` + `ken_burns.py` | `assets/title.png`, `clip.mp4` |
| compose | `compose_ffmpeg.py summary` | `output/*_summary.mp4` |
| burn（可选） | `burn_subtitles.py` | `*_subtitled.mp4` |
| qc | `qc_video.py` | stdout JSON + RESULT 行 |

## 一键 CLI

```bash
python engine/video_cli.py summary \
  --chapter ../cursor-novel-writer/novels/<slug>/chapters/01_开篇.md \
  --aspect 9:16 \
  --subtitles
```

## Storyboard 字段

```json
{
  "job_id": "...",
  "mode": "summary",
  "aspect": "9:16",
  "voice": "zh-CN-XiaoxiaoNeural",
  "scenes": [{ "id": "s01", "narration": "...", "duration_target": 60 }]
}
```

## RESULT 契约（SVM-06）

成功时 stdout 末行：

```text
RESULT: {"status":"ok","artifact":".../output/xxx_summary.mp4","mode":"summary"}
```

Agent / MCP 应解析 `RESULT:` 行，勿仅依赖 `OK:`。

## 依赖

- FFmpeg、Python 3.10+、`edge-tts`（见 requirements.txt）
- 输入：cursor-novel-writer `chapters/*.md`（Markdown，可选 `##` 场景标题）

## 与 drama 模式区别

| | summary | drama (`video-scene-drama`) |
| --- | --- | --- |
| 时长 | 60–180s | 2–5min |
| 分镜 | 单 narration | 多 scene 逐段 TTS+Ken Burns |
| Skill | `video-chapter-summary` | `video-scene-drama` |
