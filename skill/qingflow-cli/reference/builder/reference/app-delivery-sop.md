# Builder 应用交付重流程 SOP：分组 → 应用定位 → 读场 → 改场 → 发布校验

本文是历史低层交付备忘，不是当前表单写入 SOP。稳定 CLI 公开入口仍为 `qingflow builder` / `qingflow build`，但表单字段、分组、布局和设置必须使用 `qingflow --json builder app-form schema/get/validate/apply`，应用删除使用 `qingflow --json builder app delete --app-key APP_KEY`；本文件中的 `app_schema_apply` / `app_layout_apply` / `builder schema apply` / `builder layout apply` 只用于识别旧载荷和迁移，不得直接调用。

> **权限**：应用基础信息（`app_name` / 图标 / 可见性）、表单、流程、自定义按钮本体、应用级关联资源池走 **应用搭建 / EditAppAuth**；视图更新/删除、按钮的视图位置配置（`view_configs`）和视图内关联资源展示配置走 **视图管理 / ViewManagementAuth**（后端 `beingViewManageStatus`；未开启高级应用权限时等价回落到 DataManageAuth）；**新建视图**额外需要 **DataManageAuth**；报表走 **数据管理 / DataManageAuth**。失败码常见 **40002 / 40161 / 编辑锁** 等，见主技能与 **ADMIN** 速查。

> **契约**：当前表单契约固定通过 `qingflow --json builder app-form schema` 获取；其它公开 `app_*_apply` 仅是 `builder contract --tool-name` 的参数值，**不是可执行 CLI 子命令**。其 **`allowed_keys` / `allowed_values` / `execution_notes` / 示例** 以在线契约为准，命令：
> `qingflow --json builder contract --tool-name <app_flow_apply|app_views_apply|app_custom_buttons_apply|app_associated_resources_apply|app_publish_verify>`
>
> **CLI 文件载荷注意**：契约示例里可能出现 `"profile": "default"`，那是请求上下文示例；使用 CLI 的 `--*-file` 时不要把 `profile` 写进 JSON 文件。需要指定账号上下文时用根级参数：`qingflow --profile default ...`。
>
> **输出口径**：builder 读取命令仍显式加 `--json`；builder 写入/apply 命令默认直接输出 JSON 到 stdout，写入/apply 示例不再额外加 `--json`。如果需要留档，用 `| tee tmp/builder_*.json`，不要用 `>` 吞掉前端可捕获的 stdout。写入结果优先读统一 envelope：`operation` 表示本次动作，`summary` 表示总数/成功失败/发布校验，`resources[]` 表示资源卡片；每个资源统一有 `resource_type`、`operation`、`status`、`id`、`key`、`name`、`ids`、`parent`、`error_code`、`message`。旧字段如 `field_diff`、`views_diff`、`chart_results` 只作兼容和排障。
>
> **写后回读**：若 builder 写入结果为 `status=partial_success`，但同时有 `write_executed=true` / `safe_to_retry=false`，表示写动作已执行或可能已执行，问题在最终回读、发布校验或元数据确认。`package apply/update`、`schema apply`、`portal apply` 常见这种形态：`verification.readback_unavailable=true`、`details.*readback_error.backend_code=40002`、命令超时或响应只包含 partial/readback 不完整，都不等于写失败；下一步固定是 **`readback_before_retry`**，最终对用户应说明“写入已执行，回读待确认”，不要重复提交同一写动作。
> 旧的 solution/build 编排同样遵循该语义：包挂载、门户更新或门户发布之后，若只剩回读 40002，会以 `partial_success` 和 artifacts 中的 `readback_status=unavailable` 表达，不应盲目重放写动作。

---

## 1. 推荐阶段顺序（与工具名对齐）

| 阶段 | 目标资源 | 稳定 CLI（有则列出） | 作用 |
|------|------------------|----------------------|------|
| A | **`package_list`** | `qingflow --json builder package list [--query <关键词>]` | 列出当前 Builder 权限可见的应用包，返回 **`package_id/package_name`**、包权限和应用数量 |
| A′ | **`package_resolve`** | 不再作为 CLI 默认入口；用 `package list --query` 后人工/智能体确认 `package_id` | 同名包、空包都以 `package_list` 返回为准 |
| B | — | `qingflow builder package get --package-id <N>` | 已知 **数字 `package-id`**（即 `tag_id`）时读包详情 / 配置上下文 |
| C | **`app_resolve`** | `qingflow builder app resolve --app-key …` **或** `--app-name … --package-id …` | 在包内按名解析应用，或按 **`app_key`** 校验存在性 |
| D | **`app_get` / `app_get_fields`** | `qingflow --json builder app get --app-key <APP_KEY>` / `qingflow --json builder app get --app-key <APP_KEY> fields` | 默认 `app_get` 是应用地图，含字段摘要、视图、图表、自定义按钮和关联资源池；`fields` 只读表单可搭建字段 |
| D | **`app_read_layout_summary`** | `qingflow --json builder app get --app-key <APP_KEY> layout` | 读 **布局**（段落、`rows` 字段名矩阵、`unplaced_fields`） |
| D | **`app_read_flow_summary`** | `qingflow --json builder app get --app-key <APP_KEY> flow` | 读 **流程**是否启用、节点摘要（公开面能力有限） |
| E | **AppForm** | `qingflow --json builder app-form validate --schema-version VERSION --file DECLARATION.json` -> `qingflow --json builder app-form apply --file DECLARATION.json` | 完整 AppForm：字段、分组、行、设置和应用创建/更新 |
| F | — | 由 AppForm 的 `body` 一并维护 | 表单段落 / 行 / 单元格随完整声明提交 |
| G | **`app_flow_apply`** | `qingflow builder flow apply …` | **线性流程** 节点与转移（见契约限制） |
| G′（维护） | **`app_custom_buttons_apply`** | `qingflow builder button apply …` | 仅用于用户明确要求维护已有独立按钮：样式/图标、跨视图复用、删除按钮本体或批量重排 |
| G″ | **`app_associated_resources_apply`** | `qingflow builder associated-resource apply …` | 管理应用级关联视图/报表池，并配置视图详情侧边栏展示 |
| H | **`app_publish_verify`** | `qingflow builder publish verify --app-key …` | 确认 **已发布**、包挂载、视图等校验位 |

