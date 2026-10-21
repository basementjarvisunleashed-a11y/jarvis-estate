"""Cross-artifact consistency audit — Phase 2 (2026-10-20).

Verifies that the estate's artifacts agree with each other, parsing
each one fresh at run time (nothing is taken on trust from any
document's own claims):

 1. The invariant catalogue holds exactly 27 invariants; the
    traceability matrix holds exactly 27 rows; the ID sets are equal.
 2. Every catalogue statement matches ROADMAP.md section 5 verbatim.
 3. The event vocabulary: contracts/events.md defines 19 events; the
    TLA+ spec references exactly T1..T21; every T-number binds (via
    events.md) to a vocabulary event, and the two T-less events are
    exactly brief_received (creation) and execution_started (within
    `executing`) — so the .tla's transitions and the events.md
    vocabulary describe the same 19 events.
 4. The state set: exactly 12 states (3 terminal) in the .tla.
 5. Transitions: exactly 21 (T1..T21) in both the spec and events.md.
 6. Every INVARIANT / PROPERTY name in spec/state-machine.cfg is
    defined in spec/state-machine.tla, and every conjunct of
    SafetyInvs is defined there too.
 7. Every Phase 1 number cited in tests/*.md (distinct states,
    invariant violations, generated states, spec fixes) matches
    proofs/phase1-tlc-report.md, parsed from the report itself.

Exit code 0 iff every check passes. Python 3 stdlib only.
Run:  python3 tests/audit_crosscheck.py     (from the repo root)
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "layer1"))
import spec_model as sm  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
TESTS = ROOT / "tests"

RESULTS = []


def check(name, ok, detail):
    RESULTS.append((name, ok, detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: {detail}")


def table_ids(path, prefix="INV-"):
    ids = []
    for line in path.read_text(encoding="utf-8").splitlines():
        m = re.match(r"\|\s*(INV-[CAESR]\d)\s*\|", line)
        if m:
            ids.append(m.group(1))
    return ids


# --- 1. Catalogue = matrix = 27, same IDs --------------------------------
catalogue = TESTS / "invariant-catalogue.md"
matrix = TESTS / "traceability-matrix.md"
cat_ids = table_ids(catalogue)
mat_ids = table_ids(matrix)
check("catalogue-count", len(cat_ids) == 27 and len(set(cat_ids)) == 27,
      f"{len(cat_ids)} rows, {len(set(cat_ids))} unique IDs")
check("matrix-count", len(mat_ids) == 27 and len(set(mat_ids)) == 27,
      f"{len(mat_ids)} rows, {len(set(mat_ids))} unique IDs")
check("catalogue-matrix-id-parity", set(cat_ids) == set(mat_ids),
      "ID sets equal" if set(cat_ids) == set(mat_ids)
      else f"catalogue-only {sorted(set(cat_ids) - set(mat_ids))}, "
           f"matrix-only {sorted(set(mat_ids) - set(cat_ids))}")

# --- 2. Catalogue statements verbatim vs ROADMAP.md section 5 ------------
roadmap = (ROOT / "ROADMAP.md").read_text(encoding="utf-8")
section5 = roadmap[roadmap.index("# 5. Phase 2"):roadmap.index("# 6. Phase 3")]
roadmap_statements = {}
for m in re.finditer(r"INV-([CAESR]\d+): ([^.]+)\.", section5):
    roadmap_statements["INV-" + m.group(1)] = m.group(2).strip()
cat_statements = {}
for line in catalogue.read_text(encoding="utf-8").splitlines():
    m = re.match(r"\|\s*(INV-[CAESR]\d)\s*\|\s*([^|]+)\|", line)
    if m:
        cat_statements[m.group(1)] = m.group(2).strip()
mismatches = {i: (roadmap_statements.get(i), cat_statements.get(i))
              for i in set(roadmap_statements) | set(cat_statements)
              if roadmap_statements.get(i) != cat_statements.get(i)}
check("catalogue-statements-verbatim",
      len(roadmap_statements) == 27 and not mismatches,
      f"{len(roadmap_statements)} statements parsed from ROADMAP.md §5; "
      + ("all 27 match the catalogue verbatim" if not mismatches
         else f"mismatches: {mismatches}"))

# --- 3/4/5. Vocabulary, states, transitions -------------------------------
events = sm.parse_events()
states = sm.parse_states()
terminal = sm.parse_terminal_states()
tla_ts = sm.parse_tla_t_numbers()
legal, by_t = sm.build_legal_table()
check("events-count", len(events) == 19,
      f"events.md defines {len(events)} events")
# T-bindings are read from the per-event transition rows (parse_event_
# transitions), not from by_t: by_t keys T-numbers to a single event,
# which cannot represent the JOINT T6 binding (artifact_produced +
# evidence_packet_created). The per-event rows can and do.
event_rows = sm.parse_event_transitions()
t_bound_events = {e for e, rows in event_rows.items() if rows}
ts_referenced = set()
for rows in event_rows.values():
    ts_referenced |= set(rows)
t_less = set(events) - t_bound_events
check("tla-events-parity",
      tla_ts == set(range(1, 22)) and ts_referenced == tla_ts
      and t_bound_events <= set(events)
      and t_less == {"brief_received", "execution_started"},
      f".tla references T{sorted(tla_ts)[0]}..T{sorted(tla_ts)[-1]} "
      f"({len(tla_ts)} numbers); {len(t_bound_events)} events bound to "
      f"T-numbers (T6 jointly to artifact_produced and "
      f"evidence_packet_created); T-less events: {sorted(t_less)}")
check("states-count", len(states) == 12 and len(terminal) == 3,
      f"{len(states)} states, {len(terminal)} terminal "
      f"({', '.join(sorted(terminal))})")
check("transitions-count",
      len(by_t) == 21 and set(by_t) == set(range(1, 22))
      and tla_ts == set(range(1, 22)),
      f"21 transitions in events.md table and in .tla references")

# --- 6. cfg names defined in the .tla --------------------------------------
cfg_text = (ROOT / "spec" / "state-machine.cfg").read_text(encoding="utf-8")
cfg_names = re.findall(r"^(?:INVARIANTS?|PROPERT(?:Y|IES))\s+(\w+)",
                       cfg_text, re.M)
defs = sm._definitions(sm.TLA.read_text(encoding="utf-8"))
undefined = [n for n in cfg_names if n not in defs]
check("cfg-names-defined", bool(cfg_names) and not undefined,
      f"cfg declares {cfg_names}; "
      + ("all defined in state-machine.tla" if not undefined
         else f"UNDEFINED: {undefined}"))
safety_body = defs.get("SafetyInvs", "")
conjuncts = re.findall(r"/\\\s*([A-Za-z][A-Za-z0-9_]*)", safety_body)
missing_conjuncts = [c for c in conjuncts if c not in defs]
check("safetyinvs-conjuncts-defined",
      bool(conjuncts) and not missing_conjuncts,
      f"SafetyInvs has {len(conjuncts)} conjuncts; "
      + ("all defined" if not missing_conjuncts
         else f"UNDEFINED: {missing_conjuncts}"))

# --- 7. Phase 1 numbers cited in tests/*.md vs the TLC report --------------
report = (ROOT / "proofs" / "phase1-tlc-report.md").read_text(
    encoding="utf-8")
rep_states = re.search(r"([\d,]+) distinct states", report).group(1)
rep_generated = re.search(r"\(([\d,]+) generated\)", report).group(1)
rep_zero = "zero invariant violations" in report
rep_fixes = len(re.findall(r"^### Fix \d+:", report, re.M))
check("phase1-report-figures",
      rep_states == "3,266,929" and rep_generated == "205,173,020"
      and rep_zero and rep_fixes == 6,
      f"report: {rep_states} distinct states, {rep_generated} "
      f"generated, zero violations: {rep_zero}, fixes: {rep_fixes}")

problems = []
for md in sorted(TESTS.glob("*.md")):
    text = md.read_text(encoding="utf-8")
    for value in re.findall(r"([\d,]+) distinct states", text):
        if value != rep_states:
            problems.append(f"{md.name}: cites {value} distinct states")
    for value in re.findall(r"([\d,]+) generated", text):
        if value != rep_generated:
            problems.append(f"{md.name}: cites {value} generated")
    for word in re.findall(r"(\w+) invariant violations", text):
        if word.lower() != "zero":
            problems.append(
                f"{md.name}: cites '{word} invariant violations'")
    for num in re.findall(r"(six|\d+) (?:genuine )?(?:spec )?"
                          r"(?:bugs|fixes)\b", text):
        if num not in ("six", "6"):
            problems.append(f"{md.name}: cites {num} spec bugs/fixes")
    for num in re.findall(r"after (?:the )?(\w+) fixes", text):
        if num not in ("six", "6"):
            problems.append(f"{md.name}: cites 'after {num} fixes'")
check("tests-md-phase1-citations", not problems,
      "every Phase 1 figure cited in tests/*.md matches the report"
      if not problems else "; ".join(problems))

# --- verdict -----------------------------------------------------------------
failed = [n for n, ok, _ in RESULTS if not ok]
print()
print(f"Crosscheck: {len(RESULTS) - len(failed)}/{len(RESULTS)} checks "
      f"passed" + (f"; FAILED: {failed}" if failed else ""))
sys.exit(1 if failed else 0)
