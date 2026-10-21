# From Doctrine to Proof — The J.A.R.V.I.S. Formal Validation Programme

## A Twelve-Month Roadmap to a Formally Specified, Empirically Validated, Human-Governed Agent Control Plane

**Paper IV of the J.A.R.V.I.S. White Paper Series**

*Prepared for the operator (HgX) by the J.A.R.V.I.S. estate*

October 2026 · Version 1.1

---

## Abstract

Papers I–III of the J.A.R.V.I.S. series — the operating white paper, the backend technical paper, and the front-end paper — specify an estate-scale agent architecture governed by a doctrine chain: Role → Live Source → Tool → Artifact → Evidence → Approval → Routine. An independent doctoral evaluation ranked the architecture 8.3/10 overall: high distinction as engineering architecture, but incomplete as a finished dissertation. Engineering architecture scored 9.1, the conceptual thesis 9.2, and safety and governance 9.3; empirical validation scored 6.0, and it is that score which keeps the claim at the level of strong specification rather than proven engineering.

This paper is the remediation programme. It identifies six gaps between what Papers I–III assert and what they can prove: (1) the work-state machine has never been formally modelled, so its illegal transitions have never been shown unreachable; (2) doctrinal statements have not been converted into executable invariants; (3) the multi-device consistency model is implied but never specified, leaving approval decisions on five client surfaces without a determinism guarantee; (4) idempotency semantics for consequential actions are undocumented, so duplicate taps and retries have no formal at-most-once guarantee; (5) the security boundary is honestly described as procedural isolation but never formalised as a threat model with a capability matrix and trust-boundary map; and (6) the usage router, currently in shadow mode under local policy, has never been empirically compared against baselines on measured outcomes.

The programme answers each gap in order: freeze the contracts into one canonical specification (Phase 0); model-check the state machine under a defined failure model (Phase 1); verify invariants through contract, property-based, and chaos testing (Phase 2); define the consistency contract (Phase 3); specify idempotency (Phase 4); formalise the security boundary (Phase 5); evaluate the router against measured accepted work, repair cost, and attention cost (Phase 6); and integrate all of it into doctoral evidence (Phase 7). The end-state claim this programme makes defensible is deliberately narrower and stronger than "we built a personal AI assistant": a formally specified, empirically validated, human-governed agent control plane.

The trilogy this paper remediates now carries open source as its main vision. Papers I–III (v1.2, v1.1, v1.1) state it as foundation: *"Open source from day one. J.A.R.V.I.S. is built in the open as a matter of foundation, not as a release strategy. Every aim of the programme \u2014 doctrine, skills, contracts, reference implementation \u2014 is produced to be publishable, because a system that demands to be trusted must be inspectable. The boundary is absolute: the system goes public; the principal's private life never does. These papers describe a running system, not a proposal."* This programme is therefore also the proof that an open system can be a trustworthy one. Every phase below produces artifacts that are publishable by construction — the frozen glossary, the model-checked machine, the executable invariant suite, the consistency contract, the idempotency schema, the threat model, the router’s measured comparison, the evidence package — because a system that demands public trust must offer public verification. Formal validation is the precondition of publication: proof is what makes an open control plane safe to run, inspect, and build upon.

---

## The Roadmap as Normative Source

This paper is an expansion, not a replacement, of the roadmap document at `~/workspace/jarvis-formal-spec/ROADMAP.md`. That document, issued under the operator's directive on 2026-10-08, remains the authoritative statement of phases, invariants, exit criteria, and tables. Where this paper and the roadmap disagree, the roadmap governs and this paper is in error. Where this paper adds worked examples, failure cases, prose expansion, and cross-references to Papers I–III, those additions must stay faithful to the roadmap's definitions. The discipline this paper demands of the estate — one normative spec, one owner per concept, no two documents defining the same term differently — applies to this paper itself.

---

## How to Read This Document

This paper serves three audiences, and each may enter at a different point.

**The operator** should read the Abstract, Section 2 (Introduction), and Section 16 (Definition of Done). Those sections answer three questions: what the estate claims, what would have to be true for the claim to hold, and what changes in daily practice once it holds. Section 14 (The Twelve-Month Programme) gives the schedule and its three pacing options; Section 15 (Risks and the Minimum Viable Fix) gives the fallback if the full programme cannot be sustained.

