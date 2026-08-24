# Schema Apply Field Types And Scenarios

This legacy entry is kept only as a compatibility pointer.

Use the current builder schema document instead:

- [builder/30-schema-fields.md](./builder/30-schema-fields.md)

Current main rules:

- New app creation and updates use the CLI AppForm commands: pin the version with `qingflow --json builder app-form schema`, build a complete declaration, validate it with `qingflow --json builder app-form validate --schema-version VERSION --file DECLARATION.json`, then apply it with `qingflow --json builder app-form apply --file DECLARATION.json`.
- For complete systems, create apps independently, retain every returned `appKey`, and add relations only with confirmed target app keys in later complete declarations.
- New and existing apps use `spec.body` to express fields, sections, rows, and form settings together.
- Do not use retired `builder schema apply`, `builder layout apply`, `--apps-file`, `--form-file`, or `--create-if-missing` paths.
- Do not impose a one-relation-field-per-app limit; create the relation fields the business model needs and rely on backend validation plus readback.
- All field-type capability probes live under [examples/schema](./examples/schema/); probes are not business delivery templates.
