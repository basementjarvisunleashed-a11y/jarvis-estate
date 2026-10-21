# Phase 4 — Open Questions
## Needing HgX's word · Opened 2026-10-21

The idempotency spec cannot be written until these are answered. Each
question: context, options, a recommendation, and a blank answer line
for the walkthrough. Q1 is the Phase 2 Q6 carryover, deferred on his
word.

---

### Q1 (Phase 2 Q6 carryover) — Who signs the digest for worker-prepared intents?

- **Context:** Carried from `tests/PHASE-2-OPEN-QUESTIONS.md` Q6
  (answered 2026-10-21 ~12:47 ET: deferred to the Phase 4 idempotency
  spec). The approval-intent schema carries `intent_digest`; the digest
  is computed by whoever creates the intent and recomputed by the
  server at decision time. No source states who signs the digest if a
  worker prepares the intent. Procedural, not schema-level. The same
  custody question returns in the saga: who attests a worker-prepared
  compensation intent?
- **Why it matters:** chain-of-custody completeness for delegated
  intent preparation — the signature is who vouches for the digest,
  not who computed it.
- **Options:** (a) the orchestrator signs after recomputing and
  validating the worker-prepared digest — the worker's authorship is
  recorded in the intent's provenance fields, not in the signature;
  (b) the worker signs with a delegated capability and the
  orchestrator countersigns; (c) no separate signing — the
  server-side recompute plus the sealed log is the custody
  (procedural, as today).
- **Recommendation:** (a). One accountable signer matches the
  single-writer discipline (Phase 3 Q1: the deployment loop as
  reference, the iPhone as trusted surface — never a second
  orchestrator). The orchestrator already recomputes the digest at
  decision time; the signature is the attestation of that recompute.
  Authorship belongs in provenance (who prepared it); the signature
  says who vouches for it.
- **HgX's answer:** (a) the orchestrator signs after recomputing and validating the worker-prepared digest; authorship in provenance, signature is who vouches. Answered 2026-10-21 ~18:24 ET.

---

### Q2 — What does `revision` mean inside the idempotency key?

- **Context:** ROADMAP.md §7 defines the key as `hash(work_id,
  intent_id, intent_digest, action, target, scope, revision,
  operation_class)`. Phase 2 Q2 ruled revisions are integers; Phase 3's
  revision protocol makes them monotone and rejects stale mutations.
  The tension: a retry of the same approved intent issued after a
  revision bump would hash to a DIFFERENT key — the key would defeat
  its own purpose and permit a duplicate effect.
- **Options:** (a) revision = the revision at approval time, frozen at
  BIND — retries of the same approved intent share the key; a changed
  intent fails digest binding anyway (digest-first, per the Phase 3
  chaos fix); (b) revision = the revision at each attempt — every bump
  mints a new key, so a retry after any state change becomes a new
  execution; (c) drop `revision` from the key — the eight-field digest
  alone binds identity.
- **Recommendation:** (a). It keeps the roadmap's formula while making
  retries safe: the key identifies the approved effect, not the
  attempt. A mutated intent cannot ride an old key because digest
  binding lapses the ceremony before revision currency is even
  evaluated.
- **HgX's answer:** (a) revision = the revision at approval time, frozen at BIND — retries of the same approved intent share the key. Answered 2026-10-21 ~18:27 ET.

---

### Q3 — Does the idempotency key include `device_session_id`?

- **Context:** The key formula does not include it; the Phase 3
  revision token does (six fields: `work_id`, `revision`, `intent_id`,
  `intent_digest`, `device_session_id`, `timestamp`). The roadmap is
  explicit: duplicate taps return the existing decision and state —
  never a second execution — including taps from two devices. And
  Phase 3's OP-3 deferred the `device_session_id` lifecycle to Phase 5,
  so the key must not depend on session semantics Phase 5 will define.
- **Options:** (a) exclude — the key identifies the EFFECT, the token
  identifies the REQUEST: two devices, one intent, one key, one
  execution; (b) include — per-device execution records, with
  cross-device deduplication handled by a separate lookup.
- **Recommendation:** (a). Per-device keys would let the same intent
  execute once per device — exactly the duplicate effect this phase
  exists to prevent. The asymmetry is principled: the token says who
  asked, the key says what was done.
- **HgX's answer:** (a) exclude — the key identifies the effect, the token identifies the request. Answered 2026-10-21 ~18:29 ET.

---

### Q4 — How does `execution_unknown` become visible, and what does escalation look like?

- **Context:** ROADMAP.md §7: "do not mark completed; do not auto-retry
  if consequential; verify externally if possible; else mark
  `execution_unknown` and escalate with the next safe option." The pull
  discipline (deployment build, phase 1) says the server never pushes;
  Phase 3 says notification is a hint, not truth. The open part is the
  concrete visibility path for an ambiguous consequential execution.
- **Options:** (a) the record is the truth — surfaced on the next pull
  as `execution_unknown` with the safe options enumerated, plus an
  escalated notification to HgX (a hint pointing at the record, never
  the record itself); (b) silent until queried — the record waits for
  the next pull with no notification; (c) immediate push-style alert
  outside the pull discipline.
- **Recommendation:** (a). (c) breaks the pull discipline the
  deployment build proved; (b) leaves a consequential unknown
  invisible, violating "ambiguous consequential actions become visible
  unknown/failed." The notification carries no state — it points at the
  sealed record.
- **HgX's answer:** (a) the record is the truth — surfaced on the next pull as execution_unknown with safe options enumerated, plus an escalated notification to HgX (a hint pointing at the record, never the record itself). Answered 2026-10-21 ~18:30 ET.

---

### Q5 — Does a consequential compensation need its own approval ceremony?

- **Context:** ROADMAP.md §7: "compensation needs its own approval if
  consequential" and "no silent rollback of consequential effects."
  The six-step ceremony (PROPOSE→RENDER→APPROVE→BIND→EXECUTE→ATTEST,
  Phase 3) is the only path from intent to effect. The open part:
  whether a compensation intent rides the original approval (fast, but
  the original approval bound a different target and effect) or goes
  through a fresh ceremony.
- **Options:** (a) fresh ceremony for consequential compensation — the
  compensation is a new intent with its own digest, its own approval,
  and its own idempotency key; (b) the original approval covers
  compensation when the saga declares the action reversible at prepare
  time.
- **Recommendation:** (a). The approval bound the exact target and
  effect — a compensation has a different target and a different
  effect. (b) would let one approval authorize two consequential
  effects, breaking the binding the whole programme proved. Reversible
  preparation is still preferred (the roadmap's classification), but
  the undo of a consequential effect is itself consequential.
- **HgX's answer:** (a) fresh ceremony for consequential compensation — a new intent with its own digest, approval, and idempotency key; no silent rollback of consequential effects. Answered 2026-10-21 ~18:31 ET.

---

## Changelog
- 2026-10-21 ~18:08 ET: opened with Q1–Q5 on Phase 4 opening (HgX's
  order). Q1 is the Phase 2 Q6 carryover. Answers recorded here as
  given, one by one.

## Walkthrough complete
- 2026-10-21 ~18:31 ET: all five questions answered in the one-by-one walkthrough — Q1 orchestrator signs after recompute (worker authorship in provenance), Q2 revision frozen at approval time, Q3 key excludes device_session_id, Q4 execution_unknown surfaced on next pull + escalated notification, Q5 fresh ceremony for consequential compensation. Phase 4 work layers open on his word.
