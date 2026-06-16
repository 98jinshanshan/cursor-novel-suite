# Implementation Sequence

## 已完成（2026-06-10）

1. 对齐报告 + 实施计划（仓库根）
2. `novel-suite/` 产品层全集
3. README / docs/INDEX 入口链接

## 建议顺序（工程接入）

```text
Phase 1  契约校验 CLI（doctor --core-contracts）
Phase 2  install-skills 分发 rules-packs 映射
Phase 3  writer/video CLI --help 指向 core/workflows
Phase 4  LICENSE + THIRD_PARTY_NOTICES 根级落地
Phase 5  ebooklib 隔离 / EPUB adapter 决策
Phase 6  pytest 全量 + E2E 冷案回声
```

## 不在此序列

- 修改 SOLO / Reasonix
- 自动同步 Skill 正文到 Prompt Pack
- 默认启用任何 adapter
