# 记录批量导入 SOP：`app_get`（`import_capability`）→ 模板 → 校验 →（可选）本地修复 → 启动 → 状态

本文与 **MCP 工具命名**一致，并映射到 **`qingflow` CLI**。编写前已 **实跑**：`app get`、`record schema import`、`import template`、`import verify`、`import repair`（未授权分支 + 授权分支遇 **合并单元格** 异常）、`import start`、`import status`（**仅** `--import-id`）；环境为当前持久化 CLI 会话、应用 `ead8ims5i401`。

---

## 1. 编排顺序（固定）

| 顺序 | 工具名 | CLI | 说明 |
|------|--------|-----|------|
| 1 | `app_get` | `qingflow --json app get --app-key <APP_KEY>` | 读 **`data.import_capability`**，预检是否有导入能力 |
| （可选） | `record_import_schema_get` | `qingflow --json record schema import --app-key <APP_KEY>` | `schema_scope: import_ready`，列 **`columns`**；能力仍以 **`app get`** 为准 |
| 2 | `record_import_template_get` | `qingflow [--json] import template --app-key <APP_KEY> [--download-to-path <PATH>]` | 官方模板 URL 或 **本地生成的 applicant 模板**（无数据管理权限或导入权限预检未知时可能 fallback） |
| 3 | `record_import_verify` | `qingflow [--json] import verify --app-key <APP_KEY> --file-path <*.xlsx\|*.xls>` | 产出 **`verification_id`**；**`can_import`** 为真后才应 **`import start`** |
| （可选） | `record_import_repair_local` | `qingflow [--json] import repair --verification-id <UUID> --authorized-file-modification …` | **必须** 显式授权；**仅 `.xlsx`**；可重复 **`--repair`** |
| 4 | `record_import_start` | `qingflow [--json] import start --app-key <APP_KEY> --verification-id <UUID> --being-enter-auditing <true\|false> [--view-key …]` | **会真实发起导入** |
| 5 | `record_import_status_get` | `qingflow [--json] import status (--app-key \| --import-id \| --process-id-str)` **三者择一** | **不要**同时传多个 selector（例如 **`--import-id` 与 `--app-key` 同时**会被 CLI 拒绝） |

CLI 注册见全局包 **`qingflow_mcp/cli/commands/imports.py`**（`template` / `verify` / `repair` / `start` / `status` → 上述 `ImportTools` 方法）。

---

## 2. `import_capability`（来自 `app get`）

`app get` 在 **`data.import_capability`** 中附带由 `baseInfo` 推导的能力（实现：**`_derive_import_capability`**）：

| 字段 | 含义 |
|------|------|
| **`can_import`** | `true` / `false` / `null`（未知） |
| **`auth_source`** | `apply_auth`（申请人导入开关）、`data_manage_auth`（数据管理）、`none`、`unknown` |
| **`applicant_import_enabled`** | 与 `dataImportStatus` 对应 |
| **`data_manage_status`** | 与 `dataManageStatus` 对应 |
| **`runtime_checks_required`** | 预检后仍可能受 **`user_disabled`**、**`function_demoted`** 等运行态影响 |
| **`confidence`** | `preflight`（由元数据推出）或 `unknown` |

- **`record_import_schema_get` / `record_import_template_get` / `record_import_verify`**：若 `can_import === false` 且来源非 `unknown`，会直接 **`IMPORT_AUTH_PRECHECK_FAILED`**，不会继续读取导入列、官方模板或进入后端文件校验。
- **`record_import_template_get`**：当具备申请人导入能力但无数据管理权限时，可能对 **`/app/{appKey}/apply/excelTemplate`** 失败并 **本地生成** applicant 模板（警告 **`IMPORT_TEMPLATE_LOCAL_FALLBACK`**）。
- 若 **`app get` / `baseInfo`** 权限受限导致 **`import_capability.auth_source: unknown`**，但 applicant 字段 schema 可读，且官方模板接口返回 **40002 / 40027**，`record_import_template_get` 也可能返回 **`status: partial_success`** 并本地生成模板（警告 **`IMPORT_TEMPLATE_LOCAL_FALLBACK_AUTH_UNKNOWN`**）。这只说明“模板准备成功”，**不证明用户有导入权限**；后续仍以 **`record_import_verify` / `record_import_start`** 的 `can_import` 与最终结果为准。

---

## 3. 本地校验仓与运行环境

- **`verification_id`** 由 **`record_import_verify`** 生成，并写入本机 **`~/.qingflow-mcp/import-verifications/<id>.json`**（**`ImportVerificationStore`**）。
- **`record_import_start` / `repair`** 依赖该目录；**自动化/CI 需允许写此目录**，且 **`verify` → `start` 须在** 同一 profile、可达后端的会话内完成。
- **`record_import_status_get`** 在仅传 **`--import-id`** 时，会结合本地 **`ImportJobStore`** 与后端 **`GET /app/apply/dataImport/record`** 解析 **`app_key` / `process_id_str`**；与 **`import start`** 返回的 **`import_id`**、**`process_id_str`** 对齐使用。

---

## 4. 命令要点

### 4.0 文件形态、CSV 源数据与字段映射

- 当前 `import verify/start` 主链路面向官方 Excel 模板（`.xlsx` / `.xls`），不是直接把任意 CSV 交给后端。
- CSV 可以作为源数据或中间表，但必须先映射到官方模板列名，再写入模板副本；不要改模板表头。
- 字段映射以 `record schema import` / 模板列为准：源列名可以是用户习惯名，目标列名必须是官方模板 header。
- 关联字段批量导入优先使用稳定 `record_id` 或 schema 明确支持的唯一搜索值；显示名可能重复时不要猜。
- 成员/部门字段必须使用 schema/candidate 范围内的值；选项字段优先使用模板里的选项文案。

