# 流程模式速查

在构建 spec 前，先判断当前流程属于哪种模式，避免用错节点类型或边结构。

## 线性流程

最简单的流程模式：节点首尾相连，无分支、无条件。

```
n1 → n2 → n3 → n4
```

- 边不带 `condition`，按顺序流转即可
- 无需 gateway 节点
- 适用于：简单的提交→审批→结束

## 分支流程

分支流程属于 WorkflowSpec 主路径。需要分支时先读 `builder flow schema` / `builder flow get`，再用 `--spec-file` 提交完整 WorkflowSpec。

轻流的分支采用**并行分支**模型——通过 `gateway` 节点（`mode: parallel`）分发，所有出边指向的分支**都会进入**，通过每条边上的条件（`condition.autoJudges`）控制分支内的节点逻辑是否执行。

```
                ┌──[条件A成立]→ n3 → n4
n1 → n2 → g1 ──┤
                └──[条件B成立]→ n5
```

**关键点**：
- 分支起点必须是 `gateway`（`mode: parallel`），终点必须是 `gateway`（`mode: join`）
- 每条分支边都需要配置 `condition`，其中至少一条为 `kind: rules` 带 `autoJudges`
- 没有条件的边使用 `kind: default` 作为兜底
- 所有分支并行进入，条件只决定分支内逻辑是否执行，不存在"条件匹配就跳过其他分支"的互斥语义

## 循环/回退

**轻流工作流引擎不支持循环结构**。不要通过 gateway 或其他方式构建回到前序节点的环。

如需回退到前序节点重新处理，应使用审批节点的回退开关：

```json
{
  "type": "approval",
  "attrs": {
    "revert": true,
    "revertScope": "all"
  }
}
```

- `revert: true` 开启驳回/回退能力
- `revertScope` 控制回退范围：`all` 可回退到任意前序节点
- 这是引擎原生支持的回退机制，无需在 spec 中构建回退边

---

← 上一步：[02-update-mode.md](02-update-mode.md)
← 返回主流程：[../SKILL.md](../SKILL.md)
→ 下一步：[04-stage1-business-modeling.md](04-stage1-business-modeling.md)
