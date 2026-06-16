# 15 分钟 Demo 脚本（个人开发者）

> 全程只读；不生成真实内容、不调用 adapter、不发布。

## 总览

| 环节 | 时长 | 目标 |
| --- | --- | --- |
| 1 产品入口 | 2 min | 知道从哪开始 |
| 2 商业 blocked | 3 min | 知道什么不能做 |
| 3 PP-001 起点 | 4 min | 知道新手第一步 |
| 4 视频规格入口 | 3 min | 知道视频化是规格非成片 |
| 5 dry-run 反馈 | 3 min | 知道如何记录试用 |

---

## 环节 1：读产品入口（2 分钟）

1. 打开 `novel-suite/README.md` — 目录与快速路径。
2. 打开 `novel-suite/delivery-hub/README.md` — 冷启动索引。
3. 运行：`novel-suite product list --json`（可选，只读）。

**通过标准：** 能说出「立项 → PP-001 → 写作 → PP-002 → 视频规格 → PP-003」大致顺序。

---

## 环节 2：确认商业 blocked 边界（3 分钟）

1. 阅读 [blocked_boundary.md](blocked_boundary.md)。
2. 阅读 `novel-suite/solo-founder-release-blocked-declaration/prohibited_scope.md`。
3. 运行：`novel-suite commercial-release-candidate validate --json` — 确认 `verdict=blocked`。

**通过标准：** 明确「可本地 demo、不可商业发布/tag/zip/release」。

---

## 环节 3：查看 PP-001 新手起点（4 分钟）

1. 阅读 `novel-suite/prompt-packs/README.md` — 确认 PP-001 为新手起点。
2. 浏览 `novel-suite/prompt-packs/PP-001_novel_project_init.md` 前几节。
3. 打开 `novel-suite/promptpack-first-run/pp001_first_run_guide.md`（P2 首跑指南）。

**通过标准：** 知道 PP-001 输入（题材/受众/风格）与输出（故事圣经骨架），不承诺一键成书。

---

## 环节 4：查看短剧/视频生产规格入口（3 分钟）

1. 浏览 `novel-suite/video-production/README.md`（若存在）或 `novel-suite/prompt-packs/PP-003_novel_to_video.md` 标题与结构。
2. 确认 `adapters/` 默认关闭 — 规格先行，非真实成片。
3. 运行：`novel-suite product read --category prompt-packs --name PP-003_novel_to_video --json`（可选）。

**通过标准：** 区分「视频化规格/分镜 Prompt」与「一键成片/商业发布」。

---

## 环节 5：填写 dry-run 反馈模板（3 分钟）

1. 复制 `novel-suite/multi-ide-dry-run-feedback/feedback_template.md` 到本地笔记。
2. 填写：IDE 名称、本 demo 任务、入口是否清楚、是否看到 blocked 提醒。
3. **不**上传、**不**自动采集 — 见 `local_collection_policy.md`。

**通过标准：** 有一份可粘贴的本地反馈草稿，供后续 Q1/Q3 承接。
