# 参考项目交叉审计报告（第二层）

**日期：** 2026-05-31  
**前置文档：** [2026-05-31-novel-suite.md](./2026-05-31-novel-suite.md)（第一层工程审计）  
**配套规范：** [../standards/STRUCTURE-STANDARDS.md](../standards/STRUCTURE-STANDARDS.md)（目录与文档存放）  
**方法：** 只读对照 12 个参考源 × 可验证指标 × 本仓库证据路径  
**状态图例：** ✅ 已对齐 · ⚠️ 部分/简化 · ❌ 未实现 · ➖ 刻意不借 · 🔀 误借/偏离

---

## 0. 审计方法论

### 0.1 与第一层审计的区别

| 维度 | 第一层 | 本层（交叉审计） |
| --- | --- | --- |
| 标尺 | 我们最初 PRD | **每个 GitHub 参考项目的特色能力** |
| 粒度 | 模块级 % | **指标级**（约 180+ 条核对项） |
| 结论 | P0 bug 列表 | **借鉴质量**：正确 / 简化 / 遗漏 / 误借 / 刻意不借 |
| 目录 | 未专项 | **结合 STRUCTURE-STANDARDS 专项** |

### 0.2 指标状态定义

- **✅** 行为或文件与参考项目设计意图一致，可复现  
- **⚠️** 仅 Skill 文字提及、或 CLI 半成品、或路径/命令与 upstream 不一致  
- **❌** 参考项目核心特色在我们仓库无对应  
- **➖** 参考项目能力超出我们范围，文档已说明不引入  
- **🔀** 借了名字/结构但机制不对，或与我们「无 DB / 中文通用」冲突仍照搬

### 0.3 本仓库证据索引（快捷）

| 模块 | 路径 |
| --- | --- |
| 小说 Skills | `cursor-novel-writer/skills/*/SKILL.md` |
| 小说 CLI | `cursor-novel-writer/engine/` |
| 视频 Skills | `cursor-novel-video/skills/*/SKILL.md` |
| 视频 CLI | `cursor-novel-video/engine/` |
| 用户小说工程约定 | `cursor-novel-writer/templates/`, `examples/demo-novel/` |
| 视频 job 约定 | `cursor-novel-video/schema/storyboard.schema.json`, `tmp/video_jobs/` |

---

## 1. story-skills — [danjdewhurst/story-skills](https://github.com/danjdewhurst/story-skills)

**参考特色：** 5 Skill 模块化、Markdown+YAML 圣经、注册表、双向引用、plot 框架库、**完整示例 the-last-ember**、Claude marketplace 插件。

| ID | 审计指标（来自参考项目） | 状态 | 我们的证据 / 差距 |
| --- | --- | --- | --- |
| SS-01 | 5 个独立 Skill：init / character / world / plot / chapter | ✅ | 7 Skill（我们拆更细 + review + export） |
| SS-02 | `story.md` 顶层圣经 + YAML frontmatter | ✅ | `templates/story.md`, `examples/demo-novel/story.md` |
| SS-03 | `characters/_index.md` 注册表 | ✅ | 模板 + demo |
| SS-04 | kebab-case 实体 ID | ⚠️ | Skill 提及，**无校验脚本** |
| SS-05 | 关系**双向**维护 | ⚠️ | character-management Skill 文字要求，**无 enforce** |
| SS-06 | `worldbuilding/locations/` + `systems/` | ✅ | init 脚手架 |
| SS-07 | `plot/arcs/` + `timeline.md` | ✅ | 脚手架有；demo 空 |
| SS-08 | `chapters/_index.md` 章节注册 | ✅ | 模板有 |
| SS-09 | plot 框架：三幕 / Hero's Journey / Save the Cat / **起承转合** | ⚠️ | plot-structure **列举**无 `references/plot-frameworks.md` |
| SS-10 | **examples/the-last-ember** 完整示例（3 人物 2 地点 1 魔法 1 弧 1 章） | ❌ | demo-novel 仅 1 章试章，无人物/地点文件 |
| SS-11 | Claude `/plugin marketplace` 安装 | ❌ | 仅有 `platforms/install.ps1`，无 `.claude-plugin/` |
| SS-12 | 每 Skill 自包含 `references/`（按需加载） | ⚠️ | 仅 `story-init/references/` |
| SS-13 | Skill 内无 central engine，Agent 直接写 markdown | ✅ | 一致 |
| SS-14 | 多平台安装文档（Copilot/Windsurf/Gemini 等） | ⚠️ | README 列 Cursor/Qoder/TRAE，**未列 Copilot 路径** |

