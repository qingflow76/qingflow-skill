# Builder 统一筛选 / 条件写法

本文适用于 Builder 侧所有给智能体公开的筛选和条件入口：

- 视图固定筛选：`builder views apply` 的 `filters`
- 视图动作按钮显示条件：`action_buttons[].visible_when`
- QingBI 图表筛选：`builder charts apply` 或 `portal apply sections[].chart.filters`
- 关联视图 / 关联报表匹配：`builder associated-resource apply` 的 `match_mappings`
- 新增下游记录传参：`field_mappings` / `default_values`

它不是 `record_access` 分析筛选 DSL。数据分析仍走 `record access` 的 `where` 规则。
流程条件属于 WorkflowSpec 路径：先读 `app_flow_get_schema` / `app_get_flow`，再按读回结构修改；不要把 raw workflow `autoJudges/judgeType` 混入视图、报表、关联资源的公共筛选 DSL。

公开写法按场景选择，智能体不要混用。**operator 语义完全一致，区别只在字段名键**：

- **固定筛选**：`field_name + operator + value/values`
- **关联资源上下文匹配**：`target_field + operator + source_field/value`
- **新增数据传参**：`source_field + target_field`；静态默认值写 `default_values`

不要直接写 `judgeType`、`judgeValues`、`matchRules`、`beforeAggregationFilterMatrix`。CLI 会按目标协议自动编译，并在读回时还原为业务语义。

最短判断：

| 你想表达 | 写法 | 示例 |
| --- | --- | --- |
| 当前视图/图表只显示某类数据 | `filters` | `{"field_name":"状态","operator":"eq","value":"进行中"}` |
| 关联报表/关联视图只显示“当前记录相关”的数据 | `match_mappings` + `source_field` | `{"target_field":"关联客户","operator":"eq","source_field":"数据ID"}` |
| 关联报表/关联视图再加一个固定条件 | `match_mappings` + `value/values` | `{"target_field":"状态","operator":"eq","value":"有效"}` |
| 从当前记录创建下游记录并带值 | `field_mappings` | `{"source_field":"数据ID","target_field":"关联工单"}` |

---

## 1. `operator` / `value` 统一规则

| `operator` | 含义 | `value/values` |
| --- | --- | --- |
| `eq` | 等于 | 单值用 `value` |
| `neq` | 不等于 | 单值用 `value` |
| `in` | 任一匹配 | 多值用 `values` |
| `contains` | 包含 / 模糊包含 | 单值用 `value` |
| `gte` | 大于等于 | 单值用 `value` |
| `lte` | 小于等于 | 单值用 `value` |
| `is_empty` | 为空 | 不写 `value/values` |
| `not_empty` | 不为空 | 不写 `value/values` |

`operator` 省略时按 `eq` 处理，但主示例必须显式写 `operator`。`value` 是单值主写法；`values` 是多值主写法。CLI 兼容 `value` 传数组、`values` 传单个标量，但不要把兼容形态当主示例。

兼容别名：`equal`、`equals`、`=`、`==`、`!=`、`not_equal`、`any_of`、`one_of`、`include`、`like`、`empty`、`is null`、`not empty`、`not null`。主示例只写上表 canonical operator。

### 1.1 不同字段类型的值写法

默认优先写业务可读值，但要区分字段类型。选项字段（单选/多选/是否）在视图筛选、QingBI 筛选、关联资源静态筛选中均支持选项文本或 option id，CLI 会按目标协议自动转成 id 或文本。成员、部门、关联记录这类实体字段在固定筛选里优先写唯一 id 或 `{id,value}`；只有新增数据默认值、record 写入、候选解析类路径才先写名称，解析失败后再按候选改成 id。

| 字段类型 | 推荐值写法 | 示例 |
| --- | --- | --- |
| 文本 / 长文本 / 手机 / 邮箱 | 字符串；模糊匹配用 `contains` | `{"field_name":"客户名称","operator":"contains","value":"上海"}` |
| 数字 / 金额 | JSON 数字；范围用 `gte` / `lte` | `{"field_name":"金额","operator":"gte","value":10000}` |
| 日期 / 日期时间 | 字符串；优先 `YYYY-MM-DD` 或 `YYYY-MM-DD HH:mm:ss` | `{"field_name":"计划日期","operator":"lte","value":"2026-06-30"}` |
| 单选 | 选项文本或 option id；优先写文本；对象可写 `{id,value}` / `{optId,optValue}` | `{"field_name":"状态","operator":"eq","value":"进行中"}` 或 `{"field_name":"状态","operator":"eq","value":"160712876"}` |
| 多选 | 多值用 `values`；每一项可写选项文本、option id 或选项对象 | `{"field_name":"标签","operator":"in","values":["重点","续约"]}` |
| 布尔 / 是否 | 按字段实际选项文本写，通常是 `是` / `否` | `{"field_name":"是否逾期","operator":"eq","value":"是"}` |
| 成员 / 部门 | 固定筛选写唯一 id 或 `{id,value}`；候选解析类写入路径可先写名称 | `{"field_name":"负责人","operator":"eq","value":{"id":123,"value":"沈嘉慧"}}` |
| 关联记录 / relation | 固定筛选写目标记录真实 `record_id/apply_id`；当前记录跨应用匹配用 `source_field:"数据ID"` | `{"field_name":"关联客户","operator":"eq","value":"535734615263924225"}` |
| 引用 / 数据填充字段 | 按读回展示类型写值；若本质来自选项字段，仍优先写展示文本 | `{"field_name":"客户等级","operator":"eq","value":"A"}` |

