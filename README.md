![J.A.R.V.I.S. — the arc reactor over the Toronto skyline](assets/banner.png)

# J.A.R.V.I.S. — an open-source operating system for personal AI

**One principal. A federation of durable roles. Current facts, inspectable
evidence, and human authority at every consequential boundary.**

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Papers: CC-BY-4.0](https://img.shields.io/badge/Papers-CC--BY--4.0-lightgrey.svg)](LICENSE-CC-BY-4.0)
[![Status: Live](https://img.shields.io/badge/Status-Live-brightgreen)](https://basementjarvisunleashed-a11y.github.io/jarvis-estate/)
[![Phase 1: Proven](https://img.shields.io/badge/Phase%201-Proven-blue)](formal-spec/proofs/phase1-tlc-report.md)
[![Audits: Public](https://img.shields.io/badge/Audits-Public-orange)](audits/)
[![Phase 2: Open](https://img.shields.io/badge/Phase%202-Open-yellow)](https://github.com/basementjarvisunleashed-a11y/jarvis-estate/milestone/3)

**[Website](https://basementjarvisunleashed-a11y.github.io/jarvis-estate/) ·
[Wiki](https://github.com/basementjarvisunleashed-a11y/jarvis-estate/wiki) ·
[Milestones](https://github.com/basementjarvisunleashed-a11y/jarvis-estate/milestones) ·
[Project board](https://github.com/users/basementjarvisunleashed-a11y/projects/1) ·
[Papers archive (Dropbox)](https://www.dropbox.com/scl/fo/hw9x2ln0x50pcw76a6say/AJIn_Emga-QyxZiIL_YubdY?rlkey=iirish4xzkjmusybq) ·
[Evidence ledger](EVIDENCE.md) ·
[Audits](audits/) ·
[Release log](release-log/)**

## Right now — the estate is live and moving

> **2026-10-21:** Phase 2 of the doctoral programme — invariant verification —
> is **open** and evidencing: Layer 1 contract suite **39/39**, Layer 2 property
> suite **10/10** (53,079 rejections logged), Layer 3 chaos suite **10/10**,
> cross-artifact audit **12/12**, roadmap test **37/58**, Phase 0+1 backtrace
> **18/18 artifacts, 12/12 claims**. Full reports in
> [`formal-spec/tests/`](formal-spec/tests/); the
> [Phase 2 milestone](https://github.com/basementjarvisunleashed-a11y/jarvis-estate/milestone/3)
> carries six closed deliverable issues with #10 tracking. The pause→go mechanism
> passed its live test at 96/100. Public audits run every week, and the
> evidence ledger is current. This is not a demo and it is not vapourware —
> every claim on this page is graded in the [evidence ledger](EVIDENCE.md).

This repository is the complete, sanitized J.A.R.V.I.S. estate: the doctrine,
the skills, the formal specification, the evidence ledger, the public audits —
and the Watchtower that proves it's running. Everything here runs today on a
real operator's estate. This isn't a framework demo; it's the actual system,
with the personal details removed.

## What J.A.R.V.I.S. does

- **Hot-swaps models.** The estate is model-agnostic by design. A router sits
  between intent and execution, and the model underneath is swapped live —
  upgraded, replaced, specialised per task, or run side-by-side — without
  rebuilding anything and without losing memory, evidence, doctrine, or
  authority. See the headline section below.
- **Runs a federation of roles, not a monolith.** A Chief-of-Staff pattern: a
  minimum team of durable specialist roles — calendar and tasks, health,
  sports, tax, media, finances, research, publishing, estate administration —
  each owning one job, duties never crossing, context compounding inside each
  role.
- **Proves its work.** "No proof, no done." Every consequential run returns an
  artifact plus evidence: sources, changes, tests, approvals, visible gaps.
  The public [evidence ledger](EVIDENCE.md) grades every claim — Proven,
  Verified, or Tracked.
- **Obeys one-word authority.** The pause→go mechanism stops the whole estate
  cold on a single word from the principal and returns it to full alertness on
  another — tested live on 2026-10-19/20 and scored 96/100 in the
  [internal audit](audits/internal-audit-2026-10-20-pause-go.md).
- **Verifies formally.** A doctoral programme is turning the doctrine into
  proof: contracts frozen at v1.0.0 normative, the work-state machine
  model-checked in TLA+ — Phase 1 closed over 3,266,929 states with zero
  invariant violations ([report](formal-spec/proofs/phase1-tlc-report.md)).
- **Watches itself.** The [Watchtower](watchtower/) sweeps the estate hourly
  and publishes an honest status page: a service the operator paused reads as
  *paused*, never down.
- **Publishes transparently.** Public audits on a weekly, monthly, and
  quarterly cadence; a stability score recomputed under a fixed rubric; every
  paper version kept forever — nothing is ever overwritten.

## Headline capability: model hot-swap

**J.A.R.V.I.S. hot-swaps all of its models.** No single model is the system.
A routing layer (see [`skills/usage-router`](skills/usage-router/SKILL.md))
sits between the principal's intent and execution and decides, per task, which
model does the work. Models are then swapped live:

- **Upgrade without migration.** When a better model ships, the estate adopts
  it at the router — the same day — not after a rebuild. Roles, memory,
  evidence, and authority are untouched by the swap.
- **Specialise per task.** Different work can ride different models at the
  same time: the router sends each job to the model that fits it, under a
  local policy with retry budgets and loop guards.
- **Continuity is the invariant.** What makes Jarvis *Jarvis* — the doctrine,
  the memory, the ledger, the principal's authority — lives above the model
  layer. Engines change underneath; the estate persists.

Router optimality is also a formal question here: Phase 6 of the doctoral
programme (below) puts the router itself under proof.

## From proof of concept to production

**The concept.** Most people use an AI assistant like a better chat window:
one question, one answer, no memory, no accountability. The bet behind
J.A.R.V.I.S. was that a personal AI should work more like a well-run estate —
named roles that own durable jobs, facts re-read from live systems instead of
trusted from memory, and every consequential run ending in evidence the
operator can inspect.

**The production system.** That bet became an operating loop:

```
ROLE → LIVE SOURCE → TOOL → ARTIFACT → EVIDENCE → APPROVAL → ROUTINE
```

- **Roles, not a monolith.** Each bot owns one job: calendar and tasks, media
  creation, health, sports, tax, administration. Duties never cross; context
  compounds inside each role instead of blurring across them.
- **Live sources of truth.** Changing facts (scores, prices, schedules,
  account states) are re-read from the system that owns them, every run.
  Memory holds identity, preferences, and continuity — never current numbers.
- **Evidence over status updates.** A fluent "done" is not proof. Every
  consequential run returns an artifact plus sources, changes, tests,
  approvals, and visible gaps.
- **Approval at the last safe moment.** The system prepares everything
  reversible, then stops before anything consequential: nothing is sent,
  spent, published, or deleted without the operator's explicit approval.
- **Skills before routines.** A proven run becomes a reusable skill; only
  skills that survive review become scheduled routines. Automation removes
  repeated preparation before it removes human control.

**The runtime proof.** [`watchtower/STATUS.md`](watchtower/STATUS.md) is
regenerated by the estate's own hourly sweep — real timestamps, real service
states. A service the operator deliberately paused reads as *paused*, not
down: pausing is a decision, not an outage.

## The papers

Four white papers define the system. They are read in full on the
[website](https://basementjarvisunleashed-a11y.github.io/jarvis-estate/) and
kept, every version, in the
[Dropbox archive](https://www.dropbox.com/scl/fo/hw9x2ln0x50pcw76a6say/AJIn_Emga-QyxZiIL_YubdY?rlkey=iirish4xzkjmusybq).

| Paper | Version | Pages | Read (PDF) |
|---|---|---|---|
| I — J.A.R.V.I.S. (the vision) | v1.2 | 14 | [Dropbox](https://www.dropbox.com/scl/fi/tjol5sdujqgv2uc508xw0/J.A.R.V.I.S.-White-Paper.pdf?rlkey=pljgg0v9x83x7looqmitulzv9&dl=0) |
| II — Technical White Paper | v1.1 | 20 | [Dropbox](https://www.dropbox.com/scl/fi/zu14vprfemfedukywnc6w/J.A.R.V.I.S.-Technical-White-Paper.pdf?rlkey=0nz90ivkez4i6u18ojn004ttk&dl=0) |
| III — Front-End White Paper | v1.1 | 20 | [Dropbox](https://www.dropbox.com/scl/fi/tsm336r7uanmeif9qu0r0/J.A.R.V.I.S.-Front-End-White-Paper.pdf?rlkey=eraufgjy85ni7q24597xcyajz&dl=0) |
| IV — Roadmap: From Doctrine to Proof | v1.1 | 110 | [Dropbox archive](https://www.dropbox.com/scl/fo/hw9x2ln0x50pcw76a6say/AJIn_Emga-QyxZiIL_YubdY?rlkey=iirish4xzkjmusybq) |

Open source is the main vision, not a footnote: Paper I states it as the
fifth principle, and Phase 8 of the roadmap publishes the reference
implementation. Publication timing is the principal's word.

## The doctoral programme

Paper IV commissions an eight-phase programme to turn doctrine into a
formally defensible engineering and research contribution. Full roadmap:
Paper IV (above); working files in [`formal-spec/`](formal-spec/).

| Phase | Scope | Status |
|---|---|---|
| [0](https://github.com/basementjarvisunleashed-a11y/jarvis-estate/milestone/1) | Freeze the contracts | **Closed** — TLA+ ratified; glossary ratified; contracts v1.0.0 normative |
| [1](https://github.com/basementjarvisunleashed-a11y/jarvis-estate/milestone/2) | State-machine proof | **Proven** — TLC model check: 3,266,929 states, zero invariant violations |
| [2](https://github.com/basementjarvisunleashed-a11y/jarvis-estate/milestone/3) | Invariant verification | **Open** — Layer 1 39/39, Layer 2 10/10, Layer 3 10/10, crosscheck 12/12 ([evidence](formal-spec/tests/)) |
| [3](https://github.com/basementjarvisunleashed-a11y/jarvis-estate/milestone/4) | Consistency model | Planned |
| [4](https://github.com/basementjarvisunleashed-a11y/jarvis-estate/milestone/5) | Idempotency | Planned |
| [5](https://github.com/basementjarvisunleashed-a11y/jarvis-estate/milestone/6) | Security boundaries | Planned |
| [6](https://github.com/basementjarvisunleashed-a11y/jarvis-estate/milestone/7) | Router optimality | Planned |
| [7](https://github.com/basementjarvisunleashed-a11y/jarvis-estate/milestone/8) | Doctoral evidence package | Planned |

Versions follow the law in [VERSIONING.md](VERSIONING.md): v0.x.x is a
draft, v1.0.0 is ratified, versions only move forward, and every proof names
the exact version it checked.

## Audits and scores

The estate audits itself in public, on the record:

- **Weekly / monthly / quarterly audits** under a fixed template —
  [`audits/`](audits/). First weekly audit: 2026-W43, PASS, baseline
  stability 85/100 ([scores](scores/STABILITY.md)).
- **Outside audit, 2026-10-20** — an external model's claims about this
  estate, checked claim-by-claim against the primary records and rejected in
  full: [`audits/outside-audit-2026-10-20.md`](audits/outside-audit-2026-10-20.md).
- **Internal audit, 2026-10-20** — the pause→go mechanism test: 96/100, PASS:
  [`audits/internal-audit-2026-10-20-pause-go.md`](audits/internal-audit-2026-10-20-pause-go.md).
- **Stability scoring** — a fixed rubric (weights change only on the
  principal's word), a corrections ledger, and a concept registry in
  [`scores/`](scores/).

## Repository map

| Path | What it is |
|---|---|
| `index.html` + `website/` | The public hub — the GitHub Pages site: papers in full, build-out, build log, evidence, audits, scores. |
| `skills/` | The eight estate skills — reproducible playbooks: calendar office, meme forge, betting desk, sports desk, estate administrator, tax office, team deployment, usage router. |
| `formal-spec/` | The doctoral workstream: frozen contracts (canonical glossary, event vocabulary), the TLA+ work-state machine, and the Phase 1 proof report with its TLC run log. |
| `audits/` | The public audit record: template, weekly audits, and the 2026-10-20 outside and internal audits. |
| `scores/` | Stability scoring: the rubric, the current score, the corrections ledger, the concept registry. |
| `EVIDENCE.md` | The evidence ledger: every public claim graded Proven / Verified / Tracked. |
| `release-log/` | Dated build logs (markdown): date, timestamps (America/Toronto), work hours, and comments — the full chronicle from 2026-10-19 to the final build-out. |
| `watchtower/` | Honest uptime monitoring: stdlib-only Python, a service manifest, and the live `STATUS.md`. |
| `SYSTEM_PROMPT.md` | The estate's identity rules and operating doctrine, as given to the system. |
| `VERSIONING.md` | The versioning law: draft vs ratified, forward-only. |
| `CITATION.cff` | How to cite this work. |
| `CONTRIBUTING.md` | How to contribute — and the estate's approval boundaries. |

## Following the build-out

The full chronicle — logs, comments, versioning — is followable right here:

- **Website build log:** the [hub](https://basementjarvisunleashed-a11y.github.io/jarvis-estate/)
  carries the build log in real time, newest first.
- **Release log:** `release-log/` — one dated markdown file per build day,
  with timestamps (America/Toronto), work hours, and comments, from
  2026-10-19 through the final build-out.
- **Changelog:** [CHANGELOG.md](CHANGELOG.md) — notable changes per release.
- **Project board:** [J.A.R.V.I.S. Build-out](https://github.com/users/basementjarvisunleashed-a11y/projects/1) —
  Table, Board, and Roadmap views; phase milestones; every item in its true
  state.
- **Wiki:** the [wiki](https://github.com/basementjarvisunleashed-a11y/jarvis-estate/wiki)
  — the papers, architecture, glossary, doctoral programme, versioning,
  build log, skills, watchtower, contributing, FAQ.

HgX's standing rule: the growth and maturity of J.A.R.V.I.S. stay on record —
every version kept, every release logged.

## The skills

Each skill is a `SKILL.md` with the same anatomy: frontmatter (`name` +
`description`, where the description is the trigger), then Purpose, Workflow,
Output Contract, Operating Rules. Two are worth calling out:

- **`usage-router`** — a decision gate consulted before expensive work (live
  browser, deep research, retries, new subagents). Local policy by default:
  retry budget of 2, loop guard at 3, cache preferred, irreversible actions
  always escalate. Shadow mode logs every recommendation before it ever acts.
  This is the routing layer behind model hot-swap.
- **`team-deployment`** — the Chief-of-Staff pattern: one brief in, a minimum
  autonomous specialist team out, verified results back. No proof, no done.

## Principles

1. Truth over comfort — state what the evidence supports.
2. Discretion — use and reveal only what the task requires.
3. Reversibility — prefer safe preparation to premature action.
4. Stewardship — treat access, attention, and records as entrusted assets.

The scarcest resource is not compute. It is the operator's attention. A mature
system protects it: speak when there is signal, stay silent when there is
none, and never substitute confidence for proof.

## Connect

**J.A.R.V.I.S. is the public identity.**

- **X (Twitter):** **[@basementjarvisu](https://x.com/basementjarvisu)** —
  the public voice of J.A.R.V.I.S.
- **Email:** **basementjarvisunleashed@gmail.com**
- **Dropbox:** [the full /J.A.R.V.I.S./ archive](https://www.dropbox.com/scl/fo/hw9x2ln0x50pcw76a6say/AJIn_Emga-QyxZiIL_YubdY?rlkey=iirish4xzkjmusybq) —
  papers, roadmap, logs, audits, and scores. Every version kept, nothing
  overwritten.

<sub>[@hgxengineering](https://x.com/hgxengineering) · HgXengineering@gmail.com</sub>

## License

© 2026 **J.A.R.V.I.S.** — [@basementjarvisu](https://x.com/basementjarvisu) on X,
basementjarvisunleashed@gmail.com.

<sub>[@hgxengineering](https://x.com/hgxengineering) · HgXengineering@gmail.com</sub>

- Code, skills, and tooling: **MIT** — see [LICENSE](LICENSE).
- White papers and documentation: **CC-BY-4.0** — see
  [LICENSE-CC-BY-4.0](LICENSE-CC-BY-4.0).

Build your own estate.
