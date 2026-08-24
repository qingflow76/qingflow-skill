#!/usr/bin/env python3
"""
对比两个工作流 spec 的差异，输出新增/删除/修改的节点和边。
用于更新模式下辅助 agent 判断是否遵循最小修改原则。

用法:
  python3 diff_flow_spec.py <old_spec.json> <new_spec.json>
  python3 diff_flow_spec.py <old_spec.json> <new_spec.json> --json   # JSON 输出
"""

import json
import sys


def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def extract_edges(spec):
    """从 spec 中提取边列表，兼容 edges 在不同层级的情况"""
    e = spec.get('edges', [])
    if isinstance(e, dict) and 'edges' in e:
        return e['edges']
    if isinstance(e, list):
        return e
    return []


def node_key(n):
    """节点的唯一标识"""
    return n.get('id', '')


def edge_key(e):
    """边的唯一标识：from→to"""
    return (e.get('from', ''), e.get('to', ''))


def node_identity(n):
    """节点的完整内容（不含 id，用于判断是否修改）"""
    return {
        'type': n.get('type', ''),
        'name': n.get('name', ''),
        'attrs': n.get('attrs', {}),
    }


def edge_identity(e):
    """边的完整内容（不含 from/to，用于判断是否修改）"""
    return {
        'label': e.get('label', ''),
        'condition': e.get('condition', {}),
    }


def diff_nodes(old_nodes, new_nodes):
    """对比节点差异"""
    old_by_id = {node_key(n): n for n in old_nodes}
    new_by_id = {node_key(n): n for n in new_nodes}

    old_ids = set(old_by_id.keys())
    new_ids = set(new_by_id.keys())

    deleted_ids = sorted(old_ids - new_ids)
    added_ids = sorted(new_ids - old_ids)
    common_ids = sorted(old_ids & new_ids)

    modified = []
    id_changes = []
    for nid in common_ids:
        old_ident = node_identity(old_by_id[nid])
        new_ident = node_identity(new_by_id[nid])
        if old_ident != new_ident:
            modified.append({
                'id': nid,
                'old': {'type': old_ident['type'], 'name': old_ident['name']},
                'new': {'type': new_ident['type'], 'name': new_ident['name']},
                'attrs_changed': old_ident['attrs'] != new_ident['attrs'],
                'type_changed': old_ident['type'] != new_ident['type'],
                'name_changed': old_ident['name'] != new_ident['name'],
            })

    # 检测可能的不必要 ID 变更（内容相同但 ID 不同）
    old_by_identity = {}
    for n in old_nodes:
        ident = json.dumps(node_identity(n), sort_keys=True, ensure_ascii=False)
        old_by_identity.setdefault(ident, []).append(n)

    for n in new_nodes:
        if node_key(n) in added_ids:
            ident = json.dumps(node_identity(n), sort_keys=True, ensure_ascii=False)
            if ident in old_by_identity and old_by_identity[ident]:
                old_match = old_by_identity[ident][0]
                if node_key(old_match) in deleted_ids:
                    id_changes.append({
                        'old_id': node_key(old_match),
                        'new_id': node_key(n),
                        'identity': node_identity(n),
                        'warning': '节点内容未变但 ID 已变更，可能导致后端不支持配置丢失',
                    })

    return {
        'deleted': [{'id': nid, 'name': old_by_id[nid].get('name', ''), 'type': old_by_id[nid].get('type', '')} for nid in deleted_ids],
        'added': [{'id': nid, 'name': new_by_id[nid].get('name', ''), 'type': new_by_id[nid].get('type', '')} for nid in added_ids],
        'modified': modified,
        'id_changes': id_changes,
        'unchanged': len(common_ids) - len(modified),
    }


def diff_edges(old_edges, new_edges):
    """对比边差异"""
    old_by_key = {edge_key(e): e for e in old_edges}
    new_by_key = {edge_key(e): e for e in new_edges}

    old_keys = set(old_by_key.keys())
    new_keys = set(new_by_key.keys())

    deleted_keys = sorted(old_keys - new_keys)
    added_keys = sorted(new_keys - old_keys)
    common_keys = sorted(old_keys & new_keys)

    modified = []
    for key in common_keys:
        old_ident = edge_identity(old_by_key[key])
        new_ident = edge_identity(new_by_key[key])
        if old_ident != new_ident:
            modified.append({
                'from': key[0],
                'to': key[1],
                'old_condition': old_ident['condition'],
                'new_condition': new_ident['condition'],
                'label_changed': old_ident['label'] != new_ident['label'],
                'condition_changed': old_ident['condition'] != new_ident['condition'],
            })

    return {
        'deleted': [{'from': k[0], 'to': k[1]} for k in deleted_keys],
        'added': [{'from': k[0], 'to': k[1]} for k in added_keys],
        'modified': modified,
        'unchanged': len(common_keys) - len(modified),
    }


