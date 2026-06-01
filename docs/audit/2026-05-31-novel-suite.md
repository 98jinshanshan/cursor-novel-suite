# 小说 + 视频工具套件 — 深度审计报告

> 历史快照（截至 2026-05-31）。后续实施状态以  
> [ROADMAP](../plans/ROADMAP.md) 与  
> [2026-06-02-full-reference-gap-matrix.md](./2026-06-02-full-reference-gap-matrix.md) 为准。

**日期：** 2026-05-31  
**范围：** `cursor-novel-writer` + `cursor-novel-video` + 衔接 + 多平台  
**深度：** B（代码逐审 + E2E smoke + GitHub 融合核对 + 测试建议）  
**环境：** Windows 10，Python 3.13，FFmpeg 8.0.1 已安装，graphify **未**安装

---

## 执行摘要

| 维度 | 评级 | 一句话 |
| --- | --- | --- |
| 架构设计 | B+ | 「一核三端」骨架清晰，Skills/CLI/platforms 分层合理 |
| 功能完整度 | C+ | 视频 summary/drama 可跑通；小说 CLI 有关键 bug，写章依赖 Agent |
| 可靠性 | C | argparse 顺序错误、EPUB API  typo、graphify 子进程传参错误 |
| 融合兑现度 | C | 方法论在 SKILL.md，多数参考项目能力未脚本化 |
| 端到端 | C | 视频链路 OK；小说 export/review 在本机 E2E **失败** |
| 多平台 | B- | 文档与 install 脚本齐全，未在 Qoder/TRAE 实测 |
| 产出质量 | C+ | 视频无字幕、单图 Ken Burns；EPUB 未验证成功 |
| 可维护性 | D+ | 无自动化测试、无 CI |
| 安全/成本 | A- | 本地免费路径清晰，API 可选 |

**结论：** 当前为 **可演示的 V1 原型**，距「完善」还差 **P0 缺陷修复 + P1 闭环验证 + P2 融合增强** 三轮。

---

## 1. 目标对齐 — 差距矩阵

| 最初承诺 | 实现状态 | 差距 |
| --- | --- | --- |
| 两个独立目录 | ✅ 已完成 | — |
| 中文通用小说 + EPUB | ⚠️ 部分 | EPUB 导出 **运行时错误**（`EpubNavi`） |
| graphify **完整集成** | ⚠️ 部分 | 仅有 bridge + offline 降级；本机无 graphify；**子进程 `--project` 传参顺序错误** |
| Skill 与 CLI **同等能力** | ❌ 未达成 | `novel write` 仅打印提示；写章/大纲无 CLI |
| 视频 summary MVP | ✅ 已验证 | 本机产出 MP4 + QC pass |
| 视频 drama 进阶 | ✅ 已验证 | 3 场景 × 6s ≈ 18s 片，QC pass |
| 本地免费 + 可选 API | ✅ | edge-tts + FFmpeg 可用；OpenAI/Seedance 为 stub |
| 多 IDE（Cursor/Qoder/TRAE） | ⚠️ 文档级 | `npx skills add` / install.ps1 未实测 |
| GitHub 10+ 项目融合 | ⚠️ 偏文档 | 见第 5 节融合核对表 |
| 无 Web UI / 无 PostgreSQL | ✅ | 符合 |

---

## 2. 架构审计（一核三端）

```text
                    ┌─────────────────────────────────────┐
                    │  skills/  (10 × SKILL.md)           │  ← 一核：agentskills.io
                    └──────────────┬──────────────────────┘
                                   │
         ┌─────────────────────────┼─────────────────────────┐
         ▼                         ▼                         ▼
  platforms/                  engine/                    mcp/
  install.ps1                 novel_cli / video_cli       video stub only
  cursor|qoder|trae           scripts/*.py
```

| 层级 | 小说 | 视频 | 问题 |
| --- | --- | --- | --- |
| Skills | 7 个，含 references | 3 个 | 无 `scripts/` 在 skill 目录内（依赖 repo `engine/`） |
| CLI | 6 子命令 | 2 子命令 | `--project` 必须在子命令**前**（文档写反） |
| MCP | 空 example | 2 tools | 未纳入 requirements；无 novel MCP |
| platforms | install.ps1/sh | 同上 | video 的 install.ps1 仅 3 行，功能弱 |

