#!/usr/bin/env python3
"""Decide whether a lychee JSON report should fail CI.

Broken files, missing fragments, and HTTP 404/410 fail the job.
Timeouts, connection errors, and status codes that flaky hosts often
return (403, 405, 408, 429, 500, 502, 503, 504) are reported and do not
fail the job. Loopback URLs are excluded by the workflow, not here.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Hosts and codes that are noisy for unattended checkers.
SOFT_CODES = {401, 403, 405, 408, 418, 421, 425, 429, 500, 502, 503, 504}
HARD_CODES = {404, 410}


def status_of(item: dict) -> tuple[str, int | None]:
    status = item.get("status", {})
    if isinstance(status, str):
        return status, None
    if not isinstance(status, dict):
        return str(status), None
    text = str(status.get("text") or "")
    code = status.get("code")
    if isinstance(code, str) and code.isdigit():
        code = int(code)
    if not isinstance(code, int):
        code = None
    return text, code


def is_hard(text: str, code: int | None) -> bool:
    lowered = text.lower()
    if "cannot find file" in lowered or "cannot find fragment" in lowered:
        return True
    if code in HARD_CODES:
        return True
    if "not found" in lowered and (code is None or code in HARD_CODES):
        return True
    return False


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: link-check-gate.py lychee.json", file=sys.stderr)
        return 1
    path = Path(sys.argv[1])
    if not path.is_file():
        print(f"FAIL: lychee report missing: {path}")
        return 1
    report = json.loads(path.read_text(encoding="utf-8"))
    hard: list[str] = []
    soft: list[str] = []
    for source, items in (report.get("error_map") or {}).items():
        for item in items:
            url = item.get("url") or item.get("uri") or "?"
            text, code = status_of(item)
            line = f"{source}: {url} ({code if code is not None else 'no-code'}: {text})"
            if is_hard(text, code):
                hard.append(line)
            else:
                soft.append(line)
    print(
        "lychee total={total} ok={successful} errors={errors} timeouts={timeouts}".format(
            **{k: report.get(k, 0) for k in ("total", "successful", "errors", "timeouts")}
        )
    )
    if soft:
        print(f"SOFT ({len(soft)}) — reported, not failing:")
        for line in soft:
            print("  " + line)
    if hard:
        print(f"HARD ({len(hard)}):")
        for line in hard:
            print("  FAIL: " + line)
        return 1
    print("No hard link failures")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
