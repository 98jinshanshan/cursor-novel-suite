# Novel Suite W1+W2 UI Agent Workbench MVP 执行报告

**日期：** 2026-06-01  
**范围：** agent-entry-menu、本地 API Server、静态 UI Workbench  
**商业状态：** `commercial_release_allowed=false`，`verdict=blocked`（未改）

---

## 目标

将 Novel Suite 从 CLI/文档入口升级为可验证的 **UI Agent Workbench MVP 契约**：

```text
agent-entry-menu validate
→ server validate
→ server run（可选）
→ 静态 UI 展示 doctor / active / 6 菜单 / market-scan demo
```

## 交付物

| 路径 | 说明 |
| --- | --- |
| `novel-suite/agent-entry-menu/` | 6 菜单项 manifest、IDE 映射、边界 |
| `novel-suite/server/api-contract.json` | REST API 契约 |
| `novel-suite/ui-agent-workbench/static/` | index.html / app.js / styles.css |
| `src/novel_suite/core/agent_entry_menu.py` | validate / list |
| `src/novel_suite/server/` | app、contracts、runner、routes |
| `tests/test_agent_entry_menu.py` | W1 测试 |
| `tests/test_ui_agent_server_contract.py` | W2 server 测试 |
| `tests/test_ui_agent_workbench_assets.py` | UI 资产测试 |

## CLI

```powershell
novel-suite agent-entry-menu validate --json
novel-suite agent-entry-menu list --json
novel-suite server validate --json
novel-suite server run --host 127.0.0.1 --port 8765
```

## 验证结果（2026-06-01）

| 命令 | 结果 |
| --- | --- |
| `agent-entry-menu validate` | OK（6 项；blocked 字段） |
| `agent-entry-menu list` | OK |
| `server validate` | OK |
| `product validate` | OK |
| `commercial-release-candidate validate` | OK，`verdict=blocked` |
| 专项 pytest | 12 passed |

## 边界遵守

- 未读取 SOLO / Reasonix
- 未联网；market-scan API 仅 `demo=True`
- 未执行 adapter / FFmpeg / TTS / 图像 / 视频
- 未创建 tag / zip / release
- `novel.create` UI 为 planned/disabled

## 下一步

1. 用户确认是否安装 `novel-suite[server]`（FastAPI extra，可选）
2. OpenClaw 按本地 Workbench 路线复测
3. 接入 `ip.to_short_drama` Demo 为第二个可运行 Agent
