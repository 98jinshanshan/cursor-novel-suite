---
name: novel-market-scan
description: |
  Weekly/monthly trending web-fiction topic radar for Chinese platforms, with short-video fit scoring.
  Use for 扫榜、题材雷达、选题、market scan, 短视频选题, Phase 0 选品.
license: MIT
compatibility: Requires monorepo root (intel/ directory). V1.2 NEC dispatch + completion manifest.
metadata:
  author: cursor-novel-writer
  version: "1.2.0"
---

# Novel Market Scan（Phase 0 — P-1）

**上游选品 Skill**：在 `story-init` / `novel init` 之前，生成市场情报并驱动 `concept-brief` 立项。

工作区须为 **Novel Suite 根**（含 `.novel-suite-root`）。不确定时先运行：

```text
novel suite doctor
```

## Node Execution Contract (NEC)

**执行前必读：** [references/node-dispatch.md](./references/node-dispatch.md)（分派表 + 完成清单）。

1. 将用户自然语言拆解为 `P0-S0` … `P0-S6`
2. 按表调用 CLI / Agent，**禁止**仅在对话中输出表格
3. 落盘 `intel/radar/YYYY-Www.md` + `intel/radar/YYYY-Www.completion.json`
4. 用户确认后 `init --concept` → `canon/nodes/phase-0.completion.json`
5. 对话框只报 **Top3 摘要 + 路径**（全文见落盘文件）

## When to Use

- 写书前：当周/当月什么题材最火？
- 短视频推书：什么类型适合做成 summary/drama？
- 用户说：扫榜、选题、题材分析、market radar

## Outputs（固定路径）

| 产物 | 路径 |
| --- | --- |
| 周雷达报告 | `intel/radar/YYYY-Www.md` |
| 套件完成清单 | `intel/radar/YYYY-Www.completion.json` |
| 概念立项包（立项前） | `intel/concepts/<slug>.md` |
| 立项后副本 | `novels/<slug>/canon/concept-brief.md` |
| 项目 Phase0 清单 | `novels/<slug>/canon/nodes/phase-0.completion.json` |

## Workflow（与分派表一致）

1. **P0-S0** `novel intel paths`
2. **P0-S1** CLI 扫描（短视频平台）：

   ```bash
   python engine/novel_cli.py intel scan --period week
   ```

   - Wrapper：`skills/novel-market-scan/scripts/intel_scan.py` → `engine/scripts/intel_scan.py`
   - 写入 radar + `*.completion.json`

3. **P0-S2** Agent 按 [platform-scan-guide.md](./references/platform-scan-guide.md) 补全 radar 内 `## 平台快照`（番茄/起点/晋江/盐选）
4. **P0-S3** 对齐 [radar-report-template.md](./references/radar-report-template.md)
5. **P0-S4** [short-video-fit-rubric.md](./references/short-video-fit-rubric.md) + concepts
6. **P0-S5** 用户确认 → concept `approved`
7. **P0-S6** `novel init --concept` + `pipeline gate --phase 1`

## Gate（与 novel-pipeline）

- **无** `canon/concept-brief.md` → 禁止 Phase 1+
- `task_plan.md` Phase 0 须 `[x]`
- `canon/nodes/phase-0.completion.json` 中 P0-S5、P0-S6 为 `done`

## CLI 辅助

```bash
python engine/novel_cli.py intel paths
python engine/novel_cli.py intel scan --period week
python engine/novel_cli.py intel scan --period week --platforms douyin,bilibili
python engine/novel_cli.py intel scan --demo --period week
python engine/novel_cli.py node validate --phase 0
python engine/novel_cli.py pipeline gate --phase 1
```

## References

- [Node dispatch（NEC）](./references/node-dispatch.md)
- [Platform scan guide](./references/platform-scan-guide.md)
- [Short-video fit rubric](./references/short-video-fit-rubric.md)
- [Radar report template](./references/radar-report-template.md)
- [novel-pipeline Phase 0](../novel-pipeline/SKILL.md)
- [NODE-EXECUTION-CONTRACT](../../../docs/standards/NODE-EXECUTION-CONTRACT.md)

Do **not** scrape logged-in pages or violate platform ToS.
