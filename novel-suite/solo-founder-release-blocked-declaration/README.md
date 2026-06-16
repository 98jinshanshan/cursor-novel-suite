# Solo Founder Release Blocked Declaration（O2+O3 合并）

> **红线摘要：** 通过本自查 ≠ 商业发布通过。通过本自查 ≠ 法律意见或律师复核完成。通过本自查 ≠ blocker 关闭。通过本自查 ≠ tag/zip/release 可创建。

**个人开发者阶段发布仍 blocked 的合并声明** — 明确允许与禁止范围。

```yaml
personal_dev_continue_allowed: true
commercial_release_allowed: false
verdict: blocked
```

## CLI fallback

PATH 未注册 `novel-suite` 时：

```powershell
Set-Location -LiteralPath "G:\CURSOR"
$env:PYTHONPATH="G:\CURSOR\src"
$env:PYTHONDONTWRITEBYTECODE="1"
& "G:\CURSOR\.venv\Scripts\python.exe" -m novel_suite.cli solo-founder-release-blocked-declaration validate --json
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
novel-suite solo-founder-release-blocked-declaration validate --json
```

## 相关包

- [solo-founder-freeze-self-check](../solo-founder-freeze-self-check/) — O2 替代
- [solo-founder-compliance-self-check](../solo-founder-compliance-self-check/) — O3 替代
- [commercial-release-candidate](../commercial-release-candidate/) — 商业发布门禁（仍 blocked）
