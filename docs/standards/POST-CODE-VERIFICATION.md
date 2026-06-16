# 代码交付前问题项检查

**版本：** 1.0（2026-06-02，用户确认）  
**Cursor 规则：** [post-code-problems-check.mdc](../../.cursor/rules/post-code-problems-check.mdc)（`alwaysApply: true`）

---

## 目的

避免 Agent 在代码生成阶段结束后遗留 IDE **Problems** 中的错误（pyright、markdownlint 等），确保「任务完成」与「可合并质量」一致。

---

## 流程

```text
代码改动完成
    → powershell -File platforms/final-verify.ps1
    → ReadLints / Problems（改动路径）
    → 相关 pytest（若适用；final-verify 已含则以其为准）
    → 有问题？修复 → 再验
    → 收尾粘贴 Final Verification 块 → 才可结束任务
```

详见 [FINAL-VERIFICATION.md](./FINAL-VERIFICATION.md)。

**CI 双保险：** `.github/workflows/ci.yml` 的 `final-verify` job 运行 `platforms/final-verify.sh`（与本地
`final-verify.ps1` 同套检查）；`lint` / `typecheck` / `test` job 并行兜底。

---

## Agent 职责

| 步骤 | 动作 |
| --- | --- |
| 1 | 对本轮修改的文件跑 linter / Problems |
| 2 | 改动 engine/CLI 时跑子项目 smoke 测试 |
| 3 | 发现问题在本轮修掉 |
| 4 | 收尾汇报验证结果（一行即可） |

---

## 用户职责

- 一般无需操作；若 Agent 报告「遗留阻塞」，按说明补环境或授权

---

## 与 DECISION-PRINCIPLE 的关系

| 文档 | 管什么 |
| --- | --- |
| [DECISION-PRINCIPLE.md](./DECISION-PRINCIPLE.md) | **选什么方案**（Agent 推荐、用户确认） |
| 本文档 | **交什么质量**（改代码后必验 Problems） |

---

*与 [STRUCTURE-STANDARDS.md](./STRUCTURE-STANDARDS.md) 同属仓库协作规范。*
