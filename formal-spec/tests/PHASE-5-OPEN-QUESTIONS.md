# Phase 5 — Open Questions
## Needing HgX's word · Opened 2026-10-22

The security formalism cannot be written until these are answered. Each
question: context, options, a recommendation, and a blank answer line
for the walkthrough. Q1 is the Phase 3 OP-3 carryover; Q2 is the Phase 4
P4-OP-5 carryover — both deferred to this phase on the record.

---

### Q1 (Phase 3 OP-3 carryover) — Specify the `device_session_id` lifecycle?

- **Context:** Carried from `tests/phase3/revision-protocol.md` OP-3.
  Enrollment exists in the reference (`phase2/enrollment.py`); the six-
  field revision token carries `device_session_id`; but revocation,
  re-enrollment after device replacement, and session expiry are
  unspecified. The draft asked whether the security phase should
  specify them. This is that phase.
- **Why it matters:** a session identifier with no defined end is a
  trust boundary with a hole in it — the spoofing row (fake approval,
  device-bound session) names the control, but the session's own
  lifecycle is the control's foundation.
- **Options:** (a) specify the full lifecycle here — enrollment,
  revocation, re-enrollment after device replacement, expiry — as part
  of the spoofing controls; (b) specify revocation and expiry only,
  leave re-enrollment mechanics to implementation; (c) leave the whole
  lifecycle to implementation, with the session treated as an opaque
  token in the spec.
- **Recommendation:** (a). This is the security formalism — if the
  session lifecycle doesn't belong here, it belongs nowhere, and the
  spoofing control would rest on an unspecified foundation. The
  specification is the control's precondition.
- **HgX's answer:** (a) specify the full lifecycle here — enrollment, revocation, re-enrollment after device replacement, expiry — as part of the spoofing controls. Answered 2026-10-22 ~07:54 ET.

---

### Q2 (Phase 4 P4-OP-5 carryover) — How does the model treat tool-plane truthfulness?

- **Context:** Carried from `tests/phase4/ambiguity-protocol.md`
  P4-OP-5. The Phase 4 retry rules trust the tool plane to report its
  own outcomes truthfully: a definitive "failed" is taken as observed
  non-occurrence (RF7). A Byzantine tool — one that reports failure
  after executing, or success without executing — was declared outside
  the Phase 4 threat model and deferred here.
- **Why it matters:** the at-most-once guarantee Phase 4 proved rests
  on the tool telling the truth about what it did. The threat model
  must name what happens when it doesn't.
- **Options:** (a) model it as a named threat (Tampering: false
  outcome reporting) with the control being read-after-write
  verification where the integration supports it, and
  strongest-approval or manual execution where it doesn't (per the
  Phase 4 external-system classification); (b) model it as an
  accepted risk with a compensating control (execution records are
  reconciliation inputs, and the escalated unknown path from Q4
  covers the ambiguous case); (c) declare it out of scope for the
  estate model (a tool that lies is a compromised tool, handled by
  revocation, not by protocol).
- **Recommendation:** (a). The objective is to convert honest
  limitations into a formal model, not to file them away. The
  Phase 4 classification already gives the control vocabulary —
  the catalogue just has to use it. (c) would leave the at-most-once
  proof resting on an unnamed assumption.
- **HgX's answer:** (a) model it as a named threat (Tampering: false outcome reporting) with read-after-write verification where supported, strongest-approval or manual execution where not. Answered 2026-10-22 ~07:55 ET.

---

### Q3 — Isolation-level target: stay at L0 or advance?

- **Context:** ROADMAP.md §8 places the estate at **Level 0 —
  procedural** (doctrine-separated roles, shared runtime/filesystem,
  human discipline) and lists the path to L5. The exit criterion asks
  for "procedural isolation documented and compensated" — which is
  L0's job, done honestly. The question is whether this phase also
  advances the target level.
- **Why it matters:** L1 (filesystem/access discipline: per-scope
  directories, path contracts, handoff-only cross-role access, audit
  logs) is real work on the live system, not a spec exercise — it
  changes how the estate is built and run. The formalism can document
  the path without walking it.
- **Options:** (a) stay at L0 for this phase — document the
  procedural isolation, name the compensations for what L0 cannot
  do, and write the upgrade roadmap with honest sequencing; the
  advance itself is later work on his word; (b) advance to L1 in
  this phase — the spec documents double as the build order for
  per-scope directories, path contracts, and audit logs.
- **Recommendation:** (a). The roadmap puts formalization in the
  months 7–9 window; the exit criterion is satisfied by documented,
  compensated L0. L1 is implementation depth — it deserves its own
  order, its own evidence, and his explicit word, not a side effect
  of a formalism phase.
- **HgX's answer:** (a) stay at L0 for this phase — document the procedural isolation, name the compensations, write the upgrade roadmap with honest sequencing. Answered 2026-10-22 ~07:56 ET.

---

### Q4 — Capability-token posture: specify the format now?

- **Context:** The roadmap's model is capability-based: a capability
  specifies subject, action, object, scope, condition, expiry,
  approval requirement, evidence requirement. The macaroon-lineage
  token shape (intent digest + device + expiry + single-use nonce)
  already exists as a reference from the contract-freeze work. L3 of
  the isolation path is capability tokens (short-lived, scoped,
  per-task, auto-expiry) — but the phase target (Q3) may stay at L0.