**说明**：普通业务按钮不作为独立交付步骤；新建或修改业务视图时写在 **`builder views apply`** 的 **`action_buttons`** 内。**`app_charts_apply`**（CLI **`builder charts apply`**）不在上表骨架内，但同属交付闭环；详见 **[60-charts.md](../60-charts.md)**；**视图**、**门户** 见同目录另文；其余另读 **`builder contract --tool-name …`**。`app_custom_buttons_apply` 与 `app_associated_resources_apply` 有成功写入时会自动发布，不暴露 draft-only `publish` 参数。

### 1.1 批量读、批量写、局部改归位

这些不是独立流程，而是读、写、改三个动作的多资源形态：

- **批量读**：读多个应用时优先用 `--app-keys`，例如 `builder app get --app-keys a,b fields`、`builder app get --app-keys a,b views`、`builder button get --app-keys a,b`、`builder associated-resource get --app-keys a,b`、`builder publish verify --app-keys a,b`。读结果同时看成功项和 `errors[]`，不要因单个应用失败否定全批。
- **批量写**：视图、按钮、关联资源和报表按各自资源契约使用对应的批量文件；应用表单不走 `apps-file`，而是每个应用独立提交完整 AppForm 声明。
- **局部改**：只改已存在资源的少量参数时用对应 patch 文件；`patch_*` 内只写目标定位字段和 `set/unset`，不要用不完整 `upsert_*` 伪装局部更新。

---

## 2. 分组阶段：`builder package list` → `builder package get`

默认使用应用包后端列表，不再从 `app list` 曲线推断：

```bash
qingflow --json builder package list --query "产品研发"
```

读取返回：

- `items[].package_id`：后续 `package get` / 新建应用挂包要用的数字 ID。
- `items[].package_name`：展示名；可能重名，不能单独当唯一键。
- `items[].item_count`：包内应用/门户/分组数量摘要，空包也能显示。
- `items[].permissions`：当前账号对该包的可操作权限。
- `matched_count / unfiltered_count / filter_mode`：判断关键词过滤结果。

然后读详情：

```bash
qingflow --json builder package get --package-id <package_id>
```

需要创建新应用包时，`package apply` 的 config 直接写业务字段即可：

```json
{
  "package_name": "生产管理",
  "icon": "factory",
  "color": "blue"
}
```

`package_name` 且无 `package_id` 就是创建语义。

**不要**用 `app list` 代替 `package list`：`app list` 只代表当前用户可见应用，不能代表空包、同名包、包级权限或完整包结构。

### 2.1 仅有 **`app_key`**（无包名场景）

若已知道任意挂载在该包下的应用：**直接**
`qingflow --json builder app resolve --app-key "<APP_KEY>"` → **`package_ids`**。
（与 **`publish verify`** 回包里的 **`package_ids_after`** 可交叉核对。）

### 2.2 限制（务必读）

| 情况 | 说明 |
|------|------|
| **同名多包** | `package list --query` 可能返回多个同名包；必须用 `package_id/item_count/permissions` 继续确认。 |
| **无权限** | 后端 40002 会返回 `PACKAGE_LIST_FAILED`；不要自动改用 `app list`，那会改变权限口径。 |
| **关键词未命中** | 看 `matched_count=0` 和 `unfiltered_count`；必要时去掉 query 获取全包列表。 |

### 2.3 旧版 CLI fallback

如果所在环境仍没有 `qingflow builder package list`，才使用 `scripts/builder-package-from-app-list.py` 从 `app list` 曲线临时解析。该 fallback 不能覆盖空包、同名包和包级权限，只用于旧版 CLI 迁移期。

---

## 3. 应用定位与 AppForm 创建

### 3.1 `app_resolve`（CLI）

```bash
# 模式 1：已有 app_key（推荐自动化）
qingflow --json builder app resolve --app-key "<APP_KEY>"

# 模式 2：包内按应用显示名查找（须同时给 package-id）
qingflow --json builder app resolve \
  --app-name "我的应用" \
  --package-id 2030703
```

