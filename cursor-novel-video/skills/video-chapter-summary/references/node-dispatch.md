# V0 节点分派（video-chapter-summary）

| ID | 执行体 | 命令 / 参考 | 产出 |
| --- | --- | --- | --- |
| V0-S0 | `cli` | `novel active` + 读章节 md | 绑定 slug |
| V0-S1 | `agent` | [PIPELINE.md](./PIPELINE.md) | `script.md` |
| V0-S2 | `cli` | `video_cli summary --project ... --subtitles` | `tmp/video_jobs/<id>/` |
| V0-S3 | `cli` | `qc_video.py` | RESULT JSON |
| V0-S4 | `cli` | | `node.completion.json` |

## Chat Summary

MP4 路径、时长、字幕是否烧制；禁止只说「已生成」不给路径。
