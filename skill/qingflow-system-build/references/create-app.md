# Retired App Creation Path

The imperative app-creation entry described by older versions of this page is retired.
`app_schema_apply` is no longer an MCP tool or CLI command.

For new work, switch to the sibling `qingflow-app-form` Skill:

1. Resolve or create the target package with `package_get` / `package_apply`.
2. Pin a version with `app_form_schema`.
3. Select an explicit non-template icon and color with `workspace_icon_catalog_get`.
4. Submit one complete AppForm declaration without `appKey` through `app_form_apply`.
5. Record the returned `appKey` immediately and follow the Skill recovery rules for uncertain results.

The old imperative implementation remains only as an internal compatibility adapter and is marked pending deletion.
