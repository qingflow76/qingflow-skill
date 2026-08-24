# 阶段 4：验证流程输入

主链路 `--spec-file` 使用本 Skill 自带的 WorkflowSpec 验证脚本；局部修改 `patch_nodes[]` 至少检查节点 id 来自 `builder flow get` 读回，且 `set/unset` 只包含要改的字段。

WorkflowSpec 验证命令：

```bash
# WorkflowSpec 新建模式
python3 scripts/workflow/validate_flow_spec.py \
  tmp/flow_spec.json --schema tmp/flow_schema.json

# WorkflowSpec 更新模式（同时校验最小修改原则）
python3 scripts/workflow/validate_flow_spec.py \
  tmp/flow_spec.json --schema tmp/flow_schema.json --previous tmp/current_flow.json
```

## 验证内容

1. JSON Schema 结构校验（基于 `qingflow builder flow schema` 的官方 schema）
2. DAG 无环检查
3. 单 applicant 节点检查
4. Gateway 出边条件完整性检查（rules 边必须有 autoJudges）
5. 审批/填写/抄送节点必要字段检查
6. 自动化节点配置检查
7. 孤立节点检查
8. 入口节点和需要继续路由的节点显式 `sync: true`

## 验证不通过时的处理

WorkflowSpec 根据验证脚本错误修正 spec，重新验证，直到全部通过再进入 apply。

---

← 上一步：[06-stage3-build-spec.md](06-stage3-build-spec.md)
← 返回主流程：[../SKILL.md](../../../SKILL.md)
→ 下一步：[08-stage5-apply-verify.md](08-stage5-apply-verify.md)
