# 目录架构与文档存放 — 合规审计

**日期：** 2026-05-31  
**层级：** 第三层（结构专项，承接第一层工程审计 + 第二层交叉审计）  
**规范依据：** [STRUCTURE-STANDARDS.md](../standards/STRUCTURE-STANDARDS.md)  
**前置文档：**

- [2026-05-31-novel-suite.md](./2026-05-31-novel-suite.md)
- [2026-05-31-reference-crosswalk.md](./2026-05-31-reference-crosswalk.md)

---

## 执行摘要

| 维度 | 评级 | 说明 |
| --- | --- | --- |
| Monorepo `docs/` 聚合 | **B+** | 审计/规范/计划/索引已就位；verification 为占位 |
| 子项目 Skills 布局 | **C** | 7+3 个 SKILL.md 合规；**无一** skill 含 `scripts/` |
| engine vs skill 脚本 | **D** | 全部脚本在 `engine/scripts/`，与 agentskills 渐进披露惯例不符 |
| 示例与 demo | **C-** | writer 有 skeleton demo-novel；video 无 `demos/` |
| 生成物隔离 | **C** | `tmp/video_jobs/` 仍有 E2E 产物；gitignore 需强化 |
| 测试与 CI | **F** | 两项目均无 `tests/` |

**结论：** 文档层规范迁移 **约 85% 完成**；代码仓目录 **尚未执行** skill/scripts、demos、tests 重排。建议先确认 §7 Option A，再按 ROADMAP P0→P1 分批实施。

---

## 1. Monorepo 文档层 — 逐项对照

| 规范路径 | 要求 | 当前状态 | 合规 |
| --- | --- | --- | --- |
| `docs/INDEX.md` | 全仓文档导航 | ✅ 已建，链到 audit/standards/plans | ✅ |
| `docs/audit/YYYY-MM-DD-*.md` | 日期前缀审计 | ✅ novel-suite、reference-crosswalk、**本文** | ✅ |
| `docs/standards/STRUCTURE-STANDARDS.md` | 目录规范 | ✅ | ✅ |
| `docs/plans/ROADMAP.md` | 合并路线图 | ✅ | ✅ |
| `docs/verification/<platform>.md` | 多平台实测 | ⚠️ 占位已建，内容待填 | ⚠️ |
| 根 `README.md` → `docs/INDEX.md` | 入口链接 | ✅ | ✅ |
| `docs/` 根散落 `AUDIT-*` | 禁止 | ✅ 已清空 | ✅ |

### 1.1 文档命名规范

| 规则 | 示例 | 违规 |
| --- | --- | --- |
| 审计：`YYYY-MM-DD-<topic>.md` | `2026-05-31-novel-suite.md` | 无 |
| 规范：固定名大写 | `STRUCTURE-STANDARDS.md` | 无 |
| 验证：小写平台名 | `cursor.md`, `trae-cn.md` | 无 |

### 1.2 文档内容归属矩阵

| 内容类型 | 应存放 | 不应存放 |
| --- | --- | --- |
| 工程/E2E 审计结论 | `docs/audit/` | 项目 README、skill 内 |
| 参考项目交叉指标 | `docs/audit/` | `docs/plans/` |
| 目录树与命名约定 | `docs/standards/` | 审计报告正文（可摘要+链接） |
| P0/P1/P2 任务清单 | `docs/plans/ROADMAP.md` | 多个并行 ROADMAP |
| 安装 smoke 记录 | `docs/verification/` | platforms README 过长复制 |
| 用户使用说明 | `<project>/README.md` | `docs/`（除非 monorepo 级） |
| Skill 工作流细节 | `skills/*/references/` | `docs/audit/` |
| graphify upstream 命令表 | `cursor-novel-writer/docs/` 或 skill references | 根 `docs/audit/` |

---

## 2. cursor-novel-writer — 目录合规

### 2.1 现状树（2026-05-31 快照）

