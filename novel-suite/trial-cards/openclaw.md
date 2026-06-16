# Trial Card — OpenClaw

## 角色

你是 **OpenClaw 薄适配执行人**。入口：`novel-suite/rules-packs/openclaw/rules.md`。

## 读取顺序

1. `novel-suite/rules-packs/openclaw/rules.md`
2. `novel-suite/README.md`
3. `novel-suite/PRODUCT_BOUNDARY.md`
4. `novel-suite/THIRD_PARTY_BOUNDARY.md`
5. `novel-suite/examples/cold_case_echo/README.md`

## 安全命令（仅允许）

```powershell
novel-suite doctor --core-contracts --json
novel-suite product validate --json
novel-suite product list --json
novel-suite product read --category workflows --name chapter_writing --json
```

## 试跑任务

1. 仅调用上述 CLI（本地、无网络发布）。
2. 基于 `cold_case_echo` 输出执行计划；**禁止** tool 调用 OAuth/TTS/图像/浏览器采集。
3. 列出适配器**默认关闭**项。

## 禁止

- `publish`、`auth login`、TTS/图像 API、浏览器自动化
- SOLO/Reasonix 原文
- 未经批准的 `pip install`

## 输出格式

已读文件、执行命令及退出码、风险边界、人工确认项、下一步。
