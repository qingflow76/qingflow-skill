---
name: qingflow-workflow-builder
description: |
  在已有的轻流应用中，根据业务建模通过 qingflow CLI 或统一 Qingflow MCP 声明式搭建工作流。
  适用场景：应用已存在、字段已就绪，需要创建或更新审批/填写/网关/自动化/抄送流程。
  不适用场景：应用不存在或字段缺失——应先通过 `qingflow-app-form` Skill 完成应用表单/字段，再使用本 Skill。
---

# 轻流工作流搭建 Skill

> **Skill 版本**：`qingflow-skills-2026.07.01.04`（入口文档版本；如需确认 CLI 包版本，使用 `qingflow --version` 或 `qingflow --json version`）。

Use [$qingflow-common](../qingflow-common/SKILL.md) to select CLI or unified Qingflow MCP before executing. Keep one WorkflowSpec contract; only the public command or tool name changes with the selected surface.

| Operation | Qingflow CLI | Qingflow MCP |
| --- | --- | --- |
| Schema | `qingflow --json builder flow schema` | `app_flow_get_schema` |
| Read | `qingflow --json builder flow get --app-key APP_KEY` | `app_flow_get` |
| Apply | `qingflow --json builder flow apply --app-key APP_KEY --spec-file SPEC.json` | `app_flow_apply(spec=SPEC)` |
| Resolve assignees | `qingflow --json builder role search` / `member search` | `role_search` / `member_search` |

## 快速索引

| 主题 | 文件 |
|------|------|
| 依赖命令、能力边界 | [references/01-overview.md](references/01-overview.md) |
| 更新模式与最小修改原则 | [references/02-update-mode.md](references/02-update-mode.md) |
| 流程模式速查（线性/分支/回退） | [references/03-flow-patterns.md](references/03-flow-patterns.md) |
| 阶段 1：业务建模与自检 | [references/04-stage1-business-modeling.md](references/04-stage1-business-modeling.md) |
| 阶段 2：成员/角色搜索 | [references/05-stage2-members-roles.md](references/05-stage2-members-roles.md) |
| 阶段 3：Schema + 构建流程输入 | [references/06-stage3-build-spec.md](references/06-stage3-build-spec.md) |
| 阶段 4：验证流程输入 | [references/07-stage4-validate-spec.md](references/07-stage4-validate-spec.md) |
| 阶段 5：Apply + 验证循环 | [references/08-stage5-apply-verify.md](references/08-stage5-apply-verify.md) |
| 阶段 6：总结报告与回退 | [references/09-stage6-summary.md](references/09-stage6-summary.md) |
| 节点配置参考 | [references/10-node-config-reference.md](references/10-node-config-reference.md) |
| 常见问题与排障 | [references/11-troubleshooting.md](references/11-troubleshooting.md) |

---

## 一、思考（Thought）：何时启用与前置条件

### 触发条件

当用户要求**在轻流应用中搭建工作流**时启用本 Skill，典型触发语：

- "帮我搭建审批流程"
- "在这个应用里创建工作流"
- "按照这张流程图实现工作流"
- "配置流程分支条件"
- "给这个应用加一个审批节点"

### 前提检查（进入行动前必须完成）

在开始任何搭建操作前，按顺序确认以下条件：

1. **应用存在性**：`qingflow --json app get --app-key <APP_KEY>` 成功返回
2. **字段就绪**：`qingflow --json builder app get --app-key <APP_KEY> fields` 返回字段列表，确认业务建模所需字段（如单选框、成员、部门字段）均已存在
3. **未启用已有流程**（新建场景）：`qingflow --json builder app get --app-key <APP_KEY> flow` 查看 `enabled` 状态，若已有流程则为**更新模式**

**不满足时的处理**：
- 应用不存在 → 先完成应用搭建和字段配置，再继续工作流搭建
- 字段缺失 → 先补充缺失的字段定义，再继续工作流搭建
- 应用已启用流程 → 进入更新模式（读取现有 spec 再修改）

### 能力边界

| 在范围内 | 超出范围 |
|----------|----------|
| 基于已有应用搭建工作流 | 从零创建应用 |
| WorkflowSpec 生成与 apply；`patch_nodes` 局部修改 | 操作复杂命令拼接 |
| 审批/填写/抄送/自动化/分支条件等 WorkflowSpec 支持的流程 | 不读 schema/spec 就猜 raw 后端字段 |
| 审批/填写/抄送/自动化节点配置 | 修改字段定义 |
| 成员/角色搜索用于节点负责人 | 组织架构管理 |
| 验证 → apply → 校验循环 | 前端 UI 拖拽操作 |

完整命令与依赖说明见 [references/01-overview.md](references/01-overview.md)。
本 Skill 中的 `scripts/...` 路径均以 `qingflow-workflow-builder/` 技能根目录为基准；执行脚本时先解析为该技能目录下的实际文件。

---

## 二、行动（Action）：核心 SOP

按顺序执行以下阶段，每个阶段详见对应 reference 文件：

| 阶段 | 任务 | 参考文件 |
|------|------|----------|
| 阶段 0 | 判断是否为更新模式，确认最小修改原则 | [references/02-update-mode.md](references/02-update-mode.md) |
| 阶段 1 | 提取业务建模，完成七维度业务自检 | [references/04-stage1-business-modeling.md](references/04-stage1-business-modeling.md) |
| 阶段 2 | 搜索成员/角色，用于节点负责人配置 | [references/05-stage2-members-roles.md](references/05-stage2-members-roles.md) |
| 阶段 3 | 获取 Schema、读取现有流程、构建 WorkflowSpec 或 patch_nodes | [references/06-stage3-build-spec.md](references/06-stage3-build-spec.md) |
| 阶段 4 | 验证 WorkflowSpec / patch_nodes | [references/07-stage4-validate-spec.md](references/07-stage4-validate-spec.md) |
| 阶段 5 | Apply 工作流并验证部署结果 | [references/08-stage5-apply-verify.md](references/08-stage5-apply-verify.md) |

构建流程输入前，若对流程模式有疑问，先查阅 [references/03-flow-patterns.md](references/03-flow-patterns.md)。

---

## 三、反思（Reflection）：验证与总结

| 阶段 | 任务 | 参考文件 |
|------|------|----------|
| 阶段 6 | 输出结构化搭建报告，回顾业务完整性 | [references/09-stage6-summary.md](references/09-stage6-summary.md) |

搭建失败时的回退策略、节点配置细节、常见问题排障分别见：
- [references/09-stage6-summary.md](references/09-stage6-summary.md)
- [references/10-node-config-reference.md](references/10-node-config-reference.md)
- [references/11-troubleshooting.md](references/11-troubleshooting.md)