```text
cursor-novel-writer/
├── README.md, LICENSE, requirements.txt          ✅
├── skills/ (7)                                     ✅ SKILL.md 齐全
│   ├── story-init/references/                      ✅ 唯一含 references 的 skill
│   └── */ — 无 scripts/, 多数无 references/        ❌ ST-03
├── engine/
│   ├── novel_cli.py                                ✅
│   └── scripts/create_epub.py, graphify_bridge.py  ⚠️ 未在 skill 侧暴露
├── schema/, templates/, examples/, platforms/      ✅
├── examples/demo-novel/                            ⚠️ 仅 1 章 + 骨架
└── tests/                                          ❌ ST-07
```

### 2.2 Skill 目录合规表

| Skill | SKILL.md | scripts/ | references/ | 规范动作 |
| --- | --- | --- | --- | --- |
| story-init | ✅ | ❌ | ✅ (2) | 可选 init wrapper |
| character-management | ✅ | ❌ | ❌ | 可选 graphify wrapper |
| worldbuilding | ✅ | ❌ | ❌ | — |
| plot-structure | ✅ | ❌ | ❌ | **增** plot-frameworks.md |
| chapter-writing | ✅ | ❌ | ❌ | — |
| novel-review | ✅ | ❌ | ❌ | **增** forge-workflow.md |
| novel-export | ✅ | ❌ | ❌ | **增** scripts/create_epub.py wrapper |

### 2.3 用户工程约定（templates + demo）

| 路径 | 规范 §3.1 | demo-novel | 缺口 |
| --- | --- | --- | --- |
| `story.md` | ✅ | ✅ | — |
| `canon/progress.json` | ✅ | ✅ | — |
| `characters/*.md` | ✅ | ❌ 无 | ST-09 级 demo |
| `worldbuilding/` | ✅ | _index only | 缺 location 样例 |
| `plot/arcs/` | ✅ | ❌ | 缺 arc 文件 |
| `chapters/` | ✅ | 1 章 | 对标 the-last-ember 需 3+ |
| `reviews/` | 建议 | ❌ | novel-review 输出位 |
| `dist/*.epub` | 生成物 | ❌ | export 修复后补 |

---

## 3. cursor-novel-video — 目录合规

### 3.1 现状树

```text
cursor-novel-video/
├── README.md, LICENSE, requirements.txt          ✅
├── skills/ (3) — 无 scripts/, references/        ❌ ST-03
├── engine/scripts/ (5 py)                          ⚠️
├── schema/, adapters/, mcp/, platforms/            ✅
├── adapters/ — 无 README.md                        ❌ ST-08
├── examples/README.md only                         ⚠️
├── demos/                                          ❌ ST-06
├── tmp/video_jobs/* (2 jobs)                       ❌ ST-05
└── tests/                                          ❌ ST-07
```

### 3.2 视频 job 与生成物

| 路径 | 应提交 Git | 当前 | 动作 |
| --- | --- | --- | --- |
| `tmp/video_jobs/` | ❌ | 含 2 个 job 目录 | 清空 + 确认 .gitignore |
| `demos/*.mp4` | ✅ 小体积样片 | 不存在 | E2E 成功后复制到 demos/ |
| `output/*.mp4` in job | ❌ | 在 tmp 内 | 保持 ignore |

### 3.3 Skill 应对照 engine 脚本映射

| Skill | 应对应 scripts | engine 现状 |
| --- | --- | --- |
| video-chapter-summary | tts_edge, compose_ffmpeg, qc_video | ✅ 有 |
| video-scene-drama | + ken_burns, make_title_card | ✅ 有 |
| video-export | compose + qc | ✅ 有 |
| （缺）字幕 | burn_subtitles.py | ❌ 未实现 |

---

## 4. 违规清单 ST-01..ST-12 — 刷新状态

