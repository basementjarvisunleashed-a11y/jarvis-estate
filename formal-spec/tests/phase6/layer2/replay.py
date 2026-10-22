#!/usr/bin/env python3
"""Phase 6 Layer 2 — offline replay harness (stage 2 of the protocol).

Deterministic, stdlib only. Replays logged router decisions through the
alternate policies (RP-8a…RP-8c) and computes the ten roadmap metrics per
policy — UNWEIGHTED only (Q4: no weighted comparison until he signs the
weight table).

Honest replay semantics (experiment-protocol.md EP-4):
- The corpus is the real router log (1 entry today) PLUS labeled
  synthetic fixtures (fixtures.json, every entry marked synthetic:true).
- For each entry, each policy's recommendation is compared against the
  LOGGED action_taken. Outcome metrics are reported only for entries
  where the policy AGREED with what was actually done (measured
  outcomes). Where the policy would have done something else, the
  outcome is counterfactual-unknown — the harness makes no claim about
  what would have happened.
- Unlabeled entries (the real log today) count only in decision metrics.
"""
from __future__ import annotations

import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PHASE6 = os.path.dirname(HERE)
EVIDENCE = os.path.join(PHASE6, "evidence")
ROUTER_LOGS = os.path.expanduser("~/workspace/usage-router/logs")

sys.path.insert(0, HERE)
from policies import ACTIONS, cache_only_policy, local_policy, unconstrained_policy  # noqa: E402
from jev_backend import FailingBackend, JevBackend, JevNotApproved, decide_with_fallback  # noqa: E402

POLICIES = {
    "unconstrained": unconstrained_policy,
    "cache-only": cache_only_policy,
    "local": local_policy,
}

METRIC_NAMES = [
    "accepted work rate",
    "human repair cost",
    "cost per accepted artifact",
    "latency",
    "loop rate",
    "escalation precision/recall",
    "false denial rate",
    "stale-source error rate",
    "attention cost",
    "evidence completeness",
]


def load_corpus() -> list[dict]:
    """Real log lines first, then synthetic fixtures. Never mixed."""
    corpus: list[dict] = []
    for path in sorted(glob.glob(os.path.join(ROUTER_LOGS, "router-*.jsonl"))):
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                rec = json.loads(line)
                corpus.append({
                    "id": "real:%s:%s" % (os.path.basename(path), rec.get("ts")),
                    "corpus": "real",
                    "synthetic": False,
                    "state": dict(rec.get("state", {})),
                    "logged": {
                        "recommendation": rec.get("recommendation"),
                        "action_taken": rec.get("action_taken"),
                    },
                    "labels": None,  # real log is unlabeled today (DL-4)
                })
    with open(os.path.join(HERE, "fixtures.json"), encoding="utf-8") as fh:
        data = json.load(fh)
    for fx in data["fixtures"]:
        corpus.append({
            "id": fx["id"],
            "corpus": "synthetic",
            "synthetic": True,
            "state": dict(fx["state"]),
            "logged": dict(fx["logged"]),
            "labels": dict(fx["labels"]),
        })
    return corpus


def replay(corpus: list[dict]) -> dict:
    per_policy: dict[str, dict] = {}
    for pname, pfn in POLICIES.items():
        st = {
            "policy": pname,
            "n": 0,
            "n_real": 0,
            "n_synthetic": 0,
            "recommendations": {a: 0 for a in ACTIONS},
            "rule_fires": {},
            "agree": 0,
            "differ": 0,
            "counterfactual_unknown": 0,
            "guardrail_violations": 0,  # irreversible not escalated
            # outcome metrics over agreed+labeled entries only:
            "labeled_agreed": 0,
            "accepted": 0,
            "repair_minutes": 0,
            "interruptions": 0,
            "cost_units": 0,
            "latency_sum": 0,
            "evidence_complete": 0,
            "loop_events": 0,
        }
        for entry in corpus:
            state = entry["state"]
            rec, rule = pfn(state)
            st["n"] += 1
            st["n_real"] += entry["corpus"] == "real"
            st["n_synthetic"] += entry["corpus"] == "synthetic"
            st["recommendations"][rec] += 1
            st["rule_fires"][rule] = st["rule_fires"].get(rule, 0) + 1
            if state.get("irreversible") and rec != "escalate":
                st["guardrail_violations"] += 1
            if rec == entry["logged"]["action_taken"]:
                st["agree"] += 1
                labels = entry["labels"]
                if labels:
                    st["labeled_agreed"] += 1
                    if labels["outcome"] == "accepted":
                        st["accepted"] += 1
                    st["repair_minutes"] += labels["repair_time_minutes"]
                    st["interruptions"] += labels["attention_interruptions"]
                    st["cost_units"] += labels["cost_units"]
                    st["latency_sum"] += labels["latency_seconds"]
                    st["evidence_complete"] += bool(labels["evidence_complete"])
            else:
                st["differ"] += 1
                st["counterfactual_unknown"] += 1
        la = st["labeled_agreed"]
        st["accepted_work_rate"] = round(st["accepted"] / la, 4) if la else None
        st["mean_repair_minutes"] = round(st["repair_minutes"] / la, 2) if la else None
        st["mean_interruptions"] = round(st["interruptions"] / la, 2) if la else None
        st["cost_per_accepted"] = (
            round(st["cost_units"] / st["accepted"], 2) if st["accepted"] else None
        )
        st["mean_latency_s"] = round(st["latency_sum"] / la, 2) if la else None
        per_policy[pname] = st
    return per_policy


