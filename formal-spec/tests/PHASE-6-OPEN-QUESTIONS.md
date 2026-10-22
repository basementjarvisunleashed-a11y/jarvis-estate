# Phase 6 — Router Optimality — Open Questions

**Status:** v0.1-draft. Written 2026-10-22 on HgX's word. Walkthrough on his
readiness — one by one, answers recorded as given.

---

### Q1 — Empirical scope: stages 1–2 only, or include stage 3 controlled live trials?

- **Context:** ROADMAP.md §9 defines four experimental stages. Stage 1
  (shadow logging) is already supported — the router logs today. Stage 2
  (offline replay) works on measured history. Stage 3 (controlled live
  trials) randomizes policy assignment across live low-risk tasks; the
  roadmap itself says "never randomize consequential actions." Stage 3 is
  the first one that touches live work rather than observing it.
- **Why it matters:** shadow logging and offline replay can answer most of
  the research question without any live-work risk. Stage 3 adds causal
  evidence but introduces live-work experimentation — HgX's own
  attention cost is one of the measured quantities, so the experiment must
  not waste the thing it measures.
- **Options:** (a) stages 1–2 now — shadow logging with outcome labels plus
  offline replay against the alternate policies; stage 3 only later, on his
  word, per task class; (b) all of stages 1–3 now — include controlled live
  trials on the low-risk task classes from the start; (c) stage 1 only —
  log outcomes first, defer replay until the log has real volume.
- **Recommendation:** (a). Stages 1–2 answer most of the research question
  without touching live work. Stage 3 is real experimentation on his estate
  — it deserves its own order, per task class, not a quiet inclusion in an
  evaluation phase. The evidence base for stages 1–2 also tells him which
  task classes, if any, are worth trialing live.
- **HgX's answer:** (a) stages 1–2 now — shadow logging with outcome labels plus offline replay; stage 3 only later, on his word, per task class. Answered 2026-10-22 ~12:47 ET.

---

### Q2 — The TypeSafe Jev backend: evaluate it, or defer?

- **Context:** The exit criterion says "Jev evaluated if approved" — the
  roadmap deliberately makes it conditional. The router skill states the
  local policy runs at zero cost and zero data egress; the Jev backend is
  optional, never the default, requires a key he creates himself via the
  Secure Vault flow, sends only the compact decision state, and falls back
  to local on any failure. Evaluating it is a cost decision — API spend for
  the trials — and a data-egress decision, however small.
- **Why it matters:** "evaluate the backend" means paying for it during
  the trials and sending decision states off the estate. The local policy's
  whole claim is that it's good enough without it; the evaluation should
  prove or disprove that claim — but the spend is his to authorize.
- **Options:** (a) evaluate Jev only on his explicit approval — the
  comparison harness is built Jev-ready, the trial itself waits for his
  word and his key; (b) include Jev in the evaluation now — he provides
  the key and the trial budget up front; (c) defer Jev entirely — the
  learned/hybrid policies wait for Phase 6's next iteration.
- **Recommendation:** (a). The exit criterion's own words are "if approved"
  — the approval is his, and it has a price tag. Build the harness
  Jev-ready so a single word from him starts the trial; don't spend his
  money on a decision he hasn't made.
- **HgX's answer:** (a) evaluate Jev only on his explicit approval — the harness built Jev-ready, the trial waits for his word and his key. Answered 2026-10-22 ~12:48 ET.

---

### Q3 — Eligibility boundary for any live trial: which task classes are in, which are absolutely excluded?

- **Context:** Stage 3 trials randomize policy assignment — but the
  roadmap says "random assignment for eligible tasks only; never randomize
  consequential actions." The estate's custody doctrines draw hard lines:
  money (Money Bot), calendar/email/tasks (Tickler Bot), health (Dr Bot,
  sealed), food (Food Bot), research (Research Bot, sealed lab), live
  location (the eye in the sky, never named). A live trial must not put a
  policy experiment anywhere near those.
- **Why it matters:** this is the boundary between a clean experiment and
  a doctrine violation. The trial protocol needs a written eligibility
  list — what's in (e.g. read-only lookups, cache-preferred fetches) and
  what's absolutely excluded — before stage 3 exists even as a design.