- **Why it matters:** the capability matrix is a deliverable either
  way; the question is whether the token format is specified now
  (as the matrix's vocabulary) or deferred with issuance mechanics.
- **Options:** (a) specify the capability format now — the eight
  fields as the matrix's normative vocabulary, with issuance,
  storage, and rotation mechanics explicitly deferred; (b) keep
  capabilities as a matrix vocabulary only (who may do what under
  which conditions), with no token format specified; (c) defer the
  whole capability-token subject to the isolation advance.
- **Recommendation:** (a). The matrix needs a vocabulary to be
  written in, and the eight fields are the roadmap's own. Specifying
  the format commits nothing about when tokens get issued — it
  gives the formalism its nouns while the verbs wait for his word.
- **HgX's answer:** (a) specify the capability format now — the eight fields as the matrix's normative vocabulary, with issuance, storage, and rotation mechanics explicitly deferred. Answered 2026-10-22 ~07:57 ET.

---

### Q5 — How does the catalogue treat the honest limitations?

- **Context:** The deployment build's honest limits (approved by HgX
  2026-10-21 ~16:41 ET): the Phase 4 ZK work is the protocol shape,
  NOT true zero-knowledge — production circuits are required; the
  reference ZK is explicitly not a control. Approval fatigue is
  instrumented (attention budget as a monitored quantity), not
  formally modeled. Procedural isolation cannot do what containers
  do. The exit criterion demands a posture "defensible without
  overclaiming."
- **Why it matters:** this is the phase's objective stated as a
  question — "convert honest limitations into a formal security
  model." A limitation written as a footnote is not converted; a
  limitation written as a named threat with a compensating control
  is.
- **Options:** (a) each honest limitation becomes a named threat
  with a compensating control — e.g. "ZK-proofs are protocol-shape
  only" → threat: unverified privacy claim → control: no privacy
  property asserted in evidence; production circuits required
  before any claim; (b) record them as a limitations appendix,
  separate from the threat catalogue; (c) a hybrid — limitations
  that have compensations join the catalogue, the rest stay in the
  appendix.
- **Recommendation:** (a). The objective doesn't say "list the
  limitations" — it says convert them. A named threat with a
  control is the conversion; an appendix is where conversions go
  to be forgotten. The overclaiming the exit criterion forbids is
  exactly what the catalogue prevents.
- **HgX's answer:** (a) each honest limitation becomes a named threat with a compensating control. Answered 2026-10-22 ~07:58 ET.

---

### Q6 — Do the custody doctrines enter the formal model as trust boundaries?

- **Context:** The estate lives its security at L0 through HgX's
  direct orders: Money Bot is the sole custodian of money access;
  Tickler Bot the sole custodian of calendar/email/tasks; Dr Bot is
  sealed; the Overlord is the sole custodian of live location and is
  never named outside its own chat; the R&D lab is sealed — findings
  cross no boundary back. The plan above places them against the
  roadmap's ten boundaries. The question is whether the formalism
  names them.
- **Why it matters:** the formalism describes the estate as it is —
  it does not redesign the doctrines. But a trust boundary the
  model doesn't name is a boundary the model can't reason about,
  and the threat catalogue needs its subjects.
- **Options:** (a) formalize them as named trust boundaries —
  each doctrine becomes a boundary entry with its subjects, its
  assets, and its crossing rules, described exactly as ordered,
  never redesigned; (b) keep them doctrinal — the model references
  the doctrines as out-of-model governance, and the catalogue
  treats "doctrine violation" as the threat with "the doctrine
  itself" as the control; (c) formalize the structural ones
  (custody, sealed lab) and keep the secrecy ones (Overlord's
  unnamed existence) purely doctrinal.
- **Recommendation:** (a), with one reservation honestly stated:
  the Overlord's secrecy is itself a control — naming the
  boundary "the live-location custodian" without naming the
  custodian preserves the secrecy while letting the model reason
  about the boundary. Describe, never redesign — and where
  description would weaken a control, the control wins.
- **HgX's answer:** (a) formalize them as named trust boundaries — described exactly as ordered, never redesigned; where description would weaken a control, the control wins (the boundary is named, never the custodian). Answered 2026-10-22 ~07:59 ET.

---

## Session log

### 2026-10-22 ~07:51 ET — PHASE 5 OPENED (HgX's word)
- "Okay, let's close phase four and start up phase five." Phase 4 was
  already CLOSED 2026-10-21 ~22:31 ET on his word (PROVEN ~22:30 ET);
  this is the Phase 5 opening.
- Opening package: `tests/PHASE-5-PLAN.md` + this file (Q1–Q6
  awaiting his walkthrough; Q1 is the Phase 3 OP-3 carryover, Q2 is
  the Phase 4 P4-OP-5 carryover).
- The work layers open on his word after the walkthrough — this
  package is the opening, not the work.

## Walkthrough complete
- 2026-10-22 ~07:59 ET: all six questions answered in the one-by-one walkthrough — Q1 full device_session_id lifecycle specified here, Q2 tool-plane truthfulness as a named Tampering threat, Q3 stay at L0 with documented compensations, Q4 capability format specified now with issuance deferred, Q5 honest limitations as named threats with compensating controls, Q6 custody doctrines formalized as named boundaries (boundary named, never the custodian). Phase 5 work layers open on his word.

## Phase closure
- **CLOSED 2026-10-22 ~12:44 ET on HgX's word** ("Close phase five and open up phase six").
- PROVEN 2026-10-22 ~12:43 ET: report `tests/PHASE-5-PROVEN-REPORT-2026-10-22.md` — L2 93/93, L3 34/34, 146/146 claims audited, 33-file integrity manifest, all five exit criteria met.
- Open points carried: P5-OP-0…P5-OP-8 await HgX's word (flagged, not blocking).
