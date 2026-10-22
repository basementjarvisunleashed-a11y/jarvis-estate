# Phase 3 — Multi-Device Sequence Diagrams

**Status:** v0.1-draft · **Date:** 2026-10-21
**Sources:** `ROADMAP.md` §6 (approval flow); `revision-protocol.md`
(this directory); `conflict-resolution.md` (this directory);
`consistency-model.md` (this directory); `~/workspace/jarvis-deploy/phase1/loop.py`
(reference: SERVE/SENSE/QUEUE/REVIEW/MAINTAIN), `phase2/contracts.py`
(reference: surface PULLS/NEVER-PULLS).

> **Governance.** Draft until HgX ratifies. Notation: `→` is a pull or a
> request (the client always initiates); `⇐` is the sealed response.
> `ORCH` is the orchestrator (reference: the deployment loop). Revisions
> are integers; digests are the eight-field approval digest (Phase 2 Q3).

---

## (a) Approval presented on iPhone, approved on Watch

The principal reads the card on the iPhone and taps Approve on the Watch.
Both surfaces are in scope (Q2); the Watch may pull `approvals_5s`.

```
iPhone                          ORCH                          Watch
  |                               |                               |
  |-- pull(briefs, rev=r) -------->|                               |
  |<== sealed card: intent I, ----|                               |
  |    digest D, rev r, exp E     |                               |
  |                               |-- pull(approvals_5s, rev=r) -->|
  |                               |<== sealed card: same I, D, r =|
  |                               |                               |-- tap: decision(I, D_seen=D,
  |                               |                               |   rev=r, session=watch-s1)
  |                               |<-- decision ------------------|
  |                               | validate: session ok;         |
  |                               | |now-ts|<=Δ; I live;          |
  |                               | r==current; D_seen==D  ✓      |
  |                               | RECORD decision; rev -> r+1   |
  |                               |                               |-- ⇐ recorded(decision,
  |-- pull(decisions, rev=r) ---->|                                  rev=r+1)
  |<== recorded(decision, -------|                               |
  |    rev=r+1) [read of record] |                               |
```

Notes: the Watch's tap is validated against the *same* five checks as any
decision (`revision-protocol.md` §5). The iPhone's later pull is a read of
the already-recorded decision — it does not "confirm" or "second" it.
CR-1 cannot arise here because both cards rendered from revision r.

## (b) Conflicting approvals from both devices — deterministic winner

Both devices tap within the same window, under adversarial timing. The
intents differ: the Watch's card is stale (its digest no longer matches).

```
iPhone                          ORCH                          Watch
  |-- decision(I, D_seen=D1, ---->|                               |
  |    rev=r, session=iphone-s1) |                               |
  |                               | validate ✓ (all five)         |
  |                               | RECORD; rev -> r+1            |
  |<== recorded -----------------|                               |
  |                               |                               |-- decision(I, D_seen=D1,
  |                               |                               |   rev=r, session=watch-s1)
  |                               |<-- decision (stale rev) ------|
  |                               | r != current(r+1) → REFUSE    |
  |                               |   (stale-revision; names      |
  |                               |    current r+1; no state      |
  |                               |    change; sealed + logged)   |
  |                               |                               |-- ⇐ refusal(stale-revision,
  |                               |                                  current=r+1)
  |                               |                               |-- pull(approvals_5s,
  |                               |                                  rev=r+1) [re-pull]
  |                               |<------------------------------|
  |                               |                               |-- ⇐ sealed card:
  |                               |                                  recorded decision
  |                               |                                  (read, not approval)
```

Notes: this is CR-2. The loser's path is fully specified: refuse, name
the current revision, re-pull, render the recorded decision as a read.
Had the Watch's digest also mismatched (D_seen ≠ D), the refusal would be
a digest lapse with attested lapse and no execution — the stricter of the
two failures governs, and both are refused. **Layer 3 must run this
diagram under adversarial clock skew and path asymmetry** (plan
head-start note).

## (c) Stale cache on Watch rendering unknown

The Watch holds a cached "operational" render whose `fresh_until` has
passed; the pull to refresh fails (network loss).

```
Watch                           ORCH
  | cache: state=operational,        |
  | fresh_until=T < now              |
  |-- pull(state) ---- X (lost)      |
  |                                  |
  | RENDER: "unknown — last seen     |
  | operational T ago"               |
  | [never "operational"]            |
  |                                  |
  |-- pull(state) ------------------>|   (network returns)
  |<== sealed state S, rev=r', -----|
  |    observed_at, fresh_until     |
  | RENDER: S with its age           |
```

Notes: this is CR-3. The unknown render is a first-class render, not an
error screen: it shows the last-seen value *labeled as stale* alongside
its age, or nothing but "unknown" — never the expired value as current.
See `cache-policy.md` §4 and `freshness-policy.md` §4.

## (d) Offline tap on Watch → nothing recorded, ever

The Watch is offline. The principal taps Approve on a cached card.

```
Watch (offline)                 ORCH
  | tap on cached card               |
  | → record LOCAL PENDING GESTURE   |   (gesture only — not consent,
  |   (gesture log, device-local,     |    not a decision, not queued
  |    never transmitted as a        |    for execution)
  |    decision)                     |
  |                                  |
  | [reconnect]                      |
  |-- pull(approvals_5s) ----------->|
  |<== sealed current card ---------|
  | IF intent still live AND         |
  |    digest unchanged:             |
  |    present card; principal taps  |
  |    AGAIN → new decision request  |
  | ELSE: render current state;      |
  |    the pending gesture is        |
  |    DISCARDED, never sent         |
```

Notes: this is the Phase 3 exit criterion "offline taps cannot become
approvals," diagrammed. The pending gesture is not a queued approval — it
is evidence that a tap happened while offline, and it dies on reconnect.
Re-approval requires a fresh tap on a fresh card. The substrate reference
asserts the same: offline tap records nothing, ever (plan head-start
note). There is deliberately no "sync pending approvals" path; adding one
would be a change-control entry, not an interpretation.

---

## Open points

- None in the diagrams themselves. OP-1 (the skew bound Δ) governs the
  `|now − ts| ≤ Δ` check in (a) and (b); see `revision-protocol.md` §8.

## Version history

- **v0.1-draft — 2026-10-21.** First draft: four diagrams (a)–(d) with
  refusal and reconnect paths fully specified. Not ratified.
- **2026-10-21 ~17:49 ET (OP-1 RESOLVED on HgX's word):** keep both — 60 s state/event bound (Phase 0 U-5/D7 ratified), 300 s request-freshness bound (substrate reference).
