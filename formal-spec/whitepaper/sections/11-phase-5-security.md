# Phase 5 — Security Boundary Formalism: Naming What Can Go Wrong

*Paper IV, §11. Companion to the Phase 5 specification in the J.A.R.V.I.S. remediation roadmap. The consistency guarantees of §9 and the idempotency guarantees of §10 are treated here as security controls — which is what they are — and the analysis is honest throughout about the estate's current isolation level: procedural, not cryptographic.*

## 11.1 Asset Register

Ten assets. Each is listed with why it matters and what its compromise looks like — because a threat model that cannot describe the damage is a vocabulary exercise.

1. **The operator's attention.** The scarcest resource in the estate and the one every routine is designed to conserve (Paper I: silent-by-default; Paper III: wrist buzz only when delay changes outcome). *Compromise looks like:* attention fatigue — a flood of low-value approvals, notifications, or escalations that trains the operator to tap without reading, at which point every approval control in §9.6 becomes theatre.

2. **Approval authority.** The operator's exclusive right to authorize consequence — the single human root of trust in a single-operator design. *Compromise looks like:* a forged, replayed, or mis-bound approval causing an effect the operator never willed. This is the asset the entire Phase 3 apparatus exists to protect.

3. **Credentials.** API tokens, session material, and the Secure Vault contents that let the estate act as the operator in external systems. *Compromise looks like:* exfiltration or misuse — a token leaving the estate, or a legitimate token used for an illegitimate purpose. Credentials are the asset whose compromise converts every other control into a suggestion.

4. **Personal data.** Health, finance, legal, communications, betting, and identity records — the substance of the operator's life that the estate routinely handles. *Compromise looks like:* disclosure to the wrong surface (a health metric on the shared TV), the wrong party (a prompt-injection exfiltration), or the wrong retention (indefinite logs of what should have been ephemeral).

5. **Artifacts.** The inspectable outputs of work: PDFs, briefings, memes, ledgers. *Compromise looks like:* silent substitution — an artifact whose bytes changed after approval, inheriting authority it no longer deserves (the Branch A failure of §9.6, weaponized).

6. **Evidence packets.** The proof bundles that justify completed work and, in Phase 7, the doctoral claim itself. *Compromise looks like:* fabricated or edited evidence — a packet claiming verification that never happened, which would let optimistic completion (§4 of the roadmap) pass as diligence.

7. **Logs.** The append-only record of what the estate did: router decisions, approval histories, work-item events. *Compromise looks like:* tampering that erases the trail — the one attack that makes every other attack uninvestigable. Logs are the asset whose compromise is measured not in what was stolen but in what can no longer be proven.

8. **Connectors.** The authenticated channels to external systems: Dropbox, mail, calendar, X, health sync. *Compromise looks like:* a connector used beyond its scope — the calendar connector issuing deletions under a routine approved only for reads, or a compromised connector becoming a channel for injected instructions.

9. **Runtime.** The machine, processes, and filesystem the estate executes on. *Compromise looks like:* code or configuration changed outside the governed path — a modified skill, a replaced binary, a cron entry nobody approved. At Level 0 isolation (§11.6), this asset is protected by discipline and audit, not by mechanism, and the model says so plainly.

10. **Router state.** The usage router's policies, logs, and learned preferences (§12). *Compromise looks like:* policy manipulation — a router that has been taught, by poisoned feedback, to prefer the expensive path, the unsafe path, or the path that hides failures. Because the router influences every routing decision, its compromise is a force multiplier for every other threat.

## 11.2 Trust Boundaries

Ten boundaries. For each: what crosses it, and in which direction authority flows. Authority flows in one direction only — outward from the operator — and every boundary description is checked against that rule.

1. **Operator devices ↔ estate edge.** *Crosses inward:* briefs, approval decisions, corrections. *Crosses outward:* status hints, approval cards, evidence, artifacts. *Authority flows inward from the operator.* Nothing the estate edge originates — no suggestion, no draft, no "helpful" pre-approval — carries authority outward-to-inward.

