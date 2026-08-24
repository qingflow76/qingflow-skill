#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="${QINGFLOW_MCP_ROOT:-}"

if [[ -z "$ROOT" ]]; then
  if git_root="$(git rev-parse --show-toplevel 2>/dev/null)" && [[ -d "$git_root/qingflow-support/mcp-server" ]]; then
    ROOT="$git_root/qingflow-support/mcp-server"
  elif [[ -d "$PWD/qingflow-support/mcp-server" ]]; then
    ROOT="$PWD/qingflow-support/mcp-server"
  else
    repo_root="$(cd "$SCRIPT_DIR/../../../.." && pwd)"
    if [[ -d "$repo_root/qingflow-support/mcp-server" ]]; then
      ROOT="$repo_root/qingflow-support/mcp-server"
    fi
  fi
fi

if [[ -z "$ROOT" ]]; then
  echo "Unable to locate qingflow-support/mcp-server. Set QINGFLOW_MCP_ROOT to the repo copy of the MCP server." >&2
  exit 1
fi

ENTRY="$ROOT/qingflow-mcp"
PY="$ROOT/.venv/bin/python"

echo "ROOT=$ROOT"
test -d "$ROOT"
echo "OK root exists"

test -x "$ENTRY"
echo "OK entrypoint exists and is executable"

test -x "$PY"
echo "OK virtualenv python exists"

PYTHONPATH="$ROOT/src" "$PY" -c "import qingflow_mcp.server; print('OK import qingflow_mcp.server')"
