# Python 安全审查报告（Novel Suite）

**日期**：2026-06-04  
**依据**：[security-best-practices](https://github.com/anthropics/skills/tree/main/skills/security-best-practices)（通用 CLI /
本地工具模式；无 Web 框架专项参考）
**范围**：`src/novel_suite/`、`cursor-novel-writer/engine/`、`cursor-novel-video/engine/`、`platforms/*.ps1`、根目录
`SECURITY.md`、CI 与依赖声明
**方法**：静态代码检索（`subprocess`、`eval`、`pickle`、`shell=True`、`urlopen`/`httpx`、路径边界）、架构对照 `SECURITY.md`、环境探测（`pip audit` 未安装）

---

## 执行摘要

本项目为**本地优先**的 Agent/CLI 小说与短视频工具链，**不对外提供 HTTP 服务**。在「可信操作者 + 本地工作区」威胁模型下，**未发现可直接远程利用的 RCE 路径**；主要风险集中在 **（1）MCP/Agent
信任边界下的任意路径读写**、**（2）可选联网模块的 SSRF/资源耗尽**、**（3）从 GitHub 拉取并覆盖代码树的供应链信任**。

| 级别 | 数量 | 说明 |
| --- | --- | --- |
| Critical | 0 | — |
| High | 2 | 条件性（MCP 暴露、Agent 误用 `--input`） |
| Medium | 3 | 联网下载、zip 刷新、graphify 查询注入面 |
| Low / 信息 | 8+ | 依赖审计、文档化绕过、输出注入等 |

**推荐结论**：维持当前「本地 CLI + 明确信任边界」模型；**P1** 为 MCP 路径校验与 `openai_image` 下载加固；**P2** 为 CI 增加 `pip-audit`/`bandit` 与 graphify
参数过滤。无需为典型单机写作场景做大规模重构。

---

## 威胁模型

| 维度 | 假设 |
| --- | --- |
| 部署 | 开发者/作者本机；Agent（Cursor/SOLO/TRAE）代执行命令 |
| 攻击者 | 恶意 Skill 提示、被篡改的 `intel/` 或章节 Markdown、**不可信 MCP 客户端**、恶意 PyPI/zip 包 |
| 非目标 | 多租户 SaaS、公网暴露的 API、数据库注入（无 DB） |

与根目录 [SECURITY.md](../../SECURITY.md) 一致：`SKIP_GATE`、`--skip-gate`、任意 `--project`（在允许根下）、`--input`
读盘均属**设计内的能力**，不是漏洞，除非操作者非预期。

---

## 做得好的地方

1. **无 `shell=True`**：全仓库 Python 检索未发现 `subprocess`/`os.system` 使用 `shell=True`，降低命令注入面。
2. **项目路径边界（2.0）**：`assert_project_in_allowed_roots()` 将 `--project` 限制在 `novels/` 与 `cursor-novel-writer/examples/` 下。

```104:116:src/novel_suite/core/paths.py
def assert_project_in_allowed_roots(project: Path) -> Path:
    """Normalize project path and ensure it stays under novels/ or writer/examples/."""
    resolved = project.resolve()
    for base in allowed_project_roots():
        try:
            resolved.relative_to(base)
            return resolved
        except ValueError:
            continue
    raise ValueError(
        f"{E.PROJECT_PATH_OUT_OF_BOUNDS}: project must be under novels/ or "
        f"{WRITER_DIR}/examples/, got {resolved}"
    )
```

3. **无危险反序列化**：未使用 `pickle`/`yaml.load`（非 safe）等。
4. **子进程参数列表化**：`video_cli`、`create_epub`、`graphify_bridge` 等均使用 `subprocess.run([...])` 列表形式。
5. **密钥与产物**：`.gitignore` 覆盖 `novels/**`、`.env`、`tmp/` 等；`SECURITY.md` 已说明报告渠道与范围。
6. **Gate 绕过已文档化**：环境变量与 flag 在 `SECURITY.md` 中明示，便于审计而非隐蔽后门。

---

## 发现项（按严重度）

### H-1：MCP 视频工具接受任意文件系统路径（条件性 High）

**位置**：`cursor-novel-video/mcp/server.py`（`render_summary`、`burn_subtitles` 等将 `chapter_path`/`video_path`/`srt_path`
直接传给 `video_cli.py`）。

**风险**：若 FastMCP 服务以 **stdio 以外方式绑定到网络**且**无身份鉴别**，远程调用者可读写/处理本机任意可读路径上的章节与视频（依赖 FFmpeg 与脚本侧行为）。

**典型部署**：Cursor 本地 MCP → **Low**（同用户信任）。  
**错误部署**：`0.0.0.0` + 无鉴权 → **High**。

**建议（P1）**：

- 文档中明确「仅本地 stdio MCP，禁止公网暴露」。
- 可选：解析路径并限制在 `suite_root()`、`novels/` 或显式 `NOVEL_SUITE_ROOT` 子树内（与 `assert_project_in_allowed_roots` 对齐）。

---

### H-2：章节草稿 `--input` 可读取项目外文件（条件性 High）

**位置**：`src/novel_suite/writer/chapter.py`（及 legacy `run_chapter_draft`）：当提供 `--input` 时从任意绝对/相对路径 `read_text`，再写入项目内
`chapters/`。

**风险**：被诱导的 Agent 可读取用户主目录、SSH 密钥路径（若可读）、其他仓库内容，并将摘要泄露到对话或 `chapters/` 落盘。

**设计意图**：允许 Agent 使用临时提纲文件；**信任模型 = 操作者 + Agent**。

**建议（P2）**：

- Skill/文档注明：仅接受项目内 `outlines/` 或 Agent 工作区下的路径。
- 可选：`--input` 必须在 `project` 目录下或 `TMP` 白名单内（会破坏部分灵活度，需产品确认）。

---

### M-1：`openai_image` 对 URL 的 HTTP GET 无超时与大小上限

**位置**：`cursor-novel-video/engine/scripts/openai_image.py`（约 `httpx.get(url)`）。

**风险**：恶意或劫持的 `url` 导致长时间挂起、大文件内存占用（SSRF 类滥用限于**出站**请求，通常无法打内网元数据除非环境特殊）。

**建议（P1）**：

- `timeout=30`，`follow_redirects=False` 或限制重定向次数。
- 校验 `Content-Length` / 流式读取上限（如 20MB）。
- 可选：仅允许 `https` + 域名 allowlist（OpenAI CDN）。

---

### M-2：`platforms/zip-refresh.ps1` / `solo-sync.ps1` 供应链与树覆盖

**位置**：从 GitHub（或用户配置的 zip URL）下载并解压到 `cursor-novel-writer` / `.trae` 等目录。

**风险**：依赖 **TLS + GitHub 完整性**；若 URL 被篡改或中间人（企业代理需额外信任），可替换引擎脚本。属**维护流程风险**，非运行时 RCE。

**建议（P2）**：

- 固定 release tag / commit SHA 校验（zip 附 SHA256 或签名）。
- 文档要求仅在官方仓库 URL 下执行 sync。

---

### M-3：Graphify `query` 将用户/Agent 提供的角色名拼入查询字符串

**位置**：`cursor-novel-writer/engine/scripts/graphify_bridge.py` — `cmd_query` 中 `q = f"{kwargs['character']}
relationships..."` 传入 `run_graphify(["query", q, ...])`。

**风险**：对 **graphify CLI** 的注入或异常参数（取决于上游 graphifyy 实现）；项目路径已通过 `--project` 约束在允许根内。

**建议（P2）**：

- 对 `character`/`from_char`/`to_char` 做长度与字符集限制（如禁止 `--`、换行、shell 元字符）。
- 保持 graphify 为可选依赖，未安装时早退（已实现）。

---

### L-1：`intel_scan` 出站 HTTP 与 HTML 解析

**位置**：`src/novel_suite/writer/intel_scan.py`（`urllib.request.urlopen` 访问 DuckDuckGo HTML）。

**风险**：网络依赖、解析不可信 HTML；写入 `intel/radar/*.md` 时若未转义，**在 Markdown 预览器中**可能存在混淆性内容（非服务端 XSS）。

**建议（P3）**：标注为「演示/辅助」；生产扫榜以人工或官方 API 为准；可选 `--offline` 仅写模板。

---

### L-2：`SKIP_GATE` / `--skip-gate` 绕过质量门

**位置**：`export.py`、`chapter.py` 等。

**风险**：低质量或不合规内容进入 EPUB/下游视频；**完整性/品牌风险**大于传统安全。

**建议**：保持 `SECURITY.md` 与审计文档可见；CI 使用 gate 全绿路径。

---

### L-3：依赖未 pin 且 CI 无漏洞扫描

**位置**：`requirements-dev.txt`、`cursor-novel-writer/requirements.txt`（`>=` 版本）；CI 无 `pip-audit`/`bandit`。

**验证**：本环境 `py -3 -m pip audit` → `unknown command "audit"`（未安装 `pip-audit`）。

**建议（P2）**：

```yaml
# CI 可选步骤
- run: pip install pip-audit && pip-audit -r requirements-dev.txt
```

并在发布前对 lockfile 或 upper bound 做周期性升级。

---

### L-4：EPUB 导出子进程 cwd 限定在 writer 根

**位置**：`src/novel_suite/writer/export.py` — `_run_create_epub` 使用 `cwd=writer_root()`，`project`/`output` 由调用方传入。

**风险**：若上层未调用 `assert_project_in_allowed_roots`，legacy 路径可能写出界；**2.0 CLI 路径应经 registry 校验**。

**建议**：在 `run_export` 入口统一 `assert_project_in_allowed_roots(project)`（若尚未调用，应补一行防御性检查）。

---

### L-5：环境变量扩展搜索路径

**位置**：`SECURITY.md` 已列 `GRAPHIFY_PATH`、`NOVEL_SUITE_ROOT` 等。

**风险**：恶意修改环境可导致加载非预期 graphify 二进制或指向错误根目录。

**建议**：文档化「勿在不可信 shell 配置中导出」；`doctor` 输出实际解析路径（部分已有）。

---

### L-6：JSON stdout 契约

**位置**：`result_contract.py` / `novel_suite.core.result`。

**评价**：有利于 Agent 解析，避免执行 stderr 中的建议命令；**降低社会工程式「请运行 curl | bash」嵌入成功率**（仍取决于 Agent 是否遵守）。

---

## 与 Web 专项参考的差异

security-best-practices 技能对 **Django/Flask/FastAPI** 有专项 reference；本项目**无 Web 路由、无 Cookie/CSRF/SSRF 服务端入口**，故未套用 OWASP
Web Top 10 逐条矩阵。若未来增加「上传章节 HTTP API」，应重新打开 Web 审查并单独立项。

---

## 修复优先级（推荐实施顺序）

| 优先级 | 项 | 工作量 | 收益 |
| --- | --- | --- | --- |
| P1 | MCP 路径约束 + 部署文档「禁止公网 MCP」 | 小 | 堵住唯一可能的远程扩大面 |
| P1 | `openai_image` 下载 timeout + 大小上限 | 小 | 防挂死/内存 |
| P2 | CI `pip-audit`（可选 `bandit -r src`） | 小 | 供应链可见性 |
| P2 | `graphify` 查询参数 sanitization | 小 | 防御纵深 |
| P2 | zip-refresh 固定 tag + SHA256 校验 | 中 | 供应链 |
| P3 | `--input` 可选限制在项目子树 | 中 | 降低 Agent 误读敏感文件 |
| P3 | `run_export` 入口强制 `assert_project_in_allowed_roots` | 小 | 防御纵深 |

---

## 验证与后续

| 检查 | 结果 |
| --- | --- |
| `shell=True` 检索 | 未发现 |
| `pickle` / 不安全 YAML | 未发现 |
| 路径边界单元测试 | `tests/writer/test_registry.py` 覆盖越界拒绝 |
| `pip audit` | 未执行（工具未安装） |
| 动态渗透 | 未做（无对外服务） |

**建议复测触发条件**：新增 HTTP 服务、MCP 网络暴露、新增 `subprocess` 与联网模块、依赖大版本升级后。

---

## 附录：审查文件清单

- `src/novel_suite/**/*.py`（CLI、writer、video、core、intel）
- `cursor-novel-writer/engine/scripts/*.py`（graphify_bridge、create_epub、validate_relations、project_registry）
- `cursor-novel-video/engine/**/*.py`（video_cli、compose_ffmpeg、tts_edge、openai_image、mcp/server.py）
- `platforms/solo-sync.ps1`、`platforms/zip-refresh.ps1`
- `SECURITY.md`、`.github/workflows/ci.yml`、`.gitignore`

---

## 补丁状态（2026-06-04）

| 项 | 状态 |
| --- | --- |
| P1 MCP 路径约束 + 文档 | ✅ `mcp/path_guard.py`, `mcp/server.py`, README/SECURITY |
| P1 `openai_image` 下载加固 | ✅ `adapters/openai_image.py`, `path_safety.download_https_bytes` |
| P2 CI `pip-audit` + `bandit` | ✅ `.github/workflows/ci.yml` |
| P2 graphify 参数过滤 | ✅ `graphify_bridge.sanitize_graphify_token` |
| P2 zip-refresh GitHub 校验 | ✅ `platforms/zip-refresh.ps1` |
| P3 `--input` 项目/临时目录 | ✅ `path_safety.assert_chapter_input_path` |
| P3 `run_export` 路径断言 | ✅ `export.run_export` |
| P3 `intel_scan` HTML 上限 | ✅ `intel_scan.ddg_search` read cap |
| P3 `intel --offline` | — 已有 `--demo` 离线夹具，未新增 flag |
