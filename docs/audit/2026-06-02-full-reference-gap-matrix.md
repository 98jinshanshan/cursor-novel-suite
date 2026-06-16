# 第四层：十二参考项目全维度差距矩阵

**日期：** 2026-06-02  
**方法：** 第二层 180+ 指标 **刷新至 P3 完成后现状** + 跨项目 **10 维度** 扫描 + 用户 P4（多书隔离）需求  
**状态：** P4/P5/P-1 已实施（2026-06-02）— 见 [ROADMAP](../plans/ROADMAP.md)

**前置：** [reference-crosswalk](./2026-05-31-reference-crosswalk.md) ·
[workflow-validation-synthesis](./2026-06-01-workflow-validation-synthesis.md)

---

## 0. 扫描维度（10 维）

| 代号 | 维度 | 主要参考源 |
| --- | --- | --- |
| D1 | 工作流 / 编排 | novel-skill, zencoder, novel-pipeline |
| D2 | **多书隔离 / 工程注册** | story-skills, postwriter, super-video-maker, STRUCTURE-STANDARDS |
| D3 | 目录 / 注册表 / 模板 | story-skills, novel-skill, Novel Master |
| D4 | 写作 / 章节 / 快照 | chapter-writing, Novel Master, novel-skill |
| D5 | 验证 / 修订 / 去 AI / 平台合规 | postwriter, zencoder, Fiction Workshop, **平台规则** |
| D6 | 知识图谱 graphify | graphify-novel |
| D7 | 导出 / 营销 | novel-skill, Novel Master, zencoder Quill |
| D8 | 视频管线 | video_skills, super-video-maker, mcp-video |
| D9 | 工具 / CLI / MCP / 契约 | engine, mcp-video, super-video-maker RESULT |
| D10 | 安装 / 多平台 / 测试 | vercel-labs/skills, structure-compliance |
| **D11** | **市场情报 / 选品 / 短视频选题** | oh-story scan, InkOS radar, Manuscript research |

**图例（建议列）：**

- **必补** — P4 或阻塞多书/全流程  
- **建议** — 高 ROI，参考项目核心精华  
- **可选** — P5+，非阻塞  
- **不借** — 与范围/原则冲突，写入 STRUCTURE-STANDARDS 非目标

---

## 1. 跨项目横向：仍存在的系统性遗漏

| ID | 遗漏主题 | 参考依据 | P3 后现状 | 建议 |
| --- | --- | --- | --- | --- |
| X-01 | **多书工程隔离 + 自动 slug** | SS 一书一 bible；PW 一书一 canon；SVM job_id | ✅ `novels/` + registry + active slug | 已关闭 |
| X-02 | **活动书指针 / 禁止无 project 写入** | NS-10 auto-detect；VL 安装路径 | ✅ `.active` + `resolve_project` | 已关闭 |
| X-03 | **修订稿与正文分离** | PW-07/11 validate→rewrite | ✅ `chapters/.drafts/` + `promote` | 已关闭 |
| X-04 | **章后快照固定路径** | NM-03/04 | ✅ `canon/snapshots/chNN-after.md` 模板 | 已关闭 |
| X-05 | **平台 AI 合规标准** | NM-07；番茄/晋江/阅文公约 | ✅ platform-compliance + deai 平台节 | 已关闭 |
| X-06 | **graphify thread 管理** | GN-08 | 未暴露 | 建议 P5 |
| X-07 | **enforce 门控（非文字）** | PW-11 | ✅ `pipeline gate` + JSON schema（project/progress/registry）+ 阶段产物校验 | 已关闭 |
| X-08 | **视频 job ↔ 小说 project 绑定** | VS job + chapter path | ✅ `novel_bind.py` + storyboard/job_state + registry `video_jobs` | 已关闭 |
| **X-09** | **Phase 0 市场选品** | oh-story scan; InkOS radar | **P-1 已实施** | — |

---

## 1b. D11 市场情报（P-1 已交付 2026-06-02）

| ID | 指标 | 参考 | 交付 |
| --- | --- | --- | --- |
| P-1a | 扫榜 Skill | oh-story `story-*-scan` | `novel-market-scan` + `novel intel scan` |
| P-1b | 短视频选题评分 | InkOS 追读力 + Manuscript | `short-video-fit-rubric.md` |
| P-1c | concept-brief 立项包 | oh-story 拆文库 | `templates/concept-brief.md` |
| P-1d | Phase 0 pipeline gate | novel-pipeline | `pipeline gate`, task_plan Phase 0 |
| P-1e | 平台上传 | webnovel-writer publish | **远期** |

