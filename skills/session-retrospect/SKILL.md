---
name: session-retrospect
description: |
  After Cursor context compaction, ingest session-archives and update questions inventory,
  rules candidates, and ledger status. Use for 整理压缩对话、更新问题总表、session retrospect.
license: MIT
metadata:
  author: cursor-novel-suite
  version: "1.0.0"
---

# Session Retrospect（压缩对话归纳）

## When to Use

- 用户说：整理压缩对话、更新问题总表、session retrospect、压缩后复盘
- `session-ledger.jsonl` 有 `ingest: pending` 行
- `preCompact` Hook 已归档到 `docs/audit/session-archives/`

## Prerequisites

1. Read [SESSION-ARCHIVE.md](../../docs/standards/SESSION-ARCHIVE.md)
2. 工作区根目录含 `docs/audit/`

## Workflow

1. **Ingest（确定性）**

   ```bash
   py -3 platforms/session-archive.py ingest-pending --workspace .
   ```

2. **读增量**：打开 `session-ledger.jsonl` 中 `ingest=pending` 对应的
   `session-archives/<conv>/<folder>/user-queries.json`

3. **更新 Part 1 总表** `docs/audit/session-questions-inventory.md`：
   - 为新 U-序号写摘要行
   - 去重合并到 §2 主题表（T01…）；再现标 `🔁`
   - 文首注明：来源 archive 路径 + `compact-meta.json` 时间戳

4. **规则候选** `docs/audit/session-rules-candidates.md`：
   - 🔁≥2 的诉求 → 候选规则一行（不直接改 `.mdc`）

5. **回写 ledger**：将已处理行的 `ingest` 改为 `ingested`（或 meta `ingest_status`）

6. **汇报**：新增主题数、🔁 主题、archive 路径列表

## 禁止

- 不要声称「压缩丢失内容」——全文在 `transcript.jsonl`
- 不要跳过 ingest 直接编造 U-序号

## References

- [session-questions-inventory.md](../../docs/audit/2026-06-01-session-questions-inventory.md)
- [session-lifecycle-reorder](../session-lifecycle-reorder/SKILL.md)

## Sprint 4-7 备注

复盘时请将 Sprint 4-7 引入的能力纳入主题表：MCP Server、多平台 publish、番茄小说发布、analytics 数据追踪、snowflake/character_gen、平台感知 `target-platform`。