- **勿混用**：`--app-key` 与（`--app-name` 或 `--package-id`）**不能同时出现**；只能二选一模式（见 `builder.py` 校验）。

### 3.2 单应用新建（历史 `app_schema_apply` 迁移说明）

当前新建和更新请使用 `qingflow --json builder app-form schema/get/validate/apply`；下方旧命令仅用于迁移脚本识别，不能执行。

历史脚本可能先读取图标候选；当前 AppForm 新建同样先读取并固定合法图标和颜色：

```bash
qingflow --json builder icon catalog
```

```bash
qingflow builder schema apply \
  --package-id <TAG_ID> \
  --app-name "新应用显示名" \
  --icon <非 template 图标名> \
  --color <图标颜色> \
  [--app-title …] \
  [--visibility-file tmp/visibility.json] \
  [--publish | --no-publish] \
  [--add-fields-file tmp/add_fields.json] \
  ...
```

上面的 `builder schema apply` 示例是 retired 命令，当前 CLI parser 不接受；这里只保留参数形状供迁移脚本定位。

- **`--icon` / `--color`**：取值以 `builder contract --tool-name app_schema_apply` / 当前 CLI 契约候选为准；不要自造 `sales-*`、`crm-*` 等业务语义 key。契约未返回候选值时省略该参数，不要猜测写入。

- **单应用创建模式要件**（与契约一致）：**`package_id` + `app_name`**（或 CLI 的 app-title 映射到 app_name）。
- **图标必填**：创建应用必须显式传合法的 **`icon + color`**；不要用 `template`。CLI 只校验候选，不根据应用名称自动猜图标。多应用批量创建时，每个新应用应使用不同 `icon`。
- **数据标题必填**：旧载荷使用 `as_data_title` / `as_data_cover`；当前 AppForm 对应 `dataTitle` / `dataCover`，并要求最终表单只有一个顶层标题字段。
- **编辑模式**：**仅** **`--app-key`**（可选改名 `--app-name`），**不要**与 `package_id` 混用。

### 3.3 多应用一次性新建（历史 multi-app 迁移说明）

本节下方的 `--apps-file` 示例是旧 CLI 载荷，仅用于识别/迁移历史脚本；当前完整系统应逐个创建 AppForm，记录返回的 `appKey` 后再绑定关系。

旧版本允许用一个 `apps-file` 同批创建多个业务对象。当前版本不再公开该入口；完整系统应先分别创建无关系 AppForm，记录每个返回的 `appKey`，再用完整 AppForm 声明补充关系字段。以下内容只用于识别和迁移旧脚本：

```bash
qingflow builder schema apply \
  --apps-file tmp/apps.json
```

`apps.json` 中的 `package_id`、`client_key`、`app_name`、`add_fields` 和 `target_app_ref` 都是旧 snake_case 载荷键，不得改作当前 AppForm 示例：

```json
{
  "package_id": 123,
  "apps": [
    {
      "client_key": "employee",
      "app_name": "员工花名册",
      "icon": "business-personalcard",
      "color": "emerald",
      "add_fields": [
        {"name": "员工名称", "type": "text", "as_data_title": true}
      ]
    },
    {
      "client_key": "worklog",
      "app_name": "工时表",
      "icon": "clock",
      "color": "blue",
      "add_fields": [
        {"name": "工时标题", "type": "text", "as_data_title": true},
        {
          "name": "关联员工",
          "type": "relation",
          "target_app_ref": "employee",
          "display_field": {"name": "员工名称"},
          "visible_fields": [{"name": "员工名称"}]
        }
      ]
    }
  ]
}
```

- 返回里看 `mode=multi_app`、`apps[].app_key`、`created_app_keys` 和 `apps[].status`。
- 如果 CLI 看到 `[{ "package_id": 123, "apps": [...] }]`，会自动展开并返回 `APPS_FILE_WRAPPER_ARRAY_UNWRAPPED` warning；这是兼容路径，后续仍应改回对象形态。
- 如果返回 `MULTI_APP_STATIC_VALIDATION_FAILED`，读取 `details.issues[]` 的 `path/error_code/fix_hint` 修 payload；这是写入前失败，通常可以修正后重试，不需要 readback。
- 多应用 schema apply 不做事务回滚；如果部分失败，只补失败的 `apps[].row_number`，不要整批重复提交。
- 这个模式只负责应用壳与字段；视图、按钮、关联资源、报表仍拿返回的 `app_key` 继续走各自 apply 工具。
- `target_app_ref`、`as_data_title`、`display_field` 等只属于旧载荷。迁移时将关系改写为 AppForm `config.targetAppKey`、`config.displayField`、`config.visibleFields`，并使用已确认的真实 app key。
- 历史 schema adapter 写入后可读 `details.relation_readback_matrix[]`：逐项核对旧 `target_app_key`、`relation_mode`、`display_field`、`visible_fields`。迁移到当前 AppForm 后，改为读取 draft/published form 的 `config.targetAppKey`、`config.relationMode`、`config.displayField`、`config.visibleFields`，不要提交旧 `update_fields` patch。
- 一个应用可以包含多个 `relation` 字段；不要因为 relation 数量超过 1 就降级成文本。若真实写入失败或 relation readback mismatch，只按实际错误和 `details.relation_repair_plan[]` 做最小修复。
- 完整系统遇到超时、`partial_success`、`write_executed=true`、`safe_to_retry=false` 或 readback 不完整时，先按 §3.4 读回，不要直接拆成单应用创建。

