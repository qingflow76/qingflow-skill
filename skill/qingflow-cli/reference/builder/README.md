# Builder Index

This directory is for Qingflow system-building work through `qingflow builder ...`. Form fields, form layout, form settings, and application deletion use the direct CLI commands documented in [30-schema-fields.md](./30-schema-fields.md).

## Choose the main path

| Situation | Read |
|-----------|------|
| User asks for one app only | [10-build-single-app.md](./10-build-single-app.md) |
| User asks for a complete system, app package, or several related apps | [20-build-complete-system.md](./20-build-complete-system.md) |
| User asks to change one existing resource | Read that resource document directly: [fields](./30-schema-fields.md), [layout](./40-layout.md), [views](./50-views.md), [charts](./60-charts.md), [portal](./70-portal.md), [associated resources](./80-buttons-associated-resources.md), or [workflow](./90-workflow.md) |

## Decision gate before writing

| Evidence | Action |
|----------|--------|
| User gives an `app_key`, `view_key`, `chart_id`, `dash_key`, or exact existing package id | Treat the task as an update to that existing target unless the user explicitly asks for a new one |
| User names several business objects/forms/modules, or asks for a “系统 / 应用包” | Use the complete-system path; do not compress them into one app |
| Same or very similar package/app already exists and user did not say extend or replace | Stop and ask whether to extend existing, repair missing parts, or create a new package/app |
| Existing readback already contains part of the requested system | List the verified existing resources, identify gaps, and patch only missing/incorrect slices |
| Write timed out, returned `partial_success`, `write_executed=true`, or `safe_to_retry=false` | Read back before retrying; do not create `V2`, `测试`, timestamp, or random-suffix resources |

## Default build order

```text
package -> AppForm per app -> workflow if requested/needed -> views -> portal with chart -> publish/readback verify
```

Rules:

- Complete systems create apps with `builder app-form schema`, `validate --schema-version VERSION --file DECLARATION.json`, and `apply --file DECLARATION.json`, one complete declaration per app, and retain each returned `appKey`.
- Pin the AppForm schema version and preserve every existing field, section, row, and ID on updates.
- Create relation-independent apps first; use confirmed target `appKey`s in later complete AppForm declarations.
- The CLI commands for form work are `builder app-form schema`, `builder app-form get`, `builder app-form validate`, and `builder app-form apply --file`.
- The old `builder schema apply` and `builder layout apply` routes are retired compatibility adapters, not public commands.
- Single-app builds use one app path; do not add relation fields unless the user asks for cross-app modeling.
- Workflow is conditional: build it only when the user asks for approval, fill/copy, reminders, process routing, task handling, or the business process clearly cannot work without it.
- Portal chart sections use one `chart` field: `{"chart_id":"..."}` to reuse an existing QingBI chart, or `{"app_key":"...","name":"...","chart_type":"...",...}` to create/update the needed chart inline.
- Buttons are part of the view design: declare them in the target view with `action_buttons`.
- Update instructions live inside the resource document. Do not use `update-*` as a separate main route.
- Batch read, batch write, and patch are resource-specific variants, not separate workflows.

## File responsibilities

| File | Responsibility |
|------|----------------|
| [10-build-single-app.md](./10-build-single-app.md) | One-app delivery order and completion standard |
| [20-build-complete-system.md](./20-build-complete-system.md) | Multi-app package delivery order and relation strategy |
| [30-schema-fields.md](./30-schema-fields.md) | Field modeling notes and AppForm pointer |
| [40-layout.md](./40-layout.md) | Retired layout-patch pointer; use the direct AppForm CLI sequence for form layout |
| [50-views.md](./50-views.md) | Table/card/board/gantt views, filters, query panel, view patches, ordinary view action buttons |
| [60-charts.md](./60-charts.md) | Standalone QingBI chart maintenance; portal dashboards normally use section `chart` for missing reports |
| [70-portal.md](./70-portal.md) | Portal apply/delete, standard workbench layout, component config, section `chart` |
| [80-buttons-associated-resources.md](./80-buttons-associated-resources.md) | Associated views/reports and context mappings; standalone button maintenance only when the user explicitly asks to maintain existing button bodies outside view design |
| [90-workflow.md](./90-workflow.md) | WorkflowSpec, patch_nodes, workflow verification |
| [99-publish-verify.md](./99-publish-verify.md) | Publish verification, partial success, readback-before-retry |

## Example files

Use [../examples/README.md](../examples/README.md) as the example index. Main build documents stay concise; full JSON bases live under `reference/examples/<resource>/`.

Low-level historical notes start from [reference/app-delivery-sop.md](./reference/app-delivery-sop.md). Do not use them to choose the app/relation/layout creation path; the current creation path is this index plus [20-build-complete-system.md](./20-build-complete-system.md) and [30-schema-fields.md](./30-schema-fields.md).
