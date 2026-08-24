#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


VALID_PORTAL_STATUSES = {"verified", "unverified", "not_created"}
VALID_APP_VERIFY_STATUSES = {"verified", "unverified", "failed"}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate a Qingflow complete-system delivery summary JSON file.")
    parser.add_argument("summary_file", nargs="?", default="tmp/qingflow_system_build_summary.json")
    args = parser.parse_args(argv)
    path = Path(args.summary_file)
    issues = validate_summary_file(path)
    if issues:
        _emit({"status": "failed", "error_code": "SYSTEM_BUILD_SUMMARY_INVALID", "path": str(path), "issues": issues})
        return 1
    payload = json.loads(path.read_text(encoding="utf-8"))
    _emit(
        {
            "status": "success",
            "path": str(path),
            "summary": {
                "package_id": payload.get("package_id"),
                "package_name": payload.get("package_name"),
                "portal_dash_key": payload.get("portal_dash_key"),
                "portal_live_status": payload.get("portal_live_status"),
                "app_count": len(payload.get("apps") or []),
                "partial_count": len(payload.get("partial_items") or []),
                "needs_followup_count": len(payload.get("needs_followup") or []),
            },
        }
    )
    return 0


def validate_summary_file(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return [_issue("MISSING_FILE", "$", f"summary file does not exist: {path}")]
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        return [_issue("READ_FAILED", "$", str(exc))]
    except json.JSONDecodeError as exc:
        return [_issue("INVALID_JSON", "$", exc.msg)]
    if not isinstance(payload, dict):
        return [_issue("INVALID_ROOT", "$", "summary root must be a JSON object")]

    issues: list[dict[str, Any]] = []
    _require_positive_int(payload, "package_id", issues)
    _require_nonempty_string(payload, "package_name", issues)
    _require_bool(payload, "front_end_visible", issues)
    _require_string_enum(payload, "portal_live_status", VALID_PORTAL_STATUSES, issues)
    if payload.get("portal_live_status") == "verified":
        _require_nonempty_string(payload, "portal_dash_key", issues)
    elif "portal_dash_key" in payload and payload.get("portal_dash_key") is not None and not isinstance(payload.get("portal_dash_key"), str):
        issues.append(_issue("INVALID_TYPE", "$.portal_dash_key", "portal_dash_key must be a string when present"))

    apps = payload.get("apps")
    if not isinstance(apps, list) or not apps:
        issues.append(_issue("INVALID_APPS", "$.apps", "apps must be a non-empty array"))
    else:
        for index, app in enumerate(apps):
            prefix = f"$.apps[{index}]"
            if not isinstance(app, dict):
                issues.append(_issue("INVALID_APP_ITEM", prefix, "app item must be an object"))
                continue
            _require_nonempty_string(app, "app_key", issues, prefix)
            _require_nonempty_string(app, "app_name", issues, prefix)
            for key in ("fields_count", "views_count", "flows_count", "charts_count"):
                _require_nonnegative_int(app, key, issues, prefix)
            _require_string_enum(app, "publish_verify_status", VALID_APP_VERIFY_STATUSES, issues, prefix)

    for key in ("warnings", "partial_items", "needs_followup"):
        if not isinstance(payload.get(key), list):
            issues.append(_issue("INVALID_TYPE", f"$.{key}", f"{key} must be an array"))
    return issues


def _require_positive_int(payload: dict[str, Any], key: str, issues: list[dict[str, Any]], prefix: str = "$") -> None:
    value = payload.get(key)
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        issues.append(_issue("INVALID_TYPE", f"{prefix}.{key}", f"{key} must be a positive integer"))


def _require_nonnegative_int(payload: dict[str, Any], key: str, issues: list[dict[str, Any]], prefix: str = "$") -> None:
    value = payload.get(key)
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        issues.append(_issue("INVALID_TYPE", f"{prefix}.{key}", f"{key} must be a non-negative integer"))


def _require_nonempty_string(payload: dict[str, Any], key: str, issues: list[dict[str, Any]], prefix: str = "$") -> None:
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        issues.append(_issue("INVALID_TYPE", f"{prefix}.{key}", f"{key} must be a non-empty string"))


def _require_bool(payload: dict[str, Any], key: str, issues: list[dict[str, Any]], prefix: str = "$") -> None:
    if not isinstance(payload.get(key), bool):
        issues.append(_issue("INVALID_TYPE", f"{prefix}.{key}", f"{key} must be a boolean"))


def _require_string_enum(payload: dict[str, Any], key: str, allowed: set[str], issues: list[dict[str, Any]], prefix: str = "$") -> None:
    value = payload.get(key)
    if value not in allowed:
        issues.append(_issue("INVALID_VALUE", f"{prefix}.{key}", f"{key} must be one of {sorted(allowed)}"))


def _issue(code: str, path: str, message: str) -> dict[str, Any]:
    return {"code": code, "path": path, "message": message}


def _emit(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    sys.exit(main())
