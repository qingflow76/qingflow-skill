# Builder Buttons And Associated Resources

Read this when the task mentions advanced custom button maintenance, deleting button bodies, cross-view button reuse, complex qRobot/wings buttons, associated views, associated reports, or current-record context matching.

## Scope

Responsible for: `builder button apply`, `builder associated-resource apply`, advanced view button placement maintenance, associated view/report display config, `match_mappings`, and button add-data mappings.

Not responsible for: ordinary business buttons declared while creating or patching a view. For normal cases, write `action_buttons` inside `builder views apply`; see [50-views.md](./50-views.md).

## Main chain

```text
app get -> app get views/charts/buttons/associated resources -> apply button or associated-resource -> readback
```

## Demo files

| Scenario | Example |
|----------|---------|
| Associated views/reports with current-record matching | [associated_resources_semantic_full.example.json](../examples/associated/associated_resources_semantic_full.example.json) |
| Advanced standalone button maintenance | [custom_buttons_advanced.example.json](../examples/buttons/custom_buttons_advanced.example.json) |

## Custom buttons

- For normal view-level business actions, prefer `builder views apply` with `action_buttons`.
- Use this standalone button tool for advanced cases: deleting button bodies, reusing the same button across many views, bulk reordering bindings, changing style independently, or configuring qRobot/wings when the user provides exact config.
- Use `upsert_buttons` for create/update and `patch_buttons` for small changes.
- Use `view_configs` only after reading target raw `view_key`.
- Use semantic conditions from [reference/match-rules.md](./reference/match-rules.md). Fixed filters use `field_name + operator + value/values`; associated-resource context matching uses `target_field + operator + source_field/value`.
- For add-data button field mappings, use target/source semantics, not raw backend ids, unless a contract explicitly requires ids.
- If `button apply` returns `CUSTOM_BUTTON_APPLY_PARTIAL` / `VIEW_CUSTOM_BUTTON_READBACK_PENDING` while `custom_buttons_verified=true`, do not recreate the button. Run `builder app get --app-key APP views` and inspect the target view `buttons[]` for `button_type=CUSTOM` plus the expected `button_text` or `button_id`. Only reapply `view_configs` if the view binding is actually absent.

Start from user intent:

- Current record creates a downstream/related record -> `addData` / `add_data`, usually `detail` or `list`, with `target_app_key + field_mappings`.
- Global independent entry -> `addData` / `add_data` on `header`, without current-record `source_field`.
- Open a URL, SOP, or help page -> `link` with URL.
- Approve, reject, close, or change status -> do not invent a normal button; model workflow/task action or use exact existing automation config.
- Existing automation/agent -> `qRobot` / `wings` only when the user provides the exact config.

### Choose the button path

| Need | Preferred path |
| --- | --- |
| Create or patch a normal business button on one view | `builder views apply` with `action_buttons` |
| Set style, icon, cross-view reuse, remove button body, reorder bindings | `builder button apply` |
| Add qRobot/wings behavior | `builder button apply`, only with user-provided exact config |
| Clear a view's custom button bindings | `builder button apply` with `view_configs[].mode="replace"` and `buttons: []` |

### Choose the action

| Standalone `trigger_action` | View `action_buttons.action` | Use for | Required inputs | Avoid |
| --- | --- | --- | --- | --- |
| `addData` | `add_data` | Create a related/downstream Qingflow record from the current record: acceptance from order, worklog from work order, payment request from purchase order, follow-up from customer | `trigger_add_data_config.target_app_key`; usually `field_mappings: [{"source_field": "数据ID", "target_field": "关联源记录"}]`; optional `default_values` | Do not use without a real target app and compatible relation/reference field |
| `link` | `link` | Open an external system, help document, SOP, or fixed URL | `trigger_link_url` in standalone mode; `url` in view `action_buttons` | Do not use as a fake workflow/status/approval action |
| `qRobot` | `qRobot` | Trigger an existing Qingflow robot/automation | User-provided robot/config payload | Do not invent ids, parameters, or automation behavior |
| `wings` | `wings` | Trigger an existing Wings/agent/external capability | User-provided Wings/config payload | Do not use as the default button type |