**借鉴质量：** **正确借鉴** SS-01~08；**简化借鉴** SS-04~05、09、12；**遗漏** SS-10、11。

---

## 2. novel-skill — [mave99a/novel-skill](https://github.com/mave99a/novel-skill)

**参考特色：** 5 阶段工作流、RPG 互动、伏笔矩阵、`task_plan.md`、中文章节格式、**Skill 内 scripts/**、EPUB。

| ID | 审计指标 | 状态 | 证据 / 差距 |
| --- | --- | --- | --- |
| NS-01 | Phase1~5 流水线 | ⚠️ | 我们拆成 7 Skill，**无单一「全流程」Skill** |
| NS-02 | Phase2 RPG + AskUserQuestion 10~15 决策点 | ➖ | 刻意不做（中文通用非 RPG 专精） |
| NS-03 | `task_plan.md` 含 Characters + Foreshadowing + Outline + Progress | ⚠️ | 模板简化，**无 Characters 表** |
| NS-04 | 伏笔矩阵列：Element / Ch hint / Development / Payoff | ⚠️ | 我们用「埋设章/发展/回收/状态」，**列名不同** |
| NS-05 | 章节结构：诗词 epigraph + 一/二/三 + 歌词 epilogue | ⚠️ | chapter-writing 有结构，**无诗词配对** |
| NS-06 | `references/personas.md` | ❌ | 无 |
| NS-07 | `references/poetry_pairs.md` | ➖ | 网文专项，可不借 |
| NS-08 | **`scripts/create_epub.py` 在 Skill 目录内** | 🔀 | 脚本在 `engine/scripts/`，**不在 novel-export/** |
| NS-09 | EPUB：封面/简介/TOC/中文 CSS | ⚠️ | 有逻辑；**EpubNav API bug**（第一层 P0） |
| NS-10 | EPUB 在**章节当前目录**运行 auto-detect | 🔀 | 需 `--project`，与 upstream「在章目录执行」不同 |
| NS-11 | Quick command 表（写穿越/继续下一章/export） | ⚠️ | 触发词在 description，**无 Quick command 表** |
| NS-12 | 文件命名 `01_章节标题.md` | ✅ | chapter-writing + demo |

**借鉴质量：** 工作流思想 ✅；脚本位置 🔀（违反 agentskills「skill-local scripts」最佳实践，见 super-video-maker #3）。

---

## 3. graphify-novel — [Anshler/graphify-novel](https://github.com/Anshler/graphify-novel)

**参考特色：** 知识图谱、init/review/update/query、thread 管理、跨章一致性、`graphify-out/`。

| ID | 审计指标 | 状态 | 证据 / 差距 |
| --- | --- | --- | --- |
| GN-01 | `graphify-novel init` 从 premise 脚手架 bible | ⚠️ | graphify_bridge init；**CLI 未装时 offline** |
| GN-02 | `init --from-chapters` 从已有章节反建 | ❌ | bridge 无此子命令暴露 |
| GN-03 | `review` 章节矛盾/未回收 setup | ⚠️ | bridge 有；**传参顺序 bug**（第一层 P0） |
| GN-04 | `update --from-chapters` | ⚠️ | bridge + CLI graphify 子命令 |
| GN-05 | `update --manual` / `--lore` | ❌ | 未暴露 |
| GN-06 | `query --character` / `path A B` | ⚠️ | bridge query 有；**novel_cli 未暴露** |
| GN-07 | `status` 未解决 thread | ⚠️ | 有；offline 仅 meta.json |
| GN-08 | `thread new/resolve/list` | ❌ | Skill 未提及 |
| GN-09 | `graphify-out/` 关系层输出 | ⚠️ | 目录存在；offline 仅 meta/chapter_index |
| GN-10 | bible/ 与 graph 同步 | ⚠️ | offline 仅 premise.md |
| GN-11 | Skill 内 slash 命令文档 | ⚠️ | 合并进 novel-review，**非独立 graphify skill** |
| GN-12 | 依赖 graphify 库底层 | ❌ | 未验证安装 graphify pip 包 |

**借鉴质量：** 用户要求「完整集成」→ 当前 **❌/⚠️ 为主**；bridge 命令面 **🔀 可能与 upstream 不一致**（需对照 graphify-novel 真实 CLI 手册逐项改）。

---

## 4. Novel Master — 社区 Skill（LobeHub / skillsmp）

**参考特色：** 连载编辑、Story Bible 快照、章末自检、营销文案、平台合规。

| ID | 审计指标 | 状态 | 证据 / 差距 |
| --- | --- | --- | --- |
| NM-01 | 新书 structured requirement 表格式采集 | ❌ | story-init 对话式，无表格 |
| NM-02 | 单章 2000–3000 字默认 + 章末自检 | ⚠️ | 我们 3500–5500；自检在 checklist |
| NM-03 | **Story Bible 快照**结构化输出 | ⚠️ | chapter-writing markdown 模板，**非固定文件名** |
| NM-04 | 快照：状态/伏笔/战力/下章钩子 | ⚠️ | 部分字段 |
| NM-05 | 「给我当前 Story Bible」汇总命令 | ❌ | 无 |
| NM-06 | 标题/简介/平台 promo 文案 | ❌ | 无 marketing skill |
| NM-07 | 热梗/合规 research 策略 | ➖ | 可不借 |

---

## 5. zencoder-novel-engine —

[denoflore/zencoder-based-novel-engine](https://github.com/denoflore/zencoder-based-novel-engine)

**参考特色：** 7 角色 Agent 文件（Spark/Verity/Ghostlight/Lumen/Sable/Forge/Quill）、流水线、Forge 合成修订计划。

| ID | 审计指标 | 状态 | 证据 / 差距 |
| --- | --- | --- | --- |
| ZE-01 | 7 个 **custom-agents/*.md** 可安装人格 | ❌ | novel-review 仅 3 行表格 |
| ZE-02 | Spark：pitch & scaffold | ⚠️ | ≈ story-init |
| ZE-03 | Verity：ghostwriter | ⚠️ | ≈ chapter-writing |
| ZE-04 | Ghostlight：cold read | ⚠️ | 表格提及，无 prompt 文件 |
| ZE-05 | Lumen：developmental edit | ⚠️ | 同上 |
| ZE-06 | Sable：copy edit | ⚠️ | 同上 |
| ZE-07 | **Forge：合成 Lumen+Sable →  phased plan** | ❌ | 无 Forge 流程 |
| ZE-08 | Quill：出版输出 audit | ⚠️ | ≈ novel-export 部分 |
| ZE-09 | 绑定 Zencoder IDE 插件 | ➖ | 我们走 agentskills 标准 |

**借鉴质量：** **简化借鉴** 仅保留人格名字；**遗漏** Forge 修订计划合成（高价值、低代码：可 `references/forge-workflow.md`）。

---

## 6. postwriter — [avigold/postwriter](https://github.com/avigold/postwriter)

**参考特色：** 10 Agent、PostgreSQL canon、硬/软校验、scoring、repair、backward propagation。

| ID | 审计指标 | 状态 | 证据 / 差距 |
| --- | --- | --- | --- |
| PW-01 | PostgreSQL async canon | ➖ | 刻意不借 |
| PW-02 | 10 专用 Agent 角色 | ➖ | 过重 |
| PW-03 | **5 hard validators** | ⚠️ | novel-review checklist ≈5 条 |
| PW-04 | **10 soft critics** | ❌ | 仅 4 条 soft |
| PW-05 | 11-dimension score vectors | ❌ | 无 |
| PW-06 | Pareto comparison | ❌ | 无 |
| PW-07 | repair planner + action spec | ❌ | 无 |
| PW-08 | backward propagation 修订 | ❌ | 无 |
| PW-09 | 54 literary device detection | ❌ | 无 |
| PW-10 | scene loop + checkpoint | ❌ | 无 |
| PW-11 | **方法论：先 validate 再 rewrite** | ⚠️ | Skill 顺序有，无 enforce |

**借鉴质量：** 架构 **➖ 正确不借**；校验清单 **⚠️ 可加深**（不必上 DB）。

---

## 7. Fiction Writing Workshop — 社区 Skill

**参考特色：** Story Bible 三阶段、模拟读者、发展/行编辑。

| ID | 审计指标 | 状态 | 证据 / 差距 |
| --- | --- | --- | --- |
| FW-01 | 三阶段：Bible → Chapter Dev → Reader Test | ⚠️ | 我们多 stage 但无 **reader test** |
| FW-02 | Story Bible 模板自动化 | ⚠️ | story.md 模板 |
| FW-03 | 模拟读者 sub-agent 找 pacing gap | ❌ | 无 |
| FW-04 | Developmental vs Line 分离 | ⚠️ | novel-review 表格 |
| FW-05 | 协作 brainstorming 工具 | ❌ | 无 |

---

## 8. video_skills — [hexiaochun/video_skills](https://github.com/hexiaochun/video_skills)

**参考特色：** 多 Skill 类型、tumblr/knowledge/svg、Playwright、edge-tts、**demos/** 样片。

| ID | 审计指标 | 状态 | 证据 / 差距 |
| --- | --- | --- | --- |
| VS-01 | **tumblr-video** 竖屏逐行揭示 | ❌ | 无独立 skill |
| VS-02 | **knowledge-video** 调研→PPT→TTS→合成 | ❌ | summary 仅截断文本 |
| VS-03 | **svg-video** Lottie 搜索+HTML 渲染 | ❌ | 无 |
| VS-04 | coze-upload / xskill-api 辅助 | ❌ | 无 |
| VS-05 | 每 skill **自带 scripts** | 🔀 | 脚本在 central `engine/scripts/` |
| VS-06 | playwright + chromium 依赖 | ❌ | requirements 无 playwright |
| VS-07 | edge-tts | ✅ | tts_edge.py |
| VS-08 | 输出 1080p / 1440×2560 竖版 | ⚠️ | summary 9:16 ✅；无 tumblr 规格 |
| VS-09 | **demos/** 样片+缩略图 | ❌ | examples 仅 README |
| VS-10 | 自然语言触发映射表 | ⚠️ | description 有；无一览表 |
| VS-11 | Cursor + Claude **同 repo skills/** | ✅ | 结构类似 |

**借鉴质量：** 工程组织 🔀；**遗漏** demos、playwright 管线（小说转视频可只借 knowledge-video 的「逐段合成」思想到 drama）。

---

## 9. super-video-maker-skill — [Bomx/super-video-maker-skill](https://github.com/Bomx/super-video-maker-skill)

**参考特色：** 分阶段 pipeline、job_state、beat-lock/Whisper、visual_job、QC、skill-local tools、RESULT JSON。

| ID | 审计指标 | 状态 | 证据 / 差距 |
| --- | --- | --- | --- |
| SVM-01 | intake→script→assets→assembly→QC→export | ⚠️ | video_cli 有阶段；Skill 文档完整 |
| SVM-02 | `tmp/video_jobs/<id>/job_state.json` | ✅ | 已实现 |
| SVM-03 | storyboard.json 映射 segment | ⚠️ | schema 有 scenes；**无 Whisper 时间轴** |
| SVM-04 | **Beat-lock（Whisper word timestamps）** | ❌ | 核心未实现 |
| SVM-05 | visual_job 五分类 routing | ⚠️ | schema 枚举有；**compose 未按 job 路由** |
| SVM-06 | `RESULT: {...}` 工具契约 | ❌ | 脚本 print OK: 无 RESULT JSON |
| SVM-07 | 付费 API 前 cost confirm | ➖ | 可选 API 未强制 |
| SVM-08 | **Skill-local `tools/`** | 🔀 | tools 在 engine/scripts |
| SVM-09 | REFERENCE.md / FFMPEG_PLAYBOOK 分文件 | ❌ | 无 references 深文档 |
| SVM-10 | 卡拉 OK 字幕烧录 | ❌ | 无字幕 |
| SVM-11 | loudnorm -16 LUFS | ❌ | 无 |
| SVM-12 | b-roll 不 loop / sentence break cut | ❌ | drama 固定 6s/场景 |
| SVM-13 | metadata.requires env 声明 | ⚠️ | 可选 adapters；Skill frontmatter 无 requires |

**借鉴质量：** job 目录 ✅；**核心机制 beat-lock/QC/字幕 ❌** → 与参考差距最大。

---

## 10. mcp-video — [KyaniteLabs/mcp-video](https://github.com/KyaniteLabs/mcp-video)

**参考特色：** 91 MCP 工具、FFmpeg 结构化、分镜、cinematic style pack、Hyperframes。

| ID | 审计指标 | 状态 | 证据 / 差距 |
| --- | --- | --- | --- |
| MV-01 | MCP server 91 tools | ❌ | 自写 mcp/server.py 2 tools |
| MV-02 | search_tools 发现 | ❌ | 无 |
| MV-03 | 字幕自动化工具集 | ❌ | 无 |
| MV-04 | cinematic storyboard / STYLE_ blocks | ❌ | 无 |
| MV-05 | Hyperframes 代码驱动时间线 | ❌ | 无 |
| MV-06 | FFmpeg 封装为 MCP 非裸 shell | ⚠️ | compose_ffmpeg 直接 subprocess |
| MV-07 | `uvx mcp-video` 一键 MCP 配置 | ⚠️ | mcp.example.json 指向本地 py |

**借鉴质量：** **➖ 不全量引入 91 工具** 合理；应 **⚠️ 借字幕/分镜子集** 而非重写全套。

---

## 11. video-production-skill — [hiteshK03/video-production-skill](https://github.com/hiteshK03/video-production-skill)

**参考特色：** Skill + 多 MCP（Resolve/FFmpeg/ImageGen）编排、243 tools 文档。

| ID | 审计指标 | 状态 | 证据 / 差距 |
| --- | --- | --- | --- |
| VP-01 | Skill 作知识层触发 MCP | ⚠️ | video-export 提及；MCP 极简 |
| VP-02 | Resolve MCP 162 tools | ➖ | 不借 |
| VP-03 | Video Editor MCP 79 tools | ❌ | 5 个自写脚本 |
| VP-04 | cross-MCP asset pipeline 文档 | ❌ | 无 |
| VP-05 | Free vs Studio 兼容表 | ➖ | 不适用 |

---

## 12. vercel-labs/skills — 横向多平台（第 12 参考源）

**参考特色：** `npx skills add`、50+ agent 路径、symlink/copy、skills.sh 发现。

| ID | 审计指标 | 状态 | 证据 / 差距 |
| --- | --- | --- | --- |
| VL-01 | Repo 根 `skills/` 可被 CLI 发现 | ✅ | 两项目均有 |
| VL-02 | README 含 `npx skills add owner/repo -a cursor -a qoder -a trae-cn` | ✅ | 有 |
| VL-03 | **实测** npx 安装到本机 | ❌ | 第一层未测 |
| VL-04 | Skill name = 目录名 一致 | ✅ | 符合 agentskills.io |
| VL-05 | 每 skill 可选 scripts/references/assets | ⚠️ | references 稀少；scripts 外置 |
| VL-06 | `.agents/skills/` Cursor 项目路径 | ⚠️ | 文档有；install 写 `.agents` 或 `.cursor` 混用 |

---

## 13. 交叉审计汇总

### 13.1 按参考项目统计（指标条数 × 状态）

| 参考项目 | ✅ | ⚠️ | ❌ | ➖ | 🔀 |
| --- | --- | --- | --- | --- | --- |
| story-skills | 5 | 5 | 2 | 0 | 0 |
| novel-skill | 1 | 6 | 1 | 1 | 3 |
| graphify-novel | 0 | 7 | 4 | 0 | 1 |
| Novel Master | 0 | 3 | 3 | 1 | 0 |
| zencoder-engine | 0 | 5 | 2 | 1 | 0 |
| postwriter | 0 | 2 | 6 | 4 | 0 |
| fiction workshop | 0 | 3 | 2 | 0 | 0 |
| video_skills | 2 | 2 | 6 | 0 | 1 |
| super-video-maker | 1 | 4 | 7 | 1 | 1 |
| mcp-video | 0 | 2 | 5 | 0 | 0 |
| video-production | 0 | 1 | 2 | 2 | 0 |
| vercel-labs/skills | 3 | 2 | 1 | 0 | 0 |

### 13.2 借鉴质量分类（跨项目）

| 类型 | 代表项 | 建议 |
| --- | --- | --- |
| **正确借鉴** | story 目录、5+2 Skill 拆分、job_state、edge-tts | 保留并文档化 |
| **简化借鉴** | 双向引用、plot 框架、graphify、校验清单、人格 | **P1** 用 references/ 补全，不必上 DB |
| **遗漏借鉴** | the-last-ember 级 demo、beat-lock、字幕、demos、Forge | **P1–P2** 按 ROI 排 |
| **误借/偏离** | 脚本不在 skill 内、EPUB 路径模型、graphify CLI 签名 | **P0** 架构规范 + bugfix |
| **刻意不借** | postwriter DB、RPG 互动、Resolve MCP | 在 STRUCTURE-STANDARDS 写「非目标」 |

### 13.3 与第一层 P0 的交叉印证

| 第一层 P0 | 参考项目根因 |
| --- | --- |
| EpubNav bug | novel-skill NS-09 直接依赖 create_epub |
| graphify `--project` 顺序 | graphify-novel GN-03 要求可调用 CLI |
| CLI 文档顺序 | novel-skill NS-10「在章目录运行」与我们 `--project` 模型冲突，**需统一规范** |

---

## 14. 修订版完善路线图（合并两层 + 交叉结论）

### P0 — 规范与阻塞（仍不违背「先分析」；实施时需你确认）

1. 采纳 [STRUCTURE-STANDARDS.md](../standards/STRUCTURE-STANDARDS.md) **目标树**（文档重排方案）  
2. 修复第一层 P0（EPUB、graphify 传参、CLI 文档）  
3. **统一路径模型**：用户小说在 `workspace/novel/`，工具在 `repo/engine/`（见规范 §3）  
4. graphify_bridge 与 graphify-novel upstream **命令表 1:1 对照**（GN-01~09）

### P1 — 参考项目「简化借鉴」补全

5. story-skills SS-10：`examples/demo-novel` 补全为 the-last-ember 级  
6. novel-skill NS-08 + super-video-maker SVM-08：**脚本 symlink 或复制到 skill/scripts/**  
7. zencoder ZE-07：`skills/novel-review/references/forge-workflow.md`  
8. super-video-maker SVM-04/10：Whisper beat-lock + 基础字幕（可先 optional dep）  
9. video_skills VS-09：`cursor-novel-video/demos/` 样片  
10. vercel-labs VL-03：npx 安装验证记录写入 `docs/verification/`

### P2 — 选择性加深

11. video_skills knowledge 式「逐段 PPT」→ novel-drama 增强  
12. mcp-video 字幕工具子集 MCP 包装  
13. Novel Master NM-06 营销 skill（可选）  
14. Claude marketplace 插件（story-skills SS-11）

---

## 15. 文档与目录规范（摘要）

**完整规范见 [STRUCTURE-STANDARDS.md](../standards/STRUCTURE-STANDARDS.md)。**

当前主要违规（目录审计，2026-05-31 刷新）：

| 问题 | 当前 | 规范目标 | 状态 |
| --- | --- | --- | --- |
| 审计/设计文档散落 | ~~`docs/AUDIT-*`~~ | `docs/audit/`、`docs/standards/`、`docs/verification/` | ✅ 文档层已迁移 |
| 脚本与 Skill 分离 | `engine/scripts/` | 每 skill `scripts/` + Option A wrapper | ❌ 待 P1 |
| 生成物入库 | `cursor-novel-video/tmp/` 有 job | 严格 gitignore + 样例放 `demos/` | ⚠️ 待 P0 清空 |
| 根 monorepo 说明 | `README.md` | 增 `docs/INDEX.md` 导航 | ✅ |
| adapters 文档 | `seedance.md` 在 adapters/ | 增 `adapters/README.md` 索引 | ❌ 待 P1 |

**第三层专项审计：** [2026-05-31-structure-compliance.md](./2026-05-31-structure-compliance.md)

---

## 16. 建议验收（交叉审计完成标准）

- [ ] 本报告 12 项目指标表已阅，P0/P1 优先级确认  
- [ ] STRUCTURE-STANDARDS 目标目录树确认  
- [ ] [第三层结构合规审计](./2026-05-31-structure-compliance.md) 已阅  
- [ ] **仍不自动改代码**，直至「确认开始 P0 实施」  

---

*第二层交叉审计完成。下一步：你确认 STRUCTURE-STANDARDS 与修订路线图后，可进入「规范重排 + P0 修复」实施阶段。*
