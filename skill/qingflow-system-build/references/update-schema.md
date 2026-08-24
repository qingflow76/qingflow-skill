# Retired Schema Patch Path

The imperative schema-patch entry described by older versions of this page is retired.
`app_schema_apply` is no longer an MCP tool or CLI command.

For field changes, switch to the sibling `qingflow-app-form` Skill:

1. Pin `app_form_schema` and read every field-type detail used by the target.
2. Read the current draft with `app_form_get(being_draft=true)`.
3. Preserve every field, section, row, subfield, and ID that should remain.
4. Validate and submit the complete AppForm declaration with `app_form_apply`.

The old imperative implementation remains only as an internal compatibility adapter and is marked pending deletion.
