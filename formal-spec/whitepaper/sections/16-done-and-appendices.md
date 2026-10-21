# 16. Definition of Done and Appendices

## Part 1 — Definition of Done

The roadmap states fourteen definition-of-done statements, to which this paper adds a fifteenth of its own. A statement is not a criterion until an independent reviewer can check it, so each statement below is operationalised as two to four concrete checks. The reviewer needs no access to the estate's internals beyond the specification repository, the test suites, and the evidence package: if a statement cannot be checked with those, it is not done.

**1. The state machine has a formal specification.**
- Open `spec/state-machine.md` in the specification repository and confirm it defines all twelve states, the transition skeleton, and the guard table with one owner per concept.
- Confirm the formal model in `proofs/` parses in the chosen language and covers every transition in the skeleton — no transition exists in prose that has no counterpart in the model.
- Confirm the repository is versioned and that the specification the model was checked against is the version the estate currently implements (drift check).

**2. Illegal transitions are shown to be unreachable under the defined failure model.**
- Run the model checker against the archived model and confirm it reports no reachable illegal state.
- Inspect the failure model document and confirm each of the thirteen failure conditions is defined explicitly enough to be criticised.
- Select at least two guards, weaken them, re-run the checker, and confirm a counterexample is produced — the proof must be capable of failing.

**3. Core invariants are tested automatically.**
- Run the full invariant suite and confirm all 27 invariants (Appendix A) have at least one test in an applicable layer.
- Confirm the suite runs without manual steps in the estate's continuous check, and inspect the traceability matrix for any invariant with a doctrine statement but no test.
- Introduce a deliberate invariant violation in a test fixture and confirm the suite fails.

**4. Mutated or expired approvals cannot execute.**
- Run the mutated-approval test suite: submit an approval whose intent digest no longer matches the intent, attempt execution in the harness, and confirm rejection is logged.
- Attempt execution with an expired intent in the chaos harness and confirm the attempt is refused and the refusal is recorded as `approval_expired`, not silently dropped.
- Confirm no test path exists in which a mutated or expired approval reaches `execution_started`.

**5. Multi-device state conflicts resolve deterministically.**
- Run the multi-device conflict tests and confirm each row of the conflict-resolution table produces the specified resolution.
- Replay the two-devices-one-approval case twice from the same initial conditions and confirm the same device's decision is recorded and the other is told it lost, identically both times.
- Confirm no test leaves two inconsistent consequential outcomes standing.

**6. Offline taps cannot become approvals.**
- Simulate a device offline at the moment of the approval tap, then reconnect, and confirm the tap produced a pending gesture only — no `approval_granted` event exists for it.
- Confirm the server-side validation (intent exists, unexpired, digest matches, session authorised) ran after reconnect and independently of the client's cached card.
- Confirm the client rendered the authoritative result after reconnect rather than its own cached assumption.

**7. Duplicate taps cannot create duplicate consequences.**
- Execute the duplicate-tap test: two identical approval taps against the same intent, and confirm the second returns the existing decision and state with no second execution.
- Confirm the idempotency key for the action is identical across both taps and that the execution record shows a single execution.
- Confirm the attempt count incremented while the effect count did not.

**8. Ambiguous execution becomes visible unknown or failed, not false completion.**
- Run the ambiguous-outcome test: a consequential execution whose result cannot be observed, and confirm the work item renders as `execution_unknown` or `failed` — never `completed`.
- Confirm no automatic retry occurred for the consequential action (the safe-to-retry flag was not set).
- Confirm the escalation record exists: the ambiguity was surfaced with the next safe option, not buried.

**9. Security boundaries and limitations are explicitly modeled.**
- Open the threat model and confirm all ten trust boundaries are drawn, the asset register is complete, and every consequential action has a named threat and control.
- Confirm the procedural-isolation limitation is stated in the model's own words, with compensating controls named — not implied, not footnoted.
- Confirm the isolation upgrade roadmap (Levels 0–5) exists with evaluation criteria, and that the estate's current level is stated plainly.

