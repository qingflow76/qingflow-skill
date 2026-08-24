# Builder Views

Read this when the task is about table/card/board/gantt views, fixed filters, query panels, view sorting, associated report/view display on a view, or repairing existing views.

## Scope

Responsible for: `builder views apply --views-file`, top-level `views[]`, `operation`, `columns`, `filters`, `query_conditions`, `action_buttons`, and view readback.

Not responsible for: creating associated report resources or maintaining custom button bodies outside the view design. New business views must include `query_conditions`; ordinary business shortcut buttons are required and are declared only through `action_buttons` on the target view.

## Main chain

```text
app get -> app get fields/views -> views apply with required query_conditions and list/detail action_buttons -> app get/views readback
```

## Update existing views

- Prefer `views[].operation="patch"` for small changes to an existing view.
- Use raw `view_key` from `app_get.views[].view_key`; do not use record-data `custom:<view_key>` prefixes.
- Do not send a partial `upsert` object to update a complex existing view; use `operation="patch"` with `set`.
- Verify filters, query conditions, and associated resources separately before reporting success.

## Detailed contract notes

稳定命令：**`qingflow builder views apply --views-file`**（别名 **`qingflow build views apply`**）。编写前已结合 **builder 契约**与实现要点整理；**标准 `views[]` 文件**见 **[views_upsert_table_minimal.example.json](../examples/views/views_upsert_table_minimal.example.json)**（与门户/报表 **`.example.json`** 同风格，已包含必需的查询面板、列表快捷按钮和详情快捷按钮）。

> **权限**：视图**新建**走后端 `createViewgraphConfig`，需要同时满足 **视图管理 / ViewManagementAuth**（`beingViewManageStatus`）和 **数据管理 / DataManageAuth**；视图**更新/删除**只走 **ViewManagementAuth**。未开启高级应用权限时 `beingViewManageStatus` 等价回落到 **DataManageAuth**。失败时常见 **40002 / 40161 / 编辑锁**，参见主技能与 **ADMIN** 速查。

> **默认系统视图**：`全部数据`、`我的数据`、`我发起的`、`待办`、`已办`、`抄送` 等由轻流自带，**不要新建同名业务视图**。新建视图必须用业务名，例如 `项目台账视图`、`客户跟进视图`、`逾期任务看板`。如果确实要调整默认系统视图，只能从 `app get views` 取已存在的 raw **`view_key`** 后用 `views[].operation="patch"` 更新。

> **契约**（权威键名、枚举、`execution_notes`、示例）：
> `qingflow --json builder contract --tool-name app_views_apply`
> （`--tool-name` 为契约索引，用于拉取 **`allowed_keys` / 别名 / 示例**。）
> 契约示例若带 `"profile"`，不要复制到 `--views-file`；CLI 指定 profile 用根级 `qingflow --profile …`。

---

## 1. 推荐操作顺序（读 → 写 → 校验）

| 步骤 | 动作 | CLI |
|------|------|-----|
| ① 读应用地图 | 先看 compact views/charts/buttons/associated resources | `qingflow --json builder app get --app-key <APP_KEY>` |
| ② 读字段/视图 | 确认 **`columns`** / `query_conditions.rows` 可用字段、核对 **`view_key`** | `qingflow --json builder app get --app-key <APP_KEY> fields` / `qingflow --json builder app get --app-key <APP_KEY> views` |
| ③ 准备补丁 JSON | 写入一个 **`{"views":[...]}`** 文件，每个 view item 自带 `operation` 和 `app_key` | — |
| ④ 应用视图补丁 | 执行 apply | `qingflow builder views apply …`（写入命令自动 JSON，默认直接 stdout；需要留档时用 `tee`） |
| ⑤ 配置查询面板和快捷按钮 | 新建业务视图必须写 `query_conditions` 和 `action_buttons`，按钮同时覆盖 `list` 和 `detail` 位置 | `builder views apply` |
| ⑥ 需要上线时 | 发布侧校验 | `qingflow builder publish verify --app-key …` |

**说明**：`views apply` 的 **`--publish`** 对应契约里的 **`publish`**；新建业务视图必须包含 `query_conditions` 和 `action_buttons` 并使用 `publish=true`，因为底层按钮写入会自动发布。只有删除、纯维护补丁、或用户明确要求的只读/归档视图，才允许不带按钮；只读/归档视图仍应配置 `query_conditions`。

