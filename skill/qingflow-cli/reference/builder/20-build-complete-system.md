# Build Complete System

Read this when the user asks for a complete business system, app package, multiple modules, or related apps.

## Scope

Responsible for: package creation/reuse decision, all app form schemas, cross-app relation fields, shared view/portal conventions, workflow where requested, and final verification.

Not responsible for: single existing-app record CRUD. Use record documents from [../00-INDEX.md](../00-INDEX.md) for data work.

## Main chain

```text
package apply/get -> AppForm schema/get/apply per app -> app readback -> workflow if requested/needed -> views with query_conditions/action_buttons -> insert 5 sample records per app -> portal with inline chart -> publish/readback verify
```

## Hard rules

- Create each app with `qingflow --json builder app-form schema`, `validate --schema-version VERSION --file DECLARATION.json`, and `apply --file DECLARATION.json`. Record every returned `appKey` before creating dependent relation declarations.
- New package config uses `package_name + icon + color`.
- Pin one AppForm schema version per app and submit a complete declaration containing fields, sections, rows, and settings.
- Do not call the retired `builder schema apply` or `builder layout apply` routes, and do not use their `add_fields`, `apps-file`, or `form-file` payloads as the current path.
- For relations, create relation-independent apps first, read back their published `appKey`s, then submit complete declarations using the canonical relation shape and known target app keys.
- One app may contain multiple `relation` fields when the business model needs them.
- Relation selectors use the AppForm camelCase shape, not bare strings: write `config.displayField: {"name":"产品编码"}` and `config.visibleFields: [{"name":"产品名称"}]`. `config.targetAppKey` must be a target app key confirmed by readback.
- If AppForm apply times out or returns uncertain write state, perform draft/published form readback before retrying. Do not recreate apps with `V2`, `测试`, or random suffixes.
- If a same/similar package or app set already exists and the user did not say whether to extend, repair, replace, or create new, stop and ask. Do not start probing with new names.
- If readback shows part of the requested system already exists, list existing apps/fields/views/charts/portal, identify gaps, and patch only the missing or incorrect slices.
- Do not create default views such as `全部数据` or `我的数据`; those are platform defaults.
- New business views must include `query_conditions`; do not create business views that only define columns, filters, and buttons but lack a frontend query panel.
- New business views must include shortcut buttons through `action_buttons`; every core operating view must configure both `placement: "list"` and `placement: "detail"` buttons. Do not create core operating views that only contain columns and filters.
- Build workflow only when the user asks for approval, fill/copy, reminders, process routing, task handling, or the business process clearly depends on it. Do not invent workflows just to make the system look complete.
- When workflow is needed, use the complete flow chain: `builder flow schema`, `builder flow get`, then `builder flow apply --spec-file` for a full WorkflowSpec or `--patch-nodes-file` for targeted edits.
- For portal charts, use one section `chart` field: write `{"chart_id":"..."}` to reuse an existing QingBI chart, or `{"app_key":"...","name":"...","chart_type":"...",...}` to create/update the needed chart inline.
- Portal business-entry grid components must contain real entry items, not empty `config` or `items: []`.
- Unless the user explicitly says not to create sample data, insert 5 realistic records for every new app after schema/views are ready and before final chart/portal verification.

## Required reads by phase

| Phase | Read |
|-------|------|
| App package and schema | [30-schema-fields.md](./30-schema-fields.md) |
| Workflow | [90-workflow.md](./90-workflow.md) only when workflow is requested or clearly required |
| Views | [50-views.md](./50-views.md) |
| Sample data | [../record/QINGFLOW_CLI_RECORD_CREATE_WORKFLOW.md](../record/QINGFLOW_CLI_RECORD_CREATE_WORKFLOW.md) |
| Portal | [70-portal.md](./70-portal.md) |
| Final status | [99-publish-verify.md](./99-publish-verify.md) |

## Demo files

Use these examples as file bases, then replace placeholder package/app/view keys and business field names:

| Resource | Example |
|----------|---------|
| Historical multi-app schema probe (retired; migration reference only) | [schema_multi_app_form_relation_layout.example.json](../examples/schema/schema_multi_app_form_relation_layout.example.json) |
| Business views with filters, query panel, and view-bound buttons | [views_upsert_table_minimal.example.json](../examples/views/views_upsert_table_minimal.example.json) |
| Standard portal with inline QingBI charts and business views | [portal_sections_standard_workbench.example.json](../examples/portal/portal_sections_standard_workbench.example.json) |
| Workflow, when needed | [workflow/README.md](./workflow/README.md) |

AppForm command:

```bash
qingflow --json builder app-form validate --schema-version <SCHEMA_VERSION> --file /abs/path/app-form.json
qingflow --json builder app-form apply --file /abs/path/app-form.json
```

If the write returns timeout or partial success, first read back the draft and published AppForm. Do not replay a create or guess an app by name; once an `appKey` is known, recover through a complete update declaration.

## Completion standard

A complete system is not just several created apps. Before reporting completion, verify these items from readback:

- Package exists, and its `package_id` is known.
- Every core business object is a separate app with `app_key`, `app_name`, `icon`, `color`, and exactly one readable data title field.
- Cross-app relation fields are present where the business model needs them; each relation uses a confirmed `targetAppKey` and object selectors in `config.displayField` / `config.visibleFields`.
- Core apps were created with complete AppForm declarations, so fields and readable form sections/rows were submitted together.
- Core operating views exist and their `query_conditions` and `action_buttons` are verified; list-row buttons and detail-page buttons are both configured through the view.
- Each new app has 5 realistic sample records unless the user explicitly skipped sample data.
- Portal exists only after referenced apps and raw `view_key`s are known; chart sections use `chart` either with a verified `chart_id` or an inline QingBI chart definition; business-entry grids have non-empty `config.items[]`.
- Workflow is verified only when requested or clearly required; otherwise report it as not requested/not configured.
- Configured workflows are verified by `builder flow get` readback against the intended WorkflowSpec or `patch_nodes` change.
- Final status follows [99-publish-verify.md](./99-publish-verify.md): distinguish completed, unverified, frontend visible, and needs follow-up.

If workflow was not requested and not clearly required, report it as “not requested / not configured”, not as a missing resource.