**10. Prompt injection, stale state, and approval fatigue are addressed.**
- Confirm each of the three appears in the threat catalogue with a named control and at least one test — a mention without a control does not count.
- Run the prompt-injection egress test: consequential action attempted from untrusted external content, and confirm it is refused without explicit approval.
- Run the stale-state test: a consequential decision attempted against expired source freshness, and confirm it renders unknown or re-reads rather than substituting.
- Inspect the approval-rate metrics and confirm the fatigue controls (exact target/effect, risk classes, no bulk approval) are implemented, not merely specified.

**11. The usage router is evaluated against baselines.**
- Confirm the router experiment report compares the governed policy against at least the local, cache-only, and unconstrained baselines on the stated objective function.
- Confirm the decision-log schema carries outcome labels and that every evaluated decision links to a labelled outcome.
- Confirm the router guardrails were enforced during evaluation: no evaluated run shows the router approving consequence or overriding an approval boundary.

**12. The evaluation measures accepted work, repair, cost, latency, loops, and attention cost.**
- Confirm each of the six metrics is defined in the experiment protocol and present in the results — a missing metric fails the statement.
- Confirm attention cost was measured with the characterised method from Month 9, with its noise and limitations stated alongside the numbers.
- Confirm the results report uncertainty (credible intervals or equivalent), not point claims.

**13. The limitations remain honest.**
- Read the limitations section and confirm it names, specifically: the failure-model boundaries, the single-operator measurement thinness, the procedural isolation, and the bounded router evaluation.
- Confirm no limitation is phrased as a vague gesture ("further work is needed") without the specific boundary it concedes.
- Confirm the failure case studies exist and that at least one describes a gap that let a failure through, not only invariants that caught one.

**14. The evidence supports the thesis.**
- For each clause of the doctoral claim, follow the traceability matrix to its supporting and refuting evidence and confirm both exist.
- Confirm the adversarial integration review was conducted and its report records which claims were kept, cut, or downgraded, with reasons.
- Confirm the operator (HgX) reviewed the package and approved the claim as stated — or that the claim was restated until he did.

**15. The programme's artifacts are publishable by construction.**
- Open the specification repository, the formal model, the invariant suite, the consistency contract, the idempotency schema, the threat model, the router's labelled decision history, and the evidence package, and confirm each contains no private value — no family detail, credential, financial record, or live-source content.
- Confirm the open-source staging tree (`~/workspace/jarvis-estate/`) builds from these artifacts without a separate sanitising effort — publishability was constructed in, not cleaned up after.
- Confirm the trilogy's vision statement appears in the programme's own account of itself: the evidence package describes a system built to be open, with the publication boundary stated and tested.

## Part 2 — Final Recommendation

The roadmap's recommended sequence is restated here as a closing argument, because the sequence is the argument: Freeze the doctrine → Formalise the state machine → Turn doctrine into invariants → Define consistency and idempotency → Formalise security boundaries → Measure router performance → Integrate into doctoral evidence.

The order is not administrative; it is logical. Nothing can be proven about a system whose contracts are not frozen, so the freeze comes first — one vocabulary, one state machine, one owner per concept, before any model is written. The state machine is formalised next because every later guarantee (approval binding, evidence discipline, consistency, idempotency) is a property of transitions, and properties of transitions need a checked machine to hang on. Doctrine becomes invariants third because the invariants are the machine's properties made executable — the bridge between the proof and the running estate. Consistency and idempotency come fourth because they are the properties of the machine under the real world's faults: multiple devices, duplicate taps, lost networks, ambiguous outcomes. Security is formalised fifth because a threat model written before the system is specified describes a fiction; written after, it describes the thing the committee will actually attack. The router is measured sixth because measurement needs the governed system to exist first — you cannot evaluate a policy against a machine that is still changing shape. And evidence is integrated last because integration is arrangement, not discovery: the thesis is the argument the previous six phases earned.

