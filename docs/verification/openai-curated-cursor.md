# OpenAI `.curated` Skills — Cursor 安装记录

**日期：** 2026-06-04  
**来源：** [openai/skills/skills/.curated](https://github.com/openai/skills/tree/main/skills/.curated)

## 已安装（全局）

| Skill | 用途 | 路径 |
| --- | --- | --- |
| `gh-fix-ci` | GitHub Actions PR 检查失败排查与修复（需 `gh`） | `%USERPROFILE%\.agents\skills\gh-fix-ci\` |
| `security-best-practices` | Python/JS/Go 安全最佳实践与报告 | `%USERPROFILE%\.agents\skills\security-best-practices\` |

**未安装（与 Cursor 内置 `babysit` 重叠）：** `gh-address-comments`

## 安装命令

```powershell
npx skills add openai/skills@gh-fix-ci -a cursor -g -y
npx skills add openai/skills@security-best-practices -a cursor -g -y
```

## 依赖

- **GitHub CLI：** `winget install --id GitHub.cli -e`
- 已安装：`gh` 2.93.0（`winget install --id GitHub.cli -e`）
- **待你本机完成（交互式）：** `gh auth login`（勾选 `repo` + `workflow`），然后 `gh auth status` 应显示已登录

## Cursor 对话触发示例

```text
Read gh-fix-ci skill，检查当前分支 PR 的 failing checks 并给出修复计划（先别改代码）。
```

```text
Read security-best-practices，对本项目做一次 Python 安全审查并写报告。
```

## 适配说明

两个技能的 `SKILL.md` 已增加 **Cursor IDE** 小节：去掉 Codex `$skill-installer` / `sandbox_permissions`，`create-plan` 改为 Plan
模式或内联计划。
