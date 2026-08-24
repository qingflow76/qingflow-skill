# Qingflow CLI：获取数据工作流（应用记录）

> **用途**：使用当前 CLI 会话，从「选定应用」到「读懂列含义 + 样本/模糊定位 / 单条详情」的**推荐闭环**；下表 **左列**可与常见 **编排/内部接口**命名对照，**右列**仅为本 CLI 命令。
> **新版口径**：`record_list` 不是批量分析入口，而是样本浏览和模糊定位入口；`record_get` 是前端详情页首屏上下文入口；全量日志用 `record logs`；分析取数统一转 [record/analysis](../record/analysis/README.md) 的 `record access -> Python/pandas`。
> **关联**：权限、`view_id` 选取雷区、成员最短路径速查见 **[QINGFLOW_CLI_MEMBER_CHEATSHEET.md](./QINGFLOW_CLI_MEMBER_CHEATSHEET.md)**；**字段 `kind` / 数据类型**见 **[QINGFLOW_CLI_FIELD_DATA_TYPES.md](./QINGFLOW_CLI_FIELD_DATA_TYPES.md)**；**新建记录**见 **[QINGFLOW_CLI_RECORD_CREATE_WORKFLOW.md](../record/QINGFLOW_CLI_RECORD_CREATE_WORKFLOW.md)**；**更新记录**见 **[QINGFLOW_CLI_RECORD_UPDATE_WORKFLOW.md](../record/QINGFLOW_CLI_RECORD_UPDATE_WORKFLOW.md)**；最终统计结论统一使用 **[record/analysis](../record/analysis/README.md) 的 `record access -> Python/pandas`**；主技能规则见 **[../SKILL.md](../../SKILL.md)**。

---

## 概念步骤 → CLI 映射

| 习惯概念名（编排/文档） | CLI 等价命令 | 必填要点 |
| --- | --- | --- |
| `app_get`（列应用内可访问视图） | `qingflow --json app get --app-key <APP_KEY>` | 从返回体的 **`data`（若存在）** 内取 `accessible_views[]` |
| `record_schema_get`，`schema_mode=browse` | `qingflow --json record schema browse --app-key <APP_KEY> --view-id <VIEW_ID>` | 子命令 **`browse`** 即「浏览视图」表结构 |
| `record_list` | `qingflow --json record list --app-key <APP_KEY> --view-id <VIEW_ID> [--query 文本] [--query-field FIELD_ID] [--page-size N]` | 样本浏览 / 模糊定位，默认最多返回 10 条；`query_fields` 是全文搜索字段范围 |
| `record_get` | `qingflow --json record get --app-key <APP_KEY> --record-id <RECORD_ID> [--view-id <VIEW_ID>]` | 前端详情页首屏上下文：字段、首屏日志、引用、关联资源、图片与文件资产 |
| `record_logs_get` | `qingflow --json record logs --app-key <APP_KEY> --record-id <RECORD_ID> [--view-id <VIEW_ID>]` | 单条记录全量可见数据日志 + 流程日志；自动分页写本地 JSONL，响应只返回摘要和文件路径 |

**补充**：若尚未持有 `APP_KEY`，先做 `qingflow --json app list [--query <关键词>]`，在 `items[].app_key` 里选应用；带 `--query` 时读取 `matched_count` / `unfiltered_count` 判断是否命中。

---

## 推荐执行顺序

```text
app get（解析 accessible_views，选定 VIEW_ID）
  → record schema browse（对齐字段 id/类型/展示名；也是 list/access/get 的视图字段口径）
  → record list（样本浏览或 query 模糊定位候选）
  → （可选）record get（对单条 record_id 拉详情页首屏上下文）
  → （可选）record logs（需要完整审计日志时再拉全量日志 JSONL）
```

- **仅当你只需要「快速确认有无数据」**时，可以省略 `schema browse`，直接 `app get` → `record list`（与成员速查表「最短路径」一致）。
- **当你需要稳定映射列名、写过滤条件或对接自动化**时，应按上表**显式**走 `schema browse`，避免对着 `list` 里中文列名猜字段定义。
- **当用户只给出模糊信息定位单条数据**时，走 `record schema browse` 确认可搜索字段，再用 `record list --query ... --query-field ...` 返回候选；只有候选明确后才 `record get`。
- **需要分组/聚合统计、最终统计结论、分析报告、趋势/排名/比例/分布**时，必须按 **[record/analysis](../record/analysis/README.md)** 执行 `app get -> record schema browse -> record access -> Python/pandas -> final answer`。

---

## 命令模板（占位符替换即可）

**1）应用与视图**

```bash
qingflow --json app get --app-key <APP_KEY> > tmp/qingflow_app_get.json
```

从 `tmp/qingflow_app_get.json` 解析：`$.data.accessible_views`（无 `data` 时再试顶层 `accessible_views`）。每个元素含 `view_id`、`name`、`kind` 等。

若响应 `warnings[]` 含 `CUSTOM_VIEW_LIST_UNAVAILABLE`，表示 custom view 列表读取被权限或后端限制降级；这不是应用整体不可读。优先使用已返回的 `system:*` 视图继续 `schema browse` / `record list`，或从前端 URL 的 `viewgraphKey` 补充明确 `view_id`。

**2）浏览视图表结构（= `record_schema_get` browse）**

```bash
qingflow --json record schema browse \
  --app-key <APP_KEY> \
  --view-id <VIEW_ID> \
  > tmp/qingflow_schema_browse.json
```

