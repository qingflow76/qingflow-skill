# Builder Field Modeling And AppForm Pointer

Read this when the task is about app creation fields, schema updates, field types, data title, data cover, relation fields, or system fields.

## Scope

Responsible for: field modeling notes, AppForm field types, data title/cover, relation field shape, and the CLI form write sequence.

Not responsible for: record data operations. Form layout is part of the AppForm `spec.body`; do not use a separate schema/layout write path.

## Main chain

```text
app/package resolve -> builder app-form schema -> draft get for updates -> validate declaration -> apply declaration -> app get fields/layout readback -> publish/readback verify
```

For every app, run `qingflow --json builder app-form schema` and pin the returned schema version. For an update, read `qingflow --json builder app-form get --app-key APP_KEY --being-draft`; validate the complete declaration with `qingflow --json builder app-form validate --schema-version VERSION --file DECLARATION.json`, then apply it with `qingflow --json builder app-form apply --file DECLARATION.json`. The old `builder schema apply`, `--apps-file`, `--form-file`, and `add_fields/update_fields/remove_fields` routes are retired compatibility adapters, not current public commands.

## Demo files

| Scenario | Example |
|----------|---------|
| AppForm declaration shape and CLI sequence | This document: [Create app with AppForm](#create-app-with-appform) and [AppForm scenario matrix](#3-appform-场景矩阵) |
| Historical schema capability probe (not the current 21-type manifest) | [schema_apply_add_fields_all_types.json](../examples/schema/schema_apply_add_fields_all_types.json) |
| Historical existing-app field capability probe | [schema_apply_add_fields_all_types.json](../examples/schema/schema_apply_add_fields_all_types.json) |

## Create app with AppForm

The current creation shape is a complete AppForm declaration: `spec.body` contains fields, sections, rows, and settings. Pin the version with `qingflow --json builder app-form schema`. For updates, preserve IDs from `qingflow --json builder app-form get --app-key APP_KEY --being-draft`; validate and apply through the CLI commands above. Do not call the retired schema/layout CLI adapters.

```json
{
  "apiVersion": "builder.qingflow.com/v1alpha1",
  "packageId": 123456,
  "spec": {
    "appName": "生产工单",
    "dataTitleField": {"name": "工单编号"},
    "body": [
      {
        "kind": "section",
        "title": "基础信息",
        "rows": [
          {"fields": [
            {"name": "工单编号", "type": "text"},
            {"name": "产品", "type": "text"},
            {"name": "状态", "type": "single_select", "config": {"options": ["待排产", "生产中", "已完工"]}}
          ]},
          {"fields": [
            {"name": "计划数量", "type": "number"},
            {"name": "计划完成日期", "type": "date"}
          ]}
        ]
      }
    ]
  }
}
```

Historical CLI shape (retired; do not run):

```bash
qingflow --json builder schema apply \
  --package-id <PACKAGE_ID> \
  --app-name "生产工单" \
  --icon table \
  --color blue \
  --form-file /abs/path/form.json \
  > tmp/schema_apply_production_order.json
```

Historical complete-system item shape (retired; do not run):

```json
{
  "client_key": "production_order",
  "app_name": "生产工单",
  "icon": "table",
  "color": "blue",
  "form": [
    {
      "section": "基础信息",
      "rows": [[{"name": "工单编号", "type": "text", "data_title": true}]]
    }
  ]
}
```

Historical complete-system CLI (retired; do not run):

```bash
qingflow --json builder schema apply \
  --apps-file /abs/path/apps.json \
  > tmp/schema_apply_system.json
```

The following is retained only to recognize a historical `apps-file` payload. It is not a current template: create each app with its own AppForm declaration, save the returned `appKey`, then bind relations with `targetAppKey`.

```json
{
  "package_id": 123456,
  "apps": [
    {
      "client_key": "product",
      "app_name": "产品台账",
      "icon": "database",
      "color": "blue",
      "form": [
        {
          "section": "产品基础信息",
          "rows": [
            [
              {"name": "产品编码", "type": "text", "data_title": true, "required": true},
              {"name": "产品名称", "type": "text", "required": true},
              {"name": "产品状态", "type": "select", "options": ["研发中", "量产", "停用"]}
            ]
          ]
        }
      ]
    },
    {
      "client_key": "production_order",
      "app_name": "生产工单",
      "icon": "table",
      "color": "emerald",
      "form": [
        {
          "section": "工单基础信息",
          "rows": [
            [
              {"name": "工单编号", "type": "text", "data_title": true, "required": true},
              {
                "name": "关联产品",
                "type": "relation",
                "target_app_ref": "product",
                "relation_mode": "single",
                "display_field": {"name": "产品编码"},
                "visible_fields": [{"name": "产品名称"}, {"name": "产品状态"}]
              },
              {"name": "工单状态", "type": "select", "options": ["待排产", "生产中", "已完工"]}
            ],
            [
              {"name": "计划数量", "type": "number"},
              {"name": "计划完成日期", "type": "date"}
            ]
          ]
        }
      ]
    }
  ]
}
```

## Existing-app field maintenance notes

- Re-read the published and draft AppForm before updating; preserve every field and ID that should remain.
- Use complete AppForm target state for additions, edits, layout changes, and removals; never replay a partial field patch.
- Run `qingflow --json builder app-form validate --schema-version VERSION --file DECLARATION.json` before every apply and follow AppForm recovery rules for uncertain write state.

Current updates must be complete AppForm declarations. Start from
`qingflow --json builder app-form get --app-key APP_KEY --being-draft`, keep the existing `appKey`/IDs, change the
desired `spec.body`, validate the complete declaration, and apply it. The old
`add_fields`/`update_fields`/`remove_fields` patch shape is retired and is not a
current CLI payload.

## Field type reference

> **口径**：`field.questionType` 枚举和字段形状以固定版本的 **`qingflow --json builder app-form schema`** 返回结果为准；每个 canonical 类型还可用 `--field-type TYPE` 获取细节，`defaultType: 3` 的公式语法和函数目录用 `--schema-kind formula` 获取。不要从已退休的 `app_schema_apply` contract 推断当前 AppForm payload。
> **CLI**：表单写入使用 `qingflow [--profile NAME] --json builder app-form schema/get/validate/apply`；`validate/apply` 接受 `--file`，`get` 接受 `--app-key`。旧 `builder schema apply` 及 `builder layout apply` 不在当前 parser 的公开命令集合中。
> **新建应用主规则**：`spec.body` 非空时必须用 `spec.dataTitleField` 唯一选择一个顶层字段作为数据标题；数据封面可选，只能用 `spec.dataCoverField` 选择顶层 `attachment` 字段。
> **权限**：包内新建应用按后端 `CreateAppBean` 链路只预检目标包 **AddAppAuth**；已有应用的字段/基础信息变更才走应用自身 **EditAppAuth**。

## 0. 字段建模一眼决策表

先按业务语义选字段类型。当前主路径使用 pinned AppForm Schema 返回的 canonical 类型；历史别名只在迁移旧草稿时识别，不能作为新声明模板。

| 业务语义 | 推荐写法 | 注意 |
| --- | --- | --- |
| 名称、标题、编号、短文本 | `text` | 非空表单必须通过应用级 `dataTitleField` 唯一选择一个顶层字段 |
| 说明、备注、描述、长文本 | `long_text` | 多行文本 |
| 状态、类型、等级、阶段、是否枚举 | `single_select` | 必须在 `config.options` 定义非空字符串数组 |
| 标签、多选项、多个类别 | `multi_select` | 必须在 `config.options` 定义非空字符串数组 |
| 数量、比例、分数、工时、百分比、时长 | `number` | 需要小数或计算时优先 `number` |
| 金额、费用、单价、预算 | `amount` | 只用于货币/金额语义，不要拿它存比例或普通数量 |
| 日期、计划日、截止日 | `date` | 同时需要时分秒才用 `datetime` |
| 负责人、审批人、参与人 | `member` | 不要创建“申请人/提交人”等平台系统字段 |
| 部门、组织 | `department` | 可按需要补 `config.departmentScope` |
| 图片、文件、附件 | `attachment` | 只有顶层 `attachment` 可被应用级 `dataCoverField` 选择 |
| 跨应用业务对象关系 | `relation` | 使用已确认的 `targetAppKey`；`displayField` / `visibleFields` 必须写对象选择器 |

禁止创建平台系统字段：`数据ID`、`编号`、`申请人`、`申请时间`、`创建人`、`创建时间`、`提交人`、`提交时间`、`更新时间`、`更新人`、`当前流程状态`、`当前处理人`、`当前处理节点`、`流程标题`。需要引用系统字段时，只在工具明确支持的位置引用，例如按钮 `source_field: "数据ID"`。

---

## 1. 全部 `field.type`（21 种）

固定 AppForm Schema 中可用的字段类型为：

| `questionType` | 说明（搭建语义） |
|--------|------------------|
| `text` | 单行文本 |
| `long_text` | 多行文本 |
| `number` | 数字 |
| `amount` | 金额 |
| `link` | 链接 |
| `date` | 日期 |
| `datetime` | 日期时间 |
| `member` | 成员 |
| `department` | 部门（可带 `config.departmentScope`） |
| `single_select` | 单选 |
| `multi_select` | 多选 |
| `phone` | 电话 |
| `email` | 邮箱 |
| `address` | 地址 |
| `attachment` | 附件 |
| `single_choice` | 兼容的单选类型；新声明优先使用 `single_select` |
| `q_linker` | 远程查询 / 数据获取（**`config.qLinkerBinding`**） |
| `code_block` | 代码块（**`config.codeBlockBinding`**） |
| `relation` | 关联记录（**`config.relationMode`**：`single` \| `multiple`） |
| `data_relation` | 数据关联/引用填充 |
| `subtable` | 子表（**`subfields[]`**） |

**`config.relationMode`**：仅 **`relation`** 使用，取值为 **`single`** 或 **`multiple`**。一个应用可以有多个 `relation` 字段；不要因为 relation 数量超过 1 就改成文本字段。

### 1.1 历史字段类型别名

主路径使用 pinned AppForm Schema 返回的 canonical 类型；下列别名只用于识别历史载荷，不作为当前声明模板：

| 历史写法 | 当前 canonical 类型 |
|------------|----------------|
| `multiline` / `multiline_text` / `textarea` | `long_text` |
| `select` / `single_choice` / `dropdown` | `single_select` |
| `multi_select` / `multi_choice` / `multiple_choice` / `checkbox` | `multi_select` |

`boolean`、`multiline`、`select`、`checkbox` 等仅是兼容输入，归一化结果以固定版本的 `qingflow --json builder app-form schema --field-type TYPE` 类型详情为准；新声明不要使用这些别名。

---

## 2. 按类型的必填 / 常用可选（写意图）

| `questionType` | 通常必填 | 常见可选 / 约束 |
|--------|----------|-----------------|
| 标量与选择器 | `name` + `questionType`（+ 业务 `beingRequired` 等） | `questionDescription`、`beingRequired`；数据标题和封面在应用级 `dataTitleField/dataCoverField` 中选择；**`single_select` / `multi_select` 的 `config.options` 是非空字符串数组**，如 `["A", "B"]` |
| `department` | 同左 | **`config.departmentScope`**：`mode: all \| custom`；`custom` 时 **`departments[]`**（含 `deptId` 等） |
| `relation` | **`targetAppKey`**；另需 **`displayField`**、**`visibleFields[]`** | **`relationMode`**；目标应用元数据不可读时先读已发布表单，不要猜目标 key |
| `subtable` | **`subfields[]` 非空** | 子列递归同父级规则；使用 Schema 返回的 camelCase 子字段配置 |
| `q_linker` | **`config.qLinkerBinding`**：`inputs`、`request`、**`outputs[]` 每项须含 `targetField`**（能解析到本表单字段） | `request.url` 等须符合**租户/后端远程查询策略**；以字段类型 Schema 返回的配置为准 |
| `code_block` | **`config.codeBlockBinding`**：`inputs`、`code`、**`outputs[]` + `targetField`**；配置 outputs 时，代码必须显式写 **`qf_output = {...}`**，仅 `return {...}` 不会产生可回写结果，且每个 `outputs[].path` 必须从 `qf_output` 取值 | 以字段类型 Schema 返回的 camelCase 配置为准 |

别名：契约会把 `title`/`label` 映射到 **`name`** 等；字段类型自然别名见 §1.1。

### 2.1 `relation` 选择器形态

`relation` 的配置必须使用已确认的目标应用 key；展示字段选择器必须写对象，不要写裸字符串：

```json
{
  "name": "关联产品",
  "type": "relation",
  "config": {
    "targetAppKey": "PRODUCT_APP_KEY",
    "relationMode": "single",
    "displayField": {"name": "产品编码"},
    "visibleFields": [{"name": "产品名称"}, {"name": "产品线"}]
  }
}
```

只在目标应用已经创建并通过 readback 确认后填写 `targetAppKey`。如果返回选择器校验错误，修复 `config.displayField` / `config.visibleFields`，不要重建应用或改 `appKey`。

引用字段的公式默认值写在 `config.defaultValueFormula`，表达式必须符合固定版本 `relation` 字段详情中的 `FormulaExpression`。不要把后端 `referenceConfig` 字段名或其他 Schema 版本的公式写法直接放进声明。

### 2.2 工作流状态字段

要启用工作流的应用，字段阶段就创建一个明确的业务状态单选字段，例如 `状态`、`处理状态`、`审批状态`、`工单状态`、`计划状态`、`报工状态`、`单据状态`。领域结果字段不等价于流程状态；例如质量场景的 `检验结论` 只能表达结果，仍建议另建 `处理状态` 用于流程节点、视图和报表。

---

## 3. AppForm 场景矩阵

| 场景 | 当前入口 | 说明 |
|------|----------------|------|
| 编辑已有应用 | `qingflow --json builder app-form get --app-key APP_KEY --being-draft` -> `qingflow --json builder app-form validate --schema-version VERSION --file DECLARATION.json` -> `qingflow --json builder app-form apply --file DECLARATION.json` | 保留完整 `body` 和现有 IDs；不要提交部分字段 patch |
| 包内新建应用 | `qingflow --json builder app-form schema` -> declaration without `appKey` -> `qingflow --json builder app-form validate --schema-version VERSION --file DECLARATION.json` -> `qingflow --json builder app-form apply --file DECLARATION.json` | 须含 `packageId`、`spec.appName` 和完整 `body`;图标与颜色按应用名生成 |
| 多应用系统 | 每个 app 独立走 AppForm；先创建无关系 app，再用已确认 `appKey` 更新关系 | 不使用旧 `apps-file` 批量 schema 路径 |
| 删除应用 | 显式用户意图 -> `qingflow --json builder app delete --app-key APP_KEY` | 不通过字段删除 |

---

## 4. 仓库示例文件（维护参考）

| 内容 | 位置 |
|------|------|
| **当前完整系统主入口** | [20-build-complete-system.md](./20-build-complete-system.md) |
| **历史字段类型能力探针（不是新建主模板）** | [schema_apply_add_fields_all_types.json](../examples/schema/schema_apply_add_fields_all_types.json)（仅用于旧字段能力覆盖测试；当前新建和更新统一使用上文 AppForm） |
| **`q_linker` / `code_block` / relation 配置**（契约内置形状） | `qingflow --json builder app-form schema --schema-version VERSION --field-type TYPE` 返回的固定版本字段详情 |
| **默认值与其他公式文本** | `qingflow --json builder app-form schema --schema-version VERSION --schema-kind formula` 返回的同版本公式语法、字段引用、运算符和函数目录 |
| 最小新建字段（1 个 text 标题字段） | [schema_add_fields_minimal.example.json](../examples/schema/schema_add_fields_minimal.example.json) |
| 历史 scalar / complex 批测（可选） | [_batch_schema_scalar.json](../examples/schema/_batch_schema_scalar.json)、[_batch_schema_complex.json](../examples/schema/_batch_schema_complex.json) |

---

## 5. 实跑结论

**新建应用**：固定 AppForm schema 版本，使用无 `appKey` 的完整声明创建；字段、分组、行布局和设置统一在 `spec.body` 内表达。字段类型覆盖测试文件只用于能力探针，不作为正式业务应用模板。

**多应用系统**：先创建 relation-independent AppForms，立即记录每个返回的 `appKey`，再用完整 AppForm 更新依赖关系。若写入结果不确定，先读 draft/published form，禁止重放创建、猜名称或使用后缀应用。

**限制（平台硬性）**：relation 字段数量不做“每应用只能一个”的智能体侧限制，按 pinned AppForm Schema、后端校验和写后读回为准。`q_linker` / `code_block` 的配置必须使用当前字段 Schema 返回的 camelCase 形状。

**排障**：`--json`；**`DUPLICATE_FIELD`**；真实写入失败看 `SCHEMA_APPLY_FAILED` 的 `backend_code`、`details.relation_field_count` 和读回矩阵。

## 6. 交叉引用

- 交付主流程（读场 / 改场 / 发布）：[reference/app-delivery-sop.md](./reference/app-delivery-sop.md)（类型速查与 `relation`/`q_linker`/`code_block` 要点）。
- 记录读写 `kind`（与搭建 `type` 不同系）：[QINGFLOW_CLI_FIELD_DATA_TYPES.md](../core/QINGFLOW_CLI_FIELD_DATA_TYPES.md)。
- 主技能：[../SKILL.md](../../SKILL.md)。
