# No Auto PromptPack Change Policy（Q2）

```yaml
auto_promptpack_changed: false
revision_candidate_only: true
real_friction_available: false
```

## 规则

- **不得**自动修改 `novel-suite/prompt-packs/PP-001_novel_project_init.md` 等原文
- **不得**在无真实用户卡点记录时生成「修订已完成」结论
- 修订候选仅存于 `.tmp/novel-suite-q/promptpack-friction-review/` 或后续 R2 方案
- `external_call_performed` 须保持 false（首跑为文档/Prompt 层）

## 升级路径

真实卡点 → Q2 候选 → R2 修订方案 → 人工确认后合并（非 Q 阶段）
