---
name: session-lifecycle-reorder
description: |
  Reorder session themes by project lifecycle (Phase 0→release→meta), mark repeat gaps.
  Use for 逻辑重排、lifecycle 复盘、按项目生命周期整理问题.
license: MIT
metadata:
  author: cursor-novel-suite
  version: "1.0.0"
---

# Session Lifecycle Reorder（逻辑重排）

## When to Use

- 用户说：逻辑重排、lifecycle 复盘、按项目生命周期整理
- Part 1 总表已更新（`session-retrospect` 之后）

## Workflow

1. Read `docs/audit/session-questions-inventory.md` §2 主题表
2. Read 或创建 `docs/audit/session-lifecycle-reordered.md`（可复制模板节）
3. 按生命周期分桶：

   | 桶 | 示例主题 |
| --- | --- |
   | 调研/立项 | T01–T09 |
   | 工程/CI | T03,T13,T14 |
   | Phase 0 / 扫榜 | T12 |
   | 多 IDE / SOLO | T02,T17 |
   | 内容试产 | T30–T33 |
   | 复盘元问题 | T34 |

4. §11「优先还债」：按再现次数 × 业务伤害排序；已闭环标 ✅
5. 交叉链接代码/文档路径；不删 JSONL 证据

## Output

- 更新 `session-lifecycle-reordered.md`
- 可选：在 `docs/INDEX.md` 审计节补链

## References

- [2026-06-01-session-lifecycle-reordered.md](../../docs/audit/2026-06-01-session-lifecycle-reordered.md)（样板）

## Sprint 4-7 新命令（复盘时纳入生命周期桶）

| 阶段 | 新增 CLI / MCP |
| --- | --- |
| 认证 | `auth login/status/logout` · MCP `auth_login` |
| 视频发布 | `video gate` · `video publish upload` · MCP `publish_upload` |
| 小说发布 | `novel publish upload/list` · MCP `novel_publish_upload` |
| 数据追踪 | `analytics record/status/report/cross-report` |
| MCP | `mcp serve` · `mcp serve --transport sse` |
| 创作辅助 | `snowflake` · `character_gen` · `writer init --target-platform` |
