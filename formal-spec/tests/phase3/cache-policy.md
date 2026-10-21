# Phase 3 — Device Cache Policy

**Status:** v0.1-draft · **Date:** 2026-10-21
**Sources:** `ROADMAP.md` §6 (hybrid table); `tests/PHASE-3-OPEN-QUESTIONS.md`
(Q2: iPhone + Watch in scope; rest pull-only); `consistency-model.md` §3.1
(this directory); `freshness-policy.md` (this directory — stamp semantics);
`~/workspace/jarvis-deploy/phase2/contracts.py` (reference: per-surface
PULLS / NEVER-PULLS); `conflict-resolution.md` CR-3 (this directory).

> **Governance.** Draft until HgX ratifies. TTL values in §3 are draft
> proposals (see OP-5) — the *rules* are the policy; the *numbers* await
> his word.

---

## 1. What a cache is, and is not

A device cache is a **render accelerator**: a copy of a sealed pull
response held to render quickly between pulls. It is never a source of
truth, never writable by the device, and never consulted for decisions.
Every cached entry carries the response's seal, its revision pin, and its
freshness stamp (`freshness-policy.md` §2). An entry without all three is
not cached — it is discarded.

## 2. What each in-scope surface may cache

### 2.1 iPhone

May cache: briefs, decisions, blocks, packets (its substrate PULLS list),
and the approval cards it presents. May cache the current revision pin
per `work_id` for re-pull efficiency.

May NOT cache: anything on its NEVER list (`engine_internals`,
`other_roles_private_state`) — such payloads are refused at the pull and
must never be retained from any other channel. May not cache evidence
bodies beyond the review session: an evidence packet pulled for review is
held for the session, then dropped (revision-stable reads pin the
revision; the bytes are re-pulled, never stored durably on-device).

### 2.2 Watch

May cache: the current approval card (`approvals_5s`) and critical
alerts — and only the *current* one of each. The Watch holds at most one
card generation: a newer pull evicts the older card unconditionally.

May NOT cache: evidence bodies, configuration (its NEVER list), artifact
bytes, or any decision record beyond the sealed receipt of its own last
decision (kept until the next pull confirms the record, then droppable).

### 2.3 The rule both obey

**A cached entry is renderable only while fresh** (`now ≤ fresh_until`).
The moment it expires, it is not "probably still fine" — it is unknown
(CR-3, `sequence-diagrams.md` (c)).

## 3. TTLs and invalidation (draft proposals — OP-5)

| Entry | iPhone TTL | Watch TTL | Invalidation trigger |
|---|---|---|---|
| Status render | 60 s | 30 s | Any pull returning a newer revision; any sealed denial |
| Approval card | until `expires_at` or superseded | until `expires_at` or superseded | New revision of the intent; expiry; decision recorded |
| Evidence packet (review session) | session only | n/a (never pulled) | Session end; newer `artifact_revision` sealed |
| Decision receipt | until confirmed by next pull | until confirmed by next pull | Record confirmed |

TTL expiry and invalidation are *disjunctive*: whichever comes first
kills the entry. A new revision arriving by pull invalidates immediately —
the device never waits out a TTL against a known-newer revision.

## 4. The unknown render

When no fresh entry exists and no pull succeeds, the surface renders
**unknown** — with the age of the last good pull ("last seen operational
T ago") where that age is itself honest. The unknown render:

1. never presents an expired value as current;
2. never offers an approval action on an unknown card (the tap target is
   disabled — an offline tap is a pending gesture, `sequence-diagrams.md`
   (d), never consent);
3. is logged device-locally as a coverage gap (for the MAINTAIN loop's
   health accounting), not as an error the principal must clear.

## 5. Pull-only surfaces (iPad, TV, Vision Pro)

Per Q2, these surfaces are outside the consistency model. Their caching
is bounded exactly by their pull contracts: they may hold a pulled
response for the duration of its own contract-defined use (tablet: the
evidence review; TV: the ambient state wall; headset: the private
session) and no longer. They hold no revision pins, no decision receipts,
no cross-pull state. When the contract's use ends, the bytes are dropped.

## 6. Cross-references

- `freshness-policy.md` §2 (stamp fields), §4 (stale-rendering rules).
- `revision-protocol.md` §3 R5 (reads pin revisions; the pin is what the
  cache keys on).
- `conflict-resolution.md` CR-3, CR-6 (hint content is never cached as
  state).
- `consistency-model.md` §6 NT-2 (every render carries provenance — the
  cache is what supplies it between pulls).

## 7. Open points

- **OP-5 — TTL numbers.** The §3 table's seconds are proposals calibrated
  to the substrate's cadences (Watch 5-second approval budget; phone
  3/day system-initiated attention budget in the reference). **Needs
  HgX's word:** accept the numbers, or set his own. The rules (§1, §2,
  §4) stand regardless.

## 8. Version history

- **v0.1-draft — 2026-10-21.** First draft: per-surface cache rules,
  unknown-render specification, pull-only bounds, draft TTL table. Not
  ratified.