The fastest way to fix the gaps is not to add more features. That sentence, from the roadmap, deserves to be the programme's motto, because every pressure the twelve months will exert — to add a dashboard instead of characterising the noise, to add an isolation level instead of writing the cost-benefit analysis, to add formalism instead of running the trial — is a pressure to build rather than to prove. The programme resists it the same way the estate resists it: no proof, no done. A month is not complete when its artifacts exist but when its exit criteria are evidenced; a claim is not made when it is written but when its refuting evidence has been collected and came out in its favour.

What this sequence produces, if it is followed honestly, is not just a thesis but a different estate: one whose doctrine is executable, whose approvals are binding objects rather than gestures, whose evidence is structural rather than decorative, and whose operator's attention is a budgeted quantity rather than an assumed infinite resource. The doctoral claim — a formally specified, empirically validated, human-governed agent control plane — is then not a description of what was built but a statement of what was shown. That is the correct sequence, and it is also the correct order of operations for everything the estate will build afterwards: freeze, formalise, verify, and only then claim.

## Part 3 — Appendices

### Appendix A — Invariant ID Table

The 27 normative invariants, each with its one-line statement. Full definitions, doctrine links, and test mappings live in the invariant catalogue (`spec/invariants.md`) and the traceability matrix.

| ID | Normative statement |
|---|---|
| INV-C1 | No work item reaches `completed` without an evidence packet. |
| INV-C2 | No work item reaches `completed` when required tests have failed. |
| INV-C3 | No delegated claim produces completion without independent verification. |
| INV-C4 | No optimistic client state overrides authoritative backend state. |
| INV-C5 | Completion is supported by observed output, not by fluent text. |
| INV-A1 | No consequential action executes without an approved intent. |
| INV-A2 | Every approval binds to exact action, target, effect, scope, revision, and expiry. |
| INV-A3 | Any change to the bound target or effect invalidates a prior approval. |
| INV-A4 | An expired approval is unusable for execution. |
| INV-A5 | An approval granted offline cannot create authoritative consent. |
| INV-A6 | Duplicate approval taps must not produce duplicate execution. |
| INV-A7 | An approval cannot authorise adjacent or future actions beyond its bound intent. |
| INV-E1 | Every completed consequential run has an evidence packet. |
| INV-E2 | The evidence packet revision matches the artifact revision it supports. |
| INV-E3 | Missing evidence renders as missing; it is never rendered as present. |
| INV-E4 | Gaps in evidence stay visible; they are never silently filled. |
| INV-E5 | Sources are current where live truth is required for a decision. |
| INV-S1 | `unknown` never renders as operational on any surface. |
| INV-S2 | `paused` never renders as `failed` on any surface. |
| INV-S3 | `degraded` requires an observed impairment, not an inference. |
| INV-S4 | Stale data renders with reduced confidence or as `unknown`. |
| INV-S5 | Shared surfaces never render restricted content. |
| INV-R1 | The router recommends a routing path only; it never approves a consequence. |
| INV-R2 | A repeated identical error triggers escalation or a path change. |
| INV-R3 | A repeated no-progress action is denied rather than retried indefinitely. |
| INV-R4 | A fresh cache may suppress refetch when the cached value is sufficient. |
| INV-R5 | Router fallback preserves safety when the external backend fails. |

### Appendix B — Canonical Event Vocabulary

The fifteen normative events. Each event is appended to the work item's history when its transition occurs; the vocabulary is frozen in Phase 0 and owned per the specification repository.

