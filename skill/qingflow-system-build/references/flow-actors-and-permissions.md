# Flow Actors And Permissions

Use this when the workflow needs real assignees or node-level editable field permissions.

## Canonical policy

- Approval, fill, and copy nodes must declare at least one assignee.
- Prefer roles over explicit members.
- Resolve directory actors before calling `app_flow_apply`.
- Use WorkflowSpec keys from `app_flow_get_schema`; for assignees this is `attrs.responsible`.
- For node-level field permissions, follow the current WorkflowSpec schema/readback shape.

## Recommended order

1. `app_get_fields`
2. `app_get_flow`
3. `role_search`
4. `member_search` when the user explicitly names people
5. `role_create` when no reusable role exists and the user wants role-based routing
6. `app_flow_apply`

## Examples

### Route an approval node to a reusable role

```json
{
  "tool_name": "app_flow_apply",
  "arguments": {
    "profile": "default",
    "app_key": "APP_123",
    "publish": true,
    "spec": {
      "nodes": [
        {"id": "n1", "type": "applicant", "name": "提交申请", "sync": true, "attrs": {}},
        {
          "id": "n2",
          "type": "approval",
          "name": "部门审批",
          "sync": true,
          "attrs": {
            "responsible": [{"type": "role", "roleId": 123}],
            "approveType": "or_signed",
            "auditUserType": "role"
          }
        }
      ],
      "edges": {"edges": [{"from": "n1", "to": "n2"}]}
    }
  }
}
```

### Route to explicit members when the user names people

```json
{
  "tool_name": "app_flow_apply",
  "arguments": {
    "profile": "default",
    "app_key": "APP_123",
    "publish": true,
    "spec": {
      "nodes": [
        {"id": "n1", "type": "applicant", "name": "提交申请", "sync": true, "attrs": {}},
        {
          "id": "n2",
          "type": "approval",
          "name": "部门审批",
          "sync": true,
          "attrs": {
            "responsible": [{"type": "user", "uid": 10001}, {"type": "user", "uid": 10002}],
            "approveType": "or_signed",
            "auditUserType": "user"
          }
        }
      ],
      "edges": {"edges": [{"from": "n1", "to": "n2"}]}
    }
  }
}
```

### Let one node edit selected fields only

```json
{
  "tool_name": "app_flow_apply",
  "arguments": {
    "profile": "default",
    "app_key": "APP_123",
    "publish": true,
    "spec": {
      "nodes": [
        {"id": "n1", "type": "applicant", "name": "提交申请", "sync": true, "attrs": {}},
        {
          "id": "n2",
          "type": "approval",
          "name": "部门审批",
          "sync": true,
          "attrs": {
            "responsible": [{"type": "role", "roleId": 123}],
            "approveType": "or_signed",
            "auditUserType": "role",
            "fieldPermissions": [
              {"fieldName": "状态", "permission": "editable"},
              {"fieldName": "审批意见", "permission": "editable"},
              {"fieldName": "项目负责人", "permission": "editable"}
            ]
          }
        }
      ],
      "edges": {"edges": [{"from": "n1", "to": "n2"}]}
    }
  }
}
```

## Common recovery

### `ROLE_NOT_FOUND` / `AMBIGUOUS_ROLE`

- retry with `role_search`
- if the business wants a reusable route and no exact role exists, create one with `role_create`

### `MEMBER_NOT_FOUND` / `AMBIGUOUS_MEMBER`

- retry with `member_search`
- do not guess user ids

### `UNKNOWN_FLOW_FIELD`

- reread fields with `app_get_fields`
- only reference real current field names in WorkflowSpec field permission structures
