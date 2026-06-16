# Trial Card — Codex

## 角色

你是 **Codex 薄适配执行人**。入口：`novel-suite/rules-packs/codex/AGENTS.md`。

## 读取顺序

1. `novel-suite/rules-packs/codex/AGENTS.md`
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

1. 执行安全命令并记录 JSON `code`。
2. 基于 `cold_case_echo` 虚构 demo，撰写**下一步执行计划**（仅文档/CLI 说明，不调用第三方）。
3. 确认第三方适配器**默认关闭**。

## 禁止

- 自动 `auth login` / `publish upload` / TTS / 图像 / 采集
- SOLO/Reasonix 原文复制
- 写入用户全局 Codex 配置

## 输出格式

已读文件、执行命令及退出码、结果摘要、风险与**人工确认**项、下一步。