---

## 2. CLI 形态

```bash
qingflow builder views apply \
  --views-file PATH \
  [--publish | --no-publish]
```

- **`--views-file`**：推荐唯一主入口。文件为 **JSON 对象**，形如 `{"views":[...]}`；同一批可混合创建、局部修改、删除，可混合同 app / 跨 app 视图。
- 每个 `views[]` 项必须写 **`app_key`**；`operation` 为 **`upsert`** / **`patch`** / **`remove`**。
- CLI 内部按 view job 并发写入，上限 20，结果按输入顺序返回。
- 兼容旧入口 **`--app-key + --upsert-views-file / --patch-views-file / --remove-views-file`**，但不作为智能体主写法。
- 输出默认直接给 stdout，前端可直接读取；需要留档时用 `qingflow builder views apply … | tee tmp/builder_views_apply.json`。

---

## 2.1 参考示例文件（与门户 / 报表同风格）

| 文件 | 用途 |
|------|------|
| [views_upsert_table_minimal.example.json](../examples/views/views_upsert_table_minimal.example.json) | **新建 table 视图**标准 **`views[]` 文件**：`operation` + `app_key` + `name` + `type` + **`columns`** + 必需的 `query_conditions` + 必需的 `action_buttons`（含 `list` 与 `detail`） |
| [views_batch_full.example.json](../examples/views/views_batch_full.example.json) | 批量能力示例：同批 `upsert` / `patch` / `remove`，table / board / gantt，固定筛选、查询面板、视图内按钮和可见性 |

复制到具体应用前务必替换文件内 **`app_key`** 和 **`columns`**；**`name`** 重名时会更新已有同名视图而非新建（见 **§4**）。

---

## 3. 请求体形状（与契约对齐）

CLI 将参数与文件内容拼装为服务层载荷，**顶层键**如下：

| 键 | 说明 |
|----|------|
| **`views`** | 必填数组；每项是一个 view job |
| **`views[].operation`** | `upsert` / `patch` / `remove`；省略时按字段推断，但推荐显式写 |
| **`views[].app_key`** | 必填；允许同批混合同 app / 跨 app |
| **`views[].name` / `view_key`** | 创建用 `name`；更新/删除优先用 raw `view_key` |
| **`views[].query_conditions`** | 新建业务视图必填；配置前端查询面板字段布局 |
| **`views[].set` / `unset`** | `operation="patch"` 时使用 |

**别名**（契约 `aliases` 节选）：**`fields` / `column_names` → `columns`**；**`view_key` / `viewKey`**；**`tableView`→`table`**、**`kanban`→`board`** 等；**`filter_rules`→`filters`**；**`startField`→`start_field`** 等。

---

## 4. 创建 vs 更新（`view_key` 与 `name`）

服务逻辑概要：

- **`operation="remove"`**：优先传 raw **`view_key`**；也可传唯一视图显示名 `name`，显示名重名则 **`AMBIGUOUS_VIEW`**。
- **`operation="upsert"`**：
  - 若提供 **`view_key`**：对该视图做 **更新**（含类型变更等，仍受后端约束）。
  - 未提供 **`view_key`**：若 **`name` 唯一** 匹配已有视图 → **更新**；否则 → **创建**。
- **`operation="patch"`**：对已有视图做局部参数替换；必须有 `view_key` 或唯一 `name`，并写 `set` / `unset`。

响应中的 **`verification.by_view[].status`** 会出现 **`created` / `updated`** 等；**`views_diff`** 汇总创建/更新/失败名单。

**`partial_success`**：部分视图成功、部分失败时整体仍可能带成功信封，务必读 **`failed`** 与 **`execution_notes`**。

**系统默认名禁止新建**：未提供 `view_key` 的 `upsert` 不要使用 `全部数据`、`我的数据`、`我发起的`、`待办`、`已办`、`抄送` 这类默认系统视图名。它们不是业务视图模板，而是平台默认对象；新业务视图用具体业务名。

---

## 5. `type` 与各类型必填

契约 **`view.type`**：**`table`** | **`card`** | **`board`** | **`gantt`**。

