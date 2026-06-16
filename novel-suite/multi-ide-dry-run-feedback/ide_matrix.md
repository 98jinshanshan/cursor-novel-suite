# IDE 覆盖矩阵（P3）

| IDE | 标识 | Trial Card 参考 | P3 反馈要求 |
| --- | --- | --- | --- |
| Cursor | `cursor` | `multi-ide-trials/trial_cards/cursor_trial_card.md` | 填写 feedback_template |
| Codex | `codex` | `multi-ide-trials/trial_cards/codex_trial_card.md` | 同上 |
| TRAE CN | `trae_cn` | `multi-ide-trials/trial_cards/trae_cn_trial_card.md` | 同上 |
| Qoder | `qoder` | `multi-ide-trials/trial_cards/qoder_trial_card.md` | 同上 |
| OpenClaw | `openclaw` | `multi-ide-trials/trial_cards/openclaw_trial_card.md` | 同上 |
| Generic Agent | `generic_agent` | `multi-ide-trials/trial_cards/generic_agent_trial_card.md` | 同上 |

## 统一字段

所有 IDE 使用同一 `feedback_template.md`，便于 Q3 汇总与 backlog 归类。

## 禁止差异

- 不得因 IDE 不同而放宽 `commercial_release_allowed=false`
- 不得因 IDE 不同而默认允许 `external_call_performed=true`
- 不得自动采集任一 IDE 的聊天遥测
