# 常见问题与排障

`autoJudges` 属于 WorkflowSpec 路径。公开主链路是先读 `builder flow schema` / `builder flow get`，再提交 `--spec-file` 或 `--patch-nodes-file`。

| 问题 | 原因 | 解决 |
|------|------|------|
| `autoJudges` apply 后为空 | 使用了一维数组 `[{...}]` 格式 | 改为二维 `[[{...}]]` |
| 条件分支不生效 | `autoJudges` 中的 `values` 与表单选项 label 不一致 | 核对字段选项文本，确保完全一致 |
| apply 返回 `missing_input_node_ids` | 新建 flow 首次 apply 的正常提示 | 可忽略，再次 get 验证即可 |
| 录入数据后只留下“提交申请”日志，不进入下一节点 | WorkflowSpec 入口节点没有出边，或入口/路由节点缺少 `sync: true` | `builder flow get` 读回 spec，确认 applicant 出边和节点 `sync`，修正后用 `--spec-file` 发布 |
| 回退边（gateway → 前序节点）不生效 | 引擎不支持通过 gateway 实现回退 | 改用审批节点 `revert: true` |
| 审批节点无审批人 | `responsible` 中的 UID/角色 ID 无效或缺失 | 使用 `builder member search` / `role search` 确认 |
| `fieldType` 不匹配 | 单选用了 `text` 而非 `single_select` | 确认字段实际类型后更正 |

---

← 上一步：[10-node-config-reference.md](10-node-config-reference.md)
← 返回主流程：[../SKILL.md](../SKILL.md)
