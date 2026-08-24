# Retired Layout Patch Path

The imperative layout-patch entry described by older versions of this page is retired.
`app_layout_apply` is no longer an MCP tool or CLI command.

For form layout changes, switch to the sibling `qingflow-app-form` Skill:

1. Pin `app_form_schema`.
2. Read the current draft with `app_form_get(being_draft=true)`.
3. Edit the complete canonical AppForm `body`, preserving all fields, sections, rows, and IDs that should remain.
4. Validate and submit the complete declaration with `app_form_apply`.

The old imperative implementation remains only as an internal compatibility adapter and is marked pending deletion.
