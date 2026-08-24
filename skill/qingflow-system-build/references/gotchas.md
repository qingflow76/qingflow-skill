# Builder Gotchas

## Auth and workspace

- `auth_*` success does not mean a workspace is selected
- In Wingent Momo runtime, do not run `workspace_select` before builder work. Re-run it only after an explicit auth/route recovery or when a business tool reports the workspace is missing.

## Package ownership

- Public package work should stay on `package_get / package_apply`
- Do not treat `package_attach_app` as the public default story anymore; if it still exists in low-level code, treat it as internal/legacy
- Check package-related readback after schema writes instead of assuming package ownership from the write alone

## Package vs app vs field

- A package/system is not an app
- Another app is not a field
- If the user names multiple forms/modules that relate to each other, create multiple apps and connect them with relation fields
- Do not use child app names like “项目/需求/任务/缺陷/团队” as plain text fields inside one app
- For a complete system, create the package first, then use the `qingflow-app-form` Skill once per app; retain returned `appKey` values and create relation-independent apps before relation apps
- Use `target_app_key` only for an app that already exists or has been confirmed by readback

## Auto publish

- `app_form_apply` publishes when draft changes or published form lags; `app_flow_apply` and `app_views_apply` publish by default
- For those four tools, pass `publish=false` only when the user explicitly wants to leave changes in draft
- `app_custom_buttons_apply` and `app_associated_resources_apply` publish after at least one write succeeds and do not accept `publish=false`
- `app_publish_verify` is for explicit final verification, not the default next step after every write

## BI Reports

- Use `app_charts_apply` for QingBI report body/config creation or updates.
- Use `app_associated_resources_apply` only when an existing BI report or view needs to appear in the Qingflow app associated-resource area or a specific view.
- `app_charts_apply` currently creates/updates app-source BI reports only (`dataSourceType=qingflow`); dataset BI reports can only be attached when they already exist.
- Creating a chart with `app_charts_apply` does not automatically show it in the Qingflow app UI; attach it separately if display is required.
- Main chart config should use semantic `metric`, `metrics`, `group_by`, and `where`; avoid raw `indicator_field_ids`, `selectedMetrics`, and QingBI filter matrices unless diagnosing or preserving existing raw config.
- `target` and `table` remain compatibility aliases for QingBI `indicator` and `detail`; use the real QingBI chart type when you need a specific type such as `summary`, `columnar`, `stacked_bar`, `scatter`, or `dualaxes`.
- Use `app_get_fields.chart_fields` as the source for dimensions, metrics, and filters. Record schema fields or normal form fields are not enough for chart apply.
- Use `target` / `indicator` for one metric card; do not use `summary` for a single KPI.

## Custom buttons

- For ordinary view-specific business buttons, use `app_views_apply` with `action_buttons`; do not use legacy `app_views_apply.buttons` unless you are maintaining an old full-replacement patch.
- Use `app_custom_buttons_apply` for advanced button creation/update/removal and view placement: custom style/icon, cross-view reuse, deleting button bodies, bulk binding reorder, or exact qRobot/wings configs.
- When changing one existing button parameter, use `patch_buttons` with `set/unset`. Do not send a partial `upsert_buttons` object and expect the backend to preserve hidden required fields.
- `addData` / `add_data` creates a related/downstream Qingflow record; use current-record `field_mappings` only on `detail` or `list`. `link` only opens a URL. `qRobot`/`wings` require user-provided exact config and must not be invented.
- For add-data buttons, prefer semantic `trigger_add_data_config.target_app_key`, `field_mappings`, and `default_values`.
- Do not handwrite raw `que_relation` unless you are preserving an existing backend config. If `field_mappings` and `que_relation` are mixed, the tool blocks the write.
- `field_mappings.source_field` can use source app fields and supported system fields such as `数据ID` (`field_id=-17`) and `编号` (`field_id=0`).
- To fill a target relation field with the current source record, map `{"source_field": "数据ID", "target_field": "目标引用字段"}`. Use `default_values` only for static constants.
- Do not put current-record `field_mappings` on a `header` button; `header` has no current row. Use `detail` or `list` for current-record add-data actions.
- Do not model approval, rejection, close-task, or status transition as a generic `link` button. Use workflow/task behavior, or `qRobot`/`wings` only when the user provides existing automation config.
- For field type compatibility, read `references/match-rules.md`.
- Use `header` for global actions with no current-row context, `detail` for safest current-record actions, and `list` for row/list actions.
- `view_configs[].buttons` is required in merge mode. Do not send a view config with only `view_key`; it is blocked to avoid no-op writes and accidental publish.
- Builder view configs use raw `view_key` from `app_get.views[].view_key`; do not prefix it with `custom:`. The `custom:<viewKey>` form is for record-data `view_id`.
- View button bindings merge by default. Use `view_configs[].mode="replace"` to replace the full set, or pass an explicit empty `buttons: []` when you intend to clear all custom button bindings for that view.
- Advanced view button bindings can include `button_limit`, `button_formula`, `button_formula_type`, and `print_tpls`, but keep ordinary buttons simple unless the user asks for conditional visibility or print templates.
- `placement=list` configures row/list buttons. The tool maps it to the backend `INSIDE` button position, not a raw `LIST` config type.

## Associated resources

- Before creating an associated view/report, check `app_get.associated_resources` for the same `target_app_key + view_key/chart_key`.
- If the resource already exists, use `patch_resources` with its `associated_item_id`; do not call `upsert_resources` again.
- For per-view display, remove, and reorder, existing associated reports/views may be referenced by `associated_item_id`, `chart_id`/`chart_key`, or `view_key`; the tool resolves these to the internal id before writing.
- `client_key` is only a same-call alias for `view_configs[].associated_item_refs`. It is not stored by Qingflow and cannot prevent duplicates in later calls.
- Repeated `upsert_resources` without `associated_item_id` can create multiple app-level associated items pointing to the same view/report.

