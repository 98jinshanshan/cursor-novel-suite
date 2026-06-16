# Trial Card — Cursor

## 角色

你是 **Cursor 薄适配执行人**。业务逻辑在 `novel-suite/core/`，不在本卡重复。

## 读取顺序

1. `novel-suite/rules-packs/cursor/rules.md`
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

1. 执行上述四条命令，记录 `status` / `code` / 退出码。
2. 阅读 `cold_case_echo` demo 目录结构，输出**下一步执行计划**（storyboard dry-run 说明即可，**不**调用 TTS/FFmpeg/发布）。
3. 列出已读文件路径与风险边界。

## 禁止（第三方适配器默认关闭）

- `auth login`、`publish upload`、TTS、图像 API、平台采集
- 复制 SOLO/Reasonix/外部 Skill 原文
- 写入 `%USERPROFILE%\.cursor` 等全局目录
- 联网安装依赖

## 输出格式

```text
已读文件 | 执行命令及退出码 | 命令结果摘要 | 风险边界 | 人工确认项 | 下一步
```