### 3.4 多应用 schema apply 超时 / partial / readback 不完整恢复

触发条件：shell/MCP 超时、响应被截断、`status=partial_success`、`write_executed=true`、`safe_to_retry=false`、`verification.readback_unavailable=true`、`created_app_keys` 不完整，或只拿到部分 `apps[].status`。

统一判定：

- 这不是“创建失败”的证据，而是 **`write_may_have_succeeded`**。
- 下一步固定为 **`next_action: readback_before_retry`**。
- 在 readback 完成前，不得重放整份 `apps-file`，不得把完整系统拆成多次单应用重建，不得创建 `V2` / `测试` / 随机后缀应用绕过重名。

读回顺序：

1. 已知 `package_id` 时先 `qingflow --json builder package get --package-id <TAG_ID>`，确认包仍可读、包内已有应用摘要。
2. 对每个计划内 `apps[].app_name`，用 `builder app resolve --app-name <NAME> --package-id <TAG_ID>` 定位；若响应已经给出 `apps[].app_key` / `created_app_keys`，优先用这些 key。
3. 对已定位应用执行 `builder app get --app-key <APP_KEY> fields`，核对标题字段、关键业务字段、relation 字段的 `target_app_key` / 显示字段。
4. 形成矩阵：`created_and_verified`、`created_but_readback_incomplete`、`missing`、`field_or_relation_missing`、`failed_with_error`。
5. 只有读回证明某个应用确实不存在或某个字段确实缺失时，才做最小修复：补缺失 app 行、补缺失字段或修 relation；不要重跑已经存在的应用。

重试/修复限制：

- 继续使用原始 `app_name` 与业务命名。重名冲突表示需要读回/更新/询问用户，不是创建 `V2` 的理由。
- 迁移到当前 AppForm 后，不再继续补发 `client_key + target_app_ref`；先确认每个实际 `appKey`，再提交完整声明和 `config.targetAppKey`。
- 若 readback 证明主应用已存在但部分 relation 缺失，修 relation 前先说明数据影响：是否会清空已有值、是否需要迁移、是否可安全重试。
- 如果已有包内已经存在相似应用，先决定“复用/更新/新建缺失应用/询问用户”，不要用相似重名或后缀绕开。

**`visibility` JSON**（`--visibility-file`）：与包/应用通用，键见契约 `$.contract.allowed_values["visibility.*"]`：

- **`mode`**：`workspace` | `everyone` | `specific`（`specific` 须 **`selectors`**：`member_uids` / `member_emails` / `member_names` / `dept_ids` / `dept_names` / `role_ids` / `role_names` / `include_sub_departs`）。
- **`external_mode`**：`not` | `workspace` | `specific`，与对外可见性独立；**`mode=everyone`** 时行为见契约 **execution_notes**。

---

## 4. 读场三口：`app_read_*`（CLI `builder app get`）

```bash
qingflow --json builder app get --app-key "<APP_KEY>"
qingflow --json builder app get --app-key "<APP_KEY>" fields
qingflow --json builder app get --app-key "<APP_KEY>" layout
qingflow --json builder app get --app-key "<APP_KEY>" flow
# 另有 summary（默认）| views | charts
```

- **`app get` 默认摘要**：应用地图入口，包含 compact `views`、`charts`、`custom_buttons`、`associated_resources`。需要完整配置时再调用具体 `fields/layout/views/flow/charts` 或 `view get/chart get`。
- **`fields`**：每项含 **`que_id`**、**`name`**、**`type`**（字符串枚举）、**`required`**、**`section_id`**（含子表 **`subfields`**、关联 **`target_app_key`** 等）。用于 **`update_fields` / `remove_fields` 的 selector**。
- **`layout`**：**`sections[]`**（`type: paragraph`、`rows: [[字段名, …], …]`）、**`unplaced_fields`**、**`layout_mode_detected`**；可能出现 **`LAYOUT_SUMMARY_UNVERIFIED`** 警告。
- **`flow`**：**`enabled`**、**`nodes`** 摘要；契约提示 **分支/条件** 在公开工具面受限，验证仅覆盖 **线性** 结构。

**实跑摘录**（`ead8ims5i401`）：`field_count=7`；`layout` 1 个 section、`unplaced_fields` 空；`flow` `enabled=true`、`nodes` 数 1。

---

## 5. 改场三口（历史 schema/layout 迁移说明 + 当前 flow）

`app_schema_apply` / `app_layout_apply` 已从公开 MCP/CLI surface 移除。下方 schema/layout 命令只用于迁移旧脚本；当前表单和布局必须使用 `qingflow --json builder app-form schema/get/validate/apply`。

### 5.1 历史字段载荷：`builder schema apply`（仅迁移识别）