**架构建议：** 在 skill 的 `compatibility` 中明确「需 clone 完整 repo 或设置 `NOVEL_ENGINE_ROOT`」，否则 Agent 只复制 SKILL.md 时无法调用脚本。

---

## 3. 逐 Skill 审查（小说 7 + 视频 3）

### cursor-novel-writer

| Skill | 可独立执行 | 脚本依赖 | 主要缺口 |
| --- | --- | --- | --- |
| `story-init` | Agent 可 | graphify_bridge | CLI `init` 已脚手架；**不**自动写 plot/foreshadowing 表头对齐 schema |
| `character-management` | Agent 可 | graphify update | 无校验脚本；`_index` 需人工维护 |
| `worldbuilding` | Agent 可 | 无 | 无 location/system 模板文件在 `templates/` |
| `plot-structure` | Agent 可 | 无 | 三幕/起承转合仅文字说明，无 `references/plot-frameworks.md` |
| `chapter-writing` | Agent 可 | graphify review | **progress.json 无自动更新逻辑**（Skill 要求 Agent 手改） |
| `novel-review` | Agent 可 | graphify_bridge | 编辑人格仅表格，无 `references/personas/` 详细 prompt |
| `novel-export` | 需 CLI | create_epub.py | **EPUB 当前 broken** |

### cursor-novel-video

| Skill | 可独立执行 | 脚本依赖 | 主要缺口 |
| --- | --- | --- | --- |
| `video-chapter-summary` | CLI 可 | 全套 engine/scripts | 无 LLM 摘要，仅截断正文 350 字 |
| `video-scene-drama` | CLI 可 | 同上 | 无 beat-lock / Whisper 时间轴（super-video-maker 核心未实现） |
| `video-export` | 部分 | compose resize 简陋 | `resize` 硬编码 1080×1920 |

---

## 4. 逐脚本审查（engine）

### 小说

| 文件 | 行数级 | 问题 | 严重度 |
| --- | --- | --- | --- |
| `novel_cli.py` | ~180 | 调用 graphify_bridge 时 `--project` 放在子命令**后** → 失败 | **P0** |
| `novel_cli.py` | | README 示例 `--project` 在子命令后，与 argparse 不符 | **P0** |
| `novel_cli.py` | | `write` 非真正写作 | P1 |
| `graphify_bridge.py` | ~140 | 假定 graphify CLI 接受 `init <premise>` 裸参数，可能与真实 graphify-novel 不符 | P1 |
| `graphify_bridge.py` | | `query` 未暴露到 novel_cli | P2 |
| `create_epub.py` | ~130 | `EpubNavi()` → 应为 `EpubNav()` | **P0** |
| `create_epub.py` | | `markdown_to_html` 无转义，`<>&` 可破坏 XHTML | P1 |
| `create_epub.py` | | YAML 列表字段 `themes:` 解析不完整 | P2 |

### 视频 engine 脚本

| 文件 | 问题 | 严重度 |
| --- | --- | --- |
| `video_cli.py` | `subprocess.run(..., check=True)` 失败时无友好汇总 | P2 |
| `video_cli.py` | drama 每场景 TTS 未分轨，仅整段 `audio_full` | P1 |
| `compose_ffmpeg.py` | summary 全程单张 title 卡，与旁白内容无关 | P1 |
| `compose_ffmpeg.py` | drama concat 后音画时长可能不一致（靠 `-shortest` 截断） | P2 |
| `tts_edge.py` | 无重试/速率限制 | P3 |
| `ken_burns.py` | 依赖 FFmpeg zoompan，部分 build 可能缺 filter | P2 |
| `qc_video.py` | 最小 QC，无分辨率/assert | P2 |
| `openai_image.py` | 模型名 `gpt-image-1` 可能随 API 变化 | P2 |
| `mcp/server.py` | 仅 2 tools，无 drama；cwd 敏感 | P2 |

---

## 5. GitHub 融合核对表