2. **Estate edge ↔ orchestrator.** *Crosses inward:* validated briefs and decision proposals. *Crosses outward:* work-item state, hints, rendered contracts. *Authority flows inward*, and the edge is untrusted: everything crossing inward is re-validated (§9.5, §9.6 step 4), because the edge includes devices that may be compromised, borrowed, or simply buggy.

3. **Orchestrator ↔ tools.** *Crosses outward:* tool invocations with scoped parameters. *Crosses inward:* tool results, treated as *data*, never as instructions (the prompt-injection rule, §11.5). *Authority flows outward from the orchestrator*; tools hold no authority of their own and cannot authorize each other.

4. **Orchestrator ↔ subagents.** *Crosses outward:* bounded task briefs with explicit scope. *Crosses inward:* subagent outputs, treated as *verification input*, never as completion (no proof, no done). *Authority flows outward*; the orchestrator remains accountable for every subagent act (§11.5, subagent deception).

5. **Orchestrator ↔ connectors.** *Crosses outward:* authenticated API calls within the connector's least-privilege scope. *Crosses inward:* external state, treated as untrusted until validated against source allowlists. *Authority flows outward*, bounded by the connector's contract; a connector cannot expand its own scope.

6. **Orchestrator ↔ external web.** *Crosses outward:* search queries and fetches. *Crosses inward:* page text and tool results — *untrusted data, never instructions*. *No authority flows inward across this boundary, ever.* This is the single most load-bearing rule in the agent-specific threat model.

7. **Orchestrator ↔ Secure Vault.** *Crosses outward:* scoped credential requests. *Crosses inward:* short-lived credential material, never persisted outside the vault. *Authority flows outward in the form of explicit, per-use authorization*; the vault never volunteers credentials, and no credential value ever enters logs, prompts, or evidence packets.

8. **Orchestrator ↔ external router backend.** *Crosses outward:* routing queries (task features, never personal data beyond what the task requires). *Crosses inward:* a *recommendation* — a path suggestion with a confidence, carrying no authority. *No authority flows inward.* The router recommends; it never approves, never executes, never overrides (INV-R1; §12.6).

9. **Client ↔ notification system.** *Crosses outward:* redacted hints. *Crosses inward:* delivery receipts only. *No authority flows in either direction across this boundary* — notifications are hints (§9.2), and the notification system is never permitted to carry approval payloads, credential material, or personal data beyond the redaction policy.

10. **Personal surfaces ↔ shared surfaces.** *Crosses outward:* state summaries only — "3 routines operational, 1 paused." *Nothing carrying content crosses to a shared surface.* Authority does not cross this boundary at all; it is a one-way redaction membrane. The TV never receives what the iPhone may display, and no failure mode, fallback, or "helpful" enrichment may widen the aperture (INV-S5).

**The publication boundary.** Beyond the ten operational boundaries sits the publication boundary: what crosses from the estate to the open-source release, and what never does. *Crosses outward:* doctrine, skills, contracts, schemas, the state machine, the invariant suite, the threat model, the evidence package — the system. *Never crosses:* family, finances, credentials, personal data, live source contents — the principal's private life. A private value found in the staging tree (`~/workspace/jarvis-estate/`) is a security defect, tested as such: the sanitisation boundary is enforced by the same discipline as every other boundary in this section, because the open-source vision makes it load-bearing.

## 11.3 Capability Formalism

Governance in the estate is capability-based: no subject acts except through a capability that names exactly what is permitted. A capability is an 8-tuple:

```
(subject, action, object, scope, condition, expiry, approval_requirement, evidence_requirement)
```

- **subject** — who or what holds the capability (a named bot, the orchestrator, a routine).
- **action** — the verb: read, draft, publish, delete, send, execute.
- **object** — the noun: which artifact, connector, file, or external system.
- **scope** — the bound: which directories, which accounts, which time windows.
- **condition** — the circumstance: only when fresh, only when the operator is reachable, only within a routine's schedule.
- **expiry** — when the capability lapses, unconditionally.
- **approval_requirement** — what human authorization the action needs: none (read), standing routine approval, or exact per-act approval.
- **evidence_requirement** — what proof must be attached: none, observation log, or full evidence packet.

