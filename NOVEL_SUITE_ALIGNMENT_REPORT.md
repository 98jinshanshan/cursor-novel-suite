# Novel Suite 工程内核对齐报告

**生成日期：** 2026-06-10  
**规格源（只读）：** `AI_Workspace_OS/.../小说视频工具链三项目评审_20260610`  
**工程目标：** `G:\CURSOR`

---

## 1. 当前工程结构

```text
G:\CURSOR/
├─ .novel-suite-root          # 工作区契约 v2.0
├─ src/novel_suite/           # 统一 Python 包（CLI/MCP/writer/video/auth/analytics/memory）
├─ cursor-novel-writer/       # 小说 Skill + legacy engine + schema + templates
├─ cursor-novel-video/        # 视频 Skill + legacy engine + adapters + schema
├─ docs/                      # 标准、审计、验证、路线图
├─ platforms/                 # install-skills/mcp/hooks、final-verify
├─ novels/ intel/             # 用户数据区
├─ tests/                     # 统一包测试（270+）
└─ AGENTS.md README.md        # Agent 与人工入口
```

**架构：** Agent 层（Skills）→ Legacy 引擎（各子项目 `engine/`）→ 统一包层（`novel_suite`）→ 契约层（JSON Schema + NEC）。

---

## 2. 已有能力画像

### 2.1 小说写作

| 能力 | 实现位置 | Novel Suite 对应 |
| --- | --- | --- |
| 扫榜 / intel | `writer/intel.py`, `intel_scan.py` | 可选适配器（采集默认关闭） |
| 立项 init | `writer/init.py`, `scan_bridge.py` | Core workflow: novel_project_init |
| 章节 draft/promote | `writer/chapter.py` | Core workflow: chapter_writing |
| 阶段 gate | `writer/gate.py`, `pipeline_gate.py` | Core gates |
| 审稿 / DeAI | `novel-review` skill, `deai_audit.py` | Core gate: deai_review_gate |
| EPUB 导出 | `writer/export.py`, `create_epub.py` | **可选适配器**（ebooklib AGPL） |
| 多书 registry | `writer/registry.py`, `project_clean.py` | Core contract: asset_registry |
| Snowflake / 角色卡 | `writer/snowflake.py`, `character_gen.py` | Core 辅助（LLM 可选） |

### 2.2 小说视频化

| 能力 | 实现位置 | Novel Suite 对应 |
| --- | --- | --- |
| 分镜 storyboard | `video/storyboard/`, `storyboard.schema.json` | Core contract: scene_to_video |
| 角色素材 CVDP | `video/character/` | Core 结构 + 图像适配器隔离 |
| 静帧 / 合成 | `video/stills/`, `video/compose/` | video-export 适配器 |
| TTS | `tts_edge.py`, `edge-tts` 依赖 | **TTS 适配器，默认关闭** |
| ComfyUI / SD | `adapters/comfyui_*` | **image-generation 适配器，默认关闭** |
| 发布门禁 | `video/gate/`, `platform_publish_gate.py` | Core gate: publishing_gate |
| 平台上传 | `video/publish/`, `auth/platforms/` | **platform-publishing 适配器，默认关闭** |

### 2.3 Skill / CLI / MCP

| 层 | 路径 | 状态 |
| --- | --- | --- |
| Writer Skills | `cursor-novel-writer/skills/`（10 个） | 工程候选，需 Rules Pack 薄映射 |
| Video Skills | `cursor-novel-video/skills/`（5 个） | 工程候选 |
| 统一 CLI | `novel-suite` → `novel_suite.cli` | 工程执行核心候选 |
| MCP | `novel_suite/mcp_server.py` | 工程执行核心候选 |
| Cursor Rules | `.cursor/rules/` | 需对齐 `novel-suite/rules-packs/cursor/` |

---

## 3. 与 AI_Workspace_OS 规格对应关系

| 规格文档 | G:\CURSOR 现状 | 对齐动作 |
| --- | --- | --- |
| 统一产品定义 | README 仍偏 Cursor 工程表述 | 新增 `novel-suite/PRODUCT_BOUNDARY.md` |
| 多 IDE 适配契约 | 仅 Cursor/Qoder/TRAE install 脚本 | 新增 `novel-suite/rules-packs/*` |
| 核心/适配层边界 | 代码中 TTS/发布已存在但未文档化隔离 | 新增 `THIRD_PARTY_BOUNDARY.md` + adapters/ |
| P0 创作者入门包 | templates + skills 分散 | Core workflows + prompt-packs PP-001/002 |
| P0 视频化样例包 | video skills + schema | Core workflows + PP-003 + scene_to_video contract |
| 商业核心禁入规则 | 无根级 LICENSE/THIRD_PARTY_NOTICES | 文档边界 + 计划补 NOTICES |
| 资产注册表 | 无中立 asset_registry 文档契约 | `core/contracts/asset_registry.schema.md` |
| 交付包候选 | 仅在 AI_Workspace_OS | 映射至 `docs/AI_WORKSPACE_OS_SOURCE_MAP.md` |

---

## 4. 缺失项

| 缺失 | 优先级 | 本次处理 |
| --- | --- | --- |
| 去 Cursor 化产品层目录 `novel-suite/` | P0 | ✅ 新增 |
| 中立 Core contracts（Markdown） | P0 | ✅ 新增 |
| Prompt Pack 工程化（PP-001~003） | P0 | ✅ 新增 |
| 多 IDE Rules Pack | P0 | ✅ 新增 6 环境 |
| 适配器默认关闭说明 | P0 | ✅ 新增 4 类 |
| 根级 `THIRD_PARTY_NOTICES.md` | P1 | 计划项，未本次写入 |
| 根级 `LICENSE` | P1 | 计划项 |
| CLI 自动读取 `novel-suite/core` | P2 | 需用户确认后接入 |
| Skill 原文 → Pack 自动同步 | P2 | 禁止自动复制，人工维护 |

---

## 5. 高风险依赖与第三方边界

| 依赖/工具 | 风险 | 处理策略 |
| --- | --- | --- |
| `ebooklib` | AGPL | 禁入核心；EPUB 为可选/替换 |
| `edge-tts` | LGPL + 服务条款 | TTS 适配器，默认关闭 |
| ComfyUI / SD WebUI / ControlNet | AGPL/GPL | image-generation 适配器，默认关闭 |
| `MediaCrawler` | 平台规则 + NOASSERTION | 商业版禁用 |
| 平台 OAuth 发布 | 账号/风控 | platform-publishing，人工确认 |
| 外部 Skill 生态 | 版权/品牌 | 仅外部参考，禁入 Prompt Pack 原文 |

---

## 6. 建议新增目录（已执行）

本次采用**最小侵入**：新增 `G:\CURSOR\novel-suite/` 对齐层，不移动/重命名 `cursor-novel-writer`、`cursor-novel-video`、`src/novel_suite`。

详见 `NOVEL_SUITE_IMPLEMENTATION_PLAN.md` 与 `novel-suite/docs/MIGRATION_NOTES.md`。

---

## 7. 未修改范围确认

- `G:\SOLO小说项目` — 未触碰
- `G:\Reasonix\SOLO小说视频项目` — 未触碰
- `AI_Workspace_OS` — 只读（执行回执单独写回）
