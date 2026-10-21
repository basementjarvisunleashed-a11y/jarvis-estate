# Phase 3 — Revision Protocol

**Status:** v0.1-draft · **Date:** 2026-10-21
**Sources:** `ROADMAP.md` §6 (revision tokens, approval flow); the four
answered questions (`tests/PHASE-3-OPEN-QUESTIONS.md`); `consistency-model.md`
§5–§6 (this directory); `~/workspace/jarvis-deploy/phase1/pull.py` (reference:
request freshness, replay handling); glossary v1.0.0; Phase 2 rulings (expiry
and `artifact_revision` are integers; the approval digest binds eight fields).

> **Governance.** Draft until HgX ratifies. Normative over the reference
> implementation where they disagree.

---

## 1. Purpose

The revision token is the mechanism by which the estate refuses stale
action. Every client request that can change state carries one; the
orchestrator rejects any mutation whose token does not match the current
revision. This protocol makes "stale data cannot masquerade as current"
(Phase 3 exit criterion) a server-enforced rule rather than a client
courtesy.

## 2. Token fields

Every mutating client request carries, in order:

| Field | Type | Meaning |
|---|---|---|
| `work_id` | string | The work item the request addresses. |
| `revision` | integer | The revision of `work_id` the client last observed. Monotonic per `work_id`; minimum 0. |
| `intent_id` | string | The intent this request acts under, if any. |
| `intent_digest` | string (hex) | SHA-256 over the canonical eight-field approval payload (Phase 2 Q3 ruling: the paper text — `intent_id` and `work_id` included). |
| `device_session_id` | string | The enrolled device session presenting the request. Enrolled per the substrate's enrollment ceremony; unknown sessions are refused before any other check. |
| `timestamp` | integer | Epoch seconds at send time. Checked against the clock-skew bound (see OP-1). |

`revision` is an integer by the Phase 2 Q2 ruling (machine truth). `timestamp`
is integer epoch seconds by the Phase 2 Q1 ruling (machine truth).

## 3. Monotonicity rules

1. **R1.** The orchestrator holds, per `work_id`, the single current
   `revision`. It is the only writer of revisions.
2. **R2.** A mutation is accepted iff `request.revision == current revision`
   of `work_id` — no older, no newer, no missing.
3. **R3.** On acceptance, the orchestrator appends the transition event and
   the current revision becomes `revision + 1`. The response carries the new
   revision; the client replaces its held token.
4. **R4.** There is no "force" flag, no override path, no administrative
   bypass. A stale token is never upgraded in place — the client re-pulls
   current state and re-presents.
5. **R5.** Read requests (status, evidence, artifact download) carry the
   token's `work_id`/`revision` as a *pin* (see `consistency-model.md`
   HC-2), not as a mutation claim: the server serves the pinned revision or
   refuses, never a silently newer one.

## 4. Minting authority

Tokens are minted by the orchestrator and delivered inside pull responses.
Devices never mint, never increment, never forge. A token presented by a
device is a *claim of observation* ("I last saw revision N"), not a
credential. The substrate's rule stands as reference: ceremony keys never
leave governance; the device holds only its enrollment key.

## 5. Stale-mutation rejection

On any mutating request, the orchestrator checks in this order — fail
closed at the first failure, and every refusal is a sealed, logged event:

1. **Session:** `device_session_id` enrolled and unrevoked. Unknown →
   refuse (`unknown-session`).
2. **Freshness:** `|server_now − timestamp| ≤ Δ`. Outside → refuse
   (`stale-request`). Δ is **OP-1** (60 s ratified vs 300 s reference).
3. **Intent liveness:** if `intent_id` is present — the intent exists, is
   unexpired (`expires_at` integer epoch seconds, Phase 2 Q1), and its
   digest recomputes to `intent_digest`. Any failure → refuse
   (`intent-invalid`); a changed intent is never "updated in place" — a
   new intent is proposed.
4. **Revision currency:** `request.revision == current`. Mismatch →
   refuse (`stale-revision`). The refusal names the current revision so
   the client can re-pull — the refusal itself carries no authority.
5. **Digest binding:** for approval decisions, the digest the principal
   saw (`D_seen`, carried in the request) must equal the intent's current
   digest `D`. Mismatch → the ceremony LAPSES: no execution, attested
   lapse (per the deployment paper's §5.4 failure behaviors, referenced
   as the estate's failure semantics).

A refused mutation changes nothing. Re-presenting the same refused token
is not a retry — it is the same refusal.

## 6. Tokens in the approval flow

The approval flow (ROADMAP.md §6): client renders card from hint →
operator taps → client sends decision with `intent_id` + digest → server
validates → server records once → returns authoritative result → client
renders. The decision request is a revision-token request under §2–§5
above, with one addition: **first valid decision recorded wins**
(`conflict-resolution.md` CR-2). The second device's decision, arriving
after the record exists, is not "also an approval" — it is a read of the
existing decision, returned as such. Duplicate taps on one device return
the existing decision and state — never a second execution (Phase 4 will
formalize idempotency; this protocol guarantees the record is single).

## 7. Cross-references

- `consistency-model.md` §5 (event-sourced work state), §6 NT-5 (the tap
  is a gesture; the record is the decision).
- `conflict-resolution.md` CR-1 (server state wins), CR-2 (first valid
  decision wins), CR-8 (artifact changed after approval).
- `sequence-diagrams.md` (b) (conflicting approvals), (d) (offline tap).
- `freshness-policy.md` §3 (the freshness stamp rides alongside the
  token; the token governs action, the stamp governs rendering).

## 8. Open points

- **OP-1 — The skew bound Δ.** Phase 0 U-5/D7 (ratified): Δ = 60 s. The
  reference implementation (`phase1/pull.py`, `MAX_SKEW = 300`) refuses
  requests beyond ±300 s and its chaos tests exercise ±301 s. Both numbers
  are "the" freshness bound in their own document. **Needs HgX's word:**
  (a) keep both — 60 s for state/event freshness, 300 s for request
  freshness; or (b) unify on one. Layer 2 tests cannot be written until
  this is settled.
- **OP-3 — `device_session_id` lifecycle.** Enrollment exists in the
  reference (`phase2/enrollment.py`); revocation, re-enrollment after
  device replacement, and session expiry are not specified here.
  **Needs HgX's word** on whether this draft should specify them or
  whether they belong to Phase 5 (security).

## 9. Version history

- **v0.1-draft — 2026-10-21.** First draft: six-field token; R1–R5
  monotonicity; five-step rejection order; digest-lapse semantics. Not
  ratified.
