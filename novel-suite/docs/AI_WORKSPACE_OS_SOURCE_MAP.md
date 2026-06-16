# AI_Workspace_OS 源映射

规格源根：`G:\Users\admin\Documents\AI_Workspace_OS\...\小说视频工具链三项目评审_20260610`

| G:\CURSOR 文件 | 规格源 | 层级 | 可商业化 |
| --- | --- | --- | --- |
| `novel-suite/PRODUCT_BOUNDARY.md` | `统一产品定义.md` | 核心 | 是 |
| `novel-suite/THIRD_PARTY_BOUNDARY.md` | `商业核心禁入规则.md` + `第三方适配器默认关闭规则.md` | 核心 | 是 |
| `core/contracts/story_bible.schema.md` | `故事圣经生成Prompt_自有版` + P0入门包 | 核心 | 是 |
| `core/contracts/chapter_context.schema.md` | `上下文快照_模板` + `progress.schema.json` | 核心 | 是 |
| `core/contracts/scene_to_video.schema.md` | `分镜旁白Contract_自有版` + storyboard.schema | 核心 | 是 |
| `core/contracts/asset_registry.schema.md` | `资产注册表_SCHEMA.md` | 核心 | 是 |
| `core/gates/deai_review_gate.md` | `审稿DeAI门禁_自有版` | 核心 | 是 |
| `core/gates/publishing_gate.md` | `发布前门禁_自有版` | 核心 | 是 |
| `core/gates/source_risk_gate.md` | `必须署名_替换_隔离_禁用清单.md` | 核心 | 是 |
| `core/workflows/novel_project_init.md` | P0入门包 + `writer init/scan` 实践 | 核心 | 是 |
| `core/workflows/novel_to_video.md` | `小说视频化流程_自有版` | 核心 | 是 |
| `prompt-packs/PP-001..003` | `交付包候选/PROMPT_PACK/` | 核心 | 候选 |
| `rules-packs/*` | `多IDE适配契约.md` | 适配 | 是 |
| `adapters/*` | TTS/图像隔离说明 | 适配器 | 隔离声明 |
| `src/novel_suite/**` | CURSOR 工程 | 工程候选 | 须代码审查 |
| `cursor-novel-writer/skills/**` | 工程候选 | 参考/候选 | 不直接商用原文 |

## 处理策略缩写

- **禁入：** MediaCrawler、ebooklib 入核心
- **隔离：** edge-tts、ComfyUI、SD
- **署名：** 未来 THIRD_PARTY_NOTICES
- **自有：** PP/Core/Workflows 全文
