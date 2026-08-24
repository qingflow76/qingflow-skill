# Builder 报表（QingBI）创建与变更 SOP：`qingflow builder charts apply`

稳定命令：**`qingflow builder charts apply`**（子命令 **`builder charts apply`**；**`qingflow build charts apply`** 等价）。

实现要点：`builder_facade/models.py`（**`ChartUpsertPatch`**、**`ChartPartialPatch`**、**`ChartApplyRequest`**、**`ChartFilterRulePatch`**）、`builder_facade/service.py`（**`chart_apply`** / **`_build_public_chart_config_payload`**）、`cli/commands/builder.py`（**`--upsert-file`** / **`--patch-file`** / **`--remove-chart-ids-file`** / **`--reorder-chart-ids-file`**）。已对应用 **`ead8ims5i401`** 与工时测试应用实跑：**新建/更新 `target`、常规图表、`summary` / `gauge` / `scatter` / `dualaxes`，按 `chart_id` 更新（改名 + `visibility`）、仅 `reorder`**。

> **权限**：**`data_manage`**（与其它搭建写一致，`chart_apply` 内 **`_guard_app_permission`**）。

> **读取链路**：`builder chart get` / `chart_get` 读取基础信息时优先走前端同源的 **`/qingbi/charts/qflow/baseinfo/{chartId}`** 可见性链路；仅当该 qflow 路由明确不存在/不适用时才退回 BI 管理详情 **`/qingbi/charts/baseinfo/{chartId}`**。配置详情 **`/qingbi/charts/{chartId}/configs`** 仍可能需要 **`CHART_SEE`**，不可用时会尝试从 qflow 数据接口返回的 embedded config 降级。不要把中间 **`CHART_SEE` / 40002** 直接当成“用户看不到报表”。

> **契约**：`qingflow --json builder contract --tool-name app_charts_apply`  
> （`--tool-name` 为契约索引。）

> **与「应用发布」的关系**：契约 **execution_notes** 写明 **`app_charts_apply` 为 immediate-live，不走 `app_publish`**。改报表不等价于 **`builder publish verify`**。

> **能力边界**：`builder charts apply` 只创建/更新 **应用源 QingBI 报表**（生成 `dataSourceType=qingflow`）。**数据集 BI 报表不在此工具创建/编辑**；先在 QingBI 中创建数据集报表，再用 **`builder associated-resource apply`** 以 `report_source: "dataset"` 关联到轻流应用。

---

## 1. CLI 形态

```bash
qingflow --json builder charts apply \
  --app-key "<APP_KEY>" \
  [--upsert-file UPSERT_JSON] \
  [--patch-file PATCH_JSON] \
  [--remove-chart-ids-file REMOVE_JSON] \
  [--reorder-chart-ids-file REORDER_JSON] \
  > tmp/builder_charts_apply.json
```

- 四个文件参数均可省略，但 **`ChartApplyRequest`** 要求 **至少一项非空**（**upsert** / **patch** / **remove** / **reorder**），否则校验报错。
- 各文件均为 **JSON 数组**（与 `load_list_arg` 一致）。
- 大 JSON 必须 **落盘**，见主技能 **builder** 行。
- 完整系统里一次要创建很多报表时，主路径按应用或主题分批提交，推荐每批 **4-8 个 `upsert_charts`**。超过 8 个时 CLI 会在写入前返回 `CHART_UPSERT_BATCH_TOO_LARGE`，并给出 `details.suggested_batch_payloads[]`；直接逐个执行这些 payload，不要提交原始大数组。

---

## 2. 推荐顺序（读 → 写 → 核对）

