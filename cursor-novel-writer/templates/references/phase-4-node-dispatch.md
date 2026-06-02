# Phase 4 节点分派（voice-brief 模板）

无独立 Skill；使用 `templates/voice-brief.md` → `novels/<slug>/canon/voice-brief.md`。

| ID | 执行体 | 产出 |
| --- | --- | --- |
| P4-S1 | `agent` | 填妥 `canon/voice-brief.md`（含 platform_target） |
| P4-S2 | `cli` | `novel node sync --phase 4` → `phase-4.completion.json` |

## Gate

`novel pipeline gate --phase 5` 需 Phase 4 manifest `complete`。
