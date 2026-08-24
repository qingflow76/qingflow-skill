# Qingflow CLI 工作流搭建

## 快速索引

| 主题 | 文件 |
|------|------|
| 依赖命令、能力边界 | [01-overview.md](./01-overview.md) |
| 更新模式与最小修改原则 | [02-update-mode.md](./02-update-mode.md) |
| 流程模式速查（线性/分支/回退） | [03-flow-patterns.md](./03-flow-patterns.md) |
| 阶段 1：业务建模与自检 | [04-stage1-business-modeling.md](./04-stage1-business-modeling.md) |
| 阶段 2：成员/角色搜索 | [05-stage2-members-roles.md](./05-stage2-members-roles.md) |
| 阶段 3：Schema + 构建流程输入 | [06-stage3-build-spec.md](./06-stage3-build-spec.md) |
| 阶段 4：验证流程输入 | [07-stage4-validate-spec.md](./07-stage4-validate-spec.md) |
| 阶段 5：Apply + 验证循环 | [08-stage5-apply-verify.md](./08-stage5-apply-verify.md) |
| 阶段 6：总结报告与回退 | [09-stage6-summary.md](./09-stage6-summary.md) |
| 节点配置参考 | [10-node-config-reference.md](./10-node-config-reference.md) |
| 常见问题与排障 | [11-troubleshooting.md](./11-troubleshooting.md) |

---

## 一、思考（Thought）：何时启用与前置条件

### 触发条件

当用户要求**在轻流应用中搭建工作流**时阅读本节，典型触发语：

- "帮我搭建审批流程"
- "在这个应用里创建工作流"
- "按照这张流程图实现工作流"
- "配置流程分支条件"
- "给这个应用加一个审批节点"

### 前提检查（进入行动前必须完成）

在开始任何搭建操作前，按顺序确认以下条件：

1. **应用存在性**：`qingflow --json app get --app-key <APP_KEY>` 成功返回
2. **字段就绪**：`qingflow --json builder app get --app-key <APP_KEY> fields` 返回字段列表，确认业务建模所需字段（如单选框、成员、部门字段）均已存在；流程应用还需要明确的业务状态单选字段（如 `状态`、`处理状态`、`审批状态`、`工单状态`、`计划状态`、`报工状态`、`单据状态`），不要只用 `检验结论` 这类结果字段替代状态字段
3. **未启用已有流程**（新建场景）：`qingflow --json builder app get --app-key <APP_KEY> flow` 查看 `enabled` 状态，若已有流程则为**更新模式**

**不满足时的处理**：
- 应用不存在 → 先完成应用搭建和字段配置，再继续工作流搭建
- 字段缺失 → 先补充缺失的字段定义，再继续工作流搭建
- 应用已启用流程 → 进入更新模式（读取现有 spec 再修改）

### 能力边界

| 在范围内 | 超出范围 |
|----------|----------|
| 基于已有应用搭建工作流 | 从零创建应用 |
| WorkflowSpec 生成与 apply；`patch_nodes` 仅用于已有节点局部维护 | 操作复杂命令拼接 |
| 审批/填写/抄送/自动化/分支条件等 WorkflowSpec 支持的流程 | 不读 schema/spec 就猜 raw 后端字段 |
| 审批/填写/抄送/自动化节点配置 | 修改字段定义 |
| 成员/角色搜索用于节点负责人 | 组织架构管理 |
| 验证 → apply → 校验循环 | 前端 UI 拖拽操作 |

完整命令与依赖说明见 [01-overview.md](./01-overview.md)。
辅助脚本已合并到 `qingflow-cli/scripts/workflow/`。

---

## 二、行动（Action）：核心 SOP

按顺序执行以下阶段，每个阶段详见对应 reference 文件：

| 阶段 | 任务 | 参考文件 |
|------|------|----------|
| 阶段 0 | 判断是否为更新模式，确认最小修改原则 | [02-update-mode.md](./02-update-mode.md) |
| 阶段 1 | 提取业务建模，完成七维度业务自检 | [04-stage1-business-modeling.md](./04-stage1-business-modeling.md) |
| 阶段 2 | 搜索成员/角色，用于节点负责人配置 | [05-stage2-members-roles.md](./05-stage2-members-roles.md) |
| 阶段 3 | 获取 Schema、读取现有流程、构建 WorkflowSpec；已有节点小改才用 patch_nodes | [06-stage3-build-spec.md](./06-stage3-build-spec.md) |
| 阶段 4 | 验证 WorkflowSpec / patch_nodes | [07-stage4-validate-spec.md](./07-stage4-validate-spec.md) |
| 阶段 5 | Apply 工作流并验证部署结果 | [08-stage5-apply-verify.md](./08-stage5-apply-verify.md) |

构建流程输入前，若对流程模式有疑问，先查阅 [03-flow-patterns.md](./03-flow-patterns.md)。

---

## 三、反思（Reflection）：验证与总结

| 阶段 | 任务 | 参考文件 |
|------|------|----------|
| 阶段 6 | 输出结构化搭建报告，回顾业务完整性 | [references/09-stage6-summary.md](./09-stage6-summary.md) |

搭建失败时的回退策略、节点配置细节、常见问题排障分别见：
- [references/09-stage6-summary.md](./09-stage6-summary.md)
- [references/10-node-config-reference.md](./10-node-config-reference.md)
- [references/11-troubleshooting.md](./11-troubleshooting.md)