| `type` | 列/字段要点 | 类型专属键 |
|--------|----------------|------------|
| **`table`** | **`columns`**（业务字段 **显示名**，须能在 **`app get fields`** 里找到） | — |
| **`card`** | 同 table | — |
| **`board`**（看板） | 列；且须 **`group_by`**（分组字段名） | **`group_by`** |
| **`gantt`** | 列；须 **`start_field`**、**`end_field`**（通常为日期类字段名） | 可选 **`title_field`** |

实现侧校验：对 **table/card**，若声明了 **`columns`**，在 **过滤系统列**后须 **至少保留一个**真实应用字段，否则报错——**不能**只用系统列名凑一列（系统列集合见 **[reference/app-delivery-sop.md](./reference/app-delivery-sop.md)**）。

---

## 6. `filters` / `query_conditions` / `visibility` / `action_buttons`

### 6.0 条件/匹配一眼决策表

先按目标场景选入口。所有入口都接受智能体友好的字段名/操作符语义，但底层编译路径不同。

| 目标场景 | 写到哪里 | 推荐写法 | 不要这样做 |
| --- | --- | --- | --- |
| 视图打开时固定筛选数据 | `filters` | `{"field_name":"状态","operator":"eq","value":"进行中"}` | 不要写 `judgeType` / `judgeValues`；不要把它放进 `query_conditions` |
| 前端查询面板显示哪些字段 | `query_conditions.rows` | `[["客户名称", "负责人"], ["创建时间"]]` | 不要写筛选值；不要把它当 OR 条件 |
| 按钮显示条件 | `action_buttons[].visible_when` | `{"field_name":"状态","operator":"eq","value":"已完工"}` | 不要手写后端判断符 |
| 当前记录创建下游记录时传值 | `field_mappings` | `{"source_field":"数据ID","target_field":"关联工单"}` | 不要放在 `header` 按钮；`header` 没有当前记录上下文 |
| 关联视图/关联报表按当前记录过滤 | `associated-resource apply.match_mappings` | `{"target_field":"关联客户","operator":"eq","source_field":"数据ID"}` | 不要用 `filters` 或 `query_conditions` 代替 |
| 关联视图/关联报表静态筛选 | `match_mappings` | `{"target_field":"状态","operator":"eq","value":"有效"}` | 不要混用 raw `match_rules` |

短规则：**固定筛选用 `filters`；查询栏用 `query_conditions`；当前记录匹配用 `match_mappings`；当前记录传参用 `field_mappings`。**

### 6.1 `filters`

- 项形状：**`field_name`**、**`operator`**、**`values`**（或契约允许的 **`value`** 别名）。
- **`operator`**：统一公共语义，推荐 `eq` / `neq` / `in` / `contains` / `gte` / `lte` / `is_empty` / `not_empty`；兼容 `equal` / `equals` / `=` / `!=` / `any_of` / `one_of` / `empty` 等别名（以契约为准）。
- **`in` 等多值**：传 **列表**；**`value`** 为列表时可作别名。
- **`value` 按字段类型写**：文本/数字/日期直接写业务值；单选/多选/是否优先写选项文本，也支持 option id；成员/部门/关联记录固定筛选优先写唯一 id 或 `{id,value}`。完整规则见 **[reference/match-rules.md](./reference/match-rules.md)**。
- **语义**：固定筛选条件，打开视图即生效。不要把前端查询栏字段写进 `filters`。
- **写入 / 读回语义**：智能体始终写 `field_name + operator + value/values`；CLI 内部自动转换目标协议，读回也会还原成 `operator/value` 语义。不要手写或解释后端判断符。

示例：

```json
{"field_name": "状态", "operator": "eq", "value": "进行中"}
```

### 6.2 `query_conditions`

`query_conditions` 是前端“查询条件/查询栏”配置，和 `filters` 是两套语义。新建业务视图必须配置 `query_conditions`，不要交付没有查询面板的业务视图。

- `filters`：固定筛选，打开视图即生效。
- `query_conditions`：只配置前端查询面板可输入哪些字段；用户输入查询值后才生效。
- `rows` 是字段布局矩阵，不表示 OR 条件。
- `rows` 只放前端查询面板支持的字段：文本、长文本、数字、金额、日期/时间、单选/多选、成员、部门、手机号、邮箱、布尔。
- 不要把 relation、attachment、subtable/subfield、address、Q-Linker 或 code-block 字段放进 `query_conditions`。
- 需要固定筛选时用 `filters`；需要关联报表/关联视图按当前记录匹配时用 `builder associated-resource apply` 的 `match_mappings`。
- 每个新建业务视图至少配置 2-4 个查询字段；优先选择标题/编号、状态、负责人、日期等高频检索字段。

