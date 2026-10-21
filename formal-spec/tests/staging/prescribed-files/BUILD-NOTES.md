# BUILD-NOTES — seven prescribed files (DRAFT 0.1)

**Built 2026-10-21 ~00:02–00:20 ET on HgX's order.** Staged under `tests/staging/prescribed-files/`; all born as **v0.1-draft** per VERSIONING.md (new artifacts are drafts; ratification is HgX's call). Canonical promotion: on his word, copy to `spec/` and `contracts/` as v0.1, then ratify to v1.0.0. Proposed promotion path per file is given below. **Nothing below was silently resolved** — interpretations are marked INTERPRETATION and the open questions need HgX's word.

## 1. `state-machine.md`
Markdown mirror of `spec/state-machine.tla`: the 12 states, all 21 transitions T1–T21 with prose guards, formal guard references, effects, and firing events; idempotency machinery (tap vs recorded, duplicate-tap stutter, server validation); expiry semantics; chain of custody; clock-skew bound Δ=60s; forbidden transitions F1–F9; and the explicit PO-12 liveness exclusion. Every row was checked against both the TLA+ actions and `contracts/events.md` §§4–5 — **no machine line could not be squared**: the two documents agree exactly, including the provisional D5/D6/D7 adoption notes and the U1/U2/U4 opens. Promotion: copy to `spec/state-machine.md` as v0.1 on his word; the glossary's ratification checklist (D2) already names this path as its owner.

## 2. `approval-digest.md`
Implements glossary U-1 (RESOLVED 2026-10-19): SHA-256 over canonical JSON. Canonical JSON fixed as sorted keys / no whitespace (`(',', ':')` separators) / UTF-8 — this is the parent task's definition, grounded in the U-1 wording. Includes a real worked example: 249-byte canonical payload → digest `a5ba4f85e85058c009047fd497df0bfa97122822f5286551adba15fa18f63179` (computed with `hashlib`, byte-reproducible). Documents `tap_digest` semantics matching the TLA+ (`OperatorTapsApprove`, `ServerRecordsApproval`, `MutateIntent`, PO-3). Promotion: copy to `spec/approval-digest.md` as v0.1.

## 3. `approval-intent.schema.json`
Field list from Paper IV §6.6 + `contracts/events.md` event 16: `intent_id, work_id, action, target, effect, scope, revision, expiry, risk_class, intent_digest` (64-hex pattern). Promotion: copy to `contracts/approval-intent.schema.json` as v0.1.

## 4. `decision-packet.schema.json`
Field list from Paper IV §6.6: `intent_id, intent_digest, decision, device_session_id, timestamp, auth_method, server_recorded_at`. Includes the Paper III decision-packet invariant as a documented (not machine-checkable) `claimed_outcome` field, since JSON Schema cannot cross-reference the evidence packet. Promotion: copy to `contracts/decision-packet.schema.json` as v0.1.

## 5. `evidence-packet.schema.json`
Field list from Paper IV §6.6 + `contracts/events.md` event 6: `packet_id, work_id, revision, artifact_refs, source_observations (observed_at/fresh_until), test_results, approval_refs, gaps (required), created_at`, checksum. Promotion: copy to `contracts/evidence-packet.schema.json` as v0.1.

## 6. `artifact-manifest.schema.json`
Field list from Paper IV §6.6: `artifact_id, work_id, revision, digest, media_type, location, provenance`. Promotion: copy to `contracts/artifact-manifest.schema.json` as v0.1.

## 7. `watchtower.schema.json`
Merged from Paper IV §6.6 text (`service_id, state, last_observed_at/observed_at, fresh_until, confidence, evidence_ref`) and Appendix C.3's report-level sketch (`report_id, observed_at, services[]`). Closed state enum `operational|paused|degraded|unknown`. Promotion: copy to `contracts/watchtower.schema.json` as v0.1.

---

## Open questions for HgX (interpretations that need his word)

