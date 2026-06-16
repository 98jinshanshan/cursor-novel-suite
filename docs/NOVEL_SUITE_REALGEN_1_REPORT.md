# Novel Suite RealGen-1 执行报告

> **状态：已废止（superseded）**  
> **取代：** [NOVEL_SUITE_REALPIPELINE_2B_REPORT.md](./NOVEL_SUITE_REALPIPELINE_2B_REPORT.md)  
> **日期：** 2026-06-15

---

## 正式认定：RealGen-1 验收失败（D 级）

OpenClaw / 用户审计结论：**RealGen-1 未走原工作流，不得作为成功证据。**

| 失败项 | 说明 |
| --- | --- |
| 旁路 demo | 写入 `novel-suite/realgen-demo/`，非 `novels/novel-837dd4f1` |
| 角色错误 | 使用林澄/程砚，非冷案回声 canon（林骁/陈琪/傅正昆/苏晚晴） |
| 字数违规 | 1334 CJK 仅为通过旁路测试，非起点 2500–4000 合同 |
| 跳过节点 | 无 P0 扫榜、无 voice-brief、无 DeAI、无 NVP verdict |
| 视频冒充 | 动态文字卡 FFmpeg 色块，非 motion-drama |

**错误产物已删除。** 请仅使用 RealPipeline-2B。

---

## 正确入口

```powershell
.\.venv\Scripts\python.exe -m novel_suite.cli realpipeline validate --project novels/novel-837dd4f1 --json
```

见 [NOVEL_SUITE_REALPIPELINE_2B_REPORT.md](./NOVEL_SUITE_REALPIPELINE_2B_REPORT.md)。
