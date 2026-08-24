#!/usr/bin/env python3
"""
验证工作流 spec JSON 是否符合 WorkflowSpecDTO JSON Schema，
并执行自定义约束检查（DAG、单 applicant、gateway 条件等）。

用法:
  python3 validate_flow_spec.py <spec_file.json> --schema <schema_file.json>

schema 文件应在运行时通过 qingflow builder flow schema --json 动态获取。
"""

import json
import sys
import os
from collections import deque

try:
    import jsonschema
except ImportError:
    print("ERROR: jsonschema 未安装，请执行: pip install jsonschema")
    sys.exit(1)


def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def validate_schema(spec, schema):
    """使用 jsonschema 进行基础结构校验。
    注意：官方 schema 中 NodeAttrsDTO 的 oneOf 多态判别过于严格
    （GatewayAttrsDTO 和 ApplicantAttrsDTO 缺少 required 导致误匹配），
    因此这里将 attrs 的 oneOf 替换为宽松的 anyOf，类型专属校验由自定义 check 函数完成。"""
    import copy
    relaxed = copy.deepcopy(schema)
    # 修复 NodeAttrsDTO 的 oneOf → anyOf
    if '$defs' in relaxed and 'NodeAttrsDTO' in relaxed['$defs']:
        if 'oneOf' in relaxed['$defs']['NodeAttrsDTO']:
            relaxed['$defs']['NodeAttrsDTO']['anyOf'] = relaxed['$defs']['NodeAttrsDTO'].pop('oneOf')
    # 修复 WorkflowNodeDTO.attrs 的 oneOf → anyOf
    if '$defs' in relaxed and 'WorkflowNodeDTO' in relaxed['$defs']:
        attrs = relaxed['$defs']['WorkflowNodeDTO']['properties'].get('attrs', {})
        if 'oneOf' in attrs:
            attrs['anyOf'] = attrs.pop('oneOf')
    validator = jsonschema.Draft202012Validator(relaxed)
    errors = sorted(validator.iter_errors(spec), key=lambda e: e.path)
    return errors


