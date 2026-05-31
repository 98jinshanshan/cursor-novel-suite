# Graphify Upstream 对照表

**真机日期：** 2026-05-31  
**规程：** [graphify-upstream-verification.md](./graphify-upstream-verification.md)

## 架构结论（重要）

| 组件 | 实际形态 | 安装 |
| --- | --- | --- |
| [graphify-novel](https://github.com/Anshler/graphify-novel) | **Agent Skill**（`/graphify-novel` 斜杠命令） | `npx skills add Anshler/graphify-novel` |
| [graphify / graphifyy](https://github.com/safishamsi/graphify) | **Python CLI**（图谱 extract/update/query） | `pip install graphifyy` → `py -m graphify` |

**不存在**名为 `graphify-novel` 的可执行 CLI。旧 bridge 误调 `npx graphify-novel` 会失败。

`graphify_bridge.py` 已改为调用 **`py -m graphify`**，init/review/status 对齐 graphify-novel 的 bible 布局。

---

## 命令对照

| bridge 子命令 | 原假设 upstream | **实测映射** | 状态 |
| --- | --- | --- | --- |
| `init --premise` | `graphify-novel init` | 脚手架 `bible/` + `.graphifyignore`（graphify-novel 布局） | ✅ |
| `update --from-chapters` | graphify-novel update | `graphify update <project>`（无 LLM，AST 图） | ✅ demo-novel 69 nodes |
| `status` | graphify-novel status | 读 `graphify-out/GRAPH_REPORT.md` 或 graph.json 统计 | ✅ |
| `query --character X` | graphify-novel query | `graphify query "X relationships..."` | ✅ |
| `query --from A --to B` | graphify-novel path | `graphify path "A" "B"` | ⚠️ 无直连边时返回 no path |
| `review --chapter` | graphify-novel review | `graphify query` + novel-review skill 指引 | ⚠️ 完整 review 需 Agent |

---

## 可选依赖

```powershell
pip install graphifyy
py -3 -m graphify --help
```

语义抽取（`extract`）需 `GEMINI_API_KEY` 等；`update` 对 Markdown 章节可离线构建基础图。

---

## 推荐组合

1. **cursor-novel-writer** skills（story-init … novel-review）  
2. **`pip install graphifyy`** + bridge CLI  
3. **`npx skills add Anshler/graphify-novel`** — 斜杠命令与 bible 深度工作流  

---

*对照完成后 bridge 行为以本表为准。*
