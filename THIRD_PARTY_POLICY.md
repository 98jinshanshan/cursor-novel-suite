# Third-Party Policy — Novel Suite

**版本：** B4 商业合规硬化（草案）  
**法律状态：** **待人工法律复核** — 不构成法律意见。

## 1. 三层分类

| 层级 | 定义 | 默认状态 |
| --- | --- | --- |
| **自有核心** | SOP、契约、门禁、Prompt/Rules Pack、资产治理 | 可承诺、可分发（发布前仍须门禁） |
| **可选适配器** | TTS、图像、视频导出、EPUB、平台 API | **默认关闭** |
| **外部参考** | 外部 Skill、开源仓库、SOLO/Reasonix 历史素材 | 不承诺、不复制原文 |

## 2. 禁入商业核心

下列不得进入 `[project] dependencies` 或默认安装路径：

- GPL / AGPL 代码或派生实现（含 **ebooklib**、Stable Diffusion WebUI、ControlNet）
- 未知许可证或无 License 仓库内容
- MediaCrawler 及类似**平台采集**工具
- 绕过验证码/风控的自动化
- 外部 Skill 原文作为商业 Prompt Pack

## 3. 默认关闭策略

启用任何适配器前须：

1. 阅读 `novel-suite/adapters/*/ADAPTER_DISABLED_BY_DEFAULT.md`
2. 阅读本文件、`THIRD_PARTY_NOTICES.md`、`COMMERCIAL_RELEASE_GATE.md`
3. **人工书面确认**（单次发布/upload 亦须确认）

适配器类型：TTS、图像生成、视频导出、EPUB（`ebooklib`）、平台发布/采集。

**Agent 禁止**默认自动：`auth login`、`publish upload`、TTS 云服务、图像 API、采集爬虫。

## 4. AGPL/GPL/NOASSERTION 处理

| 类型 | 动作 |
| --- | --- |
| AGPL (ebooklib) | 仅 `epub` optional extra 或 legacy requirements；**禁入商业核心** |
| AGPL/GPL (SD/ControlNet) | 用户自装；产品仅文档化接口 |
| NOASSERTION (MediaCrawler) | **禁用**（商业版） |
| LGPL (edge-tts, FFmpeg) | 可选适配器 + 署名 + 用户自审 |

## 5. 发布 / 上传 / 采集

- **禁止** Agent 默认自动发布或采集
- 允许发布**前**检查（`video gate`、`publishing_gate`、`doctor --core-contracts`、`product validate`）
- 单次上传须用户**人工确认**
- `novel-suite product ...` 为只读产品层查询，**不等于**发布

## 6. ebooklib 工程状态（B4）

| 位置 | 状态 |
| --- | --- |
| `[project] dependencies` | ❌ 不得包含 |
| `[project.optional-dependencies] dev` | ❌ 已移除（B4） |
| `[project.optional-dependencies] epub` | ✅ `ebooklib>=0.18` |
| `cursor-novel-writer/requirements.txt` | ⚠️ legacy 仍声明 — 文档隔离，非商业核心默认 |

安装 EPUB：`pip install -e ".[epub]"` — 用户自担 AGPL 与法律复核。

## 7. 商业发布门禁

发布候选包须通过：

- [COMMERCIAL_RELEASE_GATE.md](COMMERCIAL_RELEASE_GATE.md) 人工勾选
- `tests/test_commercial_compliance_gate.py`
- `pytest -m "not ffmpeg"`

**当前结论：不允许商业发布**，待法律/用户最终确认。

## 8. 工程映射

- 产品边界：`novel-suite/PRODUCT_BOUNDARY.md`
- 第三方边界：`novel-suite/THIRD_PARTY_BOUNDARY.md`
- 适配器说明：`novel-suite/adapters/`
- 来源风险门禁：`novel-suite/core/gates/source_risk_gate.md`