def check_dag(nodes, edges):
    """检查边是否构成 DAG（无环）"""
    node_ids = {n['id'] for n in nodes}
    adj = {nid: [] for nid in node_ids}
    for e in edges:
        f, t = e['from'], e['to']
        if f not in node_ids:
            return [f"edge from={f} to={t}: from 节点不存在于 nodes 中"]
        if t not in node_ids:
            return [f"edge from={f} to={t}: to 节点不存在于 nodes 中"]
        adj[f].append(t)

    # Kahn's algorithm for topological sort
    indeg = {nid: 0 for nid in node_ids}
    for e in edges:
        indeg[e['to']] += 1

    q = deque([nid for nid, d in indeg.items() if d == 0])
    visited = 0
    while q:
        u = q.popleft()
        visited += 1
        for v in adj[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                q.append(v)

    if visited != len(node_ids):
        return ["检测到环路：工作流边中存在环，不符合 DAG 要求"]
    return []


def check_applicant(nodes):
    """检查有且仅有一个 applicant 节点"""
    applicants = [n for n in nodes if n.get('type') == 'applicant']
    if len(applicants) == 0:
        return ["缺少 applicant 节点：工作流必须包含一个申请人节点作为入口"]
    if len(applicants) > 1:
        ids = [a['id'] for a in applicants]
        return [f"存在多个 applicant 节点: {ids}，只允许一个"]
    return []


def check_gateway_conditions(nodes, edges):
    """检查 gateway 出边条件"""
    errors = []
    gateway_ids = {n['id'] for n in nodes if n.get('type') == 'gateway'}
    node_ids = {n['id'] for n in nodes}

    for gw_id in gateway_ids:
        out_edges = [e for e in edges if e.get('from') == gw_id]
        gw_node = next((n for n in nodes if n['id'] == gw_id), None)
        gw_mode = (gw_node or {}).get('attrs', {}).get('mode', '')
        if gw_mode == 'join':
            # join gateway 允许 0 或 1 条出边（流程终点或汇合后继续）
            pass
        elif len(out_edges) < 2:
            errors.append(f"Gateway {gw_id} 出边数={len(out_edges)}，需要至少 2 条出边")
            continue

        # 检查每条出边
        for e in out_edges:
            cond = e.get('condition')
            if not cond or not isinstance(cond, dict):
                continue
            kind = cond.get('kind', '')
            if kind != 'rules':
                continue
            auto_judges = cond.get('autoJudges', [])
            if not auto_judges or not isinstance(auto_judges, list) or len(auto_judges) == 0:
                errors.append(
                    f"Gateway {gw_id} → {e['to']} 边 kind=rules 但 autoJudges 为空"
                )
                continue
            for gi, group in enumerate(auto_judges):
                if not isinstance(group, list):
                    errors.append(
                        f"Gateway {gw_id} → {e['to']} autoJudges[{gi}] 不是数组（应为 OR 组）"
                    )
                    continue
                for ri, rule in enumerate(group):
                    if not isinstance(rule, dict):
                        errors.append(
                            f"Gateway {gw_id} → {e['to']} autoJudges[{gi}][{ri}] 不是对象"
                        )
                        continue
                    if 'fieldId' not in rule or 'judgeType' not in rule:
                        errors.append(
                            f"Gateway {gw_id} → {e['to']} autoJudges[{gi}][{ri}] 缺少 fieldId 或 judgeType"
                        )

    return errors


VALID_RESPONSIBLE_TYPES = {
    'user', 'dept', 'role', 'applicant', 'leader',
    'formEmail', 'formMember', 'formDept', 'nodeLeader'
}


def check_responsible_item(item, node_label):
    """检查单个 MemberRefDTO 项"""
    errors = []
    if not isinstance(item, dict):
        errors.append(f"{node_label} responsible 中包含非对象项")
        return errors
    if 'type' not in item:
        errors.append(f"{node_label} responsible 项缺少 type")
        return errors
    rtype = item.get('type')
    if rtype not in VALID_RESPONSIBLE_TYPES:
        errors.append(
            f"{node_label} responsible type='{rtype}' 不合法，可选: {sorted(VALID_RESPONSIBLE_TYPES)}"
        )
        return errors
    # 检查各类型的必填 ID 字段
    if rtype == 'user' and 'uid' not in item:
        errors.append(f"{node_label} responsible type='user' 缺少 uid（整数）")
    if rtype == 'dept' and 'deptId' not in item:
        errors.append(f"{node_label} responsible type='dept' 缺少 deptId（整数）")
    if rtype == 'role' and 'roleId' not in item:
        errors.append(f"{node_label} responsible type='role' 缺少 roleId（整数）")
    if rtype in ('leader', 'formEmail', 'formMember', 'formDept') and 'queId' not in item:
        errors.append(f"{node_label} responsible type='{rtype}' 缺少 queId（整数）")
    return errors


def check_responsible_array(attrs, node_label):
    """检查 responsible 是否为非空 MemberRefDTO 数组"""
    errors = []
    responsible = attrs.get('responsible')
    if responsible is None:
        return errors  # 外层已报缺字段
    if not isinstance(responsible, list):
        errors.append(
            f"{node_label} responsible 必须是数组，当前为 {type(responsible).__name__}"
        )
        return errors
    if len(responsible) == 0:
        errors.append(f"{node_label} responsible 数组至少包含 1 个元素")
        return errors
    for item in responsible:
        errors.extend(check_responsible_item(item, node_label))
    return errors


def check_approval_nodes(nodes):
    """检查审批节点必要字段"""
    errors = []
    for n in nodes:
        if n.get('type') != 'approval':
            continue
        attrs = n.get('attrs', {})
        node_label = f"审批节点 {n['id']} ({n.get('name','')})"
        if 'responsible' not in attrs:
            errors.append(f"{node_label} 缺少 responsible（审批人）")
        else:
            errors.extend(check_responsible_array(attrs, node_label))
        if 'approveType' not in attrs:
            errors.append(f"{node_label} 缺少 approveType")
        if 'auditUserType' not in attrs:
            errors.append(f"{node_label} 缺少 auditUserType")
    return errors


def check_filling_nodes(nodes):
    """检查填写节点必要字段"""
    errors = []
    for n in nodes:
        if n.get('type') != 'filling':
            continue
        attrs = n.get('attrs', {})
        node_label = f"填写节点 {n['id']} ({n.get('name','')})"
        if 'responsible' not in attrs:
            errors.append(f"{node_label} 缺少 responsible（处理人）")
        else:
            errors.extend(check_responsible_array(attrs, node_label))
    return errors


def check_automation_nodes(nodes, edges):
    """检查自动化节点配置"""
    errors = []
    node_ids = {n['id'] for n in nodes}
    for n in nodes:
        if n.get('type') != 'automation':
            continue
        attrs = n.get('attrs', {})
        sub_type = attrs.get('subType', '')
        if not sub_type:
            errors.append(f"自动化节点 {n['id']} ({n.get('name','')}) 缺少 subType")
            continue

        if sub_type == 'update':
            if 'appKey' not in attrs:
                errors.append(f"自动化节点 {n['id']} update 缺少 appKey")
            if 'targetFilterRules' not in attrs:
                errors.append(f"自动化节点 {n['id']} update 缺少 targetFilterRules")
            if 'fieldMappings' not in attrs:
                errors.append(f"自动化节点 {n['id']} update 缺少 fieldMappings")
        elif sub_type == 'add':
            if 'appKey' not in attrs:
                errors.append(f"自动化节点 {n['id']} add 缺少 appKey")
            if 'fieldMappings' not in attrs:
                errors.append(f"自动化节点 {n['id']} add 缺少 fieldMappings")
        elif sub_type == 'send_email':
            if 'mailConfig' not in attrs:
                errors.append(f"自动化节点 {n['id']} send_email 缺少 mailConfig")
            if 'mailReceivers' not in attrs:
                errors.append(f"自动化节点 {n['id']} send_email 缺少 mailReceivers")
        elif sub_type == 'http_request':
            if 'remoteRequestConfig' not in attrs:
                errors.append(f"自动化节点 {n['id']} http_request 缺少 remoteRequestConfig")
        elif sub_type == 'ai_':
            if 'aiConfig' not in attrs:
                errors.append(f"自动化节点 {n['id']} AI 节点缺少 aiConfig")
    return errors


def check_cc_nodes(nodes):
    """检查抄送节点必要字段"""
    errors = []
    for n in nodes:
        if n.get('type') != 'cc':
            continue
        attrs = n.get('attrs', {})
        if 'receivers' not in attrs:
            errors.append(f"抄送节点 {n['id']} ({n.get('name','')}) 缺少 receivers")
    return errors


def check_orphan_nodes(nodes, edges):
    """检查是否有孤立节点（无入边也无出边，且非 applicant）"""
    node_ids = {n['id'] for n in nodes}
    has_in = set()
    has_out = set()
    for e in edges:
        has_in.add(e['to'])
        has_out.add(e['from'])

    errors = []
    applicants = {n['id'] for n in nodes if n.get('type') == 'applicant'}
    for n in nodes:
        nid = n['id']
        if nid in applicants:
            if nid in has_in:
                errors.append(f"申请人节点 {nid} 不应有入边")
            continue
        if nid not in has_in:
            errors.append(f"节点 {nid} ({n.get('name','')}) 缺少入边（孤立节点）")
    return errors


def check_routing_entry_and_sync(nodes, edges):
    """检查入口出边和需要继续流转节点的 sync 标记。"""
    errors = []
    outgoing = {}
    for edge in edges:
        outgoing.setdefault(edge.get('from'), []).append(edge.get('to'))

    for node in nodes:
        node_id = node.get('id')
        node_type = node.get('type')
        node_label = f"节点 {node_id} ({node.get('name','')})"
        has_outgoing = bool(outgoing.get(node_id))
        if node_type == 'applicant' and not has_outgoing:
            errors.append(f"申请人入口节点 {node_id} 没有出边，提交后流程不会进入下一节点")
        if has_outgoing and node.get('sync') is not True:
            errors.append(f"{node_label} 存在出边但未显式 sync=true，后端可能停止继续路由")
    return errors


def check_minimal_modification(old_spec, new_spec):
    """更新模式下检查最小修改原则：ID 稳定性、无冗余删建、修改范围合理"""
    warnings = []
    errors = []

    old_nodes = old_spec.get('nodes', [])
    new_nodes = new_spec.get('nodes', [])

    old_by_id = {n['id']: n for n in old_nodes}
    new_by_id = {n['id']: n for n in new_nodes}

    old_ids = set(old_by_id.keys())
    new_ids = set(new_by_id.keys())

    deleted_ids = old_ids - new_ids
    added_ids = new_ids - old_ids
    common_ids = old_ids & new_ids

    # 1. 检测节点 ID 变更（内容相同但 ID 不同 —— 可能是不必要的重建）
    def node_identity(n):
        return json.dumps({
            'type': n.get('type', ''),
            'name': n.get('name', ''),
            'attrs': n.get('attrs', {}),
        }, sort_keys=True, ensure_ascii=False)

    old_identities = {}
    for n in old_nodes:
        ident = node_identity(n)
        old_identities.setdefault(ident, []).append(n['id'])

    for n in new_nodes:
        if n['id'] in added_ids:
            ident = node_identity(n)
            if ident in old_identities and old_identities[ident]:
                old_id = old_identities[ident][0]
                if old_id in deleted_ids:
                    errors.append(
                        f"[最小修改] 节点 {old_id} → {n['id']} ({n.get('name','')})："
                        f"内容未变但 ID 已变更，可能导致后端不支持配置丢失"
                    )

    # 2. 检测类型变更（type 不同视为破坏性修改）
    for nid in common_ids:
        old_type = old_by_id[nid].get('type')
        new_type = new_by_id[nid].get('type')
        if old_type != new_type:
            warnings.append(
                f"[最小修改] 节点 {nid} type 从 {old_type} 变为 {new_type}，"
                f"可能丢失原类型专属配置"
            )

    # 3. 检测旧边删除 + 新边添加（from/to 相同但 condition 不同 → 应该是修改而非删建）
    def extract_edges(spec):
        e = spec.get('edges', [])
        if isinstance(e, dict) and 'edges' in e:
            return e['edges']
        if isinstance(e, list):
            return e
        return []

    old_edges = extract_edges(old_spec)
    new_edges = extract_edges(new_spec)

    old_edge_keys = {(e['from'], e['to']) for e in old_edges}
    new_edge_keys = {(e['from'], e['to']) for e in new_edges}

    deleted_edges = old_edge_keys - new_edge_keys
    added_edges = new_edge_keys - old_edge_keys

    if deleted_edges:
        warnings.append(
            f"[最小修改] 删除了 {len(deleted_edges)} 条边，请确认是否为业务需要"
        )
    if added_edges:
        warnings.append(
            f"[最小修改] 新增了 {len(added_edges)} 条边，请确认是否按预期新增"
        )

    # 4. 汇总
    if deleted_ids:
        warnings.append(
            f"[最小修改] 删除了 {len(deleted_ids)} 个节点: {sorted(deleted_ids)}，请确认是否为业务需要"
        )

    return errors, warnings


def check_required_fields(nodes, edges):
    """检查所有节点必要字段"""
    errors = []
    for n in nodes:
        for field in ['id', 'type', 'name', 'attrs']:
            if field not in n:
                errors.append(f"节点缺少必要字段 {field}: {n.get('id','?')}")
    for e in edges:
        for field in ['from', 'to']:
            if field not in e:
                errors.append(f"边缺少必要字段 {field}: {e}")
    return errors


def normalize_spec(spec):
    """将 spec 标准化：处理 edges 可能在 edges 或直接在顶层的情况"""
    if 'edges' in spec:
        e = spec['edges']
        if isinstance(e, dict) and 'edges' in e:
            return spec['nodes'], e['edges']
        elif isinstance(e, list):
            return spec['nodes'], e
    # edges 可能直接是数组
    if isinstance(spec.get('edges'), list):
        return spec['nodes'], spec['edges']
    return spec.get('nodes', []), []


def inject_attrs_type(spec):
    """Schema 中 attrs 的多态判别依赖 type 字段，但实际数据中 type 在父节点。
    为满足 schema 校验，将 node.type 注入到 node.attrs.type 中（仅校验用，不修改原数据）。"""
    import copy
    spec = copy.deepcopy(spec)
    for n in spec.get('nodes', []):
        if 'attrs' in n and isinstance(n['attrs'], dict) and 'type' not in n['attrs']:
            n['attrs']['type'] = n.get('type', '')
    return spec


def strip_nulls(obj, parent_key=None):
    """递归删除对象中的 null 值字段，但保留必要字段（如 name）并给默认值。"""
    if isinstance(obj, dict):
        result = {}
        for k, v in obj.items():
            if v is None:
                if k == 'name':
                    # name 是必要字段，使用 id 作为默认名称
                    result[k] = obj.get('id', 'unnamed')
                elif k == 'role':
                    # role 是可选字符串，null 时跳过
                    continue
                else:
                    continue
            else:
                result[k] = strip_nulls(v, k)
        return result
    elif isinstance(obj, list):
        return [strip_nulls(v) for v in obj]
    return obj


def normalize_auto_judges(spec):
    """后端 get 返回的 autoJudges 可能是 [{"rules": [...]}] 格式，
    将其规范化为 OR-of-AND 二维数组 [[{...}]] 格式。"""
    import copy
    spec = copy.deepcopy(spec)
    edges = spec.get('edges', {})
    edge_list = edges.get('edges', []) if isinstance(edges, dict) else edges
    if isinstance(edge_list, list):
        for e in edge_list:
            cond = e.get('condition')
            if not cond or not isinstance(cond, dict):
                continue
            judges = cond.get('autoJudges')
            if not judges or not isinstance(judges, list):
                continue
            normalized = []
            for item in judges:
                if isinstance(item, dict) and 'rules' in item:
                    # 格式: {"rules": [...]} → 展开为 [...]
                    normalized.append(item['rules'])
                elif isinstance(item, list):
                    normalized.append(item)
            if normalized:
                cond['autoJudges'] = normalized
    return spec


def main():
    if len(sys.argv) < 2:
        print("用法: python3 validate_flow_spec.py <spec_file.json> [--schema <schema_file.json>]")
        sys.exit(1)

    spec_file = sys.argv[1]
    schema_file = None
    previous_file = None
    for i, arg in enumerate(sys.argv):
        if arg == '--schema' and i + 1 < len(sys.argv):
            schema_file = sys.argv[i + 1]
        if arg == '--previous' and i + 1 < len(sys.argv):
            previous_file = sys.argv[i + 1]

    if schema_file is None:
        print("用法: python3 validate_flow_spec.py <spec_file.json> --schema <schema_file.json> [--previous <old_spec.json>]")
        print("提示: schema 文件通过 'qingflow builder flow schema --json > tmp/flow_schema.json' 动态获取")
        sys.exit(1)

    try:
        spec = load_json(spec_file)
    except Exception as e:
        print(f"FATAL: 无法读取 spec 文件 {spec_file}: {e}")
        sys.exit(1)

    try:
        schema = load_json(schema_file)
    except Exception as e:
        print(f"FATAL: 无法读取 schema 文件 {schema_file}: {e}")
        sys.exit(1)

    all_errors = []
    warnings = []

    # 1. 预处理：null 值清理 + autoJudges 格式规范化
    spec = strip_nulls(spec)
    spec = normalize_auto_judges(spec)

    # 2. JSON Schema 校验（先注入 attrs.type 以匹配多态判别）
    spec_for_validation = inject_attrs_type(spec)
    schema_errors = validate_schema(spec_for_validation, schema)
    if schema_errors:
        for err in schema_errors:
            path = '.'.join(str(p) for p in err.path) if err.path else '(root)'
            all_errors.append(f"[Schema] {path}: {err.message}")

    # 2. 提取 nodes 和 edges
    nodes, edges = normalize_spec(spec)
    if not nodes:
        all_errors.append("[结构] spec 中未找到 nodes 数组")
    if not edges:
        all_errors.append("[结构] spec 中未找到 edges 数组")

    if nodes and edges:
        # 3. 必要字段检查
        all_errors.extend(check_required_fields(nodes, edges))

        # 4. DAG 检查（回退边/驳回边可能导致环，降级为警告）
        dag_errors = check_dag(nodes, edges)
        if dag_errors:
            warnings.extend(dag_errors)
            warnings.append("DAG 环通常由回退边（如审批驳回、gateway 回退）引起，可能是合法的业务需求")

        # 5. 单 applicant 检查
        all_errors.extend(check_applicant(nodes))

        # 6. Gateway 条件检查
        all_errors.extend(check_gateway_conditions(nodes, edges))

        # 7. 审批节点检查
        all_errors.extend(check_approval_nodes(nodes))

        # 8. 填写节点检查
        all_errors.extend(check_filling_nodes(nodes))

        # 9. 自动化节点检查
        all_errors.extend(check_automation_nodes(nodes, edges))

        # 10. 抄送节点检查
        all_errors.extend(check_cc_nodes(nodes))

        # 11. 孤立节点检查
        all_errors.extend(check_orphan_nodes(nodes, edges))

        # 12. 入口出边与 sync 检查
        all_errors.extend(check_routing_entry_and_sync(nodes, edges))

    # 13. 更新模式：最小修改原则检查
    if previous_file:
        try:
            prev_spec = load_json(previous_file)
            mod_errors, mod_warnings = check_minimal_modification(prev_spec, spec)
            all_errors.extend(mod_errors)
            warnings.extend(mod_warnings)
        except Exception as e:
            warnings.append(f"无法读取 previous spec {previous_file}: {e}，跳过最小修改检查")

    # 统计
    node_types = {}
    for n in nodes:
        t = n.get('type', 'unknown')
        node_types[t] = node_types.get(t, 0) + 1

    print("=" * 60)
    print(f"工作流 Spec 验证报告: {spec_file}")
    print(f"节点总数: {len(nodes)}")
    for t, c in sorted(node_types.items()):
        print(f"  {t}: {c}")
    print(f"边总数: {len(edges)}")
    print(f"错误数: {len(all_errors)}")
    print(f"警告数: {len(warnings)}")
    print("=" * 60)

    if all_errors:
        print("\n❌ 错误:")
        for e in all_errors:
            print(f"  - {e}")
    else:
        print("\n✅ 所有检查通过")

    if warnings:
        print("\n⚠️ 警告:")
        for w in warnings:
            print(f"  - {w}")

    sys.exit(1 if all_errors else 0)


if __name__ == '__main__':
    main()
