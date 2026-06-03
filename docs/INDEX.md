# 文档索引

本 Monorepo 的说明与审计文档统一放在 `docs/` 下。

## 审计报告

| 文档 | 层级 | 说明 |
| --- | --- | --- |
| [audit/2026-05-31-novel-suite.md](./audit/2026-05-31-novel-suite.md) | 第一层 | 工程现状、E2E、P0 bug |
| [audit/2026-05-31-reference-crosswalk.md](./audit/2026-05-31-reference-crosswalk.md) | 第二层 | 12 个 GitHub 参考项目交叉指标 |
| [audit/2026-06-01-workflow-validation-synthesis.md](./audit/2026-06-01-workflow-validation-synthesis.md) | 第三层 | Workflow 编排与验证/去 AI 合成 |
| [audit/2026-06-02-full-reference-gap-matrix.md](./audit/2026-06-02-full-reference-gap-matrix.md) | 第四层 | 十二项目全维度差距矩阵（含 D11/P-1） |
| [audit/2026-06-03-solo-ch01-入府-audit.md](./audit/2026-06-03-solo-ch01-入府-audit.md) | 试写审稿 | SOLO 第1章《入府》+ 一二三节拍格式说明 |
| [../intel/README.md](../intel/README.md) | P-1 | 市场情报目录（radar / concepts） |

## Agent 入口

| 文档 | 说明 |
| --- | --- |
| [../AGENTS.md](../AGENTS.md) | **对话主路径**：触发语、多 IDE、Phase 0 扫榜 |
| [standards/STRUCTURE-STANDARDS.md §1.4](./standards/STRUCTURE-STANDARDS.md) | Novel Suite 根契约（`.novel-suite-root`） |
| `novel suite doctor` | 工作区 / Skills / 引擎自检 |

## 规范与计划

| 文档 | 说明 |
| --- | --- |
| [standards/STRUCTURE-STANDARDS.md](./standards/STRUCTURE-STANDARDS.md) | 目录架构与文档存放规范 |
| [standards/DECISION-PRINCIPLE.md](./standards/DECISION-PRINCIPLE.md) | 决策呈现原则（Agent 推荐、用户确认） |
| [standards/SKILLS-INSTALL.md](./standards/SKILLS-INSTALL.md) | Skill 清单与 Phase 0 对照 |
| [standards/POST-CODE-VERIFICATION.md](./standards/POST-CODE-VERIFICATION.md) | 代码交付前 Problems/linter 检查（强制） |
| [standards/NODE-EXECUTION-CONTRACT.md](./standards/NODE-EXECUTION-CONTRACT.md) | 节点执行契约（NEC）：分派表 + 完成清单 |
| [standards/DIRECTORY-ARCHITECTURE.md](./standards/DIRECTORY-ARCHITECTURE.md) | **目录架构 2.0** + 版本迭代规则 |
| [standards/layout-phase-map.json](./standards/layout-phase-map.json) | Phase→路径机器可读映射 |
| [standards/WORKSPACE-LAYOUT.md](./standards/WORKSPACE-LAYOUT.md) | 左侧目录速查 |
| [../novel-suite.code-workspace](../novel-suite.code-workspace) | 可选多根工作区视图 |
| [workflow/README.md](./workflow/README.md) | Phase 0–9 + 视频工作流导航 |
| [plans/NEC-10-enrichment-matrix.md](./plans/NEC-10-enrichment-matrix.md) | 节点加厚成熟度矩阵 |
| [standards/GITHUB-RELEASE.md](./standards/GITHUB-RELEASE.md) | GitHub 创建仓库、上传与标准排版 |
| [plans/ROADMAP.md](./plans/ROADMAP.md) | 合并审计后的完善路线图 |
| [RELEASE-READINESS.md](./RELEASE-READINESS.md) | **发布就绪**：E2E 示例、清理脚本、验收表 |
| [RELEASE-NOTES-2.0.md](./RELEASE-NOTES-2.0.md) | **2.0.0** 版本说明（功能冻结） |
| [audit/2026-05-31-structure-compliance.md](./audit/2026-05-31-structure-compliance.md) | 第三层：目录与文档存放合规审计 |

## 子项目

| 项目 | README |
| --- | --- |
| 小说 | [../cursor-novel-writer/README.md](../cursor-novel-writer/README.md) |
| 视频 | [../cursor-novel-video/README.md](../cursor-novel-video/README.md) |

## 验证记录（部分完成）

| 平台 | 文档 |
| --- | --- |
| Cursor | [verification/cursor.md](./verification/cursor.md) |
| Qoder | [verification/qoder.md](./verification/qoder.md) |
| TRAE CN | [verification/trae-cn.md](./verification/trae-cn.md) |
| SOLO 克隆 | [verification/solo-clone-checklist.md](./verification/solo-clone-checklist.md) |
| SOLO NEC 测试对话 | [verification/solo-nec-dialogue.md](./verification/solo-nec-dialogue.md) |
| SOLO 选题→第一章 | [verification/solo-phase0-to-ch01-dialogue.md](./verification/solo-phase0-to-ch01-dialogue.md) |
| **SOLO 2.0 命令状态（复制粘贴）** | [verification/solo-2.0-命令状态.md](./verification/solo-2.0-命令状态.md) |
| **SOLO 2.0 测试命令（详解）** | [verification/solo-2.0-test-commands.md](./verification/solo-2.0-test-commands.md) |
| NEC 三端验收 | [verification/NEC-smoke-matrix.md](./verification/NEC-smoke-matrix.md) |
