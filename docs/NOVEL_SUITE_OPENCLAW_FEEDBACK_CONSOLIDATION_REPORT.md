# Novel Suite OpenClaw 真实反馈合并承接报告

**日期：** 2026-06-13  
**任务：** 合并 R 阶段 dry-run + O1 OpenClaw 复测 — **只读承接**，**不**自动修订。

---

## 来源

| 线 | 文件数 | 路径 |
| --- | --- | --- |
| R dry-run | 3 | `.tmp/novel-suite-q/`（R1/R2/R3） |
| O1 复测 | 4 | `.tmp/novel-suite-n/trial-decision-fill-kit/` |

---

## 合并结论（5 项修订候选）

| ID | 优先级 | 摘要 |
| --- | --- | --- |
| RC-CONSOL-001 | **P0** | CLI PATH：统一 `python -m novel_suite.cli` fallback |
| RC-CONSOL-002 | **P0** | O1 Runbook PP-001 路径与 `PP-001_novel_project_init.md` 不一致 |
| RC-CONSOL-003 | **P1** | 入口过多；需唯一「首次 O1 试用」推荐起点 |
| RC-CONSOL-004 | **P1** | PP-001 主文件顶部加强非一键成书/非商业批准提示 |
| RC-CONSOL-005 | **P2** | 短剧样例 README 增加首次只读阅读顺序 |

产物：`novel-suite/openclaw-feedback-consolidation/`

---

## 未执行（边界）

- 未改 PromptPack、O1 Runbook、`rules-packs/openclaw`、`safe_commands`
- `auto_apply=false`、`promptpack_changed=false`、`gate_changed=false`
- `commercial_release_allowed=false`、`verdict=blocked` 未改

---

## 下一阶段

- **S1：** 人工确认 P0/P1/P2 修订候选
- **S2：** 确认后执行 P0 文档修订包（优先 RC-001、RC-002）
- **S3：** OpenClaw / Codex / Cursor 复测 15 分钟路线
