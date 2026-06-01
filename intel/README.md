# 市场情报目录（P-1）

Monorepo 级选品空间，与 `novels/`（单书工程）分离。

| 路径 | 用途 |
| --- | --- |
| `radar/` | 周/月题材雷达报告（`novel-market-scan` 产出） |
| `concepts/` | 待立项概念包（`concept-brief.md` 副本，立项前） |

## 命名约定

- 雷达：`radar/YYYY-Www.md`（ISO 周，如 `2026-W22.md`）
- 概念：`concepts/<kebab-slug>.md`

## 工作流

1. 运行 CLI 扫描（或 Skill 同步调用）：

   ```bash
   py -3 cursor-novel-writer/engine/novel_cli.py intel scan --period week
   ```

   产出：
   - `radar/YYYY-Www.md`（热榜雷达）
   - `concepts/YYYY-Www-xx-*.md`（候选立项包）
2. 选定题材 → 将对应 `concepts/*.md` 的状态改为 `approved`
3. `novel init --concept intel/concepts/xxx.md ...` → 复制到 `novels/<slug>/canon/concept-brief.md`
4. `novel pipeline gate --phase 1` 通过后再进入世界观/写作

用户生成的 radar/concepts 默认 gitignore；本 README 与 `.gitkeep` 进仓。
