# PromptPack Friction Review（Q2）

**真实首跑卡点 → 修订候选** — **不**自动修改 PP-001/002/003。

```yaml
real_friction_available: false
auto_promptpack_changed: false
revision_candidate_only: true
external_call_performed: false
```

## 流程

1. 用户按 P2 首跑指南试跑 PromptPack。
2. 填写 [friction_record_template.md](friction_record_template.md) → `.tmp/novel-suite-q/promptpack-friction-review/`。
3. 可选生成 [revision_candidate_template.md](revision_candidate_template.md) — 仅为候选，非自动合并。

## 校验

```powershell
novel-suite promptpack-friction-review validate --json
```
