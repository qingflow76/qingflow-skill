# Complete System Development Guide

Use this when the user asks for a system, app package, workspace module set, or several related apps/forms.
Do not compress several business objects into one app.

## Recommended Completeness

Required:

- package exists or is created through `package_apply`
- core business objects are modeled as separate apps
- all new apps are created through one complete, version-pinned AppForm declaration per app
- every non-empty app has explicit `appName` and an app-level `dataTitleField` selector that resolves to one top-level field; AppForm derives its default icon and color from the app name
- no app creates platform system fields such as `数据ID`, `编号`, `申请人`, `申请时间`, `创建人`, `创建时间`, `提交人`, `提交时间`, `更新时间`, `更新人`, `当前流程状态`, `当前处理人`, `当前处理节点`, or `流程标题`
- relation-independent apps are created first; relation apps use confirmed target `appKey` values and the pinned canonical relation shape
- basic operating views exist for each core app
- package/apps/AppForms/relations are read back before repair or retry

Strongly recommended:

- cross-app relation fields for the main business links, using confirmed target `appKey` values
- core operating views declare needed business actions directly in `app_views_apply.views[].action_buttons`
- portal chart sections declare needed QingBI charts inline through `sections[].chart`
- a standard portal: business entry area, core metrics, BI charts, then concrete data views
- portal grid/business-entry sections contain real `config.items[]`, not empty containers

Workflow preflight:

- If an app will have approval/fill/copy workflow nodes, create an explicit business status `single_select` field with `config.options` first, such as `状态`, `处理状态`, `审批状态`, `工单状态`, or `流程阶段`.
- Do not create platform workflow system fields such as `当前流程状态`, `当前处理人`, `当前处理节点`, or `流程标题`.
- If `app_flow_apply` returns `FLOW_DEPENDENCY_MISSING`, fix schema with the returned `suggested_next_call`, read fields back, then retry the flow. Do not skip the workflow silently.

Optional:

- workflow, reminders, view-declared action buttons, associated resources, sample data, roles, and permissions when the user asks for them or the business process clearly depends on them

## Standard Path

1. Resolve or create package: `package_get` / `package_apply`.
2. Pin the AppForm Schema version and draft one complete declaration per app.
3. Create relation-independent apps first and retain every returned `appKey`; then declare relation apps or update relations with confirmed target keys.
4. Follow the AppForm Skill recovery rules for uncertain results; never blindly repeat a create.
5. Treat AppForm `body` as complete target state, including fields, sections, rows, and layout.
6. Apply workflow with the complete chain when the user asks for approval, fill, copy, reminders, or process routing: read flow schema/current flow, build a WorkflowSpec for full flow writes or `patch_nodes` for targeted edits, call `app_flow_apply`, then read back flow.
7. Apply views; put view-specific business actions in `action_buttons` while designing the core operating views.
8. Create the portal after referenced apps and views are known; create or reuse QingBI charts inline in portal sections with `chart`.
9. Before the final response, write the complete-system delivery summary file described below.

## Field Modeling Rules

- Use canonical field types returned by the pinned AppForm Schema: `text`, `long_text`, `single_select`, `multi_select`, `number`, `amount`, `date`, `datetime`, `member`, `department`, `attachment`, `relation`, and the other supported schema types.
- Historical aliases such as `multiline` and `select` may appear in old drafts; migrate them to the current canonical type instead of using them as the main template.
- Create only business fields. Do not create platform system fields listed in Required; reference them only where a tool explicitly supports system fields, such as button `source_field: "数据ID"`.
- Use `number` for ratios, completion rates, scores, percentages, durations, and quantities that may need decimals. Use `amount` only for currency/money semantics. This prevents sample data from producing decimal values for a field that the backend treats as integer money.
- For select fields, define the option set during schema design. Later sample data must use only those option labels or ids.
- Relation fields must follow the pinned AppForm Schema and use known target app keys; do not infer a legacy patch shape.
- Do not impose a one-relation-field-per-app limit. Model the real business links and let backend validation/readback decide whether a specific relation is unsupported.

## View Query Rules

- Use `filters` for fixed saved filters that apply when the view opens.
- Use `query_conditions` only for the frontend query panel layout. It is not another filter DSL and it does not express OR.
- `query_conditions.rows` should contain query-panel fields such as text, long text, number, amount, date/datetime, select, member, department, phone, email, or boolean.
- Do not put relation, attachment, subtable/subfield, address, Q-Linker, or code-block fields in `query_conditions`.
- For current-record related views/reports, use `app_associated_resources_apply.match_mappings`, not `query_conditions`.

## Portal Chart Rules

