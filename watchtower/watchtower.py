#!/usr/bin/env python3
"""Watchtower — honest uptime monitoring for a personal AI estate.

Portable core: reads services.yaml, checks what it can (http, file),
merges externally-resolved states (e.g. cron states gathered by the estate's
sweep agent via --extra), and writes status.json + STATUS.md.

States: operational | paused | degraded | unknown.
A service the operator deliberately paused is "paused", never "down" —
pausing is a decision, not an outage. That distinction is the whole point.

Usage:
    python3 watchtower.py [--services services.yaml] [--extra extra.json]
                          [--out DIR]

extra.json format: {"services": [{"name": ..., "state": ..., "note": ...},
                                 ...]}
Entries in --extra override script-resolved states by service name.
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone

try:
    import yaml
except ImportError:
    yaml = None


def check_http(target, timeout=15):
    req = urllib.request.Request(target, headers={"User-Agent": "Watchtower/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            if 200 <= r.status < 400:
                return "operational", f"HTTP {r.status}"
            return "degraded", f"HTTP {r.status}"
    except urllib.error.HTTPError as e:
        # 403 from bot protection means "could not verify", not "down".
        if e.code == 403:
            return "unknown", "HTTP 403 (bot protection) — could not verify from here"
        return "degraded", f"HTTP {e.code}"
    except Exception as e:  # noqa: BLE001 — report, don't crash the sweep
        return "degraded", f"{type(e).__name__}: {e}"[:120]


def check_file(target):
    if os.path.exists(os.path.expanduser(target)):
        return "operational", "present on disk"
    return "degraded", "missing on disk"


CHECKERS = {"http": lambda s: check_http(s["target"]), "file": lambda s: check_file(s["target"])}


def load_services(path):
    with open(path) as f:
        text = f.read()
    if yaml:
        return yaml.safe_load(text)["services"]
    # Minimal fallback parser for the simple manifest shape.
    services, current = [], {}
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("- name:"):
            if current:
                services.append(current)
            current = {"name": s.split(":", 1)[1].strip()}
        elif s.startswith(("kind:", "cron_id:", "target:", "cadence:", "description:")) and current is not None:
            k, v = s.split(":", 1)
            current[k.strip()] = v.strip()
    if current:
        services.append(current)
    return services


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--services", default="services.yaml")
    ap.add_argument("--extra", default=None)
    ap.add_argument("--out", default=".")
    args = ap.parse_args()

    services = load_services(args.services)
    overrides = {}
    if args.extra and os.path.exists(args.extra):
        with open(args.extra) as f:
            for entry in json.load(f).get("services", []):
                overrides[entry["name"]] = entry

    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    results = []
    for svc in services:
        name = svc["name"]
        if name in overrides:
            ov = overrides[name]
            results.append({
                "name": name,
                "state": ov.get("state", "unknown"),
                "note": ov.get("note", ""),
                "cadence": svc.get("cadence", ""),
                "description": svc.get("description", ""),
                "checked_at": now,
            })
            continue
        checker = CHECKERS.get(svc.get("kind"))
        if checker is None:
            results.append({
                "name": name, "state": "unknown",
                "note": f"kind '{svc.get('kind')}' needs an external resolver",
                "cadence": svc.get("cadence", ""),
                "description": svc.get("description", ""),
                "checked_at": now,
            })
            continue
        state, note = checker(svc)
        results.append({
            "name": name, "state": state, "note": note,
            "cadence": svc.get("cadence", ""),
            "description": svc.get("description", ""),
            "checked_at": now,
        })

    counts = {}
    for r in results:
        counts[r["state"]] = counts.get(r["state"], 0) + 1
    payload = {"generated_at": now, "summary": counts, "services": results}

    os.makedirs(args.out, exist_ok=True)
    with open(os.path.join(args.out, "status.json"), "w") as f:
        json.dump(payload, f, indent=2)

    lines = [
        "# Watchtower Status",
        "",
        f"Generated: `{now}` (UTC)",
        "",
        f"**Summary:** " + ", ".join(f"{v} {k}" for k, v in sorted(counts.items())),
        "",
        "| Service | State | Cadence | Note |",
        "|---|---|---|---|",
    ]
    dot = {"operational": "🟢", "paused": "⏸️", "degraded": "🔴", "unknown": "⚪"}
    for r in results:
        lines.append(
            f"| {r['name']} | {dot.get(r['state'], '❔')} {r['state']} | {r['cadence']} | {r['note']} |"
        )
    lines += [
        "",
        "_Paused means the operator deliberately paused the service — a decision, not an outage._",
        "",
    ]
    with open(os.path.join(args.out, "STATUS.md"), "w") as f:
        f.write("\n".join(lines))

    print(json.dumps({"generated_at": now, "summary": counts}))
    return 0 if counts.get("degraded", 0) == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
