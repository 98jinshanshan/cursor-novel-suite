# Novel Suite — AI 小说创作 + 视频推文 + 多平台发布 一体化工具

> 在 IDE 里用中文完成「扫题材 → 写小说 → 做视频 → 发多平台 → 看数据」的全流程。

**GitHub：** <https://github.com/98jinshanshan/cursor-novel-suite>  
**Agent 对话入口：** [AGENTS.md](AGENTS.md) · **文档导航：** [docs/INDEX.md](docs/INDEX.md)  
**产品对齐层（去 Cursor 化）：** [novel-suite/](novel-suite/) · [对齐报告](NOVEL_SUITE_ALIGNMENT_REPORT.md) ·
[实施计划](NOVEL_SUITE_IMPLEMENTATION_PLAN.md)

| 子项目 | 说明 |
| --- | --- |
| [cursor-novel-writer](./cursor-novel-writer/) | 中文小说：扫榜 → 写作 → 审稿 → 可选 EPUB → 可选多平台发布 |
| [cursor-novel-video](./cursor-novel-video/) | 章节 → 摘要短视频 / 分场景叙事片 → 可选多平台视频发布 |

---

## 商业与第三方边界（必读）

Novel Suite **内部对齐层 / 未商业发布**。下列能力均为**可选适配器，默认关闭**；Agent 不得默认自动执行：

| 能力 | 默认状态 | 启用前须 |
| --- | --- | --- |
| 平台发布 `auth login` / `publish upload` | **默认关闭** | 用户自有账号与密钥、平台条款确认、**单次人工书面确认** |
| TTS（`edge-tts`） | **默认关闭** | 读 `novel-suite/adapters/tts/`，自审服务条款 |
| 图像生成（SD / ControlNet / ComfyUI） | **默认关闭** | 读 `novel-suite/adapters/image-generation/`，自审 AGPL/GPL |
| 视频导出（FFmpeg pipeline） | 用户自装 FFmpeg | 读 `novel-suite/adapters/video-export/` |
| EPUB 导出（`ebooklib`） | **默认关闭** | `pip install -e ".[epub]"`；AGPL 风险须法律复核 |

**安全只读 / 本地门禁（≠ 发布）：**

- `novel-suite doctor --core-contracts` — 契约完整性
- `novel-suite product list/read/validate` — 产品层文档只读
- `novel-suite video gate` / `publishing_gate` — 发布**前**检查，不代替人工确认

详见
[COMMERCIAL_RELEASE_GATE.md](COMMERCIAL_RELEASE_GATE.md)、[THIRD_PARTY_POLICY.md](THIRD_PARTY_POLICY.md)、[novel-suite/THIRD_PARTY_BOUNDARY.md](novel-suite/THIRD_PARTY_BOUNDARY.md)。

---

## 快速开始

### 安装

```bash
# 1. 克隆仓库
git clone https://github.com/98jinshanshan/cursor-novel-suite.git
cd cursor-novel-suite   # 或你的本地目录名

# 2. 安装 Python 包（novel-suite 2.0 CLI）
pip install -e .

# 3. 安装 Skills（Cursor / Qoder / TRAE）
powershell -File platforms/install-skills.ps1 -Agents cursor

# 4. 安装 MCP（可选，推荐）
pip install mcp
powershell -File platforms/install-mcp.ps1
# 重启 Cursor → Settings → MCP → 确认 novel-suite 在线
```

### 自检

```bash
novel-suite doctor --core-only --json    # → emoji: 🩺  DOCTOR_OK
pytest -m "not ffmpeg"                   # 270+ 用例
```

---

## 完整工作流（10 分钟上手）

```bash
# 1. 扫题材（看什么火）
novel-suite writer scan --period week --json
# → 📊 SCAN_OK — 写入 intel/radar/<week>.md + <week>.scan.json
#    含 suggested_platform / competition_analysis / trend_prediction

# 2. 立项（从扫榜结果一键带入，推荐）
novel-suite writer init --from-scan intel/radar/<latest>.scan.json --json
# → 📖 INIT_OK — 自动填入 title / premise / target-platform，并跑 gate phase 1

# 或手动立项
novel-suite writer init --title "我的第一本书" --premise "一句梗概。" --target-platform fanqie --json

# 清理 0 章节的空项目（开发/测试残留）
novel-suite writer clean --dry-run   # 预览
novel-suite writer clean --json        # 删除 registry 中空项目 + 孤儿条目

# 3. 写小说（在 IDE 里和 Agent 对话）
# 「帮我写第一章，3000字」

# 4. 生成分镜
novel-suite video storyboard --project cursor-novel-writer/examples/demo-novel --chapter-key ch01 --json
# → 🎬 STORYBOARD_OK

# 5. 视频一键生成
novel-suite video pipeline --project cursor-novel-writer/examples/demo-novel --mode proof --json
# → 🎞️ PIPELINE_OK

# 6. 发布前检查（本地门禁，不等于已发布）
novel-suite video gate --project cursor-novel-writer/examples/demo-novel --json
# → ✅ GATE_OK 或列出待修复项

# --- 以下步骤 7–8 为【可选适配器】，默认关闭；须用户自启 + 人工确认后再执行 ---
# Agent 不要默认自动 login / upload。详见 COMMERCIAL_RELEASE_GATE.md

# 7. 发布到抖音（可选；需 DOUYIN_CLIENT_ID + 人工确认）
novel-suite auth login --platform douyin --json
novel-suite video publish upload --project <path> --platform douyin --json

# 8. 发布到番茄（可选；需 FANQIE_API_KEY + 人工确认）
novel-suite auth login --platform fanqie --json
novel-suite novel publish upload --project <path> --platform fanqie --json

# 9. 第二天录入数据
novel-suite analytics record --project <path> --metrics "播放量=15000 收入=12.5" --json
# → 📝 ANALYTICS_RECORD_OK

# 10. 看全局报告
novel-suite analytics cross-report --json
# → 📊 ANALYTICS_CROSS_OK
```

