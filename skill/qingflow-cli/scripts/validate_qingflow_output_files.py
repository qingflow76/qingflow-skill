#!/usr/bin/env python3
from __future__ import annotations

import argparse
import glob
import json
import sys
from pathlib import Path
from typing import Any


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate Qingflow CLI output artifact files.")
    parser.add_argument("paths", nargs="*", help="Output files to validate")
    parser.add_argument("--glob", action="append", default=[], dest="glob_patterns", help="Glob pattern for output files")
    parser.add_argument("--allow-invalid-json", action="store_true", help="Only check file existence and non-zero size")
    args = parser.parse_args(argv)

    paths = _expand_paths(args.paths, args.glob_patterns)
    issues: list[dict[str, Any]] = []
    if not paths:
        issues.append(_issue("NO_FILES", "$", "no output files were provided"))
    for path in paths:
        issues.extend(validate_output_file(path, require_json=not args.allow_invalid_json))

    payload: dict[str, Any] = {"status": "failed" if issues else "success", "checked_count": len(paths), "issues": issues}
    if issues:
        payload["error_code"] = "QINGFLOW_OUTPUT_ARTIFACTS_INVALID"
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 1 if issues else 0


def validate_output_file(path: Path, *, require_json: bool = True) -> list[dict[str, Any]]:
    path_text = str(path)
    if not path.exists():
        return [_issue("OUTPUT_FILE_MISSING", path_text, "output file does not exist")]
    if not path.is_file():
        return [_issue("OUTPUT_PATH_NOT_FILE", path_text, "output path is not a file")]
    try:
        size = path.stat().st_size
    except OSError as exc:
        return [_issue("OUTPUT_FILE_STAT_FAILED", path_text, str(exc))]
    if size == 0:
        return [
            _issue(
                "OUTPUT_FILE_EMPTY",
                path_text,
                "output file is 0 bytes; treat write state as unknown and run readback before retry",
                next_action="readback_before_retry",
            )
        ]
    if not require_json:
        return []
    try:
        json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        return [_issue("OUTPUT_FILE_READ_FAILED", path_text, str(exc))]
    except json.JSONDecodeError as exc:
        return [_issue("OUTPUT_FILE_INVALID_JSON", path_text, exc.msg)]
    return []


def _expand_paths(raw_paths: list[str], patterns: list[str]) -> list[Path]:
    seen: set[str] = set()
    paths: list[Path] = []
    for raw in raw_paths:
        path = Path(raw)
        key = str(path)
        if key not in seen:
            paths.append(path)
            seen.add(key)
    for pattern in patterns:
        for match in sorted(glob.glob(pattern)):
            path = Path(match)
            key = str(path)
            if key not in seen:
                paths.append(path)
                seen.add(key)
    return paths


def _issue(code: str, path: str, message: str, **extra: Any) -> dict[str, Any]:
    return {"code": code, "path": path, "message": message, **extra}


if __name__ == "__main__":
    sys.exit(main())
