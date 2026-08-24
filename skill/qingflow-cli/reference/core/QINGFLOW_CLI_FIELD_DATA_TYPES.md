# Qingflow CLI：字段数据类型（Schema / 列表 / 写入）

> **用途**：说明 **`record schema …`** 的 **`fields[]`**、**`record list` / `record get` / `record access`** 行内值、以及 **insert/update 写入 payload** 的常见对应关系；并单独说明 **选项联动、关联记录、引用填充、公式/系统题、AI 与受限类型** 等在 CLI 下的表现与处置。
> **依据**：当前 CLI 在 **`--json`** 下会对 **schema** 响应做 **裁剪**：通常只保留本节列出的键；**`kind`** 由内部写入类别归并而来（见下表）。**`que_type` 等若未出现在输出中**，以 **`kind` + 实跑预检** 为准。
> **关联**：写入值细节与成员/部门见 **[QINGFLOW_CLI_RECORD_CREATE_WORKFLOW.md](../record/QINGFLOW_CLI_RECORD_CREATE_WORKFLOW.md)**；更新流程见 **[QINGFLOW_CLI_RECORD_UPDATE_WORKFLOW.md](../record/QINGFLOW_CLI_RECORD_UPDATE_WORKFLOW.md)**；只读见 **[QINGFLOW_CLI_DATA_RETRIEVAL_WORKFLOW.md](./QINGFLOW_CLI_DATA_RETRIEVAL_WORKFLOW.md)**；**搭建侧** AppForm 的 `type`（与本文 `kind` 命名体系不同）及其 CLI 命令见 **[30-schema-fields.md](../builder/30-schema-fields.md)**；主技能 **[../SKILL.md](../../SKILL.md)**。

---

## 1. `fields[]` 通用结构（`--json` 精简后）

| 字段 | 含义 |
|------|------|
| **`field_id`** | 内部题 id（数字）；**`record_access.columns` / `where-file` / `order-by-file` 等 DSL** 常以此引用列。 |
| **`title`** | 题目标题；insert/update 的 `fields` map 键通常与之一致。 |
| **`kind`** | 见 **§2 `kind` 枚举**；决定读写时值的形态。 |
| **`options`** | 可选；**`kind=select`** 时常为允许选项的字符串列表。 |
| **`target_app_key`** | 可选；**`kind=relation`** 时关联目标应用。 |
| **`searchable_fields`** | 可选；**`kind=relation`** 时在关联侧可用来检索的字段说明。 |
| **`row_fields`** | 可选；**`kind=subtable`** 时子表列的子 schema（递归同类结构）。 |
| **`required`** | 部分场景（如 **`record schema update`** 拆出的 `required_fields` / `optional_fields`）出现。 |
| **`template`** | 少数响应里与 **`payload_template`** 联动出现，供生成初稿。 |

**browse 与 detail**：`browse` 产出视图表头的精简 **`fields[]`**；`record get` 产出当前记录详情字段。一般 **不含** 完整 **`que_type`/`writable`** 元数据。更新主链路先用 **`record get`** 的字段信息组 payload，再执行 **`record update`**；只有更新失败、字段歧义或需要诊断可写范围时，再结合 **`record schema update`**（按记录）或写入返回判断。

---

## 2. `kind` 枚举（CLI 对外）

内部写入类别经归并后形成下表 **`kind`**（与 `qingflow` 当前实现一致；升级后请以 **`record schema … --json` 实跑** 为准）：

