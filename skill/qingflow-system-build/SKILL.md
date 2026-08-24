---
name: qingflow-system-build
description: Build, configure, and modify Qingflow apps and systems through the public configuration surface. Use when the user wants to apply or repair an existing SolutionSpec, modify an existing package with app, view, workflow, portal, navigation, or reporting tools, verify results, or troubleshoot system-building behavior through Qingflow CLI or the unified Qingflow MCP. Do not use this skill to install the MCP or to author a brand new SolutionSpec from scratch.
metadata:
  short-description: Build and modify Qingflow apps and systems
---

# Qingflow System Build

> **Skill 版本**：`qingflow-skills-2026.07.01.04`（入口文档版本；CLI 实际执行包以 `qingflow --json version` 返回的 `package / version / package_root / skill_version` 为准）。

This Skill defines system-building workflow semantics. It is a task route in the unified MCP, not a separate builder service. Use [$qingflow-common](../qingflow-common/SKILL.md) to select the CLI or unified Qingflow MCP invocation surface, then use only that surface's public operations.

## Overview

This skill is for the current **public builder surface**, not for legacy low-level builder writes.
In Wingent Momo runtime, trust the injected MCP session, credentials, workspace, and route context until a tool explicitly reports otherwise.

For app creation, form fields, form sections/layout, form settings, or app deletion, switch to the sibling [qingflow-app-form Skill](../qingflow-app-form/SKILL.md) and its versioned declarative operations. The legacy `app_schema_apply` and `app_layout_apply` MCP/CLI entries have been removed and must not be called.

Before any write or verification flow, identify whether the task targets `test` or `prod` and read [references/environments.md](references/environments.md). If the user did not specify one, default to `prod`.

Before choosing a route, skim the shared maintenance baseline: [public-surface-sync.md](references/public-surface-sync.md).
Then pick the matching development guide: [single-app-development-guide.md](references/single-app-development-guide.md) for one app, or [complete-system-development-guide.md](references/complete-system-development-guide.md) for app packages/systems.

## Current Public Mental Model

Model builder requests in four layers and keep them separate:

- `package`: the app bundle or solution container
- `app`: one form/app inside that package
- `field`: one field inside one app
- `relation`: a field that links one app to another app

Default modeling rules:

- One business object -> one app
- Attributes of that object -> fields inside that app
- Another business object -> a separate app, not a text field
- Cross-object links -> relation fields, not text fields

## Route First

Before any builder write, classify the request:

- **Complete system / app package**: the user asks for a system, package, workspace module set, or several related forms/apps. Use `package_apply` for the package, then the `qingflow-app-form` Skill once per app. Retain each returned `appKey`; create relation-independent forms first, then update complete forms with relations after every target key is known. Do not squeeze several business objects into one app.
- **Single app**: the user names one form/app or gives one `appKey`. Use `app_form_get(being_draft=true)` for edits, then validate and call `app_form_apply` through the `qingflow-app-form` Skill.
- **Record/user operation**: the user wants to add, edit, delete, approve, or analyze data. Route to the record/task skills instead of builder tools.

For complete systems, an AppForm declaration without `appKey` creates exactly one app and may create a duplicate if its response is lost. Record every returned `appKey` immediately. If a create result is unknown and no key was returned, stop instead of retrying or guessing by name. Once a key is known, recover through draft get plus a complete update declaration.

Before any write, apply this decision gate:

| Evidence | Action |
| --- | --- |
| Exact `app_key`, `view_key`, `chart_id`, `dash_key`, or `package_id` is provided | Update that existing target unless the user explicitly asks for a new one |
| Several forms/modules or a “system/package” are requested | Use the complete-system path; do not compress them into one app |
| Same/similar package or app already exists and user did not say extend/replace/new | Stop and ask which target strategy to use |
| Readback already contains part of the requested build | Patch only verified missing or incorrect slices |
| Write state is uncertain | Read back before retrying; do not create duplicate names with suffixes |

Builder schema inputs should follow agent-intuitive semantics:

- choose field type by business intent first: title/short text -> `text`; notes/description -> `long_text`; status/type/stage -> `single_select` with `config.options`; labels/multiple choices -> `multi_select`; quantities/ratios/scores/durations -> `number`; money -> `amount`; cross-app link -> `relation`
- field types in AppForm declarations may use the canonical types returned by the pinned AppForm Schema; readback returning a canonical type is not a schema mismatch
- primary icon syntax is `icon + color`, for example `icon: "table", color: "blue"`; `icon_name/icon_color`, `icon_config`, and `icon: {name, color}` are compatibility aliases only
- select-style fields use `config.options` as the string array required by the pinned AppForm Schema
- relation fields need a target plus object selectors: use a confirmed `config.targetAppKey` in AppForm declarations. Keep `config.displayField: {"name": "..."}` and `config.visibleFields: [{"name": "..."}]`; `target_app_ref` and snake_case selectors are legacy aliases only.
- do not impose an artificial one-relation-field-per-app limit; create the relation fields the business model needs, then rely on backend validation and readback
- do not create built-in system fields as form fields: `数据ID`, `编号`, `申请人`, `申请时间`, `创建人`, `创建时间`, `提交人`, `提交时间`, `更新时间`, `更新人`, `当前流程状态`, `当前处理人`, `当前处理节点`, `流程标题`. They are platform-generated; only reference supported system fields where a tool explicitly says so, such as button `source_field: "数据ID"`

## Public Tools You Should Think In

- Package: `package_get`, `package_apply`
- App reads: `app_resolve`, `app_get`, `app_get_fields`, `app_get_layout`, `app_get_views`, `app_get_flow`, `app_get_charts`
- Declarative app forms: `app_form_schema`, `app_form_get`, `app_form_apply`, `app_delete` through the `qingflow-app-form` Skill
- Builder reads: `portal_list`, `portal_get`, `view_get`, `chart_get`, `builder_tool_contract`
- Directory: `member_search`, `role_search`, `role_create`
- Writes outside AppForm: `app_flow_apply`, `app_views_apply`, `app_associated_resources_apply`, `app_charts_apply`, `portal_apply`, `app_release_edit_lock_if_mine`
- Maintenance-only writes: `app_custom_buttons_apply` only when the user explicitly asks to maintain existing standalone buttons outside view design.
- Verification: `app_publish_verify`
- Cross-cutting escalation: `feedback_submit` after explicit user confirmation when the public builder surface still cannot satisfy the user's need

Treat these as the official surface. Do not default to `package_create`, `package_attach_app`, raw `portal_*` writes, or raw `qingbi_report_*` writes.

## Current Public Defaults

- Package work:
  - use `package_get(package_id=...)` to read one known package
  - use `package_apply(...)` for package creation, rename, icon, visibility, grouping, ordering, and app/portal layout
- Multi-app form work:
  - use the `qingflow-app-form` Skill for each application and retain every returned `appKey`
  - create referenced applications first, then use their published AppForm schemas when declaring relations
  - if applications refer to each other, create complete valid forms without those relations first, then submit complete update declarations containing the relations
  - never retry a create whose response was lost before an `appKey` was obtained
- App base permissions:
  - trust `app_get.editability.can_edit_app_base` for app base-info writes like app name, icon, and visibility
  - `can_edit_form` only means schema/form-route capability; it no longer implies app base-info write capability
- Partial update rule:
  - for existing views, prefer `app_views_apply.views[]` with `operation="patch"`; for custom buttons, associated resources, and charts, prefer `patch_buttons` / `patch_resources` / `patch_charts`
  - each patch item uses the object's real selector field (`view_key` / `button_id` / `associated_item_id` / `chart_id`, or unique name where supported) plus `set` and optional `unset`; do not send a literal `selector` key for these tools
  - use `upsert_*` for creation or full target configuration; do not send a partial `upsert_*` and expect the backend to merge missing required fields