以下示例是 retired `add_fields` 载荷，不能执行；当前字段新增请回到 AppForm 完整声明。

```bash
qingflow builder schema apply \
  --app-key "<APP_KEY>" \
  --no-publish \
  --add-fields-file ./reference/examples/schema/schema_add_fields_minimal.example.json
```
（路径以 `qingflow-cli/` 技能根目录为基准；执行时可解析为该技能目录下的实际文件。）

- **`name`** 须为当前应用内 **唯一** 的控件显示名；若报重名，改 **`示例搭建_CLI单行`** 后再执行。
- 本文件只记录旧 `app_schema_apply` 的 `add_fields` 形状，供迁移脚本识别；当前新建和字段维护均回到完整 AppForm 声明。

```bash
qingflow builder schema apply \
  --app-key "<APP_KEY>" \
  [--publish | --no-publish] \
  [--add-fields-file tmp/add.json] \
  [--update-fields-file tmp/update.json] \
  [--remove-fields-file tmp/remove.json]
```

- **`--publish` / `--no-publish`**：默认发布；`--no-publish` 仅草稿/预检语义（见 `server_app_builder` 总述：**schema/layout/views/flow** 的 noop 与发布关系以契约为准）。
- **文件体形状**：旧契约的顶层 **`add_fields` / `update_fields` / `remove_fields`** 数组；当前 CLI 不接受该形状。
- **标题/封面**：旧字段标记 `as_data_title` / `as_data_cover` 迁移为 AppForm 的 `dataTitle` / `dataCover`。
- **本仓实测**（`ead8ims5i401`，`--no-publish`，`name` 改为未存在过的 **`CLI搭建探针字段_可删`**）：`field_diff.added` 成功；同一 **`name`** 不可重复添加，后续请改用 **[schema_add_fields_minimal.example.json](../../examples/schema/schema_add_fields_minimal.example.json)** 内模板名或自改唯一名。

### 5.2 历史布局载荷：`builder layout apply`（仅迁移识别，不可执行）

```bash
qingflow builder layout apply \
  --app-key "<APP_KEY>" \
  --mode merge \
  [--publish | --no-publish] \
  --sections-file tmp/sections.json
```

- **`mode`**：旧载荷中的 `merge`（默认）或 `replace`；当前 AppForm 不使用该局部模式，必须提交完整 `spec.body`。
- **`sections` JSON**：数组，元素形状见契约 **`minimal_example`**：`type: paragraph`、`paragraph_id`、`title`、`rows: [[列标题…], …]`，单元格值为 **字段显示名 `name`**（与 `app_get_fields` 一致）。

### 5.3 流程：`builder flow apply`

流程前置条件：

- 审批 / 填写 / 抄送类流程需要一个显式业务状态字段；当前 AppForm 应在 schema 阶段先建 `single_select` 字段并设置 `config.options`，例如 `状态`、`处理状态`、`审批状态`、`工单状态` 或 `流程阶段`。历史 schema adapter 里的 `select` 仅用于迁移识别。
- 不要创建平台流程系统字段：`当前流程状态`、`当前处理人`、`当前处理节点`、`流程标题`。这些只能由平台维护。
- 如果返回 `FLOW_DEPENDENCY_MISSING`，先执行返回的 `suggested_next_call` 补业务状态字段，再 `builder app get fields` 回读，然后重跑 flow apply；不要跳过流程后报告“流程完成”。

```bash
qingflow builder flow apply \
  --app-key "<APP_KEY>" \
  [--publish | --no-publish] \
  --spec-file tmp/flow_spec.json
```

- 公开智能体链路只使用 WorkflowSpec `--spec-file` 或已有节点 `--patch-nodes-file`。

---

## 6. 字段类型迁移对照（旧 `app_schema_apply` 载荷）

以下内容只帮助迁移旧载荷；当前字段类型、camelCase 配置和必填项以固定版本的 `qingflow --json builder app-form schema` 返回结果为准。

智能体可优先写更自然的字段类型，工具会在写入前归一化；读回仍显示 canonical 类型：

| 智能体写法 | 内部类型 |
|------------|----------|
| `multiline` / `multiline_text` / `textarea` | `long_text` |
| `select` / `single_choice` / `dropdown` | `single_select` |
| `multi_select` / `multi_choice` / `multiple_choice` / `checkbox` | `multi_select` |

