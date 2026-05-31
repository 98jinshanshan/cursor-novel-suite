# Graphify Upstream 命令对照（草案）

对照 [graphify-novel](https://github.com/Anshler/graphify-novel)。`graphify_bridge.py` 需在 P1 后逐项验证。

| bridge 调用 | 预期 upstream | 状态 |
| --- | --- | --- |
| `init <premise>` | `graphify-novel init` | ⚠️ 待装 CLI 验证 |
| `review <chapter>` | `graphify-novel review` | ⚠️ |
| `update` | `graphify-novel update` | ⚠️ |
| `update --from-chapters` | 同上 + 章节索引 | ⚠️ |
| `status` | `graphify-novel status` | ⚠️ |
| `query --character` | `graphify-novel query` | ⚠️ |

离线降级：无 CLI 时写入 `bible/`、`graphify-out/meta.json`。

**真机对照规程：** [graphify-upstream-verification.md](./graphify-upstream-verification.md)
