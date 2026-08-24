# 阶段 5：Apply + 验证循环

## 5.1 部署工作流

推荐主链路：

```bash
qingflow --json builder flow apply \
  --app-key <APP_KEY> \
  --spec-file tmp/flow_spec.json \
  --publish \
  > tmp/flow_apply.json
```

局部修改已存在节点：

```bash
qingflow --json builder flow apply \
  --app-key <APP_KEY> \
  --patch-nodes-file tmp/flow_patch_nodes.json \
  --publish \
  > tmp/flow_patch_apply.json
```

### 解读响应

- `status: success` → 进入验证
- `status: failed` → 查看 `error_code` / `message` / `blocking_issues`，修正后重试
- `missing_input_node_ids` 警告（新建时常见）→ 可忽略，是正常现象
- 成功写入应读取 `write_executed=true`、`write_succeeded=true`、`safe_to_retry=false`；不要因中间读回 pending 立刻重放。

## 5.2 验证部署结果

```bash
qingflow --json builder flow get --app-key <APP_KEY> > tmp/deployed_flow.json
```

### 逐项对比

1. **节点数量与类型**：`nodes` 数量是否一致，每个节点的 `type` 和 `name` 是否正确
2. **边连通性**：`edges` 数量是否一致，`from`/`to` 关系是否正确
   - 必须确认 `applicant` 入口节点存在出边，不能只停留在“提交申请”
3. **分支条件**（WorkflowSpec 路径）：每个 gateway 出边是否有正确的 `autoJudges`
   - 检查 `condition.kind` 是否为 `rules`
   - 检查 `autoJudges` 中的 `fieldId`、`judgeType`、`values` 是否正确
   - **`autoJudges` 必须是非空二维数组 `[[{...}]]`，空数组或一维数组说明条件未生效**
4. **自动化节点**：`automation` 节点的 `subType`、`appKey`、`fieldMappings` 等是否正确
   - 必要时拉取其他应用数据验证：`qingflow --json builder app get --app-key <目标APP_KEY> fields`
5. **审批节点**：`responsible`、`approveType`、`revert` 等是否与建模一致

## 5.3 不一致时的循环

若验证发现不一致：
1. 分析差异原因（条件格式错误、节点缺失、边遗漏等）
2. 修正 `tmp/flow_spec.json`
3. 重新验证 → apply → 对比
4. **最多循环 3 次**；若 3 次后仍有不可修复的差异，告知用户并列出：
   - 已成功配置的部分
   - 仍存在差异的部分及可能原因
   - 建议用户在 Web 端手动调整的部分

---

← 上一步：[07-stage4-validate-spec.md](07-stage4-validate-spec.md)
← 返回主流程：[../SKILL.md](../SKILL.md)
→ 下一步：[09-stage6-summary.md](09-stage6-summary.md)
