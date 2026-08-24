# Update Flow

Use this when the app already exists and the task is only about workflow.

## Minimal sequence

1. `builder_tool_contract(tool_name="app_flow_apply")`
2. `app_get_fields`
3. Confirm the app has one explicit business status `single_select` field with `config.options`, usually named `状态`, `处理状态`, `审批状态`, `工单状态`, or `流程阶段`
4. `app_get_flow`
5. `role_search` or `member_search`
6. `role_create` if the user wants a reusable directory role and no good role exists
7. Build a complete WorkflowSpec for full replacement, or a `patch_nodes` list for targeted edits
8. `app_flow_apply`
9. `app_get_flow` when apply returns `partial_success` or the user asked for verification

If you are unsure about node shapes, call `app_flow_get_schema` and read the current `app_get_flow` / `app_flow_get` spec before guessing.

## Example

Apply a simple approval flow with a role assignee and node-level editable fields through WorkflowSpec:

```json
{
  "tool_name": "app_flow_apply",
  "arguments": {
    "profile": "default",
    "app_key": "APP_123",
    "publish": true,
    "spec": {
      "nodes": [
        {
          "id": "n1",
          "type": "applicant",
          "name": "提交申请",
          "sync": true,
          "attrs": {}
        },
        {
          "id": "n2",
          "type": "approval",
          "name": "部门审批",
          "sync": true,
          "attrs": {
            "responsible": [{"type": "role", "roleId": 123}],
            "approveType": "or_signed",
            "auditUserType": "role",
            "fieldPermissions": [{"fieldName": "状态", "permission": "editable"}]
          }
        }
      ],
      "edges": {"edges": [{"from": "n1", "to": "n2"}]}
    }
  }
}
```

For flexible business requirements, do not freehand hidden backend fields. Use this safer pattern:

1. read `app_flow_get_schema`
2. read the current flow with `app_get_flow` / `app_flow_get`
3. use `patch_nodes` for targeted edits, or submit a complete `spec` when replacing the workflow

Workflow writes use WorkflowSpec `spec` or `patch_nodes`.
After `app_flow_apply` returns blocking issues or canonical arguments, prefer reusing its `suggested_next_call.arguments` directly. Do not rewrite the result into internal fields such as `role_entries` or `editable_que_ids`.

## Common failures

### `FLOW_ASSIGNEE_REQUIRED`

Approval, fill, and copy nodes must declare at least one assignee.

Preferred fix order:

1. `role_search`
2. `member_search` only if the user explicitly named members
3. `role_create` if the business needs a reusable role
4. patch the target WorkflowSpec node with the correct `attrs.responsible`
5. retry `app_flow_apply`

### `FLOW_DEPENDENCY_MISSING`

The workflow depends on fields that do not exist yet, usually an explicit business status field. Fix schema first.

Do:

- add a business field such as `状态`, `处理状态`, `审批状态`, `工单状态`, or `流程阶段`
- use type `single_select` with a non-empty `config.options` string array
- use business options such as `草稿`, `进行中`, `已完成`

Do not:

- create platform workflow system fields such as `当前流程状态`, `当前处理人`, `当前处理节点`, or `流程标题`
- skip the flow and still report workflow completion

Preferred recovery:

1. use the returned `suggested_next_call`
2. update the complete AppForm declaration through the sibling `qingflow-app-form` Skill
3. rerun `app_get_fields`
4. rerun `app_flow_apply`

### `INVALID_FLOW_EDGE`

One or more transitions reference unknown nodes or create an invalid graph.

### `UNKNOWN_FLOW_FIELD`

The workflow referenced a field name that does not exist, often in:

- WorkflowSpec node field permission config

Call `app_get_fields` and retry with the exact field names returned by the app.

### `FLOW_NODE_TYPE_UNSUPPORTED`

The public workflow builder only supports linear flows. Remove `branch` and `condition` nodes and redesign the flow with stable sequential nodes instead of retrying the same graph.

### `STATUS_FIELD_REQUIRED`

The app has no explicit status field recognized by the workflow compiler. Switch to the `qingflow-app-form` Skill, add one through a complete versioned AppForm declaration, then retry.

### `FLOW_STAGE_CONTEXT_MISSING`

Internal flow stage context was missing or invalid. Re-run `app_flow_apply` with the normalized arguments, and do not switch to hidden `solution_*` tools.

### `VALIDATION_ERROR`

Do not keep guessing node shapes. First:

1. inspect `suggested_next_call`
2. reuse `canonical_arguments` if present
3. check `allowed_values`
4. reread `app_flow_get_schema` and current `app_get_flow` / `app_flow_get`
5. retry with a complete WorkflowSpec `spec` or a targeted `patch_nodes` payload

Do not copy internal keys from old plan outputs or logs, including:

- `role_entries`
- `editable_que_ids`

## Notes

- `app_flow_apply` publishes by default
- Prefer roles over explicit members unless the user explicitly asks for named members
- Report results precisely:
  - “WorkflowSpec 已发布” only after `app_flow_get` confirms the deployed spec
  - “流程局部修改已提交” only after `patch_nodes` apply and readback match
