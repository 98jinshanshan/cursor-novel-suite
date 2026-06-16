# 第三方边界

**与根目录同步：** [THIRD_PARTY_NOTICES.md](../THIRD_PARTY_NOTICES.md)、[THIRD_PARTY_POLICY.md](../THIRD_PARTY_POLICY.md)、[COMMERCIAL_RELEASE_GATE.md](../COMMERCIAL_RELEASE_GATE.md)

## 禁入商业核心

| 项 | 许可证/风险 | 处理 |
| --- | --- | --- |
| `ebooklib` | AGPLv3+ | 仅 `epub` optional extra（`pip install -e ".[epub]"`）；legacy `cursor-novel-writer/requirements.txt` 须文档隔离 |
| Stable Diffusion WebUI | AGPL | `adapters/image-generation/`，**默认关闭** |
| sd-webui-controlnet | GPL | 同上 |
| `MediaCrawler` | NOASSERTION + 平台规则 | 商业版**禁用** |
| 未知许可证 Skill/仓库 | 来源不明 | 禁入，仅外部参考 |

## 默认关闭的可选适配器

| 适配器 | 工程线索 | 启用前 |
| --- | --- | --- |
| TTS | `edge-tts`, `tts_edge.py` | 读 `adapters/tts/`，**人工确认** |
| 图像生成 | ComfyUI / SD adapters | 读 `adapters/image-generation/` |
| 视频导出 | FFmpeg pipeline | 读 `adapters/video-export/`，用户自装 FFmpeg |
| EPUB | `ebooklib`, `writer export` | `pip install -e ".[epub]"`，AGPL 法律复核 |
| 平台发布 | OAuth + `publish upload` CLI/MCP | 读 `adapters/platform-publishing/`，**禁止 Agent 默认自动执行** |

## Runtime vs optional（B4）

| 依赖 | 层级 |
| --- | --- |
| `jsonschema` | 允许 runtime（MIT） |
| `pytest`, `hatchling` | dev / build only |
| `ebooklib` | **epub** extra only |
| `edge-tts`, FFmpeg, SD, ControlNet | 适配器 / 外部工具，**默认关闭** |

## 署名义务

正式发布前须：

1. 更新 `THIRD_PARTY_NOTICES.md`
2. 完成 `COMMERCIAL_RELEASE_GATE.md` 人工法律复核
3. 运行 `tests/test_commercial_compliance_gate.py`

## 平台与自动化

- **禁止默认：** 绕过验证码、Cookie 采集、无人值守批量发布、Agent 自动 `publish upload`
- **允许：** 发布前检查清单、`doctor --core-contracts`、`product validate`、人工确认后的单次上传

## 引用规格源

- AI_Workspace_OS：`商业核心禁入规则.md`、`第三方适配器默认关闭规则.md`、`必须署名_替换_隔离_禁用清单.md`
