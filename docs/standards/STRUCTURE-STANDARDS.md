# 仓库目录与文档存放规范

**版本：** 1.0（审计草案，待确认后实施）  
**适用范围：** Monorepo 根 `CURSOR/`、`cursor-novel-writer/`、`cursor-novel-video/`  
**依据：** [agentskills.io](https://agentskills.io)、[story-skills](https://github.com/danjdewhurst/story-skills)、[novel-skill](https://github.com/mave99a/novel-skill)、[video_skills](https://github.com/hexiaochun/video_skills)、[super-video-maker-skill](https://github.com/Bomx/super-video-maker-skill)、[vercel-labs/skills](https://github.com/vercel-labs/skills)

---

## 1. 设计原则

### 1.1 三层空间分离

| 空间 | 含义 | 是否进 Git | 示例 |
| --- | --- | --- | --- |
| **工具仓** | 可安装的 Skills + engine + 文档 | ✅ | `cursor-novel-writer/skills/` |
| **用户工程** | 用户创作的小说/视频 job 数据 | ⚠️ 示例可进 Git | `my-novel/chapters/` |
| **生成物** | tmp、dist、EPUB、渲染 MP4 | ❌ 默认 ignore | `tmp/video_jobs/` |

### 1.2 Agent Skills 标准（强制）

每个 Skill 目录：

```text
skills/<skill-name>/
├── SKILL.md              # 必需：frontmatter + 指令
├── scripts/              # 可选：该 skill 专属可执行脚本
├── references/           # 可选：深度文档（渐进披露）
└── assets/               # 可选：模板、静态资源
```

**规则：**

- `name` 必须与目录名一致（agentskills.io）  
- Skill 内引用脚本用**相对路径** `scripts/foo.py`  
- 超过 ~500 行的说明拆到 `references/`  
- **禁止**仅在 `engine/` 有脚本而 Skill 未声明路径（当前违规，见 §5）

### 1.3 文档存放（强制）

**决策树（新建 md 时）：**

```text
Monorepo 级审计 / 规范 / 路线图 / 平台验证？
  → docs/audit | docs/standards | docs/plans | docs/verification

某 Skill 专属工作流、框架说明、persona？
  → skills/<skill-name>/references/

子项目运维（如 graphify upstream 命令表）？
  → <project>/docs/

用户安装与快速开始？
  → <project>/README.md 或 platforms/<platform>/README.md
```

| 文档类型 | 路径 | 命名 |
| --- | --- | --- |
| 第一层工程审计 | `docs/audit/YYYY-MM-DD-novel-suite.md` | 日期前缀 |
| 第二层交叉审计 | `docs/audit/YYYY-MM-DD-reference-crosswalk.md` | 日期前缀 |
| 目录/流程规范 | `docs/standards/STRUCTURE-STANDARDS.md` | 固定名 |
| 多平台安装验证 | `docs/verification/<platform>.md` | 平台名 |
| 完善路线图 | `docs/plans/ROADMAP.md` | 单活文档 |
| 索引导航 | `docs/INDEX.md` | 必须链到各 doc |
| 项目 README | `<project>/README.md` | 用户入口，简短 |
| 平台说明 | `<project>/platforms/<platform>/README.md` | 仅安装差异 |

**禁止：**

- 审计报告堆在 repo 根（除 monorepo `README.md`）  
- 在 `skills/` 内放与 skill 无关的审计 md  
- 生成物写入 `docs/`

---

## 2. 目标目录树（Monorepo 根）

```text
CURSOR/
├── README.md                      # Monorepo 入口（≤50 行 + 链到 docs/INDEX.md）
├── LICENSE                          # 可选：根许可证或各子项目独立
├── .gitignore
├── .markdownlint.json
├── .markdownlintignore
├── .vscode/settings.json
│
├── docs/                            # 【规范】全仓文档唯一聚合点
│   ├── INDEX.md
│   ├── audit/
│   │   ├── 2026-05-31-novel-suite.md          # 从 docs/ 根迁入
│   │   └── 2026-05-31-reference-crosswalk.md
│   ├── standards/
│   │   └── STRUCTURE-STANDARDS.md             # 本文档迁入
│   ├── plans/
│   │   └── ROADMAP.md                         # 合并两层审计 P0/P1/P2
│   └── verification/
│       ├── cursor.md
│       ├── qoder.md
│       └── trae-cn.md
│
├── cursor-novel-writer/             # 独立可发布仓库
└── cursor-novel-video/
```

---

## 3. 目标目录树（cursor-novel-writer）

```text
cursor-novel-writer/
├── README.md
├── LICENSE
├── requirements.txt
│
├── skills/                          # 【一核】npx skills add 发现根
│   ├── story-init/
│   │   ├── SKILL.md
│   │   ├── scripts/                 # 建议：init_scaffold.py（或链到 engine）
│   │   └── references/
│   ├── character-management/
│   ├── worldbuilding/
│   ├── plot-structure/
│   │   └── references/
│   │       └── plot-frameworks.md   # 【缺】对照 story-skills
│   ├── chapter-writing/
│   ├── novel-review/
│   │   └── references/
│   │       ├── forge-workflow.md    # 【缺】对照 zencoder Forge
│   │       └── personas/            # Ghostlight/Lumen/Sable
│   └── novel-export/
│       └── scripts/
│           └── create_epub.py       # 【迁】从 engine/scripts 链入
│
├── engine/                          # 【CLI 同等能力】薄编排层
│   ├── novel_cli.py
│   └── scripts/                     # 共享实现；skill/scripts 可 symlink 至此
│       ├── create_epub.py
│       ├── graphify_bridge.py
│       └── update_progress.py       # 【缺】
│
├── schema/
│   └── progress.schema.json
├── templates/                       # 用户 novel 工程脚手架
├── examples/
│   ├── README.md
│   └── demo-novel/                  # 【缺】对标 the-last-ember 完整度
│       ├── story.md
│       ├── characters/*.md
│       ├── worldbuilding/...
│       ├── plot/...
│       └── chapters/*.md
│
├── platforms/
│   ├── install.ps1
│   ├── install.sh
│   ├── cursor/
│   ├── qoder/
│   └── trae/
│
├── tests/                           # 【缺】
│   └── test_smoke.py
│
└── docs/                            # 【可选】子项目补充文档
    └── graphify-upstream-commands.md
```

### 3.1 用户小说工程约定（不变，与 story-skills 对齐）

```text
<user-novel-project>/                # 用户 workspace，非工具仓
├── story.md
├── task_plan.md
├── canon/progress.json
├── characters/_index.md + *.md
├── worldbuilding/...
├── plot/foreshadowing.md + arcs/...
├── chapters/NN_标题.md
├── reviews/                         # 【建议增】novel-review 输出
├── graphify-out/
├── bible/
└── dist/*.epub
```

---

## 4. 目标目录树（cursor-novel-video）

```text
cursor-novel-video/
├── README.md
├── LICENSE
├── requirements.txt
│
├── skills/
│   ├── video-chapter-summary/
│   │   ├── SKILL.md
│   │   ├── references/              # 【缺】PIPELINE.md
│   │   └── scripts/                 # 链 tts/compose/qc
│   ├── video-scene-drama/
│   └── video-export/
│
├── engine/
│   ├── video_cli.py
│   └── scripts/
│       ├── tts_edge.py
│       ├── compose_ffmpeg.py
│       ├── ken_burns.py
│       ├── make_title_card.py
│       ├── qc_video.py
│       └── burn_subtitles.py        # 【缺】对照 super-video-maker
│
├── schema/
│   └── storyboard.schema.json
├── adapters/
│   ├── README.md                    # 【缺】索引 + env 表
│   ├── openai_image.py
│   └── seedance.md
├── mcp/
│   └── server.py
├── platforms/...
├── demos/                           # 【缺】对照 video_skills/demos
│   ├── README.md
│   ├── thumbnails/
│   └── *.mp4                        # 小体积样片或 LFS
├── examples/
│   └── README.md
└── tests/
```

### 4.1 视频 job 目录（运行时，不提交）

```text
cursor-novel-video/tmp/video_jobs/<job_id>/
├── job_state.json
├── storyboard.json
├── script.md
├── audio.mp3
├── assets/
├── scenes/                          # drama
└── output/*.mp4
```

---

## 5. 当前结构 vs 规范 — 违规清单

| ID | 违规描述 | 当前路径 | 规范动作（实施阶段） |
| --- | --- | --- | --- |
| ST-01 | 审计 md 在 `docs/` 根 | `docs/AUDIT-*.md` | ✅ 已迁入 `docs/audit/` |
| ST-02 | 无 `docs/INDEX.md` | — | ✅ 已建 |
| ST-03 | 脚本集中在 engine，Skill 未 colocate | `engine/scripts/*` | skill/scripts symlink 或复制 + SKILL 更新路径 |
| ST-04 | novel-export 未 bundling create_epub | 分离 | NS-08 / SVM-08 对齐 |
| ST-05 | tmp job 曾提交/存在 | `cursor-novel-video/tmp/` | 清空 + gitignore 强化 |
| ST-06 | 无 demos/ | — | 对照 video_skills VS-09 |
| ST-07 | 无 tests/ | — | 第一层审计建议 |
| ST-08 | adapters 无 README | — | 新建 |
| ST-09 | plot-frameworks 缺失 | — | story-skills SS-09 |
| ST-10 | 根 README 未指向 docs | `README.md` | ✅ 已加链接 |
| ST-11 | `.vscode` 在根（✅ OK） | — | 保持 |
| ST-12 | 两项目 LICENSE 重复（✅ 独立发布 OK） | — | 保持 |

---

## 6. 文档迁移计划

| 步骤 | 操作 | 状态 |
| --- | --- | --- |
| 1 | 创建 `docs/audit/`、`docs/standards/`、`docs/plans/`、`docs/verification/` | ✅ |
| 2 | 移动 `AUDIT-2026-05-31-novel-suite.md` → `docs/audit/` | ✅ |
| 3 | 移动交叉审计 → `docs/audit/2026-05-31-reference-crosswalk.md` | ✅ |
| 4 | 移动 `STRUCTURE-STANDARDS.md` → `docs/standards/` | ✅ |
| 5 | 生成 `docs/plans/ROADMAP.md` | ✅ |
| 6 | 新建 `docs/INDEX.md`、更新根 README | ✅ |
| 7 | 全仓 grep 更新内部 md 链接 | ⚠️ 进行中 |
| 8 | 第三层结构合规审计 `docs/audit/2026-05-31-structure-compliance.md` | ✅ |
| 9 | `docs/verification/*.md` 占位 | ✅ |

---

## 7. Skill 脚本路径规范（已确认：Option A）

**已采纳 Option A：** 共享实现留在 `engine/scripts/`，各 skill 下 `scripts/` 为 **入口 wrapper**（P1 实施）。`compatibility` 注明需 clone 完整仓库。

---

## 8. 与参考项目的目录对齐矩阵

| 参考项目 | 目录惯例 | 我们目标 | 对齐度 |
| --- | --- | --- | --- |
| story-skills | `skills/` + `examples/the-last-ember/` | §3 examples/demo-novel | ⚠️ |
| novel-skill | `skills/novel-creator/scripts/` | novel-export/scripts/ | ❌→目标 ✅ |
| video_skills | 每 skill 自带脚本 + `demos/` | §4 demos/ | ❌→目标 ✅ |
| super-video-maker | skill 根 + `tools/` + REFERENCE.md | references/ + scripts/ | ⚠️ |
| vercel-labs/skills | repo 根 `skills/` | ✅ | ✅ |
| graphify-novel | 用户项目 `bible/` + `graphify-out/` | 用户工程约定 §3.1 | ⚠️ |

---

## 9. 确认检查表

- [x] 同意 **docs/** 为全仓文档唯一聚合点（§1.3）  
- [x] 同意 **skill/scripts** 与 **engine/scripts** 关系采用 **Option A**（§7）  
- [x] 同意 **tmp/** 永不提交，样片进 **demos/**  
- [x] 迁移步骤 §6 Phase A + P0 已完成  

---

*规范 v1.1 — Option A 与 P0 已于 2026-05-31 确认并实施。P1 wrapper + demo 进行中。*
