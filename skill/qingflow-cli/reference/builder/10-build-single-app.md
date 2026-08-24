# Build Single App

Read this when the user asks to create or complete exactly one Qingflow app.

## Scope

Responsible for: package/app resolution, form schema, workflow only when requested or clearly needed, business views, sample data, and final verification.

Not responsible for: multi-app relation modeling or a portal across several apps. Use [20-build-complete-system.md](./20-build-complete-system.md) when the user asks for a system, package, multiple modules, or cross-app relations.

## Main chain

```text
package/app resolve -> AppForm schema/get/validate/apply -> workflow if requested/needed -> views with query_conditions/action_buttons -> insert 5 sample records -> publish/readback verify
```

If a new package is needed, create it with `builder package apply --config-file`. Package JSON should contain only `package_name + icon + color`. Create or edit the app form with the CLI sequence in [30-schema-fields.md](./30-schema-fields.md): `builder app-form schema`, then `get --app-key APP_KEY --being-draft` for updates, `validate --schema-version VERSION --file DECLARATION.json`, and `apply --file DECLARATION.json`.

## Required reads by phase

| Phase | Read |
|-------|------|
| Fields, form sections, layout, and app creation | [30-schema-fields.md](./30-schema-fields.md) |
| Workflow | [90-workflow.md](./90-workflow.md) only when the user asks for approval, fill/copy, reminders, process routing, or task handling |
| Views | [50-views.md](./50-views.md) |
| Sample data | [../record/QINGFLOW_CLI_RECORD_CREATE_WORKFLOW.md](../record/QINGFLOW_CLI_RECORD_CREATE_WORKFLOW.md) |
| Final status | [99-publish-verify.md](./99-publish-verify.md) |

## Demo files

Use the examples as file bases, then replace placeholder app/package ids and business field names:

| Resource | Example |
|----------|---------|
| Historical single-app schema probe | [schema_single_app_form_standard.example.json](../examples/schema/schema_single_app_form_standard.example.json) (retired `--form-file` shape; use the AppForm CLI sequence above for current declarations) |
| Business views | [views_upsert_table_minimal.example.json](../examples/views/views_upsert_table_minimal.example.json) |
| Workflow, when needed | [workflow/README.md](./workflow/README.md) |

## Completion standard

- Exactly one top-level data title field exists.
- Common business fields use canonical or supported intuitive aliases from [30-schema-fields.md](./30-schema-fields.md).
- App creation and form edits use one complete, version-pinned AppForm declaration; preserve existing IDs on updates.
- New business views use business names, not default names such as `全部数据` or `我的数据`.
- New business views must include `query_conditions` so users can search/filter from the frontend query panel.
- New business views must include shortcut buttons through `action_buttons`; every core operating view configures both `placement: "list"` and `placement: "detail"` buttons.
- Unless the user explicitly says not to create sample data, insert 5 realistic records after schema/views are ready.
- Workflow may be skipped when no approval/fill/copy/reminder/process-routing requirement exists; mention that it was not requested instead of inventing a flow.
- When workflow is configured, use `builder flow schema` + `builder flow get` first, then `builder flow apply --spec-file` for a full flow or `--patch-nodes-file` for a targeted update.
- If a write returns `partial_success`, `write_executed=true`, `safe_to_retry=false`, timeout, or readback 40002, read back before retrying the write.

## Stop or switch conditions

- If the user names multiple business objects, modules, or cross-app relations, switch to [20-build-complete-system.md](./20-build-complete-system.md).
- If an existing app with the same or very similar name appears and the user did not explicitly say update, extend, or create new, stop and ask which target to use.
- If readback shows the requested app already has some resources, patch the verified gaps instead of recreating the app.
- Do not create `V2`, `测试`, timestamp, or random-suffix apps to bypass duplicate names in a real business package.
