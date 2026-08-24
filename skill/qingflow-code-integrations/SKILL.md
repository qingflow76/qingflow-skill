---
name: qingflow-code-integrations
description: Configure Qingflow code block and Q-Linker fields through the public configuration surface when the task involves input field insertion, alias parsing, target field binding, or troubleshooting broken code/q-linker form configurations. In Wingent Momo runtime, use the injected MCP session and recover auth/workspace only after a tool error.
metadata:
  short-description: Configure Qingflow code blocks and Q-Linkers safely
---

# Qingflow Code Integrations

> **Skill 版本**：`qingflow-skills-2026.07.01.04`（入口文档版本；如需确认 CLI 包版本，使用 `qingflow --version` 或 `qingflow --json version`）。

Use this skill when the user wants to build or repair:
- `code_block` fields
- `q_linker` fields
- output alias parsing
- target field binding
- form configurations that depend on code block or Q-Linker relations

Do not use this skill for MCP setup, generic field CRUD, or runtime execution debugging unless those are strictly supporting code block or Q-Linker configuration work.

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
   - `app_resolve`
   - `app_get_fields`
2. Confirm the target field set already exists.
3. Switch to the `qingflow-app-form` Skill and apply a complete version-pinned AppForm declaration.
4. Read the published AppForm again and verify:
   - field type
   - alias config
   - target field binding shape
5. For page-safety checks, use user-side schema or insert checks:
   - `record_insert_schema_get`
   - optional safe `record_insert`

Do not treat raw apply success as enough. Always re-read the field config.

## Code Block Rules

Read [references/code-block.md](references/code-block.md) before changing a code block field.

Use builder high-level config only for:
- input field insertion
- code content
- alias parsing
- auto trigger
- custom button text

The high-level `code_block_binding` name is a compatibility shorthand. In a current AppForm declaration, write the canonical `config.codeBlockBinding` shape returned by the pinned field Schema.

When binding outputs to target fields, do not guess payload shape from memory. Follow the current builder implementation and the readback shape.

Hard rules:
- target fields must already exist
- keep target field types business-compatible
- if a page starts hanging on “关联中”, inspect whether the target field default type or relation config was written incorrectly

## Q-Linker Rules

Read [references/q-linker.md](references/q-linker.md) before changing a Q-Linker field.

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

- `app_get_fields` shows the intended field type
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

- Code block details: [references/code-block.md](references/code-block.md)
- Q-Linker details: [references/q-linker.md](references/q-linker.md)