| `type` | 设置要点 |
|--------|----------|
| **`text`** | **`name`**；可选 **`required`**、**`description`**；无选项。 |
| **`long_text`** | 同上。 |
| **`number`** | 同上；比例、完成率、评分、数量、时长、百分比等可能出现小数或非货币数值时优先用它。 |
| **`amount`** | 同上；只用于货币/金额语义，不要把百分比、完成率、成本执行率等业务比例建成 `amount`。 |
| **`date`** | 同上。 |
| **`datetime`** | 同上。 |
| **`member`** | **`name`**、**`required`**；成员选择器，无额外 scope 键（与 **department** 不同）。 |
| **`department`** | 旧载荷使用 **`department_scope`**；当前 AppForm 使用 `config.departmentScope`，具体形状以 pinned schema 为准。 |
| **`single_select`** / **`multi_select`** | 当前 AppForm 使用 `config.options` 字符串数组；对象数组和裸 `options` 仅属于旧兼容载荷。 |
| **`phone`** / **`email`** | 标准校验类字段，**`name` + required**。 |
| **`address`** | 地址复合字段。 |
| **`attachment`** | 附件。 |
| **`boolean`** | 是否。 |
| **`relation`** | 旧载荷使用 `target_app_key` / `target_app_ref`；当前 AppForm 使用 `config.targetAppKey`、`config.relationMode`、`config.displayField`、`config.visibleFields`。 |
| **`subtable`** | 当前 AppForm 使用 `subfields[]` 及 Schema 返回的 camelCase 配置；旧 `subfield_updates` 只作迁移线索。 |
| **`q_linker`** | 当前 AppForm 使用 `config.qLinkerBinding`，其 `outputs[].targetField` 必须按字段 Schema 配置。 |
| **`code_block`** | 当前 AppForm 使用 `config.codeBlockBinding`，其 `outputs[].targetField` 必须按字段 Schema 配置。 |

### 6.1 数据标题与数据封面

- 旧载荷的 `as_data_title` / `as_data_cover` 分别迁移为 AppForm 字段的 `dataTitle` / `dataCover`。最终表单必须有且仅有一个顶层可读标题字段；封面只能用于一个顶层 `attachment` 字段。
- 子表子字段不能作为标题或封面；多标题、多封面、非附件封面都会在写入前阻断。
- 未显式标记封面时保留/不创建封面；未能形成唯一标题时视为配置错误，不要声称应用已完整创建。

**迁移提示**：旧契约中的 `aliases`、`field.type_id` 和 snake_case 配置不能替代当前 AppForm Schema。主路径以 pinned schema 的 camelCase 字段和类型详情为准。

**`update_fields` 项**：**`selector`**：`que_id` 或 `field_id` 或 **`name`**；**`set`**：允许子集（**`name` / `required` / `description` / `options` / `department_scope` / … / `subfield_updates`**）。

**`remove_fields` 项**：**`que_id` / `field_id` / `name`** 之一。

**当前 21 种字段类型与 canonical 形状**：见 **[30-schema-fields.md](../30-schema-fields.md)**，以 pinned AppForm Schema 为准。下面的 `add_fields` 文件只是历史字段能力探针，不是正式新建应用主模板：[schema_apply_add_fields_all_types.json](../../examples/schema/schema_apply_add_fields_all_types.json)。

---

### 6.2 局部参数更新规则（patch vs upsert）

后端很多保存接口仍是整份配置保存，但新版 CLI/MCP 对外提供 **public partial patch**：

- 已有视图：`builder views apply --views-file`，其中对应项写 `operation: "patch"`
- 已有按钮：`builder button apply --patch-buttons-file`
- 已有关联资源：`builder associated-resource apply --patch-resources-file`
- 已有报表：`builder charts apply --patch-file`
- 已有流程节点：`builder flow apply --patch-nodes-file`
- 已有门户组件：`builder portal apply --patch-sections-file`

局部更新的语义是：你只写要替换的参数，工具内部读取当前配置、补齐后端必填字段，再整份保存。每个 patch 项直接使用对象真实定位字段 + `set` / 可选 `unset`，不要写字面量 `selector` key。示例：`{"operation":"patch","app_key":"APP_KEY","view_key":"VIEW_KEY","set":{"query_conditions":{...}}}`、`{"button_id": 1001, "set": {"button_text": "新名称"}}`、`{"associated_item_id": 123, "set": {"match_mappings": [...]}}`、`{"chart_id": 456, "set": {"name": "新报表名"}}`、`{"id": "node_1", "set": {"name": "主管审批"}}`、`{"chart": {"chart_key": "xxx"}, "set": {"rows": 7}}`。

`upsert_*` 用于创建或提供完整目标配置；不要只给 `name/type/query_conditions` 这类局部片段然后期待后端自动合并。

---

## 7. 系统字段与视图系统列（必读）

### 7.1 平台系统字段 / 视图系统列（不可当普通字段去 `add_fields` / 录入）

平台会自动生成或维护这些系统字段 / 系统列，不要在创建表单时手工造同名控件，也不要在录入数据时写入：

**`数据ID`**、**`编号`**、**`申请人`**、**`申请时间`**、**`创建人`**、**`创建时间`**、**`提交人`**、**`提交时间`**、**`更新时间`**、**`更新人`**、**`当前流程状态`**、**`当前处理人`**、**`当前处理节点`**、**`流程标题`**。

- **含义**：这些是平台维护的系统信息，**不要**在 **`add_fields`** 里手工造同名控件来「模拟」，也不要写进 `record insert` 的 `fields` / `items[].fields`。
- **视图列例外**：`builder views apply` 对部分系统列名会过滤并警告（`ignored_system_columns`）；新建/更新业务视图至少要包含一个真实业务字段。
- **与 `app_get_fields` 的关系**：读回 **`fields[]`** 侧重 **表单搭建字段**；**编号 / 申请人** 等可能不会作为普通 `type` 出现在列表中（视应用模板与工作流是否开启），**以读回 JSON 为准**。交付时 **业务字段** 用 **`app_get_fields`**；**系统列** 由平台在 **数据列表 / 视图** 侧展示。

