# Code Block Builder Notes

## What Builder Should Configure

- code block field type
- code content
- inserted input fields inside code content
- alias parsing
- auto trigger
- custom button text

For current AppForm declarations, use `config.codeBlockBinding` from the pinned field Schema. The snake_case `code_block_binding` name is a compatibility shorthand used by the high-level builder layer.

## Stable Writing Rules

- Always emit `qf_output = {...}`
- Never emit `const qf_output = {...}`
- Never emit `let qf_output = {...}`

## Useful CRM Pattern

Inputs:
- customer name
- source
- budget
- timing
- decision-maker flag

Outputs:
- score
- level
- priority
- summary
- next follow date

## Target Field Rules

Required:
- every `outputs[*].target_field` must point to an existing field

Allowed target field types:
- text
- long text
- number
- amount
- date
- datetime
- single select
- multi select
- boolean

Do not bind code block outputs to:
- q_linker
- code_block
- relation
- subtable
- attachment
- member
- department
- address

## Safe Verification

- `app_get_fields`
- `record_insert_schema_get`
- optional `record_code_block_run`

Treat configuration verification and runtime verification as separate checks.