---

## CLI 命令全景

### 认证（可选适配器 — 默认关闭，发布前须人工确认）

| 命令 | 说明 |
| --- | --- |
| `auth login --platform douyin` | 抖音 OAuth（`DOUYIN_CLIENT_ID`）；**非默认核心** |
| `auth login --platform fanqie` | 番茄 API Key（`FANQIE_API_KEY`） |
| `auth login --platform kuaishou` | 快手 OAuth（`KUAISHOU_CLIENT_ID`） |
| `auth login --platform bilibili` | B站 OAuth（`BILIBILI_CLIENT_ID`） |
| `auth status` | 查看所有平台登录状态 |
| `auth logout --platform <name>` | 退出指定平台 |

### 题材挖掘

| 命令 | 说明 |
| --- | --- |
| `writer scan --period week` | 本周热门题材扫描 |
| `writer scan --demo` | 离线演示模式 |
| 输出字段 | `suggested_platform` / `competition_analysis` / `trend_prediction` |

### 小说创作

| 命令 | 说明 |
| --- | --- |
| `writer init --from-scan <radar.scan.json>` | 从扫榜 JSON 立项（自动 title/premise/platform） |
| `writer init --title --premise --target-platform` | 手动立项（可选目标平台） |
| `writer clean [--dry-run]` | 删除 0 章节空项目及 registry 孤儿条目 |
| `writer chapter draft --chapter N --input file.md` | 写入章节 |
| `writer chapter promote <file>` | 草稿转正式 |
| `writer export --format epub` | 导出 EPUB（需 `pip install -e ".[epub]"`；AGPL 可选适配器） |
| `writer gate --phase <1-9>` | 阶段门禁 |

### 雪花法 / 角色卡（LLM 辅助，Python API）

| API | 说明 |
| --- | --- |
| `snowflake.run_snowflake(topic)` | 4 步递进大纲 |
| `character_gen.extract_character(text, name)` | 从正文提取角色设定卡 |

### 视频管线

| 命令 | 说明 |
| --- | --- |
| `video storyboard` | 章节 → 分镜 JSON |
| `video character list/pack/qc` | 角色素材 |
| `video stills generate --mode proof` | 静帧生成 |
| `video compose` | 视频合成 |
| `video pipeline` | 一键 E2E |
| `video gate` | 发布前门禁 |

### 多平台发布（可选适配器 — 默认关闭，单次上传须人工确认）

| 命令 | 说明 |
| --- | --- |
| `video publish upload --platform douyin\|kuaishou\|bilibili` | 发布视频（**禁止 Agent 默认自动执行**） |
| `video publish list` | 视频发布记录 |
| `novel publish upload --platform fanqie\|qidian\|jinjiang` | 发布/导出小说 |
| `novel publish list` | 小说发布记录 |

### 数据追踪

| 命令 | 说明 |
| --- | --- |
| `analytics record --metrics "播放量=X 收入=Y"` | 录入效果数据 |
| `analytics status` | 项目汇总 |
| `analytics report` | 生成 Markdown 报告 |
| `analytics cross-report` | 跨项目对比 |

### MCP

| 命令 | 说明 |
| --- | --- |
| `mcp serve` | stdio 模式（IDE 拉起） |
| `mcp serve --transport sse` | HTTP Streamable 独立进程 |

---

## 平台支持矩阵

| 平台 | 发布 | 认证方式 | 状态 |
| --- | --- | --- | --- |
| 🎵 抖音 | 视频 | OAuth Cookie | 适配器（**默认关闭**，须人工确认） |
| 📹 快手 | 视频 | OAuth Cookie | 适配器（默认关闭） |
| 📺 B站 | 视频 | OAuth Cookie | 适配器（默认关闭） |
| 🍅 番茄小说 | 小说文本 | API Key | 适配器（默认 stub；真实 API 须自启） |
| 📖 起点中文网 | 小说文本 | OAuth Cookie | 格式导出适配器 |
| 🌸 晋江文学城 | 小说文本 | OAuth Cookie | 格式导出适配器 |

---

## MCP 配置

### Cursor（推荐）

