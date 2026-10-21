# Phase 3 — Freshness Policy

**Status:** v0.1-draft · **Date:** 2026-10-21
**Sources:** `ROADMAP.md` §6 ("eventual consistency with freshness
stamps"; `fresh_until` on work items); `consistency-model.md` §2–§3 (this
directory); `cache-policy.md` §3–§4 (this directory);
`~/workspace/jarvis-deploy/phase1/pull.py` (reference: `MAX_SKEW = 300`,
freshness-before-crypto-before-work); Phase 2 rulings (integer epoch
timestamps).

> **Governance.** Draft until HgX ratifies. This policy governs
> *rendering* (what the principal sees); `revision-protocol.md` governs
> *action* (what the estate does). The two are never confused.

---

## 1. Purpose

Freshness stamps are how "eventually consistent" stays honest. Every
status payload carries its age; every render shows its age or shows
unknown. The policy defines the stamp, the honesty rule, the staleness
thresholds, and the p99 expectations the stamps are judged against.

## 2. The stamp

Every status-bearing pull response carries:

| Field | Type | Meaning |
|---|---|---|
| `observed_at` | integer (epoch s) | When the orchestrator last verified this value against its source. |
| `fresh_until` | integer (epoch s) | Until when the orchestrator warrants this value as current. Past this, the value is history, not status. |
| `revision` | integer | The work-item revision this value was read at (the pin). |

`age = now − observed_at`, computed on the rendering surface at render
time. The surface never trusts a server-computed "age" — it computes from
the stamp and its own clock, and a stamp older than the skew bound (OP-1)
invalidates the response rather than producing a negative age.

## 3. Age honesty

1. **F1.** Data renders with its age, or as unknown — never stale as
   current. (The substrate's wire invariant P4: "Age honesty.")
2. **F2.** `fresh_until` is set by the orchestrator per payload class
   (§5 table); the surface does not extend it.
3. **F3.** A response arriving with `observed_at` in the future beyond
   the skew bound is refused as malformed — clocks lie, stamps don't get
   to.
4. **F4.** The unknown render (`cache-policy.md` §4) shows the last
   honest age; it never interpolates, never smooths, never guesses.

## 4. Staleness thresholds — when data becomes unknown

| Payload class | `fresh_until` horizon (draft) | Past horizon |
|---|---|---|
| Approval card | `expires_at` of the intent (binding) | Card disabled; re-pull required |
| Status flag (Watch) | 30 s past `observed_at` | Render unknown |
| Status flag (iPhone) | 60 s past `observed_at` | Render unknown |
| Decision record | indefinite (immutable once sealed) | n/a — sealed records don't stale; they supersede |
| Evidence pin | indefinite per revision | n/a — revisions are immutable (CR-7) |

Horizons are draft numbers (see OP-5 in `cache-policy.md`); the *rule*
— past horizon renders unknown — is the policy and is not negotiable.

## 5. p99 expectations by cadence class

Freshness is judged against the surface's contracted cadence, not against
an absolute latency. Expectations (reference: the substrate's pull
discipline; formal tier cadences are **OP-7**):

| Cadence class | Reference behavior | p99 expectation (draft) |
|---|---|---|
| Watch approval path | 5-second card budget (substrate) | card presented ≤ 5 s after pull; stamp age ≤ 5 s at render |
| iPhone status | contracted pull cadence | stamp age ≤ one cadence interval + skew bound at render |
| Pull-only surfaces | per-contract use | stamp age ≤ the contract's defined window |

A p99 miss is a health event for the MAINTAIN loop, not a consistency
violation — the stamp keeps the render honest even when the pipeline is
slow. Speed is a service target; honesty is the invariant.

## 6. The skew bound's role

The stamp arithmetic assumes `|surface_clock − server_clock| ≤ Δ`
(OP-1: 60 s ratified vs 300 s reference). If the bound is violated, ages
are meaningless — so the bound is enforced at the pull (reference:
`stale-request` denial, freshness checked *before* crypto before work),
not papered over at the render. A device whose clock is untrusted gets no
stamps it can compute with; it gets denials until its clock is sane.

## 7. Cross-references

- `consistency-model.md` §3 HC-1 (the guarantee this policy implements),
  §6 NT-2 (renders carry provenance — the stamp is the provenance).
- `cache-policy.md` §3 (TTLs key off `fresh_until`), §4 (unknown render).
- `revision-protocol.md` §5 step 2 (the freshness check on mutating
  requests — the action-side twin of this policy).
- `sequence-diagrams.md` (c) (the stale-cache diagram, annotated with
  stamp fields).

## 8. Open points

- **OP-1** (shared with `revision-protocol.md`): the skew bound Δ — 60 s
  ratified vs 300 s reference. Settles both the request-freshness check
  and the stamp arithmetic. **Needs HgX's word.**
- **OP-7 — Formal cadence/tier table.** The four sources name no priced
  tier cadences; §5's expectations are anchored to the substrate's
  observed budgets. If HgX wants contracted p99 tiers in this policy,
  that is a new decision, not an interpretation. **Needs HgX's word:**
  specify tiers here, or leave expectations as reference-anchored
  drafts.

## 9. Version history

- **v0.1-draft — 2026-10-21.** First draft: stamp fields, age-honesty
  rules F1–F4, staleness table, cadence-class p99 expectations. Not
  ratified.