| 参考项目 | 承诺融合点 | 落地程度 | 说明 |
| --- | --- | --- | --- |
| **story-skills** | 5 模块 + `_index` + kebab-case | **70%** | 目录与 Skill 对齐；缺 `examples/the-last-ember` 级完整示例 |
| **novel-skill** | 伏笔矩阵、EPUB、中文章节 | **50%** | 矩阵模板有；EPUB broken；无 RPG 模式（已刻意省略） |
| **graphify-novel** | 完整图谱 init/review/query | **25%** | bridge 存在；CLI 未装；传参 bug；offline 仅 JSON 索引 |
| **Novel Master** | Story Bible 快照、章末自检 | **40%** | 写在 chapter-writing Skill，无结构化 snapshot 文件格式 |
| **zencoder-novel-engine** | 6 编辑人格 | **20%** | novel-review 表格提及，无独立 persona SKILL 或 prompt 文件 |
| **postwriter** | 硬/软校验 + 修订循环 | **30%** | checklist 在 Skill；无 scoring、无 DB、无 repair planner |
| **Fiction Writing Workshop** | Story Bible 三阶段 | **15%** | 未单独实现 workshop skill |
| **video_skills** | Playwright 渲染、分类型视频 | **15%** | 无 playwright；无 tumblr/knowledge 子 skill |
| **super-video-maker** | 分阶段 job、beat-lock、QC | **35%** | job_state.json 有；无 Whisper beat-lock；无 staged cost confirm |
| **mcp-video** | 91 FFmpeg MCP 工具 | **5%** | 仅自写 5 脚本，未集成 mcp-video 包 |
| **video-production-skill** | 多 MCP 协同 | **0%** | 未集成 |

---

## 6. E2E Smoke 测试结果（本机 2026-05-31）

| 步骤 | 命令 | 结果 |
| --- | --- | --- |
| 小说 status | `novel_cli.py --project demo-novel status` | ⚠️ progress.json 输出 OK；graphify status **失败**（传参） |
| 小说 review | `novel_cli.py --project demo-novel review` | ⚠️ graphify_bridge 传参失败；offline stub 未执行到 |
| 小说 export epub | `novel_cli.py --project demo-novel export` | ❌ `AttributeError: EpubNavi` |
| 小说 graphify update | 直接调用 bridge | ❌ `--project` 顺序错误 |
| 视频 summary | `video_cli.py summary --chapter 01_试章.md` | ✅ MP4 ~12.6s，QC ok |
| 视频 drama | `video_cli.py drama --chapter 01_试章.md` | ✅ MP4 ~15.6s，QC ok |
| graphify CLI | `where graphify` | ❌ 未安装 |
| FFmpeg | `where ffmpeg` | ✅ |

**视频输出路径：** `cursor-novel-video/tmp/video_jobs/<job_id>/output/*.mp4`

---

## 7. 多平台就绪度

| 平台 | Skills 路径 | 文档 | 实测 |
| --- | --- | --- | --- |
| Cursor | `.agents/skills/` | README ✅ | 未在本审计中执行 `npx skills add` |
| Qoder | `.qoder/skills/` | platforms/qoder ✅ | 未实测 |
| TRAE CN | `.trae/skills/` | platforms/trae ✅ | 未实测 |
| Claude/Codex | `.agents/skills/` | 提及 ✅ | 未实测 |

**风险：** Skill 内脚本路径写 `engine/scripts/...`，要求 **工作区打开为 repo 根目录**；若用户仅安装 Skill 文件夹到 `~/.cursor/skills/`，Agent 找不到脚本。

**建议 P1：** 增加 `engine/_paths.py` 或环境变量 `CURSOR_NOVEL_ROOT`；Skill 内统一「先检测 repo 根」。

---

## 8. 产出质量

### EPUB（未成功导出）

- 需修复 `EpubNav` 后复测
- 缺少：封面图、简介页、章节标题从 YAML /frontmatter 解析
- 对比 novel-skill：无 `create_epub.py` Poetry/中文字体 CSS 完整度

### 视频成片质量

| 项 | 现状 | 对比参考 |
| --- | --- | --- |
| 配音 | edge-tts 可用 | video_skills 同级 |
| 画面 | 静态 title 卡 + Ken Burns | 远弱于 super-video-maker |
| 字幕 | **无** | video_skills / super-video-maker 均有 |
| 摘要质量 | 截断 350 字 | 无 LLM hook/beats 提取 |
| 竖屏 9:16 | ✅ | — |