`.cursor/mcp.json` 由 `platforms/install-mcp.ps1` 生成。重启 Cursor 即可。

```json
{
  "mcpServers": {
    "novel-suite": {
      "command": "py",
      "args": ["-3", "-m", "novel_suite.cli", "mcp", "serve", "--transport", "stdio"],
      "cwd": "${workspaceFolder}",
      "env": { "NOVEL_SUITE_ROOT": "${workspaceFolder}" }
    }
  }
}
```

HTTP 模式：终端运行 `novel-suite mcp serve --transport sse`，按 FastMCP 提示连接。

### MCP Tools

> 发布类 MCP 工具（`auth_*`、`publish_*`）为可选适配器路径，**默认关闭**；`product_*` 为只读产品层查询。

| Tool | 说明 |
| --- | --- |
| `product_list()` / `product_read()` / `product_validate()` | 只读产品层（安全） |
| `auth_login(platform)` | 登录指定平台（须人工确认） |
| `auth_status(platform)` | 查看登录状态 |
| `auth_logout(platform)` | 退出登录 |
| `publish_platforms(type)` | 列出支持的平台 |
| `publish_readiness(platform, project)` | 发布就绪检查 |
| `publish_guide(platform)` | 获取发布步骤（含 `analytics`） |
| `publish_upload(platform, project)` | 发布视频 |
| `novel_publish_upload(platform, project)` | 发布小说 |
| `analytics_record(project, metrics_json)` | 录入数据 |
| `analytics_report(project)` | 单项目或跨项目报告 |

---

## 环境变量

| 变量 | 用途 |
| --- | --- |
| `FANQIE_API_KEY` | 番茄小说 API Key |
| `FANQIE_USE_REAL_API` | `1` 启用真实番茄 HTTP API（默认 stub） |
| `DOUYIN_CLIENT_ID` / `DOUYIN_CLIENT_SECRET` | 抖音 OAuth |
| `KUAISHOU_CLIENT_ID` / `KUAISHOU_CLIENT_SECRET` | 快手 OAuth |
| `BILIBILI_CLIENT_ID` / `BILIBILI_CLIENT_SECRET` | B站 OAuth |
| `NOVEL_SUITE_ROOT` | 项目根目录（自动检测） |
| `NOVEL_SUITE_TOKEN_DIR` | 认证 token 存储目录 |

---

## 常见问题

**Q：运行时报错 `ModuleNotFoundError`？**  
A：运行 `pip install -e .`

**Q：MCP Server 连接不上？**  
A：运行 `platforms/install-mcp.ps1`，确保 `pip install mcp`，重启 Cursor。

**Q：发布时平台无效或未登录？**  
A：发布为**可选适配器**；先确认已阅读 `COMMERCIAL_RELEASE_GATE.md` 并完成人工确认，再 `auth status` / `auth login`。Agent 不应默认自动上传。

**Q：`analytics record` 支持哪些指标？**  
A：播放量、点赞、评论、分享、收入(元)、完读率、涨粉（中英文 key 均可）。

**Q：雪花法怎么用？**  
A：对 Agent 说「用雪花法生成修仙题材大纲」，会调用 `run_snowflake()` 并逐步输出 prompt。

**Q：CLI 输出里的 emoji？**  
A：人类模式终端显示 emoji + 颜色；`--json` 模式在 JSON 中有 `"emoji"` 字段，无 ANSI 颜色码。

---

## 项目架构

```text
src/novel_suite/
├── cli.py              # CLI 入口
├── mcp_server.py       # MCP Server（stdio / sse）
├── core/               # 错误码 / 路径 / Result Contract / emoji 输出
├── memory/             # 向量记忆（Qdrant + M3E）
├── writer/             # intel / init / chapter / snowflake / character_gen
├── video/              # storyboard / character / stills / compose / gate / publish
├── novel/              # 小说发布（fanqie / qidian / jinjiang）
├── auth/               # 多平台认证
├── analytics/          # 数据追踪
├── platforms/          # 平台注册表
└── tests/              # 270+ 用例

cursor-novel-writer/skills/   # Writer Skills（安装到 .cursor/skills）
cursor-novel-video/skills/    # Video Skills
```

---

## 质量 / CI

```bash
pytest -m "not ffmpeg"
powershell -File typecheck.ps1 -SkipInstall -ChangedOnly
```

GitHub Actions：`.github/workflows/ci.yml`

---

## 各 IDE 对照

| IDE | Skills 安装 | 对话入口 |
| --- | --- | --- |
| Cursor | `install-skills.ps1 -Agents cursor` | Agent + [AGENTS.md](AGENTS.md) |
| Qoder | `-Agents qoder` | Agent 对话 |
| TRAE / SOLO | `-Agents trae-cn` | Agent / `#novel-pipeline` |

验证：[docs/verification/](docs/verification/)

---

## 许可证

MIT（Novel Suite 核心）。第三方组件见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。**商业发布尚未允许**，待法律与用户最终确认（见
[COMMERCIAL_RELEASE_GATE.md](COMMERCIAL_RELEASE_GATE.md)）。
