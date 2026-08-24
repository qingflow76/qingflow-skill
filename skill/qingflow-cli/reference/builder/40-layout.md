# Builder Form Layout (AppForm)

Read this only when the task is about repairing or changing the form layout of an existing app.

## Scope

Responsible for: AppForm section titles, `rows` matrix, and existing-app layout repair.

Not responsible for: creating new apps, adding fields, or complete-system app creation. New apps must put layout directly in `spec.body` through [30-schema-fields.md](./30-schema-fields.md).

Do not read this as a standalone CLI write path. For new or existing apps, edit the complete canonical AppForm `body` through the CLI AppForm sequence in [30-schema-fields.md](./30-schema-fields.md).

## Main chain

```text
qingflow --json builder app-form get --app-key APP_KEY --being-draft -> edit spec.body sections/rows -> qingflow --json builder app-form validate --schema-version VERSION --file DECLARATION.json -> qingflow --json builder app-form apply --file DECLARATION.json -> readback on recovery
```

## Demo file

Use [layout_sections_full.example.json](../examples/layout/layout_sections_full.example.json) only as a historical layout probe. For current work, start from `qingflow --json builder app-form get --app-key APP_KEY --being-draft` and preserve the complete canonical declaration.

## Canonical shape

For AppForm layout maintenance, use canonical sections and rows from the pinned AppForm Schema. Each row contains the allowed field objects/IDs for that version. Do not invent top-level `columns`, and do not use portal `x/y/cols/rows` here.

```json
{
  "apiVersion": "builder.qingflow.com/v1alpha1",
  "appKey": "APP_KEY",
  "spec": {
    "body": [
      {
        "kind": "section",
        "sectionId": "30001",
        "title": "基础信息",
        "rows": [
          {"fields": [
            {"queId": 101, "name": "客户名称", "type": "text", "dataTitle": true},
            {"queId": 102, "name": "订单金额", "type": "amount"}
          ]},
          {"fields": [
            {"queId": 103, "name": "状态", "type": "single_select", "config": {"options": ["待处理", "已完成"]}},
            {"queId": 104, "name": "负责人", "type": "member"}
          ]}
        ]
      }
    ]
  }
}
```

## One-eye form layout rules

| Intent | Correct shape | Avoid |
| --- | --- | --- |
| Group fields on a form | `spec.body[].title + spec.body[].rows` | Portal `position.pc` / `x` / `y` / `cols` |
| Put fields on one horizontal form row | `["客户名称", "订单金额"]` inside `rows` | Top-level `columns` |
| Keep existing layout and add/update groups | complete AppForm body preserving existing blocks | partial `mode`/`sections` payloads |
| Repair missing/unknown field errors | Re-read `app get fields` and remove/correct names | Guessing field ids from old payload |

Short rule: **form layout rows arrange fields; portal rows arrange components. Do not mix the two.**

## Update existing layout

- Preserve the complete current AppForm body unless intentionally removing fields or sections.
- Re-read `qingflow --json builder app-form get --app-key APP_KEY --being-draft` before writing; every field in rows must be retained with its canonical ID.
- If apply returns `partial_success` or layout validation details, read the draft and published forms before retrying.
- There is no current batch layout CLI; update each app's complete AppForm independently.

## Common failures

| Failure | Action |
|---------|--------|
| `UNKNOWN_LAYOUT_FIELD` | Re-read the pinned AppForm Schema and draft; correct the field pointer. |
| `DUPLICATE_LAYOUT_FIELD` | Keep each field in only one row in the complete AppForm body. |
| `INCOMPLETE_LAYOUT` | Rebuild the complete body from the latest draft; do not submit a partial patch. |
| repeated shape errors | Re-run `qingflow --json builder app-form schema --schema-version VERSION` and validate before apply. |