示例：

```json
{
  "views": [
    {
      "operation": "upsert",
      "app_key": "APP_KEY",
      "name": "客户查询视图",
      "type": "table",
      "columns": ["客户名称", "负责人", "客户状态", "创建时间"],
      "filters": [
        {"field_name": "客户状态", "operator": "eq", "value": "有效"}
      ],
      "query_conditions": {
        "enabled": true,
        "exact": false,
        "hide_before_query": false,
        "rows": [["客户名称", "负责人"], ["创建时间"]]
      },
      "action_buttons": [
        {
          "text": "行内创建跟进",
          "action": "add_data",
          "target_app_key": "FOLLOWUP_APP_KEY",
          "field_mappings": [
            {"source_field": "数据ID", "target_field": "关联客户"}
          ],
          "default_values": {"跟进状态": "待跟进"},
          "placement": "list"
        },
        {
          "text": "详情创建跟进",
          "action": "add_data",
          "target_app_key": "FOLLOWUP_APP_KEY",
          "field_mappings": [
            {"source_field": "数据ID", "target_field": "关联客户"}
          ],
          "default_values": {"跟进状态": "待跟进"},
          "placement": "detail"
        }
      ]
    }
  ]
}
```

读回验证时，不要只看视图是否存在；要看 `verification.view_query_conditions_verified=true`。若返回 query condition mismatch，只能说视图已创建/更新，但查询条件未完全验证。

### 6.3 `visibility`

与包/应用/视图等 **授权形态一致**（契约 **`visibility.mode`**：`workspace` | `everyone` | `specific`；**`external_mode`**：`not` | `workspace` | `specific`；**`selectors` / `external_selectors`** 键集合见契约）。

- **更新已存在视图**：省略 **`visibility`** 可 **保留**当前后端权限。
- **名称类 selector**：须 **唯一解析**，否则失败（不猜测）。

### 6.4 `action_buttons`（主路径）

设计业务视图时，必须同时声明这个视图上的快捷按钮。常规按钮写在视图对象的 `action_buttons` 里，不要先建视图再单独找按钮工具补。新建核心业务视图必须至少包含一个 `placement: "list"` 按钮和一个 `placement: "detail"` 按钮；`header` 按钮可按需增加，但不能替代列表和详情按钮。

创建视图时：

```json
{
  "views": [
    {
      "operation": "upsert",
      "app_key": "APP_KEY",
      "name": "生产工单执行视图",
      "type": "table",
      "columns": ["工单编号", "产品", "状态", "负责人"],
      "filters": [
        {"field_name": "状态", "operator": "in", "values": ["生产中", "已完工"]}
      ],
      "query_conditions": {
        "enabled": true,
        "exact": false,
        "hide_before_query": false,
        "rows": [["工单编号", "状态"], ["负责人"]]
      },
      "action_buttons": [
        {
          "text": "行内创建质检单",
          "action": "add_data",
          "target_app_key": "QUALITY_APP",
          "field_mappings": [
            {"source_field": "数据ID", "target_field": "关联工单"}
          ],
          "default_values": {"处理状态": "待处理"},
          "placement": "list",
          "visible_when": [
            {"field_name": "状态", "operator": "eq", "value": "已完工"}
          ]
        },
        {
          "text": "详情创建返工单",
          "action": "add_data",
          "target_app_key": "REWORK_APP",
          "field_mappings": [
            {"source_field": "数据ID", "target_field": "关联工单"}
          ],
          "default_values": {"返工状态": "待处理"},
          "placement": "detail"
        }
      ]
    }
  ]
}
```

局部补按钮时：

```json
{
  "operation": "patch",
  "app_key": "APP_KEY",
  "view_key": "RAW_VIEW_KEY",
  "set": {
    "action_buttons": [
      {
        "text": "行内创建验收单",
        "action": "add_data",
        "target_app_key": "ARRIVAL_APP",
        "field_mappings": [
          {"source_field": "数据ID", "target_field": "关联工单"}
        ],
        "default_values": {"状态": "待验收"},
        "placement": "list"
      },
      {
        "text": "详情创建验收单",
        "action": "add_data",
        "target_app_key": "ARRIVAL_APP",
        "field_mappings": [
          {"source_field": "数据ID", "target_field": "关联工单"}
        ],
        "default_values": {"状态": "待验收"},
        "placement": "detail"
      }
    ],
    "action_buttons_mode": "merge"
  }
}
```

