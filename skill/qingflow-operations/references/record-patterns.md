# Record Patterns

If the task shifts into grouped analysis, ratio, ranking, trend, or any final statistical conclusion, switch to [$qingflow-record-analysis](../../qingflow-record-analysis/SKILL.md).

## Browse Pattern

Use `record_browse_schema_get -> record_list` when:

- the user wants to browse records
- the target `record_id` is unknown
- a delete target still needs confirmation
- the user needs sample rows or a small export
- the user gives fuzzy text such as a company, project, bug, or contract name

For fuzzy lookup, pass `query` and optional `query_fields`. `record_list` returns at most 10 `data.items`, plus `data.pagination.total_count` and `lookup.next_action`.

- `lookup.next_action="record_get"`: read the single returned item with `record_get`
- `lookup.next_action="ask_user"`: ask the user to choose from returned `data.items`
- `lookup.next_action="refine_query"`: ask for a narrower keyword or add `query_fields`
- `lookup.next_action="broaden_query"`: remove overly narrow fields or ask for another clue

## Detail Pattern

Use `record_browse_schema_get -> record_get` when:

- the exact `record_id` is known
- the user needs one record in detail
- a write target needs verification before action
- the user needs images or attachments shown on the detail page; read downloaded images from `media_assets.items[].local_path`, and read documents/tables from `file_assets.items[].local_path` or `extraction.text_path`

## Insert Pattern

Use `record_insert_schema_get -> record_insert(items)`.

1. Confirm the target app
2. Read `required_fields`, `optional_fields`, `runtime_linked_required_fields`, and `payload_template`
3. Build `items` as `[{"fields": {...}}]`; a single record is one item
4. Write member, department, and relation fields with natural strings first when the user provided names
5. If lookup fields are ambiguous, stop and ask for confirmation
6. On `partial_success`, keep `created_record_ids` and only repair failed `row_number` / `failed_fields`

## Update Pattern

Use `record_get -> record_update`.

1. Confirm the target app and `record_id`
2. Read `record_get` in the same view/context the user is using when a `view_id` is known
3. Build a field-title keyed `fields` map from `record_get.fields[]` and the user's requested changes
4. Run `record_update` directly; let MCP auto-select the executable update route
5. If `record_update` fails because fields/routes are ambiguous or unavailable, then use `record_update_schema_get` as a diagnostic tool

## Delete Pattern

Use `record_list / record_get -> record_delete`.

1. Confirm the exact `record_id`
2. Run `record_delete`
3. Do not invent range deletes from guessed browse results
