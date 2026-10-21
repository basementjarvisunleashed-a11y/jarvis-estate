# Phase 0 Decision Sheet — J.A.R.V.I.S. Doctoral Validation Programme

*DRAFT — 2026-10-09. Seven operator decisions stand between the programme and Phase 0's Month 1 work. Each carries the paper's recommendation where one exists; where none exists, the trade-off is stated plainly. Paper IV is the authority; section references are given.*

**D1 — Primary modelling language: TLA+ or Alloy?** *(Paper IV §7, OQ-4)*
Blocks: Phase 1's first week. The failure model is dominated by event interleavings — duplicate taps, out-of-order events, expiry racing a tap.
Paper's recommendation: **TLA+** as the single primary; Alloy remains the recommended second tool for contract structure, not a rival primary.
☐ HgX's call: __________

**D2 — Who resolves Phase 0 vocabulary conflicts?** *(Paper IV §14, Month 1 dependencies)*
Blocks: freezing the canonical glossary. The three white papers' vocabularies genuinely conflict in places; someone must rule.
Options: (a) the operator rules at a Month 1 review; (b) the chief of staff reconciles, the operator ratifies. The paper states no recommendation — (b) keeps Month 1 moving; (a) keeps the operator's hand on the normative text.
☐ HgX's call: __________

**D3 — Commit to the isolation-level upgrade?** *(Paper IV §11, Phase 5)*
Blocks: the Phase 5 security formalism's scope. The exit criterion does not require Level 5, or even Level 2 — it requires Level 0 be described honestly, with compensating controls named and tested.
Paper's position: commit to the **upgrade ladder as a real plan with entry conditions**, not to a level. The decision is whether the twelve-month programme carries an actual isolation upgrade or stops at documented-and-compensated Level 0.
☐ HgX's call: __________

**D4 — Router live trials: required for the evidence package?** *(Paper IV §12, Phase 6)*
Blocks: the Phase 6 experiment design. Stage 3 (controlled live trials) may need a sample size the estate's natural workload cannot supply inside the programme's window.
Paper's position: run Stages 1–2 (shadow logging, offline replay) first, then decide; if the trial is underpowered, **state the power limits explicitly** rather than presenting an underpowered comparison as conclusive.
☐ HgX's call: __________

**D5 — Where does an expired approval return?** *(Paper IV §5.5, OQ-3 — adopted in the §6 transition table)*
`approval_denied → cancelled`; `approval_expired → in_progress` (the intent lapsed; the work item survives and may issue a fresh intent). Expiry is a property of the intent, not a verdict on the work.
Paper's recommendation: **keep the adopted table**. Changing to expiry-cancels-work is one row if the operator prefers it.
☐ HgX's call: __________

**D6 — Keep single `verifying` and `blocked` states?** *(Paper IV §5.5, OQ-1, OQ-2)*
Whether the machine should distinguish human from machine verification, or operator-blockage from source-blockage. Splitting either state doubles the transition table for no guard-level benefit.
Paper's recommendation: **keep one state each**; record verification method and blockage cause as provenance in the evidence packet and execution record.
☐ HgX's call: ☐ ratify / ☐ amend: __________

**D7 — Clock-skew bound Δ.** *(Paper IV §7.5, OQ-5)*
All time comparisons use server `now`; the skew bound between client and server must be explicit. 60 seconds is the largest Δ for which proof obligation PO-2 holds (counterexample demonstrated at 300s).
Paper's recommendation: **Δ = 60 seconds**, with any decision inside the skew window re-validated rather than trusted.
☐ HgX's call: __________

*When all seven are answered, Phase 0's Month 1 reconciliation begins: one normative vocabulary, frozen glossary, frozen state machine, versioned specification repository. No proof, no done — a month is complete when its exit criteria are evidenced, not when its calendar page turns.*
