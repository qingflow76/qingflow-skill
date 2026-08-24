# Legacy Note

This reference set is retained only so older prompts do not break.

Prefer the split write paths:

- `record_insert_schema_get -> record_insert`
- `record_get -> record_update` for normal updates; `record_update_schema_get` is diagnostic-only after failure or ambiguity
- `record_list / record_get -> record_delete`
- `app_get -> record_import_schema_get -> record_import_*`

If a prompt still says “CRUD”, route it to the split skills instead of reviving the old unified path.