**OQ-1 — expiry type: integer or ISO-8601 string.** Paper IV Appendix C.2 names the field `expires_at` as a date-time string; the TLA+ model uses integer `expiry` (server epoch seconds, guards compare `now < intent.expiry`); Paper IV §6.6 text says `expiry`. Draft chose **integer epoch seconds** (the machine's guards are the checkable truth) and documented the discrepancy in the schema's field description. Exact source lines: whitepaper §App-C.2 (`"expires_at": {"type": "string", "format": "date-time"}`), `spec/state-machine.tla` (`expiry : Nat`, guards at `ApprovalRequested`/`can_enter_executing`/`ApprovalExpired`).

**OQ-2 — revision type: integer or string.** Appendix C.2 says `revision: string`; the TLA+ says `revision : Nat`; the glossary defines revision as a "monotonically increasing counter". Draft chose **integer**. Exact lines: whitepaper §App-C.2 (`"revision": {"type": "string"}`), `spec/state-machine.tla` (`revision : Nat`).

**OQ-3 — digest record: six fields or eight.** The TLA+ finite-instance concretization binds `(action, target, effect, scope, revision, expiry)` — six fields. Paper IV §6.6 says the digest is "over the canonical serialisation of the rest" of the intent record, which per §6.6 includes `intent_id` and `work_id`. Draft binds **all eight non-digest fields** (`approval-digest.md` §1). The eight-field digest of the worked example above reproduces; a six-field variant would differ. Exact lines: `spec/state-machine.tla` (`DigestOf(r) == <<r.action, r.target, r.effect, r.scope, r.revision, r.expiry>>`), whitepaper §6.6 ("`intent_digest` over the canonical serialisation of the rest").

**OQ-4 — canonical-JSON details beyond the three rules.** The papers specify only "canonical JSON serialisation". Draft fixed: code-point key order, exact `(',', ':')` separators, UTF-8 via `ensure_ascii=False`. Number encoding (int vs float), Unicode normalisation, and duplicate-key handling are unspecified — the reference procedure in `approval-digest.md` makes the choice concrete and byte-reproducible. Exact line: glossary §3 U-1 ("SHA-256 over the canonical JSON serialisation of the approval intent").

**OQ-5 — evidence-packet sketch vs §6.6 text.** Appendix C.1 names `artifact_revision` (string), `approval_ref`, and `checks`; §6.6 + `contracts/events.md` event 6 name `artifact_refs`, `source_observations`, `test_results`, `approval_refs`, `gaps`, `created_at`, `revision` (integer). Draft followed §6.6/events.md (the later, normative-facing sources). Exact lines: whitepaper §App-C.1 sketch; whitepaper §6.6 overview; `contracts/events.md` §5 event 6.

**RESOLVED 2026-10-21 ~12:46 ET — HgX chose the C.1 sketch names.** Rework done same day: `contracts/evidence-packet.schema.json` now carries exactly the sketch's fields — packet_id, work_id, artifact_revision (string), created_at, approval_ref (optional), checks (array of name/result[pass|fail]/observed_at/detail), gaps (optional) — required list `["packet_id", "work_id", "artifact_revision", "created_at", "checks"]`. Fixture and SCH-EP tests reworked (6 tests: SCH-EP-01–06, all passing; Layer 1 total now 25 schema tests). **DIVERGENCES RECORDED, NOT SILENTLY FIXED:** (a) ratified `contracts/events.md` event 6 still uses the §6.6 names — a contract amendment needs HgX's word; (b) the sketch types `artifact_revision` as string while Q2 decided revision tokens are integer — the packet guard compares on the coerced string, and the type-coherence question is open; (c) the sketch carries no artifact digests, `source_observations`, or packet checksum — the digest cross-check of the earlier draft is gone, so INV-E2's schema backing is name+revision-string only (weaker than before); (d) `gaps` is sketch-optional but INV-E4 enforcement moved to the packet guard (missing gaps refused at guard level). See `tests/evidence/2026-10-21-ep-rework.md`.

**OQ-6 — where the digest is computed (clarity, not conflict).** The approval-intent schema carries `intent_digest`; the digest is computed by whoever creates the intent, and recomputed by the server at decision time. No source states who signs the digest if a worker prepares the intent — procedural, not schema-level. Flagged for the Phase 4 idempotency spec.

## Non-questions (checked, clean)

- `spec/StateMachine.tla` / `StateMachine.cfg` are symlinks to the lowercase files — one machine, no conflict.
- `state-machine.cfg` instantiates `Delta = 60` — matches ratified D7.
- No machine line in `state-machine.md` required invention: every guard/effect traces to a named TLA+ action.