def print_human(result):
    """人类可读输出"""
    nodes = result['nodes']
    edges = result['edges']

    print("=" * 60)
    print("工作流 Spec 差异分析")
    print("=" * 60)

    # 节点汇总
    print(f"\n📊 节点汇总:")
    print(f"  删除: {len(nodes['deleted'])} | 新增: {len(nodes['added'])} | "
          f"修改: {len(nodes['modified'])} | 未变: {nodes['unchanged']}")

    if nodes['id_changes']:
        print(f"\n⚠️  检测到 {len(nodes['id_changes'])} 个可能的 ID 变更（内容相同但 ID 不同）:")
        for ic in nodes['id_changes']:
            print(f"  {ic['old_id']} → {ic['new_id']} ({ic['identity']['name']})")
            print(f"    ⚠ {ic['warning']}")

    if nodes['deleted']:
        print(f"\n🗑  删除的节点 ({len(nodes['deleted'])}):")
        for d in nodes['deleted']:
            print(f"  - [{d['type']}] {d['id']} ({d['name']})")

    if nodes['added']:
        print(f"\n➕ 新增的节点 ({len(nodes['added'])}):")
        for a in nodes['added']:
            print(f"  - [{a['type']}] {a['id']} ({a['name']})")

    if nodes['modified']:
        print(f"\n✏️  修改的节点 ({len(nodes['modified'])}):")
        for m in nodes['modified']:
            changes = []
            if m['type_changed']:
                changes.append(f"type: {m['old']['type']} → {m['new']['type']}")
            if m['name_changed']:
                changes.append(f"name: {m['old']['name']} → {m['new']['name']}")
            if m['attrs_changed']:
                changes.append("attrs 已变更")
            print(f"  - {m['id']}: {', '.join(changes) if changes else '无实质变更'}")

    # 边汇总
    print(f"\n📊 边汇总:")
    print(f"  删除: {len(edges['deleted'])} | 新增: {len(edges['added'])} | "
          f"修改: {len(edges['modified'])} | 未变: {edges['unchanged']}")

    if edges['deleted']:
        print(f"\n🗑  删除的边 ({len(edges['deleted'])}):")
        for d in edges['deleted']:
            print(f"  - {d['from']} → {d['to']}")

    if edges['added']:
        print(f"\n➕ 新增的边 ({len(edges['added'])}):")
        for a in edges['added']:
            print(f"  - {a['from']} → {a['to']}")

    if edges['modified']:
        print(f"\n✏️  修改的边 ({len(edges['modified'])}):")
        for m in edges['modified']:
            changes = []
            if m['label_changed']:
                changes.append("label 已变更")
            if m['condition_changed']:
                changes.append("condition 已变更")
            if changes:
                print(f"  - {m['from']} → {m['to']}: {', '.join(changes)}")
            else:
                print(f"  - {m['from']} → {m['to']}: 无实质变更")

    # 最小修改原则评估
    print(f"\n📋 最小修改原则评估:")
    issues = 0
    if nodes['id_changes']:
        print(f"  ❌ 存在 ID 变更（{len(nodes['id_changes'])} 个节点），可能导致后端不支持配置丢失")
        issues += 1
    if nodes['deleted']:
        print(f"  ⚠️  删除了 {len(nodes['deleted'])} 个节点，请确认是否为业务需要")
        issues += 1
    if not nodes['deleted'] and not nodes['id_changes'] and nodes['modified']:
        print(f"  ✅ 仅修改已有节点，未删除或变更 ID，符合最小修改原则")
    if not nodes['deleted'] and not nodes['modified'] and not nodes['added'] and not nodes['id_changes']:
        print(f"  ✅ 无任何变更")

    print(f"\n总结: 错误 {issues} 项")


def main():
    if len(sys.argv) < 3:
        print("用法: python3 diff_flow_spec.py <old_spec.json> <new_spec.json> [--json]")
        sys.exit(1)

    old_file = sys.argv[1]
    new_file = sys.argv[2]
    output_json = '--json' in sys.argv

    try:
        old_spec = load_json(old_file)
    except Exception as e:
        print(f"FATAL: 无法读取旧 spec 文件 {old_file}: {e}")
        sys.exit(1)

    try:
        new_spec = load_json(new_file)
    except Exception as e:
        print(f"FATAL: 无法读取新 spec 文件 {new_file}: {e}")
        sys.exit(1)

    old_nodes = old_spec.get('nodes', [])
    new_nodes = new_spec.get('nodes', [])
    old_edges = extract_edges(old_spec)
    new_edges = extract_edges(new_spec)

    result = {
        'nodes': diff_nodes(old_nodes, new_nodes),
        'edges': diff_edges(old_edges, new_edges),
    }

    if output_json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print_human(result)

    # 如果有 ID 变更，返回非零以便脚本判断
    has_id_changes = len(result['nodes']['id_changes']) > 0
    sys.exit(1 if has_id_changes else 0)


if __name__ == '__main__':
    main()