# Update Views

Use this when the task is only about table, card, board, or gantt views.

## Minimal sequence

1. `builder_tool_contract(tool_name="app_views_apply")`
2. `app_get_fields`
3. `app_get` for current view/chart/button inventory and app-level associated resource ids
4. `app_views_apply`
5. Use `app_associated_resources_apply` if the task includes associated reports/views
6. `app_get` or `view_get` again whenever apply returns `failed` or `partial_success`

If you are unsure about keys or view types, call `builder_tool_contract(tool_name="app_views_apply")` before guessing.

Important verification rule:

- `app_views_apply` can create a view object before every filter is fully verified in readback
- Do not report “筛选已成功应用” unless the apply result also shows `verification.views_verified=true` and `verification.view_filters_verified=true`
- Do not report “查询条件已成功配置” unless the apply result also shows `verification.view_query_conditions_verified=true`
- Do not report “关联资源已成功配置” unless `app_associated_resources_apply` shows `verification.associated_resource_view_configs_verified=true`
- If apply returns `partial_success`, inspect `verification.by_view`, `details.filter_mismatches`, `details.query_condition_mismatches`, and `details.associated_resource_mismatches` before claiming filters/query conditions/associated resources are active

## Example

Canonical rules before any example:

- Always use `columns`
- Do not emit `column_names`
- Treat `fields` only as a legacy alias the MCP may normalize, not as the preferred shape
- Use `filters` with the unified fixed-filter DSL: `field_name`, `operator`, `value`/`values`; do not write raw `judgeType` / `judgeValues`
- Use `query_conditions` for the frontend query panel. Do not put query-panel fields into `filters`.
- Do not create views named `全部数据`, `我的数据`, `我发起的`, `待办`, `已办`, or `抄送`. These are built-in default/system views. New views must use business-specific names such as `订单台账视图`, `客户跟进视图`, or `逾期任务看板`.
- To change a built-in default/system view, first read the existing raw `view_key` from `app_get.views` or `app_get_views`, then use `views[]` with `operation: "patch"`.
- New views created by `app_views_apply` default the frontend associated report/view area to visible with `limit_type="all"`. Existing views preserve their current associated-resource display unless `associated_resources` is explicitly patched.
- Use `app_associated_resources_apply` for the associated report/view resource pool, selected resources, and match rules. Permission is split like the backend: resource pool writes use EditAppAuth, while `view_configs` uses the view config/DataManageAuth path. `associated_item_id` is the internal associated-resource id from `app_get.associated_resources`; `view_configs`, remove, and reorder may also pass an existing resource's `chart_id`/`chart_key`/`view_key`, which the tool resolves to the internal id. Do not write backend raw `sourceType`; reports default to BI app reports, and dataset reports use `report_source="dataset"`. Use `match_mappings` with `target_field + operator + source_field/value` for associated view/report filters; read `match-rules.md` if field type compatibility is unclear.
- For gantt, use `start_field`, `end_field`, and optionally `title_field`
- If `app_get.views` or `app_get_views` shows duplicate view names, include `view_key` in `views[]` and update that exact target
- Builder view writes always use the raw `view_key` from `app_get.views[].view_key`, such as `emsrao25rs02`. Do not pass `custom:emsrao25rs02`; that prefixed form is only for record-data `view_id`.
- For an existing view, prefer `views[].operation="patch"` for parameter replacement. Do not send a partial `upsert` object such as only `name/type/query_conditions`; backend view saves require other type-specific fields, and the patch path preserves them for you.
- For view-specific business buttons, declare `action_buttons` inside the same `views[]` item. For existing views, use `operation: "patch"` with `set.action_buttons`.
- Choose the button by user intent before choosing a trigger type:
  - current record -> downstream/related record: `add_data` with `target_app_key + field_mappings`
  - global independent entry: `add_data` on `header` without current-record `source_field`
  - URL/SOP/help page: `link` with `url`
  - approval/status transition/close task: do not fake it with a normal button; use workflow/task action or exact existing automation config
- Button placement choice: `header` is global and has no current-row context; `list` is row/list action; `detail` is the safest current-record context action. Do not use current-record `field_mappings` on `header`.

Apply a business table view:

