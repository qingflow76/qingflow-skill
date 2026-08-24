# 节点配置参考

## `responsible` 数组结构

审批、填写节点的 `responsible` 必须是 **MemberRefDTO 数组**（`minItems: 1`），而不是单值对象。

```json
"responsible": [
  {"type": "role", "roleId": 123},
  {"type": "user", "uid": 456},
  {"type": "dept", "deptId": 789, "havingSubDept": true}
]
```

### MemberRefDTO 字段

| 字段 | 类型 | 必填场景 | 说明 |
|------|------|----------|------|
| `type` | string | always | `user` / `dept` / `role` / `applicant` / `leader` / `formEmail` / `formMember` / `formDept` / `nodeLeader` |
| `uid` | integer | `type="user"` | 成员 ID |
| `deptId` | integer | `type="dept"` | 部门 ID |
| `roleId` | integer | `type="role"` | 角色 ID |
| `queId` | integer | `leader` / `formEmail` / `formMember` / `formDept` | 字段/队列 ID |
| `havingSubDept` | boolean | `type="dept"` | 是否包含子部门 |

> ⚠️ **关键区别**：
> - 成员类型 `type` 必须是 `"user"`，不是 `"member"`
> - 用户 ID 字段是 `"uid"`（整数），不是 `"uids"`（字符串数组）
> - 角色 ID 字段是 `"roleId"`（整数），不是 `"roleIds"`（字符串数组）

---

## 审批节点（approval）完整 attrs

```json
{
  "responsible": [
    {"type": "role", "roleId": 123}
  ],
  "approveType": "or_signed",
  "auditUserType": "role",
  "revert": true,
  "revertScope": "all",
  "transferScope": "all",
  "auditFeedback": false,
  "commentStatus": "not_required",
  "timeoutConfig": {"duration": {"value": 24, "unit": "hour"}, "autoExecute": "approved"}
}
```

| 字段 | 说明 | 可选值 |
|------|------|--------|
| `responsible` | 审批人（MemberRefDTO 数组） | 见上方 MemberRefDTO |
| `approveType` | 审批模式 | `or_signed`(或签) / `countersigned`(会签) |
| `auditUserType` | 审批人来源 | `role` / `user` / `dept` |
| `revert` | 允许驳回 | `true` / `false` |
| `revertScope` | 驳回范围 | `all`（可回退到任意节点） |
| `transferScope` | 转交范围 | `all` |

## 填写节点（filling）完整 attrs

```json
{
  "responsible": [
    {"type": "user", "uid": 456}
  ],
  "auditFeedback": false,
  "timeoutConfig": null,
  "fieldPermissions": [
    {"fieldId": 343290996, "permission": "editable"}
  ]
}
```

## Gateway 节点

```json
{
  "id": "g1",
  "type": "gateway",
  "name": "分支名称",
  "attrs": {"mode": "parallel"}
}
```

`mode` 取值：
- `parallel`：并行分支（出边 ≥ 2，每条边可选择 `rules` 或 `default`）
- `join`：汇合节点（多入边、单出边）

---

← 返回主流程：[../SKILL.md](../../../SKILL.md)
→ 排障参考：[11-troubleshooting.md](11-troubleshooting.md)