Status transition or approval is not a generic custom-button action by itself. Use `addData` only if the action really creates a downstream record. Use `qRobot` / `wings` only when the automation already exists and the user supplies the configuration.

### Choose the placement

| `placement` | Frontend position | Best use | Avoid |
| --- | --- | --- | --- |
| `header` | View header | Global actions that do not depend on one current row: open SOP, create an independent record, global entrance | Current-record `field_mappings` |
| `list` | Row/list button, backend `INSIDE` | Row-level actions that depend on the current record | Actions that need a detail-page review before execution |
| `detail` | Record detail page | Current-record context actions; safest place for add-data buttons | High-frequency bulk actions |

View-type guidance:

- `table`: supports `header`, `list`, and `detail`; use it as the default view type for operational buttons.
- `board`: only add state-specific buttons and always configure `button_limit` / `visible_when`.
- `card`: prefer `detail`; use `list` only when the card-level action is obvious.
- `gantt`: prefer `header` or `detail`; avoid row/list buttons unless the user explicitly asks.

### Choose the style

| `style_preset` | Use for |
| --- | --- |
| `primary_blue` | Main positive action on the view, usually one per view |
| `text_blue` | Low-weight link or secondary row action |
| `secondary_gray` | Informational or low-priority action |
| `neutral_outline` | Related-record creation that should not dominate the page |
| `warning_orange` | Attention/risk action that is not destructive |
| `danger_red` | Destructive or high-risk action; avoid unless the user explicitly wants it |

Do not make every button primary or danger. If the user did not ask for custom style, prefer view-level `action_buttons` and let the tool choose defaults.

Standalone example:

```json
{
  "upsert_buttons": [
    {
      "client_key": "create_acceptance",
      "button_text": "创建验收单",
      "style_preset": "primary_blue",
      "trigger_action": "addData",
      "trigger_add_data_config": {
        "target_app_key": "ARRIVAL_APP",
        "field_mappings": [
          {"source_field": "数据ID", "target_field": "关联工单"}
        ],
        "default_values": {"状态": "待验收"}
      }
    }
  ],
  "view_configs": [
    {
      "view_key": "RAW_VIEW_KEY",
      "mode": "merge",
      "buttons": [
        {
          "button_ref": "create_acceptance",
          "placement": "detail",
          "button_limit": [
            [{"field_name": "状态", "operator": "eq", "value": "已完工"}]
          ]
        }
      ]
    }
  ]
}
```

## Associated views and reports

- Manage the app-level resource pool and view detail display through `associated-resource apply`.
- Use associated resources only after the target view/report already exists. This tool attaches and filters existing resources; it does not create view bodies or QingBI report configs.
- Current-record matching belongs here, not in view `filters` or `query_conditions`.
- For current-record filtering, use `match_mappings`:

```json
{
  "target_field": "关联客户",
  "operator": "eq",
  "source_field": "数据ID"
}
```

- Static filters can use `target_field + operator + value`.
- Dynamic current-record filters use `source_field`; static filters use `value`. Do not put both in the same mapping.
- `operator` / `value` follows the same public semantics as view and QingBI filters. Option fields accept option labels or option ids; member/department/relation static values should be unique, and id or `{id,value}` is safest when names may duplicate.
- Do not mix semantic `match_mappings` with raw `match_rules` in the same resource.
- Dataset BI reports can only be associated after they already exist; `charts apply` creates application-source QingBI reports.

Detailed compatibility rules are in [reference/match-rules.md](./reference/match-rules.md). The older full delivery notes are in [reference/app-delivery-sop.md](./reference/app-delivery-sop.md).
