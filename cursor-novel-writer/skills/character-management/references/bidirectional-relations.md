# 双向人物关系（SS-05）

story-skills 要求：**A→B 的关系必须在 B→A 有对应条目**（类型可不对称，但不可单边缺失）。

## 文件约定

`characters/<id>.md` frontmatter：

```yaml
relationships:
  - target: lin-mo
    type: 同事/秘密同盟
    since: ch01
```

## 维护步骤

1. 新建或修改 A 的 `relationships` 时，打开 `characters/<target>.md`
2. 添加/更新指向 A 的条目（`target: <a-id>`）
3. 更新 `characters/_index.md` 若角色新增
4. 大改后：`novel graphify update --from-chapters`

## 关系类型参考

| type 示例 | 说明 |
| --- | --- |
| 同事/上下级 | 职场线 |
| 亲属/恋人/前任 | 情感线 |
| 对立/怀疑/追踪 | 冲突线 |
| 同盟/师徒/线人 | 情节功能 |

## 可选校验

```bash
python engine/novel_cli.py relations check --project novels/<slug>
```

输出：缺失反向链接的 `(from → to)` 列表；exit 1 若有问题。

## Agent 检查清单

- [ ] 新角色已写入 `_index.md`
- [ ] 每条 `relationships[].target` 对应存在的 `<id>.md`
- [ ] 反向链接已补全
- [ ] 关系与 `plot/foreshadowing.md` / 最新 snapshot 无矛盾