| 步骤 | 动作 | CLI |
|------|------|-----|
| ① 解析应用 | 确认 **`app_key`** | **`builder app resolve --app-key …`** |
| ② 读报表字段 | 取 **`chart_fields[]`** 中的 **显示名**、**`field_id`**（如 **`field_数字`**）或 **`bi_field_id`**，供 `group_by` / `metric` / `where` 用；可直接复制 **`chart_fields[].chart_apply_examples`** 作为 apply 片段 | **`builder app get --app-key … fields`** |
| ③ 读现有报表 | 已有 **`chart_id`**、重名风险 | 先看 **`builder app get --app-key …`** 的 compact `charts`；不足时再用 **`builder app get --app-key … charts`** |
| ④ 应用变更 | upsert / remove / reorder | **`builder charts apply …`** |
| ⑤ 再读列表 | 确认顺序与条目 | 再次 **`builder app get --app-key …`**；需要完整报表清单时再下钻 `builder app get charts` |

---

## 3. `upsert_charts[]` 形状（**`ChartUpsertPatch`**）

| 键 | 说明 |
|----|------|
| **`name`** | 必填；新建时即图表名；**更新**时可改名。 |
| **`chart_type`** | 以 `qingflow --json builder contract --tool-name app_charts_apply` 的 `$.contract.allowed_values["chart.chart_type"]` 为准；当前公开面已覆盖 QingBI 常用类型，如 **`target` / `indicator` / `summary` / `pie` / `bar` / `columnar` / `line` / `table` / `detail` / `area` / `stacked_area` / `funnel` / `waterfall` / `gauge` / `heatmap` / `histogram` / `treemap` / `radar` / `stacked_bar` / `stacked_column` / `scatter` / `ring` / `rose` / `dualaxes` / `map`** 等；最终仍以 contract 为准。 |
| **`chart_id`** | 可选。**有则按 id 命中更新**；无则 **按 `name` 精确匹配**：0 个 → **创建**；多个 → **歧义报错**（须带 **`chart_id`**）。 |
| **`metric`** / **`metrics`** | **主推语义指标写法**：`"count(*)"`、`"sum(金额)"`、`"avg(工时)"`、`"max(评分)"`、`"min(耗时)"`，也支持对象 `{"op":"sum","field":"金额"}`。字段必须来自 **`chart_fields[]`**。 |
| **`group_by`** | **主推维度写法**：字段显示名、`field_id` 或 `bi_field_id` 数组，例如 `["使用状态"]`。 |
| **`where`** / **`filters`** | 统一固定筛选写法：**`field`/`field_name`**（可用 **`chart_fields[].title`** / **`field_id`** / **`bi_field_id`**）+ **`op`/`operator`** + **`value`/`values`** → 写入配置 **`beforeAggregationFilterMatrix`**。 |
| **`dimension_field_ids`** / **`indicator_field_ids`** | 兼容/高级写法；旧 payload 可继续用，但智能体主路径优先写 `group_by` + `metric(s)`。 |
| **`visibility`** | 可选；编译为 QingBI **`visibleAuth`**；**仅更新 visibility** 时不重算其它授权结构（见契约）。**更新**时 **省略** 可保留原可见性。 |
| **`config`** | 透传高级键：`aggregate`、`beforeAggregationFilterMatrix`、`afterAggregationFilterMatrix`、`chartStyleConfigs`、`displayLimitConfig`、`rawDataConfigDTO`、`query_condition_field_ids` 等；未列键会 **merge 进根**（实现 **`_build_public_chart_config_payload`**）。主路径不要手写 `selectedMetrics` / `xMetrics` / `leftMetrics`。 |
| **`question_config`** / **`user_config`** | 可选；分别 POST **`/chart/{id}/question/config`** 与 **`/user/config`**。 |

**配置是否重算**：若已存在图表且本次 **未显式**改 **`metric(s)` / `group_by` / `where` / `dimension_field_ids` / `indicator_field_ids` / `filters` / `config`**（Pydantic **`model_fields_set`**），实现可 **跳过** **`qingbi_report_update_config`**；**新建**总会写配置。

