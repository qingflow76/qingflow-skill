# Qingflow CLI：更新记录工作流（详情后直接写入）

> **用途**：使用当前 CLI 会话读取目标记录详情后，用 **`record update`** 直接提交差异字段。主链路是 `record get -> record update`；字段范围不清、候选歧义或失败排查时，才追加 **`record schema update`**。
> **关联**：只读列表/详情见 **[QINGFLOW_CLI_DATA_RETRIEVAL_WORKFLOW.md](../core/QINGFLOW_CLI_DATA_RETRIEVAL_WORKFLOW.md)**；**字段 `kind` 与写入值总表**见 **[QINGFLOW_CLI_FIELD_DATA_TYPES.md](../core/QINGFLOW_CLI_FIELD_DATA_TYPES.md)**；最终统计结论统一使用 **[record/analysis](./analysis/README.md) 的 `record access -> Python/pandas`**；**成员 / 部门等** 的细颗粒写入见 **[QINGFLOW_CLI_RECORD_CREATE_WORKFLOW.md](./QINGFLOW_CLI_RECORD_CREATE_WORKFLOW.md)**；主技能 **[../SKILL.md](../../SKILL.md)**。

---

## 习惯概念名 → CLI

| 概念名 | CLI |
| --- | --- |
| `app_get`（含 `accessible_views`） | `qingflow --json app get --app-key <APP_KEY>` |
| `record_schema_get`，`schema_mode=browse`，带 `view_id` | `qingflow --json record schema browse --app-key <APP_KEY> --view-id <VIEW_ID>` |
| `record_get` | `qingflow --json record get --app-key <APP_KEY> --record-id <RECORD_ID> [--view-id <VIEW_ID>]` |
| `record_update`（单条） | `qingflow --json record update --app-key <APP_KEY> --record-id <RECORD_ID> --fields-file <FIELDS.json> [--view-id <VIEW_ID>]` |
| `record_update`（批量） | `qingflow --json record update --app-key <APP_KEY> --items-file <ITEMS.json> [--view-id <VIEW_ID>] [--dry-run]`（见下文） |

---

## 推荐顺序

```text
record get（得到 RECORD_ID、当前值、fields[].title/field_id/kind；已知前端视图时带 view_id）
  → 智能体按用户要求组 fields key/value
  → record update --fields-file [--view-id]（只提交需要改的题；大 JSON 落盘）
```

**何时先 `app get` / `record list`**：不知道 `view_id` 或 `record_id` 时，先用 `app get` 选视图，再用 `record list` 定位候选。已知 `record_id` 但已知前端/custom view 时，直接 `record get --view-id <VIEW_ID>`。
**何时追加 `record schema browse`**：只在需要提前看视图表头或搜索字段时使用；`record get` 已经会返回单条详情所需字段信息。
**何时追加 `record schema update`**：该命令 **必须 `record_id`**，返回 **`writable_fields` / `payload_template` / `available_update_routes` / `recommended_update_route`**，只用于排查「能改什么」和「会走哪条更新路径」。已知前端/custom view 时同样带 `--view-id`，让诊断优先探测同一个详情页上下文；字段明确时不要把它当必经步骤。

**更新路径自动选择**：`record update --view-id <VIEW_ID>` 会优先用这个 view 做字段解析和 custom view 写入候选；未传时自动探测可读 route。写入时仍会先尝试 **数据管理员直改**，若后端返回权限拒绝，再 fallback 到 **前端同源 custom view 详情编辑路径**；如果当前用户存在这条记录的唯一待办且目标字段在当前节点可编辑，最后会尝试 **workflow save-only**。成功时响应中的 **`update_route`** 是最终成功路径；失败时再查看失败原因与路线诊断。若诊断里有 `40002`，只代表某条 route 被拒绝，不一定表示用户对记录完全无编辑能力。

---

## 命令模板

**1）读取详情**

```bash
qingflow --json record get \
  --app-key <APP_KEY> \
  --record-id <RECORD_ID> \
  --view-id <VIEW_ID> \
  > tmp/qingflow_record_get.json
```

已知用户前端所在视图时传同一个 `--view-id`；未知时 CLI 默认先尝试 `system:all/type=8`，若该详情 route 被权限/不可见类错误拒绝，会继续尝试可访问视图。读取 `fields[]` 中的标题、`field_id`、`kind` 与当前值来组更新 payload。