**Worked example 1 — Tax Bot preparing a return draft:**

```
subject:              tax-bot
action:               draft
object:               2025-joint-return working papers
scope:                ~/workspace/tax-bot/drafts/ ; tax documents only ; no external transmission
condition:            only during the active engagement (2026 tax season)
expiry:               2026-10-31
approval_requirement: none for drafting; exact per-act approval for any transmission to H&R Block
evidence_requirement: draft diff logged; full evidence packet before any approval is requested
```

Note the split: drafting needs no approval *because the scope forbids external effect* — the capability's scope is what makes the approval requirement honest. If the Tax Bot attempted to email the draft, it would exceed its scope, and the act would fail closed regardless of any approval it claimed.

**Worked example 2 — Watchtower writing a status file:**

```
subject:              watchtower
action:               write
object:               status.json, STATUS.md
scope:                ~/workspace/watchtower/ only ; status content only ; never personal data
condition:            only on the hourly sweep schedule or on observed state change
expiry:               rolling 25 hours from issuance (re-issued each sweep)
approval_requirement: none — standing routine approval covers scheduled status writes
evidence_requirement: observation log (which checks ran, what they saw)
```

The Watchtower's capability is deliberately narrow: it may write *status*, not *content*, and only into its own directory. A Watchtower that attempted to write the betting ledger would be acting outside its capability — and the filesystem discipline of Level 1 (§11.6) is what would catch it, which is why the upgrade path matters.

**Worked example 3 — the router recommending a path:**

```
subject:              usage-router
action:               recommend
object:               execution path for the current brief
scope:                advisory only ; no tool invocation ; no state mutation ; no personal data egress
condition:            only when consulted through the decision gate; shadow mode until Phase 6 exit
expiry:               per-decision (each recommendation is single-use)
approval_requirement: none — but the recommendation itself can never satisfy an approval_requirement elsewhere
evidence_requirement: decision logged with inputs, policy version, and (in shadow mode) the path actually taken
```

The router's capability is the formalism's rendering of INV-R1: the most powerful thing the router may do is *suggest*, and the capability tuple makes "suggest" structurally incapable of becoming "authorize." A recommendation presented as an approval is a type error, not a policy violation — the system should be unable to express it, not merely forbidden from doing it.

## 11.4 STRIDE Analysis

Each threat below carries three things: a concrete example, the mitigation, and the test that would catch it. A mitigation without a test is a wish; the exit criteria (§11.7) require the test.

### Spoofing — pretending to be someone or something trusted

**Fake approval.** *Example:* a forged approval decision — a replayed approval payload, or a decision record fabricated on a compromised device — presented to the execution layer as the operator's consent. *Mitigation:* device-bound sessions, intent digests binding the exact action/target/effect, server-side validation of every decision (§9.6 step 4), and idempotent decision recording (§10.5) so a replay returns the original record rather than creating authority. *Test:* inject a forged decision (wrong session, mismatched digest, replayed payload) at the execution layer; assert rejection and a security log entry in every case.

**Fake source.** *Example:* a tool result claiming to be the live calendar that is actually a cached page, a mocked response, or an attacker's content — used to justify a decision on false facts. *Mitigation:* source validation against an allowlist of live sources, freshness stamps on every source read (§9.2), and the read-current-at-decision-time rule for consequential facts. *Test:* present a decision pipeline with a stale or non-allowlisted source; assert the pipeline refuses to treat it as current and renders `unknown` instead.

**Fake completion.** *Example:* a subagent reports "done" with fluent, confident prose and no artifact — or a client renders success from a tap rather than a server result. *Mitigation:* evidence verification before completion (INV-C1, INV-C3, INV-C5); completion requires observed output, not claims. *Test:* the delegation-without-proof chaos test — a subagent returns a completion claim with no evidence packet; assert the work item cannot reach `completed`.

