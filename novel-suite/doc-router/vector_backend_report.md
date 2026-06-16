# DocRouter 向量后端探测报告

> 生成阶段：DocRouter-1 · 2026-06-17  
> 主索引：**SQLite FTS5**（无向量依赖即可运行）

## 结论摘要

| 后端 | 状态 | 说明 |
| --- | --- | --- |
| **SQLite FTS5** | ✅ 主路径 | `doc-router build/query/preflight` 默认使用；无需 Qdrant/embedding |
| **Qdrant** | 可选 | 见下方探测；不可用时优雅降级 |
| **sentence-transformers** | 可选 | 仅 `memory` extra；**未自动下载模型** |

## Qdrant 探测

- **配置位置：** `platforms/docker-compose.memory.yml`
- **默认 URL：** `http://127.0.0.1:6333`
- **依赖：** `pip install -e ".[memory]"` → `qdrant-client>=1.9`
- **启动（手动）：** `docker compose -f platforms/docker-compose.memory.yml up -d`
- **DocRouter-1 范围：** 仅探测连通性；**不向 Qdrant 写入文档索引**（第一阶段 FTS 已满足路由需求）

运行探测：

```powershell
.\.venv\Scripts\python.exe -c "from novel_suite.core.doc_router import probe_qdrant; import json; print(json.dumps(probe_qdrant(), ensure_ascii=False, indent=2))"
```

若 `available: false` → 继续使用 SQLite FTS，不影响 preflight/query。

## 本地 Embedding 模型

- **包：** `sentence-transformers`（`pyproject.toml` `[project.optional-dependencies] memory`）
- **DocRouter 策略：** **禁止自动下载** HuggingFace 模型
- 若需语义向量检索，用户须：
  1. `pip install -e ".[memory]"`
  2. 手动下载并缓存模型（如 `BAAI/bge-small-zh-v1.5`）
  3. 后续阶段可在 `doc_router.py` 增加可选 `vector_query()` 分支

探测：

```powershell
.\.venv\Scripts\python.exe -c "from novel_suite.core.doc_router import probe_embedding_model; import json; print(json.dumps(probe_embedding_model(), ensure_ascii=False, indent=2))"
```

## 无向量后端时

SQLite FTS + LIKE 回退 + 摘要/header 索引 **可独立工作**，满足：

- Top-K 文档命中
- DOC_CHAIN / DOC_META 字段检索
- preflight 读取预算
- Cursor health 联动

## 后续可选增强（非 DocRouter-1 范围）

- 将 DocRouter 命中写入 Qdrant collection（与 `novel_suite.memory` 共用基础设施）
- 混合检索：FTS 召回 + 向量 rerank
- LlamaIndex 适配（见 `novel-suite/agent-architecture/FUTURE_ORCHESTRATOR_BACKENDS.md`）