| CLI `kind` | 维护侧常见内部类别（参考） | 在 `record list` / `record get` / `record access` 中（常见） | insert/update 写入值 |
|------------|-----------------------------------|--------------------------------------------|----------------------------------|
| **`scalar`** | `scalar_text`、`boolean_label`、`date_string` 及未映射类型默认归此 | 多为 **字符串或数字** JSON 标量；布尔/日期常以 **展示字符串** 出现；**地址**题在精简里常仍归 **scalar**，写入时按 **地址对象/分段**（见创建记录文档） | **字符串 / 数字 / 布尔** 等；具体以后端预检为准 |
| **`select`** | `single_select`、`multi_select` 合并为同一 kind（**§3.1**） | **单选**：与选项同文案的字符串；**多选**：字符串数组或实现可识别的列表 | **单选**：**`options` 中某一元素的字符串**（或实现接受的选项对象）；**多选**：**数组** |
| **`member`** | `member_list` | 常为人类可读名；或对象（含 id、邮箱等，随租户配置） | 优先自然语言字符串，如 `"张三"`；`needs_confirmation` 时按候选改显式对象，如 `{"uid":1048599,"name":"沈嘉慧Seth","email":"..."}` |
| **`department`** | `department_list` | 部门名或 id 形态 | 优先自然语言字符串，如 `"直销部"`；`needs_confirmation` 时按候选改显式对象/id |
| **`relation`** | `relation_record`（**§3.2**） | 常为关联展示字段或 `apply_id` 相关信息 | **`apply_id`**、可解析对象或自然语言；多匹配会返回 `needs_confirmation`，需选候选后重试 |
| **`attachment`** | `attachment_list` | URL、文件名或结构化附件对象 | **`{"value"或"url", "name"?}`**；常需 **`builder file upload-local` 先上传** |
| **`address`** | `address_parts`（**对外 `kind` 常被映射进 `scalar`**，以实跑为准） | 对象或分段地址 | **省/市/区/detail 对象** 或 **有序片段数组**（见 **[QINGFLOW_CLI_RECORD_CREATE_WORKFLOW.md](../record/QINGFLOW_CLI_RECORD_CREATE_WORKFLOW.md)**） |
| **`subtable`** | `subtable_rows` | **行数组**；行内键为子列 title | **行数组**；行内 **`title → 值`**；更新行可带 **`row_id`/`__row_id__`**（见实现） |
| **`unsupported`** | `unsupported_direct_write`（**§3.4、§3.5**） | 只读/仅流程内填写等 | **勿直接写入**；预检会 `UNSUPPORTED_WRITE` / 类似 blockers |

说明：

- **单选/多选**在对外 `kind` 上 **同是 `select`**；以 **`options` 是否存在 + 业务语义** 区分；多选写入用 **数组**。
- **`scalar`** 是 **桶类型**：文本、数字、金额、日期、布尔等在对外展示上常同为 `scalar`，**具体校验以后端与预检为准**。数字/金额能否写小数以 insert/update schema 的 `expected_format`、`example_value` 和实际错误为准；不要仅凭字段标题或 builder `number` 推断可写 decimal。
- **`field_id=0`** 等系统列可能为 **`system`+只读**；不要写入 insert/update payload（见创建文档「系统维护字段」）。

---

## 3. 特殊字段详解（选项联动、关联、引用、受限类型）

本节对应轻流里常见的 **「选项」「选项联动」「关联记录」「引用/数据联动」** 等；CLI 侧大多仍落在 **`kind=select` / `relation` / `scalar` + 只读** 等组合上，需结合 **预检** 理解。

### 3.1 选项字段（单选 / 多选）

| 概念 | CLI 表现 | 读写注意 |
|------|----------|----------|
| **单选** | 内部题类型常为 **10、11**；对外 **`kind=select`**，多带 **`options` 字符串列表** | **列表/详情**：常为与选项 **完全一致** 的展示文案。写入：传 **`options` 中某项字符串**（或预检接受的选项对象） |
| **多选** | 内部题类型常为 **12、15**；对外仍为 **`kind=select`**（与单选 **同名 kind**） | **列表/详情**：常为 **字符串数组** 或可解析的多值结构。写入：传 **JSON 数组**（每个元素对应一个选项值） |
| **区分单多选** | 精简 schema **仅有 `kind`+`options`** | 以 **表单配置 / 同一 `title` 在别处的表现 / 写入预检** 为准；**唯一写入层面**的硬规则是：**多选必须按数组传** |

**选项联动（控制显隐、必填等）**

- 实现上来自 **题目关系 + 选项上的联动题 id**（如其它题因当前选项而被激活）。
- **`record schema browse` 的 `--json`**：精简 `fields[]` 可能不展示完整 `linkage` / 联动明细；新建记录以 [record/insert](../record/insert/README.md) 的 `record schema insert` 为准，不要用兼容保留的 applicant schema 入口替代。
- **写入时**：若更新返回提示 **上游未选、联动未激活、字段尚未显示**，应 **先写或改 payload 里处于上游的选项（或其它驱动题）**，再写下游；必要时用 **`record schema update --record-id …`** 诊断当前记录下 **`required_fields` / `optional_fields` / `payload_template`**。

### 3.2 关联字段（关联记录）

| 概念 | CLI 表现 | 读写注意 |
|------|----------|----------|
| **关联记录** | 内部题类型 **25**；对外 **`kind=relation`** | Schema 常含 **`target_app_key`**，以及可选 **`searchable_fields`**（在 **被关联应用** 侧参与检索的字段线索） |
| **列表/详情** | 多为 **展示用字符串** 或结构化片段（以租户配置为准） | 不要猜测 `apply_id`；从 **关联列表 / 人工指定 / 预检返回的候选** 取得 |
| **写入 payload** | 「选中一条被关联记录」 | 优先传可被唯一解析的自然语言（如客户名/项目名）或 `{"apply_id":"..."}`；**多匹配** 时易出现 **待确认候选** 或 **阻断**（按返回 `confirmation_requests` / `blockers` 处理） |

