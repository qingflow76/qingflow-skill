# Qingflow CLI Code Block / Q-Linker Builder

Use this section when the user wants to build or repair:
- `code_block` fields
- `q_linker` fields
- output alias parsing
- target field binding
- form configurations that depend on code block or Q-Linker relations

Do not use this section for generic field CRUD or runtime execution debugging unless those are strictly supporting code block or Q-Linker configuration work.

## Core Rule

Treat code blocks and Q-Linkers as **integration fields**, not ordinary fields.

For both of them, the public builder request may look like one step, but the real backend form structure has multiple layers. Never invent a new backend meaning. Only compile into the backend structures that already exist.

## Mental Model

### Code block

There are three conceptual layers:

1. Code block field itself
2. Parsed output aliases
3. Target field bindings

Current builder support:
- configure the code block field itself
- configure input insertion into code content
- configure alias parsing

Important:
- keep `qf_output = {...}` as a plain assignment
- do not emit `const qf_output =` or `let qf_output =`

### Q-Linker

There are two conceptual layers:

1. Q-Linker field itself via `remoteLookupConfig`
2. Target field bindings via relation-default + `questionRelations(relationType=Q_LINKER)`

Current builder support:
- one-step high-level config through `q_linker_binding`
- internal compilation into existing backend payloads

`q_linker_binding` is the compatibility/high-level builder shorthand. In a current AppForm declaration, write the canonical `config.qLinkerBinding` shape returned by the pinned field Schema.

## Operating Order

For code block or Q-Linker work, use this order:

1. Resolve the app and read fields:
   - `qingflow builder app resolve`
   - `qingflow builder app get fields`
2. Confirm the target field set already exists.
3. Read the AppForm schema and the update draft, preserve the complete declaration, run `qingflow --json builder app-form validate --schema-version VERSION --file DECLARATION.json`, then run `qingflow --json builder app-form apply --file DECLARATION.json`.
4. Read the published AppForm again and verify:
   - field type
   - alias config
   - target field binding shape
5. For page-safety checks, use user-side schema or insert checks:
   - `qingflow record schema insert`
   - optional safe `qingflow record insert`

Do not treat raw apply success as enough. Always re-read the field config.

## Code Block Rules

Read [code-block.md](./code-block.md) before changing a code block field.

Use builder high-level config only for:
- input field insertion
- code content
- alias parsing
- auto trigger
- custom button text

When binding outputs to target fields, do not guess payload shape from memory. Follow the current builder implementation and the readback shape.

Hard rules:
- target fields must already exist
- keep target field types business-compatible
- if a page starts hanging on “关联中”, inspect whether the target field default type or relation config was written incorrectly

## Q-Linker Rules

Read [q-linker.md](./q-linker.md) before changing a Q-Linker field.

First-stage stable support is only:
- custom mode
- request config
- alias parsing
- target field binding
- auto trigger / button text

Do not generate:
- template mode
- openApp/light-wing branches
- subtable table-match bindings

Hard rules:
- `outputs[*].target_field` is required
- use only supported target field types
- on rebinding, old target fields must be restored from relation-default to safe default type
- `resultFormatPath` must preserve backend-required alias metadata

## Verification Checklist

After each code block or Q-Linker change, verify all of these:

- `qingflow builder app get ... fields` shows the intended field type
- the high-level config is readable and stable
- target fields still have valid types
- insert schema can be opened
- record insert does not get blocked by malformed integration config

If the task explicitly includes runtime verification, keep it separate from configuration verification.

## Common Pitfalls

- Writing code block code with `const qf_output =`
- Treating a Q-Linker or code block binding as a plain field default
- Forgetting to restore old target fields after unbinding
- Using unsupported target field types
- Assuming apply success means the form page can open

## References

- Code block details: [references/code-block.md](./code-block.md)
- Q-Linker details: [references/q-linker.md](./q-linker.md)
