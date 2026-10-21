# Contract Governance — J.A.R.V.I.S. Phase 0

*The canonical specification repository: what each contract file is, who owns it, how it versions,
and how it changes. Companion to `contracts/events.md` (the canonical event vocabulary, v1.0.0).*

## (a) Contract files and owners

Owner = the role accountable for changes to that file. "Ratify" means no normative change takes
effect without HgX's approval (decision D2: the coordinator resolves vocabulary conflicts; HgX
ratifies the final glossary).

### Phase 0 normative core (owner: Phase 0 coordinator — Jarvis as chief-of-staff; HgX ratifies)

| File | What it is | Owner |
|---|---|---|
| `spec/state-machine.md` | The canonical work-state machine: the twelve states (`received`, `accepted`, `in_progress`, `awaiting_approval`, `executing`, `verifying`, `completed`, `blocked`, `failed`, `paused`, `unknown`, `cancelled`), the transition table T1–T21 with guards, and the forbidden transitions F1–F9. Per Paper IV §6.1–§6.3. **Implemented as `spec/state-machine.tla` (TLA+, ratified proof language).** | Phase 0 coordinator; HgX ratifies |
| `contracts/events.md` | The canonical event vocabulary: 19 events (this directory), naming convention (snake_case), envelope, structural rules, conflicts and resolutions. Per Paper IV §6.4 and Roadmap §0.3. | Phase 0 coordinator; HgX ratifies |
| `contracts/glossary.md` | The canonical glossary: 69 normative term definitions, 25 vocabulary conflicts with resolutions, 3 open questions (U-2, U-3, U-4); 3 resolved at ratification (U-1, U-5, U-6). The single vocabulary the model checker, test suite, and doctoral committee refer to. | Phase 0 coordinator; **HgX ratifies (v1.0.0 gate)** |
| `spec/approval-digest.md` | The approval-intent digest rule: exact field construction, hash, and canonicalisation, stated precisely enough that two independent implementations produce the same digest for the same intent (Paper IV §14, Month 1 deliverable). | Phase 0 coordinator; HgX ratifies |
| `contracts/watchtower.schema.json` | Service-state rendering contract: `service_id`, closed `state` enum (`operational`, `paused`, `degraded`, `unknown` — paused explicitly distinct from failed), `last_observed_at`, `fresh_until`, `confidence`, `evidence_ref`. Paper III (Contracts/I); Paper IV §6.6. | Phase 0 coordinator; HgX ratifies |
| `contracts/evidence-packet.schema.json` | Proof-bundle schema: `packet_id`, `work_id`, `revision`, `artifact_refs`, `source_observations`, `test_results`, `approval_refs`, required `gaps` (omission is a schema violation — INV-E4), `created_at`, packet checksum. Paper IV §6.6. | Phase 0 coordinator; HgX ratifies |
| `contracts/approval-intent.schema.json` | Exact intent schema: `intent_id`, `work_id`, `action`, `target`, `effect`, `scope`, `revision`, `expiry`, `risk_class`, `intent_digest` over the canonical serialisation. Paper II (approval object); Paper III (approval intent); Paper IV §6.6. | Phase 0 coordinator; HgX ratifies |
| `contracts/decision-packet.schema.json` | Recorded decision schema: `intent_id`, `intent_digest` (as presented), `decision` (granted/denied), `device_session_id`, `timestamp`, `auth_method`, `server_recorded_at` — together the definition of "authoritative" (INV-A5). Duplicate-tap path returns this packet instead of creating a second one (INV-A6). Paper IV §6.6; RD-4. | Phase 0 coordinator; HgX ratifies |
| `contracts/artifact-manifest.schema.json` | Digest manifest: `artifact_id`, `work_id`, `revision`, `digest`, `media_type`, `location`, `provenance` (which worker, which sources, which brief revision). Binds INV-E2 to bytes. Paper IV §6.6. | Phase 0 coordinator; HgX ratifies |