**Engineers** executing the programme should read the whole document in order. Sections 5–11 are the working specification of each phase: methods, failure models, guard tables, exit criteria, and the precise artifacts each phase must produce. Everything asserted here is traceable to the roadmap document, `~/workspace/jarvis-formal-spec/ROADMAP.md`, which is the normative source; where this paper expands, it expands rather than contradicts.

**A doctoral committee** should read Section 2 for the thesis and its evaluative context, Section 3 for the gap analysis that constitutes the problem statement, Sections 5–12 for the methodology, Section 13 for the evidence package and thesis structure, and Section 15 for the stated limitations. The limitations are part of the claim. A thesis that does not say where its proofs stop is not a doctoral thesis; it is a brochure.

---

## Conventions Used in This Paper

Terminology follows the canonical glossary to be frozen in Phase 0 (Section 5). Where a term's normative definition is not yet frozen, the paper uses the meaning given in the roadmap and says so. "Consequential action" means any action that moves effects outside the estate's observation boundary: sending, publishing, purchasing, deleting, transferring, or changing shared state. "Acceptance" means a bounded check with a stated test, applied against observed output — never against fluent text. State names (`received`, `awaiting_approval`, `completed`, and so on) and event names (`approval_requested`, `execution_observed`, and so on) are set in code font throughout, matching the canonical vocabulary.

**Open questions** are marked in bold wherever this paper identifies a decision the programme has not yet resolved — for example, the choice between TLA+ and Alloy as the primary modelling language in Phase 1, or whether the doctoral evidence will require a live multi-month router trial. These are not gaps in the paper; they are the honest frontiers of the work.

---

## Version History

| Version | Date | Status | Changes |
|---:|---|---|---|
| 0.1 | October 2026 | Draft | Initial structure: front matter, introduction, six gaps, target end-state. Remaining sections (5–16) to be drafted against ROADMAP.md phases. |
| 1.1 | October 2026 | Current | Open source elevated to the main vision throughout, consistent with the trilogy rewrites (Paper I v1.2, Papers II–III v1.1): vision statement added to the abstract, publishability woven into every phase’s exit criteria, risks, and definition of done; version history updated. |

---

## Provisional Table of Contents

| § | Title | Description |
|---:|---|---|
| 1 | Front Matter | Title, abstract, reading guide, version history, and this contents table. |
| 2 | Introduction | The trilogy's thesis restated; the independent evaluation's verdict; why formal validation is now the work. |
| 3 | The Six Gaps | Deep analysis of each gap: what Papers I–III assert, what is missing, why it matters, what "fixed" means. |
| 4 | Target End-State | The expanded end-state table: what the estate can demonstrably claim once each gap closes. |
| 5 | Phase 0: Canonical Glossary | Freezing the contracts: one normative definition per term across all three papers. |
| 6 | Phase 0: Canonical State Machine | The single work-state machine, event vocabulary, and specification repository layout. |
| 7 | Phase 1: Formal State Machine Proof | Model-checking the machine: guards, failure model, proof obligations, counterexamples. |
| 8 | Phase 2: Invariant Verification | Converting doctrine into executable invariants across three verification layers. |
| 9 | Phase 3: Consistency Model | The hybrid consistency contract for five client surfaces and one authoritative writer. |
| 10 | Phase 4: Idempotency Guarantees | Transactional semantics for preparation, approval, execution, verification, and retry. |
| 11 | Phase 5: Security Boundary Formalism | Threat model, capability matrix, trust-boundary map, and the isolation upgrade path. |
| 12 | Phase 6: Router Optimality | The empirical comparison: policies, objective function, metrics, and experimental design. |
| 13 | Phase 7: Doctoral Evidence | The evidence package, the doctoral claim, and the suggested thesis structure. |
| 14 | The Twelve-Month Programme | The three pacing options — 12-week engineering fix, 6-month validation, 12–18 month PhD track. |
| 15 | Risks and the Minimum Viable Fix | What each gap can fall back to, and what the programme assumes. |
| 16 | Definition of Done and Appendices | The fourteen completion criteria and the immediate next actions. |
