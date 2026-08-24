# Builder App Delivery Workflow (Legacy Redirect)

This file is kept only for old cross-links. Do not use it as the main build flow.

Use the current Qingflow CLI builder documents instead:

- [builder/README.md](./builder/README.md)
- [builder/10-build-single-app.md](./builder/10-build-single-app.md)
- [builder/20-build-complete-system.md](./builder/20-build-complete-system.md)
- [builder/30-schema-fields.md](./builder/30-schema-fields.md)
- [builder/50-views.md](./builder/50-views.md)
- [builder/70-portal.md](./builder/70-portal.md)
- [builder/90-workflow.md](./builder/90-workflow.md)
- [builder/99-publish-verify.md](./builder/99-publish-verify.md)

Current complete-system main chain:

```text
package apply/get -> AppForm schema/get/validate/apply per app -> app readback -> workflow if requested/needed -> views with query_conditions/action_buttons -> insert 5 sample records per app -> portal with inline chart -> publish/readback verify
```

Current rules:

- New apps use complete, version-pinned AppForm declarations; do not use the retired `apps[].form`, `add_fields`, or `--apps-file` schema adapters.
- Do not call the retired `builder schema apply` or `builder layout apply` routes.
- Create relation-independent apps first, then use confirmed target `appKey`s in complete AppForm declarations.
- Business buttons are declared in view `action_buttons`.
- Portal charts use the section `chart` field, either an existing `chart_id` or an inline QingBI definition.
- Historical low-level notes live in [builder/reference/app-delivery-sop.md](./builder/reference/app-delivery-sop.md) and are for debugging only, not route selection.