### Later-phase specifications (drafts begun in Phase 0 Month 1; ownership transfers to the phase owner on Phase 0 exit)

| File | What it is | Owner |
|---|---|---|
| `spec/invariants.md` | The invariant catalogue: INV-C1…C5, INV-A1…A7, INV-E1…E5, INV-S1…S5, INV-R1…R5 — one owner per invariant (Paper IV §8). | Research Bot / doctoral programme (Phase 2); drafts in Month 1 |
| `spec/consistency.md` | Multi-device consistency contract: hybrid guarantee matrix, single authoritative writer, revision tokens, conflict resolution table, freshness policy (Paper IV §9; Roadmap §6). | Research Bot / doctoral programme (Phase 3); matrix drafted in Month 1 |
| `spec/idempotency.md` | Transaction and retry semantics: idempotency-key schema, execution-record lifecycle, governed saga, retry/compensate policy (Paper IV §10; Roadmap §7). | Research Bot / doctoral programme (Phase 4); key schema drafted in Month 1 |
| `spec/security-threat-model.md` | Assets, trust boundaries, threats, capability matrix, isolation roadmap (Paper IV §11; Roadmap §11). | Research Bot / doctoral programme (Phase 5); skeleton in Month 1 |
| `spec/router-policy.md` | Router policies, metrics (accepted work, repair cost, attention cost), experiment protocol (Paper IV §12; Roadmap §12). | Research Bot / doctoral programme (Phase 6) |

### Supporting trees (not normative contracts; versioned alongside)

`tests/` (Layer 1 contract tests, Layer 2 property tests, Layer 3 chaos tests — Paper IV §8),
`proofs/` (TLA+ model, guard table, checker results — Paper IV §7), `experiments/` (Phase 6 logs and
reports). Owned by the phase that produces them.

## (b) Versioning scheme — SemVer

The versioning law — why versions matter and how they move — is stated in
`VERSIONING.md` at the repository root. This section is its application to
the contracts.

- **Baseline:** every Phase 0 contract file starts at **v0.1.0** on first freeze commit.
- **Pre-1.0 (0.x.y):** PATCH bumps = clarifications, examples, typo fixes — no normative semantic
  change. MINOR bumps (`0.x`) = additive normative changes (new event, new optional field, new guard)
  — backwards compatible. Renames and removals stay in 0.x but require ratification and a migration
  note; repeated breaking change is recorded as a minor bump with the old term retired in the glossary.
- **v1.0.0:** only when **HgX ratifies the glossary** AND the Phase 0 exit criteria are green (Paper IV
  §6.7: one normative spec; one owner per concept; no duplicate definitions; versioned and reviewable;
  RD-1…RD-6 adopted; contract sketches complete). The paper's version history records the freeze.
- **Post-1.0.0:** standard SemVer — MAJOR = breaking normative change (renamed event, removed
  transition, changed guard); every MAJOR bump requires HgX ratification.
- Versions are recorded in-repo (file frontmatter or `CHANGELOG.md`); "the repository is under version
  control; changes to normative files carry rationales" (Paper IV §6.7).

## (c) Change process — propose → evidence → ratify

1. **Propose.** The file's owner drafts a change request: the file, the proposed version bump, the
   normative diff, the rationale, every affected transition/invariant/event/glossary term, and a
   migration note if anything is renamed or removed. No silent edits to normative text.
2. **Evidence.** The proposer demonstrates the change preserves the programme's guarantees — per the
   doctrine, no proof, no done: (i) no duplicate definitions — checked where mechanically possible by
   CI over the glossary and schema files (Paper IV §6.7); (ii) invariants preserved — property tests
   and/or the TLA+ model updated and passing; (iii) the glossary, state machine, event vocabulary, and
   contract schemas updated consistently together. Estate drift is recorded, never silently accommodated
   (Paper IV §15).