- Portal work:
  - `portal_apply` is the public write path
  - in edit mode, omitting `sections` means “preserve existing layout and update base info only”
  - supplying `sections` means full replace semantics for sections
  - `patch_sections[]` is the preferred path for changing one existing portal block
  - do not confuse form layout with portal layout: form layout uses field-name `rows`; portal layout uses component `position.pc.x/y/cols/rows`
  - portal PC layout uses a 24-column grid; components with the same `y` must share the same `rows`, and their `cols` should sum to 24 unless the user explicitly wants blank space
  - standard workbench heights: metric cards `rows=5`, BI charts `rows=7`, data views `rows=11`
  - business-entry grid sections must include real `config.items[]`; do not submit an empty grid container
  - build portals only after referenced apps, raw `view_key`s, and chart ids/keys are known by readback
  - standard order is business entry -> metric cards -> BI charts -> concrete data views
  - do not use platform default views such as `全部数据` / `我的数据` as the main portal views
  - do not use `source_type: "filter"` as the normal automation path; portal filter is raw/unstable and not part of the unified filter DSL
- Chart work:
  - `app_charts_apply` is the public write path for app-source QingBI report bodies/configs; it creates/updates reports with `dataSourceType=qingflow`
  - dataset BI reports are not created or edited by `app_charts_apply` yet; create them in QingBI first, then attach the existing report with `app_associated_resources_apply` and `report_source="dataset"`
  - it does not attach the report to the Qingflow app associated-resource display; use `app_associated_resources_apply` for that
  - use `app_get_fields.chart_fields` as the source for dimensions, metrics, and filters; normal record/form fields are not enough
  - choose chart type by goal: `target/indicator` for one KPI, `bar/columnar/pie` for distribution, `line/area` for trend, `table/detail/summary` for tabular summaries, `dualaxes` for two-metric comparison
  - use semantic metrics: `count(*)`, `sum(金额)`, `avg(工时)`, `group_by`, `where`; do not handwrite raw `indicator_field_ids`, `selectedMetrics`, or QingBI filter matrices on the main path
  - do not use `summary` for a single metric card; use `target` / `indicator`
  - supported `chart_type` values include legacy public aliases `target`, `table` and QingBI types such as `summary`, `columnar`, `area`, `stacked_area`, `funnel`, `waterfall`, `gauge`, `heatmap`, `histogram`, `treemap`, `radar`, `stacked_bar`, `stacked_column`, `scatter`, `ring`, `rose`, `dualaxes`, `map`, and `timeline`
  - chart `filters` use the unified fixed-filter DSL: `field_name + operator + value/values`; the tool compiles them to QingBI string judge types
  - for complete systems, keep chart payloads business-scoped, commonly 4-8 `upsert_charts` by app or topic. Larger calls are accepted; if `CHART_UPSERT_BATCH_SIZE_RECOMMENDED` appears, read back before retrying and only repair failed items.
  - use `patch_charts` for changing a chart name, visibility, filters, or one config fragment on an existing chart
  - `visibility` is a public capability and should be treated as a base-only permission update
  - do not model chart visibility changes as raw config rewrites
- View action work:
  - for view-specific business buttons, use `app_views_apply.views[].action_buttons`; for existing views use `operation="patch"` with `set.action_buttons`
  - choose by user intent first: current record -> downstream record uses `add_data`; global independent entry uses `header`; URL/SOP/help uses `link`; approval/status transition/close task is workflow/task/automation, not a fake button
  - use `field_mappings` for dynamic current-record values, including system fields such as `数据ID` (`field_id=-17`) and `编号` (`field_id=0`)
  - to prefill a target relation field with the current source record, map `{"source_field": "数据ID", "target_field": "目标引用字段"}`; use `default_values` only for static constants
  - placement choice: `header` is global and has no current-row context; `list` is row/list action and maps to backend `INSIDE`; `detail` is the safest current-record context action. Do not use current-record `field_mappings` on `header`
  - if field type compatibility is unclear, read [references/match-rules.md](references/match-rules.md)
  - `app_custom_buttons_apply` is not a main build path; use it only after an explicit maintenance request for existing standalone buttons, cross-view binding, deletion, or exact advanced automation config
