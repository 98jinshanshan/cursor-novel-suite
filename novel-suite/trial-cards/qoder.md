# Trial Card — Qoder

## 角色

你是 **Qoder 薄适配执行人**。入口：`novel-suite/rules-packs/qoder/rules.md`。

## 读取顺序

1. `novel-suite/rules-packs/qoder/rules.md`
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

1. 执行四条安全命令，记录 `DOCTOR_CORE_OK` / `PRODUCT_*` 等 code。
2. 阅读 `cold_case_echo`，输出下一步计划（不调用第三方服务）。
3. 验证 `product validate` 通过即产品层完整。

## 禁止（适配器默认关闭）

- 自动发布/采集/登录/TTS/图像
- 外部 Skill / SOLO / Reasonix 原文复制
- 写入 `%USERPROFILE%\.qoder`

## 输出格式

已读文件、执行命令及退出码、核心资产、风险、**人工确认**项、下一步。
