# Agent 工具权限模型（P0–P5）

Agent 调用任何 Novel Suite 能力前，须识别权限等级。本模型为 **文档规范**（F1），与 C5/C6/C7 门禁一致。

## 等级定义

| 等级 | 名称 | 说明 |
| --- | --- | --- |
| **P0** | read-only | 只读索引/校验，无副作用 |
| **P1** | dry-run local artifact | 本地计划/manifest，不外部调用 |
| **P2** | local write inside workspace | 仓内可逆写入（文档、样例、job 状态） |
| **P3** | credential-required | 需 token/OAuth/账号 |
| **P4** | external-call | 外部 API/本地进程（ComfyUI、TTS、FFmpeg 等） |
| **P5** | publish/upload/exfiltration risk | 平台发布、上传、外发 |

## 执行规则

| 等级 | Agent 自动执行 | 要求 |
| --- | --- | --- |
| P0 | ✅ 允许 | 无 |
| P1 | ✅ 允许 | 输出须含 `external_call_performed=false` |
| P2 | ⚠️ 条件允许 | 仅限 `novels/`、`cursor-novel-*`、`novel-suite/`、`.tmp/` 等仓内路径；不可逆操作须确认 |
| P3 | ❌ 须人工确认 | `auth login`、cookie、API key |
| P4 | ❌ 须人工确认 | 须 C8 安全评审 + adapter 显式启用 |
| P5 | ❌ 默认禁止 | 用户明确授权 + 商业/法律门禁 + `publishing_gate` |

## 当前能力映射

| 能力 | 等级 | 入口示例 |
| --- | --- | --- |
| `product list/read/validate` | **P0** | `novel-suite product validate --json` |
| `commercial-review validate` | **P0** | `novel-suite commercial-review validate --json` |
| `doctor --core-contracts` | **P0** | `novel-suite doctor --core-contracts --json` |
| C5 adapter dry-run | **P1** | `video-production adapter dry-run --adapter comfyui` |
| `writer init` / chapter draft | **P2** | `novel-suite writer init` |
| `memory store` | **P2** | `novel-suite memory store` |
| video job create/run | **P2–P4** | 无 FFmpeg/TTS 时 P2；调用 FFmpeg 升为 P4 |
| `auth login` / token | **P3** | `novel-suite auth login` |
| ComfyUI / Runway / Kling / Pika / Luma | **P4** | 未实现执行；handoff 文档 only |
| TTS (`edge-tts`) / 图像生成 | **P4** | adapter 默认关闭 |
| FFmpeg 真实执行 | **P4** | `pytest -m ffmpeg` 与用户环境 |
| `publish upload` / 平台 OAuth | **P5** | `novel-suite video publish`、MCP `tool_publish_upload` |

## MCP 工具分级（摘要）

| MCP 工具族 | 默认等级 |
| --- | --- |
| `tool_product_*` | P0 |
| `tool_auth_*` | P3 |
| `tool_publish_*` | P5（upload）/ P0（readiness/guide） |

## Skill 作者须知

1. Skill 正文应标明推荐权限等级。
2. 禁止 Skill 默认链式调用 P4/P5。
3. P5 须引用 `COMMERCIAL_RELEASE_GATE.md` 与 `claims-forbidden.md`。
4. dry-run 产物不得宣传为「已完成渲染」。

## 与 Commercial Gate 关系

- C6 `release-blockers.md`：商业发布 P0–P1 演示 vs P5 阻断。
- C7 `claims-forbidden.md`：禁止暗示 P4/P5 默认可用。