- **Options:** (a) propose the boundary in L1 — the experiment protocol
  drafts the eligible/ineligible task classes against the custody
  doctrines, and he ratifies it line by line before anything is built;
  (b) exclude everything consequential or custodial by default and let the
  trial design pull classes in one at a time on his word; (c) defer the
  boundary entirely until stage 3 is approved.
- **Recommendation:** (a). The boundary should be written down first —
  proposed against the doctrines he ordered, ratified by him line by line.
  A boundary that lives only in somebody's head is not a boundary.
- **HgX's answer:** (a) propose the boundary in L1 — eligible/ineligible task classes drafted against the custody doctrines; he ratifies line by line. Answered 2026-10-22 ~12:49 ET.

---

### Q4 — Objective-function weights: who sets the trade-offs?

- **Context:** The objective function is
  `accepted_work − human_repair_cost − attention_cost − financial_cost −
  loop_penalty − latency_penalty`. As written, every term counts equally —
  but is one minute of his attention worth the same as one API call? The
  weights are a value judgement about his time, his money, and his
  patience, not a mathematical derivation.
- **Why it matters:** the weights decide what "optimal" means. Set them
  wrong and the harness will diligently optimize for the wrong thing —
  saving pennies while burning his attention. There is no measured answer
  to "how much is my attention worth"; there is only his answer.
- **Options:** (a) propose defaults in L1 — the policy spec carries a
  weight table with honest defaults (e.g. attention priced above compute),
  and he ratifies or overrides each before any comparison is run; (b) his
  word first — no defaults, the walkthrough sets the weights directly;
  (c) equal weights — run the comparisons unweighted, let the dashboard
  show the raw trade-offs, and tune later.
- **Recommendation:** (a). Give him a concrete table to react to — defaults
  are faster to correct than a blank sheet, and a blank sheet at
  walkthrough speed gets vague answers. But no comparison runs until he
  has signed the weights.
- **HgX's answer:** (a) propose defaults in L1 — the policy spec carries a weight table; he ratifies or overrides each before any comparison runs. Answered 2026-10-22 ~12:51 ET.

---

### Q5 — Router decision logs with outcome labels: where do they live, who may read them?

- **Context:** Stage 1 extends the router logs with outcome labels —
  outcome, human_repair, repair_time_minutes, cost_units, latency_seconds,
  attention_interruptions, evidence_complete. Those labels describe what he
  did, what went wrong, and how long the repair took. The logs already live
  at `~/workspace/usage-router/logs/`; the outcome labels make them a
  record of his working life, and the custody doctrines say who may hold
  what.
- **Why it matters:** the labels are the evidence base the whole phase
  rests on — and they're also a diary of his attention. Where they live,
  who can read them, and whether any part of them ever leaves the estate
  (e.g. to a Jev backend) are custody decisions, not engineering ones.
- **Options:** (a) propose placement in L1 — the log schema draft names
  the location, the readers, and the egress rules (nothing off-estate
  except the compact decision state, and only with his Jev approval), and
  he ratifies it; (b) keep the logs where they are with no new readers —
  Jarvis only, no exceptions, no egress, full stop; (c) treat the labels
  as ordinary estate data under his standing rules.
- **Recommendation:** (a). The labels deserve a written custody line —
  proposed in the schema, ratified by him. (b) is likely where the line
  lands, but let him see the proposal and say so, rather than assuming it.
- **HgX's answer:** (a) propose placement in L1 — the log schema names the location, the readers, and the egress rules; he ratifies. Answered 2026-10-22 ~12:52 ET.

## Walkthrough complete
- 2026-10-22 ~12:52 ET: all five questions answered in the one-by-one walkthrough — Q1 stages 1–2 now, stage 3 later on his word per task class; Q2 Jev evaluated only on his explicit approval; Q3 eligibility boundary proposed in L1 against the custody doctrines, he ratifies line by line; Q4 weight-table defaults proposed in L1, he signs before any comparison runs; Q5 outcome-labeled log placement proposed in L1, he ratifies. Phase 6 work layers open on his word.