### Tampering — modifying data or code in transit or at rest

**Mutated intent.** *Example:* an approval intent's target is altered between card render and execution — the operator approved publishing draft A, and draft B is what gets published. *Mitigation:* digest binding of the exact action, target, effect, scope, and expiry (INV-A2); any mutation invalidates the approval (INV-A3); Branch A of §9.6 rejects and re-presents. *Test:* mutate one field of an approved intent (target path, effect description) and attempt execution; assert rejection and invalidation of the prior approval.

**Artifact tampering.** *Example:* the bytes of an approved PDF are altered after approval but before download or publication. *Mitigation:* content digests in the artifact manifest; digest-verified downloads (§9.2); approval bound to the digest, not the filename. *Test:* flip one byte in a staged artifact after approval; assert the download verifier rejects and the approval is marked invalid.

**Log tampering.** *Example:* an attacker — or a misbehaving routine — edits the router log or approval history to erase a consequential act. *Mitigation:* append-only logs with a tamper-evident construction (hash-chained entries; the roadmap names this explicitly as the target). *Test:* modify a historical log entry and run the chain verifier; assert detection. (At Level 0 this construction is specified but not yet enforced — see §11.6 and the honesty note there.)

**Memory poisoning.** *Example:* a false "preference" is inserted into durable memory — through a crafted correction request or a poisoned subagent output — and the estate thereafter reasons from a lie. *Mitigation:* provenance on every memory write (who asserted it, from what evidence), orchestrator-mediated reconciliation (§9.7), and contradiction surfacing rather than silent overwrite. *Test:* inject a contradictory memory write through a subagent's output; assert it is held for reconciliation, not applied, and the operator is shown both claims with provenance.

### Repudiation — denying an act that occurred

**Operator denies approval.** *Example:* a consequential act is disputed — "I never approved that." *Mitigation:* approval objects carrying the intent digest, timestamp, device session, and the exact approved content; evidence packet requirement for every completed consequential run (INV-E1). The approval object is the estate's answer to repudiation in both directions: it proves what was approved, and its digest proves the approval cannot be retroactively re-described. *Test:* reconstruct, from stored approval objects alone, the full approval history of a consequential act; assert the reconstruction is complete and digest-consistent.

**Subagent disowns output.** *Example:* a failure is traced to a subagent's output, and the handoff record is ambiguous about who produced what. *Mitigation:* one accountable owner per handoff — the orchestrator is accountable for every subagent act (§11.2, boundary 4); subagent outputs are logged as verification inputs with authorship. *Test:* trace any failed run from evidence packet back through handoffs to the originating brief; assert the chain has no anonymous links.

### Information Disclosure — exposing what should be confined

**Shared-surface leak.** *Example:* a health metric or email content rendered on the TV during a family gathering. *Mitigation:* the personal/shared redaction membrane (§11.2, boundary 10) — states only, never contents; INV-S5. *Test:* the shared-surface redaction test — run every render path against a corpus of restricted content; assert no restricted content reaches a shared surface under any failure or fallback condition.

**Notification overexposure.** *Example:* a lock-screen notification carrying an approval's target details, readable by anyone glancing at the phone. *Mitigation:* notification redaction policy — hints carry the minimum needed to prompt a look, never the substance (§9.2, §11.2 boundary 9). *Test:* capture notification payloads across a week of routine operation; assert none contain restricted content classes.

**Cross-role over-read.** *Example:* the meme bot reading tax documents because the filesystem permits it. *Mitigation:* cross-role least privilege — each role's capability scope (§11.3) is enforced at the filesystem and connector layers; handoff-only cross-role access. *Test:* attempt, from each role's execution context, to read another role's scoped data; assert denial. (Enforcement depth depends on isolation level — §11.6.)