- Associated resources:
  - `app_associated_resources_apply` is the public write path for the Qingflow app-level associated report/view pool and per-view display config
  - it attaches existing BI reports/views for in-app display; it does not create or edit QingBI report bodies/configs, including dataset reports
  - use `patch_resources` for changing match rules or other existing associated-resource parameters; the tool preserves backend-required raw fields internally
  - `associated_item_id` is the backend internal associated-resource id; for `view_configs`, `remove_associated_item_ids`, and `reorder_associated_item_ids`, you may pass `associated_item_id` or an existing resource's `chart_id`/`chart_key`/`view_key`, and the tool resolves it to the internal id
  - before creating a resource, check `app_get.associated_resources` for the same `target_app_key + view_key/chart_key`; if it already exists, use `patch_resources` with that `associated_item_id`
  - `client_key` is only a same-call reference for `view_configs[].associated_item_refs`; it is not saved and cannot deduplicate later calls
  - do not pass backend raw `sourceType`; view resources infer the internal Qingflow view source, report/chart resources default to BI app reports, and existing dataset reports use `report_source="dataset"`
  - use `match_mappings` for associated view/report filters; dynamic context matches use `source_field`, static filters use `value`; do not handwrite raw `matchRules`
  - if field type compatibility is unclear, read [references/match-rules.md](references/match-rules.md)
- Views and flows:
  - stay on `app_views_apply` / `app_flow_apply`
  - before building approval/fill/copy flows, make sure the app schema has an explicit business status `single_select` field with `config.options`, such as `状态` / `处理状态` / `审批状态`; do not create platform workflow system fields such as `当前流程状态`
  - use `views[]` with `operation="patch"` for existing-view parameter changes such as `query_conditions`, `filters`, `columns`, or visibility
  - builder view writes use raw `view_key` values from `app_get.views`; `custom:<viewKey>` is a record-data `view_id` form, not a builder `view_key`
  - do not create platform default/system views named `全部数据`, `我的数据`, `我发起的`, `待办`, `已办`, or `抄送`; they are built in. New views must use business-specific names. To change a built-in view, patch by its existing raw `view_key`
  - use `builder_tool_contract` whenever the minimal legal shape is unclear
  - keep view `filters` and `query_conditions` separate: `filters` use `field_name + operator + value/values` and are fixed saved filters; `query_conditions` configure the frontend query panel fields and only take effect after users enter query values
  - choose condition/matching surface by intent: fixed saved filters -> `filters`; frontend query panel -> `query_conditions.rows`; current-record associated report/view filtering -> `match_mappings`; current-record add-data prefill -> `field_mappings`; button visibility -> `visible_when` / `button_limit`
  - keep relation/attachment/subtable/address/Q-Linker/code-block fields out of `query_conditions`; member/department fields may be used as query-panel fields when readback supports them. Use `filters` for fixed filters or associated-resource `match_mappings` for current-record related report/view matching
  - new views default the associated report/view display area to visible with `limit_type="all"`; existing views preserve their current associated-resource display unless `associated_resources` is explicitly patched
  - configure associated reports/views through `app_associated_resources_apply`, not through `app_views_apply`

## Standard Operating Order

1. Trust the current MCP/session when it is already injected by the runtime; only run auth/workspace recovery after a tool explicitly reports an auth, credential, or workspace error
2. Confirm whether the task is read-only or write-impacting
3. Classify the build scope:
   - complete system/package -> `package_apply` or `package_get`, then use `qingflow-app-form` once per app and retain every returned `appKey`
   - single app form -> switch to `qingflow-app-form`; read the draft for editing, validate, then apply the complete target
   - record/task/data request -> leave builder and use the matching record/task skill
4. Resolve the smallest stable target:
   - app-scoped work -> `app_resolve`
   - package-scoped work with known id -> `package_get`
   - portal inventory -> `portal_list`
5. Read only the smallest config slice needed:
   - app map -> `app_get` (default entry; includes compact views, charts, custom buttons, and associated resource pool)
   - fields -> `app_get_fields`
   - layout -> `app_get_layout`
   - views -> `app_get_views` only when the app_get compact list is not enough
   - flow -> `app_get_flow` only when the task involves approval, fill/copy, reminders, process routing, task handling, or flow repair
   - charts -> `app_get_charts` only when the app_get compact list is not enough
   - portal -> `portal_get`
