#!/usr/bin/env python3
"""纯 CLI 曲线：在 **无** `package_list` / `package_resolve` 子命令时，用 `app list` + `builder app resolve` 解析包。

- `app list`（`GET /tag/apps` 扁平结果）常见含 **`package_name`**（分组显示名），**不一定**含数值 **`tag_id`**。
- `builder app resolve --app-key` 的 JSON 里常有 **`package_ids`**（与 MCP `package_get` 所用的 `tag_id` 同源）。

子命令:
  list-names              打印去重后的 `package_name` 列表（JSON 数组）
  resolve-id <显示名>      **精确匹配** `package_name`，取该组下第一个 `app_key`，再 `builder app resolve`，打印含 `package_ids` 的 JSON object

环境（可选）: `QINGFLOW_PROFILE` → 等价于 `qingflow --profile <名称>`

注意:
- 若工作区内存在 **同名分组**（多个 `tag_id` 共用显示名），本脚本 **无法**区分，请用管理端或 MCP `package_list`。
- 某包下 **尚未有任何可见应用** 时，无法从 `app list` 曲线解析。

用法:
  ./scripts/builder-package-from-app-list.py list-names
  ./scripts/builder-package-from-app-list.py resolve-id 'test'
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from typing import Any


def _qf_base() -> list[str]:
    cmd = ["qingflow"]
    pf = os.environ.get("QINGFLOW_PROFILE") or os.environ.get("QING_FLOW_PROFILE")
    if pf:
        cmd.extend(["--profile", pf])
    return cmd


def _run_json(cmd: list[str]) -> dict[str, Any]:
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=None)
    if proc.returncode != 0:
        sys.stdout.buffer.write(proc.stdout)
        sys.stdout.flush()
        raise SystemExit(proc.returncode)
    try:
        text = proc.stdout.decode("utf-8")
        payload = json.loads(text)
    except (UnicodeDecodeError, json.JSONDecodeError) as e:
        print(f"qingflow JSON 解析失败: {e}", file=sys.stderr)
        sys.stdout.buffer.write(proc.stdout)
        sys.stdout.flush()
        raise SystemExit(1) from e
    if not isinstance(payload, dict):
        print("qingflow JSON 根不是 object", file=sys.stderr)
        raise SystemExit(1)
    return payload


def _app_list_items(payload: dict[str, Any]) -> list[dict[str, Any]]:
    it = payload.get("items")
    if isinstance(it, list):
        return [x for x in it if isinstance(x, dict)]
    nested = payload.get("data")
    if isinstance(nested, dict):
        it2 = nested.get("items")
        if isinstance(it2, list):
            return [x for x in it2 if isinstance(x, dict)]
    return []


def cmd_list_names() -> None:
    if not shutil.which("qingflow"):
        print("qingflow: command not found", file=sys.stderr)
        sys.exit(127)
    payload = _run_json(_qf_base() + ["--json", "app", "list"])
    rows = _app_list_items(payload)
    names: set[str] = set()
    for o in rows:
        pn = o.get("package_name")
        if isinstance(pn, str) and pn.strip():
            names.add(pn.strip())
    json.dump(sorted(names), sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")


def cmd_resolve_id(display_name: str) -> None:
    if not shutil.which("qingflow"):
        print("qingflow: command not found", file=sys.stderr)
        sys.exit(127)
    want = display_name.strip()
    if not want:
        print("显示名不能为空", file=sys.stderr)
        sys.exit(2)

    payload = _run_json(_qf_base() + ["--json", "app", "list"])
    rows = _app_list_items(payload)
    app_key: str | None = None
    for o in rows:
        pn = o.get("package_name")
        if isinstance(pn, str) and pn.strip() == want:
            ak = o.get("app_key")
            if isinstance(ak, str) and ak.strip():
                app_key = ak.strip()
                break
    if not app_key:
        print(json.dumps({"error": "no_app_under_package_name", "package_name": want}, ensure_ascii=False, indent=2))
        sys.exit(3)

    resolved = _run_json(_qf_base() + ["--json", "builder", "app", "resolve", "--app-key", app_key])
    out = {
        "package_name": want,
        "sample_app_key": app_key,
        "package_ids": resolved.get("package_ids"),
        "resolve": resolved,
    }
    json.dump(out, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")


def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__.strip(), file=sys.stderr)
        sys.exit(2)
    sub = sys.argv[1].strip().lower()
    if sub in {"list-names", "list_names", "names"}:
        cmd_list_names()
        return
    if sub in {"resolve-id", "resolve_id", "resolve"}:
        if len(sys.argv) != 3:
            print("用法: … resolve-id '<package显示名>'", file=sys.stderr)
            sys.exit(2)
        cmd_resolve_id(sys.argv[2])
        return
    print(__doc__.strip(), file=sys.stderr)
    sys.exit(2)


if __name__ == "__main__":
    main()
