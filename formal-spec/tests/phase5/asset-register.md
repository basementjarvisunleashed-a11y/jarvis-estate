# Phase 5 — Asset Register

**Status:** v0.1-draft · **Date:** 2026-10-22
**Sources:** `ROADMAP.md` §8 (asset list); `tests/PHASE-5-PLAN.md` (custody doctrines placement);
`tests/PHASE-5-OPEN-QUESTIONS.md` Q5, Q6 (answered 2026-10-22); `trust-boundaries.md` (boundary IDs TB-1…TB-15).

> **Governance.** Draft until HgX ratifies. Descriptive over the estate as
> ordered; nothing here redesigns a custody doctrine. Boundary IDs refer
> to `trust-boundaries.md`.

---

## 1. Purpose

The threat catalogue (`threat-catalogue.md`) needs named things to
protect. This register names them: every asset the roadmap lists, each
with a classification and the trust boundary that holds custody. Where
the source list's counting is ambiguous, the register says so (§6, P5-OP-0).

## 2. Asset classes

Classification scale, applied uniformly:

- **CRITICAL** — loss or misuse directly compromises HgX's safety,
  money, or identity.
- **SENSITIVE** — personal or operational material; disclosure harms
  privacy or the estate's integrity.
- **OPERATIONAL** — the machinery's own records; misuse degrades
  trust but discloses no personal content.

## 3. The register

| ID | Asset | Class | Custodian boundary |
|---|---|---|---|
| AR-1 | HgX attention | CRITICAL | TB-9 (client ↔ notification system) |
| AR-2 | Approval authority (HgX's power to bind consequence) | CRITICAL | TB-1 (devices ↔ estate edge), TB-2 (edge ↔ orchestrator) |
| AR-3 | Credentials (keys, tokens, session secrets) | CRITICAL | TB-7 (orchestrator ↔ Secure Vault) |
| AR-4 | Personal data — health | CRITICAL | TB-13 (health-data sealed boundary) |
| AR-5 | Personal data — finance | CRITICAL | TB-11 (money-access custody boundary) |
| AR-6 | Personal data — legal | SENSITIVE | TB-12 (calendar-communications-tasks custody boundary), TB-10 |
| AR-7 | Personal data — communications | SENSITIVE | TB-12 |
| AR-8 | Personal data — betting | SENSITIVE | TB-10 |
| AR-9 | Personal data — identity | CRITICAL | TB-1, TB-7 |
| AR-10 | Artifacts (inspectable work outputs) | OPERATIONAL | TB-3 (orchestrator ↔ tools) |
| AR-11 | Evidence packets (proof bundles) | OPERATIONAL | TB-3, TB-4 |
| AR-12 | Logs (operational records) | OPERATIONAL | TB-3, TB-7 |
| AR-13 | Connectors (integrations, grants) | OPERATIONAL | TB-5 (orchestrator ↔ connectors) |
| AR-14 | Runtime (the estate's execution substrate) | OPERATIONAL | TB-8 (orchestrator ↔ external router) |
| AR-15 | Router state (routing decisions, outcome labels) | OPERATIONAL | TB-8 |

## 4. Custody notes

1. **AR-1 (attention).** Attention is the asset the whole estate is
   built to conserve. Crossing rule (TB-9): notifications are hints,
   never payload; silent-by-default except direct human emails needing
   a reply, deadlines inside 24 hours, or genuinely anomalous security
   alerts.
2. **AR-2 (approval authority).** Resides in HgX alone. No client,
   subagent, router, or routine may exercise it; an approval binds the
   exact target, effect, scope, revision, and expiry of one intent
   (`capability-matrix.md` §4; `session-lifecycle.md` SL-12).
3. **AR-4 (health).** The health-data sealed boundary (TB-13) is
   absolute: health contents never cross any boundary to any other
   room, chat, worker, or report (`trust-boundaries.md` §4, TB-13).
4. **AR-5 (finance).** Money access is held solely by the money-access
   custody boundary (TB-11): one custodian; any money need from another
   room routes to HgX personally with one approval per exact amount,
   account, and date.
5. **AR-6/AR-7 (legal, communications).** Calendar/email/tasks custody
   (TB-12): one custodian for the estate; nothing about them happens
   silently or in another room.
6. **Live-location data.** Personal data in motion. It is governed by
   the live-location custody boundary (TB-14) — the boundary is named,
   the custodian is never named outside its own chat, per Q6 and the
   secrecy constraint. This register does not enumerate it further.
7. **AR-11 (evidence packets).** Every completed consequential run has
   one; an evidence packet is the only form in which an asset claim
   (completion, execution, approval) may be asserted.

## 5. Numbered claims

- **AR-1.** The roadmap's §8 asset list is captured without omission:
  attention, approval authority, credentials, personal data in its six
  named classes, artifacts, evidence packets, logs, connectors,
  runtime, router state.
- **AR-2.** Every asset has a classification and at least one
  custodian boundary (§3).
- **AR-3.** CRITICAL assets (AR-1…AR-5, AR-9) are those whose loss or
  misuse compromises HgX's safety, money, or identity; the
  classification is descriptive, not a claim of a control.
- **AR-4.** Custody doctrines are reflected as placement, not
  redesign: money under TB-11, calendar/email/tasks under TB-12,
  health sealed under TB-13, live location under TB-14 (boundary
  named, custodian never named), research findings sealed under
  TB-15.
- **AR-5.** Live-location data is not separately enumerated in this
  register; it is governed by TB-14 and surfaced in the model only
  through that boundary's crossing rules (§4.6).
- **AR-6.** An asset claim (completion, execution, approval) that is
  not carried by an evidence packet (AR-11) is not a claim the model
  recognizes.

## 6. Open points

- **P5-OP-0 — the "12 assets" count.** ROADMAP.md §8's list contains
  ten top-level names (fifteen distinct assets when personal-data
  classes are counted separately). The opening brief said "the
  roadmap's 12 assets." This register uses fifteen entries and maps
  the roadmap's ten lines without omission; it does not claim twelve
  is the roadmap's number. **Needs HgX's word** on whether the
  twelve-count was a shorthand or a different grouping to adopt. **RESOLVED 2026-10-22 ~13:25 ET: keep fifteen as written — the twelve-count was shorthand.**

## 7. Cross-references

- `trust-boundaries.md` — TB-1…TB-15, the custodian boundaries placed
  against the doctrines.
- `capability-matrix.md` — the eight-field vocabulary for actions on
  these assets.
- `threat-catalogue.md` — every STRIDE row names the assets it
  threatens.
- `control-matrix.md` — control-to-asset coverage.

## 8. Version history

- **v0.1-draft — 2026-10-22.** First draft: AR-1…AR-15 registered,
  classified, placed against TB-1…TB-15; Q6 baked in (custodians
  described, never redesigned; live-location custodian never named);
  P5-OP-0 recorded. Not ratified.