| Event | Definition |
|---|---|
| `brief_received` | The operator or an authorised routine submits a bounded unit of work. |
| `brief_accepted` | The orchestrator accepts the scope of the submitted work. |
| `plan_created` | A bounded plan for the work exists and is recorded. |
| `artifact_produced` | An inspectable output of the work exists. |
| `evidence_packet_created` | The structured proof bundle for the work exists. |
| `approval_requested` | The work has reached a consequence boundary; an approval intent is issued. |
| `approval_granted` | The exact bound intent was approved by the operator. |
| `approval_denied` | The bound intent was denied by the operator. |
| `approval_expired` | The bound intent passed its expiry without decision. |
| `execution_started` | The approved consequential action began executing. |
| `execution_observed` | The result of the execution was observed. |
| `acceptance_passed` | The bounded acceptance test passed against observed output. |
| `failure_observed` | A failure condition was observed during the work. |
| `operator_paused` | The operator paused the service or the work item. |
| `observation_unavailable` | The state of the work cannot currently be established. |

### Appendix C — Contract Schema Sketches

Compact sketches of the four principal contracts. Field types are indicative; the normative schemas live in `contracts/` and are frozen in Phase 0. Each sketch is kept under forty lines.

**C.1 `evidence-packet.schema.json`** — the structured proof bundle attached to completed consequential work.

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "EvidencePacket",
  "type": "object",
  "required": ["packet_id", "work_id", "artifact_revision", "created_at", "checks"],
  "properties": {
    "packet_id":        { "type": "string" },  // unique packet identifier
    "work_id":          { "type": "string" },  // work item this packet proves
    "artifact_revision":{ "type": "string" },  // must equal the artifact revision (INV-E2)
    "created_at":       { "type": "string", "format": "date-time" },
    "approval_ref":     { "type": "string" },  // intent_id, required if consequential
    "checks": {                               // acceptance checks, each observed
      "type": "array",
      "items": {
        "type": "object",
        "required": ["name", "result", "observed_at"],
        "properties": {
          "name":        { "type": "string" },
          "result":      { "type": "string", "enum": ["pass", "fail"] },
          "observed_at": { "type": "string", "format": "date-time" },
          "detail":      { "type": "string" }  // what was observed, not asserted
        }
      }
    },
    "gaps": {                                 // visible gaps (INV-E4)
      "type": "array",
      "items": { "type": "string" }
    }
  }
}
```

**C.2 `approval-intent.schema.json`** — the exact consequential action awaiting the operator, digest-bound.

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "ApprovalIntent",
  "type": "object",
  "required": ["intent_id", "action", "target", "effect", "scope",
               "revision", "expires_at", "intent_digest"],
  "properties": {
    "intent_id":     { "type": "string" },  // unique intent identifier
    "action":        { "type": "string" },  // e.g. send, publish, purchase, delete
    "target":        { "type": "string" },  // exact target of the action
    "effect":        { "type": "string" },  // exact effect to be produced
    "scope":         { "type": "string" },  // bounds of the authorisation
    "revision":      { "type": "string" },  // intent revision; any change invalidates (INV-A3)
    "expires_at":    { "type": "string", "format": "date-time" },
    "intent_digest": { "type": "string" },  // hash over the bound fields (digest rule, Phase 0)
    "risk_class":    { "type": "string", "enum": ["standard", "high", "irreversible"] },
    "requested_at":  { "type": "string", "format": "date-time" }
  }
}
```

**C.3 `watchtower.schema.json`** — the status report contract for the hourly monitoring sweep.

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "WatchtowerReport",
  "type": "object",
  "required": ["report_id", "observed_at", "services"],
  "properties": {
    "report_id":   { "type": "string" },
    "observed_at": { "type": "string", "format": "date-time" },
    "services": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["name", "state", "freshness"],
        "properties": {
          "name":      { "type": "string" },
          "state": {                            // operator-paused reads as paused, never down
            "type": "string",
            "enum": ["operational", "paused", "degraded", "unknown"]
          },
          "freshness": {                        // when the observation was taken
            "type": "object",
            "required": ["observed_at", "fresh_until"],
            "properties": {
              "observed_at": { "type": "string", "format": "date-time" },
              "fresh_until": { "type": "string", "format": "date-time" }
            }
          },
          "note": { "type": "string" }          // only when state is not operational
        }
      }
    }
  }
}
```

**C.4 `router-decision-log.schema.json`** — the usage router's decision record with outcome labels (Phase 6).

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "RouterDecision",
  "type": "object",
  "required": ["decision_id", "work_id", "decided_at", "policy", "chosen_path"],
  "properties": {
    "decision_id": { "type": "string" },
    "work_id":     { "type": "string" },
    "decided_at":  { "type": "string", "format": "date-time" },
    "policy":      { "type": "string" },  // e.g. local, cache-only, hybrid
    "chosen_path": { "type": "string" },  // recommendation only; never an approval (INV-R1)
    "alternatives_considered": { "type": "array", "items": { "type": "string" } },
    "outcome": {                           // labels attached after the fact (Month 9)
      "type": "object",
      "properties": {
        "accepted":               { "type": "boolean" },
        "human_repair":           { "type": "boolean" },
        "repair_time_minutes":    { "type": "number" },
        "cost_units":             { "type": "number" },
        "latency_seconds":        { "type": "number" },
        "attention_interruptions":{ "type": "integer" },
        "evidence_complete":      { "type": "boolean" }
      }
    }
  }
}
```