3. **Ratify.** HgX ratifies. Pre-1.0.0, all normative changes to Phase 0 core files require ratification
   at a Month-1-style review (D2). Post-1.0.0, MINOR and PATCH bumps may be approved by the owning
   role and recorded; MAJOR bumps always return to HgX. Ratified changes commit with descriptive
   messages and a `CHANGELOG.md` entry (estate standing rule).

Unresolved questions follow the same pipeline: OQ-1…OQ-3 carry Paper IV's recommendations as working
assumptions with named owners (decision-sheet D6); the open question is closed by a ratified change
request, not by drift. Pending operator decisions D3–D6 (isolation ladder, router trials, expiry
semantics) are adopted per Paper IV's recommendations and marked accordingly
until ratified. D7 (clock-skew bound) RATIFIED 2026-10-19: Δ = 60 seconds.

## (d) Phase 0 contract files — current versions

| File | Version | Status |
|---|---|---|
| `contracts/events.md` | 1.0.0 | RATIFIED by HgX 2026-10-19 |
| `contracts/README.md` | 1.0.0 | RATIFIED by HgX 2026-10-19 |
| `spec/state-machine.tla` | 1.0.0 | RATIFIED by HgX 2026-10-19 — written from Paper IV §6.1–§6.3 (12 states, 21 transitions, chain-of-custody by construction); TLC model-checking required in Phase 1 |
| `contracts/glossary.md` | 1.0.0 | RATIFIED by HgX 2026-10-19 — 69 terms, 25 conflicts resolved, 6 unresolved (flagged, not fudged) |
| `spec/approval-digest.md` | 0.1.0 | DRAFT — to be written from Paper IV §14 Month 1 deliverable |
| `contracts/watchtower.schema.json` | 0.1.0 | DRAFT — sketch per Paper IV §6.6 / Appendix C |
| `contracts/evidence-packet.schema.json` | 0.1.0 | DRAFT — sketch per Paper IV §6.6 / Appendix C |
| `contracts/approval-intent.schema.json` | 0.1.0 | DRAFT — sketch per Paper IV §6.6 / Appendix C |
| `contracts/decision-packet.schema.json` | 0.1.0 | DRAFT — sketch per Paper IV §6.6 / Appendix C |
| `contracts/artifact-manifest.schema.json` | 0.1.0 | DRAFT — sketch per Paper IV §6.6 / Appendix C |
| `spec/invariants.md` | 0.1.0 | DRAFT — Phase 2 owner; doctrine-to-invariant list begins in Month 1 |
| `spec/consistency.md` | 0.1.0 | DRAFT — Phase 3 owner; guarantee matrix drafted in Month 1 |
| `spec/idempotency.md` | 0.1.0 | DRAFT — Phase 4 owner; key schema drafted in Month 1 |
| `spec/router-policy.md` | 0.1.0 | DRAFT — Phase 6 owner |
| `spec/security-threat-model.md` | 0.1.0 | DRAFT — Phase 5 owner; skeleton in Month 1 |

**Distribution note (estate standing rule, 2026-10-19):** Phase 0 outputs are ingested into the
`jarvis-estate` open-source staging repository with descriptive commit messages and `CHANGELOG.md`
versioning as they land; publishability is the standing requirement, publication timing stays on HgX's
word. Nothing is pushed, shared, or published by this freeze — the contracts are drafted, not released.

---
*Authority: Paper IV v1.1 §§5.4–§6.7, §14 (Month 1); ROADMAP.md §0.4; phase-0-decision-sheet.md
(D1, D2, D5–D7). Decision D2 (2026-10-19): coordinator resolves vocabulary conflicts; HgX ratifies.*

## Version history

- **v1.1 (2026-10-20, on HgX's order):** corrected the glossary row's unresolved-term count ("6" → "3 open: U-2, U-3, U-4; 3 resolved at ratification: U-1, U-5, U-6"), matching `contracts/glossary.md` §3's 2026-10-19 ratification record. No normative change.