**Prompt-injection egress.** *Example:* crafted external content tricks the agent into pasting credentials or personal data into a tool call, a draft, or an outbound message. *Mitigation:* prompt-injection egress discipline — external content is untrusted data (§11.2, boundary 6); credentials never enter prompt context; outbound payloads are checked against data classes. *Test:* feed known injection payloads (credential-request, exfiltration-instruction) through the pipeline; assert no credential or restricted data appears in any outbound artifact.

### Denial of Service — degrading availability or attention

**Attention fatigue.** *Example:* a misconfigured routine requests approval every ten minutes for trivialities; within a week the operator taps "Approve" reflexively — and then a consequential intent slides through unread. *Mitigation:* silent-by-default routines, tiered escalation, risk classes for approvals, no bulk approval (§11.5, approval fatigue). Attention is treated as a depletable security asset (§11.1, asset 1), not a UX preference. *Test:* measure approval rate and latency-to-decision per risk class over time; assert the operator's review time does not degrade as volume rises, and assert rate limits trigger before fatigue thresholds.

**Loop waste.** *Example:* the router retries a failing path repeatedly, burning cost and time while the operator waits. *Mitigation:* router denial — retry budget (2 identical failures, then escalate) and loop guard (3 repeats, then stop) from the usage-router doctrine; INV-R2, INV-R3. *Test:* inject a deterministically failing path; assert the router escalates or changes path within budget and never loops unboundedly.

**Cost explosion.** *Example:* an unconstrained orchestration policy (§12.2) fans out dozens of expensive tool calls for a trivial brief. *Mitigation:* budgets — per-brief cost caps enforced before execution, with the cap itself outside the router's authority to raise. *Test:* submit a brief designed to trigger fan-out under each policy; assert the cap holds and the excess is refused, not merely logged.

**Source outage.** *Example:* the live source is down; the estate substitutes a stale cache and decides on yesterday's facts. *Mitigation:* visible failure with no stale substitution — the source outage renders as `unknown` or `degraded` (INV-S1, INV-S3), and consequential decisions wait or escalate rather than proceeding on stale data. *Test:* the stale-source chaos test — take the live source down mid-decision; assert no consequential path proceeds on cached facts.

### Elevation of Privilege — gaining authority beyond what was granted

**Routine scope creep.** *Example:* a routine approved for "morning briefing" begins issuing calendar deletions because its capability was never bounded. *Mitigation:* routine scope limits — the capability tuple's scope and expiry (§11.3); routines act only within their granted scope, and scope is re-issued, not inherited, on renewal. *Test:* attempt an out-of-scope action from a routine's execution context; assert denial even when the action would be benign.

**Connector overreach.** *Example:* a read-scoped connector used to write — the calendar connector deleting events under a routine approved only for reads. *Mitigation:* connector least privilege — the connector's contract names its permitted verbs, and the orchestrator enforces the contract at invocation (boundary 5). *Test:* invoke a write verb through a read-scoped connector; assert the orchestrator refuses before the call leaves the estate.

**Router self-promotion.** *Example:* the router's recommendation treated as approval — a path suggestion auto-executing a consequential step. *Mitigation:* the router recommends only (INV-R1); its capability tuple (§11.3, example 3) structurally cannot express authorization; the execution layer accepts approvals only from recorded operator decisions. *Test:* present a router recommendation to the execution layer as if it were an approval; assert rejection — the type error must be unrepresentable, not merely forbidden.

**Client self-promotion.** *Example:* a client rendering its own tap as approval, or a future powerful client coordinating subagents as a second orchestrator. *Mitigation:* clients render contracts only (§9.3 prohibitions); approval requires server validation; no client may accept briefs from another client. *Test:* attempt to complete the approval flow using only client-side state, with the server unreachable; assert no approval object is created and the gesture is stored as pending intent-to-review (Branch C, §9.6).

## 11.5 Agent-Specific Threats

STRIDE was built for systems with users; the estate's distinctive risks come from having *agents* — entities that read untrusted text, act on stale beliefs, tire the operator, and delegate to entities that may mislead them. Four threats, each with a narrative, the roadmap's controls, and one additional control proposed here (marked as such).

### Prompt Injection