```json
{
  "tool_name": "app_views_apply",
  "arguments": {
    "profile": "default",
    "publish": true,
    "views": [
      {
        "operation": "upsert",
        "app_key": "APP_123",
        "name": "订单台账视图",
        "view_key": "VIEW_KEY_IF_DUPLICATE_NAMES_EXIST",
        "type": "table",
        "columns": ["订单编号", "客户名称", "订单金额", "状态"]
      }
    ]
  }
}
```
After `app_views_apply` returns canonical arguments or blocking issues, prefer reusing its `suggested_next_call.arguments` directly. Do not rewrite aliases back into non-canonical keys such as `column_names`.

Create a table view with ordinary business buttons:

```json
{
  "tool_name": "app_views_apply",
  "arguments": {
    "profile": "default",
    "publish": true,
    "views": [
      {
        "operation": "upsert",
        "app_key": "APP_123",
        "name": "工单执行视图",
        "type": "table",
        "columns": ["工单编号", "产品", "状态", "负责人"],
        "action_buttons": [
          {
            "text": "创建质检单",
            "action": "add_data",
            "target_app_key": "QUALITY_APP",
            "field_mappings": [
              {"source_field": "数据ID", "target_field": "关联工单"}
            ],
            "default_values": {"处理状态": "待处理"},
            "placement": "detail",
            "visible_when": [
              {"field_name": "状态", "operator": "eq", "value": "已完工"}
            ]
          },
          {
            "text": "查看作业说明",
            "action": "link",
            "url": "https://example.com/sop",
            "placement": "header"
          }
        ]
      }
    ]
  }
}
```

Existing table view: replace only frontend query conditions:

```json
{
  "tool_name": "app_views_apply",
  "arguments": {
    "profile": "default",
    "publish": true,
    "views": [
      {
        "operation": "patch",
        "app_key": "APP_123",
        "view_key": "VIEW_KEY",
        "set": {
          "query_conditions": {
            "enabled": true,
            "exact": false,
            "hide_before_query": false,
            "rows": [["客户名称", "负责人"], ["创建时间"]]
          }
        }
      }
    ]
  }
}
```

Meaning:

- `filters` are saved view filters and apply immediately when the view opens.
- `query_conditions` only configures which fields appear in the frontend query panel. The query values come later from the user through the page.
- `query_conditions.rows` is a matrix of field names and is compiled to backend `queryCondition` field ids.
- The patch call preserves the view's existing columns, saved filters, type-specific date/card/board config, buttons, visibility, and other backend-required fields.

View associated resources example:

```json
{
  "tool_name": "app_associated_resources_apply",
  "arguments": {
    "profile": "default",
    "app_key": "APP_123",
    "upsert_resources": [],
    "remove_associated_item_ids": [],
    "reorder_associated_item_ids": [],
    "view_configs": [
      {
        "view_key": "VIEW_KEY",
        "visible": true,
        "limit_type": "select",
        "associated_item_ids": [123, 124]
      }
    ]
  }
}
```

Use `{"visible": true, "limit_type": "all"}` to show all app-level associated resources, and `{"visible": false}` to hide the area. The ids above can be internal `associated_item_id` values or existing resource `chart_id`/`chart_key`/`view_key` values from `app_get.associated_resources`. Before creating a resource, check whether the same `target_app_key + view_key/chart_key` already exists; if it does, use `patch_resources` with that `associated_item_id`. Dataset BI reports must already exist in QingBI and should be attached with `report_source="dataset"`; do not try to create them through `app_charts_apply`. If you create a new associated item in the same call, give it a `client_key` and reference it from `view_configs[].associated_item_refs`; `client_key` is not persisted and cannot deduplicate a later call.

Create and show a BI indicator-card report in the same call:

```json
{
  "tool_name": "app_associated_resources_apply",
  "arguments": {
    "profile": "default",
    "app_key": "APP_123",
    "upsert_resources": [
      {
        "client_key": "total_hours_card",
        "graph_type": "chart",
        "target_app_key": "TIMESHEET_APP",
        "chart_key": "CHART_KEY",
        "report_source": "app",
        "match_mappings": [
          {"target_field": "关联员工", "source_field": "数据ID"},
          {"target_field": "状态", "value": "待提交"}
        ]
      }
    ],
    "remove_associated_item_ids": [],
    "reorder_associated_item_ids": [],
    "view_configs": [
      {
        "view_key": "VIEW_KEY",
        "visible": true,
        "limit_type": "select",
        "associated_item_refs": ["total_hours_card"]
      }
    ]
  }
}
```

