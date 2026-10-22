# Phase 5 — Device Session Lifecycle

**Status:** v0.1-draft · **Date:** 2026-10-22
**Sources:** `ROADMAP.md` §8 (spoofing row: device-bound session);
`tests/phase3/revision-protocol.md` (six-field revision token; OP-3);
`tests/PHASE-5-OPEN-QUESTIONS.md` Q1 (answered 2026-10-22 — option (a):
full lifecycle specified here); `trust-boundaries.md` (TB-1);
`capability-matrix.md` (CM-3); `attack-trees.md` (AT-1).

> **Governance.** Draft until HgX ratifies. This document answers Q1:
> the full `device_session_id` lifecycle — enrollment, revocation,
> re-enrollment after device replacement, expiry — specified here as
> the spoofing control's foundation. Normative over the reference
> where they disagree (Phase 0 governance).

---

## 1. Purpose

A session identifier with no defined end is a trust boundary with a
hole in it. The spoofing row names "device-bound session" as the
control for fake approval; this document is the control's foundation:
the states a session can be in, the transitions between them, and the
rule that revocation and expiry kill authority.

## 2. States

| State | Meaning |
|---|---|
| `unenrolled` | No session exists for this device. All requests refused. |
| `enrolling` | Enrollment ceremony in progress. No authority granted. |
| `active` | Session valid. Requests carry `device_session_id` and are checked against it. |
| `suspended` | Session frozen by operator or anomaly. Requests refused; the session record persists for re-activation. |
| `revoked` | Session dead by explicit revocation. Terminal for this session ID. |
| `expired` | Session dead by expiry. Terminal for this session ID. |

**SL-1.** These six states are exhaustive: a session is always in
exactly one of them.

## 3. Transitions

```text
unenrolled ──enroll────▶ enrolling ──complete──▶ active
                              │
                              └──fail/cancel──▶ unenrolled

active ──revoke──▶ revoked            (terminal)
active ──expire──▶ expired            (terminal)
active ──suspend──▶ suspended

suspended ──reactivate──▶ active      (operator action only)
suspended ──revoke──▶ revoked

revoked ──(no outgoing transitions)──▶ ·   terminal
expired ──(no outgoing transitions)──▶ ·   terminal
```

**SL-2.** `revoked` and `expired` are terminal: no transition leaves
them. A terminal session's ID is never reused.
**SL-3.** An `unenrolled` device's requests are refused before any
other check — unknown sessions never reach validation logic.
**SL-4.** `enrolling` grants no authority: the enrollment ceremony
cannot itself authorize consequence.
**SL-5.** Only the operator (HgX) or an explicit anomaly rule may move
a session to `suspended`; only HgX may move it back to `active`.

## 4. Enrollment

**SL-6.** Enrollment binds a device to a session ID through the
substrate's enrollment ceremony (the reference exists in the Phase 2
work; the ceremony's mechanics are implementation depth).

**SL-7.** Enrollment records, at minimum: the device identity, the
session ID, the enrollment timestamp, and the operator who authorized
it.

**SL-8.** Enrollment is itself an approval-adjacent act: it may only
be initiated by HgX (or by a device already presenting a valid session
for a second device — see §6 re-enrollment).

**SL-9.** Enrollment never confers approval authority. It confers
only the right to *present requests* that the estate will evaluate.

## 5. Expiry

**SL-10.** Every session carries an expiry: a session that cannot end
cannot be a control.

**SL-11.** Expiry is evaluated at decision time, not at render time:
a session that lapses between card render and decision kills the
pending decision.

**SL-12.** On expiry the session transitions to `expired`; any
in-flight intent that depended on that session becomes unusable
(bound by CM-3: the capability's `condition` is now false).

**SL-13.** The expiry duration is an open point (P5-OP-6): it must be
short enough that a lost device's window of authority is bounded, and
long enough that HgX is not re-enrolling daily. The value is HgX's
decision, not the model's.

## 6. Revocation

**SL-14.** Revocation is immediate and total: the moment a session is
`revoked`, every authority derived from it dies — pending approvals,
in-flight intents, revision-token validity. There is no grace period.

**SL-15.** Revocation is operator-initiated (HgX) or automatic on
defined anomaly signals (e.g. a session presenting from an impossible
location pair — the signal list is implementation depth).

**SL-16.** A revoked session's ID is tombstoned: it is never
re-issued, and its tombstone is logged as a sealed record.

## 7. Re-enrollment after device replacement

**SL-17.** Device replacement is the normal case the model must not
break: when HgX replaces a device, the old session is revoked and a
new session is enrolled — two distinct IDs, never one ID carried over.

**SL-18.** Re-enrollment after replacement follows the enrollment
ceremony (§4) with one addition: the operator must attest that the
old device is decommissioned (or declare it lost — see SL-19).

**SL-19.** Lost device: if the old device is lost rather than
replaced, revocation of its session (SL-14) happens *before*
enrollment of the new one, and the revocation is logged as a security
event. The lost device's session can never be resurrected.

**SL-20.** A replacement device inherits no approvals from its
predecessor. Pending intents bound to the old session are void; they
are re-requested, not re-issued.

## 8. How revocation and expiry kill authority

**SL-21.** Authority in this model is always conditional on
`session ∈ {active}` (CM-1's `condition` field). Revocation and
expiry change the session state; the condition fails; the authority
dies. There is no separate "kill switch" — the state *is* the switch.

**SL-22.** The kill is evaluated at every decision point: approval
validation (TB-2), execution gating, and evidence attestation all
re-check session state. A session that dies mid-flight stops the
flight.

**SL-23.** Logs record every transition with timestamp and actor; the
session log is append-only (C-22).

## 9. Numbered claims

- **SL-24.** The full lifecycle — enrollment (§4), expiry (§5),
  revocation (§6), re-enrollment after device replacement (§7) — is
  specified here, as Q1 ordered.
- **SL-25.** Revocation and expiry are terminal, immediate, and
  total: no grace period, no resurrection, no ID reuse
  (SL-2, SL-14, SL-16).
- **SL-26.** Re-enrollment after replacement is revocation-then-
  enrollment with a fresh ID — never a carryover, never an
  inheritance of approvals (SL-17…SL-20).
- **SL-27.** The session lifecycle is the foundation of the
  spoofing control (T-1): attack-tree AT-1's device-impersonation
  leaves (unknown, revoked, expired sessions) are distinct kill
  points because they are distinct states.

## 10. Open points

- **P5-OP-6 — Session expiry duration.** The model requires an
  expiry; its length is HgX's decision. **Needs HgX's word.**
- **P5-OP-7 — Second-device enrollment.** §4's SL-8 allows a device
  already holding a valid session to initiate enrollment for a
  second device; whether that delegation should require a fresh
  operator gesture each time is unspecified. **Needs HgX's word.**

## 11. Cross-references

- `trust-boundaries.md` — TB-1, whose crossing rule this document
  implements.
- `capability-matrix.md` — CM-1/CM-3, the condition semantics the
  session state feeds.
- `threat-catalogue.md` — T-1 (fake approval), whose control rests
  on this lifecycle.
- `attack-trees.md` — AT-1, the fake-approval tree.
- `control-matrix.md` — C-1…C-3, C-9, the testable controls.
- `tests/phase3/revision-protocol.md` — OP-3, now answered here.

## 12. Version history

- **v0.1-draft — 2026-10-22.** First draft: six states, full
  transition map, enrollment/expiry/revocation/re-enrollment
  specified (SL-1…SL-23); claims SL-24…SL-27; Q1 baked in;
  P5-OP-6, P5-OP-7 recorded. Not ratified.
