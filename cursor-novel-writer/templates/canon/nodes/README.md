# Phase completion manifests（NEC）

每 Phase 完成后由 Agent 写入（或由 `novel init` / CLI 生成）：

```text
canon/nodes/phase-0.completion.json
canon/nodes/phase-1.completion.json
…
```

Schema：`cursor-novel-writer/schema/node-completion.schema.json`  
校验：`novel node validate --phase N --project novels/<slug>`

Phase 0 套件级清单：`intel/radar/YYYY-Www.completion.json`

同步命令（Phase 1–8）：

```bash
novel node sync --phase 4 --project novels/<slug>
```

Phase 4 分派：[phase-4-node-dispatch.md](../../references/phase-4-node-dispatch.md)
