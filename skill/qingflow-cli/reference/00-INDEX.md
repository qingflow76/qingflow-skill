# Qingflow CLI Reference Index

Use this file as the first routing page after `SKILL.md` when the task is not a trivial one-command lookup.

## Route by user goal

| User goal | Read first | Then read |
|-----------|------------|-----------|
| Read records, locate one record, inspect schema | [core/data retrieval](./core/QINGFLOW_CLI_DATA_RETRIEVAL_WORKFLOW.md) | [core/field data types](./core/QINGFLOW_CLI_FIELD_DATA_TYPES.md) |
| Create records | [record/create](./record/QINGFLOW_CLI_RECORD_CREATE_WORKFLOW.md) | [record/insert details](./record/insert/README.md) |
| Update records | [record/update](./record/QINGFLOW_CLI_RECORD_UPDATE_WORKFLOW.md) | [core/field data types](./core/QINGFLOW_CLI_FIELD_DATA_TYPES.md) |
| Delete records | [record/delete](./record/QINGFLOW_CLI_RECORD_DELETE_WORKFLOW.md) | - |
| Import records in bulk | [record/import](./record/QINGFLOW_CLI_RECORD_IMPORT_WORKFLOW.md) | - |
| Statistical analysis, ratios, rankings, trends | [record/analysis](./record/analysis/README.md) | [analysis patterns](./record/analysis/analysis-patterns.md) |
| Task/todo context or task action | [task context](./task/QINGFLOW_CLI_TASK_CONTEXT_WORKFLOW.md) | [task ops](./task/ops/README.md) |
| Build or modify apps, views, charts, portal, workflow | [builder index](./builder/README.md) | The resource document named there |

## Builder task shortcuts

| Builder task | Main document |
|--------------|---------------|
| One app end-to-end | [builder/single app](./builder/10-build-single-app.md) |
| Multi-app system / app package | [builder/complete system](./builder/20-build-complete-system.md) |
| Fields, schema, data title/cover | [builder/schema fields](./builder/30-schema-fields.md) |
| Form layout | [builder/layout](./builder/40-layout.md) |
| Views and view filters | [builder/views](./builder/50-views.md) |
| QingBI charts/reports | [builder/charts](./builder/60-charts.md) |
| Portal/workbench | [builder/portal](./builder/70-portal.md) |
| Associated views/reports and current-record matching | [builder/associated resources](./builder/80-buttons-associated-resources.md) |
| Workflow | [builder/workflow](./builder/90-workflow.md) |
| Publish and readback verification | [builder/publish verify](./builder/99-publish-verify.md) |

## Reading rule

Pick the document for the target resource first. Do not start from historical playbooks or old MCP skill names. If a task says "update", route by the resource being updated: fields -> schema fields, views -> views, portal -> portal, charts -> charts, workflow -> workflow.
