# Single App Development Guide

Use this when the user asks for one app/form, or gives one `app_key`.
If the user asks for a package, system, or several related modules, use `complete-system-development-guide.md` instead.

## Recommended Completeness

Required:

- target package/app resolved by `package_get`, `app_resolve`, or `app_get`
- business fields and layout created or updated through the `qingflow-app-form` Skill
- exactly one readable top-level canonical `dataTitle: true`
- no platform system fields in AppForm `body`
- layout places the important fields
- at least one business view beyond platform default views when the task includes user-facing list work

Strongly recommended:

- saved filters and query panel fields for the main operating views
- core operating views declare needed business actions directly in `app_views_apply.views[].action_buttons`, when the view has real actions
- simple charts when the app has status, amount, date, or owner fields worth tracking

Optional:

- workflow, sample data, roles, or visibility changes when requested by the user or clearly needed by the app's job

Workflow preflight:

- If the app will have approval/fill/copy workflow nodes, add one explicit business status `single_select` field with `config.options` first, such as `状态`, `处理状态`, `审批状态`, `工单状态`, or `流程阶段`.
- Do not create platform workflow system fields: `当前流程状态`, `当前处理人`, `当前处理节点`, or `流程标题`.

## Standard Path

1. Read current target: `app_resolve` or `app_get`.
2. Read current fields: `app_get_fields`.
3. Switch to the `qingflow-app-form` Skill, pin `app_form_schema`, and read the draft with `app_form_get(being_draft=true)` for updates.
4. Apply one complete AppForm target with `app_form_apply`; preserve every existing field, section, row, and ID that should remain.
5. Apply workflow with the complete chain when the user asks for approval, fill, copy, reminders, or process routing: read flow schema/current flow, build a WorkflowSpec for full flow writes or `patch_nodes` for targeted edits, call `app_flow_apply`, then read back flow.
6. Apply views with `app_views_apply` when list/table/card/gantt behavior is part of the request; declare needed view actions in `action_buttons` while designing the view.
7. Apply charts only if they are part of the app's actual reporting need.
8. Use `app_publish_verify` only when explicit live verification is required.

## Field Rules

- Use canonical field types from the pinned AppForm Schema: `text`, `long_text`, `single_select`, `multi_select`, `number`, `amount`, `date`, `datetime`, `member`, `department`, `attachment`, `relation`, and other types returned by the schema.
- Historical aliases such as `multiline`, `select`, and `checkbox` are migration-only; do not use them as the current declaration template.
- Select fields must define `config.options` as the non-empty string array required by the current schema; later sample data should use those option labels.
- Relation fields are for real cross-object links. Read the exact canonical relation shape from the pinned AppForm Schema and use known target app keys.
- Do not impose a one-relation-field limit. Add the relation fields the business needs, then rely on backend validation and readback.
- Do not create `数据ID`, `编号`, `申请人`, `申请时间`, `创建人`, `创建时间`, `提交人`, `提交时间`, `更新时间`, `更新人`, `当前流程状态`, `当前处理人`, `当前处理节点`, or `流程标题`.
- Do not create built-in default views such as `全部数据` or `我的数据`; Qingflow provides system views.

## View Query Rules

- `filters` are fixed saved filters; `query_conditions` only configures frontend query-panel fields.
- Put only query-panel fields in `query_conditions.rows`: text, long text, number, amount, date/datetime, select, member, department, phone, email, or boolean.
- Do not put relation, attachment, subtable/subfield, address, Q-Linker, or code-block fields in `query_conditions`; use fixed `filters` or associated-resource `match_mappings` instead.

## Chart Rules

- Read `app_get_fields.chart_fields` before chart apply; normal form fields are not enough for QingBI dimensions, metrics, or filters.
- Use semantic chart input first: `metric`, `metrics`, `group_by`, and `where`.
- One KPI card uses `target` / `indicator` with `metric: "count(*)"` or `metric: "sum(金额)"`.
- Grouped distribution uses `bar` / `columnar` / `pie` with `group_by + metric`.
- Trend uses `line` / `area` / `columnar` with a date/month `group_by`.
- Do not use `summary` for a single KPI; `summary` is for table-style grouped summaries.
- Do not handwrite raw `indicator_field_ids`, `selectedMetrics`, or QingBI filter matrices on the main path.

## View Action Rules

- Use `action_buttons` inside `app_views_apply.views[]` for buttons tied to one view.
- Use `add_data` when a current record creates a downstream/child record; configure `target_app_key + field_mappings`, usually mapping `source_field: "数据ID"` to the target relation/reference field.
- Use `link` only for SOP, help, external system, or fixed URL navigation. Do not use it to fake approval, status transition, or data writeback.
- Prefer `detail` for current-record add-data actions, `list` for row actions, and `header` for global actions with no current-row context. Do not use current-record `field_mappings` on `header`.
- Approval, rejection, close-task, and status transition should be workflow/task behavior or existing automation; they are not generic custom-button types.

## Stop Conditions

- If the task actually needs multiple business objects, stop and switch to the complete-system guide.
- If an existing app with the same or very similar name appears and the user did not explicitly say update, extend, or create new, stop and ask which target to use.
- If readback shows the requested app already has some resources, patch the verified gaps instead of recreating the app.
- If a write returns `partial_success`, `write_executed=true`, or `safe_to_retry=false`, read back before retrying.
- If the same validation error repeats twice, re-read `builder_tool_contract` instead of guessing.
- Do not create `V2`, `测试`, timestamp, or random-suffix apps to bypass duplicate names in a real business package.