6. If the public shape is unclear, call `builder_tool_contract`
7. Apply the smallest patch tool that fits:
   - form fields/layout/settings -> switch to the `qingflow-app-form` Skill and submit a complete versioned AppForm declaration
   - flow -> `app_flow_apply` only when workflow is requested or clearly required
   - views -> `app_views_apply(views=[...])`; use `operation="upsert"` for new/full views and `operation="patch"` for existing-view parameter changes
   - view-specific business buttons -> put `action_buttons` on the same `views[]` item; use `set.action_buttons` for patch
   - standalone button maintenance explicitly requested by the user -> `app_custom_buttons_apply`
   - existing associated resources -> `app_associated_resources_apply.patch_resources`; new/full resources -> `app_associated_resources_apply.upsert_resources`
   - existing charts -> `app_charts_apply.patch_charts`; new/full charts -> `app_charts_apply.upsert_charts`
   - portal -> `portal_apply`
   - package metadata/layout -> `package_apply`
8. Use `app_publish_verify` only when the user explicitly wants final publish/live verification or you need a dedicated verification pass
9. For complete-system builds, write `tmp/qingflow_system_build_summary.json` before the final response and make the final report match that file

## Safe Usage Rules

- Do not guess package identity from a loose name. Public package work assumes a known `package_id`, or an explicit create/update intent through `package_apply`.
- Do not perform routine auth probes before every builder action in runtime contexts with injected MCP credentials; recover auth only after an actual auth/workspace failure.
- If `package_id` is unknown, derive it from related app/portal readback when possible; otherwise ask the user instead of falling back to hidden package lookup tools.
- Do not bypass package/app-name conflicts by inventing `V2`, `测试`, timestamp, or random suffix apps in a real business package. Read back and decide whether to update the existing app, create only a truly missing app, or ask the user.
- After any uncertain AppForm update, read the latest draft and published forms before deciding whether to repair or publish only. Never replay a stale backend payload or edit version.
- Do not use `package_create` or `package_attach_app` as a public default path. If they still appear in low-level code, treat them as internal/legacy implementation details.
- Do not use raw `portal_*` writes or raw `qingbi_report_*` writes as the default builder strategy.
- `app_form_apply` publishes when its draft changes or the published form lags behind; `app_flow_apply` and `app_views_apply` publish by default; `app_custom_buttons_apply` and `app_associated_resources_apply` publish after at least one write succeeds and do not accept a draft-only `publish` parameter; `app_charts_apply` is immediate-live without publish.
- In AppForm declarations, exactly one readable top-level field must use `dataTitle: true`; `dataCover: true` is optional and only valid on one top-level `attachment` field.
- Do not add platform system fields to an AppForm `body`; if the user asks for record id, number, applicant, creation/update time, or workflow status, use the built-in data/list/readback fields instead of creating duplicate controls.
- If the same validation error repeats twice, stop guessing and re-read `builder_tool_contract`.
- Do not create workflows just to make a build look complete. If no approval/fill/copy/reminder/process-routing requirement exists, report workflow as not requested/not configured.
- For workflow assignees, prefer `role_search` over explicit members unless the user explicitly wants named members.
- Workflow work uses `app_flow_get_schema` / `app_get_flow` readback plus `app_flow_apply(spec=...)` for full WorkflowSpec writes, or `patch_nodes` for targeted existing-node edits.
- Respect collaborative edit locks. Only use `app_release_edit_lock_if_mine` when the lock owner is the current authenticated user.
- If the supported builder surface is still awkward or blocked after reasonable use, summarize the gap, ask whether to submit feedback, and call `feedback_submit` only after explicit user confirmation.

## Response Interpretation

- All builder apply/write tools return a standard UI envelope in addition to legacy fields:
  `schema_version`, `operation`, `summary`, and `resources[]`.
