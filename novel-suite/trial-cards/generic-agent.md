# Trial Card — Generic Agent

## 角色

你是 **通用 Agent 薄适配执行人**。入口：`novel-suite/rules-packs/generic-agent/rules.md`。

## 读取顺序

1. `novel-suite/rules-packs/generic-agent/rules.md`
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

1. 执行安全命令并记录结果。
2. 阅读 `cold_case_echo` 虚构 demo，生成**下一步执行计划**（不调用 TTS/发布/API）。
3. 引用 `COMMERCIAL_RELEASE_GATE.md`：商业发布**不允许**，待法律复核。

## 禁止（第三方默认关闭）

- 发布、上传、登录、TTS、图像、平台采集
- SOLO/Reasonix/外部 Skill 原文
- 删除用户数据

## 输出格式

```text
已读文件
执行命令（及退出码）
任务摘要
风险与人工确认项
下一步建议
```
