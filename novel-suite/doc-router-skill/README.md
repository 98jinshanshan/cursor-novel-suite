# DocRouter Skill 注册说明

规则级文档路由 Skill 主文件：

```text
G:/CURSOR/skills/doc-router/SKILL.md
```

## 安装到 IDE

```powershell
powershell -File platforms/install-skills.ps1 -Agents cursor
```

或手动 symlink/copy 到 `.agents/skills/doc-router/`。

## CLI 入口（规则层）

```powershell
python -m novel_suite.cli doc-router preflight "<任务>" --json
python -m novel_suite.cli doc-router query "<关键词>" --top-k 10 --json
python -m novel_suite.cli doc-router build --root G:/CURSOR --json
python -m novel_suite.cli doc-router validate --json
```

## Cursor 规则

`.cursor/rules/doc-router.mdc`（alwaysApply 建议由用户按需启用；长任务 Agent 须 Read 本 Skill）
