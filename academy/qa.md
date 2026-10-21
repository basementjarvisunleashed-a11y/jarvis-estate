# Academy Q&A

Checkpoint questions from the papers, with answers drafted strictly from the paper texts. Where the study digest does not carry the exact wording, the answer says so and the question is marked for the session.

---

## Paper I — The Vision (v1.2)

**Q1. Recite the fifth principle verbatim, and explain the paper's distinction between open source as "foundation" versus as "release strategy."**

A: *"A fifth principle stands alongside the four above: Open source from day one. J.A.R.V.I.S. is built in the open as a matter of foundation, not as a release strategy. Every aim of the programme — doctrine, skills, contracts, reference implementation — is produced to be publishable, because a system that demands to be trusted must be inspectable. The boundary is absolute: the system goes public; the principal's private life never does."* Foundation means the work is *produced to be publishable* from the first day — clarity, honest testing, no hidden assumptions — regardless of when anything is actually released. Release strategy would be a timing decision about shipping; the paper rejects that framing: *"Open source is the main vision, not a release strategy."* Publishability is the standing requirement from day one; publication timing remains on HgX's word.

**Q2. The paper draws an absolute boundary. State it exactly, then name three things that go public and three that never do, with the paper's reason for the sanitising pass.**

A: *"The boundary is absolute: the system goes public; the principal's private life never does."* Goes public: the doctrine and principles; skills as versioned reusable operating contracts; the reference implementation, its tests, and its history. Never goes public: the principal's private life, family, and household; finances, credentials, and personal records; live estate data, messages, and private memory. The reason: *"The sanitising pass is real work: only the system is publishable."*

**Q3. The paper says open source is how leverage compounds beyond one estate. Explain the mechanism in the paper's terms — what travels, and what explicitly does not.**

A: *"Other operators can adopt the doctrine, inspect the reference implementation, and improve it, without ever gaining access to this estate."* What travels: the doctrine, the contracts, the reference implementation, the papers. What explicitly does not: access to this estate — no operator gains entry to HgX's system by adopting its published parts.

**Q4. What does the "Open architecture" rule require of the federation's contracts, and who is its imagined reader?**

A: *"The federation is described in published contracts, not in private folklore. A new role, engine, or operator should be able to understand the architecture from the public papers and repository alone."* The imagined reader is a stranger — a new role, engine, or operator — who can learn the architecture from the papers and the repository without private briefing.

**Q5. State the five-part chain maxim verbatim, and explain the sentence about the "private habit."**

A: *"Keep roles narrow. Keep facts current. Keep proof visible. Keep consequences reviewable. Keep the method publishable."* The paper adds: *"Every stage of the chain produces something an outside reviewer could, in principle, inspect. A method that cannot survive publication is not finished doctrine; it is a private habit."* Publishability is a quality gate: if the method couldn't be shown, it isn't done.

**Q6. Where does the paper say the public/private boundary is enforced in practice, and which two classes of memory fall on each side?**

A: *"Memory is where the boundary is enforced in practice."* On the publishable side: *"Durable methods, role definitions, and principles belong to the system and are publishable."* On the side that never leaves the estate: *"Personal memory — preferences tied to a private life, household detail, and lived history — stays in the estate and is never part of a public release."*

**Q7. The paper calls evidence "the bridge to open source." Explain the bridge — what is "one discipline, applied twice"?**

A: *"Evidence is also the bridge to open source: the same packet that lets HgX verify a run lets an external reviewer verify the system. Inspectability inside the estate and inspectability in public are one discipline, applied twice."* One evidence packet serves both audiences: the principal's verification and the public's inspection.

**Q8. State roadmap item 8 verbatim, and explain the two timing rules it contains.**

A: *"PUBLISH THE REFERENCE IMPLEMENTATION IN THE OPEN — 8. Complete the sanitising pass, publish doctrine, skills, contracts, and the reference implementation under an open licence, and maintain them in public. Publication timing remains on HgX's word; publishability is the standing requirement from day one."* The two timing rules: (1) *when* to publish is HgX's word alone; (2) *being publishable* is required from day one regardless.

---

## Paper II — The back end (technical)

**Q1. Name the five engineering invariants and state the operational meaning of "No proof, no done."**

A: The five invariants: **No proof, no done** — *"Delegation output is reviewed against artifacts, sources, tests, approvals, and gaps before completion is reported."* **Current facts stay live** — *"Memory carries durable context; changing state is re-read from its owning system."* **Automate preparation first** — *"One-time task becomes a proven skill, then a tested routine. Consequential execution remains approval-gated."* **Persistence is explicit** — *"/tmp and system paths are treated as disposable. Home-directory state survives restarts."* **Failure is visible** — *"Stale sources, exhausted retries, unverified handoffs, and missing permissions surface as failures or escalation."*

**Q2. Distinguish the durability boundary, the role boundary, the consequence boundary, and the delegation boundary — which one makes a subagent's completion claim an input rather than a result?**

A: Durability: *"~/ is the persistence root"* — what survives restarts. Role: *"Side chats isolate duties and memory procedurally. They are not a cryptographic boundary."* Consequence: *"Sending, publishing, spending, deletion, permission changes, and other consequential effects stop for approval."* Delegation: *"A subagent response is an input to verification, not a completion signal. The orchestrator remains accountable for acceptance."* — the **delegation boundary** is the one that makes a subagent's "done" an input to verification.

**Q3. A subagent reports "done" but shows no evidence. Under the state machine, what state is the work actually in, and what is the required response?**

A: It is not in Verified — *"Completion exists only after observed output passes the stated acceptance test"* and *"No optimistic completion: queued, running, active, or delegated are intermediate states."* The work sits in In progress awaiting verification. The required response is the delegation boundary plus the first invariant: treat the report as an input, and review the output against artifacts, sources, tests, approvals, and gaps before completion is reported. *"No proof, no done."*

