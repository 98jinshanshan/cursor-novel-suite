# Solo Founder Freeze Self-Check（O2 替代）

> **红线摘要：** 通过本自查 ≠ 商业发布通过。通过本自查 ≠ 法律意见或律师复核完成。通过本自查 ≠ blocker 关闭。通过本自查 ≠ tag/zip/release 可创建。
>
> **术语：** freeze candidate 仅指本地 demo 候选冻结，不是 release freeze，不创建 tag/zip/release。

**个人开发者冻结自查** — 替代团队冻结会议；**非**会议决议、**非**发布批准。

```yaml
freeze_candidate_only: true
tag_created: false
zip_created: false
release_created: false
agent_may_create_tag: false
commercial_release_allowed: false
verdict: blocked
```

## CLI fallback

PATH 未注册 `novel-suite` 时：

```powershell
Set-Location -LiteralPath "G:\CURSOR"
$env:PYTHONPATH="G:\CURSOR\src"
$env:PYTHONDONTWRITEBYTECODE="1"
& "G:\CURSOR\.venv\Scripts\python.exe" -m novel_suite.cli solo-founder-freeze-self-check validate --json
```

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
novel-suite solo-founder-freeze-self-check validate --json
```
