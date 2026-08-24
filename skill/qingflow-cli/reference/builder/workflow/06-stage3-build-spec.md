# 阶段 3：获取 Schema + 构建流程输入

## 3.1 获取当前工作流 Schema

```bash
qingflow builder flow schema --json > tmp/flow_schema.json
```

> 注意：若已在阶段 1 前执行过，可复用。建议每次搭建前刷新以获取最新 schema。

## 3.2 读取现有 Flow Spec（更新模式下必须执行）

```bash
qingflow --json builder flow get --app-key <APP_KEY> > tmp/current_flow.json
```

从返回的 `spec` 中提取 `nodes` 和 `edges` 作为修改基础。

**更新模式下**：如果走 `patch_nodes[]`，直接使用读回的 `spec.nodes[].id` 做局部修改；如果提交完整 `--spec-file`，用 diff 脚本确认变更范围是否符合预期：

```bash
python3 scripts/workflow/diff_flow_spec.py tmp/current_flow.json tmp/flow_spec.json
```

新建场景可跳过此步。

## 3.3 主路径：构建 WorkflowSpec

`--spec-file` 用于已经从 `builder flow schema` / `builder flow get` 读回并理解的 WorkflowSpec。节点结构、节点 id、负责人、字段权限和边条件都以 schema/readback 为准。

所有需要继续向下路由的节点都显式写 `sync: true`。Q-Robot 也在 WorkflowSpec 中表达为 `type: "automation"`，由 `attrs.subType` 选择具体能力。

WorkflowSpec 示例：

```json
{
  "nodes": [
    {
      "id": "n1",
      "type": "applicant",
      "name": "员工提交申请",
      "sync": true,
      "attrs": {}
    },
    {
      "id": "n2",
      "type": "approval",
      "name": "部门经理审批",
      "sync": true,
      "attrs": {
        "responsible": [
          {"type": "role", "roleId": 123}
        ],
        "approveType": "or_signed",
        "auditUserType": "role",
        "revert": true,
        "revertScope": "all",
        "transferScope": "all"
      }
    },
    {
      "id": "g1",
      "type": "gateway",
      "name": "服务类型判断",
      "sync": true,
      "attrs": {"mode": "parallel"}
    },
    {
      "id": "n3",
      "type": "filling",
      "name": "补充信息",
      "sync": true,
      "attrs": {
        "responsible": [
          {"type": "user", "uid": 456}
        ]
      }
    },
    {
      "id": "n4",
      "type": "approval",
      "name": "技术服务审批",
      "sync": true,
      "attrs": {
        "responsible": [
          {"type": "role", "roleId": 456}
        ],
        "approveType": "or_signed",
        "auditUserType": "role"
      }
    },
    {
      "id": "g2",
      "type": "gateway",
      "name": "分支汇合",
      "sync": true,
      "attrs": {"mode": "join"}
    }
  ],
  "edges": {
    "edges": [
      {"from": "n1", "to": "n2"},
      {"from": "n2", "to": "g1"},
      {
        "from": "g1",
        "to": "n3",
        "label": "客诉",
        "condition": {
          "kind": "rules",
          "autoJudges": [
            [
              {
                "fieldId": 343290994,
                "fieldType": "single_select",
                "matchType": "literal",
                "judgeType": "equals",
                "values": ["客诉"]
              }
            ]
          ]
        }
      },
      {
        "from": "g1",
        "to": "n4",
        "label": "技术服务",
        "condition": {
          "kind": "rules",
          "autoJudges": [
            [
              {
                "fieldId": 343290994,
                "fieldType": "single_select",
                "matchType": "literal",
                "judgeType": "equals",
                "values": ["技术服务"]
              }
            ]
          ]
        }
      },
      {"from": "n3", "to": "g2"},
      {"from": "n4", "to": "g2"}
    ]
  }
}
```

## WorkflowSpec 节点类型速查

| type | 说明 | 必要 attrs |
|------|------|-----------|
| `applicant` | 工作流入口（仅1个） | 可选: `commentStatus`, `submitText`, `fieldPermissions` |
| `approval` | 审批节点 | `responsible`, `approveType`, `auditUserType` |
| `filling` | 填写节点 | `responsible` |
| `gateway` | 分支/汇合 | `mode`: `parallel`（分支）或 `join`（汇合） |
| `cc` | 抄送节点 | `receivers` |
| `automation` | 自动化/Q-Robot | `subType` + 对应配置 |

## 边条件体系

本节属于 `--spec-file` WorkflowSpec 路径。不要凭记忆手写 `autoJudges`、`judgeType` 或 raw `fieldId` 条件；先读 `builder flow schema` / `builder flow get`，再按读回结构修改。

| condition.kind | 含义 | 要求 |
|---------------|------|------|
| `rules` | 条件选路 | 必须含 `autoJudges`（OR-of-AND 二维数组） |
| `default` | 兜底边 | 无 `autoJudges` |
| 省略 | 无条件线性边 | — |

## autoJudges 结构

OR-of-AND 二维数组：

```json
"autoJudges": [
  [  // OR 组 1
    {"fieldId": N, "fieldType": "single_select", "matchType": "literal", "judgeType": "equals", "values": ["选项"]}
  ],
  [  // OR 组 2
    {"fieldId": M, "fieldType": "single_select", "matchType": "literal", "judgeType": "equals", "values": ["另一个选项"]}
  ]
]
```

**关键约束：`autoJudges` 必须是 `[[{...}]]` 二维数组！一维数组 `[{...}]` 格式会被后端静默吞掉。**

**judgeType 常用值**：`equals`, `not_equals`, `equals_any`, `includes`, `greater_than` 等（共21种，详见 schema）。

## 3.4 局部修改 patch_nodes

局部修改现有流程时，先 `builder flow get`，使用读回 `spec.nodes[].id`：

```json
[
  {"id": "89160906", "set": {"name": "需求评审（局部改）"}}
]
```

```bash
qingflow --json builder flow apply \
  --app-key <APP_KEY> \
  --patch-nodes-file tmp/flow_patch_nodes.json \
  --publish \
  > tmp/flow_patch_apply.json
```

---

← 上一步：[05-stage2-members-roles.md](05-stage2-members-roles.md)
← 返回主流程：[../SKILL.md](../../../SKILL.md)
→ 下一步：[07-stage4-validate-spec.md](07-stage4-validate-spec.md)