**Q4. Why does the paper say moving a final artifact after publication is an "engineering consequence," and what is the prescribed discipline for choosing a file's home?**

A: *"Engineering consequence. Moving a final artifact after publication can break its reference; copying it creates two mutable truths."* The discipline: *"The final home is selected before the first user-facing byte is written"* — because *"a path is not clerical metadata; it is the contract that determines whether a future run can locate, revise, or safely discard state."* (Ordinary artifacts: `~/workspace/your_files/<slug>/`; goal documents: the goal's `files/` subtree.)

**Q5. What are the five stages of the skill pipeline, and which gate must a method pass before it "earns a schedule"?**

A: Observed task → proven run → **Skill** → test run → **Routine**. The gate: *"Only a reviewed method receives a schedule"* — a routine is *"a schedule bound to a tested skill, a live source, a failure policy, and an approval boundary."* The promotion gate runs: *"A real run establishes the inputs and finish line"* → *"Decision, failure, validation, and approval rules are written"* → *"The skill proves behavior on current data"* → *"Only a reviewed method receives a schedule."*

**Q6. A routine finds nothing actionable. What user-visible output is correct, and what internal evidence must still exist?**

A: User-visible: nothing — *"Silent-by-default is an output contract. A routine that finds no actionable change returns no user-visible output. Silence is deliberate, not missing observability."* Internal: the observability principle still holds — *"Silence may be the correct user-facing result, but it must not erase internal evidence that the routine ran, found no actionable change, or failed."*

**Q7. A stored fact contradicts what the owning system now shows. What is the read policy for each of the three memory classes, and how are corrections reconciled?**

A: The three classes: **durable memory** (stable facts — load when prior decisions matter), **working state** (run logs, watermarks — read from the owning goal/service), **live source** (prices, schedules — re-read at decision time; *never trust memory*). The continuity rule governs the conflict: *"The orchestrator consults memory before acting on prior work, but uses the original files and live systems as the authority for changing or consequential facts. Memory answers 'what matters'; the source system answers 'what is true now.'"* Corrections: *"Corrections replace contradictions — when HgX corrects a fact, the memory system reconciles the old note rather than appending a second incompatible version. The objective is a usable current record, not an archaeology of mistakes."*

**Q8. A task would spend heavily on deep research from a vague goal. Walk the policy order: which rule fires first, and what action results?**

A: The policy is first-match-wins, checked in order. Rule 1 (irreversible/consequential) does not match deep research. Rules 2–3 (retry budget, loop guard) do not match. Rule 4 (fresh cache) does not match. Rule 5 concerns subagent candidacy. Then **Rule 6**: *"Browser or deep research lacks a live-state requirement — Deny expensive path; use search or local evidence."* If the research has no live-state requirement, rule 6 fires first: deny the expensive path. If it does require live state, **Rule 7** fires: *"High-cost work begins from a vague goal — Defer for one focused question."*

**Q9. In shadow mode, the router recommends "deny delegation" but the orchestrator disagrees. Who chooses the action? How does this change in active mode?**

A: Shadow mode: *"Compute and log a recommendation; normal orchestrator judgment still chooses the action"* — the orchestrator chooses. Active mode: *"Honor the router action, except that approval and security rules remain authoritative."* (Current deployment: local backend, enabled, shadow mode.)

**Q10. State the six fields of the worker contract ("one agent, one job") and the standing rule for consequential subagent actions.**

A: Mission — *"One bounded responsibility that does not overlap another worker."* Inputs — *"The source files, facts, and constraints needed for that responsibility."* Tools — *"Only the capabilities necessary to produce the assigned output."* Expected output — *"A concrete artifact, finding, patch, or evidence packet."* Stop condition — *"Done, blocked, or approval needed."* Proof — *"Sources, tests, changed files, or other observable completion evidence."* The standing rule: *"No subagent publishes, sends, spends, or deletes without HgX's approval. A persuasive status message without proof has no standing in the completion state."*

**Q11. An approval is granted for one publish action. Does it cover a second publish to the same target tomorrow? Cite the non-goal.**

A: No. The approval non-goal: *"Approval does not authorize adjacent actions or future repetitions."* One approval is one action — the paper's standing example is that no agent publishes, sends, spends, or deletes without HgX's explicit approval for that exact action.

**Q12. The same operation fails with the same error twice. What must the system do next — and what is it forbidden to do?**

A: The retry budget (router policy rule 2): *"Same operation, same error, two retries consumed — Escalate or choose a fundamentally different approach."* What it is forbidden to do: repeat an unobserved consequential action — *"The system's strongest retry rule is to avoid repeating an unobserved consequential action."* Fail visible: the failure is reported with the observed condition, never papered over.

**Q13. In the test matrix, what is the expected observation for the "Stale source" test? How does the promotion gate distinguish a "safe test" from a "routine"?**

A: The matrix cell's exact wording is in the paper (to be taken up in session); the paper's supported position is the scheduling failure rule: *"When a required source is stale or unavailable, report failure. Do not silently reuse old data"* — consistent with the Failure-is-visible invariant. The promotion gate distinguishes them by stage: a **safe test** is the third stage (*"The skill proves behavior on current data"*); a **routine** is only the fourth (*"Only a reviewed method receives a schedule"*). The change-management rule: *"Skipping a stage spends reliability before the estate has earned it. A routine is promoted evidence, not a convenient timer."*

---

## Session Q&A (standing — grows with each session)

| Date | Question | Answer |
|---|---|---|
| — | — | — |

*Session questions from HgX are recorded here verbatim with the Academy's answers, dated and versioned like everything else.*