**报表筛选 operator**：推荐使用 `eq` / `neq` / `in` / `contains` / `gte` / `lte` / `is_empty` / `not_empty`；兼容 `equal` / `equals` / `=` / `!=` / `any_of` / `one_of` / `empty` 等别名。CLI 会自动转成 QingBI 字符串判断符（如 `equal`、`anyMatch`、`isNull`）和 BI 前端需要的 `judgeValue` 文本值；单选/多选筛选入参可传选项文本或 option id，CLI 会按 QingBI 路径转成文本。智能体不要手写 `judgeType`、`judgeValue`、`beforeAggregationFilterMatrix`。

**读回语义**：`builder chart get` / `chart_get` 会返回语义化 `group_by`、`metrics`、`filters`；`config.*` 仅作为 raw 诊断，不作为智能体更新主输入。

示例：

```json
{"field_name": "使用状态", "operator": "eq", "value": "正常"}
```

### 3.1 推荐语义写法

指标卡：

```json
{"name": "正常设备数", "chart_type": "target", "metric": "count(*)", "where": [{"field": "使用状态", "op": "eq", "value": "正常"}]}
```

字段聚合：

```json
{"name": "维修费用总额", "chart_type": "target", "metric": "sum(维修费用)"}
```

分组图表：

```json
{"name": "设备状态分布", "chart_type": "bar", "group_by": ["使用状态"], "metric": "count(*)"}
```

双轴图：

```json
{"name": "预算执行对比", "chart_type": "dualaxes", "group_by": ["月份"], "left_metric": "sum(预算金额)", "right_metric": "sum(实际金额)"}
```

字段发现返回的 `chart_fields[].chart_apply_examples` 会给出同样语义的可复制片段：

- `count_by_field`：按该字段分组计数，适合 bar/columnar/pie 类分布图。
- `filtered_count`：按该字段固定筛选后计数，适合 target/indicator 指标卡。
- `sum_metric`：仅数值字段提供，适合金额/数量/工时等合计指标卡。

拿到片段后只改 `name`、`chart_type` 和筛选值即可，不要改写成 `indicator_field_ids` / `config.aggregate` / `selectedMetrics`。

### 3.2 BI 类型与后端字段映射

CLI 对外推荐使用 **`group_by` + `metric(s)`**；旧的 **`dimension_field_ids`** 和 **`indicator_field_ids`** 仍兼容。字段来源必须是 **`app_get_fields.chart_fields`** 的 QingBI datasource 字段。部分 QingBI 类型后端字段槽位不同，CLI 会自动转换：

| `chart_type` | 后端要求 | CLI 处理 |
|--------------|----------|----------|
| **`summary`** | `xDimensions` / `yDimensions` + `selectedMetrics` | `rows` 写入 `xDimensions`，`columns` 写入 `yDimensions`，`metrics` 写入 `selectedMetrics`。 |
| **`scatter`** | `selectedDimensions` + 单个 `xMetrics` + 单个 `yMetrics` | `x_metric` / `y_metric` 分别写入 X/Y；也兼容 `metrics` 前两个。 |
| **`dualaxes`** | `selectedDimensions` + `leftMetrics` / `rightMetrics` | `left_metric` / `right_metric` 分别写入左/右轴；也兼容 `metrics` 前两个。 |
| **`gauge`** | 无维度，且必须有两个不重复指标 | `value_metric` / `target_metric` 为主；只给一个真实指标时，第二指标自动补 **`数据总量`**。 |
| **`histogram`** | 最多 1 个维度，且必须 1 个普通数值指标 | 不能省略指标，不能使用默认 **`数据总量`** / count，不能使用文本字段或聚合公式字段；推荐 `metric: "sum(数值字段)"` 或 `metric: "avg(数值字段)"`。 |
| **`heatmap`** | 2 个维度 + 1 个指标 | 不满足时 CLI 会提前返回 `diagnostics`，不要等后端裸 810xx。 |
| **`waterfall` / `map`** | 1 个维度 + 1 个指标 | `map` 的维度应选位置/地区含义字段。 |
| **`treemap`** | 1-2 个维度 + 1 个指标 | 维度过少/过多都会被前置校验。 |

这些转换用于避免“报表配置未完成”。若用户显式在 `config` 中提供 `xDimensions`、`xMetrics`、`leftMetrics` 等高级字段，应以 contract 与后端校验为准。