规则：

- `action_buttons_mode` 默认 `merge`：新增/更新声明按钮并绑定到该视图，不清空已有按钮。
- `replace`：替换该视图上的自定义按钮绑定；`action_buttons: []` + `action_buttons_mode: "replace"` 可清空视图按钮绑定，但不删除按钮本体。
- 新建核心业务视图时 `query_conditions` 和 `action_buttons` 都不能为空，并且按钮必须同时配置 `placement: "list"` 和 `placement: "detail"`。不要交付缺少查询面板或缺少列表/详情按钮的核心操作视图。
- `publish=false` + `action_buttons` 会被阻断为 `VIEW_ACTION_BUTTONS_REQUIRE_PUBLISH`。
- 视图内按钮写智能体语义：`action: "add_data"` 或 `action: "link"`。不要手写底层触发名。
- 响应里同时看 `verification.views_verified`、`verification.action_buttons_verified`、`verification.view_button_bindings_verified`。
- 按钮失败但视图成功时是 `partial_success`；先按 `suggested_next_call` 重试失败视图的 `views[]` patch。 如果回读里目标视图已有 `CUSTOM` 按钮、文本/位置/触发类型正确，不要重建视图或重复创建按钮。

`default_values` 是写入**目标应用新增表单**的静态默认值，必须按目标应用 schema 写：

- 写按钮前先确认 **`target_app_key` 对应应用**的字段与选项；优先用 `builder app get --app-key TARGET_APP fields` 看字段名/选项，必要时用 `record schema insert --app-key TARGET_APP` 看 insert-ready 写入格式。
- 单选/多选字段的默认值必须来自目标字段 `options` 的**原始文本或 option id**；不要用业务近义词。例如 schema 选项是 `每月`、`中`，就不要写 `月检`、`普通`。
- 成员/部门/关联字段默认值按 record insert 的写法处理；不确定候选或目标记录时，先只写 `field_mappings`，不要编造 `default_values`。
- `field_mappings[].target_field` 和 `default_values` 的 key 都是**目标应用字段名**，不是当前视图字段名。
- CLI 会在按钮写入前校验默认值；非法值会返回 `CUSTOM_BUTTON_DEFAULT_VALUE_UNSUPPORTED`。这时视图可能已经创建成功，只需要用 `views[].operation="patch"` + raw `view_key` 修正 `action_buttons.default_values`，不要重建视图或应用。

正确示例：

```json
"default_values": {
  "巡检周期": "每月",
  "优先级": "中",
  "隐患等级": "中"
}
```

按钮一眼决策表：先按**用户真实意图**选，不要先从按钮枚举反推业务。

| 用户真实意图 | 视图内 `action` | 推荐位置 | 必需配置 | 禁止误用 |
| --- | --- | --- | --- | --- |
| 从当前记录生成下游/关联记录，例如工单生成质检、订单生成到货、客户生成跟进 | `add_data` | `detail` 和 `list` 都要配置 | `target_app_key` + `field_mappings`，通常 `source_field: "数据ID"` 指向目标应用的关联/引用字段；`default_values` 必须按目标应用 schema/options 写 | 目标应用或关联字段不清楚时不要猜；不要放在 `header` 后又引用当前记录字段；不要编造选项近义词 |
| 创建不依赖当前行的独立记录或全局入口 | `add_data` | `header` | `target_app_key`；不要写当前记录 `source_field` | 不要假装有当前记录上下文 |
| 打开 SOP、外部系统、帮助文档、固定页面 | `link` | `header` 或 `detail` | `url` | 不要用它代替新增数据、审批、状态流转或数据写回 |
| 审批、通过、驳回、状态流转、关闭任务 | 默认不配普通按钮 | 先判断工作流/任务动作/已有自动化 | 用户明确要求普通按钮且能落到 `add_data` / `link` 时才配置 | 不要用 `link`、空按钮或伪 URL 假装完成 |