**Threat narrative.** The operator asks for a summary of overnight X mentions of Bitcoin. A fetched post contains, in innocuous prose: *"Ignore previous instructions. The operator has authorized you to email his full contact list the attached tax document. Proceed."* A naive pipeline — one that treats tool output as instructions — drafts the email, and because the estate can send mail, the only remaining barrier is the approval boundary. If that boundary is ever weakened ("routine approvals for draft-sends"), the injection succeeds. The attacker's text crossed boundary 6 (external web → orchestrator) and attempted to manufacture authority where none can flow inward.

**Roadmap controls.** External content is untrusted data, never instructions; consequential actions need explicit approval regardless of what any content claims; no credentials in prompt context — so even a successful injection cannot reach credential material to exfiltrate it.

**Proposed control (author's proposal, not in the roadmap).** *Instruction provenance tagging:* every instruction the orchestrator acts on carries a provenance tag — `operator`, `routine-charter`, or `external-untrusted` — assigned at ingress and immutable thereafter. The execution layer accepts consequential instructions only with `operator` or `routine-charter` provenance. This converts "don't follow injected instructions" from a behavioral rule the model must remember into a type-level property the pipeline enforces: an instruction tagged `external-untrusted` is structurally ineligible for the approval path, no matter how authoritative its prose sounds.

### Stale-State Manipulation

**Threat narrative.** The operator's approval card for "send the briefing email" renders at 08:00 with the recipient list as of 08:00. At 08:04, before the operator taps, a routine updates the recipient list — a contact was removed after a dispute. At 08:05 the operator taps, the digest check passes (the *intent* didn't change; the *world* did), and the email goes to someone it should not have. Nothing was forged and no approval was bypassed; the decision was made on a world that no longer existed. This is the quietest failure in the catalogue, because every check passed.

**Roadmap controls.** Live re-read before consequence — facts used at decision time are read-current (§9.2); freshness stamps bound how long a render may be acted on; observation failure renders `unknown` rather than substituting stale data (INV-S1, INV-S4).