---

## 2. 逐项目指标刷新（❌/⚠️ → 现状 → 建议）

### 2.1 story-skills（14 项）

| ID | 指标 | 原状态 | **P3 后** | 建议 |
| --- | --- | --- | --- | --- |
| SS-04 | kebab-case ID 校验 | ⚠️ | ⚠️ | 可选：schema 校验脚本 |
| SS-05 | 关系双向维护 | ⚠️ | ⚠️ | 建议：character-management reference |
| SS-09 | plot-frameworks.md | ⚠️ | ✅ | — |
| SS-10 | the-last-ember 级 demo | ❌ | ✅ demo-novel 3人2地1规则1弧1章 | — |
| SS-11 | Claude marketplace | ❌ | ⚠️ 有 `.claude-plugin/` 桩 | 可选完善 |
| SS-12 | 每 skill references/ | ⚠️ | ⚠️ 仅 init/plot/review/marketing/pipeline | 建议：worldbuilding 模板 reference |
| SS-14 | Copilot 等安装路径 | ⚠️ | ⚠️ | 可选：platforms/copilot/README |

### 2.2 novel-skill（12 项）

| ID | 指标 | 原状态 | **P3 后** | 建议 |
| --- | --- | --- | --- | --- |
| NS-01 | 五阶段流水线 | ⚠️ | ✅ novel-pipeline 9 阶段 | — |
| NS-03 | task_plan 含 Characters 表 | ⚠️ | ⚠️ | 建议 P4：task_plan 增 characters 摘要表 |
| NS-04 | 伏笔矩阵列名对齐 | ⚠️ | ⚠️ | 可选：与 upstream 列名兼容层 |
| NS-05 | 诗词 epigraph/epilogue | ⚠️ | ⚠️ | 不借（网文专项） |
| NS-06 | personas.md | ❌ | ⚠️ 在 novel-review/personas/ | — |
| NS-08 | script 在 skill 内 | 🔀 | ✅ Option A wrapper | — |
| NS-09 | EPUB 完整 | ⚠️ | ✅ EpubNav 已修 | — |
| NS-10 | 章目录 auto-detect | 🔀 | ⚠️ 仍要 --project | **必补 P4**：registry + active 替代 auto-detect |
| NS-11 | Quick command 表 | ⚠️ | ⚠️ | 建议：novel-pipeline references/quick-triggers.md |

### 2.3 graphify-novel（12 项）

| ID | 指标 | 原状态 | **P3 后** | 建议 |
| --- | --- | --- | --- | --- |
| GN-02 | init --from-chapters | ❌ | ❌ | 可选 P5 |
| GN-05 | update --manual/--lore | ❌ | ❌ | 可选 P5 |
| GN-06 | query 暴露到 novel_cli | ⚠️ | ⚠️ graphify 子命令有 | 建议：novel_cli graphify query |
| GN-08 | thread new/resolve/list | ❌ | ❌ | 建议 P5（长篇连载） |
| GN-09~10 | graphify-out / bible 同步 | ⚠️ | ✅ 真机 69 nodes | — |
| GN-11 | 独立 graphify skill | ⚠️ | ⚠️ 合并 novel-review | 可选：companion npx skill |
| GN-12 | graphifyy 安装验证 | ❌ | ✅ | — |

### 2.4 Novel Master（7 项）

| ID | 指标 | 原状态 | **P3 后** | 建议 |
| --- | --- | --- | --- | --- |
| NM-01 | structured requirement 表 | ❌ | ❌ | 建议 P5：story-init references/requirements-table.md |
| NM-02 | 2000–3000 字默认 | ⚠️ | ⚠️ 仍 3500–5500 | 可选：voice-brief 可配置字数 |
| NM-03 | 快照固定文件 | ⚠️ | ❌ 仍无 canon/snapshots/ | **必补 P4** |
| NM-04 | 快照字段完整 | ⚠️ | ⚠️ | **必补 P4**（模板 chNN-after.md） |
| NM-05 | Story Bible 汇总命令 | ❌ | ❌ | 建议 P5：`novel_cli bible summary` |
| NM-06 | 营销文案 | ❌ | ✅ novel-marketing | — |
| NM-07 | 平台合规 | ➖ | ❌ 未做 | **必补 P4** platform-compliance.md |

### 2.5 zencoder-novel-engine（9 项）

