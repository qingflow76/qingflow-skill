---
name: qingflow-app-form
description: Create, edit, validate, publish, verify, and recover Qingflow application forms through the versioned declarative AppForm surface. Use for app form fields, sections, layout, form settings, attachments, serial numbers, relations, Q-Linker, code blocks, package attachment, or explicit app deletion through either Qingflow CLI or Qingflow MCP. Do not use draft form reads for record operations or other published-schema consumers.
---

# Qingflow App Form

AppForm is one shared declaration contract. Choose one execution surface and use it consistently for the operation; the JSON declaration, schema version, IDs, reconciliation, and recovery rules below are the same.

| Step | Qingflow CLI | Qingflow MCP |
| --- | --- | --- |
| Schema | `qingflow --json builder app-form schema` | `app_form_schema` |
| Read | `qingflow --json builder app-form get` | `app_form_get` |
| Static validation | `qingflow --json builder app-form validate --file DECLARATION.json` | `app_form_apply` validates internally |
| Apply | `qingflow --json builder app-form apply --file DECLARATION.json` | `app_form_apply(spec=DECLARATION)` |
| Delete | `qingflow --json builder app delete --app-key APP_KEY` | `app_delete(app_key=APP_KEY)` |

Before creating an app, let AppForm derive a stable default icon and color from `spec.appName`; do not add visual metadata to the declaration. `app_publish_verify` is retained only for an explicit final cross-resource verification; AppForm recovery never depends on it. For general surface selection, read [$qingflow-common](../qingflow-common/SKILL.md).

## Workflow

1. Read the AppForm Schema and pin its `schemaVersion` and `apiVersion` for the entire operation.
2. Read the pinned field Schema for every canonical field type used, including subtable child types.
3. When a field uses `defaultType: 3` or another config accepts a formula, read the pinned formula Schema with CLI `--schema-kind formula` or MCP `schema_kind="formula"`; use its field-reference, operator, and function catalog instead of inventing formula syntax.
4. For an update, read the draft form with `being_draft=true`. Preserve every field, row, section, and subfield that should remain. For a create, build a declaration without `appKey` and with `packageId`, `spec.appName`, and complete `spec.body`; AppForm derives the icon and color from `spec.appName`.
5. Keep existing `queId`, `sectionId`, `attachId`, and `aliasId` values from get. Omit them only for new resources. Treat `body`, `subfields`, explicit `attachments`, and custom serial-number `components` as complete target state.
6. Save the declaration as JSON. In CLI, run `qingflow --json builder app-form validate --schema-version PINNED --file DECLARATION.json` before every apply and fix every reported pointer. In MCP, call apply directly; it performs the same declaration validation internally. YAML is not accepted.
7. Apply the declaration on the selected surface. Record a newly returned `appKey` immediately. On success, show only `operation`, the non-empty `changes/actions` summary, and warnings. On any non-success result, show the recovery diagnostics, especially deleted/changed field names in `diff/remainingDiff`, and the failed phase.
8. A successful apply has already read back the draft, verified the complete target, and verified the published form. Do not call get only to verify it again. For any non-success result, follow Recovery; never replay a saved backend payload or edit version.

## Read Source

- Use `being_draft=true` for editing and apply recovery.
- Use the default published read for inspecting a live form, configuring another app's relation/Q-Linker, inserting or importing records, and every other consumption workflow.
- Never expose draft-only fields to a published-schema consumer.

## Identity And Deletion

- `sectionId` is a positive decimal string. `queId`, `attachId`, and `aliasId` are positive integers.
- A declaration with `appKey` updates. A declaration without `appKey` always creates a new app and must include `packageId` and `spec.appName`. Neither form accepts `spec.icon` or `spec.color`.
- Repeating a create after losing its response can create a duplicate. Once an `appKey` is known, add it to the original declaration and recover as an update.
- Update `packageId` only when the user wants to ensure that package references the app. It never removes other package references.
- Removing an existing field from `body` or a child from `subfields` deletes it. Replace a field type in two explicit applies: delete, verify, then add the new type without the old `queId`.

## Recovery

- `EDIT_VERSION_CONFLICT`: read the latest draft, rebuild the complete declaration, validate, and retry once.
- `APPLY_READBACK_MISMATCH`: read the latest draft, rebuild the complete declaration from that state, validate, and retry once.
- `APPLY_RESULT_UNKNOWN`: read draft and published forms. Repair from the latest draft; if draft matches but published differs, reapply the same complete target so reconciliation performs publish only.
- `PUBLISH_FAILED`: display `appPublishStatus` and `publishDetails`; resolve the backend validation or approval problem before retrying.
- `EDIT_FINISHED_FAILED`: if published equals draft, call `app_release_edit_lock_if_mine`; do not publish again.
- `RELATION_REBIND_FAILED`: read the draft, preserve returned IDs, and repair only unresolved bindings. Never recreate the app.
- `PACKAGE_ATTACH_RESULT_UNKNOWN`: retain the same `appKey`, `packageId`, and full spec. Reapplying is safe because package attachment is ensure-present.
- If an apply without `appKey` returns no `appKey` and reports `APP_CREATE_RESULT_UNKNOWN`, stop. Do not retry or search by name to guess the created app.

## Constraints

- Pin one Schema version; never combine details from different versions or silently upgrade recovery work.
- Ordinary and section rows contain one to four fields. A section is its own outer block. Subtable columns use only the allowed subfield types returned by the subtable detail Schema.
- Field declarations may set `defaultType` (`1` static, `2` relation/binding, `3` formula) and `defaultValue`; `defaultValue` is `string | null` because the backend `queDefaultValue` is a string, so numeric literals must be passed as strings. For `defaultType: 3`, query the same version with `--schema-kind formula` or `schema_kind="formula"` before composing the formula. Use `null` to clear a default. These properties also apply to subtable fields. Choice defaults belong in `config.defaultOptions`; address, attachment, subtable, and relation defaults belong in `config.defaultValues`. Omit a default when none is intended.
- For `code_block`, when `config.codeBlockBinding.outputs` is non-empty, the `code` must explicitly assign `qf_output`, for example `qf_output = { score: input.score };`; `return {...}` alone does not satisfy output writeback, and each output `path` must point under `qf_output`.
- A relation formula default is `config.defaultValueFormula` and must satisfy the pinned `relation` field Schema's `FormulaExpression`; do not infer its syntax from another version or from backend DTO names.
- If widths are present, every field in that row must have one and the total must equal 100.
- Keep declarations at or below 2 MiB and 64 object/array nesting levels. For a Q-Linker `json_path` input, set `key` to the selected field's exact name so get can reconstruct the placeholder losslessly.
- Do not call CLI apply when the validation command fails. The command validates the local Schema plus declaration-only cross-field rules, including resolvable integration selectors, supported output target types, and globally unique Q-Linker/code-block output targets. It is not a dry run and does not read or modify Qingflow; checks that need current or external app state remain in apply. For MCP, resolve validation errors returned by `app_form_apply` before retrying.
- Delete an application only after explicit user intent through the selected CLI or MCP delete operation.
