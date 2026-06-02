---
name: video-export
description: |
  Final export, aspect variants, and QC for novel-derived videos. Use for 导出视频、多平台尺寸、video QC.
license: MIT
compatibility: Python 3.10+, FFmpeg, full repo clone for scripts/.
metadata:
  author: cursor-novel-video
  version: "1.0.0"
---

# Video Export & QC

## Node Execution Contract (NEC)

**执行前必读：** [references/node-dispatch.md](./references/node-dispatch.md)（V2 节点）。

## Export Targets

| Platform | Aspect | Resolution |
| --- | --- | --- |
| 抖音/小红书 | 9:16 | 1080×1920 |
| B站/YouTube | 16:9 | 1920×1080 |
| 方形 | 1:1 | 1080×1080 |

## Commands

```bash
python skills/video-export/scripts/compose_ffmpeg.py resize --input out.mp4 --aspect 9:16 --output out_916.mp4
python skills/video-export/scripts/qc_video.py out.mp4 --min-duration 30 --require-audio
```

## QC Checklist (super-video-maker inspired)

- [ ] Video stream present, expected resolution
- [ ] Audio present, loudness roughly -16 LUFS (optional)
- [ ] No black frames > 0.5s at start
- [ ] Duration within target band
- [ ] Captions readable (if burned in)

## job_state.json Contract

```json
{
  "status": "succeeded",
  "stage": "export",
  "artifacts": [{"type": "video", "path": "output/ch03_summary.mp4"}]
}
```