`record_get` 的 `unavailable_context[]` 是辅助上下文提示：`detail_schema` / `audit_info` / 首屏日志等 40002 不等于记录详情读取失败。只要顶层 `status=ok` 且 `fields[]` 中已有目标字段，就按这些字段组 `record update` 的 key/value；只有顶层失败才按失败原因排查。

`record update` 的字段集合应是当前 `record get.fields[]` 的子集。带 `--view-id` 时，当前前端详情/视图隐藏的字段不要强写；字段不在 `fields[]` 中时，先切到包含该字段的视图/详情上下文，或用 `record schema update` 诊断可写字段和失败路径。`FIELD_NOT_FOUND` 通常表示当前更新上下文没有这个题，不等于整条记录不可编辑。

**2）如果缺 `record_id`，先定位候选**

```bash
qingflow --json record list \
  --app-key <APP_KEY> \
  --view-id <VIEW_ID> \
  > tmp/qingflow_records.json
# 或
qingflow --json record get --app-key <APP_KEY> --record-id <RECORD_ID> \
  > tmp/qingflow_record_get.json
```

**3）单条更新**

```bash
qingflow --json record update \
  --app-key <APP_KEY> \
  --record-id <RECORD_ID> \
  --fields-file tmp/qingflow_patch_fields.json \
  --view-id <VIEW_ID> \
  > tmp/qingflow_update_result.json
```

`--view-id` 可省略；已知用户来自某个 `custom:...` 前端详情页时建议传入，CLI 会优先尝试该 view，失败后再按自动路径 fallback。

**4）（仅排障）本条记录的更新诊断**

```bash
qingflow --json record schema update \
  --app-key <APP_KEY> \
  --record-id <RECORD_ID> \
  --view-id <VIEW_ID> \
  > tmp/qingflow_schema_update.json
```

**`tmp/qingflow_patch_fields.json`**：JSON **对象**，键为 **题目标题**（优先来自 `record get.fields[]`），**只放需要修改的键**；值类型与 **新建** 相同（成员、部门、附件等见 **[QINGFLOW_CLI_RECORD_CREATE_WORKFLOW.md](./QINGFLOW_CLI_RECORD_CREATE_WORKFLOW.md)**）。实现要求 **`fields` 为「按标题索引的 map」**（与 `record insert` 一致）。

不要把 schema 中见过但当前 `record get.fields[]` 没出现的隐藏字段直接放进 `fields-file`。这会让智能体把视图上下文问题误判成权限或字段不存在问题。

**特殊字段值**：

- **成员字段 `kind=member`**：先传自然语言字符串，如 `{"客户成功":"周颖"}`。若返回 `status="needs_confirmation"`，说明尚未写入；从 `confirmation_requests[].candidates[]` 选一项，改传显式对象，如 `{"客户成功":{"uid":1048599,"name":"沈嘉慧Seth","email":"shenjiahui@exiao.tech"}}`。
- **部门字段 `kind=department`**：先传部门名，如 `{"负责部门":"客户成功部"}`；歧义时同样按候选对象/id 重试。
- **关联字段 `kind=relation`**：传唯一可解析的自然语言、或 `{"apply_id":"..."}`；多匹配时按候选记录重试，不要猜 `apply_id`。
- **选项字段 `kind=select`**：单选传一个选项字符串；多选传字符串数组。
- **引用/公式/自动填充/只读/系统字段**：不要强写目标字段；改写上游驱动字段，或把 blocker 原因反馈给用户。

`needs_confirmation` 的语义是 **`write_executed=false`，等待确认候选**；不要把它当成功，也不要把它当最终权限失败。只有用明确候选对象重试并成功后，才报告写入完成。

**`--verify-write` / `--no-verify-write`**：见 `qingflow record update -h`；默认倾向 **保留校验**。

更新后优先查看：

- **`update_route.route_type`**：`admin_direct`、`view_edit` 或 `task_save_only`。
- **`tried_routes[]`**：只在失败或 verbose 诊断时需要看；成功时不要把中间路径失败当最终结果。
- **`write_executed`**：是否已经发出写请求；为 `true` 时不要盲目整单重试。
- **`verification_status`**：读回校验是否通过。

