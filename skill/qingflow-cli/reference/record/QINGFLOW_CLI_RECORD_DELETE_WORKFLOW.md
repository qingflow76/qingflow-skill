# Qingflow CLI：删除记录 SOP

删除记录是高风险写操作，默认先定位、再确认目标、再最小删除。

## 主链路

```bash
qingflow --json record list --app-key <APP_KEY> --view-id <VIEW_ID> --query "<关键词>"
qingflow --json record get --app-key <APP_KEY> --record-id <RECORD_ID> --view-id <VIEW_ID>
qingflow --json record delete --app-key <APP_KEY> --record-id <RECORD_ID> --view-id system:all
```

批量删除用文件传 record ids：

```bash
qingflow --json record delete --app-key <APP_KEY> --record-ids-file tmp/delete_record_ids.json --view-id system:all
```

`tmp/delete_record_ids.json` 是记录 ID 数组：

```json
["535734615263924225", "535734615263924226"]
```

## 规则

1. 先用 `record list` 或 `record get` 解析精确 `record_id`，不要用模糊标题直接删。
2. 高风险或批量删除前，向用户确认记录数量、关键字段和应用名。
3. `record delete` 必须传可访问的系统 `--view-id system:*`；读取定位时可以使用 custom/system view，删除提交时不要传 `custom:*`、`list_type`，也不要省略系统视图上下文。
4. 删除后需要验证时，用 `record get` 或 `record list` 读回确认；读回 404/不存在才代表已删除，权限型 40002 只说明当前读回路径不可见。
5. 批量删除若出现部分成功，按返回的成功/失败项只处理失败 ID，不要重放全批。