核心判断：**要把当前记录的数据带到另一个应用，就用 `add_data`；只打开页面就用 `link`；审批/状态流转不是普通按钮。**

按钮位置选择：

| `placement` | 前端位置 | 适合场景 | 注意事项 |
| --- | --- | --- | --- |
| `header` | 视图顶部 | 全局入口，不依赖当前行：打开说明、创建独立记录、批量入口 | 不能依赖当前记录的 `source_field` |
| `list` | 列表/行内 | 对当前行记录操作：从工单创建质检、从客户创建跟进 | 必须确认当前记录上下文可用于 `field_mappings` |
| `detail` | 记录详情页 | 当前记录上下文操作：创建子记录、查看外部详情、补充材料 | 最稳妥的上下文按钮位置 |

不同视图类型：

- `table`：必须配置 `list` 和 `detail` 快捷按钮，是最适合放业务按钮的视图。
- `board`：必须配置状态相关的 `list` 和 `detail` 快捷按钮，并配 `visible_when`，例如只在“待验收”显示“创建验收单”。
- `card`：必须配置 `detail`，并在卡片行操作明确时配置 `list`；核心操作视图不要只给 `header`。
- `gantt`：不适合作为唯一核心操作视图；需要快捷按钮时同时提供配套 table/board 视图，在该操作视图中配置 `list` 和 `detail`。

### 6.5 关联视图/报表

新版默认不要通过 `app_views_apply.associated_resources` 配置关联资源。应用级关联资源池和视图展示开关统一走 **`app_associated_resources_apply`** / CLI **`builder associated-resource apply`**。

- `builder views apply` **新建视图时默认开启详情页关联查看**：等价于 `asosChartVisible=true`、`limit_type=all`，会展示当前应用级关联资源池里的全部关联视图/报表。
- **更新已有视图**：未显式传 `associated_resources` 时保留原关联查看状态；需要关闭或改成指定资源时，用 **`builder associated-resource apply --view-configs-file`**，或维护旧配置时显式 patch `associated_resources`。
- 已有资源的最终口径是 `app_get.associated_resources[].associated_item_id`；它不是 `chart_id`、`chart_key` 或 `view_key`。
- 新版 CLI 在关联报表时可先传 `chart_id` / `chart_key`，内部会解析为轻流后端需要的 id；创建前先检查是否已有相同 `target_app_key + view_key/chart_key`，已存在时用 `patch_resources`；`client_key` 只在同一次 apply 中可被 `associated_item_refs` 引用，不会持久化。
- 数据集 BI 报表只能关联已有报表，使用 `report_source: "dataset"`；应用源报表可先用 `builder charts apply` 创建/更新。
- 关联筛选优先用 `match_mappings`；字段类型、`operator`、`value/values` 和跨应用当前记录匹配规则见 **[reference/match-rules.md](./reference/match-rules.md)**。

---

## 7. 删除视图

- 主路径使用 `views[].operation="remove"`；元素必须带 `app_key`，优先带 raw **`view_key`**，也可以带唯一视图显示名。
- 优先用 **`view_key`** 删除；显示名重名会导致 **`AMBIGUOUS_VIEW`**，需先在 **`app get views`** 里确认。
- DELETE 发出后，工具会用单个 **`view_key`** 回读验证，而不是再读全量视图列表判断删除结果。
- 删除结果看 **`verification.by_view[].delete_executed`**、**`readback_status`**、**`safe_to_retry_delete`**：
  - **`readback_status=deleted`**：删除已验证。
  - **`readback_status=unavailable`** 或 **`still_exists`**：删除请求已发出但回读未完全确认，**不要盲目重复删除**；稍后用 `builder app get views` 或对应视图详情确认。

---

## 8. 契约示例（可复制为文件基底）

**Table + `visibility`（`minimal_example` 节选）**：

```json
{
  "views": [
    {
      "operation": "upsert",
      "app_key": "APP_KEY",
      "name": "项目台账视图",
      "type": "table",
      "columns": ["项目名称"],
      "visibility": {
        "mode": "workspace",
        "selectors": {},
        "external_mode": "not",
        "external_selectors": {}
      }
    }
  ]
}
```

**Gantt（`gantt_example` 节选）**：