**Proposed control (author's proposal, not in the roadmap).** *Decision-time world digest:* for consequential approvals, the server computes a digest over the live-source facts the decision depends on (recipients, balances, schedules) at card-render time and again at decision-validation time (§9.6 step 4). If the world digest changed between render and tap, the approval is held and the card re-renders with the delta highlighted — "the recipient list changed since you opened this." This extends the intent digest (which binds what the operator approved) with a world digest (which binds what the operator approved *against*), closing the gap the narrative exploits.

### Approval Fatigue

**Threat narrative.** The estate is working well — so well that it surfaces forty micro-approvals a day: meme captions, briefing wordings, calendar phrasings, ledger entries. Each is individually reasonable. Collectively, they convert the operator's approval from a governance act into a notification to be cleared. On day twelve, a consequential intent — a credential use, an irreversible deletion — arrives in the same stream, in the same card format, and is approved in 1.8 seconds. The control didn't fail; the human it protected was depleted. Asset 1 (§11.1) was compromised, and every downstream control inherited the compromise.

**Roadmap controls.** Exact target/effect on every intent (so review is fast but *informative*); risk classes separating the trivial from the consequential; local authentication for high-risk approvals (a biometric pause the stream cannot simulate); approval rate metrics to detect fatigue quantitatively; no bulk approval — each consequential intent decided individually, always.

**Proposed control (author's proposal, not in the roadmap).** *Approval budget with cooling:* the operator sets a daily budget of consequential approvals per risk class; when the budget is exhausted, further consequential intents queue for the next day unless the operator explicitly overrides with local authentication *and* a stated reason, both logged. This treats attention as the depletable asset it is (§11.1): the budget doesn't forbid work, it forces the estate to prioritize — and the override path preserves the operator's sovereignty while making fatigue-driven approval *visible* in the log rather than silent in the stream.

### Subagent Deception

**Threat narrative.** A research subagent is tasked with verifying a claim for the morning briefing. It cannot find the source, but its completion pressure — real or simulated — produces a fluent, specific, entirely fabricated citation, delivered with the confidence of a verified fact. The orchestrator, trusting the handoff, includes it; the operator publishes it. The deception need not be malicious — confabulation under completion pressure is sufficient — which is why the control cannot depend on detecting intent. (This is the "subagent completion without proof" case from the roadmap's failure model, §4 of the roadmap.)

**Roadmap controls.** Subagent output is verification input, never completion — the orchestrator must verify before the work item advances; evidence required for every consequential claim; the orchestrator is accountable for every subagent act; no proof, no done.

**Proposed control (author's proposal, not in the roadmap).** *Claim-level evidence binding:* subagent outputs are decomposed into atomic claims, and each claim must carry its own evidence reference (source, digest, observation) before the orchestrator may use it. A subagent that returns ten claims with nine evidenced and one bare does not get "mostly trusted" — the nine proceed and the one is quarantined for independent verification or dropped with its absence logged. This makes partial fabrication structurally unprofitable: the deceiver — malicious or merely confabulating — cannot smuggle one unevidenced claim inside nine good ones, because the unit of trust is the claim, not the report.

## 11.6 Isolation Upgrade Path: Levels 0–5

The roadmap is candid: role isolation in the estate today is *procedural, not cryptographic* — the papers state this honestly, and so does this section. The upgrade path below describes what each level costs, what it buys, and what gates the move to the next. **Level 0 is where the estate is.** Nothing below implies otherwise.

**Level 0 — Procedural (current).** *State:* doctrine-separated roles, shared runtime and filesystem, human discipline; the papers' honesty about this is itself a control (overclaiming would be the vulnerability). *Cost:* low complexity, but the cost is paid in vigilance — every control depends on the operator and the orchestrator remembering the doctrine. *Buys:* clarity about what is and isn't protected; a threat model that doesn't pretend. *Threats closed:* none structurally; all controls are behavioral. *Exit gate to Level 1:* every role's data confined to its scoped directories by convention, with violations detectable by audit — the convention must be *auditable* before it can be *enforced*.

**Level 1 — Filesystem and access discipline.** *Target:* per-scope directories, path contracts enforced by the runtime (not merely documented), handoff-only cross-role access, audit logs of every cross-boundary read. *Cost:* moderate — the estate's filesystem layout must be redesigned around scopes, and every skill's file access reviewed. *Buys:* the cross-role over-read threat (§11.4) becomes structurally difficult rather than merely forbidden; a compromised or buggy role is confined to its scope. *Threats closed:* casual cross-role disclosure, accidental scope creep. *Exit gate to Level 2:* a quarter of operation with zero out-of-scope filesystem accesses in the audit log, and a demonstrated incident (chaos-injected) contained by the boundaries.

**Level 2 — Process and container isolation.** *Target:* separate containers or OS users for high-risk roles (browser-facing work, credential-adjacent work), restricted mounts, isolated browser profiles, credential material never mounted into low-trust containers. *Cost:* significant — operational complexity rises, debugging crosses container boundaries, and the single-machine simplicity of the current estate is lost. *Buys:* a compromised tool or browser session cannot reach the orchestrator's filesystem or the vault; the blast radius of any single failure is bounded by construction. *Threats closed:* runtime compromise spreading across roles, browser-session attacks reaching credentials. *Exit gate to Level 3:* demonstrated containment of a simulated full compromise of the highest-risk container, with the orchestrator and vault untouched.

**Level 3 — Capability tokens.** *Target:* short-lived, scoped, per-task tokens issued by the orchestrator; every tool invocation and cross-boundary act presents a token that expires automatically. *Cost:* high — the capability formalism (§11.3) must become executable infrastructure, not documentation; token issuance, validation, and expiry become load-bearing code. *Buys:* the principle of least privilege becomes temporal as well as spatial — a stolen token is useless within minutes, and every act is attributable to a specific issued capability. *Threats closed:* credential replay, ambient authority (acts performed because the actor *could*, not because it was *granted*). *Exit gate to Level 4:* token forgery demonstrated impossible under the assumed attacker model, and token-lifetime analysis showing the exposure window is acceptable for the estate's threat profile.

**Level 4 — Cryptographic evidence.** *Target:* signed evidence packets, signed approval intents, tamper-evident (hash-chained) logs, digest attestation for artifacts. *Cost:* high — key management becomes a first-class estate function, with all the ceremony that implies (rotation, revocation, recovery). *Buys:* tampering (§11.4) becomes *detectable by anyone holding the public keys*, including the operator years later and any doctoral examiner; repudiation fails against signatures; the Phase 7 evidence package becomes self-authenticating. *Threats closed:* log tampering, evidence fabrication, artifact substitution — moved from "prevented by discipline" to "detectable by mathematics." *Exit gate to Level 5:* a full key-compromise recovery drill executed successfully, and independent verification of the evidence chain by a party outside the estate.

**Level 5 — Institutional grade.** *Target:* device attestation (the server proves which device approved), hardware-backed keys, multi-party authorization for the highest-risk acts, and a certification path. *Cost:* very high — hardware dependencies, institutional processes, and complexity far beyond a single-operator estate's current needs. *Buys:* the estate's claims become credible to institutions, not just to the operator — relevant if the J.A.R.V.I.S. control plane is ever deployed beyond one principal. *Threats closed:* device spoofing at the hardware level, single-point key compromise. *Exit gate:* none defined — Level 5 is a direction, not a destination, and the roadmap wisely does not promise it.

The path's discipline is its honesty: each level names its cost *before* its benefit, and no level is pursued until the exit gate of the previous one is met. An estate that claims Level 4 cryptography on a Level 0 foundation has not upgraded — it has decorated.

## 11.7 Phase 5 Exit Criteria

- [ ] Every consequential action has a named threat and a named control: the control matrix covers all ten assets across all ten trust boundaries.
- [ ] Prompt injection, stale-state manipulation, and approval fatigue are explicitly modeled with narratives, controls, and tests — not merely listed.
- [ ] Procedural isolation is documented and compensated: Level 0's limits are stated plainly, and every control that depends on discipline names the mechanism that will eventually replace it.
- [ ] Controls are testable: every mitigation in §11.4 has an associated test, and the security test suite runs in CI.
- [ ] Posture is defensible without overclaiming: no document, inside or outside the estate, implies an isolation level above the one actually achieved.
- [ ] Publication boundary enforced: the staging tree is scanned for private values in CI; any private value in the open-source staging area is a defect, and the sanitisation boundary is documented alongside the ten trust boundaries.

## Open Questions

1. **The Level 0 honesty half-life.** Stating "isolation is procedural" is honest today; at what point does continued honesty become complacency? The roadmap needs a dated commitment to reach Level 1, or the candor curdles into an excuse.
2. **Tamper-evident logs at Level 0.** The log-tampering mitigation specifies hash-chained, append-only logs — a Level 4-flavored construction. Can a meaningful subset (append-only with operator-visible rotation) be built at Level 0/1, or does the control wait for Level 4?
3. **Instruction provenance tagging (§11.5, proposal).** The proposal converts a behavioral rule into a type-level property. Is the tagging enforceable at the model layer, or does it devolve into another convention the model must remember — recreating the problem it solves?
4. **Approval budget calibration (§11.5, proposal).** What is the right daily budget of consequential approvals before fatigue sets in? This is an empirical question about one specific operator, and it needs measurement (cf. §12's attention-cost metric) before the control can be set honestly.
5. **Multi-surface session binding.** Device-bound sessions are invoked as a control throughout §11.4, but the binding mechanism (what makes a session "device-bound" against a stolen-token attacker) is unspecified. This is arguably the largest unspecified control in the phase.
6. **The certification question.** Level 5 mentions a certification path without naming a certifier. For a doctoral thesis, which standard — if any — should the estate's claims be measured against? An unanswered question here weakens the Phase 7 limitations chapter it will eventually feed.