### 7.2 布局 / 流程中的「系统行为」

- **布局**：仅摆放 **`app_get_fields`** 里出现的 **`name`**；不要把上表系统列名放进 **`rows`** 除非读回确认存在对应可摆放控件。
- **流程**：WorkflowSpec 中的字段权限、条件和自动化映射须引用 **真实业务字段名 / 字段 id**（先读 `fields` 与 `builder flow schema`）。流程需要状态时，创建业务字段 `状态` / `处理状态` 等，不创建平台字段 `当前流程状态`。

---

## 8. 按钮维护与关联资源

### 8.1 独立按钮维护：`app_custom_buttons_apply`

普通业务按钮只随视图写 `builder views apply` 的 `action_buttons`；不要把 `builder button apply` 当成系统搭建主流程。只有用户明确要求维护已有独立按钮，例如自定义样式/图标、跨视图复用、删除按钮本体、批量重排位置，或提供了明确的 qRobot/wings 配置时，才使用 `qingflow builder button apply` 管理按钮本体和视图位置。

```bash
qingflow builder button apply \
  --app-key "<APP_KEY>" \
  --upsert-buttons-file tmp/upsert_buttons.json \
  --remove-buttons-file tmp/remove_buttons.json \
  --view-configs-file tmp/button_view_configs.json
```

新增数据按钮优先用语义化字段映射：

```json
{
  "client_key": "add_worklog",
  "button_text": "快捷添加工时",
  "trigger_action": "addData",
  "trigger_add_data_config": {
    "target_app_key": "WORKLOG_APP",
    "field_mappings": [
      {"source_field": "员工名称", "target_field": "员工"}
    ],
    "default_values": {"状态": "待提交"}
  }
}
```

- 新增数据按钮只写 `field_mappings/default_values`。
- `addData` 用于从当前记录创建下游/关联记录；`link` 只用于跳转 URL；`qRobot` / `wings` 只在用户提供现成配置时使用，不要编造。
- `view_configs[].buttons[]` 绑定位置：`header`、`detail`、`list`。对外入参仍写 `placement=list`；CLI 会映射为后端 `INSIDE` 行内/列表按钮。
- `button_ref` 可以引用同次 `upsert_buttons[].client_key`，也可以引用已有 `button_id`。
- `view_configs[].view_key` 使用 `builder app get --app-key APP_KEY` 返回的 raw `view_key`，不要加 `custom:`。
- `view_configs[].mode` 默认 `merge`，merge 模式必须传 `buttons`；清空用 `mode="replace"` 或显式 `buttons: []`。
- 字段兼容与 `数据ID` / `编号` 规则见 **[match-rules.md](./match-rules.md)**。
- 删除按钮时优先传 **`button_id`**；若用 **`button_text`** 必须能唯一匹配。DELETE 发出后会按单个 **`button_id`** 回读验证，结果看 **`removed[].delete_executed/readback_status/safe_to_retry_delete`**。只要 **`delete_executed=true`**，就不要盲目重复删除；**`readback_status=unavailable|still_exists`** 表示回读待确认。
- 该工具有成功写入时自动发布；全阻断、全失败或无变化不会额外发布。

### 8.2 关联视图/报表：`app_associated_resources_apply`

默认使用 `qingflow builder associated-resource apply` 管理应用级关联资源池与视图展示配置。

- 权限分层：`upsert_resources` / `patch_resources` / 删除 / 排序应用级关联资源池走 **EditAppAuth**；`view_configs` 修改某个视图里的关联资源展示配置，还需要视图配置侧的 **ViewManagementAuth**（未开启高级应用权限时回落到 **DataManageAuth**）。
- 多应用批量配置时可用 `--apps-file`，文件为 JSON 数组，每项写 `{ "app_key": "...", "upsert_resources": [...], "patch_resources": [...], "remove_associated_item_ids": [...], "reorder_associated_item_ids": [...], "view_configs": [...] }`；不要和单应用的 `--app-key` / `--*-file` 混用。

```bash
qingflow builder associated-resource apply \
  --app-key "<APP_KEY>" \
  --upsert-resources-file tmp/upsert_resources.json \
  --view-configs-file tmp/associated_view_configs.json
```

```bash
qingflow builder associated-resource apply \
  --apps-file tmp/associated_resource_apps.json
```