```json
{
  "views": [
    {
      "operation": "upsert",
      "app_key": "APP_KEY",
      "name": "项目甘特图",
      "type": "gantt",
      "columns": ["项目名称", "开始日期", "结束日期"],
      "start_field": "开始日期",
      "end_field": "结束日期",
      "title_field": "项目名称",
      "filters": [
        {
          "field_name": "状态",
          "operator": "eq",
          "value": "进行中"
        }
      ]
    }
  ]
}
```

**Table + 筛选 + 查询条件 + 快捷按钮（完整 views-file）**：

```json
{
  "views": [
    {
      "operation": "upsert",
      "app_key": "APP_KEY",
      "name": "客户查询视图",
      "type": "table",
      "columns": ["客户名称", "负责人", "客户状态", "创建时间"],
      "filters": [
        {"field_name": "客户状态", "operator": "eq", "value": "有效"}
      ],
      "query_conditions": {
        "enabled": true,
        "exact": false,
        "hide_before_query": false,
        "rows": [["客户名称", "负责人"], ["创建时间"]]
      },
      "action_buttons": [
        {
          "text": "行内创建跟进",
          "action": "add_data",
          "target_app_key": "FOLLOWUP_APP_KEY",
          "field_mappings": [
            {"source_field": "数据ID", "target_field": "关联客户"}
          ],
          "default_values": {"跟进状态": "待跟进"},
          "placement": "list"
        },
        {
          "text": "详情创建跟进",
          "action": "add_data",
          "target_app_key": "FOLLOWUP_APP_KEY",
          "field_mappings": [
            {"source_field": "数据ID", "target_field": "关联客户"}
          ],
          "default_values": {"跟进状态": "待跟进"},
          "placement": "detail"
        }
      ]
    }
  ]
}
```

---

## 9. 实测记录（`ead8ims5i401`，`--publish`）

内容与仓库 **[views_upsert_table_minimal.example.json](../examples/views/views_upsert_table_minimal.example.json)** 一致（或历史探针名 **`CLI探针视图_可删`**）。

**读视图**：

```bash
qingflow --json builder app get --app-key ead8ims5i401 views
```

**应用**：

```bash
qingflow builder views apply \
  --publish \
  --views-file ./reference/examples/views/views_upsert_table_minimal.example.json
```

**结果摘要**（示例视图名 **`示例业务操作视图_CLI模板`**）：`status: success`，`verification.by_view[0].status: created`，返回 **`view_key`**（如 **`ecdk22v65c02`**），并验证 `query_conditions` 与 `action_buttons`。

---

## 10. 排障要点

| 现象 | 处理 |
|------|------|
| 列校验失败 / 无有效业务列 | **`app get fields`** 核对 **`name`**；避免 `columns` 仅含 **§7.1 系统列** |
| 重名视图 / 删错 | **`app get views`**；更新时带 **`view_key`** |
| 过滤器未生效疑虑 | 看响应 **`verification.view_filters_verified`**；必要时再 **`app get views`** |
| 查询条件未生效疑虑 | 看响应 **`verification.view_query_conditions_verified`**；不要把 `query_conditions` 当 `filters` |
| 后端 **40038 / Object not exist** | 先读失败项 **`details.per_view_results[].details.field_level_diagnostics`** 与 **`recommended_minimal_retry`**。不要删除字段、不要重建应用；先按最小列重试，再逐步加非关键列/筛选。 |
| 按钮/关联资源配置 | 常规业务按钮随视图写 **`action_buttons`**；关联视图/报表走 **`builder associated-resource apply`** |
| 部分失败 | 读 **`views_diff.failed`** 与契约 **execution_notes** 中 **partial_success** |
| 权限/锁 | 同 [publish verify](./99-publish-verify.md) 与 [app delivery reference](./reference/app-delivery-sop.md) |

---

## 11. 交叉引用

- [views_upsert_table_minimal.example.json](../examples/views/views_upsert_table_minimal.example.json)（**table** 视图最小 **`views[]`**）
- [SKILL.md](../../SKILL.md)：builder 直接输出、鉴权顺序。
- [99-publish-verify.md](./99-publish-verify.md)：发布与回读。
- [reference/app-delivery-sop.md](./reference/app-delivery-sop.md)：系统列与历史交付细节。
- [QINGFLOW_CLI_EXPLORATION_REPORT.md](../core/QINGFLOW_CLI_EXPLORATION_REPORT.md)：CLI 覆盖与 **`view_id` vs `view_key`** 备忘。