低频报表失败时优先看 **`chart_results[].diagnostics`**：

- **`81002`** 通常会翻译为 `WRONG_METRIC_COUNT_OR_TYPE`，代表指标数量或指标类型不满足当前图表。
- **`81005`** 通常会翻译为 `CHART_FIELD_ID_REPEAT`，代表某个维度/指标槽位里出现重复 `fieldId`。
- `diagnostics.next_action` 是下一步修复建议；不要只把裸后端码返回给用户。

### 3.3 应用源报表 vs 数据集报表

- **应用源 BI 报表**：使用 `builder charts apply` 创建/更新，配置里保持 `dataSourceType=qingflow`。
- **数据集 BI 报表**：当前 CLI 不创建、不编辑；只能在已有报表基础上，用 `builder associated-resource apply` 关联到应用，传 `report_source: "dataset"`。
- 不要把 dataset 报表的 `chart_id` 交给 `builder charts apply --patch-file` 更新；工具会拒绝，避免误写应用源配置。

---

## 3.4 已有报表局部更新：`patch_charts`

`patch_charts` 用于已有报表的小参数替换，工具会读当前 base/config、合并 `set/unset`，再按后端要求保存整份配置。

```json
[
  {
    "chart_id": "CHART_ID",
    "set": {
      "name": "本月工时总览",
      "visibility": {"mode": "workspace"}
    }
  }
]
```

- patch 项直接用真实定位字段 `chart_id` + `set` / 可选 `unset`，不要写字面量 `selector` key。
- 改名称、可见性、筛选、单个 config 片段时优先用 `patch_charts`。
- 新建或提供完整目标配置才用 `upsert_charts`。

---

## 4. 创建流程（实现摘要）

1. **读** 应用表单 **`fields`** + QingBI datasource **`chart_fields`**；报表维度/指标/筛选/查询条件字段以 **`chart_fields`** 为权威，表单字段只用于补充显示名/类型。
2. **无 `chart_id` 且无名或名未命中**：**`qingbi_report_create`**（临时 **`chartId`** 形如 **`mcp_<hex>`**），再以 **`chartName`/`chartType`** 做 **读回确认**，得到 **最终 `chart_id`**。  
3. **有名唯一命中** 或 **`chart_id` 命中**：必要时 **`qingbi_report_update_base`**（改名、类型、**`visibleAuth`**）。  
4. **新建或 config 有变**：**`qingbi_report_update_config`**（**`_build_public_chart_config_payload`**）；特殊 BI 类型会按上文转换后端字段。

---

## 5. **remove** / **reorder**

- **`--remove-chart-ids-file`**：字符串 id 数组 → **`qingbi_report_delete`**。  
- 删除成功后工具会用单个 **`chart_id`** 回读验证是否已不存在；**纯删除不会再读全量报表列表**。若返回 **`readback_status: unavailable`** 或 **`still_exists`**，表示删除请求已发出但回读未确认，**不要盲目重复删除**，可稍后用 **`builder chart get --chart-id …`** 确认。
- **`--reorder-chart-ids-file`**：期望的 **展示顺序前缀**；实现会 **反转** 后调 **`qingbi_report_reorder`**；验证时要求列表 **`chart_list_source == "sorted"`** 且前缀与请求一致。

---

## 6. 响应与排障

| 字段 | 含义 |
|------|------|
| **`chart_results[]`** | 每项 **`status`**: **`created`** / **`updated`** / **`removed`** / **`failed`**。 |
| **`verification.charts_verified`** | 新建/更新/排序通过报表清单回读验证；删除通过单个 **`chart_id`** 回读验证。 |
| **`partial_success` / `CHART_APPLY_PARTIAL`** | 部分 **`upsert/remove`** 失败。若同时 `write_executed=true` / `write_may_have_succeeded=true`，先读回报表列表，不要整批重试。 |
| **`CHART_READBACK_PENDING`** | 变更已提交但列表读回未完成。 |
| **`CHART_DELETE_READBACK_PENDING`** | 删除请求已完成，但单个 **`chart_id`** 回读未确认已删除。 |
| **`CHART_UPSERT_BATCH_TOO_LARGE`** | 一次 upsert 图表数超过 8；CLI 写前阻断，`write_executed=false`，按 `details.suggested_batch_payloads[]` 分批执行。 |
| **`chart_results[].readback_status`** | 删除结果专用：**`deleted`** / **`still_exists`** / **`unavailable`**。只要 **`delete_executed=true`**，**`safe_to_retry_delete=false`**，不要直接重复删除。 |

