# Solo Demo Trial Intake（Q1）

**本地 demo 真实试跑记录承接** — 用户/IDE 填写；**非** Agent 代填体验结论。

```yaml
trial_executed: false
fake_feedback_generated: false
external_call_performed: false
commercial_release_allowed: false
verdict: blocked
```

## 流程

1. 按 P1 `solo-demo-15min/demo_script_15min.md` 完成真实试跑。
2. 复制 [trial_record_template.md](trial_record_template.md) 到 `.tmp/novel-suite-q/solo-demo-trial-intake/`。
3. 脱敏后由用户手动保存；R1 阶段授权后只读承接。

## 校验

```powershell
novel-suite solo-demo-trial-intake validate --json
```
