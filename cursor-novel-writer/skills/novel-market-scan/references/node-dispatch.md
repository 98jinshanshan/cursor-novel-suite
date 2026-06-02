# Phase 0 节点分派表（novel-market-scan）

**契约：** [NODE-EXECUTION-CONTRACT.md](../../../../docs/standards/NODE-EXECUTION-CONTRACT.md)

## 1. Entry Triggers

- 扫榜、本周热门短视频、题材雷达、选题
- 去各大平台搜集最火视频 / 推书爆款
- Phase 0、market scan、intel scan

## 2. Intent Decomposition

| 用户意图片段 | 子任务 ID |
| --- | --- |
| 确认周期/路径 | P0-S0 |
| 短视频平台（抖音/B站/快手/小红书/微博） | P0-S1 |
| 文字平台（番茄/起点/晋江/盐选） | P0-S2 |
| Top10 题材簇 + 雷达结构 | P0-S3 |
| 短视频五维评分 + 候选 concept | P0-S4 |
| 用户选定题材 | P0-S5 |
| 立项 + gate | P0-S6 |

## 3. Dispatch Table

| ID | 执行体 | 命令 / 参考 | 产出 |
| --- | --- | --- | --- |
| P0-S0 | `cli` | `python engine/novel_cli.py intel paths` | manifest 记录路径 |
| P0-S1 | `cli` | `skills/novel-market-scan/scripts/intel_scan.py` → `intel scan --period week [--platforms douyin,bilibili,...]` | `intel/radar/YYYY-Www.md` |
| P0-S2 | `hybrid` | CLI 写入「平台快照」骨架 + Agent 读 [platform-scan-guide.md](./platform-scan-guide.md) 补表 | radar `## 平台快照` 各平台表 |
| P0-S3 | `hybrid` | Agent 按 [radar-report-template.md](./radar-report-template.md) 对齐 | `## 题材簇 Top 10` 或热度榜 |
| P0-S4 | `cli` | 同上 scan（默认生成 concepts）；Agent 用 [short-video-fit-rubric.md](./short-video-fit-rubric.md) 复核 | `intel/concepts/*.md` |
| P0-S5 | `agent` | 用户确认后改 concept 状态 `approved` | `intel/concepts/<slug>.md` |
| P0-S6 | `cli` | `novel init --concept ...` + `pipeline gate --phase 1` | `novels/<slug>/canon/concept-brief.md` + `canon/nodes/phase-0.completion.json` |

## 4. Execution Order

```text
P0-S0 → P0-S1 → P0-S2（可与 S1 后并行补表）→ P0-S3 → P0-S4 → [用户] P0-S5 → P0-S6
```

## 5. Output Contract

| 产物 | 路径 |
| --- | --- |
| 雷达报告 | `intel/radar/YYYY-Www.md` |
| 套件完成清单 | `intel/radar/YYYY-Www.completion.json` |
| 候选 concept | `intel/concepts/*.md` |
| 项目完成清单 | `novels/<slug>/canon/nodes/phase-0.completion.json` |
| 立项副本 | `novels/<slug>/canon/concept-brief.md` |

## 6. Chat Summary（必报）

- 本周 Top3 题材簇 + 短视频分（/25）
- 推荐 platform_target
- 落盘路径：`intel/radar/...` 与 `...completion.json`
- 待用户确认：选 concept ①②③

**禁止：** 仅在对话中给表而不写 radar + completion。

## 7. Gate Handoff

- `novel pipeline gate --phase 1`：concept-brief + task_plan Phase0 `[x]` + 项目 `phase-0.completion.json`（P0-S5/S6 done）
- 若无项目 manifest：校验当周 `intel/radar/*.completion.json`（P0-S0–S4 done）
