# 更新模式与最小修改原则

当应用已有工作流时，进入**更新模式**。核心原则是**最小修改**——只改动必要的部分，保持其他结构不变。

## 为什么要保持节点 ID 稳定

后端可能存储了 spec 中不支持的运行时配置（如审批策略、超时规则、高级权限等），这些配置与节点 ID 绑定。一旦修改节点 ID，后端会将其视为「删除旧节点 + 创建新节点」，导致不支持的配置全部丢失。

**因此：修改已有节点时，只改 attrs/name，绝不改 id。**

## 最小修改原则速查

| 操作 | ✅ 正确做法 | ❌ 错误做法 |
|------|-----------|-----------|
| 添加节点 | 使用新 ID，追加到 nodes 末尾 | 重排已有节点 ID |
| 删除节点 | 删除对应 node 和关联边 | 不删关联边导致孤立边 |
| 修改节点配置 | 同一 ID 下只改 attrs/name | 改 ID 导致节点重建 |
| 添加边 | 追加到 edges 数组 | 修改已有边的 from/to |
| 修改条件 | 同一条边内改 condition | 删除边再新建 |
| 调整流转 | 修改边的 from/to | 改节点 ID 来适配 |

## 使用 patch_nodes 优先

如果只是改节点名称、负责人、局部 attrs，优先使用 `patch_nodes[]`，节点 id 从 `builder flow get` 的 `spec.nodes[]` 读取：

```json
[
  {"id": "89160906", "set": {"name": "需求评审（局部改）"}}
]
```

## WorkflowSpec 更新时使用 diff 脚本辅助判断

需要提交完整 `--spec-file` 时，在 apply 前使用 diff 脚本对比新旧 spec：

```bash
python3 scripts/diff_flow_spec.py tmp/current_flow.json tmp/flow_spec.json
```

输出会显示删除的节点/边、新增的节点/边、修改的节点/边，并自动评估是否符合最小修改原则。

验证脚本也支持在 WorkflowSpec 更新模式下进行最小修改原则校验：

```bash
python3 scripts/validate_flow_spec.py \
  tmp/flow_spec.json \
  --schema tmp/flow_schema.json \
  --previous tmp/current_flow.json
```

## 更新模式 SOP 调整

在更新模式下，阶段 3.2 变为**必须执行**（读取现有 spec），阶段 5.2 的对比验证增加最小修改原则检查：

- 节点 ID 不应无故变更
- 删除的节点/边应为业务需要，而非误删
- 修改范围应仅限于业务建模中变更的部分

---

← 上一步：[01-overview.md](01-overview.md)
← 返回主流程：[../SKILL.md](../../../SKILL.md)
→ 下一步：[03-flow-patterns.md](03-flow-patterns.md)