常见问题：**重名**须 **`chart_id`**；**`chart_id` 不存在**；报表字段必须来自 **`app get fields.chart_fields`**，**record schema 可见** 或 **普通表单 fields 可见** 不等于 QingBI 可用；系统字段如 **申请人/申请时间/编号** 只有出现在 **`chart_fields`** 时才可用于报表；字段标题重复时用 **`bi_field_id`** 或 **`field_queId`** 精确指定；**子表等**类型是否可做维度/指标以后端为准。

`CHART_APPLY_PARTIAL` 恢复规则：

- 先看 `details.failed_chart_names`、`details.failed_delete_chart_ids` 和 `details.readback_first`。
- 若 `details.readback_first=true`，先 `builder app get --app-key <APP_KEY> charts` 或 `chart get` 确认哪些报表已经存在/已更新。
- 只重试 `details.suggested_retry_payload` 里的失败项；不要重放原始 `upsert_charts` 全量数组。
- 如果失败项已经在读回中存在但配置未确认，按失败项名称或 `chart_id` 做一次最小 patch。

`CHART_UPSERT_BATCH_TOO_LARGE` 处理规则：

- 这是写前阻断，不是后端失败；`write_executed=false`，可以安全按建议重试。
- 直接复制执行 `details.suggested_batch_payloads[]`，每次只跑一个 payload。
- 不要改报表名称、不要拆成单个图表反复试、不要重放原始大数组。

---

## 7. 示例文件（可复制）

- **目标图（契约极简）**：[charts_upsert_minimal.example.json](./charts_upsert_minimal.example.json)  
- **柱状（须替换 `field_id`）**：[charts_upsert_bar.example.json](./charts_upsert_bar.example.json)  
- **重排**：[charts_reorder.example.json](./charts_reorder.example.json)  
- **删除**：[charts_remove.example.json](./charts_remove.example.json)

---

## 8. 本环境实测（`ead8ims5i401`）

| 操作 | 载荷要点 | 结果 |
|------|-----------|------|
| 新建 **bar** | **`group_by`: [`状态`]**，**`metric`: `sum(金额)`** | **`chart_id`: `mcp_3a35981aff4f4f57`**，`status: created`，**`verified: true`** |
| **更新** | 同上 id，**`name`** 改为 **`CLI图表探针_柱状_已改名`**，补 **`visibility`** workspace | **`status: updated`**，**`verified: true`** |
| **reorder** | **`[mcp_3a35981aff4f4f57, mcp_fb104267c5c249ca]`** | **`success`**，**`chart_order_verified: true`** |

（环境中另有早期探针 **`mcp_fb104267c5c249ca`（target）**，供门户 **`chart_ref`** 使用。）

---

## 9. 交叉引用

- [SKILL.md](../SKILL.md)  
- [QINGFLOW_CLI_BUILDER_APP_DELIVERY_WORKFLOW.md](./QINGFLOW_CLI_BUILDER_APP_DELIVERY_WORKFLOW.md)  
- [QINGFLOW_CLI_BUILDER_PORTAL_WORKFLOW.md](./QINGFLOW_CLI_BUILDER_PORTAL_WORKFLOW.md)（**`chart_ref`**）  
- [QINGFLOW_CLI_FIELD_DATA_TYPES.md](./QINGFLOW_CLI_FIELD_DATA_TYPES.md)（成员侧 **`kind`** 与搭建 **`type`** 对照理解业务）