- For UI cards or quick narration, read `resources[]` first. Each resource has `resource_type`, `operation`, `status`, `id`, `key`, `name`, typed `ids`, and `parent`.
- Use legacy fields such as `field_diff`, `views_diff`, `chart_results`, `created/updated/removed`, and `verification` only for compatibility and troubleshooting.
- Treat post-write readback as the source of truth, not just write status codes.
- `success` means write and verification completed; `partial_success` means the write landed or may have landed but verification is incomplete. If `write_executed=true`, `safe_to_retry=false`, or readback is unavailable, do `readback_before_retry` before any create retry.
- Final status rule:
  - write result answers whether the write was attempted
  - readback answers what actually exists
  - publish/portal verification answers whether it is front-end visible
  - validation/contract error with `write_executed=false` is a real failure and can be fixed/retried
  - `partial_success`, timeout, post-write 40002/404, or readback unavailable is not enough to call the write failed; read back first and patch only proven gaps
- For portals, distinguish clearly between:
  - base-info-only update with layout preserved
  - full sections replace
  - patching one section with `patch_sections[]`
  - layout validity: same-row `rows`, same-row `cols` sum, and non-empty grid `items`
- For object apply tools, distinguish clearly between:
  - `patch_*`: public partial parameter replacement; the tool hydrates current config and full-saves internally
  - `upsert_*`: create or full target configuration; omitted fields may mean default/clear depending on that object
- For charts, distinguish clearly between:
  - base / visibility change
  - real chart-config change
- For app permissions, report `can_edit_app_base` separately from `can_edit_form / can_edit_flow / can_edit_views / can_edit_charts`.

## Practical Patterns

- Read one package: `package_get`
- Create or update one package: `package_apply`
- Resolve one app: `app_resolve`
- Read one app map: `app_get`
- Read fields only: `app_get_fields`
- Read layout summary: `app_get_layout`
- Read views summary: `app_get_views`
- Read flow summary: `app_get_flow`
- Read chart summary: `app_get_charts`
- Read portal config: `portal_get`
- Search members or roles: `member_search`, `role_search`
- Create reusable role: `role_create`
- Create/update app forms and layout: use the `qingflow-app-form` Skill
- Replace workflow: `app_flow_apply`
- Upsert/patch/remove views, including view-specific `action_buttons`: `app_views_apply(views=[...])`
- Advanced standalone button maintenance only when explicitly requested: `app_custom_buttons_apply`
- Upsert/patch/remove app associated reports/views and per-view display: `app_associated_resources_apply`
- Upsert/patch/remove/reorder charts: `app_charts_apply`
- Create or update portal pages: `portal_apply`
- Release your own stale edit lock: `app_release_edit_lock_if_mine`
- Final publish verification: `app_publish_verify`

## Standalone Button Boundary

For ordinary business builds, do not start from `app_custom_buttons_apply`. Put buttons in the view with `action_buttons`; see [references/update-views.md](references/update-views.md).

## Resources

- Shared public-surface baseline: [public-surface-sync.md](references/public-surface-sync.md)
- Environment switching: [references/environments.md](references/environments.md)
- Tool choice and sequencing: [references/tool-selection.md](references/tool-selection.md)
- Field matching rules: [references/match-rules.md](references/match-rules.md)
- Result semantics and gotchas: [references/gotchas.md](references/gotchas.md)
- Single app development guide: [references/single-app-development-guide.md](references/single-app-development-guide.md)
- Complete system development guide: [references/complete-system-development-guide.md](references/complete-system-development-guide.md)
- Declarative app creation, fields, layout, settings, and deletion: [qingflow-app-form Skill](../qingflow-app-form/SKILL.md)
- Legacy app creation compatibility notes: [references/create-app.md](references/create-app.md)
- Retired schema/layout implementation notes are not public usage guides; use `qingflow-app-form` for all form work
- Update workflow only: [references/update-flow.md](references/update-flow.md)
- Workflow assignees and node permissions: [references/flow-actors-and-permissions.md](references/flow-actors-and-permissions.md)
- Update views only: [references/update-views.md](references/update-views.md)
- Standard end-to-end builder sequences: [references/solution-playbooks.md](references/solution-playbooks.md)
