# Third-Party Notices

Novel Suite includes or may optionally use third-party software.  
**MIT-licensed Novel Suite core** does not imply all listed components are MIT or bundled by default.

**商业发布状态：** 草案 — **待人工法律复核**。见 [COMMERCIAL_RELEASE_GATE.md](COMMERCIAL_RELEASE_GATE.md)。

## Runtime dependencies (Python package)

| Component | License (declared) | Role | Core status |
| --- | --- | --- | --- |
| [jsonschema](https://pypi.org/project/jsonschema/) | MIT | JSON Schema validation | **Runtime** in `[project] dependencies` |

## Development / build dependencies

| Component | License | Role | Core status |
| --- | --- | --- | --- |
| [pytest](https://pypi.org/project/pytest/) | MIT | Test runner | `dev` optional extra only |
| [hatchling](https://pypi.org/project/hatchling/) | MIT | Build backend | Build only |

## Optional extras / adapters (default off)

| Component | License / risk | Install path | Policy |
| --- | --- | --- | --- |
| [ebooklib](https://pypi.org/project/ebooklib/) | **AGPLv3+** (PyPI metadata) | `pip install -e ".[epub]"` | **禁入商业核心**；EPUB 为可选适配器；AGPL 须法律复核 |
| [edge-tts](https://pypi.org/project/edge-tts/) | LGPLv3 + Microsoft 服务条款 | 用户自装 / TTS 适配器 | **默认关闭**；用户自审 ToS |
| FFmpeg | LGPL/GPL 依构建 | 用户自行安装 | 视频转码外部工具；许可自审 |
| Stable Diffusion WebUI | **AGPL-3.0** | 用户自部署 | **默认关闭**；见 `novel-suite/adapters/image-generation/` |
| sd-webui-controlnet | **GPL-3.0** | 用户自部署 | **默认关闭** |
| ComfyUI 生态 | 各节点许可不一 | 用户自部署 | **默认关闭** |
| [qdrant-client](https://pypi.org/project/qdrant-client/) / sentence-transformers | 各包许可 | `memory` optional extra | 向量记忆可选；非默认核心 |

## High-risk — commercial core prohibited

| Component | License / risk | Role | Policy |
| --- | --- | --- | --- |
| MediaCrawler 及类似采集工具 | NOASSERTION / 平台 ToS | 榜单/内容采集 | **商业版禁用**；须单独合规审查 |
| 未知许可证仓库 / Skill 原文 | 来源不明 | 参考 | **禁入**商业 Prompt Pack |

## Platform APIs (user-provided, default off)

| Service | Notes |
| --- | --- |
| 抖音 / 快手 / B站 / 番茄 等平台 OAuth/API | 用户自有账号与密钥；**默认关闭**；单次发布须**人工确认** |

## Legacy paths (not default core)

| Path | Notes |
| --- | --- |
| `cursor-novel-writer/requirements.txt` | 仍声明 `ebooklib` — legacy 开发路径；**不等同**商业核心默认依赖 |
| `requirements-dev.txt` | 本地开发清单；安装前须阅读本文件 |

## External reference (not bundled)

- Anthropic / OpenAI / Vercel Skills 生态 — 标准参考，**不复制原文**
- 外部开源小说/视频仓库 — 学习来源，非商业核心承诺
- `G:\SOLO小说项目` / `G:\Reasonix` — 只读参考，非捆绑内容

## Updates

维护本文件与 `THIRD_PARTY_POLICY.md`、`novel-suite/THIRD_PARTY_BOUNDARY.md` 同步。  
正式商业发布前须完成 [COMMERCIAL_RELEASE_GATE.md](COMMERCIAL_RELEASE_GATE.md) 人工法律复核。
