# Builder Example Files

Use these files as copyable bases after reading the matching resource document. Replace placeholder ids, app keys, field names, and chart/view ids before applying.

| Resource | Main example | Notes |
|----------|--------------|-------|
| Historical single-app schema probe | [schema/schema_single_app_form_standard.example.json](./schema/schema_single_app_form_standard.example.json) | Retired `--form-file` shape; use `builder app-form schema/get/validate/apply` for current declarations. |
| Historical multi-app schema probe | [schema/schema_multi_app_form_relation_layout.example.json](./schema/schema_multi_app_form_relation_layout.example.json) | Retired `--apps-file` shape; current systems create independent AppForms and then bind confirmed app keys. |
| Existing-app layout probe | [layout/layout_sections_full.example.json](./layout/layout_sections_full.example.json) | Historical layout-patch shape; current new and existing forms use the complete AppForm `spec.body`. |
| Views | [views/views_upsert_table_minimal.example.json](./views/views_upsert_table_minimal.example.json), [views/views_batch_full.example.json](./views/views_batch_full.example.json) | `views[]` shape with filters, query panel, view-bound buttons, batch upsert/patch/remove. |
| Charts | [charts/charts_upsert_dashboard_starter.example.json](./charts/charts_upsert_dashboard_starter.example.json) | Standalone chart apply; portal usually creates missing charts inline. |
| Portal | [portal/portal_sections_standard_workbench.example.json](./portal/portal_sections_standard_workbench.example.json) | Standard workbench with inline QingBI charts and data views. |
| Associated resources | [associated/associated_resources_semantic_full.example.json](./associated/associated_resources_semantic_full.example.json) | Current-record matching through `match_mappings`. |
| Record insert | [record/record_insert_all_field_types.example.json](./record/record_insert_all_field_types.example.json) | `record insert --items-file` shape for common field kinds; replace all titles/options/ids from `record schema insert`. |
| Advanced standalone buttons | [buttons/custom_buttons_advanced.example.json](./buttons/custom_buttons_advanced.example.json) | For maintenance only; normal business buttons are declared in views. |

Probe files such as `portal_sections_all_types.example.json` and `schema_apply_add_fields_all_types.json` are for capability testing, not default business delivery.
