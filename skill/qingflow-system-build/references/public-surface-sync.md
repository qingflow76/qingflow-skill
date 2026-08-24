# Qingflow Core Public Surface Sync

Use this file as the maintenance baseline for the core Qingflow skills.
It is not a user-facing product spec. It exists to prevent skill drift.

## Current Public Defaults

### User data

- Read range first with `app_get`, then `record_browse_schema_get(view_id=...)`
- Treat `record_browse_schema_get.fields` as the selected Qingflow table view header schema; `record_access.fields` and `record_list` field selectors must stay aligned with it.
- Standard flows:
  - analyze: `app_get -> record_browse_schema_get -> record_access -> Python`
  - browse detail: `app_get -> record_browse_schema_get -> record_list / record_get`
  - explicit export/download/Excel: `app_get -> choose view_id -> view_get -> record_export_*` or `record_export_direct`; export tools require explicit `view_id`
  - insert: `record_insert_schema_get -> record_insert(items)`
  - update: `record_get -> record_update`; use `record_update_schema_get` only for failure diagnosis or ambiguous writable-field routing

### Tasks

- Discovery stays on `task_list`
- `task_list --query` uses backend search first and only applies local fallback when backend returns zero rows
- Public actions are:
  - `approve`
  - `reject`
  - `rollback`
  - `transfer`
  - `urge`
  - `save_only`
- `reject` requires `payload.audit_feedback`
- `save_only` requires non-empty `fields`
- `TASK_RUNTIME_CONSUMED_AFTER_ACTION` is a normal post-success warning when the current node runtime is consumed and `46001` appears on re-read

### Builder

- Official package entry: `package_get`, `package_apply`
- Official builder writes:
  - `app_form_apply`
  - `app_delete`
  - `app_flow_apply`
  - `app_views_apply`
  - `app_custom_buttons_apply`
  - `app_associated_resources_apply`
  - `app_charts_apply`
  - `portal_apply`
  - `app_publish_verify`
- `app_schema_apply` and `app_layout_apply` are retired internal adapters and are not MCP/CLI tools.
- `portal_apply` edit mode may omit `sections` for base-info-only updates
- `app_charts_apply.visibility` is a public capability and should be treated as a base-only visibility update
- Existing view parameter replacement should use `app_views_apply.views[]` with `operation="patch"`; existing buttons, resources, and charts should use `patch_buttons`, `patch_resources`, and `patch_charts`; `upsert_*` is for creation or full target config
- `app_get.editability` uses:
  - `can_edit_app_base`
  - `can_edit_form`
  - `can_edit_flow`
  - `can_edit_views`
  - `can_edit_charts`

## Known High-Drift Areas

- Task actions, especially `save_only`, reject payload requirements, and `46001` post-action interpretation
- Package public tools: do not regress to `package_create` / `package_attach_app` as the public default story
- App editability: do not let `can_edit_form` imply app base-info writes
- Portal and chart visibility: keep the public story on `portal_apply` / `app_charts_apply`, not low-level internal writes
- Analysis path: standard path stays `record_access -> Python`

## Release Checklist For Skill Maintenance

After each beta that changes public behavior, re-check:

1. `public_surface.py`
2. `README.md`
3. `server_app_builder.py` and `server.py` top-level guidance
4. CLI help for `task`, `builder package`, `builder portal`, `builder charts`
5. Whether new warnings or verification fields need to be explained in skills

If a tool behavior changed but the public surface did not, prefer updating the relevant skill section instead of expanding this file.
