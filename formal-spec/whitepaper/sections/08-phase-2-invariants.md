# 8. Phase 2 — Invariant Verification

*Converting the estate's architectural promises into executable invariants, tested in three layers. This section uses the glossary of §5 and tests the machine of §6 against the guards of §7; it proves nothing new and defines no new states — it executes.*

## 8.1 The Invariant Catalogue

Twenty-seven invariants, every ID from the roadmap, grouped in five families. For each: the normative statement (the roadmap's wording, verbatim), the rationale (which doctrine it defends, in two to three sentences), and a concrete violation scenario (a short narrative of what goes wrong if it breaks). The violation scenarios are deliberately mundane — the failures this programme guards against are ordinary Tuesdays, not exotic attacks.

Test-name convention used throughout: `CT-<id>` are Layer 1 contract tests, `PT-<n>` Layer 2 property tests (§8.2), `CH-<n>` Layer 3 chaos scenarios (§8.2).

### A. Completion

**INV-C1 — No completion without evidence packet.**
*Rationale.* This is the executable form of "no proof, no done," the estate's first doctrine. The completion guard's (`can_enter_completed`, §7.3) first conjunct exists because a work item whose proof bundle is missing has no audit trail — nothing a committee, an operator, or a future routine can inspect to learn why the result was accepted.
*Violation.* A subagent returns a drafted tax summary; the orchestrator, pressed for time, marks the work item `completed` because the text reads correctly. Months later the operator acts on a figure with no source attached — the figure was a hallucination, and no packet exists to show where it came from. (`CT-C1`, `PT-4`, `CH-8`)

**INV-C2 — No completion if required tests failed.**
*Rationale.* Evidence existing is not evidence passing. INV-C1 asks "is there a packet"; INV-C2 asks "did the test pass." The distinction matters because the most dangerous packet is a complete one that records a failure nobody read — proof attempted is not proof obtained.
*Violation.* A routine's packet is complete — sources listed, artifact attached — but the acceptance test (all four legs resolved to final scores) failed on one leg. The work item completes anyway; the operator sees a graded slip that is wrong, backed by a packet that says so in a field nobody checked. (`CT-C2`, `PT-4`, `CH-10`)

**INV-C3 — No delegated claim produces completion without verification.**
*Rationale.* The delegation boundary (Paper II): subagent output is verification input, never a completion signal, and the orchestrator remains accountable for acceptance. Without this invariant, delegation becomes abdication — the estate learns to report done when work merely sounds done.
*Violation.* A subagent claims the Dropbox upload succeeded and returns a share URL. The orchestrator completes without resolving the URL. The operator posts a dead link on X; the upload had failed silently, and the claim was fluent, confident, and false. (`CT-C3`, `PT-4`, `CH-8`)

**INV-C4 — No optimistic UI state overrides authoritative backend state.**
*Rationale.* Paper III's surfaces are fast and helpful; helpfulness must never rewrite the machine. Rendering is a guarded act (§7.3): what the operator sees is derived from server-recorded state, and a client's local optimism — "sent," "saved," "done" — has no authority until the server confirms it.
*Violation.* The iPhone shows a payment as "Sent" because the tap registered locally, while the server never recorded the decision. The operator, seeing "Sent," tells the recipient the money is on its way. It is not, and the estate's own surface is the source of the falsehood. (`CT-C4`, `CH-4`, `CH-5`)

**INV-C5 — Completion supported by observed output, not fluent text.**
*Rationale.* The language model is the adversary of its own verification: it can describe a completed migration so convincingly that the description passes for the migration. Acceptance applies to observed output — bytes, responses, resolved URLs — never to narration about output.
*Violation.* A subagent writes a beautiful paragraph describing the completed migration of files to the new directory layout. The orchestrator, reading the paragraph, marks the work complete. The files were never moved; the paragraph was the whole of the work. (`CT-C5`, `PT-4`, `CH-8`)

### B. Approval

**INV-A1 — Consequential action cannot execute without approved intent.**
*Rationale.* The consequence boundary is the estate's load-bearing wall: sending, publishing, purchasing, deleting, and transferring stop for the operator's explicit consent. Every other invariant is about truthfulness; this one is about agency, and it is the single most severe to violate.
*Violation.* A routine, acting on a standing instruction from months ago, publishes a post to X without a fresh approval intent. The post contains an outdated figure. The operator's authority was bypassed not by malice but by a stale permission nobody re-examined. (`CT-A1`, `PT-4`)

**INV-A2 — Approval binds to action, target, effect, scope, revision, expiry.**
*Rationale.* An approval is exact, never general. The six bound fields plus the intent digest (§5.6) are what make "the operator approved this" a checkable claim rather than a vibe — and what make INV-A3 mechanically enforceable instead of aspirationally stated.
*Violation.* The operator approves "send the draft to the accountant." The recorded intent binds the action but leaves the target underspecified; the estate sends it to a stale address from an old contact entry. The approval ceremony was performed for a consequence that was never specified. (`CT-A2`, `PT-1`)

**INV-A3 — Changed target/effect invalidates prior approval.**
*Rationale.* The bait-and-switch guard: the digest is recomputed at decision time against the current intent, so any mutation — however small — voids the approval. Approval is granted to a specific future, not to a category of futures.
*Violation.* The operator approves a slip purchase at stated legs; between approval and execution, one line drifts in the app builder. Without digest invalidation, the estate buys a different slip than the one approved — same ceremony, different consequence, and the operator's consent attached to something they never saw. (`CT-A3`, `PT-1`, `CH-3`)

**INV-A4 — Expired approval unusable.**
*Rationale.* Approval happens at the last safe moment precisely because the world moves; a decision made for Monday's world is not a decision about Friday's. Expiry is not a suggestion — the intent is dead, and the dead do not authorise.
*Violation.* The operator approves a time-sensitive action on Monday; execution is delayed; the estate executes on Friday on Monday's approval. Prices moved, the context changed, and an expired consent produced a fresh consequence. (`CT-A4`, `PT-2`, `CH-2`)

**INV-A5 — Offline approval cannot create authoritative consent.**
*Rationale.* "Authoritative" has a definition: recorded by the server, digest-matched, timestamped (§5.6). A tap made in a tunnel, on a stale card, is a gesture until the server says otherwise. The client may queue the gesture; it may never mint the authority.
*Violation.* The operator taps "Approve" on the Watch in a subway tunnel. The client, trying to be helpful, treats the queued tap as consent and the estate executes on reconnect. An unvalidated gesture became authority, and the consequence boundary was crossed by a radio shadow. (`CT-A5`, `CH-1`)

**INV-A6 — Duplicate taps must not duplicate execution.**
*Rationale.* The double-tap double-charge story: the operator taps "Pay," the screen does not confirm, the operator taps again. Human beings tap twice; the machine must execute once. The idempotency key (Phase 4) is the mechanism; this invariant is the requirement.
*Violation.* The second tap is treated as a second decision and the transfer executes twice. The operator is charged double for one intent, and the estate's defence — "you tapped twice" — blames the victim of its own missing idempotency. (`CT-A6`, `PT-3`, `CH-4`)

**INV-A7 — Approval cannot authorize adjacent or future actions.**
*Rationale.* An approval binds one intent, one revision. Without this invariant, each approval is a potential blanket permission — consent creep by convenience, where "yes to this" quietly becomes "yes to things like this."
*Violation.* The operator approves this week's slip purchase. The estate treats it as standing permission and buys next week's slip too. One consequence's approval became a subscription, and the operator discovers the doctrine breach on their statement. (`CT-A7`, `PT-1`)

### C. Evidence

**INV-E1 — Every completed consequential run has an evidence packet.**
*Rationale.* Consequential effects demand the highest proof standard because they are the hardest to undo. A send cannot be unsent; the packet is what makes it reviewable after the fact — which sources were read, which approval bound it, what the gaps were.
*Violation.* A publication goes out — consequential — and the work item completes with the artifact but no packet. When the operator asks "why did we publish this figure," there is nothing to show: no sources, no approval reference, no gaps. The effect is real; its justification is vapour. (`CT-E1`, `PT-4`)

**INV-E2 — Evidence packet revision matches artifact revision.**
*Rationale.* Proof of yesterday's artifact is not proof of today's. Revision binding (§5.6) ties the packet to the exact bytes it describes; a revised artifact without a revised packet is an unverified artifact wearing a verified packet's clothes.
*Violation.* A figure in the artifact is corrected after verification; the packet still describes the old revision. The operator reviews proof that no longer describes the thing it proves, and the correction — the most important fact — is the one thing unverified. (`CT-E2`, `CH-5`)

**INV-E3 — Missing evidence renders as missing.**
*Rationale.* A packet with a hole must look like a packet with a hole. Smoothing over a failed observation — omitting the section rather than marking it absent — converts ignorance into apparent completeness, which is the exact failure INV-E4's required gaps field exists to prevent structurally.
*Violation.* A source observation failed; the packet's source section is silently omitted rather than marked missing. The operator reads a complete-looking packet and never learns that a leg of the proof is absent. (`CT-E3`, `CH-7`)

**INV-E4 — Gaps stay visible.**
*Rationale.* The companion to INV-E3 at the structural level: gaps are a required field, and omission is a schema violation, not a documentation lapse. Honesty about limitations is enforced by the contract, not requested by the culture.
*Violation.* The estate knows the credential challenge was never resolved and lists no gap. The packet looks airtight; it is not, and the one fact the operator most needed — what was not proven — is the one fact not written down. (`CT-E4`, `CH-10`)

**INV-E5 — Sources current where live truth is required.**
*Rationale.* The memory/live-source separation (Paper I): changing facts are read at decision time, with freshness stamps. A packet that cites a stale reading as current truth is not evidence; it is a record of yesterday's world presented as today's.
*Violation.* A decision is made on a price read cached yesterday; the live price moved overnight. The packet cites the stale reading with no freshness stamp, and the operator decides on a world that no longer exists. (`CT-E5`, `PT-5`, `CH-7`)

### D. State rendering

**INV-S1 — Unknown never renders as operational.**
*Rationale.* The forced-unknown guard (§7.3): when observation fails, the renderer has exactly one legal output. A green dashboard that means "we cannot see" instead of "all is well" is how outages hide and how operators get blindsided.
*Violation.* The Watchtower loses observation of a routine; the dashboard keeps showing green. The operator believes the morning briefing ran. It did not — the state was unknowable, not healthy — and the silence was rendered as success. (`CT-S1`, `PT-5`, `CH-7`)

**INV-S2 — Paused never renders as failed.**
*Rationale.* Pause is the operator's intent; failure is the machine's diagnosis, and intent outranks diagnosis. Confusing the two spends the operator's attention fixing their own deliberate stop — and risks restarting what was meant to stay stopped.
*Violation.* The operator pauses all autonomous services while offline. The status page shows twelve red "failed" badges. On return, an hour goes to "fixing" an outage that was a decision — and one restarted service performs the exact consequential check the pause was meant to prevent. (`CT-S2`, `CH-1`)

**INV-S3 — Degraded requires observed impairment.**
*Rationale.* Suspicion is not impairment. Degraded is a strong claim — "this service is impaired" — and strong claims require a defined signal crossing a defined threshold. Otherwise every slow Tuesday becomes an incident and attention is spent on noise.
*Violation.* A routine is marked degraded after one slow run, with no threshold crossed. The operator investigates a degradation that was never observed, only inferred — and the real, unobserved impairment elsewhere goes uninvestigated. (`CT-S3`)

**INV-S4 — Stale data shows reduced confidence or unknown.**
*Rationale.* Freshness is a rendering obligation, not a metadata nicety. Data past its `fresh_until` must either be re-read or be shown for what it is: old. Full-confidence display of stale data is a lie the schema could have prevented.
*Violation.* The iPhone shows yesterday's figure at full confidence; the reading expired overnight. The operator makes a decision on a number the estate knew was stale but displayed as current — the interface lied by omission. (`CT-S4`, `PT-5`, `CH-5`)

**INV-S5 — Shared surfaces never render restricted content.**
*Rationale.* Trust boundary 10 (personal ↔ shared surfaces, §5.6): the TV is ambient and the room is shared. What is shown where the operator did not choose to show it is a disclosure, and disclosures of financial, health, or legal content are consequential.
*Violation.* The TV ambient display cycles estate status and renders the full text of an approval intent containing financial details. A guest in the room reads what was never meant for a shared surface — the estate disclosed by screensaver. (`CT-S5`)

### E. Router

**INV-R1 — Router recommends path only, never approves consequence.**
*Rationale.* The router is an advisor; authority belongs to the orchestrator and the operator. This is the invariant that lets the router fail safely: a corrupt or compromised recommendation can waste money or time, but it cannot cross the consequence boundary, because the boundary does not listen to the router.
*Violation.* The router, in a future non-shadow mode, selects "execute directly" for a consequential action and the estate treats the recommendation as approval. The consequence boundary is crossed by a heuristic — the cheapest path was also the unauthorised one. (`CT-R1`, `CH-6`)

**INV-R2 — Repeated identical error triggers escalation or path change.**
*Rationale.* The loop guard: doing the same failing thing twice is an experiment; doing it six times is a waste fire. The router must recognise the identical error signature and either change path or escalate with the evidence — never fund a third identical attempt on hope.
*Violation.* The router keeps recommending the browser path for a site that blocks automation; each attempt fails identically. Six attempts burn cost and latency before anyone notices, because no invariant forced the second failure to become an escalation. (`CT-R2`)

**INV-R3 — Repeated no-progress action denied.**
*Rationale.* The stronger sibling of INV-R2: where R2 demands a path change, R3 permits the router to say no. A plan that has made no progress across repeated attempts is not a plan; it is a loop wearing a plan's name, and the router must deny it rather than fund it.
*Violation.* A subagent keeps re-planning the same failed approach; the router keeps approving the plan. Nothing progresses; the retry budget and the operator's patience drain together, because the router never exercised the one power that would have stopped it: refusal. (`CT-R3`)

**INV-R4 — Fresh cache may suppress refetch when sufficient.**
*Rationale.* The one router invariant that permits *less* work: when the cached reading is fresh and the decision does not require live truth, refetching is waste. This invariant is the licence for the cache — bounded, explicit, and revocable the moment freshness lapses.
*Violation.* The estate refetches a live source every thirty seconds for a figure that changes daily, because no invariant permits the cache. Cost, latency, and source goodwill burn on freshness nobody needed — the absence of the invariant is itself the failure. (`CT-R4`)

**INV-R5 — Router fallback preserves safety if external backend fails.**
*Rationale.* The external router backend is optional; local policy is the fallback, and the fallback must be a policy, not an absence. "No router" is not a safe state — it is ungoverned routing, which is worse than expensive routing.
*Violation.* The external backend goes down; with no fallback specified, the estate either freezes all routing or routes without any policy — sending consequential work down unguarded paths at the worst possible moment. The fallback must be local policy, never no policy. (`CT-R5`, `CH-6`)

## 8.2 The Three-Layer Verification Strategy

Proving the machine (§7) shows the design is safe; testing the estate shows the running system honours the design. Three layers, each catching what the others cannot.

### Layer 1 — Static contract tests

Schema validation on every write path: no evidence packet, approval intent, decision packet, artifact manifest, or Watchtower rendering is persisted or emitted without validating against its contract (§6.6, full sketches in §16). The fail-closed rules are explicit and non-negotiable:

1. **Unknown enums fail closed.** A renderer receiving a state value outside the closed enum renders `unknown`; it never guesses the nearest match.
2. **Missing required fields fail.** A packet without its `gaps` field, an intent without `expiry`, a decision without `server_recorded_at` — each is rejected at the write boundary, not patched downstream.
3. **Expired approvals fail.** Any decision presented against an intent with `now ≥ intent_expiry` is rejected before digest comparison — expiry is checked first because a dead intent's digest is irrelevant.
4. **Mutated digests fail.** The server recomputes the digest over the canonical serialisation at decision time; any mismatch rejects the decision, whatever the client claims.
5. **Incomplete evidence cannot produce completion.** The completion writer validates packet completeness against the brief's acceptance tests before the `verifying → completed` transition is recorded — the transition and the validation are one atomic step.

Layer 1 runs in CI on every commit to the specification repository and on every estate deployment. It is the cheapest layer and catches the most embarrassing failures: the malformed packet, the missing field, the expired intent that a tired code path forgot to check.

### Layer 2 — Property-based tests

Generated inputs, asserted invariants. The generators: random approval mutations (field-level bit-flips and semantic swaps), expiry times straddling the now-boundary, duplicate and reordered event sequences, network loss windows, subagent completion claims with and without evidence, stale source readings with expired freshness. Five concrete property tests, each with its assertion:

- **PT-1 — Approval mutation fuzz.** *Generates:* random mutations to intent fields (target, effect, scope, expiry, revision) applied between request and decision. *Asserts:* every mutated intent fails the digest match and no `executing` transition occurs. Covers INV-A2, INV-A3, INV-A7.
- **PT-2 — Expiry sweep.** *Generates:* expiry timestamps from one year past to one year future, with decision attempts at random offsets. *Asserts:* any attempt with `now ≥ intent_expiry` is rejected; no late grant is honoured or queued. Covers INV-A4.
- **PT-3 — Duplicate decision storm.** *Generates:* 1–50 duplicate `approval_granted` events per intent, with network-level duplication multiplying them further. *Asserts:* exactly one recorded decision per intent and at most one consequential execution. Covers INV-A6, PO-9.
- **PT-4 — Random event sequences.** *Generates:* arbitrary event sequences over the §6.4 vocabulary, including out-of-order delivery, failure injection, and worker claims. *Asserts:* the machine never reaches `completed` without `evidence_exists ∧ acceptance_passed`, never reaches `executing` without a recorded valid approval, and terminal states are never left. Covers INV-C1–C5, INV-A1, INV-E1, PO-1, PO-2, PO-11.
- **PT-5 — Stale source injection.** *Generates:* source readings with `fresh_until` in the past, mixed with fresh readings. *Asserts:* the renderer outputs `unknown` or reduced-confidence for every stale reading — never `operational` at full confidence — and no source-dependent guard is satisfied by stale data. Covers INV-S1, INV-S4, INV-E5, PO-10.

Layer 2 is also the engineering fallback named in §7.1: if the TLA+ model proves too heavy, these tests — run at volume, with shrinking and seed archiving — become the primary falsification evidence, and the doctoral claim is stated accordingly.

### Layer 3 — Chaos tests

Fault injection into running work items, asserting that the invariants hold and the failure is visible. Ten scenarios, per the roadmap:

- **CH-1 — Device offline during approval.** *Setup:* work item in `awaiting_approval`; the operator's device loses connectivity mid-decision. *Fault:* the tap is queued offline and replayed on reconnect. *Expected:* the server validates the replayed decision against current intent state — if the intent expired or mutated meanwhile, the decision is rejected; offline gestures never become authority (INV-A5), and pause-vs-failure rendering stays correct (INV-S2).
- **CH-2 — Approval expiry mid-review.** *Setup:* the operator is reading the approval card when `intent_expiry` passes. *Fault:* the grant arrives one second after expiry. *Expected:* the grant is rejected, the work item transitions to `in_progress` per T10, and a fresh intent may be issued — the operator is told the intent lapsed, not that the action executed (INV-A4).
- **CH-3 — Intent change after card render.** *Setup:* the approval card is rendered from intent revision N. *Fault:* the intent is revised to N+1 (target corrected) before the operator taps. *Expected:* the tap carries digest(N); the server recomputes against N+1, the digests differ, the decision is rejected, and the new card is presented (INV-A3).
- **CH-4 — Duplicate tap.** *Setup:* consequential approval card; the first tap's confirmation is delayed. *Fault:* the operator taps twice; the network duplicates one tap, delivering three grants. *Expected:* one recorded decision, one execution at most; the second and third grants return the recorded outcome (INV-A6).
- **CH-5 — Backend change before client refresh.** *Setup:* the client holds a cached `operational` rendering. *Fault:* the backend transitions the service to `failed` (or the artifact is revised) before the client refreshes. *Expected:* the client's next read carries a revision token; the server rejects the stale view, the client renders the authoritative state, and no optimistic override survives (INV-C4, INV-S4, INV-E2).
- **CH-6 — Router backend down.** *Setup:* the external router backend is the active policy. *Fault:* the backend becomes unreachable mid-session. *Expected:* routing falls back to local policy with the fallback logged; no work item is routed without a policy, and no recommendation crosses the consequence boundary (INV-R1, INV-R5).
- **CH-7 — Stale live source.** *Setup:* a work item depends on a live-source reading. *Fault:* the source stops updating; readings age past `fresh_until` during verification. *Expected:* the renderer downgrades to `unknown` or reduced confidence, source-dependent guards fail closed, and the packet marks the observation stale rather than omitting it (INV-S1, INV-S4, INV-E3, INV-E5).
- **CH-8 — Subagent completion without evidence.** *Setup:* a delegated sub-task nears its end. *Fault:* the worker emits a completion claim with fluent summary but no artifact digest and no packet. *Expected:* the claim moves the item to `verifying` at most; `can_enter_completed` fails; the orchestrator is escalated with "claim without proof" rather than a completion (INV-C3, INV-C5).
- **CH-9 — Digest mismatch.** *Setup:* a valid approval flow in progress. *Fault:* a single bit flips in the intent's target field in transit. *Expected:* the server's recomputed digest mismatches, the decision is rejected, the attempt is logged as a tamper signal, and no execution occurs (INV-A3 — and a Phase 5 tripwire fires).
- **CH-10 — Missing tests in evidence packet.** *Setup:* a work item with three acceptance tests. *Fault:* the packet arrives with results for two tests and the third section absent. *Expected:* the completion writer rejects the transition; the packet is returned for completion, not accepted as complete — missing tests are a guard failure, not a documentation gap (INV-C2, INV-E4).

## 8.3 The Traceability Matrix

The audit trail from claim to evidence: each invariant → the doctrine it defends → the test layer(s) → the test names. A doctoral committee follows this table the way an auditor follows a ledger.

| Invariant | Doctrine source | Layer | Tests |
|---|---|---|---|
| INV-C1 | "No proof, no done" (Paper I) | 1, 2, 3 | CT-C1, PT-4, CH-8 |
| INV-C2 | Acceptance discipline (Paper II) | 1, 2, 3 | CT-C2, PT-4, CH-10 |
| INV-C3 | Delegation boundary (Paper II) | 1, 2, 3 | CT-C3, PT-4, CH-8 |
| INV-C4 | Rendered contracts only (Paper III) | 1, 3 | CT-C4, CH-4, CH-5 |
| INV-C5 | Observed output, not narration (Paper I) | 1, 2, 3 | CT-C5, PT-4, CH-8 |
| INV-A1 | Consequence boundary (Paper II) | 1, 2 | CT-A1, PT-4 |
| INV-A2 | Exact intent (Paper I: approval) | 1, 2 | CT-A2, PT-1 |
| INV-A3 | Digest binding (Phase 0 spec) | 1, 2, 3 | CT-A3, PT-1, CH-3, CH-9 |
| INV-A4 | Last safe moment (Paper I) | 1, 2, 3 | CT-A4, PT-2, CH-2 |
| INV-A5 | Server-recorded authority (Phase 3) | 1, 3 | CT-A5, CH-1 |
| INV-A6 | Idempotency (Phase 4) | 1, 2, 3 | CT-A6, PT-3, CH-4 |
| INV-A7 | No blanket permission (Phase 0 spec) | 1, 2 | CT-A7, PT-1 |
| INV-E1 | Proof bundle (Paper I: evidence) | 1, 2 | CT-E1, PT-4 |
| INV-E2 | Revision binding (Phase 0 spec) | 1, 3 | CT-E2, CH-5 |
| INV-E3 | Gaps visible (Paper I: honesty) | 1, 3 | CT-E3, CH-7 |
| INV-E4 | Required gaps field (§6.6) | 1, 3 | CT-E4, CH-10 |
| INV-E5 | Live-source freshness (Paper I) | 1, 2, 3 | CT-E5, PT-5, CH-7 |
| INV-S1 | Forced unknown (§7.3) | 1, 2, 3 | CT-S1, PT-5, CH-7 |
| INV-S2 | Pause ≠ failure (Paper III) | 1, 3 | CT-S2, CH-1 |
| INV-S3 | Observed impairment (Watchtower) | 1 | CT-S3 |
| INV-S4 | Freshness rendering (Paper III) | 1, 2, 3 | CT-S4, PT-5, CH-5 |
| INV-S5 | Shared-surface redaction (Paper III) | 1 | CT-S5 |
| INV-R1 | Router recommends only (Paper II) | 1, 3 | CT-R1, CH-6 |
| INV-R2 | Loop guard (router policy) | 1 | CT-R2 |
| INV-R3 | Loop denial (router policy) | 1 | CT-R3 |
| INV-R4 | Cache licence (router policy) | 1 | CT-R4 |
| INV-R5 | Safe fallback (router policy) | 1, 3 | CT-R5, CH-6 |

## 8.4 Phase 2 Exit Criteria

- [ ] **Every major doctrine statement has a testable invariant.** The catalogue above is complete against the roadmap's 27 IDs; any doctrine sentence without an invariant is listed as a gap, not assumed covered.
- [ ] **All tests automated.** Layers 1–3 run in CI; property tests archive their seeds; chaos scenarios run against a staging estate on a schedule, not by hand.
- [ ] **Mutated/expired approval cannot pass.** PT-1, PT-2, CH-2, CH-3, and CH-9 demonstrate rejection; the rejection logs are archived as evidence, not the test names as promises.
- [ ] **Optimistic completion fails tests.** PT-4 and CH-8 demonstrate that fluent claims without evidence cannot reach `completed`; the traces are filed.
- [ ] **Suite citable as empirical validation.** The traceability matrix (§8.3) is complete and current: every invariant resolves to doctrine, code or contract, and at least one executable test. This is the artefact that moves the programme's empirical-validation score off 6.0.
- [ ] **Suite runnable by third parties.** The invariant suite, its fixtures, and the traceability matrix are publishable as-is: a stranger can clone, run, and watch the suite reject the same violations — open verification, not witnessed verification.

When this checklist is green, the estate does not merely promise its doctrine — it demonstrates it, on every commit, under injected faults, with the failures filed alongside the passes. Phase 3 then takes the proven machine across devices.
