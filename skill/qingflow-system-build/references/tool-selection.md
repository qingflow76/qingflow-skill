# Tool Selection

Use the smallest v2 builder tool chain that can finish the task.

## Default path

`summary read -> apply -> publish_verify`

Public builder `apply` tools already perform server-side planning, normalization, and dependency checks internally. Do not route normal public builder work through explicit `*_plan` tools.

## Hierarchy first

Before picking tools, decide which layer the request targets:

- `package`: a solution/app bundle like “研发项目管理” or “费控管理系统”
- `app`: one form/app inside that package
- `field`: one field inside one app
- `relation`: a field that links two apps

If the user asks for multiple forms/modules that relate to each other, this is a package-level multi-app task, not a single-app create.

Use this split consistently:

- Complete system/package: `package_apply` first, then use the `qingflow-app-form` Skill once per app and retain each returned `appKey`.
- Single app: `app_resolve/app_get` first, then app-scoped apply tools.
- Record/task/data operation: leave builder and use record/task skills.

Decision gate before writing:

| Evidence | Action |
| --- | --- |
| User gives an `app_key`, `view_key`, `chart_id`, `dash_key`, or exact `package_id` | Treat the task as an update to that existing target unless the user explicitly asks for a new one |
| User names several forms/modules or asks for a system/package | Use the complete-system path; do not compress them into one app |
| Same or very similar package/app already exists and the user did not say extend/replace/new | Stop and ask whether to extend existing, repair missing parts, or create a new target |
| Existing readback already contains part of the requested system | List verified existing resources, identify gaps, and patch only missing or incorrect slices |
| A write is uncertain: timeout, `partial_success`, `write_executed=true`, or `safe_to_retry=false` | Read back before retrying; do not create `V2`, `测试`, timestamp, or random-suffix resources |

## Resolve

- `package_get`: read one known package by `package_id`; it reads package `baseInfo` first and may warn `PACKAGE_DETAIL_READ_DEGRADED` when the richer detail endpoint needs package edit/add-app permission. Treat that warning as degraded detail, not as package-read failure.
- `package_apply`: create or update one package; `package_name` without `package_id` creates a package; layout/group/order changes require package edit permission because they call the backend package ordering route
- `member_search`: resolve named people from the directory
- `role_search`: resolve reusable roles from the directory
- `role_create`: create a reusable role when the business owner wants role-based routing
- `app_resolve`: locate an existing app by exactly one selector mode: `app_key`, or `app_name + package_id`; by-name resolution checks package detail/current visible apps before using broader admin-style app search, so a `/app/item` permission miss is not a frontend-visible-app failure

## Summary reads

- `app_get`: overall app config health, publish state, counts, and builder editability
- `app_get_fields`: field names, types, required flags, section ids
- `app_get_layout`: sections, rows, unplaced fields
- `app_get_views`: current view names, types, columns, group-by
- `app_get_flow`: workflow enabled state, nodes, transitions
- `app_get_charts`: current chart ids, names, types, order
- `chart_get`: one chart's base/config detail; base info is read through the Qingflow/qflow visible route first, and config may degrade from chart data when the CHART_SEE config endpoint is unavailable. Treat degraded config as a read-mode warning, not as proof the user cannot see the chart.
- `portal_get`: current portal config detail and component inventory

## Apply tools

App creation, form fields, form layout, form settings, and app deletion belong to the `qingflow-app-form` Skill. The old `app_schema_apply` and `app_layout_apply` MCP/CLI entries are removed. The remaining tools execute normalized non-form patches.

- `app_form_schema` / `app_form_get` / `app_form_apply` / `app_delete`: switch to the `qingflow-app-form` Skill and follow its complete, version-pinned declaration workflow
- `app_flow_apply`: replace workflow
- `app_views_apply`: use top-level `views[]`; `operation="upsert"` creates or fully targets a view, `operation="patch"` changes existing view parameters, and `operation="remove"` removes by key; declare view-specific business buttons in the same `views[]` item with `action_buttons`; new views default associated report/view display to visible with `limit_type="all"`
- `app_custom_buttons_apply`: advanced custom-button maintenance only: style/icon changes, cross-view reuse, deleting button bodies, bulk reordering bindings, or exact qRobot/wings configs. Use `patch_buttons` for existing-button parameter replacement; use `upsert_buttons` for creation or full target config; bind buttons to header/detail/list view positions; `placement=list` maps to the backend `INSIDE` row/list button position; merge-mode view configs require `buttons`; use `view_configs[].mode="replace"` or `buttons=[]` to clear a view's custom button bindings. For child-record creation linked to the current source record, map `source_field: "数据ID"` to the target relation field.
- `app_associated_resources_apply`: attach existing BI reports/views to the Qingflow app associated-resource pool and per-view display area; it does not create or edit QingBI report bodies/configs. Permission is split like the backend: resource pool writes use EditAppAuth, while `view_configs` uses the view config/DataManageAuth path. Use `patch_resources` for existing associated-resource parameter replacement; use `upsert_resources` for creation or full target config; `view_configs`, remove, and reorder may reference existing resources by internal `associated_item_id` or by `chart_id`/`chart_key`/`view_key`; use `match_mappings` with `target_field + operator + source_field/value` for associated view/report filters; publishes after successful writes; omit raw `sourceType`, and use `report_source="dataset"` only to attach an existing BI dataset report. Before `upsert_resources`, read `app_get.associated_resources` and reuse an existing matching `target_app_key + view_key/chart_key`; repeated upsert can create duplicates because `client_key` is only valid inside one apply call.
- `app_charts_apply`: create/edit/remove/reorder app-source QingBI report bodies/configs with `dataSourceType=qingflow`; it does not create/edit dataset BI reports and does not attach reports to Qingflow app associated-resource display. Use `app_get_fields.chart_fields` as the source for dimensions, metrics, and filters. Use semantic `metric`, `metrics`, `group_by`, and `where`: `target/indicator` for one KPI, `bar/columnar/pie` for distribution, `line/area` for trend, `table/detail/summary` for tabular summaries, and `dualaxes` for two-metric comparison. Do not use `summary` for a single metric card. Use `filters` with `field_name + operator + value/values`; the tool compiles them to QingBI string judge types. Use `patch_charts` for existing-chart parameter replacement; use `upsert_charts` for creation or full target config; avoid raw `indicator_field_ids`, `selectedMetrics`, and QingBI filter matrices on the main path; charts are immediate-live and do not publish; use `chart_id` when names are not unique; for complete systems, keep chart writes business-scoped, commonly 4-8 upserts by app or topic. Larger calls are accepted; if `CHART_UPSERT_BATCH_SIZE_RECOMMENDED` appears, read back before retrying and only repair failed items.
- `portal_apply`: create or replace-update portal pages; use `dash_key` for update mode or `package_id + dash_name` for create mode; create mode only prechecks package add_app, matching backend portal creation; edit mode may omit `sections` for base-info-only updates; when sections are supplied they still use replace semantics. Build portals only after referenced apps, raw `view_key`s, and chart ids/keys are known. PC layout uses 24 columns: components with the same `y` must have the same `rows`, same-row `cols` should sum to 24, metric cards use `rows=5`, BI charts use `rows=7`, data views use `rows=11`, and business-entry grids must include real `config.items[]`. Use business entry -> metrics -> BI charts -> concrete data views; do not use platform default views or raw `source_type: "filter"` as the main path.

