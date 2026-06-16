# Solo Founder Compliance Self-Check（O3 替代）

> **红线摘要：** 通过本自查 ≠ 商业发布通过。通过本自查 ≠ 法律意见或律师复核完成。通过本自查 ≠ blocker 关闭。通过本自查 ≠ tag/zip/release 可创建。

**个人开发者合规自查** — 替代律师/委员会评审；**非**法律意见。

```yaml
legal_conclusion_auto_generated: false
legal_review_completed: false
auto_blocker_closure: false
commercial_release_allowed: false
verdict: blocked
```

## CLI fallback

PATH 未注册 `novel-suite` 时：

```powershell
Set-Location -LiteralPath "G:\CURSOR"
$env:PYTHONPATH="G:\CURSOR\src"
$env:PYTHONDONTWRITEBYTECODE="1"
& "G:\CURSOR\.venv\Scripts\python.exe" -m novel_suite.cli solo-founder-compliance-self-check validate --json
```

## Blocker 保留

| ID | 状态 |
| --- | --- |
| B01 | open — 无律师复核 |
| B03 | open — 无真实成片 |
| B04 | open — 真实 adapter 未启用 |
| B05 | resolved-demo-only — 不代表商业权利完成 |

## 允许继续 vs 仍禁止

| 允许继续 | 仍禁止 |
| --- | --- |
| 本地 demo | 商业发布 |
| PromptPack 优化 | tag/zip/release |
| 文档打磨 | 关闭 B01–B04 |
| 多 IDE dry-run | 声称法律通过 |
| backlog 收集 | 启用真实 adapter / 上传 / 外发 |

## 校验

```powershell
novel-suite solo-founder-compliance-self-check validate --json
```