| ID | 指标 | 原状态 | **P3 后** | 建议 |
| --- | --- | --- | --- | --- |
| ZE-01 | 7 custom-agents 可安装 | ❌ | ⚠️ 3 personas 文件 | 可选：Spark/Verity/Quill/Forge 独立 md |
| ZE-04~06 | Ghostlight/Lumen/Sable prompt | ⚠️ | ✅ personas/*.md | — |
| ZE-07 | Forge 合成 phased plan | ❌ | ✅ forge-workflow 3–5 | — |
| ZE-08 | Quill 出版 audit | ⚠️ | ⚠️ | 建议 P5：novel-export 前 Quill checklist |

### 2.6 postwriter（11 项）

| ID | 指标 | 原状态 | **P3 后** | 建议 |
| --- | --- | --- | --- | --- |
| PW-01~02 | DB / 10 Agent | ➖ | ➖ | 不借 |
| PW-03 | 5 hard validators | ⚠️ | ✅ novel-review | — |
| PW-04 | 10 soft critics | ❌ | ⚠️ 4+deai 部分覆盖 | 建议 P5：soft-critics.md 扩到 10 条 |
| PW-05~06 | scoring / Pareto | ❌ | ❌ | 不借（无 DB） |
| PW-07 | repair planner | ❌ | ⚠️ Forge 修订计划文字 | 建议 P4：reviews 内 action spec 表格 |
| PW-08 | backward propagation | ❌ | ❌ | 可选 P5：改前章需标记 retcon |
| PW-09 | 54 device detection | ❌ | ❌ | 不借；deai-checklist 已覆盖高频 |
| PW-10 | scene loop checkpoint | ❌ | ❌ | 可选 P5 |
| PW-11 | validate before rewrite | ⚠️ | ⚠️ 文档 gate，无 enforce | **必补 P4**：pipeline 禁止跳过 + CLI 可选 |

### 2.7 Fiction Writing Workshop（5 项）

| ID | 指标 | 原状态 | **P3 后** | 建议 |
| --- | --- | --- | --- | --- |
| FW-01 | Bible→Chapter→Reader Test | ⚠️ | ⚠️ Ghostlight≈Reader Test | — |
| FW-03 | 模拟读者 pacing | ❌ | ⚠️ Ghostlight 部分 | 建议：ghostlight 增 pacing 脚本问题 |
| FW-05 | brainstorming 工具 | ❌ | ❌ | 不借 |

### 2.8 video_skills（11 项）

| ID | 指标 | 原状态 | **P3 后** | 建议 |
| --- | --- | --- | --- | --- |
| VS-01 | tumblr-video | ❌ | ❌ | 可选 P6 |
| VS-02 | knowledge-video 完整 | ❌ | ⚠️ drama 逐段 | 可选：summary 增强 |
| VS-03~04 | svg / coze | ❌ | ❌ | 不借 |
| VS-05 | skill-local scripts | 🔀 | ✅ wrappers | — |
| VS-06 | playwright | ❌ | ❌ | 不借（依赖重） |
| VS-09 | demos/ | ❌ | ✅ | — |
| VS-10 | 触发映射表 | ⚠️ | ⚠️ | 建议：video README 触发一览 |

### 2.9 super-video-maker（13 项）

| ID | 指标 | 原状态 | **P3 后** | 建议 |
| --- | --- | --- | --- | --- |
| SVM-01 | 完整 pipeline | ⚠️ | ✅ | — |
| SVM-03 | Whisper 时间轴 | ⚠️ | ⚠️ beat_lock 启发式非 Whisper | 可选：optional whisper dep |
| SVM-04 | Beat-lock Whisper | ❌ | ⚠️ beat_lock.py 无 Whisper | 可选 P5 |
| SVM-05 | visual_job 路由 | ⚠️ | ⚠️ | 可选 P5 |
| SVM-06 | RESULT JSON | ❌ | ❌ | 建议 P5：脚本统一 RESULT 行 |
| SVM-09 | REFERENCE 深文档 | ❌ | ❌ | 建议：video-chapter-summary/references/PIPELINE.md |
| SVM-10 | 字幕烧录 | ❌ | ✅ burn_subtitles | — |
| SVM-11 | loudnorm -16 LUFS | ❌ | ❌ | 可选 P5 |
| SVM-12 | b-roll / sentence cut | ❌ | ⚠️ drama 固定时长 | 可选 P5 |
| SVM-13 | requires env frontmatter | ⚠️ | ⚠️ | 建议：Skill compatibility 补 ffmpeg |

### 2.10 mcp-video（7 项）

| ID | 指标 | 原状态 | **P3 后** | 建议 |
| --- | --- | --- | --- | --- |
| MV-01~05 | 91 tools / cinematic | ❌ | ❌ | 不借全量 |
| MV-03 | 字幕工具集 MCP | ❌ | ⚠️ 4 tools | — |
| MV-06~07 | MCP 封装 / uvx | ⚠️ | ⚠️ local mcp.example | 可选 |

### 2.11 video-production-skill（5 项）

| ID | 指标 | 原状态 | **P3 后** | 建议 |
| --- | --- | --- | --- | --- |
| VP-01~05 | Resolve / 243 tools | ➖/❌ | ➖/❌ | 不借 |

### 2.12 vercel-labs/skills（6 项）

| ID | 指标 | 原状态 | **P3 后** | 建议 |
| --- | --- | --- | --- | --- |
| VL-03 | npx 实测 | ❌ | ✅ Cursor 已装 junction | — |
| VL-05 | references 丰富度 | ⚠️ | ⚠️ | 随 P4/P5 补 |
| VL-06 | .agents vs .cursor 混用 | ⚠️ | ⚠️ 双路径 junction | 建议：install 文档统一 |

---

## 3. P4 包（你已确认方向，本报告细化范围）

| 包内 ID | 交付 | 参考 |
| --- | --- | --- |
| P4-1 | `novels/` + `_registry.json` + `canon/project.json` | X-01, NS-10, STRUCTURE §3 |
| P4-2 | 自动 slug + 冲突后缀 | story-init, novel-pipeline Phase 1 |
| P4-3 | `novels/.active` + Skill 强制 resolve | X-02 |
| P4-4 | `chapters/.drafts/` + promote 规则 | X-03, PW-07/11 |
| P4-5 | `canon/snapshots/chNN-after.md` | X-04, NM-03/04 |
| P4-6 | `platform-compliance.md` + deai 平台节 | X-05, NM-07 |
| P4-7 | voice-brief 增 `platform_target` | NM-07 |
| P4-8 | `.gitignore` novels/dist；examples 不动 | D2 |
| P4-9 | STRUCTURE-STANDARDS + synthesis 文档更新 | D10 |

---

## 4. 建议确认的补充清单（按优先级）

### 4.1 必补（P4 已实施，2026-06-02）

1. P4-1 ~ P4-9（多书隔离全包）✅  
2. PW-11 enforce（pipeline/CLI gate）✅ schema 校验 + 产物检查（`pipeline_gate.py`）  
3. NM-07 / X-05 平台合规文档 ✅  

### 4.2 建议补（P5，高 ROI）— **已实现 2026-06-02**

4. NS-11 / VS-10 Quick trigger 一览表 ✅  
5. GN-06 novel_cli graphify query 暴露 ✅  
6. PW-04 soft critics 扩展到 10 条 ✅  
7. PW-07 repair action spec 表格模板 ✅  
8. NM-05 `bible summary` CLI ✅  
9. ZE-08 Quill export audit checklist ✅  
10. SVM-06 RESULT JSON 契约 ✅  
11. SVM-09 video PIPELINE.md reference ✅  
12. SS-05 双向关系 reference + `relations check` ✅  

### 4.3 可选（P6+）

13. GN-08 graphify thread  
14. SVM-04/11 Whisper + loudnorm  
15. VS-01 tumblr-video skill  
16. SS-11 marketplace 完善  
17. NS-03 task_plan characters 表  

### 4.4 明确不借（写入非目标即可）

- postwriter DB/scoring/Pareto/PW-09 全自动  
- novel-skill RPG、诗词配对 NS-05/07  
- video Resolve/VP-02、playwright VS-06、svg/coze  
- zencoder IDE 绑定  

---

## 5. 统计（刷新后）

| 类别 | 约计项数 |
| --- | --- |
| 第二层 ❌/⚠️ 总指标 | ~120 |
| P0–P3 已关闭 | ~45 |
| **仍遗漏（含 P4 包）** | **~35** |
| 建议不借 | ~25 |
| 可选待定 | ~15 |

---

## 6. 当前使用方式（更新）

- §4.1/§4.2 已实施条目作为已完成审计证据。  
- 新增改动请继续登记到 ROADMAP，并在本矩阵回写状态。  
- §4.3 可选默认暂缓，除非业务明确点名。

---

*第四层全量扫描完成。本报告替代「用户提醒式」查缺，作为后续实施唯一 backlog 来源。*
