#!/usr/bin/env python3
"""Phase 6 Layer 2 — offline replay harness (stage 2 of the protocol).

Deterministic, stdlib only. Replays logged router decisions through the
alternate policies (RP-8a…RP-8c) and computes the ten roadmap metrics per
policy.

Weighted mode (--weighted): computes WT-9 per policy using the SIGNED
weight table (weight-table.md, all six weights signed 2026-10-22
~13:09–13:14 ET). Weights are parsed from the signed document — never
hardcoded. The weighted gate is OPEN.

Honest replay semantics (experiment-protocol.md EP-4, decision-log-schema.md DL-4):
- The corpus is the real router log lines (router-*.jsonl under
  ~/workspace/usage-router/logs/), optionally PLUS labeled synthetic
  fixtures (fixtures.json, every entry marked synthetic:true) with
  --corpus all. Weighted EVIDENCE runs use --corpus real only; the
  synthetic set is a separately-labeled sanity check, never evidence.
- For each entry, each policy's recommendation is compared against the
  LOGGED action_taken. Outcome metrics are reported only for entries
  where the policy AGREED with what was actually done (measured
  outcomes). Where the policy would have done something else, the
  outcome is counterfactual-unknown — the harness makes no claim about
  what would have happened.
- Entries whose action_taken is "unknown" can never agree — decision
  metrics only.
- Per DL-4, entries with unknown outcome labels are EXCLUDED from
  outcome metrics (counted in decision metrics only). Numeric labels
  that are "unknown" contribute 0 to sums and are counted as unknown —
  the harness never invents them.
- Weighted score terms: accepted_work counts outcome == "accepted" only
  (repaired/rejected contribute 0 — stated, not smoothed). Loops are
  detected in the decision state (action_repeat_count >= 3, the RP-6.3
  condition). Latency-over-budget needs both latency_seconds and a
  stated budget; both absent → 0, counted unknown.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PHASE6 = os.path.dirname(HERE)
EVIDENCE = os.path.join(PHASE6, "evidence")
ROUTER_LOGS = os.path.expanduser("~/workspace/usage-router/logs")
WEIGHT_TABLE = os.path.join(PHASE6, "weight-table.md")

sys.path.insert(0, HERE)
from policies import ACTIONS, cache_only_policy, local_policy, unconstrained_policy  # noqa: E402
from jev_backend import FailingBackend, JevBackend, JevNotApproved, decide_with_fallback  # noqa: E402

POLICIES = {
    "unconstrained": unconstrained_policy,
    "cache-only": cache_only_policy,
    "local": local_policy,
}

# WT-9 terms, in document order. Parsed from the signed weight table.
WEIGHT_TERMS = [
    "accepted_work",               # WT-3
    "human_repair_minutes",        # WT-4
    "attention_interruptions",     # WT-5
    "cost_units",                  # WT-6
    "loops",                       # WT-7
    "latency_over_budget_seconds", # WT-8
]
WT_NUMBER_TO_TERM = {
    "3": "accepted_work",
    "4": "human_repair_minutes",
    "5": "attention_interruptions",
    "6": "cost_units",
    "7": "loops",
    "8": "latency_over_budget_seconds",
}
NUMERIC_TERMS = [
    "human_repair_minutes",
    "attention_interruptions",
    "cost_units",
    "latency_over_budget_seconds",
]
# corpus label key -> WT-9 term
LABEL_TO_TERM = {
    "repair_time_minutes": "human_repair_minutes",
    "attention_interruptions": "attention_interruptions",
    "cost_units": "cost_units",
}


def parse_weights(path: str = WEIGHT_TABLE) -> dict:
    """Parse the SIGNED weights from weight-table.md. Fails loudly unless
    all six are present and marked SIGNED — the gate check."""
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    weights: dict[str, float] = {}
    for m in re.finditer(
        r"\|\s*WT-([3-8])\s*\|[^|]*\|[^|]*\|\s*\*\*\s*([+\-−]?\d+(?:\.\d+)?)\s*—\s*SIGNED",
        text,
    ):
        # the table uses U+2212 MINUS SIGN for negatives — normalize it
        weights[WT_NUMBER_TO_TERM[m.group(1)]] = float(m.group(2).replace("−", "-"))
    missing = [t for t in WEIGHT_TERMS if t not in weights]
    if missing:
        raise SystemExit(
            "weighted gate CLOSED: weight-table.md lacks SIGNED values for %s"
            % ", ".join(missing)
        )
    return weights


def is_known(v) -> bool:
    return v is not None and v != "unknown"


def numeric(v):
    """A real number, or None. Booleans are not numbers (corpus uses
    True/False/"unknown" for flags)."""
    if isinstance(v, bool):
        return None
    return v if isinstance(v, (int, float)) else None


def load_corpus(which: str = "all") -> list[dict]:
    """Real log lines first, then synthetic fixtures only if which == "all".
    Never mixed silently — every entry carries its corpus tag."""
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
                    # outcome_labels may be absent/None (old real log) or
                    # carry "unknown" values (backfill) — handled per DL-4.
                    "labels": rec.get("outcome_labels"),
                })
    if which == "all":
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


def detect_loop(state: dict) -> int:
    """A loop event is detected in the decision state when the RP-6.3
    condition holds (action_repeat_count >= 3). 1 or 0."""
    arc = state.get("action_repeat_count") or 0
    return 1 if arc >= 3 else 0


def replay(corpus: list[dict], weights: dict | None = None) -> dict:
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
            "action_unknown": 0,  # action_taken == "unknown": can never agree
            "counterfactual_unknown": 0,
            "guardrail_violations": 0,  # irreversible not escalated
            # outcome metrics over agreed + outcome-known entries only (DL-4):
            "labeled_agreed": 0,
            "excluded_outcome_unknown": 0,
            "accepted": 0,
            "repair_minutes": 0,
            "repair_minutes_unknown": 0,
            "interruptions": 0,
            "interruptions_unknown": 0,
            "cost_units": 0,
            "cost_units_unknown": 0,
            "latency_sum": 0,
            "latency_unknown": 0,
            "evidence_complete": 0,
            "loop_events": 0,
        }
        if weights is not None:
            st["weighted"] = {
                "contributing": 0,  # agreed + outcome known
                "excluded_action_unknown": 0,
                "excluded_outcome_unknown": 0,
                "terms": {t: 0 for t in WEIGHT_TERMS},
                "terms_unknown": {t: 0 for t in NUMERIC_TERMS},
                "score": None,
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
            action_taken = entry["logged"]["action_taken"]
            if action_taken == "unknown":
                st["action_unknown"] += 1
                st["differ"] += 1
                st["counterfactual_unknown"] += 1
                if weights is not None:
                    st["weighted"]["excluded_action_unknown"] += 1
                continue
            if rec == action_taken:
                st["agree"] += 1
                labels = entry["labels"] or {}
                outcome = labels.get("outcome")
                if not is_known(outcome):
                    st["excluded_outcome_unknown"] += 1
                    if weights is not None:
                        st["weighted"]["excluded_outcome_unknown"] += 1
                    continue
                st["labeled_agreed"] += 1
                if outcome == "accepted":
                    st["accepted"] += 1
                # numeric labels: accumulate only real numbers; count unknowns
                for lkey, skey, ukey in (
                    ("repair_time_minutes", "repair_minutes", "repair_minutes_unknown"),
                    ("attention_interruptions", "interruptions", "interruptions_unknown"),
                    ("cost_units", "cost_units", "cost_units_unknown"),
                    ("latency_seconds", "latency_sum", "latency_unknown"),
                ):
                    v = numeric(labels.get(lkey))
                    if v is None:
                        st[ukey] += 1
                    else:
                        st[skey] += v
                if is_known(labels.get("evidence_complete")):
                    st["evidence_complete"] += bool(labels["evidence_complete"])
                st["loop_events"] += detect_loop(state)
                if weights is not None:
                    w = st["weighted"]
                    w["contributing"] += 1
                    terms = w["terms"]
                    tu = w["terms_unknown"]
                    if outcome == "accepted":
                        terms["accepted_work"] += 1
                    # repaired / rejected contribute 0 to accepted_work (stated)
                    for lkey, term in LABEL_TO_TERM.items():
                        v = numeric(labels.get(lkey))
                        if v is None:
                            tu[term] += 1
                        else:
                            terms[term] += v
                    terms["loops"] += detect_loop(state)
                    lat = numeric(labels.get("latency_seconds"))
                    bud = numeric(state.get("latency_budget_seconds"))
                    if lat is None or bud is None:
                        tu["latency_over_budget_seconds"] += 1
                    else:
                        terms["latency_over_budget_seconds"] += max(0.0, lat - bud)
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
        if weights is not None:
            w = st["weighted"]
            w["score"] = round(
                sum(weights[t] * w["terms"][t] for t in WEIGHT_TERMS), 4
            )
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


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Phase 6 Layer 2 offline replay harness")
    ap.add_argument("--weighted", action="store_true",
                    help="compute WT-9 per policy (requires signed weight table)")
    ap.add_argument("--corpus", choices=("real", "all"), default="all",
                    help="'real': router logs only (evidence runs). "
                         "'all': plus synthetic fixtures (sanity check).")
    args = ap.parse_args(argv)

    weights = parse_weights() if args.weighted else None
    corpus = load_corpus(args.corpus)
    per_policy = replay(corpus, weights)
    checks = invariant_checks()

    tag = "weighted" if args.weighted else "unweighted"
    synthetic_note = (
        "SANITY CHECK ONLY — includes synthetic fixtures; NOT evidence"
        if args.corpus == "all" and args.weighted else
        ("synthetic entries are harness-verification fixtures, "
         "not measured evidence of router performance"
         if args.corpus == "all" else
         "real router logs only — no synthetic entries")
    )
    metrics = {
        "mode": tag,
        "corpus": {
            "selection": args.corpus,
            "n_total": len(corpus),
            "n_real": sum(1 for e in corpus if e["corpus"] == "real"),
            "n_synthetic": sum(1 for e in corpus if e["corpus"] == "synthetic"),
            "note": synthetic_note,
        },
        "policies": per_policy,
        "invariant_checks": checks,
    }
    if args.weighted:
        metrics["weights"] = {
            "source": "weight-table.md (ALL SIGNED 2026-10-22 ~13:09–13:14 ET)",
            "values": weights,
            "formula": ("score = 1.0*accepted_work - 5.0*human_repair_minutes "
                        "- 10.0*attention_interruptions - 1.0*cost_units "
                        "- 8.0*loops - 0.1*latency_over_budget_seconds"),
            "honesty": ("unknown numeric labels contribute 0 and are counted; "
                        "accepted_work counts outcome=='accepted' only; "
                        "loops detected in state (action_repeat_count>=3); "
                        "latency-over-budget needs stated budget (absent->0, unknown)"),
        }
    else:
        metrics["weighted_mode"] = "DISABLED"

    suffix = "-weighted" if args.weighted else ""
    metrics_path = os.path.join(EVIDENCE, "2026-10-22-phase6-layer2%s-metrics.json" % suffix)
    os.makedirs(EVIDENCE, exist_ok=True)
    with open(metrics_path, "w", encoding="utf-8") as fh:
        json.dump(metrics, fh, indent=2, sort_keys=True)

    log_path = os.path.join(EVIDENCE, "2026-10-22-phase6-layer2%s.log" % suffix)
    with open(log_path, "w", encoding="utf-8") as fh:
        fh.write("Phase 6 Layer 2 replay (%s) — 2026-10-22\n" % tag)
        fh.write("corpus: %s — %d total (%d real, %d synthetic)\n" % (
            args.corpus,
            len(corpus),
            sum(1 for e in corpus if e["corpus"] == "real"),
            sum(1 for e in corpus if e["corpus"] == "synthetic"),
        ))
        if args.weighted:
            fh.write("weights: %s\n" % json.dumps(weights, sort_keys=True))
        for pname in ("unconstrained", "cache-only", "local"):
            st = per_policy[pname]
            fh.write(
                "[%s] n=%d agree=%d differ=%d action_unknown=%d labeled_agreed=%d "
                "excluded_outcome_unknown=%d accepted_rate=%s guardrail_violations=%d rec=%s\n" % (
                    pname, st["n"], st["agree"], st["differ"],
                    st["action_unknown"], st["labeled_agreed"],
                    st["excluded_outcome_unknown"], st["accepted_work_rate"],
                    st["guardrail_violations"],
                    json.dumps(st["recommendations"], sort_keys=True),
                )
            )
            if args.weighted:
                w = st["weighted"]
                fh.write(
                    "  weighted: contributing=%d score=%s terms=%s terms_unknown=%s\n" % (
                        w["contributing"], w["score"],
                        json.dumps(w["terms"], sort_keys=True),
                        json.dumps(w["terms_unknown"], sort_keys=True),
                    )
                )
        for cid, ck in sorted(checks.items()):
            fh.write("[check %s] %s — %s\n" % (cid, ck["result"], ck["detail"]))

    failures = [c for c in checks.values() if c["result"] != "pass"]
    print("mode: %s | corpus: %s (%d total)" % (tag, args.corpus, len(corpus)))
    for pname in ("unconstrained", "cache-only", "local"):
        st = per_policy[pname]
        line = "%-13s agree=%d/%d accepted_rate=%s guardrail_violations=%d" % (
            pname, st["agree"], st["n"], st["accepted_work_rate"],
            st["guardrail_violations"])
        if args.weighted:
            w = st["weighted"]
            line += " | weighted: contributing=%d score=%s" % (w["contributing"], w["score"])
        print(line)
    print("checks: %d/%d pass" % (len(checks) - len(failures), len(checks)))
    if args.weighted:
        print("weights: %s" % json.dumps(weights, sort_keys=True))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
