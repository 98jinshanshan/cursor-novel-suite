---
name: doc-router
description: |
  Rule-level document routing before bulk reads. Query summary index via doc-router preflight,
  then read only selected docs within budget. Use for 执行前读取文档、Cursor 卡顿、文档拥堵、
  找相关文档、DOC_CHAIN 检索、RealPipeline / VideoRender / ComfyUI 长任务、
  需要读取大量 docs / reports / receipts.
license: MIT
metadata:
  author: cursor-novel-suite
  version: "1.0.0"
---

# DocRouter — 规则级文档路由（防卡死）

## When to Use

- 执行长任务前需要读取大量 `docs/`、回执、索引、报告
- 用户提到 Cursor 卡顿、文档拥堵、state.vscdb 膨胀
- RealPipeline / VideoRender / ComfyUI / 文档治理等跨目录任务
- 需要按 DOC_CHAIN / DOC_META 找相关文档

## 强制规则

```text
先 doc-router preflight，再读取原文。
preflight 未通过，不得全量读取。
high/critical 风险时，只允许摘要索引，不允许全文追链。
未命中文档不得追链式全量阅读；扩大范围须二次 query。
```

## Workflow

### 1. Preflight（必须）

```powershell
Set-Location -LiteralPath "G:/CURSOR"
$env:PYTHONPATH="G:/CURSOR/src"
.\.venv\Scripts\python.exe -m novel_suite.cli doc-router preflight "<任务描述>" --json
```

检查输出：

| 字段 | 动作 |
| --- | --- |
| `status=blocked` | 停止长任务；仅摘要模式或请用户重启 Cursor |
| `risk_level=high/critical` | 禁止全文读取；只用 `selected_docs` 中的 summary/header |
| `selected_docs` | **唯一**优先读取列表 |
| `read_budget` | 遵守 `max_docs` / `max_chars_per_doc` |

### 2. 按需 Query（扩大范围时）

```powershell
.\.venv\Scripts\python.exe -m novel_suite.cli doc-router query "<关键词>" --top-k 10 --json
```

禁止：直接 `Read` 整个 `docs/` 目录或索引总表全文。

### 3. 按预算读细节

- 使用 `tools/safe-runner/safe_read.py` 或 IDE 分段读取
- 单文档不超过 `read_budget.max_chars_per_doc`
- 聊天中只粘贴路径 + 摘要 + 关键句，不粘贴全文

### 4. 索引维护（索引过期或首次使用）

```powershell
.\.venv\Scripts\python.exe -m novel_suite.cli doc-router build --root G:/CURSOR --json
.\.venv\Scripts\python.exe -m novel_suite.cli doc-router validate --json
```

## 索引范围

| scope | 路径 |
| --- | --- |
| `cursor_project` | `G:/CURSOR` README、docs、novel-suite、src、tests |
| `workflow_os_docs` | Project_10 Workflow OS `docs/**/*.md`（只索引，不修改） |
| `active_novel` | `novels/.active` 对应书的 canon/chapters/reviews/video |

## 与防卡死联动

- 优先读取 `Test-CursorStateHealth.ps1 -Json` 输出的 `risk_level`
- 复用 `tools/safe-runner/` 做受限读取
- 复用 `tools/local-accel/` 做环境探测（不替代 DocRouter）

## 禁止

- 读取 `G:/SOLO小说项目`、`G:/Reasonix/SOLO小说视频项目`
- 全量粘贴 docs / 回执 / 长 JSON 进聊天
- 自动清理 state.vscdb 或删除聊天历史
- 联网下载 embedding 模型（须用户手动安装）

## References

- CLI 模块：`src/novel_suite/core/doc_router.py`
- Cursor 规则：`.cursor/rules/doc-router.mdc`
- 向量后端报告：`novel-suite/doc-router/vector_backend_report.md`
- 工具脚本：`tools/doc-router/`