### Appendix D — References and Further Reading

The estate's own sources first, then the general literature a committee would expect. General works are cited by name and idea only; no publication details are asserted beyond what is stated here.

- **Paper I — the J.A.R.V.I.S. operating white paper.** The estate's operating doctrine: the Role → Live Source → Tool → Artifact → Evidence → Approval → Routine chain, the approval disciplines, and the silent-by-default routine posture. The philosophical source of the programme's claim.
- **Paper II — the J.A.R.V.I.S. backend technical white paper.** The backend lifecycle (Brief → Route → Plan → Execute → Verify → Approve → Handoff), the runtime and skill architecture, and the scheduling and memory contracts. The engineering source of the state machine and invariant work.
- **Paper III — the J.A.R.V.I.S. front-end white paper.** The operator loop (Brief → Work → Evidence → Approval → Decision) across the five client surfaces, the attention disciplines, and the rendering contracts. The source of the consistency model and the attention-cost invariant.
- **The Grok Bot field guide** — *The One-Person Company: how one operator turns one request into a small working team* (independent 12-page field guide, 2026). Cited honestly as the doctrine's source text: the role, live-source, tool, artifact, evidence, approval, and routine pattern that Papers I–III formalise. The programme claims the formalisation, not the pattern.
- **The roadmap document** — `~/workspace/jarvis-formal-spec/ROADMAP.md` (2026-10-08). The normative source for this paper: phases, invariants, exit criteria, tables, and the fourteen definition-of-done statements. Where this paper and the roadmap disagree, the roadmap governs.
- **TLA+** — Leslie Lamport's temporal specification language and its model checker: the recommended primary tool for the Phase 1 state-machine proof, valued for its treatment of concurrency, failure, and liveness properties in systems work.
- **Alloy** — the lightweight formal modelling language: the recommended alternative for Phase 1, valued for its lower learning curve and its analyser's ability to find counterexamples in bounded scopes.
- **Calm technology** — Weiser & Brown, *The Coming Age of Calm Technology*: the intellectual ancestry of the attention-cost invariant — the proposition that technology should respect the periphery of human attention, here operationalised as a measurable, budgeted system property rather than a design preference.
- **STRIDE threat modelling** — the spoofing, tampering, repudiation, information disclosure, denial of service, and elevation of privilege taxonomy: the structural basis of the Phase 5 threat catalogue, extended with the agent-specific threats (prompt injection, stale-state manipulation, approval fatigue, subagent deception).
- **Property-based testing** — the discipline of asserting properties over randomly generated inputs and event sequences: the methodological basis of the Phase 2 Layer 2 suite, where the invariants are checked against generated approval mutations, expiry timings, duplicates, and network faults rather than hand-written cases.
- **Human-AI interaction governance** — the literature on keeping a human meaningfully in command of autonomous systems: the field within which the approval-binding mechanism and the attention-cost measurement claim their contribution, and against which the thesis positions its "contracts around the model" proposition.
