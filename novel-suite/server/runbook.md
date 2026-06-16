# UI Agent Server — 运行 Runbook

## 路线 A：stdlib HTTP（默认）

### validate（不长驻）

```powershell
Set-Location -LiteralPath "G:\CURSOR"
$env:PYTHONPATH="G:\CURSOR\src"
.\.venv\Scripts\python.exe -m novel_suite.cli server validate --json
```

检查项：server 模块 import、`api-contract.json`、agent-entry-menu、workbench static、doctor/list/scan-demo/ip-demo runners。

### run（阻塞至 Ctrl+C）

```powershell
.\.venv\Scripts\python.exe -m novel_suite.cli server run --host 127.0.0.1 --port 8765
```

- Workbench：`http://127.0.0.1:8765/workbench`
- API 基址：`http://127.0.0.1:8765/api`

### API 端点（契约）

见 [api-contract.json](../server/api-contract.json)

## 路线 B：可选 FastAPI/uvicorn

**不自动安装。** 用户确认后：

```powershell
.\.venv\Scripts\python.exe -m pip install "novel-suite[server]"
```

说明：`pyproject.toml` 中 `[project.optional-dependencies] server` 为预留；当前实现为 stdlib，validate/run 均不依赖 FastAPI。

## Contract-only

不启动 server 时，可直接调用 Core/CLI：

```powershell
.\.venv\Scripts\python.exe -m novel_suite.cli ip-production-demo run --json
```

## 边界

- 所有 API 返回 Result Contract 形态
- `commercial_release_allowed=false` 不变
- market-scan：demo only；live scan 返回 `SCAN_LIVE_BLOCKED`