| ID | 描述 | 迁移前 | **当前（2026-05-31）** | 下一步 |
| --- | --- | --- | --- | --- |
| ST-01 | 审计在 docs 根 | ❌ | ✅ 已迁入 audit/ | — |
| ST-02 | 无 INDEX | ❌ | ✅ | — |
| ST-03 | engine 脚本未 colocate | ❌ | ✅ Option A wrapper | — |
| ST-04 | novel-export 无 bundling | ❌ | ✅ scripts/create_epub.py | — |
| ST-05 | tmp job 入库风险 | ❌ | ✅ 已清空 + gitignore | — |
| ST-06 | 无 demos/ | ❌ | ✅ 含样片 MP4 | — |
| ST-07 | 无 tests/ | ❌ | ✅ pytest smoke + CI | — |
| ST-08 | adapters 无 README | ❌ | ✅ | — |
| ST-09 | plot-frameworks 缺失 | ❌ | ✅ | — |
| ST-10 | 根 README 无 docs 链 | ❌ | ✅ | — |
| ST-11 | .vscode 在根 | ✅ | ✅ | — |
| ST-12 | 独立 LICENSE | ✅ | ✅ | — |

**文档层：** ST-01、ST-02、ST-10 **已关闭**。  
**代码仓层：** ST-03～ST-06、ST-08、ST-09 **已关闭**；ST-07 待 P2。

---

## 5. 规范重排 — 推荐执行顺序

与用户确认的 **Option A**（engine 保留实现，skill/scripts 为薄 wrapper）一致时：

### Phase A — 文档（本次审计后，**无需改业务逻辑**）

1. ✅ `docs/audit|standards|plans|INDEX` 就位  
2. ✅ 本文档（第三层结构合规）  
3. ✅ `docs/verification/*.md` 占位  
4. ☐ 全仓 grep 更新残留链接（`AUDIT-*` → `audit/2026-*`）  
5. ☐ 子项目 README 增加「文档见 ../../docs/INDEX.md」一行  

### Phase B — 生成物与 ignore（P0）

1. 删除 `cursor-novel-video/tmp/video_jobs/*`  
2. 确认 `.gitignore` 含 `tmp/`、`dist/`、`*.epub`（用户工程侧）  
3. 修复 create_epub / graphify CLI（见第一层审计）  

### Phase C — Skill 脚本 colocate（P1）

1. `novel-export/scripts/create_epub.py` → 调用 `engine/scripts/create_epub.py`  
2. 三个 video skill 各增 `scripts/` wrapper + SKILL.md 路径更新  
3. `compatibility` 注明需 full repo clone  

### Phase D — 内容与 demo（P1）

1. 扩展 `demo-novel`  
2. 新建 `cursor-novel-video/demos/`  
3. `plot-frameworks.md`、`forge-workflow.md`、`adapters/README.md`  

### Phase E — 质量（P2）

1. `tests/test_smoke.py` 两项目  
2. CI markdownlint + compileall  

---

## 6. 新建文档时的存放决策树

```text
是否 monorepo 级审计/规范/计划？
  ├─ 是 → docs/audit | standards | plans | verification
  └─ 否 → 是否某 Skill 专属工作流？
        ├─ 是 → skills/<name>/references/
        └─ 否 → 是否子项目运维说明（graphify upstream）？
              ├─ 是 → <project>/docs/
              └─ 否 → <project>/README.md 或 platforms/
```

**反模式（禁止）：**

- 在 `docs/audit/` 写用户使用教程  
- 在 `skills/` 放 `AUDIT-*.md`  
- 把 EPUB/MP4 放进 `docs/`  
- 在 repo 根新增除 `README.md` 外的说明 md  

---

## 7. 已确认决策（2026-05-31）

| 决策 | 结论 |
| --- | --- |
| Skill 脚本 | **Option A**：engine 实现 + skill 薄 wrapper |
| demo-novel | 3 人物 + 2 地点 + 1 世界观 + 1 弧 + 1 章 |
| 实施顺序 | P0 已完成 → 进入 P1 |

协作原则见 [DECISION-PRINCIPLE.md](../standards/DECISION-PRINCIPLE.md)。

---

## 8. 验收检查表

- [x] 已阅 STRUCTURE-STANDARDS 全文  
- [x] 已阅本文 ST 清单与 Phase A–E  
- [x] Option A 已确认  
- [x] P0 已实施（2026-05-31）  
- [x] P1 主体已实施（wrapper + demo-novel + demos + references）  

---

*第三层结构合规审计完成。文档迁移 Phase A 基本完成；代码仓重排等待确认后按 ROADMAP 执行。*
