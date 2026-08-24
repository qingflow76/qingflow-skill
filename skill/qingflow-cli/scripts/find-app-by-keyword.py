#!/usr/bin/env python3
"""旧版 CLI 兼容：在本地对已登录会话的「应用列表」做关键字过滤。
新版 CLI 默认使用 `qingflow --json app list --query <keyword>`；本脚本仅调用
`qingflow --json app list`。仅用标准库 json/subprocess/os/shutil。

qingflow stderr 不重定向，与直接执行 CLI 时一致。
qingflow 非零退出码时：本脚本将 **stdout 原文**写入当前进程 stdout；退出码与该进程相同。

用法:
  python3 scripts/find-app-by-keyword.py '<keyword>'
  ./scripts/find-app-by-keyword.py '<keyword>'

环境（可选）: QINGFLOW_PROFILE → 等价于 qingflow --profile <名称>
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from typing import Any


def _usage() -> None:
    bn = os.path.basename(sys.argv[0]) if sys.argv else "find-app-by-keyword.py"
    print(f"用法: {bn} <keyword>", file=sys.stderr)
    print(
        "  匹配 app_name、package_name、app_key 子串（不区分大小写）。"
        " 仅 subprocess: qingflow [--profile …] --json app list",
        file=sys.stderr,
    )


def _merge_and_dedupe(data: dict[str, Any]) -> list[dict[str, Any]]:
    parts: list[dict[str, Any]] = []
    it = data.get("items")
    if isinstance(it, list):
        for x in it:
            if isinstance(x, dict):
                parts.append(x)
    nested = data.get("data")
    if isinstance(nested, dict):
        it2 = nested.get("items")
        if isinstance(it2, list):
            for x in it2:
                if isinstance(x, dict):
                    parts.append(x)
    # 与 jq unique_by(.app_key) / 首次出现获胜 对齐
    seen: set[Any] = set()
    out: list[dict[str, Any]] = []
    for obj in parts:
        k = obj.get("app_key")
        if k in seen:
            continue
        seen.add(k)
        out.append(obj)
    return out


def _filtered(keyword_lc: str, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    hits: list[dict[str, Any]] = []
    for o in rows:
        for field in ("app_name", "package_name", "app_key"):
            v = o.get(field)
            if isinstance(v, str) and keyword_lc in v.lower():
                hits.append(o)
                break
    return hits


def main() -> None:
    if len(sys.argv) != 2:
        _usage()
        sys.exit(2)
    kw = sys.argv[1].strip()
    if not kw:
        bn = os.path.basename(sys.argv[0]) if sys.argv else "find-app-by-keyword.py"
        print(f"{bn}: keyword 不能为空", file=sys.stderr)
        _usage()
        sys.exit(2)

    if not shutil.which("qingflow"):
        print("qingflow: command not found", file=sys.stderr)
        sys.exit(127)

    cmd = ["qingflow"]
    pf = os.environ.get("QINGFLOW_PROFILE") or os.environ.get("QING_FLOW_PROFILE")
    if pf:
        cmd.extend(["--profile", pf])
    cmd.extend(["--json", "app", "list"])

    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=None)
    buf = proc.stdout

    if proc.returncode != 0:
        sys.stdout.buffer.write(buf)
        sys.stdout.flush()
        raise SystemExit(proc.returncode)

    try:
        text = buf.decode("utf-8")
    except UnicodeDecodeError as e:
        print(f"qingflow stdout UTF-8 解码失败: {e}", file=sys.stderr)
        sys.stdout.buffer.write(buf)
        sys.stdout.flush()
        raise SystemExit(1)

    try:
        payload = json.loads(text)
    except json.JSONDecodeError as e:
        print(f"qingflow stdout 不是合法 JSON: {e}", file=sys.stderr)
        sys.stdout.buffer.write(buf)
        sys.stdout.flush()
        raise SystemExit(1)

    if not isinstance(payload, dict):
        print("qingflow JSON 根不是 object", file=sys.stderr)
        sys.stdout.buffer.write(buf)
        sys.stdout.flush()
        raise SystemExit(1)

    merged = _merge_and_dedupe(payload)
    hits = _filtered(kw.lower(), merged)
    out = {"keyword": kw, "match_count": len(hits), "items": hits}
    json.dump(out, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
