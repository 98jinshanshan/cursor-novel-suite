# Phase 1 节点分派（story-init）

## Entry Triggers

新建小说、开书、立项、`novel init`

## Dispatch Table

| ID | 执行体 | 命令 / 参考 | 产出 |
| --- | --- | --- | --- |
| P1-S0 | `cli` | `novel active` / `novel list` | 确认无冲突 slug |
| P1-S1 | `agent` | [story-template.md](./story-template.md) | `story.md` 草稿 |
| P1-S2 | `cli` | `novel init --title ... --premise ... --concept ...` | `novels/<slug>/` 脚手架 |
| P1-S3 | `cli` | `pipeline gate --phase 2` | `canon/project.json` |
| P1-S4 | `agent` | 填写 `task_plan.md` Phase 1 `[x]` | task_plan |
| P1-S5 | `cli` | `node validate --phase 1 --project ...` | `canon/nodes/phase-1.completion.json` |

## Output Contract

- `novels/<slug>/story.md`, `canon/project.json`, `canon/nodes/phase-1.completion.json`
- **Chat：** slug、路径、下一步 Phase 2 delegate

## Gate

`pipeline gate --phase 2` 需 Phase 1 `[x]` + project.json schema OK
