# 样片（demos）

对标 [video_skills](https://github.com/hexiaochun/video_skills) 的 `demos/` 目录。

## 生成样片

```bash
cd cursor-novel-video
py -3 engine/video_cli.py summary \
  --chapter ../cursor-novel-writer/examples/demo-novel/chapters/01_试章.md \
  --aspect 9:16 --subtitles
```

将 `tmp/video_jobs/*/output/*_subtitled.mp4`（或 `*_summary.mp4`）复制到本目录并更新下表。

## 索引

| 文件 | 模式 | 来源章 | 说明 |
| --- | --- | --- | --- |
| [demo-novel-ch01-summary-9x16-subtitled.mp4](./demo-novel-ch01-summary-9x16-subtitled.mp4) | summary | 01_试章 | 竖屏 9:16，约 13s，含烧录字幕 |

## 体积

- 提交 Git 的样片建议 **< 5 MB**；更大文件用 Git LFS 或仅保留 README 说明。
