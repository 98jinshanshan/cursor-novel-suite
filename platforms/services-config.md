# 本地服务端口绑定规范（Sprint 0 Day 2）

## 原则

所有本地推理/向量服务必须绑定 `127.0.0.1`（localhost），禁止绑定 `0.0.0.0` 暴露到局域网。

## 服务列表

| 服务 | 端口 | 绑定方式 | 状态 |
|------|------|---------|------|
| Qdrant | 6333 / 6334 | `platforms/docker-compose.memory.yml` → `127.0.0.1:6333:6333` | ✅ |
| Ollama | 11434 | `OLLAMA_HOST=http://127.0.0.1:11434` | 📌 Sprint 2 |
| ComfyUI | 8000 / 8001 | 启动参数 / 反向代理仅 localhost | ✅ 见 `.env.example` |
| SD WebUI | 7860 | `--listen 127.0.0.1` | 📌 回退 only |

## 验证命令

```powershell
# Windows — 应见 127.0.0.1:6333，不应有 0.0.0.0:6333
netstat -an | Select-String 6333

# Qdrant 仪表盘
# http://127.0.0.1:6333/dashboard
```

```bash
# Linux / macOS
ss -tlnp | grep 6333
```

## 安装

```powershell
.\platforms\install-memory-stack.ps1 -InstallDocker -InstallPython
```
