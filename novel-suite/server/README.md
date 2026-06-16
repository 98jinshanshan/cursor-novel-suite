# UI Agent Server API

本地 API Server MVP 契约（stdlib HTTP；可选 FastAPI extra）。

```yaml
commercial_release_allowed: false
verdict: blocked
```

## 契约文件

- [api-contract.json](api-contract.json)

## CLI

```powershell
novel-suite server validate --json
novel-suite server run --host 127.0.0.1 --port 8765
```

`server validate` 不启动长驻服务。

## 依赖（可选）

```powershell
pip install "novel-suite[server]"
```

未安装 FastAPI/uvicorn 时仍可通过 stdlib `http.server` 运行。
