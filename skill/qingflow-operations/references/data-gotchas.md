# Data Gotchas

For final statistics, grouped distributions, rankings, trends, or insight-style conclusions, use [$qingflow-record-analysis](../../qingflow-record-analysis/SKILL.md) instead of keeping that reasoning inside `$qingflow-operations`.

## Record Reads

- For analysis-style reads, use `record_access` through [$qingflow-record-analysis](../../qingflow-record-analysis/SKILL.md)
- `record_list` is for browsing and sample inspection only
- `record_get` is for one exact record and downloads readable detail-page images into `media_assets.items[].local_path` plus attachments/documents/tables into `file_assets.items[].local_path`
- Use `record_browse_schema_get` when field titles are uncertain instead of guessing ids
- Do not present paged browse output as if it were a grouped or full-population conclusion
- Use `record_export_direct` only when the user explicitly asks for export/download/Excel output, and always pass an explicit `view_id` from `app_get.accessible_views` or the frontend URL

## Direct Writes

- `record_insert` is schema-first through `record_insert_schema_get`; default to `items=[{"fields": {...}}]`
- `record_update` is detail-first: read `record_get`, compose the requested title-keyed `fields` map, then write directly; use `record_update_schema_get` only after update failure or ambiguity
- `record_delete` does not need a schema-get step
- For batch insert, `partial_success` means some rows were created; use `created_record_ids`, failed `row_number`, and `failed_fields` to repair only failed rows
- If a direct-write tool returns `write_executed=false`, the write was blocked and not executed for that item
- Prefer `verify_write=true` for complex, relation-heavy, subtable, or production writes

## Lookup Fields

- Member / department / relation fields may accept natural text, but MCP may return `needs_confirmation`
- Do not guess ids when the response returns candidate options
- Retry only after the user confirms the explicit candidate

## Subtables and Attachments

- Subtable payloads stay under the parent table field as a row array
- Attachment fields are two-step: upload first, then write the returned upload payload
- For reads, attachment/rich-text images returned by `record_get` should be opened from local `media_assets` paths, and non-image files should be read from `file_assets` local paths or `extraction.text_path`, instead of remote file URLs
