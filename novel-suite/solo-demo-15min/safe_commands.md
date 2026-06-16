# 安全命令（只读 validate / list / read）

本 demo **仅允许**下列类命令。禁止 generate、upload、publish、adapter 执行、FFmpeg、TTS。

## CLI 调用方式

### 已安装可执行入口时（PATH 已注册）

```powershell
novel-suite product validate --json
```

### 未注册 PATH 时（推荐 fallback）

```powershell
Set-Location -LiteralPath "G:\CURSOR"
$env:PYTHONPATH="G:\CURSOR\src"
$env:PYTHONDONTWRITEBYTECODE="1"
& "G:\CURSOR\.venv\Scripts\python.exe" -m novel_suite.cli product validate --json
```

若本机 `python` 已在 PATH 且指向项目 venv，也可写 `python -m novel_suite.cli ...`（效果等同，仍须设置 `PYTHONPATH`）。

**说明：** 两种方式均为只读 validate/list/read；**不代表**允许 adapter、发布或商业 release。

## 产品层只读

```powershell
novel-suite product list --json
novel-suite product read --category workflows --name novel_project_init --json
novel-suite product read --category prompt-packs --name PP-001_novel_project_init --json
novel-suite product validate --json
```

## 门禁与自查（只读 validate）

```powershell
novel-suite commercial-release-candidate validate --json
novel-suite solo-founder-release-blocked-declaration validate --json
novel-suite solo-demo-15min validate --json
novel-suite promptpack-first-run validate --json
novel-suite multi-ide-dry-run-feedback validate --json
novel-suite solo-founder-freeze-self-check validate --json
novel-suite solo-founder-compliance-self-check validate --json
```

## 版本信息

```powershell
novel-suite version --json
novel-suite doctor --json --core-only
```

## 明确禁止

| 禁止 | 原因 |
| --- | --- |
| `writer export` / EPUB 外发 | 可能触及发布边界 |
| `video` 管线执行 | 真实 adapter / FFmpeg |
| `mcp serve` + 外部工具链 | 可能触发外部调用 |
| `git tag` / `zip` / release | 商业发布门禁 |
| 任何上传 / API 发布 | `external_call_performed` 须保持 false |
