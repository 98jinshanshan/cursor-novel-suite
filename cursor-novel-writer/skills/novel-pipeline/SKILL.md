---
name: novel-pipeline
description: |
  End-to-end Chinese fiction pipeline: Phase 0 market scan → multi-novel isolation → write → review → export.
  Use for 全流程写小说、一键写作流程、pipeline、从选题到导出、扫榜后写小说.
license: MIT
compatibility: Requires full repo clone (monorepo root). Always resolve project via novels/.active or --project.
metadata:
  author: cursor-novel-writer
  version: "1.2.0"
---

# Novel Pipeline（总控）

**编排 Skill**：delegate 原子 Skill，**强制一书一目录**，禁止跨书写入。

## Node Execution Contract (NEC)

进入任一 Phase 前：**Read** 该 Phase 原子 Skill 的 [node-dispatch.md](./references/node-dispatch.md)（或子 Skill 内同名文件）。  
总控路由表见上文；微观分派与完成清单见各 Skill NEC。

## Multi-Novel Isolation（P4 — 必守）

1. **用户新书** → `novels/<auto-slug>/`（非 `my-novel`、非 repo 根）  
2. **登记** → `novels/_registry.json` + `novels/.active`  
3. **开始任何阶段前** 执行：

   ```bash
   python engine/novel_cli.py active
   # 或 novel use <slug> / --project novels/<slug>
   ```

4. **禁止** 无 `--project` 且无 active 时写入 chapters/reviews/snapshots  
5. **产物路由**（均在 `<project>/` 下）：

| 产物 | 路径 |
| --- | --- |
| 章节正文 | `chapters/NN_标题.md` |
| 验证修订稿 | `chapters/.drafts/NN_标题.md` → `novel promote` |
| 章后小结 | `canon/snapshots/chNN-after.md` |
| 审稿报告 | `reviews/chNN-review.md` |
| EPUB | `dist/*.epub` |
| 元数据 | `canon/project.json`, `canon/voice-brief.md` |
| **选品（Phase 0）** | `intel/radar/YYYY-Www.md` → `canon/concept-brief.md` |

`examples/demo-novel` 仅演示；用户生产书在 `novels/`。

## Phase 0 + 1（选品 → 立项）

```bash
# 0. 扫榜（全平台）→ intel/radar/YYYY-Www.md
python engine/novel_cli.py intel paths
python engine/novel_cli.py intel scan --period week

# 1. 用户确认 concept → init
python engine/novel_cli.py init --title "书名" --premise "..." \
  --concept ../../intel/concepts/<your-topic>.md --platform-target 番茄小说
python engine/novel_cli.py pipeline gate --phase 1
python engine/novel_cli.py list
```

## Pipeline Phases

| Phase | 名称 | Delegate | 完成标志 |
| --- | --- | --- | --- |
| **0** | **选品** | `novel-market-scan` | `canon/concept-brief.md` + task_plan Phase 0 `[x]` |
| 1 | 立项 | `story-init` | story.md + canon/project.json |
| 2 | 世界观+人物 | `worldbuilding` + `character-management` | ≥2 地点/系统，≥2 人物 |
| 3 | 大纲 | `plot-structure` | plot/arcs + foreshadowing |
| 4 | 文风契约 | voice-brief + platform_target | `canon/voice-brief.md` |
| 5 | 写作 | `chapter-writing` | `chapters/NN_*.md` |
| 6 | 验证 | `novel-review` 1–3 | `reviews/chNN-review.md`，无 blocker |
| 7 | 去 AI | deai + [platform-compliance.md](../novel-review/references/platform-compliance.md) | De-AI + Platform 全绿 |
| 8 | 再验证 | re-review | 最多 2 轮 |
| 9 | 导出 | `novel-export` | `dist/*.epub` |

## Gates（enforce — schema + 产物）

- **Phase 0** → 无 `canon/concept-brief.md` 或 Phase 0 未 `[x]` → **禁止** Phase 1+（`novel pipeline gate --phase 1`）
- **Phase 2+** → 除 task_plan `[x]` 外，CLI 校验 JSON schema（`project.json` / `progress.json`）与阶段产物（人物/大纲/章节等）
- **blocker** → 仅改 `.drafts/` 或定向修订，**禁止** Phase 7/9  
- 修订后 `novel promote <file>` 再进入 Phase 6  
- Phase 7 必查 platform_target（见 project.json）
- `novel export` 会自动执行 `pipeline gate --phase 9`（需 Phase 6/7/8 完成且最新 review 无 open blockers）

```bash
python engine/novel_cli.py pipeline validate --project novels/<slug>
python engine/novel_cli.py pipeline gate --phase 1 --project novels/<slug>
```

## CLI

```bash
python engine/novel_cli.py pipeline status --project novels/<slug>
python engine/novel_cli.py pipeline gate --phase 1 --project novels/<slug>
python engine/novel_cli.py promote 01_标题.md --project novels/<slug>
```

## References

- [Quick triggers](./references/quick-triggers.md)
- [Market scan (Phase 0)](../novel-market-scan/SKILL.md)
- [Forge workflow](../novel-review/references/forge-workflow.md)
- [Gap matrix P4](../../../docs/audit/2026-06-02-full-reference-gap-matrix.md)
