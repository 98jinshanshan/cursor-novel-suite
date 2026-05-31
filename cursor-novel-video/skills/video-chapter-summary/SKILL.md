---
name: video-chapter-summary
description: |
  Create 60-180s chapter summary short video from novel markdown: script, TTS, subtitles, Ken Burns, FFmpeg.
  Use for 章节摘要视频、把小说做成短视频、chapter summary video, 抖音竖屏.
license: MIT
compatibility: Python 3.10+, FFmpeg, edge-tts, full repo clone for scripts/. Optional OpenAI for images (adapters/).
metadata:
  author: cursor-novel-video
  version: "1.0.0"
---

# Video Chapter Summary (MVP)

Fuses [video_skills](https://github.com/hexiaochun/video_skills) one-shot workflow
and [super-video-maker](https://github.com/Bomx/super-video-maker-skill) staged pipeline.

## Pipeline

```text
intake → summary script → storyboard.json → TTS → visuals → FFmpeg compose → QC → MP4
```

Job dir: `tmp/video_jobs/<job_id>/` with `job_state.json`.

## Stage 1: Intake

- Input: path to `chapters/NN_*.md` or novel project root + chapter number
- Platform: `9:16` (default 抖音) or `16:9`
- Duration target: 60-180s
- Voice: `zh-CN-XiaoxiaoNeural` (edge-tts default)

## Stage 2: Summary Script

Extract: hook, 3-5 beats, cliffhanger. Save `script.md` and `storyboard.json` per schema.

## Stage 3: Assets

From repo root, use skill wrappers (`skills/video-chapter-summary/scripts/`):

```bash
python skills/video-chapter-summary/scripts/tts_edge.py --text-file script.md --output audio.mp3
python skills/video-chapter-summary/scripts/ken_burns.py --image assets/slide.png --duration 5 --output clip.mp4
python skills/video-chapter-summary/scripts/beat_lock.py --script script.md --audio audio.mp3 --output subtitles.srt
python skills/video-chapter-summary/scripts/burn_subtitles.py --video out.mp4 --srt subtitles.srt --output out_sub.mp4
```

Optional image: `python adapters/openai_image.py --prompt "..." --output assets/slide.png`

## Stage 4: Compose

```bash
python skills/video-chapter-summary/scripts/compose_ffmpeg.py summary --job tmp/video_jobs/<id> --aspect 9:16
```

## Stage 5: QC

```bash
python skills/video-chapter-summary/scripts/qc_video.py output/ch03_summary.mp4
```

## CLI Equivalent

```bash
python engine/video_cli.py summary --chapter ../cursor-novel-writer/examples/demo-novel/chapters/01_试章.md --aspect 9:16 --subtitles
```

## Trigger Phrases

- 把第3章做成60秒摘要视频
- 章节短视频 竖屏
- chapter summary video