- For complete systems, do not make chart creation a separate main step. When the portal needs metrics or BI blocks, declare them in `portal_apply.sections[].chart`.
- Read `app_get_fields.chart_fields` before writing portal chart sections; normal form fields are not enough for QingBI dimensions, metrics, or filters.
- Use semantic chart input first: `metric`, `metrics`, `group_by`, and `where`.
- One KPI card uses `target` / `indicator` with `metric: "count(*)"` or `metric: "sum(金额)"`.
- Grouped distribution uses `bar` / `columnar` / `pie` with `group_by + metric`.
- Trend uses `line` / `area` / `columnar` with a date/month `group_by`.
- Two-metric comparison uses `dualaxes` with `left_metric` and `right_metric`.
- Do not use `summary` for a single KPI; `summary` is for table-style grouped summaries.
- Do not handwrite raw `indicator_field_ids`, `selectedMetrics`, or QingBI filter matrices on the main path.
- Keep portal chart definitions business-scoped, commonly 4-8 charts by app or topic. Larger calls are accepted but should be read back before retrying.

## View Action Rules

- Design business buttons only with the view: `app_views_apply.views[].action_buttons`; for existing views use `operation="patch"` with `set.action_buttons`.
- Use `add_data` when a current record creates a downstream/child record, such as order -> acceptance, work order -> inspection, or customer -> follow-up. Configure `target_app_key + field_mappings`; map `source_field: "数据ID"` to the target relation/reference field when linking back to the source record.
- Use `link` only for SOP, help, external system, or fixed URL navigation. Do not use `link` to fake approval, status transition, or data writeback.
- Prefer `detail` for current-record add-data actions, `list` for row actions, and `header` for global actions with no current-row context. Do not use current-record `field_mappings` on `header`.
- Approval, rejection, close-task, and status transition should be modeled as workflow/task behavior or existing automation; they are not generic custom-button types.
- Do not claim a complete operational system if all core operating views have no buttons and no reason is given.

## Delivery Summary File

For complete-system builds, create or update one local JSON file before the final response:

`tmp/qingflow_system_build_summary.json`

Use this file as the structured source of truth for the final report. Include at least:

```json
{
  "package_id": 0,
  "package_name": "",
  "portal_dash_key": "",
  "portal_live_status": "verified | unverified | not_created",
  "front_end_visible": true,
  "apps": [
    {
      "app_key": "",
      "app_name": "",
      "fields_count": 0,
      "views_count": 0,
      "flows_count": 0,
      "charts_count": 0,
      "publish_verify_status": "verified | unverified | failed"
    }
  ],
  "warnings": [],
  "partial_items": [],
  "needs_followup": []
}
```

Rules:

- Populate IDs and counts from readback, not from intended payload only.
- If a required resource is not verified, put it in `partial_items` or `needs_followup` instead of reporting the system as fully complete.
- If the user later adds a data-entry task, keep that separate from the system-build summary unless the user explicitly wants one combined report.
- The final response should match this file: completed resources, unverified items, frontend visibility, and follow-up needs must not contradict the JSON.
- `front_end_visible=true` only when the relevant portal/app publish or live readback proves it. Backend write success alone is not enough.
- Do not mark workflow as missing when the user did not ask for approval, fill, copy, reminders, or process routing. Report it as "not requested/not configured".
- If `partial_items` or `needs_followup` is non-empty, the final status is partial, not complete.
- When running from the CLI repo or a test harness, validate the file with:
  `python scripts/validate_system_build_summary.py tmp/qingflow_system_build_summary.json`.

Final response shape:

```text
已完成：...
未验证/待确认：...
前端可见：是/否/未确认
需要继续修复：是/否；原因...
```

## Recovery Rules

- Timeout, `partial_success`, `write_executed=true`, `safe_to_retry=false`, or incomplete readback means `write_may_have_succeeded`.
- Next action is always `readback_before_retry`: read package, resolve intended apps, then read fields/relations.
- Retry only verified missing apps, fields, or relations.
- Do not rebuild the system as separate single-app creates.
- Do not create `V2`, `测试`, timestamp, or random-suffix apps to bypass duplicate names.

## Portal Template

- Top area: one business entry grid plus one todo/common/frequent component when useful.
- Metrics: one row of 4-6 indicator/target cards with portal section `role: "metric"`; recommended height 5.
- BI charts: one row of 2-3 charts, 1-2 rows; recommended height 7.
- Data views: one row of 1-2 concrete views, 1-2 rows; recommended height 11.
- PC layout uses 24 columns. Components in the same row share the same `y`, must have the same `rows`, and their `cols` should sum to 24.
- Business-entry grid components must include real `config.items[]` entries linking to apps or portals; never submit an empty grid container.
- Build the portal only after referenced apps, raw `view_key`s, and chart ids/keys have been read back.
- Standard section order is business entry -> metric cards -> BI charts -> concrete business views.
- Do not reference platform default views such as `全部数据` / `我的数据` as main portal data views.
- Do not use portal `source_type: "filter"` as the normal automation path; it is raw/unstable and not part of the unified filter DSL.

## Stop Conditions

- If the user only asked for one app, switch to the single-app guide.
- If a same/similar package or app set already exists and the user did not say whether to extend, repair, replace, or create new, stop and ask. Do not start probing with new names.
- If readback shows part of the requested system already exists, list existing apps/fields/views/charts/portal, identify gaps, and patch only the missing or incorrect slices.
- If required package/app/field/relation readback contradicts the intended model, repair the specific missing slice before building dependent resources.
- If a public tool cannot express a needed business feature, state the gap and ask before using any fallback or submitting feedback.
