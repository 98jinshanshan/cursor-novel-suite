# Final Verification（本地收尾验收）

**版本：** 1.0（2026-06-02）  
**脚本（Windows）：** [platforms/final-verify.ps1](../../platforms/final-verify.ps1)  
**脚本（Linux/macOS/CI）：** [platforms/final-verify.sh](../../platforms/final-verify.sh)  
**Cursor 规则：** [post-code-problems-check.mdc](../../.cursor/rules/post-code-problems-check.mdc)  
**CI：** `.github/workflows/ci.yml` → `final-verify` job

---

## 目的

把「记得检查 Problems / pytest」从软约束变成**可执行命令**，降低 Agent 在长对话中遗漏验收的概率。

三层防护建议：

```text
Cursor 规则（提醒 + 固定收尾模板）
    + platforms/final-verify.ps1（本地一键）
    + CI / pre-commit（硬拦截，见 .github/workflows）
```

---

## 何时运行

- 本轮对话**修改了代码/配置/模板**且即将向用户声明「完成」
- Phase 收尾、JSON 契约修复、CLI/engine 改动后

可跳过：纯问答、只读审计、用户明确不要动仓库。

---

## 命令

```powershell
powershell -File platforms/final-verify.ps1
```

```bash
bash platforms/final-verify.sh
```

常用参数：

| 参数 | 作用 |
| --- | --- |
| `-ChangedOnly` | 仅对 git 变更的 `.py` 跑 pyright |
| `-SkipPytest` | 跳过 pytest（仅做静态检查时用） |
| `-SkipMarkdown` | 跳过 markdownlint |

---

## Agent 收尾模板（必须出现在最终回复）

```markdown
### Final Verification
- Problems: 已检查 / 清零 / 遗留项：…
- Script: `powershell -File platforms/final-verify.ps1` → …
- Tests: `py -3 -m pytest -m "not ffmpeg" -q` → …
- Files changed: …
- Remaining blockers: 无 / …
```

未运行 `final-verify.ps1`（或等价步骤并说明原因）时，**不得**声明任务完成。

---

## 与 POST-CODE-VERIFICATION 的关系

- [POST-CODE-VERIFICATION.md](./POST-CODE-VERIFICATION.md)：原则与 ReadLints 职责
- 本文档：可执行脚本 + 固定汇报块

两者同时生效；脚本不替代 IDE Problems，但可覆盖 pytest / pyright / markdownlint。

## markdownlint 范围（与 CI 一致）

`final-verify.ps1` 与 `.github/workflows/ci.yml` 的 `lint` job 使用相同 glob：

- `cursor-novel-writer/**/*.md`
- `cursor-novel-video/**/*.md`
- `docs/**/*.md`
- **`intel/**/*.md`**（含本地 `intel/radar/*.md`，即使用户数据被 gitignore）
- `skills/**/*.md`
- `.cursor/rules/**/*.mdc`
- `novels/README.md`
- 仓库根 `*.md`

另跑 **`tests/test_intel_radar_markdown.py`**：保证 `intel_scan.render_radar` 产出可通过 markdownlint（CI 硬拦截，不依赖 radar 文件进 git）。
