# Builder Playbooks

Use these when you need a quick reminder of the standard v2 builder sequences.

## Create a complete system / app package

1. `package_get` or `package_apply`
2. switch to `qingflow-app-form` and apply one complete declaration per app
3. retain each returned `appKey`; create relation-independent apps first, then declare relations with known app keys
4. use returned/readback `appKey` values for views, workflow, charts, buttons, associated resources, and portal work
5. `app_publish_verify` only when the user asks for explicit live verification or a final verification pass is required

Follow the AppForm Skill recovery rules for uncertain create/update results. Never repeat a create after losing its response or create `V2` / `测试` / random-suffix apps to dodge duplicate names.

## Create a new app in an existing package

1. `package_get`
2. switch to `qingflow-app-form`
3. `app_form_schema -> app_form_apply`
5. `app_publish_verify` only if the user asks for explicit live verification

## Update fields on an existing app

1. `app_resolve`
2. switch to `qingflow-app-form`
3. `app_form_schema -> app_form_get(being_draft=true) -> app_form_apply`

## Rework layout

1. switch to `qingflow-app-form`
2. `app_form_schema -> app_form_get(being_draft=true) -> app_form_apply`

AppForm `body` is complete target state. Preserve every field, section, row, and ID that should remain.

## Add or update workflow

1. `app_get_fields`
2. `app_get_flow`
3. `role_search` or `member_search`
4. `role_create` if the business wants a reusable role and no good exact role exists
5. `app_flow_apply`

If `app_flow_apply` reports `FLOW_DEPENDENCY_MISSING`, fix schema first.
If it reports `FLOW_ASSIGNEE_REQUIRED`, resolve roles or members first and retry with WorkflowSpec `attrs.responsible`.

## Add or update views

1. `app_get_fields`
2. `app_get_views`
3. `app_views_apply`

For both workflow and view work, prefer `suggested_next_call` over re-guessing arguments after a validation failure.

## Final readback

Prefer these fields after writes:

- `app_get.tag_ids`
- `app_get.publish_status`
- `app_get_layout.unplaced_fields`
- `app_get_views.views`
- `app_get_flow.nodes`