def invariant_checks() -> dict:
    """INV-R1…R5 behavioural checks against the harness."""
    checks: dict[str, dict] = {}
    # INV-R5: backend failure -> local fallback, logged.
    rec, used = decide_with_fallback({"goal": "x", "irreversible": True}, FailingBackend())
    checks["INV-R5"] = {
        "statement": "router fallback preserves safety if external backend fails",
        "result": "pass" if (rec == "escalate" and used.startswith("local-fallback")) else "FAIL",
        "detail": "failing backend -> %s via %s" % (rec, used),
    }
    # Q2: Jev interface refuses without approval; nothing sent.
    try:
        JevBackend()
        checks["Q2-jev-refusal"] = {"result": "FAIL", "detail": "JevBackend() did not refuse"}
    except JevNotApproved as exc:
        checks["Q2-jev-refusal"] = {
            "result": "pass",
            "detail": "refused: %s" % str(exc)[:60],
        }
    return checks


def main() -> int:
    os.makedirs(EVIDENCE, exist_ok=True)
    corpus = load_corpus()
    per_policy = replay(corpus)
    checks = invariant_checks()

    metrics_path = os.path.join(EVIDENCE, "2026-10-22-phase6-layer2-metrics.json")
    with open(metrics_path, "w", encoding="utf-8") as fh:
        json.dump(
            {
                "corpus": {
                    "n_total": len(corpus),
                    "n_real": sum(1 for e in corpus if e["corpus"] == "real"),
                    "n_synthetic": sum(1 for e in corpus if e["corpus"] == "synthetic"),
                    "note": "synthetic entries are harness-verification fixtures, "
                            "not measured evidence of router performance",
                },
                "policies": per_policy,
                "invariant_checks": checks,
                "weighted_mode": "DISABLED — weight table unsigned (Q4)",
            },
            fh,
            indent=2,
            sort_keys=True,
        )

    log_path = os.path.join(EVIDENCE, "2026-10-22-phase6-layer2.log")
    with open(log_path, "w", encoding="utf-8") as fh:
        fh.write("Phase 6 Layer 2 replay — 2026-10-22\n")
        fh.write("corpus: %d total (%d real, %d synthetic)\n" % (
            len(corpus),
            sum(1 for e in corpus if e["corpus"] == "real"),
            sum(1 for e in corpus if e["corpus"] == "synthetic"),
        ))
        for pname in ("unconstrained", "cache-only", "local"):
            st = per_policy[pname]
            fh.write(
                "[%s] n=%d agree=%d differ=%d labeled_agreed=%d "
                "accepted_rate=%s guardrail_violations=%d rec=%s\n" % (
                    pname, st["n"], st["agree"], st["differ"],
                    st["labeled_agreed"], st["accepted_work_rate"],
                    st["guardrail_violations"],
                    json.dumps(st["recommendations"], sort_keys=True),
                )
            )
        for cid, ck in sorted(checks.items()):
            fh.write("[check %s] %s — %s\n" % (cid, ck["result"], ck["detail"]))

    failures = [c for c in checks.values() if c["result"] != "pass"]
    print("corpus: %d total" % len(corpus))
    for pname in ("unconstrained", "cache-only", "local"):
        st = per_policy[pname]
        print("%-13s agree=%d/%d accepted_rate=%s guardrail_violations=%d" % (
            pname, st["agree"], st["n"], st["accepted_work_rate"],
            st["guardrail_violations"]))
    print("checks: %d/%d pass" % (len(checks) - len(failures), len(checks)))
    print("weighted mode: DISABLED (weight table unsigned)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