**`record_id` 与写入（排查前置）**：若后端 **`record_id` 超出 JavaScript `Number.MAX_SAFE_INTEGER`（约为 `9007199254740991`）**：在旧 1.0.x 或同类实现分支上，**`record list` / `record get` / `record schema update` 常仍可正常**，而 **`record update` 的实际落库**可能在 **`apply_id` 二次校验**处失败——stdout 常表现为 **`apply_id must be positive`**，根本原因多为 **「整数超过 JS 安全范围」**。**批量 `--dry-run`** 仍可用于覆盖 **预检**流程。处理方式见 **「排查摘要」**末行。

---

## 批量模式（`--items-file`）

- **不可**与 **`--record-id` / `--fields-file`** 同时使用。
- `items` 为 **数组**，每项为对象，至少包含：
  - **`record_id`**：正整数（字符串或可解析数字均可，以 CLI 校验为准）
  - **`fields`**：与单条相同的「标题 → 值」map

示例：

```json
[
  { "record_id": "518257794791628802", "fields": { "客户名称": "新名称" } },
  { "record_id": "518257794791628803", "fields": { "备注": "批量第 2 条" } }
]
```

- **`--dry-run`**：**仅批量模式**支持（单条模式需走 `items-file` 才能 dry-run）；用于预检。详见 `qingflow record update -h` 与 CLI 报错指引。
- 批量输出优先读顶层语义，不需要再钻进 `data.summary`：
  - `mode="batch"`、`dry_run`
  - `total`、`succeeded`、`failed`、`needs_confirmation`
  - `updated_record_ids`
  - `write_executed`、`safe_to_retry`、`verification_status`
  - `items[].row_number / record_id / status / failed_fields / confirmation_requests`
- `dry_run=true` 时 `write_executed=false`、`safe_to_retry=true`，只能说明预检通过；真正写入仍需去掉 `--dry-run` 再执行。
- `write_executed=true` 后不要盲目整批重试；根据 `items[].row_number` 和 `updated_record_ids` 判断是否只补失败行。

---

## 安全与落盘

- **`record update` 为写操作**；仅在授权环境、**必要时**对测试应用演练。
- **`list` / `get` / `schema browse` / `schema update` / 更新结果** 体大量时按主技能 **落盘规则** 重定向。
- 主技能 **危险操作** 中对 `record update --dry-run`（批量）的说明仍适用。

---

## 排查摘要

| 现象 | 处理 |
| --- | --- |
| 缺 `record_id` | 先用 **`record list`**（同一 `view_id`）或 **`record get`**。 |
| 不知道字段标题或当前值 | 先查 **`record get`** 的 `fields[]`。 |
| 不知道能改哪些题 / 路径失败 | 再查 **`record schema update`** 的 `writable_fields` / `payload_template` / 路径诊断；它不是主链路前置步骤。 |
| 配置类报错 | 单条更新必须 **`--record-id` + `--fields-file`**；批量必须 **`--items-file`**，且勿混用单条参数。 |
| `needs_confirmation` | 尚未写入；从 `confirmation_requests[].candidates[]` 选明确对象/id 后重试，再读回确认。 |
| `40002` | 先看 **`tried_routes`**：如果 `admin_direct` 拒绝但 `view_edit` 或 `task_save_only` 成功，说明某条具体通道不可用但仍有可写路径；如果所有 route 都拒绝，再按权限问题处理。 |
| 成员/部门格式错误 | 与 **创建记录** 文档同一套结构；必要时用 **`record member-candidates` / `record department-candidates`** 走字段候选范围。不要改用 `builder member search` 做记录字段候选。 |
| **`apply_id must be positive`**，或内部报错含 **`exceeds JavaScript's safe integer range`**（单条 **`record update`** 或批量 **非 dry-run**） | **`record_id` 典型超出 JavaScript 安全整数上限**（`Number.MAX_SAFE_INTEGER`，约为 `9007199254740991`）：读链路与 **`schema update`、批量 `--dry-run`** 可走通；**写入**须在 **新版本 CLI** 重做或向维护方确认。短期仅用 **更小 id 的授权测试应用/记录**演练。 |

---

*维护：复核 `qingflow record schema update -h`、`record update -h`；`view_id` 与成员策略以当前 CLI help 与同目录成员速查表为准。*