CSV 源数据示例（规划用）：

```csv
客户名称,关联客户,状态,负责人
上海示例客户,CUST_RECORD_ID_001,有效,张三
```

映射到模板后的行语义：

```json
{
  "客户名称": "上海示例客户",
  "关联客户": "CUST_RECORD_ID_001",
  "状态": "有效",
  "负责人": "张三"
}
```

### 4.1 模板

```bash
qingflow --json import template --app-key "<APP_KEY>" \
  --download-to-path tmp/qingflow_import_template.xlsx \
  > tmp/qingflow_import_template_meta.json
```

- 关注 **`verification.template_source`**：`official` 或本地 fallback。
- 若 `verification.import_auth_prechecked: false`，表示模板来自 schema 可读分支但导入权限尚未预检成功；不要把该模板结果当作导入授权结论。
- **`expected_columns`** 在部分响应负荷中给出；**与校验**一致。

### 4.2 校验

```bash
qingflow --json import verify --app-key "<APP_KEY>" \
  --file-path tmp/qingflow_import_template.xlsx \
  > tmp/qingflow_import_verify.json
```

- 始终解析 **`verification_id`**；仅 **`can_import: true`** 时进入后端 multipart **`/upload/verification`**。
- **标准输出**上 OpenPyXL 可能对某些 xlsx 打出 **`UserWarning`**（**出现在 JSON 前**）。 jq/直解 **`json.load` 失败时，从首个 `{` 起截取再解析**。

### 4.3 本地修复（可选）

```bash
qingflow --json import repair \
  --verification-id "<VERIFICATION_UUID>" \
  --authorized-file-modification \
  [--output-path tmp/repaired.xlsx] \
  [--repair normalize_headers] [--repair trim_trailing_blank_rows] \
  ... \
  > tmp/qingflow_import_repair.json
```

- **未加** `--authorized-file-modification` → **`IMPORT_REPAIR_NOT_AUTHORIZED`**。
- **`--repair`** 可重复；允许集合（实现 **`SAFE_REPAIRS`**）：  
  **`normalize_headers`**、**`trim_trailing_blank_rows`**、**`normalize_enum_values`**、**`normalize_date_formats`**、**`normalize_number_formats`**、**`normalize_url_cells`**。  
  **省略 `--repair`** 时实现默认对 **全集** 尝试。
- **仅 `.xlsx`**；**合并单元格表格** 在 **`normalize_headers`** 等路径上可能触发 **`MergedCell` 只读** 类异常（实跑曾遇到）；此时应改模板或跳过 repair、重新导出模板再 **`verify`**。

成功时返回 **`new_verification_id`**，后续 **`start`** 应用 **新 ID**（若 repair 后重新校验通过）。

### 4.4 启动导入

```bash
qingflow --json import start \
  --app-key "<APP_KEY>" \
  --verification-id "<VERIFICATION_UUID>" \
  --being-enter-auditing false \
  [--view-key "<VIEW_KEY>"] \
  > tmp/qingflow_import_start.json
```

- **`--being-enter-auditing`**：**必填**，布尔字面量：`true` / `false` / `1` / `0` / `yes` / `no` 等（见 argparse `parse_bool_text`）。
- **会校验**：校验记录仍存在、**`can_import`**、**文件 sha256** 未变、**`schema_fingerprint`** 未变；否则 **`IMPORT_VERIFICATION_STALE`** / **`IMPORT_FILE_CHANGED_AFTER_VERIFY`** / **`IMPORT_SCHEMA_CHANGED_AFTER_VERIFY`**。

### 4.5 状态

**参数规则（CLI）**：**必须且只能** 提供 **`--app-key`**、**`--import-id`**、**`--process-id-str`** 中的 **一个**。

```bash
# 已知本次 start 返回的 import_id（不要同时加 --app-key）
qingflow --json import status --import-id "<IMPORT_UUID>" \
  > tmp/qingflow_import_status.json

# 或只看该应用最近一次导入（仅 --app-key）
qingflow --json import status --app-key "<APP_KEY>" \
  > tmp/qingflow_import_status_latest.json
```

---

## 5. 与 `record schema import` 的关系

- **`record schema import`**：专注 **导入列 / 指纹**（与校验用的 schema bundle 一致思路），**不替代** **`app get` 的 `import_capability`**。
- 推荐顺序：**`app get`（能力）** →（可选）**`record schema import`（列清单）** → **`import template`** → …

---

## 6. 实测摘要（编写时）

| 步骤 | 结果 |
|------|------|
| `app get` | `import_capability.can_import: true`，`auth_source: data_manage_auth` |
| `record schema import` | `schema_scope: import_ready` |
| `import template --download-to-path` | 落盘 xlsx 成功 |
| `import verify` | `can_import: true`，`verification_id` 可用；可能有 **`IMPORT_HEADERS_AUTO_NORMALIZED`** |
| `import repair --authorized-file-modification` | 特定模板因 **合并单元格** 在 **`normalize_headers`** 崩溃；属 **模板/实现边界** |
| `import start` | `status: accepted`，返回 **`import_id`**、**`process_id_str`** |
| `import status --import-id …` | 返回 `app_key`、**`process_id_str`**、**`status`**（后端枚举字符串，如实测 `"3"`） |
| `import status --import-id … --app-key …` | **CLI 拒绝**：只能选一个 selector |

---

## 7. 交叉引用

- 主技能 [SKILL.md](../SKILL.md)：**落盘**、导入类权限码 **`IMPORT_*`** 提示。
- [QINGFLOW_CLI_ADMIN_CHEATSHEET.md](./QINGFLOW_CLI_ADMIN_CHEATSHEET.md)：管理侧与 **`IMPORT_*`** 失败排查。
