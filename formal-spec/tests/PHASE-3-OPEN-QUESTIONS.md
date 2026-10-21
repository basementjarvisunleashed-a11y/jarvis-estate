# Phase 3 — Open Questions
## Needing HgX's word · Opened 2026-10-21

The consistency model cannot be written until these are answered. Each
question: context, options, a recommendation, and a blank answer line
for the walkthrough.

---

### Q1 — Who is the orchestrator in his estate?

- **Context:** ROADMAP.md §6 names "the orchestrator (or authorized
  execution layer)" as the single authoritative writer, and forbids any
  client from becoming a second orchestrator. Two live candidates: (a)
  the iPhone — his live point of presence, Always location, the device
  he carries; (b) the deployment build's orchestrator loop (SERVE /
  SENSE / QUEUE / REVIEW / MAINTAIN) as the reference implementation.
  Note the tension: the roadmap's architecture also says clients may
  NOT become a second orchestrator — and the iPhone is, in the
  roadmap's device list, a client surface.
- **Options:** (a) iPhone as orchestrator; (b) the deployment build's
  orchestrator loop as the reference implementation, with the iPhone
  as the trusted enrollment/command surface; (c) a server-side
  orchestrator (to be built — not the iPhone, not the build).
- **Recommendation:** (b). The iPhone as single writer makes the most
  carried, most losable device the estate's source of truth — and the
  roadmap forbids clients from becoming orchestrators. The build's loop
  is tested (60 tests across its pull + surface-contract phases) and
  already implements the single-writer discipline; the iPhone stays the
  trusted surface (enrollment root, approval card presenter), not the
  writer.
- **HgX's answer:** _(blank — walkthrough pending)_

---

### Q2 — Which devices are in scope for the consistency model?

- **Context:** ROADMAP.md §6 names five devices: iPhone, Watch, iPad,
  TV, Vision Pro. His live estate today: iPhone (live point of
  presence) + Watch (+ the basement laptop as home node only). The
  consistency model must cover every device that can observe or act on
  estate state — but writing the model for hardware he does not carry
  risks specifying fiction.
- **Options:** (a) iPhone + Watch in scope now; iPad/TV/Vision Pro as
  pull-only surfaces per their contracts (no consistency obligations
  beyond their pull contracts) until he carries them; (b) all five
  now, specified against the roadmap; (c) iPhone only.
- **Recommendation:** (a). The Watch is the five-second approval gate —
  it acts on state, so it is in scope. TV/headset never pull approvals
  or contents (§3.2 contracts); specifying consistency for them now is
  fiction. iPad joins the model the day it joins his pocket.
- **HgX's answer:** _(blank — walkthrough pending)_

---

### Q3 — Does the Research Bot's orchestrator survey gate the architecture decisions?

- **Context:** On his 2026-10-21 ~14:53 ET order, the Research Bot is
  surveying the state of the art in orchestrator/consistency
  architectures (standalone problem; sealed in the research section;
  findings never return to the working room). His own words: his
  architecture will be different and much better — the survey maps
  where the literature goes silent.
- **Options:** (a) the survey runs in parallel — architecture decisions
  (Q1, Q2, the model spec) proceed on his word now, informed by the
  survey if/when he orders its publication; (b) the architecture waits
  for the survey.
- **Recommendation:** (a). Waiting stalls the phase on a survey whose
  findings he has already said he will surpass. The survey's value is
  positioning (what the literature would reach for; where it is
  silent) — that informs the doctoral write-up, not the architecture.
- **HgX's answer:** _(blank — walkthrough pending)_

---

### Q4 — Is the deployment build's pull + surface-contract substrate adopted as the Phase 3 reference implementation?

- **Context:** The deployment build's phase 1 (pull protocol, 27 tests)
  and phase 2 (surface enrollment + per-surface contracts, 33 tests)
  are green and published. Phase 3's consistency model sits directly on
  this substrate: revision tokens ride the pull request; surface
  contracts bound what each device may observe. The alternative is a
  separate Phase 3 harness, duplicating 60 tested behaviors.
- **Options:** (a) adopt as the reference implementation — Phase 3
  tests build on it; the formal spec documents remain the normative
  layer (the build implements, the spec governs); (b) keep separate —
  Phase 3 gets its own harness.
- **Recommendation:** (a). Duplicating 60 green tests to prove the
  same substrate is motion, not progress. The honest boundary stays:
  the build is the reference implementation, not the specification —
  where they disagree, the ratified contracts govern (same discipline
  as the TLA+ anchor in Phase 1).
- **HgX's answer:** _(blank — walkthrough pending)_

---

## Changelog
- 2026-10-21 ~17:29 ET: opened with Q1–Q4 on Phase 3 opening (HgX's
  order). Answers recorded here as given, one by one.
