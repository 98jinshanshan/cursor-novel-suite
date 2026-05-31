# Graphify Upstream 真机对照规程

**版本：** 1.0（2026-05-31）  
**状态：** 待执行（本机 graphify CLI 未安装时 bridge 走 offline）  
**命令草案：** [graphify-upstream-commands.md](./graphify-upstream-commands.md)

---

## 1. 目标

将 `engine/scripts/graphify_bridge.py` 的调用与 [graphify-novel](https://github.com/Anshler/graphify-novel) 官方 CLI **逐项对照**，填实 verification 表，消除「假定命令签名」风险。

---

## 2. 环境准备

```powershell
cd G:\CURSOR\cursor-novel-writer
pip install -r requirements.txt

# 任选一种（以 upstream 文档为准）
pip install graphify
# 或
npm install -g graphify-novel

where graphify
where graphify-novel
```

记录版本：

```powershell
graphify-novel --version
# 或 graphify --version
```

---

## 3. 测试工程

使用仓库内示例（勿用含 secrets 的私有工程）：

```text
examples/demo-novel/
```

---

## 4. 对照表（实测后填 ✅/❌）

在 **`graphify-upstream-commands.md`** 表格中更新「状态」列。

| 步骤 | bridge 命令 | 验收标准 |
| --- | --- | --- |
| 1 | `init --premise "..."` | 生成 `bible/` 或 upstream 约定目录；无 argparse 错误 |
| 2 | `status` | 输出图谱/线程摘要，非 offline JSON |
| 3 | `review --chapter chapters/01_试章.md` | 返回一致性报告或 exit 0 |
| 4 | `update --from-chapters` | 索引全部章节 |
| 5 | `query --character chen-wei` | 有结构化输出（若 upstream 支持） |

### 4.1 推荐执行顺序

```powershell
cd G:\CURSOR\cursor-novel-writer
$P = "examples/demo-novel"

py -3 engine/scripts/graphify_bridge.py --project $P init --premise "雾港匿名信与林默旧案"
py -3 engine/scripts/graphify_bridge.py --project $P status
py -3 engine/scripts/graphify_bridge.py --project $P review --chapter chapters/01_试章.md
py -3 engine/scripts/graphify_bridge.py --project $P update --from-chapters
py -3 engine/scripts/graphify_bridge.py --project $P query --character chen-wei
```

### 4.2 通过 novel CLI（回归）

```powershell
py -3 engine/novel_cli.py --project examples/demo-novel status
py -3 engine/novel_cli.py review --project examples/demo-novel
py -3 engine/novel_cli.py graphify update --project examples/demo-novel --from-chapters
```

---

## 5. 偏差处理

| 现象 | 动作 |
| --- | --- |
| 子命令名不一致 | 改 `graphify_bridge.py` `run_graphify()` 参数映射 |
| premise 需 flag 非 positional | 调整 `cmd_init` 传参 |
| review 路径需相对/绝对 | 文档 + bridge 统一为相对 project 根 |
| CLI 不存在 | 保持 offline fallback；README 注明 optional |

修完后：

1. 更新 `graphify-upstream-commands.md` 状态列  
2. 在 [docs/verification/cursor.md](../../docs/verification/cursor.md) 增加 graphify 行  
3. 提交 PR / push 并跑 CI  

---

## 6. 与 GitHub 发布顺序

1. **Cursor 本机**：pytest + export + video summary 已通过  
2. **GitHub push**：见 [GITHUB-RELEASE.md](../../docs/standards/GITHUB-RELEASE.md)  
3. **graphify 真机对照**：可在 push 前或后完成；不阻塞上传  
4. **Qoder/TRAE**：clone 同一远程仓后按 verification 模板填写  

---

*执行完毕后在本文件顶部将「状态」改为「已完成 YYYY-MM-DD」。*