## Readback scope

- Prefer summary reads over large raw payloads
- Use `app_get_fields` before schema or view work
- Use `app_get_layout` before layout work
- Use `app_get_flow` before workflow work
- Use `app_get_views` before view work

## Partial update discipline

- Existing views use `app_views_apply.views[]` with `operation="patch"` plus `set` and optional `unset`; custom buttons, associated resources, and charts use their `patch_*[].set` plus optional `patch_*[].unset`.
- The backend may still save a full payload. The MCP/CLI patch path is responsible for reading current config and preserving fields the user did not mention.
- Do not use view `operation="upsert"`, `upsert_buttons`, `upsert_resources`, or `upsert_charts` for a tiny parameter replacement unless you are deliberately providing the full desired target config.
- AppForm `body` is complete target state. Preserve every field, section, row, subfield, and ID that should remain.
- `portal_apply` without `sections` is base-info-only. Supplying `sections` replaces the portal sections list; use `patch_sections[]` for one-section updates.
- PC portal layout is 24-column. Group components by the same `y`: all components in that row must have the same `rows`, and their `cols` should sum to 24 unless the user explicitly wants blank space.
- Standard workbench heights: metric cards `rows=5`, BI charts `rows=7`, data views `rows=11`.
- Business-entry `grid` sections must include real `config.items[]`; an empty grid container is not a valid business entrance.
- Build portals only after referenced apps, raw `view_key`s, and chart ids/keys are known by readback. Intended names are not enough.
- Use standard order: business entry -> metric cards -> BI charts -> concrete data views.
- Do not use platform default views such as `全部数据` / `我的数据` as the main portal views.
- Do not use portal `source_type: "filter"` as the normal automation path; it is raw/unstable and not part of the unified filter DSL.
- `app_flow_apply` writes complete WorkflowSpec via `spec` or targeted existing-node edits via `patch_nodes`.

## Workflow dependencies

- Approval-style flows usually require an explicit status field
- Approval, fill, and copy nodes also require at least one assignee
- Prefer roles over explicit members unless the user explicitly names people
- Resolve assignees with `role_search` / `member_search` before flow apply
- Use the field permission shape from `app_flow_get_schema` / current WorkflowSpec readback; do not guess field ids or permission keys
- For targeted edits, patch real node ids from `app_get_flow` / `app_flow_get`; do not use remembered node ids.
- If `app_flow_apply` reports `FLOW_DEPENDENCY_MISSING`, fix schema first
- Do not switch to hidden `solution_*` tools from public builder flows

## Retry discipline

- If a write returns `partial_success`, read back before retrying
- If an AppForm apply times out, returns `write_executed=true`, returns `safe_to_retry=false`, or has incomplete readback, treat it as `write_may_have_succeeded`; read the latest draft and published forms before recovery.
- AppForm recovery means classify which fields, sections, rows, settings, and relation bindings actually exist, then retry only a complete declaration for the verified target; never replay a lost create.
- Do not repeat create steps after `app_key` already exists
- Do not split a complete-system schema create into single-app rebuilds until readback proves exactly what is missing
- Do not bypass duplicate/conflict states by inventing `V2`, `测试`, timestamp, or random-suffix app names in a real business package
- For backend rejects, keep the retry narrow: retry only the failed tool, not the whole chain
- For `VALIDATION_ERROR`, do not keep guessing. Reuse `suggested_next_call`, `canonical_arguments`, `allowed_keys`, and `allowed_values` first.
- For `builder_tool_contract`, read the returned `json_paths` first. Successful contract data is under `$.contract`; `allowed_values` uses flat dotted keys such as `["field.type"]`, not nested objects. Do not read successful field enums from top-level `allowed_values`.
- For `workspace_icon_catalog_get`, read icon candidates from `$.icon_names` and colors from `$.icon_colors`.
- For builder apply responses, read returned `json_paths` first. Stable fields are `$.summary` and `$.resources[]`; use `resources[].id/key/name` before legacy top-level fields.
- For AppForm validation failures, fix every reported JSON pointer and rerun local declaration validation before apply; do not query a retired builder contract.
- For flow work, do not replay internal keys from old logs or plan outputs. Public builder calls should stay on WorkflowSpec `spec` or `patch_nodes` read from `app_get_flow` / `app_flow_get`.
- For view work, treat `columns` as the only canonical public key. `app_get_views` and `app_views_apply` should all be read and written in that shape.
- For existing view parameter changes, prefer `views[]` with `operation="patch"`. Example: to change only query-panel fields, set only `query_conditions`; the tool will preserve columns, filters, date config, card fields, buttons, and other backend-required fields.
- For form layout work, treat the pinned AppForm Schema's `body`/section/row shape as canonical. `title + rows`, `fields`, `field_ids`, and `columns` from retired layout adapters are not public write shapes.
- A created view is not enough to claim a filter succeeded. When `app_views_apply` returns `partial_success`, `views_verified=false`, or `details.filter_mismatches`, treat the view as present but the filter as unverified.
- If duplicate view names exist, do not retry by name. Read the exact `view_key` and target that one.
- If a view or flow write fails, report the smallest next action:
  - wrong key -> switch to canonical key
  - missing/invalid WorkflowSpec shape -> reread `app_flow_get_schema` and current flow
  - backend reject -> re-read summary and retry only the failed patch
- Do not translate abstract user phrases like “灵活流程” or “默认视图” directly into MCP arguments. First convert them to an explicit WorkflowSpec or targeted patch plan.
