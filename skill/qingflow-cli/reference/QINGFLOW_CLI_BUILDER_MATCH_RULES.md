# Builder 字段匹配规则：按钮传参与关联视图/报表筛选

本文只适用于 **Builder 侧 MatchRule**：

- `builder button apply` 的新增数据按钮传参
- `builder associated-resource apply` 的关联视图 / 关联报表筛选条件

它不是 `record_access` 分析筛选 DSL，也不是普通视图 `filters`。

统一语义：

- 固定筛选用 `field_name + operator + value/values`，例如视图 `filters`、报表 `filters`。
- 当前记录上下文匹配用 `target_field + operator + source_field/value`，例如关联资源 `match_mappings`、新增数据按钮传参。
- 不要直接写 `judgeType`、`judgeValues`、`matchRules`；CLI 会按目标协议自动编译。
- 单选 / 多选 / 布尔这类选项值，入参可写选项文本或 option id；视图 / 按钮 / 工作流路径会编译成 Qingflow 需要的 id + details，QingBI 报表路径会编译成 BI 前端需要的文本 `judgeValue`。

---

## 1. 默认写法

优先使用语义化映射，不手写后端 raw `que_relation` / `match_rules`。

### 1.1 新增数据按钮

```json
[
  {
    "client_key": "add_worklog",
    "button_text": "快捷添加工时",
    "trigger_action": "addData",
    "trigger_add_data_config": {
      "target_app_key": "WORKLOG_APP",
      "field_mappings": [
        {"source_field": "数据ID", "target_field": "关联员工"},
        {"source_field": "员工名称", "target_field": "员工姓名"}
      ],
      "default_values": {
        "状态": "待提交"
      }
    }
  }
]
```

`field_mappings` 表示从当前记录动态带值；`default_values` 只表示静态默认值。

### 1.2 关联视图 / 报表

跨应用关联必须显式传 `target_app_key`。若关联的是当前应用自己的视图或报表，可以省略 `target_app_key`，CLI 会默认使用命令里的 `--app-key`。

```json
[
  {
    "client_key": "employee_worklogs",
    "graph_type": "view",
    "target_app_key": "WORKLOG_APP",
    "view_key": "WORKLOG_VIEW",
    "match_mappings": [
      {"target_field": "关联员工", "source_field": "数据ID"},
      {"target_field": "状态", "value": "待提交"}
    ]
  }
]
```

动态条件用 `source_field`；静态条件用 `value`。

`operator` 推荐使用 `eq` / `neq` / `in` / `contains` / `gte` / `lte` / `is_empty` / `not_empty`；兼容 `equal` / `equals` / `=` / `!=` / `any_of` / `one_of` / `empty` 等别名。`field_name` / `field` 可作为 `target_field` 别名；静态单值可写 `value`，也兼容单元素 `values`。

示例：

```json
{"target_field": "客户ID", "operator": "eq", "source_field": "数据ID"}
{"target_field": "状态", "operator": "eq", "value": "有效"}
```

---

## 2. 系统字段

系统字段可以参与匹配：

| 写法 | field_id | 含义 |
| --- | --- | --- |
| `数据ID` / `row_record_id` / `apply_id` / `_id` | `-17` | 当前记录真实 record/apply ID |
| `编号` / `数据编号` / `record_number` | `0` | 前端可见数据编号，可能是自定义编号 |

也可以显式写：

```json
{"source_field": {"field_id": -17}, "target_field": "关联员工"}
```

注意：`数据ID` 和 `编号` 不是同一个东西。要把当前记录填入目标引用字段时，用 `数据ID`。

---

## 3. 类型兼容规则

| 目标 / 源字段类型 | 可匹配对象 |
| --- | --- |
| 引用字段 | 同目标应用的引用字段，或当前源应用记录的 `数据ID(-17)` |
| `数据ID(-17)` | 指向当前源应用的目标引用字段；也可匹配 ID 兼容的文本/数字字段 |
| `编号(0)` | 文本、长文本、数字、金额、编号类字段 |
| 成员字段 | 成员字段 |
| 部门字段 | 部门字段 |
| 单选 / 多选 / 布尔 | 选项类字段或静态选项值 |
| 日期 / 日期时间 | 日期类字段互通 |
| 文本 / 长文本 / 电话 / 邮箱 | 文本类字段互通 |
| 数字 / 金额 | 数值类字段互通 |

附件、子表、代码块、Q-Linker、地址字段默认不作为匹配字段。

---

## 4. 常见错误处理

| 错误场景 | 下一步 |
| --- | --- |
| 字段不存在 | 重新 `builder app get --app-key APP_KEY fields` / `builder app get --app-key APP_KEY`，用准确字段标题或 `field_id` |
| 类型不兼容 | 按上表换兼容的源字段 / 目标字段 |
| 引用来源不一致 | 目标引用字段指向了别的应用；换成指向当前源应用的引用字段 |
| 同时传 semantic 与 raw | 同一项里只能二选一：`field_mappings/match_mappings` 或 raw `que_relation/match_rules` |

---

## 5. 关联资源 ID 口径

`associated_item_id` 是应用级关联资源池里的 `form_asos_chart.id`，最终口径来自：

```bash
qingflow --json builder app get --app-key APP_KEY
```

或同等 `app_get.associated_resources[].associated_item_id`。

它不是 `chart_id`、`chart_key`、`view_key`。但新版 `builder associated-resource apply` 在部分入口可接受 `chart_id` / `chart_key` / `view_key` 作为 selector，并自动解析成后端需要的 `associated_item_id`；写 view config 或排障时仍以读回的 `associated_item_id` 为准。
