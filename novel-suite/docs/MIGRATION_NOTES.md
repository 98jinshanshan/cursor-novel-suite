# Migration Notes

## 为何新增 `novel-suite/` 而非重命名子项目

- `cursor-novel-writer` / `cursor-novel-video` 为历史工程名，大量脚本与测试依赖路径。
- 产品层去 Cursor 化通过 **平行目录** 实现，避免破坏 CI 与 Skills 安装路径。
- `src/novel_suite` 保持 Python 包名；`novel-suite/` 为**文档与契约**对齐层。

## 双轨共存

| 层 | 路径 | 职责 |
| --- | --- | --- |
| 产品 | `novel-suite/` | 边界、Pack、契约 |
| 工程 | `src/novel_suite/` | CLI/MCP 实现 |
| Agent | `cursor-novel-*/skills/` | 对话入口（逐步指向 Core） |

## 未来收敛（可选）

1. 根 README 主品牌改为 Novel Suite（子项目降为 Implementation）
2. `AGENTS.md` 首段指向 `novel-suite/rules-packs/codex/AGENTS.md`
3. JSON Schema 从 `core/contracts/*.schema.md` 导出到 `novel-suite/schema/`

## 回滚

删除 `novel-suite/`、`NOVEL_SUITE_*.md` 及 README/INDEX 追加段落即可。