Board example:

```json
{
  "tool_name": "app_views_apply",
  "arguments": {
    "profile": "default",
    "views": [
      {
        "operation": "upsert",
        "app_key": "APP_123",
        "name": "按状态看板",
        "type": "board",
        "group_by": "状态",
        "columns": ["订单编号", "客户名称", "订单金额"]
      }
    ]
  }
}
```

Gantt example with filters:

```json
{
  "tool_name": "app_views_apply",
  "arguments": {
    "profile": "default",
    "views": [
      {
        "operation": "upsert",
        "app_key": "APP_123",
        "name": "项目甘特图",
        "type": "gantt",
        "columns": ["项目名称", "开始日期", "结束日期", "状态"],
        "start_field": "开始日期",
        "end_field": "结束日期",
        "title_field": "项目名称",
        "filters": [
          {
            "field_name": "状态",
            "operator": "eq",
            "value": "进行中"
          }
        ]
      }
    ]
  }
}
```

## Common failures

### `UNKNOWN_VIEW_FIELD`

At least one `columns` or `group_by` field name does not exist.

### `INVALID_VIEW_TYPE`

Public view types are only `table`, `card`, `board`, `gantt`.

Map old or intuitive labels before calling the tool:

- `tableView` -> `table`
- `cardView` -> `card`
- `kanban` -> `board`

### `INVALID_GANTT_CONFIG`

Gantt views require at least:

- `start_field`
- `end_field`

Also make sure these field names already exist on the app.

### `VIEW_APPLY_FAILED`

The backend rejected the normalized view payload. Re-read fields and inspect `request_id` before retrying.

Do not repeat `app_views_apply` with guessed keys. First:

1. check `suggested_next_call`
2. reuse `canonical_arguments` if present
3. call `app_get_views` to see whether any requested views landed anyway
4. if needed, call `builder_tool_contract`
5. retry only the minimal failed view patch

### `VIEW_FILTER_READBACK_MISMATCH`

The view object was created or updated, but the readback config did not keep the intended filter values.

Treat this as:

- the view exists
- the filter is **not yet verified**

Do not tell the user the filter is active until the readback verification matches the intended filter.

### `VIEW_QUERY_CONDITION_READBACK_MISMATCH`

The view object was created or updated, but the readback config did not keep the intended frontend query-condition settings.

Treat this as:

- the view exists
- the query panel configuration is **not yet verified**

Do not tell the user the query condition is active until readback matches the intended `query_conditions`.

### `QUERY_CONDITION_FIELD_NOT_FOUND`

At least one `query_conditions.rows` field does not exist on the app.

### `INVALID_QUERY_CONDITION_FIELD`

The field exists but cannot be used in the frontend query-condition panel.

Supported `query_conditions.rows` fields are query-panel fields:

- text / long text
- number / amount
- date / datetime
- single select / multi select
- member / department
- phone / email
- boolean

Do not use these fields in `query_conditions`:

- relation
- attachment
- subtable or subtable subfield
- address/location
- Q-Linker
- code block

Fix path:

- If you wanted a saved filter that opens with the view, use `filters`.
- If you wanted a related report/view to match the current record, use `app_associated_resources_apply.match_mappings`.
- If you only need frontend search fields, remove unsupported fields from `query_conditions.rows` and keep query-panel supported fields only.

## Notes

- `fields` is accepted as an alias for `columns`, but skill examples should still use `columns`
- `column_names` should not appear in skill examples
- `app_get_views` should be treated as canonical readback and now returns `columns`
- If `app_views_apply` returns `AMBIGUOUS_VIEW`, stop and re-run `app_get_views`; then retry with the exact `view_key`
- `filters` are ANDed together as one flat condition group
- `query_conditions.rows` does not mean OR; it controls frontend query-field layout and should only contain query-panel supported fields
- `app_views_apply` publishes by default
- For select-style filters, success means the backend preserved the option value in readback, not just that the view name now exists
