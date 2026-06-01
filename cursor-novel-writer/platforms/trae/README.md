# TRAE / TRAE CN / SOLO

## 安装 Skills（必须 — 对话能力来源）

在 **Novel Suite 根目录**（含 `.novel-suite-root`，路径任意）执行：

```powershell
powershell -File platforms/install-skills.ps1 -Agents trae-cn
py -3 cursor-novel-writer/engine/novel_cli.py suite doctor
```

或：

```bash
npx skills add ./cursor-novel-writer -a trae-cn -y
npx skills add ./cursor-novel-video -a trae-cn -y
```

| 范围 | Skills 路径 |
| --- | --- |
| 项目 | `.trae/skills/` |
| 全局 (TRAE CN) | `~/.trae-cn/skills/` |

SOLO 模式使用同一 Skills 目录。触发：自然语言或 `#novel-pipeline`。

## SOLO 自定义 Agent（可选）

System Prompt 模板：[solo-agent-prompt.md](./solo-agent-prompt.md)

**上传 Agent ≠ 安装 Skills。**

- Agent：对话里显示的名字 + system prompt
- Skills：`.trae/skills/*/SKILL.md` 工具库

若 Agent 可见但报「找不到技能」，请按 [docs/verification/trae-cn.md](../../docs/verification/trae-cn.md) 排障。

## Agent 对话入口

见 [AGENTS.md](../../AGENTS.md)。

## Import 单文件（不推荐单独使用）

Settings → Rules and Skills → Import File (SKILL.md) 仅导入**一个** skill，  
无法替代完整安装（缺 `engine/scripts` 时脚本会失败）。
