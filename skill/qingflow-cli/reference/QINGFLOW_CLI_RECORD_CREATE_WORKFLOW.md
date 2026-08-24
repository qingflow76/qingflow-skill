# Qingflow CLI：创建记录 SOP（申请节点）

---

**创建记录 SOP 见 skill：`qingflow-record-insert`。**

CLI 对应主路径：

```bash
qingflow --json record schema insert --app-key <APP_KEY> > tmp/qingflow_insert_schema.json
qingflow --json record insert --app-key <APP_KEY> --items-file tmp/records.json > tmp/qingflow_insert_result.json
```

不要用 `record schema applicant` 代替 `record_insert_schema_get` 的主路径；新建记录需要 insert-ready schema 里的 `required_fields`、`optional_fields`、`payload_template`、`format_hint`、`expected_format`、`example_value` 和字段级 `options`。

成员、部门、关联记录、选项、附件等特殊字段按 `qingflow-record-insert` 的 **Special Field Write Cheatsheet** 写：先读 insert schema；部门/成员不能自造候选；选项值必须来自 schema `options` 的文本或 id；关联记录批量写入优先 `record_id`，自然名称只在唯一匹配时使用；附件先上传再写返回值。

追加样例数据时也必须 schema-first：按 `required_fields` 补齐必填；按 `expected_format/example_value` 选择数值、金额、日期等格式；按 `options` 生成选项值。不要按业务常识自造“正常/已完成/高优先级”等 schema 里不存在的选项。比例、完成率、评分、百分比等字段也按 schema 示例写；如果字段被建成金额/整数类而不接受小数，不要强塞 decimal，改用符合 schema 的整数值，或回到 builder 阶段把字段建模为 `number`。

录入数据时不要填写轻流系统字段：`数据ID`、`编号`、`申请人`、`申请时间`、`创建人`、`创建时间`、`提交人`、`提交时间`、`更新时间`、`更新人`、`当前流程状态`、`当前处理人`、`当前处理节点`、`流程标题`。这些字段由平台生成；需要确认时在创建成功后读取记录详情，不要把它们写进 `fields` / `items[].fields`。
