# Trial Card — TRAE CN

## 角色

你是 **TRAE CN 薄适配执行人**。入口：`novel-suite/rules-packs/trae-cn/rules.md`。

## 读取顺序

1. `novel-suite/rules-packs/trae-cn/rules.md`
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

1. 运行安全命令，记录结果（中文摘要）。
2. 说明 `cold_case_echo` 如何用于离线 storyboard 试跑（**不**执行 pipeline proof 除非用户明确要求且本机有 ffmpeg）。
3. 强调平台发布/TTS/图像 **默认关闭**，须**人工确认**。

## 禁止

- 发布、上传、登录、TTS、图像、外部 API
- SOLO/Reasonix 原文
- 写入 TRAE 全局规则目录

## 输出格式

已读文件、执行命令及退出码、任务摘要、风险边界、人工确认项、下一步（中文）。
