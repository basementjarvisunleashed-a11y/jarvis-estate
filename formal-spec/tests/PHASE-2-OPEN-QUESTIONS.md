# Phase 2 — Open Questions and Remaining Items

**Purpose:** every Phase 2 question and remaining item that needs HgX's word, documented one by one with context, source lines, options, and his answers. Indexable for GitHub; the memory source for weekly/monthly summaries.
**Status:** Phase 2 OPEN. Created 2026-10-21 on HgX's order ("walk me through everything one by one").
**Companion records:** `tests/PHASE-2-HISTORY.md` (what was done), `tests/PHASE-2-PLAN.md` (the plan), `tests/staging/prescribed-files/BUILD-NOTES.md` (build interpretations).

---

## Decisions for HgX (answer one by one)

### Q1 — OQ-1: expiry type — integer epoch seconds or ISO-8601 string?
- **Context:** the approval intent carries an expiry. Paper IV Appendix C.2 names `expires_at` as a date-time string; the TLA+ machine uses integer `expiry` (server epoch seconds; guards compare `now < intent.expiry`); Paper IV §6.6 text says `expiry`. The v0.1 draft chose integer epoch seconds (the machine's guards are the checkable truth) and documented the discrepancy in the schema's field description.
- **Source lines:** whitepaper §App-C.2 (`"expires_at": {"type": "string", "format": "date-time"}`); `spec/state-machine.tla` (`expiry : Nat`, guards at `ApprovalRequested`/`can_enter_executing`/`ApprovalExpired`).
- **Why it matters:** Phase 3's revision protocol and freshness policy cannot be written until the type is fixed; the Layer 1 expiry tests (3,000 samples) assert integer semantics.
- **Options:** (a) integer epoch seconds — the machine is truth; (b) ISO-8601 string — the paper text is truth (requires a machine/spec change).
- **HgX's answer:** (a) integer epoch seconds — the machine is truth. Answered 2026-10-21 ~12:40 ET. The v0.1 draft choice stands confirmed; paper erratum recorded (App-C.2 `expires_at` string).

### Q2 — OQ-2: revision type — integer or string?
- **Context:** Appendix C.2 says `revision: string`; the TLA+ says `revision : Nat`; the glossary defines revision as a "monotonically increasing counter". The v0.1 draft chose integer.
- **Source lines:** whitepaper §App-C.2 (`"revision": {"type": "string"}`); `spec/state-machine.tla` (`revision : Nat`).
- **Why it matters:** same as Q1 — Phase 3's revision protocol gates on this.
- **Options:** (a) integer — machine and glossary agree; (b) string — paper text (requires machine/spec change).
- **HgX's answer:** (a) integer — machine and glossary agree. Answered 2026-10-21 ~12:41 ET. The v0.1 draft choice stands confirmed; paper erratum recorded (App-C.2 `revision` string).
- **Context:** the TLA+ finite-instance concretization binds `(action, target, effect, scope, revision, expiry)` — six fields. Paper IV §6.6 says the digest is "over the canonical serialisation of the rest" of the intent record, which per §6.6 includes `intent_id` and `work_id`. The v0.1 draft binds all eight non-digest fields; the worked example in `spec/approval-digest.md` (249-byte payload → `a5ba4f85…f63179`) reproduces the eight-field digest. A six-field variant would differ.
- **Source lines:** `spec/state-machine.tla` (`DigestOf(r) == <<r.action, r.target, r.effect, r.scope, r.revision, r.expiry>>`); whitepaper §6.6 ("`intent_digest` over the canonical serialisation of the rest").
- **Why it matters:** the approval-digest spec cannot be ratified to v1.0.0 until the binding is fixed; Layer 1 digest-mismatch tests assume the eight-field form.
- **Options:** (a) eight fields — intent_id and work_id included (paper text); (b) six fields — the machine's concretization.
- **HgX's answer:** (a) eight fields — intent_id and work_id included (paper text). Answered 2026-10-21 ~12:43 ET. The v0.1 draft choice stands confirmed; machine concretization noted as the narrower variant (would produce different digests — not adopted).
- **Context:** the papers specify only "canonical JSON serialisation". The draft fixed code-point key order, exact `(',', ':')` separators, UTF-8 via `ensure_ascii=False`. Number encoding (int vs float), Unicode normalisation, and duplicate-key handling are unspecified; the reference procedure in `spec/approval-digest.md` makes the choice concrete and byte-reproducible.
- **Source lines:** glossary §3 U-1 ("SHA-256 over the canonical JSON serialisation of the approval intent").
- **Why it matters:** two implementations must produce identical digests; without pinning the details, they may not.
- **Options:** (a) accept the draft's concrete procedure as the definition; (b) specify different details (say which).
- **HgX's answer:** (a) accept the draft's concrete procedure as the definition. Answered 2026-10-21 ~12:44 ET. `spec/approval-digest.md`'s reference procedure is now the canonical-JSON definition.
- **Context:** Appendix C.1's sketch names `artifact_revision` (string), `approval_ref`, `checks`; §6.6 + `contracts/events.md` event 6 name `artifact_refs`, `source_observations`, `test_results`, `approval_refs`, `gaps`, `created_at`, `revision` (integer). The draft followed §6.6/events.md (the later, normative-facing sources).
- **Source lines:** whitepaper §App-C.1 sketch; whitepaper §6.6 overview; `contracts/events.md` §5 event 6.
- **Why it matters:** the evidence-packet schema's field names must match what Phase 3's consistency model reads.
- **Options:** (a) §6.6/events.md names (draft choice); (b) C.1 sketch names (requires schema change).
- **HgX's answer:** (b) C.1 sketch names — `artifact_revision` (string), `approval_ref`, `checks`. Answered 2026-10-21 ~12:46 ET. AMENDMENT APPLIED 2026-10-21 ~14:43 ET: `contracts/events.md` v1.0.0 → v1.1 (event 6 packet fields now the sketch names; version history appended). The schema↔vocabulary contradiction is CLOSED. Remaining open: INV-E2 backing now name+revision-string only.
- **Type-coherence decision (2026-10-21 ~14:45 ET, HgX's word, matching Jarvis's preference):** `artifact_revision` is INTEGER — changed the field, diverging from the C.1 sketch's string typing, per his Q2 (all revision tokens are integers). Applied to `contracts/evidence-packet.schema.json` (integer, minimum 0), the valid fixture (integer 3), and the packet guard (integer comparison). All 83 Layer 1 tests pass. Recorded as a divergence from Paper IV App. C.1 in the events.md v1.1a version history. **REWORK DONE 2026-10-21 ~12:50 ET:** schema, fixture, guard, and tests reworked (SCH-EP-01–06, 25/25 schema tests pass). Sketch HAS a `gaps` field (sketch-optional) — INV-E4 enforcement moved to the packet guard, invariant holds. Divergence with events.md and the revision-type tension (sketch string vs Q2 integer) flagged in `tests/evidence/2026-10-21-ep-rework.md`; matrix updated.
- **Context:** the approval-intent schema carries `intent_digest`; the digest is computed by whoever creates the intent and recomputed by the server at decision time. No source states who signs the digest if a worker prepares the intent. Procedural, not schema-level — flagged for the Phase 4 idempotency spec.
- **Why it matters:** chain-of-custody completeness for delegated intent preparation.
- **Options:** (a) defer to the Phase 4 idempotency spec (recommended); (b) decide now (say how).
- **HgX's answer:** (a) defer to the Phase 4 idempotency spec. Answered 2026-10-21 ~12:47 ET. Recorded as a Phase 4 work item.
- **Context:** five contract schemas and two spec documents sit in canonical placement as v0.1 drafts (promoted 2026-10-21 on his "push all of it" order). They become normative only on his ratification. Q1–Q5 answers should land first — ratification of a draft built on undecided types would be premature.
- **HgX's answer:** hold all ratification. Answered 2026-10-21 ~12:48 ET. All seven remain v0.1 drafts; the rework's new tensions (Q2-vs-sketch type coherence, weaker INV-E2, events.md divergence) stay open with the drafts.
- **REVISITED 2026-10-21 ~14:49 ET — RATIFIED to v1.0.0 on his word:** all seven drafts are now normative (spec/state-machine.md, spec/approval-digest.md, the five schemas — each carries `"version": "1.0.0"` / a v1.0.0 header and a ratification history entry). The tensions that held ratification are closed: events.md v1.1 amendment (Q5) and the integer type-coherence decision. Layer 1: 83/83 green.
- **Context:** the evidence is in (62 Layer 1, 10 property, 10 chaos, 11/12 crosscheck, 37/58 roadmap test, 18/18 + 12/12 backtrace, six closed milestone issues). The standing rule: no phase closes without his word. Remaining by design: INV-R2/R3/R4 (router — Phase 6 dependency), CH-5/CH-6 full form (Paper III client/router artifacts), INV-E3/S3/S5 rendering side, OQ-1..OQ-6, CI/third-party runnability (Paper IV §8.4), roadmap-test paperwork remedies (paper errata recorded, not edited, per U-6).
- **HgX's answer:** keep Phase 2 open. Answered 2026-10-21 ~12:49 ET. Bookkeeping continues at his pace; Phase 3 not opened.
- **Context:** `tests/audit_crosscheck.py`'s `tests-md-phase1-citations` check requires every "N distinct states" figure in tests/*.md to equal the Phase 1 report's 3,266,929 — it cannot distinguish other runs' properly log-attributed figures (exhaustive 4,854,966; retest 12,524,558). The failure is the check's, not the figures'. A working artifact, not ratified — improvement proposal staged in `tests/staging/CHANGELOG-ENTRIES.md`.
- **HgX's answer:** apply the improvement. Answered 2026-10-21 ~12:50 ET. Applied the same session — the check now accepts run-attributed citations.

---

## Remaining work items (not decisions)

| Item | State | Owner/dependency |
|---|---|---|
| INV-R2/R3/R4 coverage | Uncovered by design | Router is estate runtime; Phase 6 artifact `spec/router-policy.md` |
| CH-5/CH-6 full form | Contract level only | Paper III client/router artifacts |
| INV-E3/S3/S5 rendering side | E3 schema-backed, S3 schema-level, S5 uncovered | Rendering artifacts |
| CI wiring + third-party runnability | Not started | Paper IV §8.4 phase-level gates |
| Roadmap-test paper errata | Recorded, not edited | U-6: papers stand as historical |

## Changelog

- 2026-10-21: created on HgX's order; Q1–Q9 pending.
- 2026-10-21 ~12:50 ET: all nine questions answered in the one-by-one walkthrough — Q1 expiry=integer epoch seconds, Q2 revision=integer, Q3 digest=eight fields, Q4 draft canonical-JSON procedure accepted, Q5 evidence-packet=C.1 sketch names (schema rewritten, 25/25 schema tests; divergences recorded: events.md event 6 amendment pending, Q2-vs-sketch type coherence open, INV-E2 backing weaker), Q6 digest-signer deferred to Phase 4, Q7 all ratification held, Q8 Phase 2 stays open, Q9 crosscheck improvement applied (run-attributed citations accepted; "0" accepted alongside "zero"; version-number false positives excluded — 12/12 checks pass, log evidence/2026-10-21-crosscheck-v2.log).