---

## 9. 安全与依赖

| 依赖 | 小说 | 视频 | 备注 |
| --- | --- | --- | --- |
| Python 3.10+ | ✅ | ✅ | 3.13 已测 |
| ebooklib | requirements | — | 需 pin 版本；API 变更导致 bug |
| edge-tts | — | requirements | 需网络 |
| FFmpeg | — | 必需 | 已安装 |
| graphify | 可选 | — | 用户要求完整集成但未装 |
| OPENAI/Replicate | 可选 | stub | — |

---

## 10. 建议测试用例（完善前应先有 smoke tests）

```text
tests/
├── test_novel_cli_init.py      # init 后目录结构断言
├── test_graphify_bridge_offline.py
├── test_create_epub_smoke.py   # 1 章 → epub 文件存在
├── test_video_summary_smoke.py # 需 ffmpeg marker
└── test_argparse_order.py      # --project 位置回归
```

**CI 建议：** GitHub Actions，`markdownlint-cli2` + `pytest -m "not ffmpeg"` + 可选 ffmpeg job。

---

## 11. 完善路线图

### P0 — 阻塞「完善」定义，必须先修（估 0.5–1 天）

1. **修复 `create_epub.py`：** `EpubNavi` → `EpubNav`（或按 ebooklib 版本兼容写法）
2. **修复 graphify_bridge 调用：** 所有 subprocess 改为 `--project PATH <subcommand> ...`
3. **统一 CLI 文档与 argparse：** README 全部改为 `novel --project PATH export`；或改为子命令也接受 `--project`（更友好）
4. **E2E 复跑：** demo-novel export 成功 + review offline 路径返回 0

### P1 — 闭环与体验（估 2–3 天）

5. 安装并验证 **graphify-novel** 真实 CLI；修正 bridge 命令行与 upstream 对齐
6. **progress.json 更新脚本** `engine/scripts/update_progress.py`（字数、章节状态）
7. 视频 **烧录字幕**（ASS/SRT + FFmpeg），summary 至少 3 张卡切换
8. **完整 demo-novel**：3 章 + 人物 + 伏笔 + EPUB + 2 条视频
9. **Skill 路径解析**：repo 根探测 + README「工作区必须含 engine/」
10. 在本机执行 **npx skills add** 安装到 Cursor，验证 Agent 自动触发

### P2 — 融合增强（估 3–5 天）

11. 从 video_skills 移植 **playwright 字幕渲染**（可选依赖）
12. super-video-maker 式 **Whisper beat-lock**（可选）
13. novel-review **personas/** 参考 zencoder 拆成 3 个小 skill 或 references
14. postwriter 式 **review 报告模板** 写入 `reviews/chNN-review.md` 的 CLI
15. MCP 扩展：novel canon query + video drama
16. Qoder / TRAE CN **安装验证清单**（截图或步骤 doc）

### 不建议（YAGNI）

- Postwriter 级 PostgreSQL 多 Agent
- 91 工具全量 mcp-video 集成
- HeyGen 硬依赖

---

## 12. 请你确认的「完善」验收标准（P0+P1 完成后）

- [ ] `novel --project X export` 生成合法 EPUB，Calibre/阅读器可开
- [ ] `novel --project X review` 在无 graphify 时不崩溃，有 graphify 时真实 review
- [ ] `video summary` + `video drama` 各一条 reproducible 命令 documented
- [ ] `examples/demo-novel` 至少 3 章 + 1 条 summary 视频 + 1 条 drama 视频
- [ ] markdownlint 0 error 保持
- [ ] ≥5 个 pytest smoke 绿

---

## 附录 A：文件清单统计

| 项目 | Skills | Python | 模板/Schema | 平台脚本 |
| --- | --- | --- | --- | --- |
| novel-writer | 7 | 3 | 6 | 4 |
| novel-video | 3 | 8 | 1 | 3 |

**合计：** 10 Skills，11 Python 模块，无测试文件。

---

*报告结束。确认 P0 项后可在 Agent 模式下逐项修复。*