- Shell 退出码为 0、重定向成功或 `echo OK` 只表示命令执行完，不表示业务成功。必须读取输出 JSON，检查顶层 `status`、`error_code`、`warnings`、`blocking_issues`；`status: failed`、`partial_success`、`ASSOCIATED_RESOURCES_APPLY_BLOCKED` 都不能当作完成。
- 关联资源要生效必须同时处理两层：应用级资源池（`upsert_resources` / `patch_resources`）和视图详情展示绑定（`view_configs`）。只传 `--upsert-resources-file` 往往只是在资源池准备资源，不会让按钮或视图详情里看到关联资源。
- `builder views apply` 新建视图会默认打开详情页关联查看（展示全部应用级关联资源）；若只需要默认展示全部资源，创建视图时不用额外写 `view_configs`。需要指定部分资源、关闭展示或配置匹配筛选时，仍必须使用本工具的 `view_configs` / `match_mappings`。
- `associated_item_id` 是后端 `form_asos_chart.id`，最终来自 `app_get.associated_resources[].associated_item_id`；它不是 `chart_id`、`chart_key` 或 `view_key`。
- 创建前先检查 `associated_resources` 中是否已有相同 `target_app_key + view_key/chart_key`；已存在时用 `patch_resources`，不要重复 `upsert_resources`。
- 公开面只写 `graph_type`、`view_key` / `chart_key` 和可选 `report_source`；关联视图内部自动使用后端需要的来源，关联报表默认是 **应用源 BI 报表**，可先用 `builder charts apply` 创建/更新。**数据集 BI 报表只能关联已有报表**，使用 `report_source: "dataset"`，不要用 `builder charts apply` 创建或编辑 dataset 报表。
- 关联报表时优先传 `chart_id` / `chart_key`；CLI 会解析为轻流后端需要的内部关联 id。视图展示配置里已有资源仍以 `associated_item_id` 为最终口径。
- 同次创建资源并配置视图时，用 `client_key` + `view_configs[].associated_item_refs`。
- `client_key` 只用于同一次 apply 内给 `view_configs[].associated_item_refs` 引用，后端不会保存，不能用于后续去重。
- 每个主应用都要生成自己的 upsert/view-config payload，不要复用其他应用的 tmp JSON；命令中 `--app-key` 只写一次，且必须与 payload 的主应用一致。
- 成功后必须用 `builder app get --app-key ...` 回读：确认 `associated_resources[].associated_item_id` 已生成，并确认目标视图的详情配置中已绑定对应资源。若只看到资源池有记录、视图详情无绑定，继续补 `view_configs`，不能宣称完成。
- 关联筛选优先用 `match_mappings`，不要手写 raw `match_rules`；字段兼容规则见 **[match-rules.md](./match-rules.md)**。
- 删除关联资源时传 **`associated_item_id`**，也可传已有资源的 `chart_id/chart_key/view_key` 让工具解析为内部 id。后端暂无确认可用的单项关联资源 GET，所以工具只做一次资源池回读验证；结果看 **`removed[].delete_executed/readback_status/safe_to_retry_delete`**。只要 **`delete_executed=true`**，就不要盲目重复删除；**`readback_status=unavailable|still_exists`** 表示回读待确认。
- 该工具有成功写入时自动发布；不提供 `--no-publish`。

## 9. `app_publish_verify`（CLI `builder publish verify`）

```bash
qingflow builder publish verify \
  --app-key "<APP_KEY>" \
  [--expected-package-id <TAG_ID>]
```

- 校验 **已发布**、**视图 OK**、可选 **包一致性**（**`expected_package_id`**）。
- **编辑锁**：若因 **当前用户持有锁** 失败，契约提示：**`builder app release-edit-lock-if-mine`**（须 **邮箱 / 姓名** 参数）后再重试。

**实跑**（`ead8ims5i401`）：`message: app already published and verified`，`package_ids_after: [2030703]`。

---

## 9. 输出与排障

- **builder 写入/apply 工具默认直接输出 JSON 到 stdout**，便于前端捕获；builder 读取命令仍显式加 `--json`。需要同时留档时使用 `| tee tmp/builder_*.json`，不要用 `>` 吞掉 stdout。
- **schema apply 超时 / partial / write_executed 后**：先 `readback_before_retry`。尤其是完整系统 multi-app 创建，慢响应常见但可能已经落库；不要直接重放整批、拆单应用重建或用后缀应用绕过冲突。
- **446 / 49614**：多看契约 **execution_notes**（如 **多选关联限制**）。
- **40161 / 元数据不可读**：**relation / q_linker / code_block** 按上文 **显式 name / binding** 路径降级。

---

## 10. 交叉引用

- **最小 `add_fields` 示例**：[schema_add_fields_minimal.example.json](../../examples/schema/schema_add_fields_minimal.example.json)
- **历史字段 type 一次性 `add_fields` 探针（非当前主路径）**：[schema_apply_add_fields_all_types.json](../../examples/schema/schema_apply_add_fields_all_types.json)
- **类型与场景总表**：[30-schema-fields.md](../30-schema-fields.md)
- [SKILL.md](../../../SKILL.md)：`builder` 命令边界、**ADMIN** 指向。
- [QINGFLOW_CLI_FIELD_DATA_TYPES.md](../../core/QINGFLOW_CLI_FIELD_DATA_TYPES.md)：成员侧 **记录读写** 的 `kind` / 值形态（与 **搭建 `type`** 名称不同系，但可对照理解业务）。
- [QINGFLOW_CLI_ADMIN_CHEATSHEET.md](../../core/QINGFLOW_CLI_ADMIN_CHEATSHEET.md)：`package apply`、权限类 **`IMPORT_*` / 40002**。
