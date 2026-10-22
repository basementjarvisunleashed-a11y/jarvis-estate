"""Layer 1 reference model for the J.A.R.V.I.S. Phase 2 invariant suite.

Parses the ratified Phase 0/1 artifacts (contracts/events.md and
spec/state-machine.tla) and implements the spec's guard semantics
(can_enter_executing, ServerRecordsApproval, can_enter_completed) as
fail-closed Python reference checks.

Nothing here modifies the artifacts; they are read-only inputs.
Paths resolve relative to this file: tests/layer1/ -> repo root is
two directories up.
"""

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EVENTS_MD = ROOT / "contracts" / "events.md"
TLA = ROOT / "spec" / "state-machine.tla"

# ---------------------------------------------------------------------------
# Parsing: contracts/events.md
# ---------------------------------------------------------------------------

_EVENT_ROW = re.compile(r"^\|\s*\d+\s*\|\s*`([a-z_]+)`", re.M)
_T_REF = re.compile(r"T(\d+)\b")
_ARROW = re.compile(r"([a-z_]+|any state)\s*→\s*`?([a-z_]+)`?")


def parse_events(text=None):
    """Return the canonical event names, in document order (19 expected)."""
    text = EVENTS_MD.read_text(encoding="utf-8") if text is None else text
    return _EVENT_ROW.findall(text)


def parse_event_transitions(text=None):
    """Return {event: {t_number: (from_state, to_state)}} from events.md.

    from_state is the string "ANY" where the table says "any state".
    Events with no T-number (brief_received, execution_started) map to {}.
    """
    text = EVENTS_MD.read_text(encoding="utf-8") if text is None else text
    out = {}
    for line in text.splitlines():
        m = _EVENT_ROW.match(line)
        if not m:
            continue
        event = m.group(1)
        cells = line.split("|")
        # Columns: ['', ' # ', ' Event ', ' Fires when ', ' Payload ',
        #           ' Transitions ', ' Papers ', '']
        transitions_cell = cells[5] if len(cells) > 5 else ""
        rows = {}
        refs = list(_T_REF.finditer(transitions_cell))
        for i, ref in enumerate(refs):
            seg_end = refs[i + 1].start() if i + 1 < len(refs) else len(transitions_cell)
            segment = transitions_cell[ref.start():seg_end]
            arrow = _ARROW.search(segment)
            if arrow:
                src = "ANY" if arrow.group(1) == "any state" else arrow.group(1)
                rows[int(ref.group(1))] = (src, arrow.group(2))
            else:
                rows[int(ref.group(1))] = None  # joint ref, resolved below
        out[event] = rows
    # Second pass: a joint reference (T6, fired jointly by artifact_produced
    # and evidence_packet_created) carries its from/to on one row only;
    # resolve the other row's bare T reference from the global T map.
    by_t_global = {}
    for rows in out.values():
        for t, pair in rows.items():
            if pair is not None:
                by_t_global[t] = pair
    for event, rows in out.items():
        out[event] = {t: (pair if pair is not None else by_t_global[t])
                      for t, pair in rows.items()}
    return out


# ---------------------------------------------------------------------------
# Parsing: spec/state-machine.tla
# ---------------------------------------------------------------------------

_DEF_HEADER = re.compile(r"^([A-Za-z][A-Za-z0-9_]*)\s*(?:\([^)]*\))?\s*==", re.M)


def _definitions(text):
    """Split the .tla source into {name: body} for top-level definitions."""
    matches = list(_DEF_HEADER.finditer(text))
    defs = {}
    for i, m in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[m.start():end]
        # A definition's body ends where the next banner/header comment
        # block begins (comment blocks start at column 0 with "(*"); the
        # following action's header comment must not leak into this body
        # (it can name guards, e.g. can_enter_completed, that this action
        # does not use).
        cut = body.find("\n(*", body.find("\n"))
        if cut != -1:
            body = body[:cut]
        defs[m.group(1)] = body
    return defs


def _state_set(text, name):
    m = re.search(name + r"\s*==\s*\{([^}]*)\}", text, re.S)
    if not m:
        raise ValueError(f"{name} set not found in spec")
    return re.findall(r'"([a-z_]+)"', m.group(1))


def parse_states(text=None):
    text = TLA.read_text(encoding="utf-8") if text is None else text
    return _state_set(text, "States")


def parse_terminal_states(text=None):
    text = TLA.read_text(encoding="utf-8") if text is None else text
    return _state_set(text, "TerminalStates")


def parse_spec_transitions(text=None):
    """Extract state-changing actions from the .tla source.

    Returns {action_name: (source, target)} where source is a state name,
    or "ANY_NONTERMINAL" for actions guarded by work_state \\in NonTerminal.
    Sources for ApprovalGranted / AcceptancePassed are resolved through the
    can_enter_executing / can_enter_completed guard definitions, exactly as
    the spec composes them.
    """
    text = TLA.read_text(encoding="utf-8") if text is None else text
    defs = _definitions(text)

    def guard_source(guard_name):
        m = re.search(r'work_state = "([a-z_]+)"', defs[guard_name])
        return m.group(1)

    transitions = {}
    for name, body in defs.items():
        target = re.search(r"""work_state' = "([a-z_]+)\"""", body)
        if not target:
            continue  # not a state-changing action
        if "can_enter_executing" in body:
            source = guard_source("can_enter_executing")
        elif "can_enter_completed" in body:
            source = guard_source("can_enter_completed")
        elif re.search(r"work_state \\in NonTerminal", body):
            source = "ANY_NONTERMINAL"
        else:
            m = re.search(r'work_state = "([a-z_]+)"', body)
            source = m.group(1)
        transitions[name] = (source, target.group(1))
    return transitions


