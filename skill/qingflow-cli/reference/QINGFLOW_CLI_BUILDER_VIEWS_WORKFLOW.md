# Builder Views Workflow (Legacy Redirect)

This file is kept only for old cross-links. Use the current canonical document instead:

- [builder/50-views.md](./builder/50-views.md)

Current main path:

```bash
qingflow builder views apply --views-file /abs/path/views.json
```

Use one top-level `views[]` array. Each item carries its own `app_key` and `operation`.

Minimum current shape:

```json
{
  "views": [
    {
      "operation": "upsert",
      "app_key": "APP_KEY",
      "name": "订单跟进视图",
      "type": "table",
      "columns": ["订单编号", "客户名称", "状态", "负责人"],
      "filters": [
        {"field_name": "状态", "operator": "neq", "value": "已关闭"}
      ],
      "query_conditions": {
        "enabled": true,
        "rows": [["订单编号", "客户名称"], ["状态", "负责人"]]
      },
      "action_buttons": [
        {
          "text": "行内新建跟进",
          "action": "add_data",
          "target_app_key": "TARGET_APP_KEY",
          "placement": "list",
          "field_mappings": [
            {"source_field": "数据ID", "target_field": "关联订单"}
          ]
        },
        {
          "text": "详情新建跟进",
          "action": "add_data",
          "target_app_key": "TARGET_APP_KEY",
          "placement": "detail",
          "field_mappings": [
            {"source_field": "数据ID", "target_field": "关联订单"}
          ]
        }
      ]
    }
  ]
}
```

Do not use the old `--app-key + --upsert-views-file / --patch-views-file / --remove-views-file` shape as the normal agent path.