实跑样例响应顶层键包含：`status`、`app_key`、`schema_scope`、`fields`、`suggested_dimensions` 等（**以实际 JSON 为准**）。

**3）记录列表**

```bash
qingflow --json record list \
  --app-key <APP_KEY> \
  --view-id <VIEW_ID> \
  > tmp/qingflow_records.json
```

列表默认最多返回 10 条，行数据常见于 `$.data.items`；每条一般有 `record_id`（及业务字段键值）。需要调整样本量时加 `--page-size <N>`；它只影响浏览/候选定位样本，不替代分析取数。响应会给出总数/下一步建议；如果是模糊定位，优先看 `lookup.total_count`、`lookup.next_action`。

`record_list.data.items[]` 是**字段平铺行对象**，不是 `fields[]` 数组。定位候选或做名称到记录 ID 映射时直接读字段标题键：

```python
rows = payload["data"]["items"]
name_to_record_id = {row["客户名称"]: row["record_id"] for row in rows}
```

只有 `record_get` 详情使用 `fields[]` 来表示字段列表。

**模糊定位示例**：

```bash
qingflow --json record list \
  --app-key <APP_KEY> \
  --view-id <VIEW_ID> \
  --query "北京和路元" \
  --page-size 20 \
  --query-field 6299262 \
  > tmp/qingflow_record_lookup.json
```

`--query-field` 对应 `record_browse_schema_get.fields[].field_id`，表示后端全文搜索范围；它不是输出列控制。

**4）单条记录详情**

```bash
qingflow --json record get \
  --app-key <APP_KEY> \
  --record-id <RECORD_ID> \
  --view-id <VIEW_ID> \
  > tmp/qingflow_record_get.json
```

已知前端视图时必须传同一个 `--view-id`；未知时 CLI 会先试默认详情 route，再在权限/不可见类错误下尝试可访问视图。`record_get` 现在返回详情页首屏上下文，重点看：`fields[]`、`references[]`、`data_logs`、`workflow_logs`、`associated_resources`、`media_assets`、`file_assets`、`semantic_context`。其中 `data_logs` / `workflow_logs` 只表示详情页首屏日志，不是全量审计历史。若 `unavailable_context[]` 中出现 `detail_schema`、`audit_info`、`data_logs`、`workflow_logs` 等，只说明这些辅助详情上下文读取受限；只要顶层 `status=ok` 且 `fields[]` 有目标字段，就不要把辅助 40002 当作记录不可读。图片读 `media_assets.items[].local_path`；文档/表格/PDF 等附件读 `file_assets.items[].local_path` 和 `file_assets.items[].extraction.text_path`。**不要直接访问远端 Qingflow 附件 URL**。

**5）全量日志（仅在用户明确需要完整审计/日志历史时）**

```bash
qingflow --json record logs \
  --app-key <APP_KEY> \
  --record-id <RECORD_ID> \
  --view-id <VIEW_ID> \
  > tmp/qingflow_record_logs.json
```

响应重点看：`data_logs.local_path`、`workflow_logs.local_path`、`items_count`、`pages_fetched`、`complete`、`context_integrity.safe_for_full_log_conclusion`。完整日志在本地 JSONL 文件中，默认目录为 `~/.qingflow-mcp/record-logs/<run_id>/`；不要把 JSONL 全文直接塞进上下文，按需用脚本读取、筛选或汇总。

---

## `view_id` 选取（成员侧必读摘要）

- **`system:all` 等业务系统视图**：实跑可用于 `schema browse` + `record list`（具体以租户配置为准）。显式传入的 `view_id` 必须按前端当前视图忠实执行；`system:all` 报 40002 / 40027 / 404 / 500 时，不要自动换成 `system:initiated`、`system:todo` 等其它系统视图，除非用户或前端 URL / `app get.accessible_views` 重新指定了那个视图。
- **`CUSTOM_VIEW_LIST_UNAVAILABLE`**：只说明 `app get` 没能列出 custom view；若已有 `system:*` 可用，不要把它当作应用或记录读取失败。
- **`custom:` 后仅数字**（如 `custom:1`）：成员侧常见 **`schema browse` / `list` / `access` 均 40038**，应**跳过**，改选 **`custom:` 带字母后缀**或其它可用视图（详见成员速查表「先有通路、再要有数据」）。
- **待办 / 已办 / 抄送「任务箱」**：不要用旧文档里的 `system:todo` 等视图充当任务中心；应使用 **`task list --task-box …`**（见主技能 **待办 SOP**）。

---

## 落盘与解析

- `schema browse`、`record list`、`record get`、`record logs` 体量大时，**必须**重定向到文件，勿将整段 JSON 直接塞进 LLM 上下文（规则见主技能「输出落盘规则」）。`record_get` 下载的本地图片/文件路径可以再交给图片理解、文档解析或 Python 读取；`record logs` 的全量日志读 `*.jsonl` 文件。
- 解析前**先 unwrap `data`**：多数业务成功响应为 `{ "data": { ... } }`，与 `schema browse` 部分字段在顶层的形态可能不同，以每次响应为准。

---

*维护：CLI 升级后请用 `qingflow record schema browse -h`、`qingflow record list -h`、`qingflow record get -h`、`qingflow record logs -h` 复核选项名；概念名 `record_schema_get` / `schema_mode=browse` 在 CLI 中固定对应子命令 `record schema browse`。*
