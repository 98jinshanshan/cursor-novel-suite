# 向量记忆栈验证（Sprint 1.2）

> SOLO 节点 3：Qdrant + M3E，JSONL 为权威源，Qdrant 为检索索引。

## 1. 安装

```powershell
cd G:\CURSOR
.\platforms\install-memory-stack.ps1 -InstallDocker -InstallPython
```

或手动：

```powershell
docker run -d --name novel-suite-qdrant -p 127.0.0.1:6333:6333 -v novel-suite-qdrant-storage:/qdrant/storage qdrant/qdrant:latest
pip install -e ".[memory]"
```

## 2. 环境变量

```powershell
$env:QDRANT_URL = "http://127.0.0.1:6333"
$env:MEMORY_EMBED_BACKEND = "m3e"
$env:MEMORY_EMBED_MODEL = "moka-ai/m3e-base"
```

未装 `sentence-transformers` 时自动回退 **hash**（256 维，仅冒烟）；生产请用 M3E（768 维）。

## 3. 探测

```powershell
py -3 -m novel_suite.cli memory probe --project novels/novel-837dd4f1 --json
```

预期 `details.qdrant.reachable: true`，`details.embed.backend: m3e`（或 hash 回退）。

## 4. 写入 + 同步

```powershell
py -3 -m novel_suite.cli memory store `
  --project novels/novel-837dd4f1 --layer L4 `
  --tags "character,林骁" `
  --text "林骁：26岁，深褐眼睛，东亚面孔" --json

py -3 -m novel_suite.cli memory sync --project novels/novel-837dd4f1 --reembed --json
```

`--reembed`：切换 embed 后端后必须重嵌再同步（维度 256↔768 不兼容）。

## 5. 检索

```powershell
py -3 -m novel_suite.cli memory search `
  --project novels/novel-837dd4f1 `
  --query "林骁眼睛" --track writing --json
```

有 Qdrant 时走混合检索（Qdrant 优先，失败回退 JSONL）。

## 6. 故障排除

| 现象 | 处理 |
|------|------|
| `MEMORY_QDRANT_UNAVAILABLE` | 设 `QDRANT_URL`；`docker start novel-suite-qdrant` |
| `pip install qdrant-client` | `pip install -e ".[memory]"` |
| 检索为空 / 分数异常 | `memory sync --reembed` 后重试 |
| M3E 首次慢 | 模型下载缓存于 `~/.cache/huggingface` |

## 7. 安全（文档 D CHK-005）

Qdrant 绑定 **127.0.0.1**，勿暴露公网；无认证仅限本机开发。
