# Novel Suite Trial Cards — 多 IDE 试跑任务卡

**阶段：** B6 多 IDE 试跑矩阵  
**原则：** 各 IDE/Agent 仅作**薄适配执行人**；不启动 GUI、不写全局配置、不调用第三方服务。

## 使用方式

1. 在目标 IDE 加载对应 `novel-suite/rules-packs/<agent>/` 入口文件。
2. 将本目录下 `<agent>.md` 任务卡全文交给 Agent。
3. Agent 仅执行任务卡中的**安全命令**；禁止项见各卡与 `COMMERCIAL_RELEASE_GATE.md`。

## 任务卡索引

| Agent | 任务卡 | Rules Pack 入口 |
| --- | --- | --- |
| Cursor | [cursor.md](cursor.md) | `rules-packs/cursor/rules.md` |
| Codex | [codex.md](codex.md) | `rules-packs/codex/AGENTS.md` |
| TRAE CN | [trae-cn.md](trae-cn.md) | `rules-packs/trae-cn/rules.md` |
| Qoder | [qoder.md](qoder.md) | `rules-packs/qoder/rules.md` |
| OpenClaw | [openclaw.md](openclaw.md) | `rules-packs/openclaw/rules.md` |
| Generic Agent | [generic-agent.md](generic-agent.md) | `rules-packs/generic-agent/rules.md` |

## 仓内分发（B6 验证用）

```powershell
powershell -File platforms/install-rules-packs.ps1 -Copy -DestRoot .agent-rules -Agents cursor,codex,trae-cn,qoder,openclaw,generic-agent
```

**不要**使用 `-UseIdeDirs` 写入用户全局目录。

## 矩阵文档

见 [docs/NOVEL_SUITE_B6_IDE_TRIAL_MATRIX.md](../../docs/NOVEL_SUITE_B6_IDE_TRIAL_MATRIX.md)。