字段值选择原则：

- 选项字段：优先写选项文本，例如 `"正常"`；如果文本不唯一或来自读回，也可写 option id，例如 `"160712876"`。
- 成员/部门：固定筛选优先写 id 或 `{id,value}`；record 写入、默认值等候选解析路径可先写名称，若返回 `needs_confirmation` 再按候选改成 id。
- 关联/relation：固定筛选写目标记录真实 `record_id/apply_id`；跨应用当前记录匹配写 `source_field:"数据ID"`，不要写前端编号。
- 引用/数据填充字段：按前端展示的业务值写；如果引用来源是选项字段，仍优先写选项文本。
- 读回口径：`builder view/chart/associated-resource get` 优先返回业务文本和 canonical `operator`，不把后端数字 `judgeType`、option id、`matchRules` 作为智能体主输出。raw `config` 只用于诊断。

空值判断示例：

```json
{"field_name": "完工日期", "operator": "is_empty"}
```

读回示例：

```json
{"field_name":"使用状态","operator":"eq","value":"正常"}
{"target_field":"状态","operator":"in","values":["有效","待提交"]}
```

---

## 2. 当前记录上下文匹配

优先使用语义化映射，不手写后端 raw `que_relation` / `match_rules`。

心智模型：**同一个 operator，同一套 value 规则；只是当前记录匹配要把 `field_name` 改成 `target_field`，并用 `source_field` 表示当前记录字段。**

- 固定筛选当前资源自己的数据：`field_name + operator + value/values`
- 用当前记录过滤另一个资源：`target_field + operator + source_field`
- 给另一个资源加静态筛选：`target_field + operator + value/values`
- 从当前记录创建下游记录时传值：`source_field + target_field`，不写 `operator`

`operator` 和 `value/values` 的含义与 §1 完全一致。`operator` 省略时默认为 `eq`，但为了可读性，主配置仍推荐显式写出。
不要把跨应用“当前记录匹配”写成 `filters`：`filters` 只筛当前视图/报表自己的数据；`match_mappings` 才表示“拿当前记录的某个字段去匹配另一个资源”。

### 2.1 新增数据按钮

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

`field_mappings` 表示从当前记录动态带值，不需要 `operator`；`default_values` 只表示静态默认值。

### 2.2 关联视图 / 报表

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

动态条件用 `source_field`；静态条件用 `value/values`。如果一个条件写了 `source_field`，就不要再写 `value/values`。

`field_name` / `field` 可作为 `target_field` 别名；静态单值写 `value`，多值写 `values`，空值类 operator 不写值。

跨应用 relation 最常见写法是把当前记录的数据 ID 匹配到目标应用的引用字段：

```json
{"target_field": "关联客户", "operator": "eq", "source_field": "数据ID"}
```

这里 `target_field` 是被关联资源所在应用里的字段，`source_field` 是当前详情页这条记录里的字段。不要把它写成视图/报表 `filters`，也不要手写 `matchRules`。

如果 `target_field` 是目标应用中的引用 / relation 字段，最稳妥的当前记录匹配值是 `source_field: "数据ID"`，因为它表示当前记录真实 `record_id/apply_id`。不要用前端可见 `编号` 代替，除非目标字段本身就是文本/编号字段。

示例：

```json
{"target_field": "客户ID", "operator": "eq", "source_field": "数据ID"}
{"target_field": "状态", "operator": "eq", "value": "有效"}
{"target_field": "状态", "operator": "in", "values": ["有效", "待提交"]}
{"target_field": "归档说明", "operator": "is_empty"}
```

---

## 3. 系统字段

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

## 4. 类型兼容规则

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

## 5. 常见错误处理

| 错误场景 | 下一步 |
| --- | --- |
| 字段不存在 | 重新 `builder app get --app-key APP_KEY fields` / `builder app get --app-key APP_KEY`，用准确字段标题或 `field_id` |
| 类型不兼容 | 按上表换兼容的源字段 / 目标字段 |
| 引用来源不一致 | 目标引用字段指向了别的应用；换成指向当前源应用的引用字段 |
| 同时传 semantic 与 raw | 同一项里只能二选一：`field_mappings/match_mappings` 或 raw `que_relation/match_rules` |

---

## 6. 关联资源 ID 口径

`associated_item_id` 是应用级关联资源池里的 `form_asos_chart.id`，最终口径来自：

```bash
qingflow --json builder app get --app-key APP_KEY
```

或同等 `app_get.associated_resources[].associated_item_id`。

它不是 `chart_id`、`chart_key`、`view_key`。但新版 `builder associated-resource apply` 在部分入口可接受 `chart_id` / `chart_key` / `view_key` 作为 selector，并自动解析成后端需要的 `associated_item_id`；写 view config 或排障时仍以读回的 `associated_item_id` 为准。