For object-level updates, use the object's real selector field plus `set` and optional `unset`; `selector` is only a concept, not a literal key. Examples: `views: [{"operation": "patch", "app_key": "APP_KEY", "view_key": "VIEW_KEY", "set": {...}}]`, `patch_buttons: [{"button_id": 1001, "set": {...}}]`, `patch_resources: [{"associated_item_id": 123, "set": {...}}]`, `patch_charts: [{"chart_id": 456, "set": {...}}]`. The tool reads the current backend config, merges the patch, then submits the full backend payload internally. Do not send a partial `upsert_*` and expect missing required fields to be preserved.

## Explicit post-apply tools

- `app_publish_verify`: explicit final publish verification when the user asks for live confirmation

## Decision shortcuts

- Create one app inside an existing package:
  `package_get -> qingflow-app-form(app_form_schema -> app_form_apply)`
- Create a brand new package, then create one app in it:
  `package_apply(package_name, icon, color) -> qingflow-app-form(app_form_schema -> app_form_apply)`
- Create a brand new multi-app system/package:
  `package_apply(package_name, icon, color) -> qingflow-app-form` once per app; create relation-independent apps first, then use returned `appKey` values for relations
- Update fields on an existing app:
  `app_resolve -> qingflow-app-form(app_form_schema -> app_form_get(being_draft=true) -> app_form_apply)`
- Tidy layout:
  `qingflow-app-form(app_form_schema -> app_form_get(being_draft=true) -> app_form_apply)`
- Add workflow:
  `builder_tool_contract -> app_get_fields -> app_get_flow -> role_search/member_search -> app_flow_apply -> app_get_flow`
- Add views:
  `builder_tool_contract -> app_get_fields -> app_get_views -> app_views_apply(views[]) -> app_get_views`
- Maintain advanced custom buttons:
  `app_get -> app_custom_buttons_apply.patch_buttons/upsert_buttons + view_configs -> app_get_views`
- Add QingBI charts:
  `builder_tool_contract -> app_get_fields -> app_get_charts -> app_charts_apply.patch_charts/upsert_charts -> app_get_charts`
- Show an existing QingBI chart inside a Qingflow app/view:
  `app_get -> app_associated_resources_apply.upsert_resources/patch_resources + view_configs -> app_get`
- Create or update a portal:
  `builder_tool_contract -> portal_get -> portal_apply -> portal_get`
- Patch one portal section:
  `portal_get -> portal_apply.patch_sections[] -> portal_get`

## Avoid

- Do not handcraft raw Qingflow schema payloads
- Do not rely on internal `solution_*` tools in public builder flows
- Do not create a new package without first asking the user to confirm package creation
- Do not regress to `package_create` or `package_attach_app` as the public default story
- Do not treat a package/system name as `app_name` when the user clearly wants multiple apps inside it
- Do not compress multiple business objects into one app with several text fields
- Do not skip summary reads before flow or view work
- Do not emit `column_names`; always use `columns`
- Do not model form layout with retired `fields`, `field_ids`, top-level `columns`, or `title + rows` patch payloads; use the complete AppForm `body` from the pinned schema.
- Do not reuse internal flow keys such as `role_entries` or `editable_que_ids` in public builder calls
- Workflow writes use WorkflowSpec `spec` or `patch_nodes`
- Do not omit assignees on approval/fill/copy nodes
- For targeted workflow edits, read `app_get_flow` / `app_flow_get` and patch real WorkflowSpec node ids
- Do not guess role ids, member ids, or editable field ids; resolve names first
- Do not force agent-authored form declarations into backend-internal names: write AppForm fields with the pinned schema's camelCase keys. Relation targets should use confirmed app keys from readback; same-call `target_app_ref` / `target_app` are compatibility aliases only.