def parse_tla_t_numbers(text=None):
    """T-numbers (T1..T21) referenced in the transitions region of the .tla.

    The region runs from the "Transitions T1" banner to the failure-model
    banner, covering every transition action definition and its header.
    """
    text = TLA.read_text(encoding="utf-8") if text is None else text
    start = text.index("Transitions T1")
    end = text.index("Failure-model actions")
    region = text[start:end]
    return {int(n) for n in re.findall(r"(?<![A-Za-z])T(\d+)(?![0-9])", region)}


def build_legal_table():
    """The legal (from_state, event, to_state) set, cross-built from both
    artifacts: from/to per T-number from contracts/events.md, expanded over
    NonTerminal states where the table says "any state".

    Returns (legal_set, by_t) where by_t maps T-number -> (event, from, to)
    with from already expanded marker "ANY" preserved.
    """
    states = parse_states()
    terminal = set(parse_terminal_states())
    nonterminal = [s for s in states if s not in terminal]
    event_rows = parse_event_transitions()
    legal = set()
    by_t = {}
    for event, rows in event_rows.items():
        for t, (src, dst) in rows.items():
            by_t[t] = (event, src, dst)
            if src == "ANY":
                for s in nonterminal:
                    # Spec discipline (PO-4; Phase 1 Fixes 4-5):
                    # FailureObserved and OperatorPaused require
                    # observation_status = "observed", and in `unknown`
                    # observation is unavailable by construction, so
                    # those two actions are disabled from `unknown` —
                    # the only exit from ignorance is T21 (F6).
                    if s == "unknown" and event in (
                            "failure_observed", "operator_paused"):
                        continue
                    legal.add((s, event, dst))
            else:
                legal.add((src, event, dst))
    # brief_received creates the work item in `received` (events.md section 4).
    legal.add((None, "brief_received", "received"))
    # execution_started fires within `executing` (entry); no state change.
    legal.add(("executing", "execution_started", "executing"))
    return legal, by_t


# ---------------------------------------------------------------------------
# Guard reference implementation (mirrors spec/state-machine.tla)
# ---------------------------------------------------------------------------

#: The eight fields an approval binds (Paper IV section 6.6; INV-A2).
#: HgX's decision Q3 (2026-10-21): the digest binds intent_id and work_id
#: in addition to the six TLA+ concretization fields — paper text over the
#: narrower machine variant. A six-field and an eight-field digest differ
#: entirely; this binding is not reversible without re-hashing history.
INTENT_FIELDS = ("intent_id", "work_id", "action", "target", "effect",
                 "scope", "revision", "expiry")


def intent_digest(intent):
    """SHA-256 over the canonical JSON serialisation of the eight bound
    fields — the ratified digest rule (decision U-1, 2026-10-19) as
    configured by HgX's Q3 decision (2026-10-21). Any change to any bound
    field changes the digest (INV-A2, INV-A3)."""
    canonical = {k: intent[k] for k in INTENT_FIELDS}
    blob = json.dumps(canonical, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def can_enter_executing(s):
    """Mirror of can_enter_executing in spec/state-machine.tla (T9 guard).

    s keys: work_state, approval_state, now, intent, intent_digest,
    revision, session_authorised, operator_pause.
    """
    return (
        s["work_state"] == "awaiting_approval"
        and s["approval_state"] == "recorded"          # recorded, not tapped (INV-A5)
        and s["now"] < s["intent"]["expiry"]           # live intent (INV-A4)
        and s["intent_digest"] == intent_digest(s["intent"])  # recomputed (INV-A3)
        and s["intent"]["revision"] == s["revision"]   # revision-current (INV-A2)
        and s["session_authorised"]                    # authorised session (PO-8)
        and not s["operator_pause"]
    )


def server_record_approval(s):
    """Mirror of ServerRecordsApproval: the only path to "recorded".

    Returns True iff the server may record the operator's tap: the tap
    exists, the intent is unexpired, what was tapped is what is recorded
    (digest match), and the session is authorised. A client gesture alone
    (an offline tap) can never satisfy this (INV-A5).
    s keys: approval_state, now, intent, tap_digest, session_authorised.
    """
    return (
        s["approval_state"] == "tapped"
        and s["now"] < s["intent"]["expiry"]            # INV-A4
        and intent_digest(s["intent"]) == s["tap_digest"]  # PO-3
        and s["session_authorised"]                    # PO-8
    )


def can_enter_completed(s):
    """Mirror of can_enter_completed in spec/state-machine.tla (T15 guard).

    s keys: work_state, evidence_exists, acceptance_passed,
    failure_observed, delegated_claim. The delegated claim is not an
    input to the guard: a claim, however fluent, cannot satisfy it
    (INV-C3, INV-C5). Completion requires the evidence packet and a
    passed acceptance test against observed output, with no failure
    observed (INV-C1, INV-C2).
    """
    return (
        s["work_state"] == "verifying"
        and s["evidence_exists"]
        and s["acceptance_passed"]
        and not s["failure_observed"]
    )


# ---------------------------------------------------------------------------
# Fail-closed transition validation
# ---------------------------------------------------------------------------

class Rejected(Exception):
    """Raised when a transition fails closed."""


def apply_transition(legal, events, states, from_state, event, to_state):
    """Validate one transition against the legal table.

    Fails closed: unknown events, unknown states, and any (from, event,
    to) triple absent from the legal table are rejected.
    """
    if event not in events:
        raise Rejected(f"unknown event: {event!r}")
    if from_state is not None and from_state not in states:
        raise Rejected(f"unknown from-state: {from_state!r}")
    if to_state not in states:
        raise Rejected(f"unknown to-state: {to_state!r}")
    if (from_state, event, to_state) not in legal:
        raise Rejected(f"illegal transition: {from_state} -{event}-> {to_state}")
    return True