**`needs_confirmation`**：表示工具没有写入（`write_executed=false`），只是返回候选。成员、部门、关联字段都可能触发；应从 `confirmation_requests[].candidates[]` 选一个候选对象/id 重试，成功后再报告最终结果。

### 3.3 「引用」与数据填充（非独立 `kind`）

产品里的 **「引用」** 常指：**本题由其它题（选项、关联、成员等）通过规则自动带出**，对应表单元数据中的 **引用/填充配置**。

| 现象 | 建议 |
|------|------|
| 目标列 **只读** 或预检判定 **只能通过上游带出** | **不要**在 payload 里强行赋值；改 **上游题**（选项、关联、`relation`、`member` 等），让服务端重算 |
| 目标列 **`kind` 仍是 `scalar` / `select`** | **「引用」不是单独对外 `kind`**；是否可手填以 **`writable` / 预检 / `record schema update`** 为准 |
| 需要联动说明 | 非精简 schema 中可能出现 **`linkage`** 类结构（如引用链角色）；**当前 CLI `--json` 精简常去掉 `linkage`**，以 **实跑预检错误信息** 与 **表单设计** 为准 |

**公式、默认值**：若题目由 **公式或默认规则** 计算，常与 **只读 / 系统题** 同类处理，以 **`UNSUPPORTED_WRITE`、`READONLY_OR_SYSTEM_FIELD`** 等预检结果为准。

### 3.4 受限或禁止直写的类型（实现约定）

下列为 **当前 CLI 写入规范化实现** 中的典型 **`unsupported_direct_write`**（对外 **`kind=unsupported`**），**不要依赖 CLI 直接构造复杂载荷**：

| 内部 `que_type`（维护参考） | 含义（简述） |
|-----------------------------|--------------|
| **14** | **时间区间** 等：需要后端原生结构，CLI 侧不承诺拼装正确 |
| **34** | **图像识别**（运行时 AI） |
| **35** | **AI 生图**（运行时 AI） |
| **36** | **文档解析**（运行时 AI） |

**处置**：改在 **轻流界面 / 流程节点** 中产生这些值；或缩小 payload 仅写 **不受支持的题之外** 的字段。

### 3.5 其它 layout / 展示类

内部 **24** 等为 **布局/说明** 类题，通常 **不出现在可写字段** 中；若误入 payload，以预检 **`unsupported`** / **`readonly`** 为准剔除即可。

---

## 4. 与 `field_id` / 列选择


- **`record list --column`**：参数为 **数字列 id**，用于样本/候选列表展示列，须与 **`fields[].field_id`** 一致。
- **`record get`**：默认读取前端详情页首屏上下文；不要把 `--column` 当成详情字段投影主路径，单条字段、首屏日志、引用、图片/文件资产以 `record_get` 的结构化上下文为准。若用户要完整数据日志/流程日志历史，用 `record logs`。
- **标题重复**：同一 `title` 可能对应多个 `field_id`（极少见）；列表 DSL 应用 **`field_id`** 消歧。

---

## 5. 读者操作建议

1. **按场景取上下文**：只读/定位视图列用 `record schema browse --view-id …`；新建用 `record schema insert --app-key …`；更新用 `record get --record-id …` 先读当前记录详情，再用 `record update` 写入；`record schema update --record-id …` 只在失败、字段歧义或显式诊断时使用。
2. **数据分析**：最终统计结论、分析报告、趋势/排名/比例/分布必须走 **[record/analysis](../record/analysis/README.md) 的 `record access -> Python/pandas`**。
3. **看 `kind` + `options` / `row_fields` / `target_app_key`**，并对照 **§3 特殊字段** 判断是否存在联动、引用或只读带出。
4. **选项联动 / 引用带出**：先写 **驱动题**，再写 **被带出的题**；只读带出列 **不要强写**。
5. **写入前缩小 payload**；insert 默认用 `record insert --items-file`，单条也是 `items` 数组一行。根据 **`status` / `blockers` / `field_errors` / `failed_fields` / `created_record_ids`** 迭代（`--json` 在 stdout）。

---

*维护：`kind` 集合与精简字段以当前 CLI 的 `record schema … --json` 实跑为准；内部 `que_type` 枚举随轻流版本变化，文档只稳定描述对外 **`kind`** 桶。*
